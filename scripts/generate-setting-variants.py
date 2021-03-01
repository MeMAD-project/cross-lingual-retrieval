#!/usr/bin/env python3

from os import path
from paths import Paths

import json

paths = Paths()

data_dir = paths.get('DATA-DIR')

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

## Configure paths and generate all other settings as variants of the original setting

io_paths = [
  {
    'original': path.join(data_dir, 'setting-original.json'),
    'masked': path.join(data_dir, 'setting-masked.json')
  },
  {
    'original': path.join(data_dir, 'setting-original-only-qrels.json'),
    'masked': path.join(data_dir, 'setting-masked-only-qrels.json')
  }
]

setting = {}

for io_pair in io_paths:
  original_path = io_pair['original']
  masked_path = io_pair['masked']
  
  mask_setting(original_path, masked_path)

print('All done!')