
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
data_files['ned'] = {'path': 'config/links/ned/ned_objects.tab'}
data_files['nonarticle'] = {'path': 'config/links/nonarticle/all.links', 'file_reader': reader.OnlyTrueFileReader}
data_files['ocrabstract'] = {'path': 'config/links/ocr/all.links', 'file_reader': reader.OnlyTrueFileReader}
data_files['private'] = {'path': 'config/links/private/all.links', 'file_reader': reader.OnlyTrueFileReader}
data_files['pub_openaccess'] = {'path': 'config/links/openaccess/pub.dat', 'file_reader': reader.OnlyTrueFileReader}
data_files['reader'] = {'path': 'config/links/alsoread_bib/all.links'}
data_files['reads'] = {'path': 'config/links/reads/all.links'}
data_files['refereed'] = {'path': 'config/links/refereed/all.links', 'file_reader': reader.OnlyTrueFileReader}
data_files['reference'] = {'path': 'config/links/reference/all.links'}
data_files['relevance'] = {'path': 'config/links/relevance/docmetrics.tab'}
data_files['simbad'] = {'path': 'config/links/simbad/simbad_objects.tab'}

#data_files['data_link'] = {'path': 'facet_datasources/datasources.links'}
#data_files['ejournal_link'] = {'path': 'electr/all.links'}


def process():
    # read a line and generate nonbib record
    d = read_next()
    while (d is not None):
        # process it
        d = read_next()
        rec = convert(d)
        nonbib = NonBibRecord(**rec)
        met = metrics.compute_metrics(d['canonical'], len(d['author']))
        met_proto = MetricsRecord(**met)
        print('processed {} {}'.format( d['canonical'], nonbib))

        
def convert(d):
    """convert the passed dict of info from column files into a dict matching NonBibRecord

    most values are read into an array, 
    the exception is boolean membership like refereed"""
    ret = {}
    for k in d:
        if k == 'canonical':
            ret[k] = d[k]
        elif k == 'private' or 'pub_openaccess' or 'refereed':
            ret[k] = d[k]
        elif (k == 'simbad' or k == 'grants' or k == 'ned') and d[k]:
            rek[k] = ','.join(k['simbad'])
        elif k == 'author':
            ret['author_count'] = 0
            if d[k]:
                ret['author_count'] = len(d['author'])

        

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
            data_files[x]['file_descriptor'] = reader.StandardFileReader(x, root_dir + data_files[x]['path'])


