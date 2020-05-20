
import sys
import traceback

from adsmsg import NonBibRecord, MetricsRecord
from adsdata import diffs, metrics, tasks, reader, aggregator
from adsdata.memory_cache import Refereed, ReferenceNetwork, CitationNetwork

from adsdata.file_defs import data_files

# read data for the current bibcode from all the files
# generate a complete nonbib record
# send it to master
# generate a complete metrics record
# send it to master

app = tasks.app
logger = tasks.app.logger
nonbib_keys = data_files.keys()


def test_process(compute_metrics=True):
    agg = aggregator.TestAggregator()
    agg.open_all()
    count = 0
    s = agg.read_next()
    while s:
        try:
            if count % 100 == 0:
                logger.info('process, count = {}, line = {}'.format(count, s[:40]))
            s = agg.read_next()
            count = count + 1
            if s is None:
                break
        except:
            e = sys.exc_info()[0]
            logger.error('Error! perhaps while processing line: {}, error: {}'.format(s[:40], str(e)))
                 

def process(compute_metrics=True):
    # keep reading one (logical) line from each file
    # generate nonbib and metrics record
    
    open_all(root_dir=app.conf.get('INPUT_DATA_ROOT', './adsdata/tests/data1/config/'))
    count = 0
    # skip_lines(100000)
    d = read_next()
    while (d is not None):
        try:
            # process it
            bibcode = d['canonical']
            if count % 100 == 0:
                logger.info('processing, count = {}, current bibcode = {}'.format(count, bibcode))
            if len(bibcode) == 0:
                print('no bibcode, exiting main loop')
                break
            if not app.conf.get('TEST_NO_PROCESSING', False):
                rec = convert(d)
                nonbib = NonBibRecord(**rec)
            if compute_metrics:
                met = metrics.compute_metrics(d)
                met_proto = MetricsRecord(**met)
                if count % 100 == 0:
                    logger.info('met = {}'.format(met))
            d = read_next()
            if app.conf.get('TEST_MAX_ROWS', -1) > 0:
                if app.conf['TEST_MAX_ROWS'] >= count:
                    break  # useful during testing
            count += 1
        except AttributeError as e:
            logger.error('AttributeError while processing bibcode: {}, error: {}'.format(d['canonical'], str(e)))
            logger.error(traceback.format_exc())
        except:
            e = sys.exc_info()[0]
            logger.error('Error! perhaps while processing bibcode: {}, error: {}'.format(d['canonical'], str(e)))


def process_bibcodes(bibcodes, compute_metrics=True):
    """this funciton is useful when debugging"""
    open_all(root_dir=app.conf.get('INPUT_DATA_ROOT', './adsdata/tests/data1/config/'))
    for bibcode in bibcodes:
        nonbib = read_next_bibcode(bibcode)
        logger.info('bibcode: {}, nonbib: {}'.format(bibcode, nonbib))
        converted = convert(nonbib)
        logger.info('bibcode: {}, nonbib converted: {}'.format(bibcode, converted))
        nonbib_proto = NonBibRecord(**converted)
        logger.info('bibcode: {}, nonbib protobuf: {}'.format(bibcode, nonbib_proto))
        if compute_metrics:
            met = metrics.compute_metrics(nonbib)
            logger.info('bibcode: {}, metrics: {}'.format(bibcode, met))
            met_proto = MetricsRecord(**met)
            logger.info('bibcode: {}, metrics protobuf: {}'.format(bibcode, met_proto))


