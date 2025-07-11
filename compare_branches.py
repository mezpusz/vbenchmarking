#!/usr/bin/env python3

import argparse, subprocess, time, os

VDIR = '/home/mhajdu/vampire'
CMAKEDIR = os.path.join(VDIR, 'cmake-build')

def run_cmd(cmd, cwd=None):
  subprocess.check_call(cmd, shell=True, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def build_and_run(branch, benchmark_file, run, now):
  print(f'building {branch}...')
  run_cmd('git fetch', VDIR)
  run_cmd(f'git checkout {branch}', VDIR)
  run_cmd('git rebase', VDIR)

  run_cmd('cmake .', CMAKEDIR)
  run_cmd('make -j60', CMAKEDIR)
  subprocess.check_output('./vampire --version', shell=True, cwd=CMAKEDIR)

  print(f'running {branch}...')
  run_cmd(f'benchexec --no-container \
            --numOfThreads 60 \
            --tool-directory "{CMAKEDIR}" \
            --name "{branch}" \
            --startTime "{now}" \
            "{benchmark_file}"')


def results_for_run(run, branch1, branch2, now_out):
  print(f'results for {run}')
  run_cmd(f'table-generator -x vbenchmarking/results.xml -f csv -q \
    results/tptp-regression.{branch1}.{now_out}.results.{run}.xml.bz2 \
    results/tptp-regression.{branch2}.{now_out}.results.{run}.xml.bz2')

  subprocess.check_call('python3 vbenchmarking/stat.py -all vbenchmarking/results.table.csv', shell=True)


if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('benchmark_file')
  parser.add_argument('-branch1', default='master')
  parser.add_argument('-branch2')
  parser.add_argument('-run')
  args = parser.parse_args()

  if len(subprocess.check_output(f'git ls-remote --heads origin "refs/heads/{args.branch1}"', shell=True, cwd=VDIR)) == 0:
    raise ValueError(f'Branch {args.branch1} does not exist')
  if len(subprocess.check_output(f'git ls-remote --heads origin "refs/heads/{args.branch2}"', shell=True, cwd=VDIR)) == 0:
    raise ValueError(f'Branch {args.branch2} does not exist')

  now = time.gmtime()
  now_in = time.strftime("%Y-%m-%d %H:%M:%S", now)
  now_out = time.strftime("%Y-%m-%d_%H-%M-%S", now)

  build_and_run(args.branch1, args.benchmark_file, args.run, now_in)
  build_and_run(args.branch2, args.benchmark_file, args.run, now_in)

  results_for_run('discount', args.branch1, args.branch2, now_out)
  results_for_run('otter', args.branch1, args.branch2, now_out)
