"""Small LSTM for predicting per-pair activity in the next interval."""

import json

import numpy as np


def _sigmoid(values):
  return 1.0 / (1.0 + np.exp(-np.clip(values, -30.0, 30.0)))


class PairActivityLSTM(object):
  """Shared LSTM trained from binary per-interval pair activity."""

  def __init__(self, history=8, hidden=8, learning_rate=0.1, train_steps=4, seed=7):
    self.history = history
    self.hidden = hidden
    self.learning_rate = learning_rate
    self.train_steps = train_steps
    self.rng = np.random.RandomState(seed)
    scale = 1.0 / np.sqrt(hidden + 1)
    self.weights = self.rng.normal(0.0, scale, (hidden + 1, hidden * 4))
    self.bias = np.zeros(hidden * 4)
    self.output_weights = self.rng.normal(0.0, scale, (hidden, 1))
    self.output_bias = np.zeros(1)
    self.sequences = {}
    self.pending = {}

  def _forward(self, inputs):
    batch = inputs.shape[0]
    h = np.zeros((batch, self.hidden))
    c = np.zeros_like(h)
    caches = []
    for t in range(inputs.shape[1]):
      combined = np.concatenate((inputs[:, t, :], h), axis=1)
      gates = combined.dot(self.weights) + self.bias
      i, f, o, g = np.split(gates, 4, axis=1)
      i, f, o, g = _sigmoid(i), _sigmoid(f), _sigmoid(o), np.tanh(g)
      previous_c = c
      c = f * c + i * g
      tanh_c = np.tanh(c)
      h = o * tanh_c
      caches.append((combined, previous_c, i, f, o, g, tanh_c))
    probability = _sigmoid(h.dot(self.output_weights) + self.output_bias)
    return probability, h, caches

  def _train(self, inputs, targets):
    if not len(targets):
      return
    probability, final_h, caches = self._forward(inputs)
    dlogit = (probability - targets) / max(1, len(targets))
    grad_output = final_h.T.dot(dlogit)
    grad_output_bias = dlogit.sum(axis=0)
    dh_next = dlogit.dot(self.output_weights.T)
    dc_next = np.zeros_like(dh_next)
    grad_weights = np.zeros_like(self.weights)
    grad_bias = np.zeros_like(self.bias)

    for combined, previous_c, i, f, o, g, tanh_c in reversed(caches):
      dc = dc_next + dh_next * o * (1.0 - tanh_c * tanh_c)
      di = dc * g
      df = dc * previous_c
      do = dh_next * tanh_c
      dg = dc * i
      d_gates = np.concatenate((di * i * (1.0 - i), df * f * (1.0 - f),
                                do * o * (1.0 - o), dg * (1.0 - g * g)), axis=1)
      grad_weights += combined.T.dot(d_gates)
      grad_bias += d_gates.sum(axis=0)
      d_combined = d_gates.dot(self.weights.T)
      dh_next = d_combined[:, 1:]
      dc_next = dc * f

    gradients = [grad_weights, grad_bias, grad_output, grad_output_bias]
    norm = np.sqrt(sum(float(np.sum(g * g)) for g in gradients))
    factor = min(1.0, 5.0 / max(norm, 1e-12))
    self.weights -= self.learning_rate * gradients[0] * factor
    self.bias -= self.learning_rate * gradients[1] * factor
    self.output_weights -= self.learning_rate * gradients[2] * factor
    self.output_bias -= self.learning_rate * gradients[3] * factor

  def reset_state(self):
    self.sequences = {}
    self.pending = {}

  def update(self, pairs, active, learn=True):
    """Consume one interval, optionally train, and return next-interval scores."""
    keys = sorted(set(pairs) | set(active))
    if not keys:
      self.pending = {}
      return {}

    if learn and self.pending:
      train_keys = [key for key in keys if key in self.pending]
      if train_keys:
        train_x = np.zeros((len(train_keys), self.history, 1))
        for index, key in enumerate(train_keys):
          sequence = self.pending[key]
          train_x[index, -len(sequence):, 0] = sequence
        train_y = np.asarray([[1.0 if key in active else 0.0] for key in train_keys])
        for _ in range(self.train_steps):
          self._train(train_x, train_y)

    for key in keys:
      sequence = self.sequences.setdefault(key, [])
      sequence.append(1.0 if key in active else 0.0)
      self.sequences[key] = sequence[-self.history:]

    inputs = np.zeros((len(keys), self.history, 1))
    self.pending = {}
    for index, key in enumerate(keys):
      sequence = self.sequences[key]
      inputs[index, -len(sequence):, 0] = sequence
      if learn:
        self.pending[key] = list(sequence)
    probabilities, _, _ = self._forward(inputs)
    return {key: float(probabilities[i, 0]) for i, key in enumerate(keys)}

  def save(self, path, metadata=None):
    """Save learned weights and training metadata in a NumPy archive."""
    np.savez(path, history=self.history, hidden=self.hidden,
             learning_rate=self.learning_rate, train_steps=self.train_steps,
             weights=self.weights, bias=self.bias, output_weights=self.output_weights,
             output_bias=self.output_bias, metadata=json.dumps(metadata or {}))

  @classmethod
  def load(cls, path):
    """Load a trained model without restoring any per-pair runtime history."""
    with np.load(path, allow_pickle=False) as archive:
      model = cls(history=int(archive['history']), hidden=int(archive['hidden']),
                  learning_rate=float(archive['learning_rate']),
                  train_steps=int(archive['train_steps']))
      model.weights = archive['weights'].copy()
      model.bias = archive['bias'].copy()
      model.output_weights = archive['output_weights'].copy()
      model.output_bias = archive['output_bias'].copy()
      model.metadata = json.loads(str(archive['metadata']))
    return model
