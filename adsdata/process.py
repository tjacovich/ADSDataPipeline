
from collections import OrderedDict

from adsmsg import NonBibRecord, MetricsRecord
import metrics
import reader

# read data for the current bibcode from all the files
# generate a complete nonbib record
# send it to master
# generate a complete metrics record
# send it to master

data_files = OrderedDict()
data_files['canonical'] = {'path': 'bibcodes.list.can', 'file_reader': reader.BibcodeFileReader}
data_files['author'] = {'path': 'links/facet_authors/all.links'}
data_files['citation'] = {'path': 'links/citation/all.links'}
data_files['download'] = {'path': 'links/reads/downloads.links'}
data_files['grants'] = {'path': 'links/grants/all.links'}
data_files['ned_objects'] = {'path': 'links/ned/ned_objects.tab'}
data_files['nonarticle'] = {'path': 'links/nonarticle/all.links', 'data_type': bool}
data_files['ocrabstract'] = {'path': 'links/ocr/all.links', 'data_type': bool}
data_files['private'] = {'path': 'links/private/all.links', 'data_type': bool}
data_files['pub_openaccess'] = {'path': 'links/openaccess/pub.dat', 'data_type': bool}
data_files['readers'] = {'path': 'links/alsoread_bib/all.links'}
data_files['reads'] = {'path': 'links/reads/all.links'}
data_files['refereed'] = {'path': 'links/refereed/all.links', 'data_type': bool}
data_files['reference'] = {'path': 'links/reference/all.links'}
data_files['relevance'] = {'path': 'links/relevance/docmetrics.tab'}
data_files['simbad'] = {'path': 'links/simbad/simbad_objects.tab'}

data_files['pub_html'] = {'path': 'links/electr/all.links'}
data_files['eprint_html'] = {'path': 'links/eprint_html/all.links'}
data_files['pub_pdf'] = {'path': 'links/pub_pdf/all.links'}
data_files['ads_pdf'] = {'path': 'links/ads_pdf/all.links'}
data_files['eprint_pdf'] = {'path': 'links/eprint_pdf/all.links'}
data_files['author_html'] = {'path': 'links/author_html/all.links'}
data_files['author_pdf'] = {'path': 'links/author_pdf/all.links'}
data_files['ads_pdf'] = {'path': 'links/ads_scan/all.links'}
data_files['associated'] = {'path': 'links/associated/all.links'}
data_files['presentation'] = {'path': 'links/video/all.links'}
data_files['librarycatalog'] = {'path': 'links/library/all.links'}
data_files['inspire'] = {'path': 'links/spires/all.links'}
# data_files['toc'] = {'path': 'links/toc/all.links'}  # I don't see how data in this file affect the nonbib record


#data_files['data_link'] = {'path': 'facet_datasources/datasources.links'}
#data_files['ejournal_link'] = {'path': 'electr/all.links'}

nonbib_keys = data_files.keys()

def process():
    # read one (logical) line from each file
    # generate nonbib and metrics record
    # open_all(root_dir='./adsdata/tests/data1/')
    open_all(root_dir='./logs/input/current/')
    count = 0
    d = read_next()
    while (d is not None):
        try:
            # process it
            bibcode = d['canonical']
            print('bibcode::: {}'.format(bibcode))
            if len(bibcode) == 0 or count > 10:
                print('exiting main loop')
                break
            d = read_next()
            rec = convert(d)
            nonbib = NonBibRecord(**rec)
            print('bibcode: {}, nonbib: {}'.format(bibcode, nonbib))
            met = metrics.compute_metrics(d)
            met_proto = MetricsRecord(**met)
            print('bibcode: {}, metrics: {}'.format(bibcode, met_proto))
            count += 1
        except AttributeError as e:
            print('error processing bibcode: {}, error: {}'.format(d['canonical'], e))


def process_bibcode(bibcodes):
    open_all(root_dir='./adsdata/tests/data1/')
    for bibcode in bibcodes:
        d = read_next_bibcode(bibcode)
        rec = convert(d)
        print('bibcode: {}, nonbib: {}\n'.format(bibcode, rec))
        nonbib = NonBibRecord(**rec)
        met = metrics.compute_metrics(d)
        print('bibcode: {}, metrics: {}\n'.format(bibcode, met))
        met_proto = MetricsRecord(**met)

            
