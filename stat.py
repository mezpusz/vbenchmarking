#!/usr/bin/env python3

import argparse

SEP = '\t'
MEASUREMENTS = ['status', 'cputime (s)', 'walltime (s)', 'memory (MB)', 'instruction-count', 'szs-status']
MLEN = len(MEASUREMENTS)

if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('filename')
  parser.add_argument('-all', action=argparse.BooleanOptionalAction)
  parser.add_argument('-unsat', action=argparse.BooleanOptionalAction)
  parser.add_argument('-sat', action=argparse.BooleanOptionalAction)
  parser.add_argument('-cputime', action=argparse.BooleanOptionalAction)
  parser.add_argument('-instructions', action=argparse.BooleanOptionalAction)
  parser.add_argument('-memory', action=argparse.BooleanOptionalAction)
  args = parser.parse_args()

  csv_file = open(args.filename).read().splitlines()

  tools = csv_file[0].split(SEP)
  run_sets = csv_file[1].split(SEP)
  header = csv_file[2].split(SEP)

  num_runs = 0

  for i in range(1,len(header),MLEN):
    num_runs += 1
    for j,k in enumerate(range(i,i+MLEN)):
      assert(MEASUREMENTS[j]==header[k])

  results = {}

  for row in csv_file[3:]:
    vals = row.split('\t')

    curr_benchmark = []
    for i in range(1,len(vals),MLEN):
      curr = {}
      for j,k in enumerate(range(i,i+MLEN)):
        curr[header[k]] = vals[k]
      curr_benchmark.append(curr)

    results[vals[0]] = curr_benchmark

  print(f'total number of benchmarks {len(results)}')
  print()

  for i in range(num_runs):
    cputime = sum([float(v[i]['cputime (s)']) for k,v in results.items()])
    instructions = sum([int(v[i]['instruction-count']) for k,v in results.items()])
    memory = sum([float(v[i]['memory (MB)']) for k,v in results.items()])

    def solved(row, i, val):
      return row[i]['status'] == val

    def solved_unique(row, i, val):
      return row[i]['status'] == val and len([j for j in range(num_runs) if i != j and row[j]['status'] == val]) == 0

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
      run_str += f" cputime: {cputime} s"
    if args.all or args.instructions:
      run_str += f" instructions: {instructions} Mi"
    if args.all or args.memory:
      run_str += f" memory: {memory} MB"
    print(run_str)

