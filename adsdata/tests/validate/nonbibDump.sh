#!/bin/bash

# usage:
# ./nonbibDump.sh > sqlResults.txt < listOfBibcodes.txt

while IFS= read -r line; do
    sql="psql -P pager=off --tuples-only -h localhost -c \"select nonbib_data from records where bibcode='$line';\" master_pipeline"
    eval $sql
done