def convert(passed):
    """convert full nonbib dict to what is needed for nonbib protobuf

    data links values are read from separate files so they are in separate dicts
        they must be merged into one field for the protobuf
    a copule fields are summarized
    some other fields are just copied
    some fields are deleted
    """
    return_value = {}
    return_value['data_links_rows'] = []
    return_value['property'] = set()
    for filetype, value in passed.items():
        file_properties = data_files[filetype]
        if filetype == 'canonical':
            return_value['bibcode'] = passed['canonical']
        elif ('extra_values' in file_properties and
              'link_type' in file_properties['extra_values']):
            if value != data_files[filetype]['default_value']:
                # here with a real datalinks value, they all get merged into a single field
                d = {}
                d['link_type'] = value['link_type']
                if value['link_sub_type'] != 'NA':
                    d['link_sub_type'] = value['link_sub_type']
                    if type(value['url']) is str:
                        d['url'] = [value['url']]
                    else:
                        d['url'] = value['url']
                    if 'title' in value:
                        d['title'] = value.get('title', '')
                #if 'item_count' in value:
                #    if isinstance(value['item_count'], str):
                #        item_count = 0
                #    else:
                #        item_count = value['item_count']
                #else:
                #    item_count = 0
                #    d['item_count'] = item_count
                return_value['data_links_rows'].append(d)
            if value != data_files[filetype]['default_value'] or value is True:
                return_value['property'].add(data_files[filetype]['extra_values']['link_type'])
                return_value['property'].update(data_files[filetype]['extra_values'].get('PROPERTY', []))
        elif filetype == 'relevance':
            for k in passed[filetype]:
                # simply dict value to top level
                return_value[k] = passed[filetype][k]
        # elif filetype == 'citation':  # from relevance
        #     return_value['citation_count'] = len(passed['citation'])
        # elif filetype == 'reads':
        #     return_value['read_count'] = len(passed['readers'])
        elif filetype == 'refereed' and passed[filetype]:
            return_value['property'].add('REFEREED')
        else:
            # otherwise, copy value
            return_value[filetype] = passed[filetype]

    if 'REFEREED' not in return_value['property']:
        return_value['property'].add('NOT REFEREED')
    return_value['property'] = sorted(return_value['property'])
        
    # finally, delted the keys not in the nonbib protobuf
    not_needed = ['author', 'canonical', 'citation', 'download', 'nonarticle', 'ocrabstract', 'private', 'pub_openaccess',
                  'reads', 'refereed', 'relevance']
    for n in not_needed:
        return_value.pop(n, None)
    return return_value


def read_next():
    """read all the info for the next bibcode into a dict"""
    global data_files
    d = {}
    for x in data_files:
        if x is 'canonical':
            d['canonical'] = data_files['canonical']['file_descriptor'].readline()
            if d['canonical'] is None:
                return None
            else:
                d['canonical'] = d['canonical'].strip()
        else:
            d.update(data_files[x]['file_descriptor'].read_value_for(d['canonical']))
    return d


def read_next_bibcode(bibcode):
    """read all the info for the passed bibcode into a dict"""
    d = {}
    d['canonical'] = bibcode
    for x in data_files:
        if x is not 'canonical':
            d.update(data_files[x]['file_descriptor'].read_value_for(bibcode))
    return d


def open_all(root_dir='/proj/ads/abstracts'):
    """simply open file descriptors to all the input files

    we store these descriptors in the file properties object"""

    for x in data_files:
        data_files[x]['file_descriptor'] = reader.StandardFileReader(x, root_dir + data_files[x]['path'])

        
def skip_lines(n):
    c = 0
    logger.info('starting to skip canonical lines')
    while c < n:
        data_files['canonical']['file_descriptor'].readline()
        if c % 1000 == 0:
            print('skipping canonical at {}'.format(c))
        c = c + 1
    logger.info('done skippline lines')


cache = {}

# def init_cache(root_dir=app.conf['INPUT_DATA_ROOT'])):
def init_cache(root_dir='/proj/ads/abstract/'):
    global cache
    if cache:
        # init has already been called
        return cache
    cache['reference'] = ReferenceNetwork(root_dir + data_files['reference']['path'])
    cache['citation'] = CitationNetwork(root_dir + data_files['citation']['path'])
    cache['refereed'] = Refereed(root_dir + data_files['reference']['path'])
    return cache


def get_cache():
    return cache


def compute_diffs():
    logger.info('compute diffs starting')
    diffs.sort_input_files()
    diffs.compute_changed_bibcodes()
    diffs.merge_changed_bibcodes()
    logger.info('compute diffs completed')
