#!/usr/bin/env python3
"""Train a pair-activity LSTM from generated traffic schedules."""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, REPO)

import workloads
from controllers.lstm_predictor import PairActivityLSTM


def train(args):
  hosts = ['h%d' % i for i in range(1, args.hosts + 1)]
  edge_of = {host: 'e%d' % (index // args.edge_fanout)
             for index, host in enumerate(hosts)}
  pairs = [(src, dst) for src in hosts for dst in hosts if src != dst]
  model = PairActivityLSTM(history=args.history, hidden=args.hidden,
                           learning_rate=args.learning_rate, train_steps=args.train_steps,
                           seed=args.model_seed)
  traces = 0

  for workload in args.workloads:
    if workload == 'isp':
      raise ValueError('isp training requires a traffic-matrix host map; use a DC workload')
    for seed in args.seeds:
      flows, info = workloads.make_schedule(
        workload, hosts, edge_of, args.duration, args.load, args.bw, args.max_mb * 10**6,
        'lstm-train-%s-%d' % (workload, seed), pair_zipf=args.pair_zipf)
      activity = [set() for _ in range(args.duration)]
      for start, src, dst, _size in flows:
        activity[min(args.duration - 1, int(start))].add((src, dst))

      model.reset_state()
      for active in activity:
        model.update(pairs, active, learn=True)
      traces += 1
      print('%s seed %d: %d flows, %.1f flows/s' % (
        workload, seed, info['flows'], info['flows_per_s']))

  metadata = {'workloads': args.workloads, 'seeds': args.seeds, 'hosts': args.hosts,
              'edge_fanout': args.edge_fanout, 'duration_seconds': args.duration,
              'interval_seconds': 1, 'pair_zipf': args.pair_zipf, 'traces': traces}
  model.save(args.out, metadata)
  print('saved trained model: %s' % args.out)
  return model


def main():
  ap = argparse.ArgumentParser(description=__doc__)
  ap.add_argument('--workloads', nargs='+', choices=sorted(workloads.WORKLOADS),
                  default=['university', 'websearch', 'datamining'])
  ap.add_argument('--seeds', nargs='+', type=int, default=list(range(101, 111)))
  ap.add_argument('--duration', type=int, default=60, help='training seconds per generated trace')
  ap.add_argument('--hosts', type=int, default=16)
  ap.add_argument('--edge-fanout', type=int, default=4)
  ap.add_argument('--load', type=float, default=0.3)
  ap.add_argument('--bw', type=int, default=100)
  ap.add_argument('--max-mb', type=int, default=20)
  ap.add_argument('--pair-zipf', type=float, default=1.0)
  ap.add_argument('--history', type=int, default=8)
  ap.add_argument('--hidden', type=int, default=8)
  ap.add_argument('--learning-rate', type=float, default=0.1)
  ap.add_argument('--train-steps', type=int, default=4)
  ap.add_argument('--model-seed', type=int, default=7)
  ap.add_argument('--out', required=True, help='output .npz model artifact')
  args = ap.parse_args()

  if args.hosts < 2 or args.edge_fanout < 1 or args.duration < 2:
    ap.error('--hosts must be >= 2, --edge-fanout >= 1 and --duration >= 2')
  if args.max_mb < 1:
    ap.error('--max-mb must be >= 1')
  if not args.out.endswith('.npz'):
    ap.error('--out must end in .npz')
  train(args)


if __name__ == '__main__':
  main()
