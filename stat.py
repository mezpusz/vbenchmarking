#!/usr/bin/env python3

import argparse
from resultparser import parse, STATUS, CPUTIME, MEMORY, INSTRUCTIONS

TRUE = 'true'
FALSE = 'false'
INS_LIMIT = 'OUT OF INSTRUCTIONS'

if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('filename')
  parser.add_argument('-all', action=argparse.BooleanOptionalAction)
  parser.add_argument('-unsat', action=argparse.BooleanOptionalAction)
  parser.add_argument('-sat', action=argparse.BooleanOptionalAction)
  parser.add_argument('-cputime', action=argparse.BooleanOptionalAction)
  parser.add_argument('-instructions', action=argparse.BooleanOptionalAction)
  parser.add_argument('-memory', action=argparse.BooleanOptionalAction)
  parser.add_argument('-diff', action=argparse.BooleanOptionalAction)
  args = parser.parse_args()

  num_runs,header,results = parse(args.filename)

  print(f'total number of benchmarks {len(results)}')
  print()

  for i in range(num_runs):
    cputime = sum([float(v[i][CPUTIME]) for k,v in results.items()]) if CPUTIME in header else None
    instructions = sum([int(v[i][INSTRUCTIONS]) for k,v in results.items()]) if INSTRUCTIONS in header else None
    memory = sum([float(v[i][MEMORY]) for k,v in results.items()]) if MEMORY in header else None

    def solved(row, i, val):
      return row[i][STATUS] == val

    def solved_unique(row, i, val):
      return row[i][STATUS] == val and len([j for j in range(num_runs) if i != j and row[j][STATUS] == val]) == 0

    unsat = sum([1 for k,v in results.items() if solved(v, i, TRUE)])
    unsat_unique = sum([1 for k,v in results.items() if solved_unique(v, i, TRUE)])
    sat = sum([1 for k,v in results.items() if solved(v, i, FALSE)])
    sat_unique = sum([1 for k,v in results.items() if solved_unique(v, i, FALSE)])

    run_str = f"run {i}"
    if args.all or args.unsat:
      run_str += f" unsat: {unsat} ({unsat_unique})"
    if args.all or args.sat:
      run_str += f" sat: {sat} ({sat_unique})"
    if args.all or args.cputime:
      run_str += " cputime: {:.2f} s".format(cputime)
    if args.all or args.instructions:
      run_str += f" instructions: {instructions} Mi"
    if args.all or args.memory:
      run_str += " memory: {:.2f} MB".format(memory)
    print(run_str)

  if args.all or args.diff:

    if num_runs != 2:
      print('-diff only works for 2 runs')
      exit(1)

    def pred(row, val1, val2):
      return row[0][STATUS] == val1 and row[1][STATUS] == val2

    pairs = [
      [TRUE, INS_LIMIT, 'run 0 uniquely proved'],
      [FALSE, INS_LIMIT, 'run 0 uniquely disproved'],
      [INS_LIMIT, TRUE, 'run 1 uniquely proved'],
      [INS_LIMIT, FALSE, 'run 1 uniquely disproved'],
      [TRUE, FALSE, 'run 0 unsound or run 1 incomplete'],
      [FALSE, TRUE, 'run 0 incomplete or run 1 unsound']
    ]

    for [v1,v2,n] in pairs:
      ks = [k for k,v in results.items() if pred(v, v1, v2)]
      print()
      print(f'{n}: {len(ks)}')
      for k in ks:
        print(k)

    print()
    print('other values')
    for k,v in results.items():
      if v[0][STATUS] != v[1][STATUS] and (v[0][STATUS] not in [TRUE, FALSE, INS_LIMIT] or v[1][STATUS] not in [TRUE, FALSE, INS_LIMIT]):
        print(f'{k} run 0 {v[0][STATUS]} run 1 {v[1][STATUS]}')
