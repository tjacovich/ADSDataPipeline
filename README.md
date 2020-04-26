
### Reads flat/classic file with non-bibliographic data and sends
    nonbib and metrics protobufs to master pipeline 


# Memory Caches
Computing metrics requires the entire reference and citation networks
as well a list of all the refereed bibcodes.  The reference and
citation networks are cached in memory into python defaultdicts where
the key is the bibcode and the default value is [].  Refereed status
is cached in a python list of bibcodes.  The cache code reads these
files directly, it does not use the reader.py code.

# Nonbib Processing
Conceptually, the code reads one line from each of the ~30 input
files.  This yields all the nonbib data for the next bibcode.  First, it is
transformed into a nonbib probobuf and sent to master.  Second, this
nonbib data and the memory caches are used to generate a metrics
protobuf that is sent to master.

Some implementation details complicate this picture.  Every bibcode
does not appear in every file so one can't just read the next line
from every file and naively merge.  Also, in some files the data for a
bibcode is spread acroos multiple lines (requiring merging of data).

# Describing And Reading Files
About 30 files need to be consumed.  As noted above, due to the
properties the files encode and slight variations in file formats,
having code to read all the various files can be compliated.  This
code deals with the complications in a single reader class, 
StandardFileReader in adsdata/reader.py.  It supports a small
"description language" where the idiosyncrasies and properties of each
file can be explicitly declared.  The goal is for the reader to
generate "ready to use" data that needs little further massaging.
This is true if you read a file holding scalar data (e.g., refereed),
an array of data (e.g., downloads) or a hashtable of data (e.g.,
relevance or eprint_html).   

How are the various file idiosycrasies and properties are encoded?
There is a 'file properties' dict for each file.  All these
property dictionares are in the file adsdata/file_defs.py.


What idiosycrasies and properties are supported?
As noted above, the various files encode data of different type
(boolean, array, hashtables, etc.).  So for each file we encode the
default value to use for bibcodes that aren't in the file.
Some files have a single line for each bibcode and that contains an
list of similar values (e.g., the number of reads per year).  We read
lists of similar data into an array.  In other files, the multiple
values in a single line contains very different values (e.g.,
relevance holds 4 values: boost, citation_count, read_count and
norm_cites).  We read sets of very different values into a dict.  The
file properties dict holds the (ordered) list of keys.  There are
cases where we want to associate some data with all bibcodes in a
file.  For example, all the data links info read from the file
spires/all.links must have a link_type of 'INSPIRE' and a
link_sub_type of NA.  To accomidate these constants each file property
dict can include 'extra_values' that are merged with the data for
every bibcode as it is read.

# Converting Nonbib Data To Protobuf
The nonbib protobuf sent to master contains only a subset and a
summary of the data read in.  There is code in process.py that
converts the full nonbib dict to a nonbib protobuf.  

# Status/To Do
Data links and metrics values need better unit tests and must be validated.
There is no code to submit protobufs to rabbitmq.
Delete BibcodeFileReader
Test on adsvm04 with full data

