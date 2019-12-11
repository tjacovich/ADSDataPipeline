
from collections import OrderedDict()


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
    for x in data_files:
        if x is 'canonical':
            current_bibcode = data_files['canonical']['file_descriptor'].readline()
        else:
            if current_bibcode == data_files[x]['last_bibcode']:
                # here if the last read has current data
                data_files[x]['current_data'] = data_files[x]['last_data']
            else:
                l = data_files[x]['file_descriptor'].readline
                if l.startsWith(current_bibcode):
                    
        
    

def open():
    global data_files
    # open all the files and out file descriptor back in dict
    root_dir = './adsdata/data1/'  # hack
    for x in data_files:
        reader_class = reader.StandardFileReader
        if 'reader_file' in data_files[x]:
            reader_class = data_files[x]['reader_file']
        data_files[x]['file_descriptor'] = reader_class(root_dir + x['path'])
        


