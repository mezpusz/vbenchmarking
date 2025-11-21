#!/usr/bin/env python3

import argparse
from resultparser import parse, STATUS, CPUTIME, MEMORY, INSTRUCTIONS

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

    unsat = sum([1 for k,v in results.items() if solved(v, i, 'true')])
    unsat_unique = sum([1 for k,v in results.items() if solved_unique(v, i, 'true')])
    sat = sum([1 for k,v in results.items() if solved(v, i, 'false')])
    sat_unique = sum([1 for k,v in results.items() if solved_unique(v, i, 'false')])

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
    print()
    print('diff:')
    for k,v in results.items():
      if any(any(v[i][STATUS] != v[j][STATUS] for j in range(num_runs) if i != j) for i in range(num_runs)):
        diff_str = f'{k}'
        for i in range(num_runs):
          diff_str += f' {i} {v[i][STATUS]}'
        print(diff_str)
