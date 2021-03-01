#!/bin/bash

for TREC_PATH in $(ls ../data/{setting-original,setting-masked}.*trec); do
  ZIDX_PRFX=${TREC_PATH%.trec}.zettair-index
  
  zet --index --filename ${ZIDX_PRFX} --big-and-fast -t TREC --index ${TREC_PATH}
  
  mv ${ZIDX_PRFX}* ../models
done

echo "...all done!"

