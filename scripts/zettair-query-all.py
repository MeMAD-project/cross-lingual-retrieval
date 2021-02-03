#!/usr/bin/env python3

from bs4 import BeautifulSoup
from os import path
from paths import Paths

import json, os, re

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

doc_topics = {}
relevant_docs = {}

with open(setting_original_path, mode='r', encoding='utf-8') as setting_original_file:
  setting_original = json.load(setting_original_file)
  
  for doc_id in setting_original:
    doc_topics[doc_id.strip()] = setting_original[doc_id]['relevant-topics']
    
    for topic_id in setting_original[doc_id]['relevant-topics']:
      if topic_id not in relevant_docs:
        relevant_docs[topic_id] = []
      
      relevant_docs[topic_id].append(doc_id)

models_dir = paths.get('MODELS-DIR')

for query_lang in ['en', 'de', 'fr']:
  for topic_id in topic_descriptions:
    topic_desc = topic_descriptions[topic_id][query_lang]
    
    os.system('./zettair-query.sh %s 50 "%s" > zettair-query-output.tmp' % (path.join(models_dir, 'setting-masked.zettair-index'), topic_desc))
    
    query_results = []
    
    with open('zettair-query-output.tmp', mode='r', encoding='utf-8') as query_output:
      for line in query_output:
        regex_search = re.search('^[0-9]+\. ([0-9]+)', line)
        if regex_search:
          query_results.append(regex_search.group(1))
    
    os.system('rm -f zettair-query-output.tmp')
    
    query_matches = [topic_id in doc_topics[doc_id] for doc_id in query_results]
    
    precision_at = {}
    recall_at = {}
    
    for n in [5, 10, 20, 50]:
      first_n_matches = query_matches[:min(n, len(query_matches))]
      
      precision_at[n] = float(len([match for match in first_n_matches if match])) / len(first_n_matches) \
                        if len(first_n_matches) > 0 else float(0)
      
      recall_at[n] = float(len([match for match in first_n_matches if match])) / len(relevant_docs[topic_id]) \
                     if len(relevant_docs[topic_id]) > 0 else float(0)
    
#    print('%d (%s)\n\tp@5: %.1f | p@10: %.1f | p@20: %.1f | p@50: %.1f\n\tr@5: %.1f | r@10: %.1f | r@20: %.1f | r@50: %.1f' % (topic_id, query_lang, precision_at[5], precision_at[10], precision_at[20], precision_at[50], recall_at[5], recall_at[10], recall_at[20], recall_at[50]))
    print('%d\t(%s)\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f' % (topic_id, query_lang, precision_at[5], precision_at[10], precision_at[20], precision_at[50], recall_at[5], recall_at[10], recall_at[20], recall_at[50]))
