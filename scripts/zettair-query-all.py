#!/usr/bin/env python3

from bs4 import BeautifulSoup
from os import path
from paths import Paths
from copy import copy

import json, os, re, argparse
import numpy as np

text_search_indices = [
  'setting-original.zettair-index',
  'setting-original.autocaps.zettair-index',
  'setting-original.translations.zettair-index',
  'setting-original.fully-enriched.zettair-index',
  'setting-masked.zettair-index',
  'setting-masked.autocaps.zettair-index',
  'setting-masked.translations.zettair-index',
  'setting-masked.fully-enriched.zettair-index'
]

langs = ['en', 'de', 'fr', 'vi']
langs_test_all = copy(langs)
for i in range(len(langs)):
  for j in range(i+1, len(langs)):
    langs_test_all.append(langs[i]+'+'+langs[j])
for i in range(len(langs)):
  for j in range(i+1, len(langs)):
    for k in range(j+1, len(langs)):
      langs_test_all.append(langs[i]+'+'+langs[j]+'+'+langs[k])
langs_test_all.append('en+de+fr+vi')
langs_test_all=','.join(langs_test_all)
      
parser = argparse.ArgumentParser(description='ZET query and combination with visual retrieval.')
parser.add_argument('--languages', type=str, default=langs_test_all,
                    help='comma-separated list of languages and their plus-separated combinations, '+
                    ' default=%(default)s')
parser.add_argument('--results', type=int, default=50,
                    help='number of textual retrieval results requested from zet, default=%(default)s')
parser.add_argument('--negatives', type=str, default='implicit',
                    choices=['implicit', 'explicit'],
                    help='either "implicit" or "explicit", default=%(default)s')
parser.add_argument('--verbose', action='store_true',
                    help='show also topic-wise results')
parser.add_argument('--search-index', type=str, default='setting-masked.zettair-index',
                    help='the prefix of the search index (under `../models\') to use when retrieving results from text queries, default=%(default)s')
args = parser.parse_args()

langs_test = args.languages.split(',')

n_zet_results = args.results

paths = Paths()

dataset_dir = paths.get('WIKIDATA-DIR')

topic_metadata_path = path.join(dataset_dir, 'wikipedia_topics_2011', 'wikipedia_topics_2011_v3.xml')

topic_descriptions = {}

with open(topic_metadata_path, mode='r', encoding='iso-8859-1') as topic_metadata_file:
  topic_metadata = BeautifulSoup(topic_metadata_file, features='lxml-xml')

  for topic in topic_metadata.find_all('topic'):
    topic_id = int(topic.number.string.strip())

    try:
      topic_descriptions[topic_id] = {'de': None, 'en': None, 'fr': None}

      for title in topic.find_all('title'):
        topic_descriptions[topic_id][title['xml:lang']] = title.string.strip()

    except:
      print('Metadata parse error for topic #%d!' % topic_id)

data_dir = paths.get('DATA-DIR')

setting_original_path = path.join(data_dir, 'setting-original.json')

doc_topics_positive = {}
doc_topics_negative = {}
relevant_docs = {}

#print(setting_original_path)
with open(setting_original_path, mode='r', encoding='utf-8') as setting_original_file:
  setting_original = json.load(setting_original_file)
  
  for doc_id in setting_original:
    doc_topics_positive[doc_id.strip()] = setting_original[doc_id]['relevant-topics']
    doc_topics_negative[doc_id.strip()] = setting_original[doc_id]['non-relevant-topics']
    
    for topic_id in setting_original[doc_id]['relevant-topics']:
      if topic_id not in relevant_docs:
        relevant_docs[topic_id] = []
      
      relevant_docs[topic_id].append(doc_id)

visuals_dir = paths.get('VISUALS-DIR')
best_visual_path = path.join(visuals_dir, 'best-visual-1000.csv')

vis = {}
with open(best_visual_path) as visual:
  for l in visual:
    m = re.match('query-(.*),0+(.*),(.*)', l)
    assert m
    q = m.group(1)
    i = m.group(2)
    v = m.group(3)
    #print(q, i, v)
    q = int(q)
    if not q in vis:
      vis[q] = []
    vis[q].append(i)

