
import argparse, os

spc_str = '% SPC      : '

if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('tptp_dir')
  parser.add_argument('output_dir')
  args = parser.parse_args()

  if not os.path.isdir(args.tptp_dir):
    print(f'TPTP dir {args.tptp_dir} is not a directory')
    exit(1)

  if not os.path.isdir(args.tptp_dir):
    print(f'Output dir {args.output_dir} is not a directory')
    exit(1)

  problems_dir = os.path.join(args.tptp_dir, 'Problems')

  if not os.path.isdir(problems_dir):
    print(f'TPTP problems dir {problems_dir} does not exist')
    exit(1)

  result = dict()

  for cat in os.listdir(problems_dir):
    cat_dir = os.path.join(problems_dir, cat)

    if not os.path.isdir(cat_dir):
      print(f'Found file in root of Problems/ directory')
      continue

    print(f'Parsing category {cat}')

    for prb in os.listdir(cat_dir):
      if not prb.endswith('.p'):
        print(f'  Skipping {prb}')
        continue

      prb_file = open(os.path.join(cat_dir, prb))

      prb_spc = None
      for line in prb_file:
        if line.startswith(spc_str):
          prb_spc = line[len(spc_str):]
          break

      if prb_spc is None:
        print(f'  Problem {prb} has no SPC line')

      prb_cat = prb_spc[:prb_spc.find('_')]
      result.setdefault(prb_cat, list())
      result[prb_cat].append(os.path.join(cat,prb))

  for k,v in result.items():
    print(f'Category {k} has {len(v)} values')
    with open(os.path.join(args.output_dir, f'tptp_{k}.set'), 'w') as output_file:
      for e in sorted(v):
        full_e = os.path.join('/data/benchmarks/TPTP/Problems', e)
        output_file.write(full_e + os.linesep)
