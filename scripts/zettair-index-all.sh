#!/bin/bash

for TREC_PATH in $(ls *.trec); do
  ZIDX_PRFX=${TREC_PATH%.trec}.zettair-index
  
  rm ${ZIDX_PRFX}.*
  
  zet --index --filename ${ZIDX_PRFX} --big-and-fast -t TREC --index ${TREC_PATH}
done

echo "...all done!"

