#!/bin/bash

ZIDX_PRFX=$1
N_BEST=$2
QUERY=$3

zet -f ${ZIDX_PRFX} -n ${N_BEST} --big-and-fast "${QUERY}"

