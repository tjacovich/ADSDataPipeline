
from collections import defaultdict
from datetime import datetime

import argparse

from adsdata import reader
from adsputils import load_config, setup_logging

logger = None
config = {}
refereed = set()
bibcode_to_references = defaultdict(set)
bibcode_to_cites = defaultdict(set)


# read in data required for metrics compuation
# it appears set memebership is O(1)

def load(config):
    # need to read at least refereed, len of references and bibcode from citations
    global refereed
    logger.info('starting to load refereed')
    refereed_filename = config['DATA_PATH'] + config['REFEREED']
    count = 0
    with open(refereed_filename) as f:
        for l in f:
            # need more clean up on input
            l = l.strip()
            refereed.add(l)
            count += 1
            if count % 1000000 == 0:
                logger.info('reading refereed, count = {}'.format(count))
    print('1886Natur..34Q.131. in refereed: {}'.format('1886Natur..34Q.131.' in refereed))
    print('refereed count: {}, first: {}'.format(count, refereed.pop()))
    logger.info('completed refereed')    

    global bibcode_to_references
    logger.info('starting to load reference')
    reference_filename = config['DATA_PATH'] + config['REFERENCE']
    read_count = 0
    with open(reference_filename) as f:
        for l in f:
            parts = l.split('\t')
            bibcode = l[:19]
            reference = l[20:39]
            bibcode_to_references[bibcode].add(reference)
            read_count += 1
            if read_count % 1000000 == 0:
                logger.info('reading references, count = {}'.format(read_count))
    logger.info('completed references')
    logger.info('number of references {}'.format(len(bibcode_to_references)))

    global bibcode_to_cites
    logger.info('starting to load citation')
    citation_filename = config['DATA_PATH'] + config['CITATION']
    read_count = 0
    with open(citation_filename) as f:
        for l in f:
            parts = l.split('\t')
            bibcode = l[:19]
            cite = l[20:39]
            bibcode_to_cites[bibcode].add(cite)
            read_count += 1
            if read_count % 1000000 == 0:
                logger.info('reading citations, count = {}'.format(read_count))

    logger.info('completed citation')
    logger.info('number of citations {}'.format(len(bibcode_to_cites)))

    logger.info('number of references {}, citations {}'.format(len(bibcode_to_references), len(bibcode_to_cites)))


def compute_metrics(bibcode):

    global refereed
    global bibcode_to_references
    global bibcode_to_cites

    author_num = 20  # hack
    
    total_normalized_citations = 0
    normalized_reference = 0.0
    citations_json_records = []
    citations = bibcode_to_cites[bibcode]
    citation_num = len(citations)
    refereed_citations = []
    reference_num = len(bibcode_to_references[bibcode])
    citations_histogram = defaultdict(float)

    if citations:
        for citation_bibcode in citations:
            citation_refereed = citation_bibcode in refereed
            len_citation_reference = len(bibcode_to_references[citation_bibcode])
            citation_normalized_references = 1.0 / float(max(5, len_citation_reference))
            total_normalized_citations += citation_normalized_references
            normalized_reference += citation_normalized_references
            tmp_json = {"bibcode":  citation_bibcode.encode('utf-8'),
                        "ref_norm": citation_normalized_references,
                        "auth_norm": 1.0 / author_num,
                        "pubyear": int(bibcode[:4]),
                        "cityear": int(citation_bibcode[:4])}
            citations_json_records.append(tmp_json)
            if (citation_refereed):
                refereed_citations.append(citation_bibcode)
            citations_histogram[citation_bibcode[:4]] += total_normalized_citations    

    refereed_citation_num = len(refereed_citations)
    
    # annual citations
    today = datetime.today()
    resource_age = max(1.0, today.year - int(bibcode[:4]) + 1)
    an_citations = float(citation_num) / float(resource_age)
    an_refereed_citations = float(refereed_citation_num) / float(resource_age)

    # normalized info
    rn_citations = normalized_reference 
    rn_citations_hist = dict(citations_histogram)
    logger.info('bibcode: {}, len(citations): {}, citation_normalized_references {}, refereed_citation_num {}, total_normalized_citations {}, citations_histogram {}, an_citations {}, an_refereed_citations {}'.format(bibcode, 
                len(citations), citation_normalized_references, refereed_citation_num, total_normalized_citations,citations_histogram, an_citations, an_refereed_citations))
    logger.info('refereed_citation_num {}, rn_citations {}'.format(refereed_citation_num, rn_citations))

    
def lots_of_metrics(config):
    bibcodes_filename = config['DATA_PATH'] + config['CANONICAL']
    count = 0
    logger.info('starting to compute metrics')
    with open(bibcodes_filename) as f:
        for l in f:
            # l = f.readline()
            l = l.strip()
            compute_metrics(l)
            count += 1
            if count > 1000000:
                logger.info('completed metrics for  3 bibcodes')
                return
    print 'end'


def main():
    global config
    config.update(load_config())
    global logger
    logger = setup_logging('ADSData', config.get('LOG_LEVEL', 'INFO'))

    parser = argparse.ArgumentParser(description='generate nonbib data')
    ars = parser.parse_args()

    load(config)

 
    # compute metrics for a bibcode
    compute_metrics('2012ApJS..199...26H')
    # lots_of_metrics(config)
    logger.info('end of program')

if __name__ == '__main__':
    main()
