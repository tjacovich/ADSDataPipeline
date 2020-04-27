
import sys
import traceback

from adsmsg import NonBibRecord, MetricsRecord
import tasks
import metrics
import reader
from file_defs import data_files

# read data for the current bibcode from all the files
# generate a complete nonbib record
# send it to master
# generate a complete metrics record
# send it to master

app = tasks.app
logger = app.logger
nonbib_keys = data_files.keys()


def process():
    # keep reading one (logical) line from each file
    # generate nonbib and metrics record
    
    open_all(root_dir=app.conf['INPUT_DATA_ROOT'])
    count = 0
    d = read_next()
    while (d is not None):
        try:
            # process it
            bibcode = d['canonical']
            if count % 100 == 0:
                app.logger.info('processing, count = {}, current bibcode = {}'.format(count, bibcode))
            if len(bibcode) == 0 or count > 10:
                print('exiting main loop')
                break
            rec = convert(d)
            nonbib = NonBibRecord(**rec)
            met = metrics.compute_metrics(d)
            met_proto = MetricsRecord(**met)
            d = read_next()
            count += 1
        except AttributeError as e:
            app.logger.error('AttributeError while processing bibcode: {}, error: {}'.format(d['canonical'], str(e)))
            app.logger.error(traceback.format_exc())
        except:
            e = sys.exc_info()[0]
            app.logger.error('Error! perhaps while processing bibcode: {}, error: {}'.format(d['canonical'], str(e)))


def process_bibcodes(bibcodes):
    """this funciton is useful when debugging"""
    open_all(root_dir=app.conf['INPUT_DATA_ROOT'])
    for bibcode in bibcodes:
        nonbib = read_next_bibcode(bibcode)
        app.logger.info('bibcode: {}, nonbib: {}'.format(bibcode, nonbib))
        converted = convert(nonbib)
        app.logger.info('bibcode: {}, nonbib converted: {}'.format(bibcode, converted))
        nonbib_proto = NonBibRecord(**converted)
        app.logger.info('bibcode: {}, nonbib protobuf: {}'.format(bibcode, nonbib_proto))
        met = metrics.compute_metrics(nonbib)
        app.logger.info('bibcode: {}, metrics: {}'.format(bibcode, met))
        met_proto = MetricsRecord(**met)
        app.logger.info('bibcode: {}, metrics protobuf: {}'.format(bibcode, met_proto))


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
    for filetype, value in passed.iteritems():
        file_properties = data_files[filetype]
        if filetype == 'canonical':
            return_value['bibcode'] = passed['canonical']
        elif ('extra_values' in file_properties and
              'link_type' in file_properties['extra_values']):
            if value != data_files[filetype]['default_value']:
                # here with a real datalinks value, they all get merged into a single field
                d = {}
                d['link_type'] = value['link_type']
                d['link_sub_type'] = value['link_sub_type']
                d['url'] = value['url']
                d['title'] = value.get('title', '')
                if 'item_count' in value:
                    if isinstance(value['item_count'], str):
                        item_count = 0
                    else:
                        item_count = value['item_count']
                else:
                    item_count = 0
                    d['item_count'] = item_count
                    return_value['data_links_rows'].append(d)
            else:
                # here with an empty data links value
                # consume key, don't copy to return_value
                pass
        elif filetype == 'citation':
            return_value['citation_count'] = len(passed['citation'])
        elif filetype == 'reads':
            return_value['read_count'] = sum(passed['reads'])
        else:
            # otherwise, copy value
            return_value[filetype] = passed[filetype]

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
            d['canonical'] = data_files['canonical']['file_descriptor'].readline().strip()
            if d['canonical'] is None:
                return None
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


