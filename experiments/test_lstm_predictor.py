import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # repo root

from controllers.lstm_predictor import PairActivityLSTM  # noqa: E402


class PairActivityLSTMTest(unittest.TestCase):

  def test_forecast_tracks_repeating_activity(self):
    predictor = PairActivityLSTM(seed=13)
    pair = ('src', 'dst')
    active_scores = []
    idle_scores = []
    for step in range(240):
      active_now = step % 4 in (0, 1)
      active_next = (step + 1) % 4 in (0, 1)
      scores = predictor.update([pair], {pair} if active_now else set())
      if 120 <= step < 239:
        (active_scores if active_next else idle_scores).append(scores[pair])

    self.assertGreater(sum(active_scores) / len(active_scores),
                       sum(idle_scores) / len(idle_scores) + 0.15)

  def test_loaded_model_predicts_without_training(self):
    predictor = PairActivityLSTM(seed=13)
    pair = ('src', 'dst')
    for step in range(80):
      active = {pair} if step % 3 == 0 else set()
      predictor.update([pair], active)

    with tempfile.TemporaryDirectory() as directory:
      model_path = os.path.join(directory, 'activity.npz')
      predictor.save(model_path, {'workloads': ['university']})
      loaded = PairActivityLSTM.load(model_path)
      weights_before = loaded.weights.copy()
      predictor.reset_state()
      expected = predictor.update([pair], {pair}, learn=False)[pair]
      actual = loaded.update([pair], {pair}, learn=False)[pair]

    self.assertAlmostEqual(actual, expected)
    self.assertEqual(loaded.metadata['workloads'], ['university'])
    self.assertTrue((loaded.weights == weights_before).all())

  def test_warmup_updates_weights_then_inference_freezes_them(self):
    predictor = PairActivityLSTM(seed=19)
    pair = ('src', 'dst')
    initial_weights = predictor.weights.copy()
    for step in range(40):
      active = {pair} if step % 3 == 0 else set()
      predictor.update([pair], active, learn=True)
    self.assertFalse((predictor.weights == initial_weights).all())

    trained_weights = predictor.weights.copy()
    for step in range(10):
      active = {pair} if step % 2 == 0 else set()
      predictor.update([pair], active, learn=False)
    self.assertTrue((predictor.weights == trained_weights).all())


if __name__ == '__main__':
  unittest.main()
