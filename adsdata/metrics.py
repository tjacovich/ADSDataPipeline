from collections import defaultdict
from datetime import datetime
from adsmsg import MetricsRecord
from adsputils import load_config, setup_logging

import memory_cache

logger = setup_logging('ADSData', 'INFO')


def compute_metrics(d):
    """passed a dict with the full nonbib record read from many files"""

    bibcode = d['canonical']
    author_num = 1
    if 'author' in d and d['author']:
        author_num = len(d['author'])

    # hack: eventually need lots of info for bibcode, not just author_num
    cache = memory_cache.get()
    refereed = cache['refereed']
    bibcode_to_references = cache['reference']
    bibcode_to_cites = cache['citation']

    citations = bibcode_to_cites.get(bibcode)
    citations_histogram = defaultdict(float)
    citations_json_records = []
    citation_normalized_references = 0.0
    citation_num = len(citations)
    normalized_reference = 0.0
    refereed_citations = []
    reference_num = len(bibcode_to_references.get(bibcode))
    total_normalized_citations = 0.0

    if citation_num:
        for citation_bibcode in citations:
            citation_refereed = citation_bibcode in refereed
            len_citation_reference = len(bibcode_to_references.get(citation_bibcode))
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


    modtime = datetime.now()
    reads = d['reads']
    downloads = d['download']
    ret = {'bibcode': bibcode, 'an_citations': an_citations, 'an_refereed_citations': an_refereed_citations,
           'author_num': author_num, 'citation_num': citation_num, 'citations': citations,
           'downloads': downloads, 'modtime': modtime, 'reads': reads, 'refereed': bibcode in refereed,
           'refereed_citation_num': refereed_citation_num, 'reference_num': reference_num,
           'rn_citations': rn_citations, 'rn_citation_hist': rn_citations_hist}  #  'citation_record': citations_json_records,
    return ret
