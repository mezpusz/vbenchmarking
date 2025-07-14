#!/usr/bin/env python3

import argparse, zipfile, os
from resultparser import parse, STATUS

if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('resultfile')
  parser.add_argument('logfiles')
  args = parser.parse_args()

  num_runs,header,results = parse(args.resultfile)
  archive = zipfile.ZipFile(args.logfiles, 'r')
  archive_prefix = args.logfiles[:-4]
  print(archive_prefix)

  if num_runs != 1:
    raise ValueError('There should be only one run in result')

  error_counts = {}

  for benchmark,values in results.items():

    for i in range(num_runs):
      if not values[i][STATUS].startswith('ERROR'):
        continue

      if values[i][STATUS] not in error_counts:
        error_counts[values[i][STATUS]] = 0
      error_counts[values[i][STATUS]] += 1

      # print(f'Benchmark {benchmark} error {values[i][STATUS]}')

      # log = archive.read(os.path.join(args.logfiles[:-4], 'stable.'+benchmark[4:]+'.log'))
      # print(log)

      # print(benchmark)
      # print(values)

  print(error_counts)