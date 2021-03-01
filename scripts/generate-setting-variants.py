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

## Adds translations of existing metadata in each item, from their
## original language to the other two languages, as additional metadata.
##
def translate_setting(input_path, output_path):
  print('Generating `%s`...' % path.basename(output_path))

  print('...caching German translations...')

  metadata_translations = {}

  de_metadata_path = path.join(data_dir, 'de-metadata.tsv')

  with open(de_metadata_path, mode='r', encoding='utf-8') as de_metadata_file:
    for de_metadata_line in de_metadata_file:
      image_id, metadata_key, _, translation_en, translation_fr = de_metadata_line.split('\t')
      metadata_key += '-from-de'
      
      if image_id not in metadata_translations:
        metadata_translations[image_id] = {'metadata-de': {},
                                           'metadata-en': {},
                                           'metadata-fr': {}}
      
      metadata_translations[image_id]['metadata-en'][metadata_key] = translation_en
      metadata_translations[image_id]['metadata-fr'][metadata_key] = translation_fr
  
  print('...caching English translations...')
  
  en_metadata_path = path.join(data_dir, 'en-metadata.tsv')

  with open(en_metadata_path, mode='r', encoding='utf-8') as en_metadata_file:
    for en_metadata_line in en_metadata_file:
      image_id, metadata_key, _, translation_de, translation_fr = en_metadata_line.split('\t')
      metadata_key += '-from-en'

      if image_id not in metadata_translations:
        metadata_translations[image_id] = {'metadata-de': {},
                                           'metadata-en': {},
                                           'metadata-fr': {}}

      metadata_translations[image_id]['metadata-de'][metadata_key] = translation_de
      metadata_translations[image_id]['metadata-fr'][metadata_key] = translation_fr
  
  print('...caching French translations...')
  
  fr_metadata_path = path.join(data_dir, 'fr-metadata.tsv')

  with open(fr_metadata_path, mode='r', encoding='utf-8') as fr_metadata_file:
    for fr_metadata_line in fr_metadata_file:
      image_id, metadata_key, _, translation_de, translation_en = fr_metadata_line.split('\t')
      metadata_key += '-from-fr'

      if image_id not in metadata_translations:
        metadata_translations[image_id] = {'metadata-de': {},
                                           'metadata-en': {},
                                           'metadata-fr': {}}
     
      metadata_translations[image_id]['metadata-de'][metadata_key] = translation_de
      metadata_translations[image_id]['metadata-en'][metadata_key] = translation_en
  
  print('...parsing input metadata...')

  with open(input_path, mode='r', encoding='utf-8') as input_file:
    setting = json.load(input_file)
  
  print('...adding translations of existing metadata...')

  added_translations_tally = {
    'de': 0,
    'en': 0,
    'fr': 0
  }

  for image_id in sorted(list(setting.keys()), key=lambda k: int(k)):
    image_data = setting[image_id]
    
    if image_id in metadata_translations:
      for original_key in setting[image_id]['metadata-de'].keys():
        translation_key = original_key + '-from-de'
        
        for metadata_xx in ['metadata-en', 'metadata-fr']:
          if translation_key in metadata_translations[image_id][metadata_xx]:
            setting[image_id][metadata_xx][translation_key] = metadata_translations[image_id][metadata_xx][translation_key]
            added_translations_tally['de'] += 1
      
      for original_key in setting[image_id]['metadata-en'].keys():
        translation_key = original_key + '-from-en'

        for metadata_xx in ['metadata-de', 'metadata-fr']:
          if translation_key in metadata_translations[image_id][metadata_xx]:
            setting[image_id][metadata_xx][translation_key] = metadata_translations[image_id][metadata_xx][translation_key]
            added_translations_tally['en'] += 1
      
      for original_key in setting[image_id]['metadata-fr'].keys():
        translation_key = original_key + '-from-fr'

        for metadata_xx in ['metadata-de', 'metadata-en']:
          if translation_key in metadata_translations[image_id][metadata_xx]:
            setting[image_id][metadata_xx][translation_key] = metadata_translations[image_id][metadata_xx][translation_key]
            added_translations_tally['fr'] += 1
      
  print('...generating output file...')

  with open(output_path, mode='w', encoding='utf-8') as output_file:
    json.dump(setting, output_file, indent='\t', sort_keys=True, ensure_ascii=False)

  print('...added metadata translations:\n\t%s' % '\n\t'.join(['\'%s\': %d' % (lang, added_translations_tally[lang]) for lang in added_translations_tally]))


## Configure paths and generate all other settings as variants of the original setting

io_dicts = [
  {
    'original': path.join(data_dir, 'setting-original.json'),
    'original-autocaps': path.join(data_dir, 'setting-original.autocaps.json'),
    'original-translations': path.join(data_dir, 'setting-original.translations.json'),
    'original-fully-enriched': path.join(data_dir, 'setting-original.fully-enriched.json'),
    'masked': path.join(data_dir, 'setting-masked.json'),
    'masked-autocaps': path.join(data_dir, 'setting-masked.autocaps.json'),
    'masked-translations': path.join(data_dir, 'setting-masked.translations.json'),
    'masked-fully-enriched': path.join(data_dir, 'setting-masked.fully-enriched.json')
  },
  {
    'original': path.join(data_dir, 'setting-original-only-qrels.json'),
    'original-autocaps': path.join(data_dir, 'setting-original-only-qrels.autocaps.json'),
    'original-translations': path.join(data_dir, 'setting-original-only-qrels.translations.json'),
    'original-fully-enriched': path.join(data_dir, 'setting-original-only-qrels.fully-enriched.json'),
    'masked': path.join(data_dir, 'setting-masked-only-qrels.json'),
    'masked-autocaps': path.join(data_dir, 'setting-masked-only-qrels.autocaps.json'),
    'masked-translations': path.join(data_dir, 'setting-masked-only-qrels.translations.json'),
    'masked-fully-enriched': path.join(data_dir, 'setting-masked-only-qrels.fully-enriched.json')
  }
]

for io_dict in io_dicts:
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
  
  # Process metadata settings containing translated metadata

  original_translations_path = io_dict['original-translations']
  translate_setting(original_path, original_translations_path)
  convert_json_to_trec(original_translations_path)

  masked_translations_path = io_dict['masked-translations']
  translate_setting(masked_path, masked_translations_path)
  convert_json_to_trec(masked_translations_path)

  # Process metadata settings containing both auto-captions and translated metadata

  original_fully_enriched_path = io_dict['original-fully-enriched']
  autocap_setting(original_translations_path, original_fully_enriched_path)
  convert_json_to_trec(original_fully_enriched_path)

  masked_fully_enriched_path = io_dict['masked-fully-enriched']
  autocap_setting(masked_translations_path, masked_fully_enriched_path)
  convert_json_to_trec(masked_fully_enriched_path)

print('All done!')
