#!/usr/bin/env python3

import argparse, subprocess, time, os

VAMPIREDIR = '/home/mhajdu/vampire'
BUILDDIR = os.path.join(VAMPIREDIR, 'cmake-build')
BENCHMARKINGDIR = '/home/mhajdu/vbenchmarking'

def run_cmd(cmd, cwd=None):
  print(f'running {cmd}')
  try:
    subprocess.check_call(cmd, shell=True, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  except subprocess.CalledProcessError as e:
    print(e.output)
    raise e

class Runner:
  def __init__(self, benchmark, run, branch):
    self.benchmark = benchmark
    self.run = run
    self.branch = branch
    self.timestamp = time.gmtime() # we need a timestamp for benchexec

  def __str__(self):
    return f'{self.benchmark} {self.run} {self.branch}'

  def check_branch(self):
    return len(subprocess.check_output(f'git ls-remote --heads origin "refs/heads/{args.branch1}"', shell=True, cwd=VAMPIREDIR)) > 0

  def result_file(self):
    runStr = ""
    if self.run:
      runStr = f'.{self.run}'
    return f'results/{self.benchmark}.{self.branch}.{time.strftime("%Y-%m-%d_%H-%M-%S", self.timestamp)}.results{runStr}.xml.bz2'

  def build_and_run(self):
    print(f'building {self.branch}...')
    run_cmd('git fetch', VAMPIREDIR)
    run_cmd(f'git checkout {self.branch}', VAMPIREDIR)
    run_cmd('git rebase', VAMPIREDIR)
    run_cmd('cmake .', BUILDDIR)
    run_cmd('make -j60', BUILDDIR)
    subprocess.check_output('./vampire --version', shell=True, cwd=BUILDDIR)

    runOption = ""
    if self.run:
      runOption = f'-r "{self.run}"'

    print(f'running {self.branch}...')
    run_cmd(f'benchexec --no-container \
              --numOfThreads 60 \
              --tool-directory "{BUILDDIR}" \
              --name "{self.branch}" \
              {runOption} \
              --startTime "{time.strftime("%Y-%m-%d %H:%M:%S", self.timestamp)}" \
              "{os.path.join(BENCHMARKINGDIR, "benchmarks", self.benchmark)}.xml"')
    print(f'result file is {self.result_file()}')


def results_for_run(runner1, runner2):
  print(f'results for {runner1} and {runner2}')
  assert(runner1.benchmark == runner2.benchmark)
  assert(runner1.run == runner2.run)
  run_cmd(f'table-generator -x {BENCHMARKINGDIR}/results.xml -f csv -q \
    {runner1.result_file()} {runner2.result_file()}')

  subprocess.check_call(f'python3 {BENCHMARKINGDIR}/stat.py -all {BENCHMARKINGDIR}/results.table.csv', shell=True)


if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('benchmark')
  parser.add_argument('-branch1', default='master')
  parser.add_argument('-branch2')
  parser.add_argument('-run')
  args = parser.parse_args()

  runner1 = Runner(args.benchmark, args.run, args.branch1)
  runner2 = Runner(args.benchmark, args.run, args.branch2)

  if not runner1.check_branch():
    raise ValueError(f'Branch {args.branch1} does not exist')
  if not runner2.check_branch():
    raise ValueError(f'Branch {args.branch2} does not exist')

  runner1.build_and_run()
  runner2.build_and_run()

  results_for_run(runner1, runner2)
