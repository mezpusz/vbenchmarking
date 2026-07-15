# This file is part of BenchExec, a framework for reliable benchmarking:
# https://github.com/sosy-lab/benchexec
#
# SPDX-FileCopyrightText: 2007-2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import benchexec
import benchexec.result as result

def in_output(str, output):
  for l in output:
    if str in l:
      return True
  return False

class Tool(benchexec.tools.template.BaseTool2):

    def name(self):
        return "GDV"

    def project_url(self):
        return "https://github.com/"

    def executable(self, tool_locator):
        return tool_locator.find_executable("gdv_wrapper.sh")

    def version(self, executable):
        return "1.0"

    def environment(self, executable):
        return {"keepEnv": {"TPTP": 1}}

    def cmdline(self, executable, options, task, rlimits):
        return [executable, *options, task.single_input_file]

    def determine_result(self, run):
        if in_output("FAILURE", run.output):
          return "FAILURE"
        if in_output("ERROR", run.output):
          return "ERROR"
        if in_output("WARNING", run.output):
          return "WARNING"
        return "OK"