def convert(d):
    """convert the passed dict of info from column files into a dict matching NonBibRecord

    most values are read into an array, 
    the exception is boolean membership like refereed"""
    ret = {}
    esources = set()
    links_data = []
    properties = set()
    for k in nonbib_keys:  # should we iterate over keys in protobuf instead?
        if k == 'canonical':
            ret['bibcode'] = d[k]
        elif k in ('author', 'canonical', 'download', 'citation', 'nonarticle', 'ocrabstract', 'private', 'pub_openaccess', 'reads', 'refereed', 'relevance', 'simbad'):
            pass  # field not in protobuf, do not copy
        elif k in ('citation', 'grants', 'ned_objects', 'reference', 'relevance') and (not k in d or d[k]):
            # if there is no value, provide array default
            print('providing default for {}'.format(k))
            ret[k] = []
        elif k in ('foo') and not (k in d or not d[k]):
            # if there is no value, provide boolean default
            ret[k] = False
            print 'changing private to false: {}'.format(ret)
        elif k in ('associated') and k in d and d[k]:
            # sample:
            #    1825AN......4..241B     1825AN......4..241B Main Paper
            #    1825AN......4..241B     2010AN....331..852K Translation
            urls = []
            titles = []
            for current in d[k]:
                urls.append(current.split('\t')[0][:19])
                titles.append(current.split('\t')[0][20:])

            links_data.append({'title': ','.join(titles), 'url': ','.join(urls),  # do we need quotes around array elements?
                               'link_type': k.upper(), 'link_sub_type': 'NA', 'item_count': len(links_data), 'title': []})
            properties.add('ESOURCE')
        elif k in ('presentation', 'librarycatalog', 'inspire') and k in d:
            # sample:
            #   1997kbls.confE..10C	http://online.kitp.ucsb.edu/online/bblunch/carroll/
            links_data.append({'link_type': k.upper(), 'link_sub_type': 'NA', 'url': d[k], 'item_count': len(links_data), 'title': []})
            properties.add(k.upper())

        elif k in ('pub_html', 'eprint_html', 'pub_pdf', 'ads_pdf', 'eprint_pdf', 'author_html', 'author_pdf', 'ads_pdf') and k in d:
            if d[k]:
                esources.append(k.upper())
                t = k.split('_')[1].lower()
                links_data.append({'item_count': len(links_data), 'title': [],
                                   'link_type': 'ESOURCE', 'link_sub_type': t.upper(), 'url': d[k]})
            if 'author' in k:
                properties.add('AUTHOR_OPENACCESS')
            if 'ads' in k:
                properties.add('ADS_OPENACCESS')
                esources.add('ADS_PDF')
                esources.add('ADS_SCAN')
            properties.add('ESOURCE')
            properties.add('OPENACCESS')

        if k in ('citation', 'reads') and k in d:
            count = 0
            if d[k]:
                count = len(d[k])
            tmp = k + '_count'
            if k == 'reads':
                tmp = 'read_count'  # not reads_count
            ret[tmp] = count

    ret['property'] = list(properties)
    ret['esource'] = list(esources)
    ret['data_links_rows'] = links_data
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

def read_next_bibcode(bibcode):
    d = dict()
    d['canonical'] = bibcode
    for x in data_files:
        if x is not 'canonical':
            d[x] = data_files[x]['file_descriptor'].read_value_for(bibcode)
    return d


def open_all(root_dir='/proj/ads/abstracts'):
    global data_files
    # open all the files and out file descriptor back in dict
    for x in data_files:
        if 'file_reader' in data_files[x]:
            reader_class = data_files[x]['file_reader']
            data_files[x]['file_descriptor'] = reader_class(root_dir + data_files[x]['path'])
        else:
            data_files[x]['file_descriptor'] = reader.StandardFileReader(root_dir + data_files[x]['path'], data_type=data_files[x].get('data_type', list))


