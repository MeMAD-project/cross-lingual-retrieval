#!/usr/bin/env python3

from os import path

import json

dataset_dir = path.join('/scratch', 'project_2000945', 'retrieval-data', 'wiki-retrieval-2010')

setting_paths = [
  path.join(dataset_dir, 'memad', 'setting-original.json'),
  path.join(dataset_dir, 'memad', 'setting-masked.json')
]

for setting_path in setting_paths:
  print('Parsing `%s\'...' % path.basename(setting_path))
  
  with open(setting_path, mode='r', encoding='utf-8') as setting_file:
    setting = json.load(setting_file)
    
    metadata_tally = {
      'metadata-de': 0,
      'metadata-en': 0,
      'metadata-fr': 0
    }
    
    for image_id in setting:
      image_data = setting[image_id]
      
      for stratum in image_data:
        if stratum.startswith('metadata') and image_data[stratum] != {}:
          metadata_tally[stratum] += 1
    
    for stratum in sorted(metadata_tally, key=lambda k: metadata_tally[k]):
      print('...`%s\': %d' % (stratum, metadata_tally[stratum]))

print('...all done!')

