#!/usr/bin/env python3

import statistics, sys

SEP = '\t'
MEASUREMENTS = ['status', 'cputime (s)', 'walltime (s)', 'memory (MB)', 'szs-status']

if __name__ == "__main__":

  if len(sys.argv) != 2:
    print("syntax: stat.py <csv_file>")
    exit(1)

  csv_file = open(sys.argv[1]).read().splitlines()

  tools = csv_file[0].split(SEP)
  run_sets = csv_file[1].split(SEP)
  header = csv_file[2].split(SEP)

  num_runs = 0

  for i in range(1,len(header),len(MEASUREMENTS)):
    num_runs += 1
    for j,k in enumerate(range(i,i+len(MEASUREMENTS))):
      assert(MEASUREMENTS[j]==header[k])

  results = {}

  for row in csv_file[3:]:
    vals = row.split('\t')

    curr_benchmark = []
    for i in range(1,len(vals),len(MEASUREMENTS)):
      curr = {}
      for j,k in enumerate(range(i,i+len(MEASUREMENTS))):
        curr[header[k]] = vals[k]
      curr_benchmark.append(curr)

    results[vals[0]] = curr_benchmark

  print('total {}'.format(len(results)))

  for i in range(num_runs):
    mean_cputime = statistics.mean([float(v[i]['cputime (s)']) for k,v in results.items()])
    mean_memory = statistics.mean([float(v[i]['memory (MB)']) for k,v in results.items()])

    def solved(row, i, val):
      return row[i]['status'] == val

    def solved_unique(row, i, val):
      return row[i]['status'] == val and sum([1 for j in range(num_runs) if i != j and row[j]['status'] == val]) == 0

    unsat = sum([1 for k,v in results.items() if solved(v, i, 'true')])
    unsat_unique = sum([1 for k,v in results.items() if solved_unique(v, i, 'true')])
    sat = sum([1 for k,v in results.items() if solved(v, i, 'false')])
    sat_unique = sum([1 for k,v in results.items() if solved_unique(v, i, 'false')])

    print("run {} unsat: {} ({}) sat: {} ({}) mean cputime: {} mean memory: {}".format(i, unsat, unsat_unique, sat, sat_unique, mean_cputime, mean_memory))

