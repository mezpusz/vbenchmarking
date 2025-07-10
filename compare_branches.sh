#!/bin/bash

set -euo pipefail

VDIR="/home/mhajdu/vampire"

branch1="master"
branch2="fix-proc-encompassment-corner-cases"

benchmark_file="/home/mhajdu/vbenchmarking/tptp-regression.xml"

curr_date=$(date +"%Y-%m-%d %H:%M:%S")
curr_date_conv=$(date -d "${curr_date}" +"%Y-%m-%d_%H-%M-%S")

pushd "${VDIR}"
  if [ $(git ls-remote --heads origin "refs/heads/${branch1}" | wc -l) -eq "0" ]; then
    echo "ERROR: First branch does not exist"
    exit 1
  fi

  if [ $(git ls-remote --heads origin "refs/heads/${branch2}" | wc -l) -eq "0" ]; then
    echo "ERROR: Second branch does not exist"
    exit 1
  fi
popd

build_and_run()
{
  pushd "${VDIR}"
    git fetch
    git checkout "${1}"
    git rebase

    pushd cmake-build
      cmake .
      make -j60
      ./vampire --version
    popd
  popd

  benchexec --no-container \
            --numOfThreads 60 \
            --tool-directory "${VDIR}/cmake-build/" \
            --startTime "${curr_date}" \
            --name "${1}" \
            "${benchmark_file}"
}

build_and_run ${branch1}
build_and_run ${branch2}

table-generator -x vbenchmarking/results.xml -f csv -q \
  results/tptp-regression.${branch1}.${curr_date_conv}.results.discount.xml.bz2 \
  results/tptp-regression.${branch2}.${curr_date_conv}.results.discount.xml.bz2

python3 vbenchmarking/stat.py -all vbenchmarking/results.table.csv

table-generator -x vbenchmarking/results.xml -f csv -q \
  results/tptp-regression.${branch1}.${curr_date_conv}.results.otter.xml.bz2 \
  results/tptp-regression.${branch2}.${curr_date_conv}.results.otter.xml.bz2

python3 vbenchmarking/stat.py -all vbenchmarking/results.table.csv