def one_zet_result(q, n):
    os.system('./zettair-query.py --index-prefix %s --n-best %d --query "%s" > zettair-query-output.tmp'
              % (path.join(models_dir, args.search_index), n, q))

    res = []

    with open('zettair-query-output.tmp', mode='r', encoding='utf-8') as query_output:
      for line in query_output:
        regex_search = re.search('^[0-9]+\. ([0-9]+)', line)
        if regex_search:
          res.append(regex_search.group(1))

    os.system('rm -f zettair-query-output.tmp')
    return res

def filter_unknowns(l, t):
  if args.negatives=='implicit':
    return l
  r = []
  for i in l:
    if t in doc_topics_positive[i] or t in doc_topics_negative[i]:
      r.append(i)
  return r

def fusion(r):
  a = set()
  for l, x in r:
    for j in x:
      a.add(j)
  z = [ 1.0/(len(i[1])+1) for i in r]
  b = {}
  for i in a:
    b[i] = copy(z)

  # print(len(r[0][1]), len(r[1][1]), len(a), z)

  for x in range(len(r)):
    for i, j in enumerate(r[x][1]):
      b[j][x] = 1.0/(i+1)

  for i, l in b.items():
    v = np.sum(l)
    b[i] = v

  s = sorted(b, reverse=True, key=lambda i:b[i])
  #print(s)
  #for i in s:
  #  print(i, b[i])
  return s
    
models_dir = paths.get('MODELS-DIR')

avg_res = []

for query_lang in langs_test:
  avg = [0] * 8
  ll = query_lang.split('+')
  
  trec_res = open('trec.' + args.search_index + '.'+query_lang+'.top', 'w')

  for topic_id in topic_descriptions:
    qres = []
    for l in ll:
      if l=='vi':
        qr = vis[topic_id]
      else:
        topic_desc = topic_descriptions[topic_id][l]
        qr = one_zet_result(topic_desc, n_zet_results)

      qr = filter_unknowns(qr, topic_id)
      qres.append((l, qr))

    if len(qres)==1:
      query_results = qres[0][1]
    else:
      query_results = fusion(qres)
      
    # print(topic_id, query_lang, len(query_results), query_results[:5])

    ii = 1
    for i in query_results:
      print(topic_id, 'iter', i, 'rank', 1.0/ii, query_lang, file=trec_res)
      ii += 1
      
    if args.negatives=='implicit':
      query_matches = [topic_id in doc_topics_positive[doc_id] for doc_id in query_results]
    else: # 'explicit'
      query_matches = []
      for doc_id in query_results:
        if topic_id in doc_topics_positive[doc_id]:
          query_matches.append(True)
        elif topic_id in doc_topics_negative[doc_id]:
          query_matches.append(False)

    # print(len(query_matches), query_matches)
    
    precision_at = {}
    recall_at = {}
    
    for n in [5, 10, 20, 50]:
      first_n_matches = query_matches[:min(n, len(query_matches))]
      
      precision_at[n] = float(len([match for match in first_n_matches if match])) / len(first_n_matches) \
                        if len(first_n_matches) > 0 else float(0)
      
      recall_at[n] = float(len([match for match in first_n_matches if match])) / len(relevant_docs[topic_id]) \
                     if len(relevant_docs[topic_id]) > 0 else float(0)
    
      #    print('%d (%s)\n\tp@5: %.1f | p@10: %.1f | p@20: %.1f | p@50: %.1f\n\tr@5: %.1f | r@10: %.1f | r@20: %.1f | r@50: %.1f' % (topic_id, query_lang, precision_at[5], precision_at[10], precision_at[20], precision_at[50], recall_at[5], recall_at[10], recall_at[20], recall_at[50]))

    if args.verbose:
      print('%d\t(%s)\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f'
            % (topic_id, query_lang,
               precision_at[5], precision_at[10], precision_at[20], precision_at[50],
               recall_at[5], recall_at[10], recall_at[20], recall_at[50]))

    avg[0] +=  precision_at[5]
    avg[1] +=  precision_at[10]
    avg[2] +=  precision_at[20]
    avg[3] +=  precision_at[50]
    avg[4] +=  recall_at[5]
    avg[5] +=  recall_at[10]
    avg[6] +=  recall_at[20]
    avg[7] +=  recall_at[50]

  for i in range(8):
    avg[i] /= 50
  avg_res.append((query_lang, avg))

for query_lang, avg in avg_res:
  print('%s\t(%s)\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f' %
        ('avg', query_lang, avg[0], avg[1], avg[2], avg[3],
         avg[4], avg[5], avg[6], avg[7]))
