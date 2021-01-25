#!/usr/bin/env python3

import json, os, re

topics = {}

with open('topics.tsv', mode='r', encoding='utf-8') as topics_file:
  for topic_row in topics_file:
    topic_id, topic_desc_en, topic_desc_de, topic_desc_fr = topic_row.split('\t')
    topics[int(topic_id)] = {'en': topic_desc_en.strip(), 'de': topic_desc_de.strip(), 'fr': topic_desc_fr.strip()}

doc_topics = {}
relevant_docs = {}

with open('setting-original.json', mode='r', encoding='utf-8') as setting_original_file:
  setting_original = json.load(setting_original_file)
  
  for doc_id in setting_original:
    doc_topics[doc_id.strip()] = setting_original[doc_id]['relevant-topics']
    
    for topic_id in setting_original[doc_id]['relevant-topics']:
      if topic_id not in relevant_docs:
        relevant_docs[topic_id] = []
      
      relevant_docs[topic_id].append(doc_id)

for query_lang in ['en', 'de', 'fr']:
  for topic_id in topics:
    topic_desc = topics[topic_id][query_lang]
    
    os.system('./zettair-query.sh setting-masked.zettair-index 50 "%s" > zettair-query-output.tmp' % topic_desc)
    
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
