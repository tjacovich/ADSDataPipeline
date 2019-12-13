
from collections import OrderedDict()

from adsmsg.msg import NonBibRecord

import reader

# read one line from each file
# generate a complete nonbib record
# send it to master

data_files = OrderedDict([
    ('canonical': {'path': 'config/bibcodes.list.can', 'file_reader': reader.BibcodeFileReader}),
    ('author':  {'path': 'config/links/facet_authors/all.links', 'file_reader': }),
    ('canonical': {'path': 'config/bibcodes.list.can'}),
    ('citation': {'path': 'config/links/citation/all.links'}),
    ('download': {'path': 'config/links/reads/downloads.links'}),
    ('grants': {'path': 'config/links/grants/all.links'}),
    ('ned': {'path': 'config/links/ned/ned_objects.tab'}),
    ('nonarticle': {'path': 'config/links/nonarticle/all.links', 'file_reader': reader.OnlyTrueFileReader}),
    ('ocrabstract': {'path': 'config/links/ocr/all.links', 'file_reader': reader.OnlyTrueFileReader}),
    ('private': {'path': 'config/links/private/all.links', 'file_reader': reader.OnlyTrueFileReader}),
    ('pub_openaccess': {'path': 'config/links/openaccess/pub.dat', 'file_reader': reader.OnlyTrueFileReader}),
    ('reader': {'path': 'config/links/alsoread_bib/all.links'}),
    ('reads': {'path': 'config/links/reads/all.links'}),
    ('refereed': {'path': 'config/links/refereed/all.links', 'file_reader': reader.OnlyTrueFileReader}),
    ('reference': {'path': 'config/links/reference/all.links'}),
    ('relevance': {'path': 'config/links/relevance/docmetrics.tab'}),
    ('simbad': {'path': 'config/links/simbad/simbad_objects.tab'}),

    ('data_link': {'path': 'facet_datasources/datasources.links'}),
    ('ejournal_link': {'path': 'electr/all.links'})
    ])


def process():
    # read a line and generate nonbib record
    d = read_next()
    while (d is not None):
        # process it
        d = read_next()
        r = convert(d)

def convert(d):
    """convert the passed dict of info from files into a dict matching NonBibRecord

    most values are read into an array, 
    the exception is boolean membership like refereed"""
    ret = {}
    for k in d:
        if k == 'canonical':
            ret[k] = d[k]
        elif k == 'refereed' or 'private' or 'pub_openaccess':
            ret[k] = d[k]
        elif k == 'simbad':
            rek[k] = 'todo'
        

def read_next():
    """read all the info for the next bibcode"""
    global data_files
    d = dict()
    for x in data_files:
        if x is 'canonical':
            d['bibcode'] = data_files['canonical']['file_descriptor'].readline()
            if d['bibcode'] is None:
                return None
        else:
            d[x] = x['file_descriptor'].read_value_for(d['bibcode'])
    return d

def open():
    global data_files
    # open all the files and out file descriptor back in dict
    root_dir = './adsdata/data1/'  # hack
    for x in data_files:
        reader_class = reader.StandardFileReader
        if 'reader_file' in data_files[x]:
            reader_class = data_files[x]['reader_file']
        data_files[x]['file_descriptor'] = reader_class(root_dir + x['path'])
        


