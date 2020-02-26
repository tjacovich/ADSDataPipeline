
## Reads non-bibliographic flat files and sends nonbib and metrics data to master pipeline


# Memory Cache
Computing metrics requires the entire reference and citation network
as well a list of all the refereed bibcodes.  The reference and
citation networks are cached into python defaultdicts where the
default value is [].  To record refereed status the cache has a list
of bibcodes that are refereed.

