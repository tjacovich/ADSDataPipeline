
from collections import OrderedDict

from adsmsg import NonBibRecord, MetricsRecord
import metrics
import reader

# read one line from each file
# generate a complete nonbib record
# send it to master

data_files = OrderedDict()
data_files['canonical'] = {'path': 'config/bibcodes.list.can', 'file_reader': reader.BibcodeFileReader}
data_files['author'] = {'path': 'config/links/facet_authors/all.links'}
data_files['citation'] = {'path': 'config/links/citation/all.links'}
data_files['download'] = {'path': 'config/links/reads/downloads.links'}
data_files['grants'] = {'path': 'config/links/grants/all.links'}
data_files['ned_objects'] = {'path': 'config/links/ned/ned_objects.tab'}
data_files['nonarticle'] = {'path': 'config/links/nonarticle/all.links', 'data_type': bool}
data_files['ocrabstract'] = {'path': 'config/links/ocr/all.links', 'data_type': bool}
data_files['private'] = {'path': 'config/links/private/all.links', 'data_type': bool}
data_files['pub_openaccess'] = {'path': 'config/links/openaccess/pub.dat', 'data_type': bool}
data_files['readers'] = {'path': 'config/links/alsoread_bib/all.links'}
data_files['reads'] = {'path': 'config/links/reads/all.links'}
data_files['refereed'] = {'path': 'config/links/refereed/all.links', 'data_type': bool}
data_files['reference'] = {'path': 'config/links/reference/all.links'}
data_files['relevance'] = {'path': 'config/links/relevance/docmetrics.tab'}
data_files['simbad'] = {'path': 'config/links/simbad/simbad_objects.tab'}

#data_files['electr'] = {'path': 'config/links/eprint_html/all.links'}
#data_files['pub_html'] = {'path': 'config/links/electr/all.links'}



#data_files['data_link'] = {'path': 'facet_datasources/datasources.links'}
#data_files['ejournal_link'] = {'path': 'electr/all.links'}

nonbib_keys = data_files.keys()

def process():
    # read a line and generate nonbib record
    open(root_dir='./adsdata/tests/data1/')
    d = read_next()
    while (d is not None):
        # process it
        d = read_next()
        rec = convert(d)
        print('in process, rec = {}'.format(rec))
        nonbib = NonBibRecord(**rec)
        met = metrics.compute_metrics(d['canonical'], len(d['author']))
        import pdb
        pdb.set_trace()
        met_proto = MetricsRecord(**met)
        print('processed {} {}'.format( d['canonical'], nonbib))

        
def convert(d):
    """convert the passed dict of info from column files into a dict matching NonBibRecord

    most values are read into an array, 
    the exception is boolean membership like refereed"""
    ret = {}
    esources = []
    for k in nonbib_keys:  # should we iterate over keys in protobuf instead?
        if k == 'canonical':
            ret['bibcode'] = d[k]
        elif k in ('author', 'canonical', 'download', 'citation', 'nonarticle', 'ocrabstract', 'private', 'pub_openaccess', 'reads', 'refereed', 'relevance', 'simbad'):
            pass  # field not in protobuf, do not copy
        elif k in ('citation', 'grants', 'ned_objects', 'reference', 'relevance') and not d[k]:
            # if there is no value, provide array default
            print('providing default for {}'.format(k))
            ret[k] = []
        elif k in ('foo') and not d[k]:
            # if there is no value, provide boolean default
            ret[k] = False
            print 'changing private to false: {}'.format(ret)
        elif k in ('pub_html'):
            if k is 'pub_html' and d[k]:
                esources.append(k.upper_case())
        else:
            ret[k] = d[k]
        if k in ('citation', 'reads'):
            count = 0
            if d[k]:
                count = len(d[k])
            tmp = k + '_count'
            if k == 'reads':
                tmp = 'read_count'  # not reads_count
            ret[tmp] = count
        #if k == 'author':
        #    ret['author_count'] = 0
        #    if d[k]:
        #        ret['author_count'] = len(d['author'])
    return ret

def read_next():
    """read all the info for the next bibcode into a dict"""
    global data_files
    d = dict()
    for x in data_files:
        if x is 'canonical':
            d['canonical'] = data_files['canonical']['file_descriptor'].readline()
            if d['canonical'] is None:
                return None
        else:
            d[x] = data_files[x]['file_descriptor'].read_value_for(d['canonical'])
    return d

def open(root_dir='/proj/ads/abstracts'):
    global data_files
    # open all the files and out file descriptor back in dict
    for x in data_files:
        if 'file_reader' in data_files[x]:
            reader_class = data_files[x]['file_reader']
            data_files[x]['file_descriptor'] = reader_class(root_dir + data_files[x]['path'])
        else:
            data_files[x]['file_descriptor'] = reader.StandardFileReader(root_dir + data_files[x]['path'], data_type=data_files[x].get('data_type', list))


