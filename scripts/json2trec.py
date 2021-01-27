#!/usr/bin/env python3

from os import path
from paths import Paths

import html, json

paths = Paths()

data_dir = paths.get('DATA-DIR')

json_paths = [
  path.join(data_dir, 'setting-original.json'),
  path.join(data_dir, 'setting-masked.json')
]

for json_path in json_paths:
  print('Processing `%s\'...' % path.basename(json_path))
  
  with open(json_path, mode='r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)
  
  trec_path = path.splitext(json_path)[0] + '.trec'
  
  with open(trec_path, mode='w', encoding='utf-8') as trec_file:
    for image_id in sorted(list(json_data.keys()), key=lambda k: int(k)):
      trec_file.write('<DOC>\n'
                    + '  <DOCNO>%s</DOCNO>\n' % image_id
                    + '  <TEXT>\n')
      
      image_data = json_data[image_id]
      
      for stratum in image_data:
        if stratum.startswith('metadata'):
          for metadata_key in image_data[stratum]:
            if metadata_key.startswith('image-'):
              metadata_value = image_data[stratum][metadata_key]
              trec_file.write('    %s\n' % html.unescape(metadata_value))
            elif metadata_key.startswith('topic-'):
              for metadata_value in image_data[stratum][metadata_key]:
                trec_file.write('    %s\n' % html.unescape(metadata_value))
      
      trec_file.write('  </TEXT>\n'
                    + '</DOC>\n')

print('...all done!')

