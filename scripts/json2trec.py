#!/usr/bin/env python3

from os import path

import html, json
 
class JSON2TREC:
  def convert(self, json_path, trec_path):
    print('Converting `%s\'...' % path.basename(json_path))
    
    print('...parsing the input...')
    
    with open(json_path, mode='r', encoding='utf-8') as json_file:
      json_data = json.load(json_file)
    
    print('...generating the output...')
    
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
              if metadata_key.startswith('image-') or metadata_key.startswith('auto-'):
                metadata_value = image_data[stratum][metadata_key]
                trec_file.write('    %s\n' % html.unescape(metadata_value))
              elif metadata_key.startswith('topic-'):
                for metadata_value in image_data[stratum][metadata_key]:
                  trec_file.write('    %s\n' % html.unescape(metadata_value))
        
        trec_file.write('  </TEXT>\n'
                      + '</DOC>\n')
    
    print('...done!')

