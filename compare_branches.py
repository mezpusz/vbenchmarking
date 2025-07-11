#!/usr/bin/env python3

import argparse, subprocess, time, os

VAMPIREDIR = '/home/mhajdu/vampire'
BUILDDIR = os.path.join(VAMPIREDIR, 'cmake-build')
BENCHMARKINGDIR = '/home/mhajdu/vbenchmarking'

def run_cmd(cmd, cwd=None):
  try:
    subprocess.check_call(cmd, shell=True, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  except subprocess.CalledProcessError as e:
    print(e.output)
    raise e

def build_and_run(benchmark, run, branch, now_in):
  print(f'building {branch}...')
  run_cmd('git fetch', VAMPIREDIR)
  run_cmd(f'git checkout {branch}', VAMPIREDIR)
  run_cmd('git rebase', VAMPIREDIR)

  run_cmd('cmake .', BUILDDIR)
  run_cmd('make -j60', BUILDDIR)
  subprocess.check_output('./vampire --version', shell=True, cwd=BUILDDIR)

  print(f'running {branch}...')
  run_cmd(f'benchexec --no-container \
            --numOfThreads 60 \
            --tool-directory "{BUILDDIR}" \
            --name "{branch}" \
            -r "{run}" \
            --startTime "{now_in}" \
            "{os.path.join(BENCHMARKINGDIR, benchmark)}.xml"')


def results_for_run(benchmark, run, branch1, branch2, now_out):
  print(f'results for {run}')
  run_cmd(f'table-generator -x {BENCHMARKINGDIR}/results.xml -f csv -q \
    results/{benchmark}.{branch1}.{now_out}.results.{run}.xml.bz2 \
    results/{benchmark}.{branch2}.{now_out}.results.{run}.xml.bz2')

  subprocess.check_call(f'python3 {BENCHMARKINGDIR}/stat.py -all {BENCHMARKINGDIR}/results.table.csv', shell=True)


if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('benchmark')
  parser.add_argument('-branch1', default='master')
  parser.add_argument('-branch2')
  parser.add_argument('-run')
  args = parser.parse_args()

  if len(subprocess.check_output(f'git ls-remote --heads origin "refs/heads/{args.branch1}"', shell=True, cwd=VAMPIREDIR)) == 0:
    raise ValueError(f'Branch {args.branch1} does not exist')
  if len(subprocess.check_output(f'git ls-remote --heads origin "refs/heads/{args.branch2}"', shell=True, cwd=VAMPIREDIR)) == 0:
    raise ValueError(f'Branch {args.branch2} does not exist')

  now = time.gmtime()
  now_in = time.strftime("%Y-%m-%d %H:%M:%S", now)
  now_out = time.strftime("%Y-%m-%d_%H-%M-%S", now)

  build_and_run(args.benchmark, args.run, args.branch1, now_in)
  build_and_run(args.benchmark, args.run, args.branch2, now_in)

  results_for_run(args.benchmark, args.run, args.branch1, args.branch2, now_out)
