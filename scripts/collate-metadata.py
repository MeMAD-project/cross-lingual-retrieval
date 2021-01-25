#!/usr/bin/env python3

from os import path
from bs4 import BeautifulSoup

import json, zipfile

topic_ids = [str(topic_id) for topic_id in range(71, 121)]

dataset_dir = path.join('/scratch', 'project_2000945', 'retrieval-data', 'wiki-retrieval-2010')

qrels_path = path.join(dataset_dir, 'wikipedia_topics_2011', 'wikipedia_2011.qrels')
cime_features_path = path.join(dataset_dir, 'features', 'cime.txt')
image_metadata_path = path.join(dataset_dir, 'all_text', 'metadata.zip')
topic_metadata_path = path.join(dataset_dir, 'wikipedia_topics_2011', 'wikipedia_topics_2011_v3.xml')

output_path = path.join(dataset_dir, 'memad', 'setting-original.json')
output = {}

print('Caching qrels...')

relevances = {}

with open(qrels_path, mode='r', encoding='utf-8') as qrels_file:
  for qrels_line in qrels_file:
    topic_id, _, image_id, relevance = qrels_line.split()
    
    topic_id = int(topic_id)
    image_id = int(image_id)
    
    if image_id not in relevances:
        relevances[image_id] = []
    
    if relevance == '1':
      relevances[image_id].append(topic_id)

print('...done!')

print('Collating topic relevances...')

with open(cime_features_path, mode='r', encoding='utf-8') as visual_features_file:
  for visual_features_line in visual_features_file:
    image_id = int(visual_features_line.split()[0])
    
    output[image_id] = {'relevant-topics': relevances[image_id] if image_id in relevances else []}

print('...done!')

print('Collating topic metadata...')

topic_descriptions = {}
topic_narratives = {}

with open(topic_metadata_path, mode='r', encoding='iso-8859-1') as topic_metadata_file:
  topic_metadata = BeautifulSoup(topic_metadata_file, features='lxml-xml')
  
  for topic in topic_metadata.find_all('topic'):
    topic_id = int(topic.number.string.strip())
    
    try:
      topic_narratives[topic_id] = topic.narrative.string.strip()
      topic_descriptions[topic_id] = {'de': None, 'en': None, 'fr': None}
      
      for title in topic.find_all('title'):
        topic_descriptions[topic_id][title['xml:lang']] = title.string.strip()
    
    except:
      print('Metadata parse error for topic #%d!' % topic_id)
  
  for image_id in output:
    if output[image_id]['relevant-topics']:
      if 'metadata-en' not in output[image_id]:
        output[image_id]['metadata-en'] = {}
      
      output[image_id]['metadata-en']['topic-narrative'] = [topic_narratives[topic_id] for topic_id in output[image_id]['relevant-topics']]
    
      for lang in topic_descriptions[topic_id]:
        if ('metadata-' + lang) not in output[image_id]:
          output[image_id]['metadata-' + lang] = {}
        
        output[image_id]['metadata-' + lang]['topic-description'] = [topic_descriptions[topic_id][lang] for topic_id in output[image_id]['relevant-topics']]

print('...done!')

print('Collating image metadata...')

with zipfile.ZipFile(image_metadata_path, mode='r') as image_metadata_archive:
  ct = 0
  for filename in image_metadata_archive.namelist():
    ct += 1
    if ct % 1000 == 0:
      print('%dk-' % int(ct / 1000))
    if path.splitext(filename)[-1] == '.xml':
      image_id = int(path.splitext(path.basename(filename))[0])
      
      if image_id in output:
        with image_metadata_archive.open(filename) as image_metadata_file:
          image_metadata = BeautifulSoup(image_metadata_file, features='lxml-xml')
          
          try:
            for text in image_metadata.find_all('text'):
              lang = text['xml:lang']
              if ('metadata-' + lang) not in output[image_id]:
                output[image_id]['metadata-' + lang] = {}
              
              if text.description.string:
                output[image_id]['metadata-' + lang]['image-description'] = text.description.string.strip()
              if text.comment.string:
                output[image_id]['metadata-' + lang]['image-comment'] = text.comment.string.strip()
              if text.caption.string:
                output[image_id]['metadata-' + lang]['image-caption'] = text.caption.string.strip()
          
          except:
            print('Metadata parse error for image #%d!' % image_id)

print('...done!')

print('Generating output file...')

with open(output_path, mode='w', encoding='utf-8') as output_file:
  json.dump(output, output_file, indent='\t', sort_keys=True, ensure_ascii=False)

print('...done!')
