
### Reads flat/classic file with non-bibliographic data and sends
    nonbib and metrics protobufs to master pipeline 


# Memory Caches
Computing metrics requires the entire reference and citation networks
as well a list of all the refereed bibcodes.  The reference and
citation networks are cached in memory into python defaultdicts where
the key is the bibcode and the default value is [].  Refereed status
is cached in a python set of bibcodes.  The cache code reads these
files directly, it does not use the reader.py code.

# Nonbib Processing
Conceptually, the code reads one line from each of the ~30 input
files.  This yields all the nonbib data for the next bibcode.  It is
transformed into a nonbib probobuf and sent to master.  

Some implementation details complicate this picture.  Every bibcode
does not appear in every file so one can't just read the next line
from every file and naively merge.  In some files the data for a
bibcode is spread acroos multiple lines (requiring merging of data).
A few values values are computed (e.g., property) from the data read
in.  Some detail data is not sent to master (e.g., author list read in
but only number of authors is used).

# Metrics Processing
If we have read in cache, as we read the nonbib data one bibcode at a
time we can compute the metrics record.  Essensically the same core
metrics code from the old pipeline is used the compute a metrics
record.  It is converted to a metrics protobuf and sent to master.

# Describing And Reading Files  
About 30 files need to be consumed.  As noted above, the different
data files have different customs and quirks.  This complicates
reading all the files.  This 
code deals with the complications in a single reader class, 
StandardFileReader in adsdata/reader.py.  The goal of the reader is
generate "ready to use" data that needs little further massaging.  It
supports a small "description language" where the idiosyncrasies and
customs of each file are explicitly declared.  

What idiosycrasies and properties are supported?  
As noted above, the various files encode data of different type
(boolean, array, hashtables, etc.).  So for each file we encode the
default value to use for bibcodes that aren't in the file.
Some files have a single line for each bibcode and that contains an
list of similar values (e.g., the number of reads per year).  We read
lists of similar data into an array.  In other files, the multiple
values in a single line contains very different values (e.g.,
relevance holds 4 values: boost, citation_count, read_count and
norm_cites).
We read sets of very different values into a dict (for example, the
relevance file contains boost, citation count, read count and norm
cites).  The file properties for releveance defines a 'subparts' list
which holdss the ordered list of keys.
This works when all the values in each row stored as a scalar.  This
isn't always the case.  Some data links values are always stored in
arrays even when there is a single value (for example, url and
title).  To indicate this, the key in the file description is enclosed in
a list.  

There are
cases where we want to associate some data with all bibcodes in a
file.  For example, all the data links info read from the file
spires/all.links must have a link_type of 'INSPIRE' and a
link_sub_type of NA.  To accomidate these constants each file property
dict can include 'extra_values' that are merged with the data for
every bibcode as it is read.  This 'extra_values' field can also hold
additional values for the 'property' list.

# Converting Nonbib Data To Protobuf
The nonbib protobuf sent to master contains only a subset and a
summary of the data read in.  There is code in process.py that
converts the full nonbib dict to a nonbib protobuf.  

# Performance
A single thread can send nonbib and metrics protobufs to master faster than
workers on master can process them.

# Status/To Do
Fix issue with some vizier catalog bibcodes


