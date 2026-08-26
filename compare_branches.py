#!/usr/bin/env python3

import argparse, subprocess, time, os

VAMPIREDIR = '/home/mhajdu/vampire'
BUILDDIR = os.path.join(VAMPIREDIR, 'cmake-build')
BENCHMARKINGDIR = '/home/mhajdu/vbenchmarking'
DRY_RUN = False

def run_cmd(cmd, cwd=None):
  print(f'running {cmd}')
  if DRY_RUN:
    return
  try:
    subprocess.check_call(cmd, shell=True, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  except subprocess.CalledProcessError as e:
    print(e.output)
    raise e

class Runner:
  def __init__(self, benchmark, run, remote, branch, timestamp):
    self.benchmark = benchmark
    self.run = run
    self.remote = remote
    self.branch = branch
    self.timestamp = timestamp # we need a timestamp for benchexec

  def __str__(self):
    return self.run_id()

  def fetch(self):
    run_cmd(f'git fetch {self.remote} {self.branch}', VAMPIREDIR)

  def run_id(self):
    runStr = f".{self.run}" if self.run else ""
    # replace slashes with dots in branch name to avoid bad filenames
    return f"{self.remote}.{self.branch.replace('/', '.')}{runStr}"

  def result_file(self):
    runStr = ""
    if self.run:
      runStr = f'.{self.run}'
    return f'results/{self.benchmark}.{self.run_id()}.{time.strftime("%Y-%m-%d_%H-%M-%S", self.timestamp)}.results{runStr}.xml.bz2'

  def summary_file(self):
    runStr = ""
    if self.run:
      runStr = f'.{self.run}'
    return f'results/{self.benchmark}.{time.strftime("%Y-%m-%d_%H-%M-%S", self.timestamp)}.results{runStr}.txt'

  def build_and_run(self):
    print(f'building {self.run_id()}...')
    self.fetch()
    run_cmd(f'git checkout FETCH_HEAD', VAMPIREDIR)
    run_cmd('cmake .', BUILDDIR)
    run_cmd('make -j60', BUILDDIR)
    run_cmd('./vampire --version', BUILDDIR)

    runOption = ""
    if self.run:
      runOption = f'-r "{self.run}"'

    print(f'running {self.run_id()}...')
    run_cmd(f'benchexec --no-container \
              -N 60 -c -1 \
              --tool-directory "{BUILDDIR}" \
              --name "{self.run_id()}" \
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

  run_cmd(f'python3 {BENCHMARKINGDIR}/stat.py -all \
    {BENCHMARKINGDIR}/results.table.csv > {runner1.summary_file()}')


def compare(benchmark, run, timestamp, remote1, branch1, remote2, branch2):
  runner1 = Runner(benchmark, run, remote1, branch1, timestamp)
  runner2 = Runner(benchmark, run, remote2, branch2, timestamp)

  # precheck that both branches exist
  runner1.fetch()
  runner2.fetch()

  runner1.build_and_run()
  runner2.build_and_run()

  results_for_run(runner1, runner2)


if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('benchmark')
  parser.add_argument('-remote1', default='origin')
  parser.add_argument('-branch1', default='master')
  parser.add_argument('-remote2', default='origin')
  parser.add_argument('-branch2')
  parser.add_argument('-runs')
  args = parser.parse_args()

  timestamp = time.gmtime()

  if args.runs:
    for run in args.runs.split(','):
      compare(args.benchmark, run, timestamp, args.remote1, args.branch1, args.remote2, args.branch2)
  else:
    compare(args.benchmark, None, timestamp, args.remote1, args.branch1, args.remote2, args.branch2)
