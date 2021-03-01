#!/usr/bin/env python3

from json2trec import JSON2TREC
from os import path
from paths import Paths

import json

paths = Paths()

data_dir = paths.get('DATA-DIR')

json2trec = JSON2TREC()

## Converts a JSON-formatted metadata collection to the TREC format for indexing.
##
def convert_json_to_trec(json_path):
  trec_path = path.splitext(json_path)[0] + '.trec'
  json2trec.convert(json_path, trec_path)


## Reduces each item with multilingual metadata to keep metadata in one language
## only, prioritizing languages to keep the distribution as uniform as possible.
##
def mask_setting(input_path, output_path):
  print('Generating `%s`...' % path.basename(output_path))

  print('...parsing input metadata...')

  with open(input_path, mode='r', encoding='utf-8') as input_file:
    setting = json.load(input_file)

  print('...masking metadata on images with multilingual metadata...')

  metadata_tally = {
    'metadata-de': 0,
    'metadata-en': 0,
    'metadata-fr': 0
  }

  for image_id in sorted(list(setting.keys()), key=lambda k: int(k)):
    image_data = setting[image_id]

    stratum_priority_order = sorted(metadata_tally.keys(), key=lambda stratum: metadata_tally[stratum])

    for stratum in image_data:
      if stratum.startswith('metadata'):
        image_data[stratum].pop('topic-description', None)
        image_data[stratum].pop('topic-narrative', None)

    for priority_stratum in stratum_priority_order:
      if priority_stratum in image_data and image_data[priority_stratum] != {}:
        for other_stratum in image_data:
          if other_stratum != priority_stratum and other_stratum.startswith('metadata'):
            image_data[other_stratum] = {}

        metadata_tally[priority_stratum] += 1
        break

  print('...generating output file...')

  with open(output_path, mode='w', encoding='utf-8') as output_file:
    json.dump(setting, output_file, indent='\t', sort_keys=True, ensure_ascii=False)

  print('...final metadata tally:\n\t%s' % '\n\t'.join(['\'%s\': %d' % (stratum, metadata_tally[stratum]) for stratum in metadata_tally]))

## Adds automatically generated image captions as additional metadata
## for each item in the language(s) that it already has metadata for.
##
def autocap_setting(input_path, output_path):
  print('Generating `%s`...' % path.basename(output_path))

  print('...caching automatically-generated captions...')
  
  autocaps = {}
  
  autocaps_path = path.join(data_dir, 'en-autocaps.tsv')
  
  with open(autocaps_path, mode='r', encoding='utf-8') as autocaps_file:
    for autocaps_line in autocaps_file:
      image_id, autocap_en, autocap_de, autocap_fr = autocaps_line.split('\t')
      
      autocaps[image_id] = {'de': autocap_de,
                            'en': autocap_en,
                            'fr': autocap_fr}
  
  print('...parsing input metadata...')

  with open(input_path, mode='r', encoding='utf-8') as input_file:
    setting = json.load(input_file)

  print('...adding automatically-generated captions to existing metadata...')
  
  added_autocaps_tally = {
    'de': 0,
    'en': 0,
    'fr': 0
  }
  
  for image_id in sorted(list(setting.keys()), key=lambda k: int(k)):
    image_data = setting[image_id]
    
    if 'metadata-de' in image_data and image_data['metadata-de']:
      image_data['metadata-de']['auto-caption'] = autocaps[image_id]['de']
      added_autocaps_tally['de'] += 1
    
    if 'metadata-en' in image_data and image_data['metadata-en']:
      image_data['metadata-en']['auto-caption'] = autocaps[image_id]['en']
      added_autocaps_tally['en'] += 1
    
    if 'metadata-fr' in image_data and image_data['metadata-fr']:
      image_data['metadata-fr']['auto-caption'] = autocaps[image_id]['fr']
      added_autocaps_tally['fr'] += 1
  
  print('...generating output file...')

  with open(output_path, mode='w', encoding='utf-8') as output_file:
    json.dump(setting, output_file, indent='\t', sort_keys=True, ensure_ascii=False)

  print('...auto-captions added as metadata:\n\t%s' % '\n\t'.join(['\'%s\': %d' % (lang, added_autocaps_tally[lang]) for lang in added_autocaps_tally]))

## Configure paths and generate all other settings as variants of the original setting

io_paths = [
  {
    'original': path.join(data_dir, 'setting-original.json'),
    'original-autocaps': path.join(data_dir, 'setting-original.autocaps.json'),
    'masked': path.join(data_dir, 'setting-masked.json'),
    'masked-autocaps': path.join(data_dir, 'setting-masked.autocaps.json')
  },
  {
    'original': path.join(data_dir, 'setting-original-only-qrels.json'),
    'original-autocaps': path.join(data_dir, 'setting-original-only-qrels.autocaps.json'),
    'masked': path.join(data_dir, 'setting-masked-only-qrels.json'),
    'masked-autocaps': path.join(data_dir, 'setting-masked-only-qrels.autocaps.json')
  }
]

setting = {}

for io_dict in io_paths:
  # Process the original metadata collection
  
  original_path = io_dict['original']
  convert_json_to_trec(original_path)
  
  # Process the masked metadata setting
  
  masked_path = io_dict['masked']
  mask_setting(original_path, masked_path)
  convert_json_to_trec(masked_path)
  
  # Process metadata settings containing auto-captions
  
  original_autocaps_path = io_dict['original-autocaps']
  autocap_setting(original_path, original_autocaps_path)
  convert_json_to_trec(original_autocaps_path)
  
  masked_autocaps_path = io_dict['masked-autocaps']
  autocap_setting(masked_path, masked_autocaps_path)
  convert_json_to_trec(masked_autocaps_path)

print('All done!')
