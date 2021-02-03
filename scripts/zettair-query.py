#!/usr/bin/env python3

from paths import Paths

import argparse, os

parser = argparse.ArgumentParser(description='Query a Zettair index and display the n-best matches.')
parser.add_argument('-f', '--index-prefix', type=str, required=True, help='path to the Zettair index to query (excluding file suffixes)')
parser.add_argument('-n', '--n-best', type=int, default=10, help='the number of best matches to display (default: 10)')
parser.add_argument('-q', '--query', type=str, required=True, help='the query term')

args = parser.parse_args()

paths = Paths()

zettair_dir = paths.get('ZETTAIR-DIR')

zet_path = os.path.join(zettair_dir, 'zet')

os.system('%s -f %s -n %d --big-and-fast "%s"' % (zet_path, args.index_prefix, args.n_best, args.query))
