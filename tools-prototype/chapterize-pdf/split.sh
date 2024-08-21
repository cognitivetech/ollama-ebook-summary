#!/bin/bash
sequence=1
pdftk $1 dump_data | awk -f split.awk | \
while IFS="%" \
read -r title start end
do
  pdftk $1 cat "$start"-"$end" output $sequence-"$title".pdf
  sequence=$((sequence+1))
done

