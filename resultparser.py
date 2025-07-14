
SEPARATOR = '\t'

STATUS = 'status'
SZSSTATUS = 'szs-status'
CPUTIME = 'cputime (s)'
MEMORY = 'memory (MB)'
INSTRUCTIONS = 'instruction-count'

MEASUREMENTS = [STATUS, SZSSTATUS, CPUTIME, MEMORY, INSTRUCTIONS]

def parse(filename):
  csv_file = open(filename).read().splitlines()

  tools = csv_file[0].split(SEPARATOR)
  run_sets = csv_file[1].split(SEPARATOR)
  headers = csv_file[2].split(SEPARATOR)

  if len(headers) <= 1:
    raise ValueError('Table does not contain enough columns')

  one_header = []
  for i in range(1,len(headers)):
    # iterate until we find the second header
    if len(one_header) > 0 and headers[i] == one_header[0]:
      break
    one_header.append(headers[i])

  hlen = len(one_header)
  num_runs = 1

  for i in range(1+hlen,len(headers),hlen):
    num_runs += 1
    for j,k in enumerate(range(i,i+hlen)):
      if one_header[j] != headers[k]:
        raise ValueError('All runs should have the same header')

  results = {}

  for row in csv_file[3:]:
    vals = row.split(SEPARATOR)

    curr_benchmark = []
    for i in range(1,len(vals),hlen):
      curr = {}
      for j,k in enumerate(range(i,i+hlen)):
        curr[headers[k]] = vals[k]
      curr_benchmark.append(curr)

    results[vals[0]] = curr_benchmark

  return num_runs,one_header,results
