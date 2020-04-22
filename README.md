
### Reads non-bibliographic flat files and sends nonbib and metrics protobufs to master pipeline


# Memory Caches
Computing metrics requires the entire reference and citation networks
as well a list of all the refereed bibcodes.  The reference and
citation networks are cached into python defaultdicts where the
key is the bibcode and the default value is [].  Refereed status is
cached in a python list of bibcodes.

# Nonbib Processing
Conceptually, the code reads one line from each of the ~30 input
files.  This yields all the nonbib data for the next bibcode.  First, it is
transformed into a nonbib probobuf and sent to master.  Second, this
nonbib data and the memory caches are used to generate a metrics
protobuf that is sent to master.

Some implementation details complicate this picture.  Every bibcode
does not appear in every file so one can't just read the next line
from every file and naively merge.  Also, in some files the data for a
bibcode is spread acroos multiple line (requiring multiple lines from
some files to be read).

# Status
Development for this code is not complete.  It was coded from the
bottom up.  There is code to create the memory caches, read all the
nonbib data files, generate a nonbib protobuf and a metrics protobuf.
There is not code to submit protobufs to rabbitmq.

