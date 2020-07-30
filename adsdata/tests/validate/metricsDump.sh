#!/bin/bash

# usage:
# ./metricsDump.sh > sqlResults.txt < listOfBibcodes.txt

while IFS= read -r line; do
    sql="psql -P pager=off --tuples-only -h localhost -c \"select metrics from records where bibcode='$line';\" master_pipeline"
    eval $sql
done

