
from collections import OrderedDict

# file properties definitions
# use dict to hold each input files and their properties and idiosycrasies

data_files = OrderedDict()
data_files['canonical'] = {'path': 'bibcodes.list.can', 'default_value': ''}
data_files['author'] = {'path': 'links/facet_authors/all.links', 'default_value': []}
data_files['citation'] = {'path': 'links/citation/all.links', 'default_value': [], 'multiline': True}
data_files['download'] = {'path': 'links/reads/downloads.links', 'default_value': []}
data_files['grants'] = {'path': 'links/grants/all.links', 'default_value': [], 'string_to_number': False, 'multiline': True}
data_files['ned_objects'] = {'path': 'links/ned/ned_objects.tab', 'default_value': [], 'string_to_number': False, 'multiline': True}
data_files['nonarticle'] = {'path': 'links/nonarticle/all.links', 'default_value': False, 'multiline': True}
data_files['ocrabstract'] = {'path': 'links/ocr/all.links', 'default_value': False}
data_files['private'] = {'path': 'links/private/all.links', 'default_value': False}
data_files['pub_openaccess'] = {'path': 'links/openaccess/pub.dat', 'default_value': False}
data_files['readers'] = {'path': 'links/alsoread_bib/all.links', 'default_value': [], 'multiline': True}
data_files['reads'] = {'path': 'links/reads/all.links', 'default_value': []}
data_files['refereed'] = {'path': 'links/refereed/all.links', 'default_value': False}
data_files['reference'] = {'path': 'links/reference/all.links', 'default_value': [], 'multiline': True}
data_files['relevance'] = {'path': 'links/relevance/docmetrics.tab', 'default_value': {},
                           'subparts': ['boost', 'citation_count', 'read_count', 'norm_cites']}
data_files['simbad_objects'] = {'path': 'links/simbad/simbad_objects.tab', 'default_value': [],
                                'string_to_number': False, 'multiline': True}

data_files['pub_html'] = {'path': 'links/electr/all.links', 'default_value': {},
                          'extra_values': {'link_type': 'ESOURCE', 'link_sub_type': 'PUB_HTML', 'property': ['ADS_OPENACCESS', 'ARTICLE', 'OPENACCESS']},
                          'subparts': [['url']]}
data_files['eprint_html'] = {'path': 'links/eprint_html/all.links', 'default_value': {},
                             'extra_values': {'link_type': 'ESOURCE', 'link_sub_type': 'EPRINT_HTML'},
                             'subparts': ['url']}
data_files['pub_pdf'] = {'path': 'links/pub_pdf/all.links', 'default_value': {},
                         'extra_values': {'link_type': 'ESOURCE', 'link_sub_type': 'PUB_PDF'},
                         'subparts': ['url']}
data_files['ads_pdf'] = {'path': 'links/ads_pdf/all.links', 'default_value': {},
                         'extra_values': {'link_type': 'ESOURCE', 'link_sub_type': 'ADS_PDF', 'property': ['ADS_OPENACCESS', 'ARTICLE', 'OPENACCESS']},
                         'subparts': [['url']]}
data_files['eprint_pdf'] = {'path': 'links/eprint_pdf/all.links', 'default_value': {},
                            'extra_values': {'link_type': 'ESOURCE', 'link_sub_type': 'EPRINT_PDF'},
                            'subparts': ['url']}
data_files['author_html'] = {'path': 'links/author_html/all.links', 'default_value': {},
                             'extra_values': {'link_type': 'ESOURCE', 'link_sub_type': 'AUTHOR_HTML'},
                             'subparts': ['url']}
data_files['author_pdf'] = {'path': 'links/author_pdf/all.links', 'default_value': {},
                            'extra_values': {'link_type': 'ESOURCE', 'link_sub_type': 'AUTHOR_PDF'},
                            'subparts': ['url']}
data_files['ads_scan'] = {'path': 'links/ads_scan/all.links', 'default_value': {},
                          'extra_values': {'link_type': 'ESOURCE', 'link_sub_type': 'ADS_SCAN', 'property': ['ADS_OPENACCESS', 'ARTICLE', 'OPENACCESS']},
                          'subparts': [['url']]}
data_files['associated'] = {'path': 'links/associated/all.links', 'default_value': {},
                            'extra_values': {'link_type': 'ASSOCIATED', 'link_sub_type': 'NA'},
                            'subparts': ['url', 'title'], 'multiline': True}
data_files['presentation'] = {'path': 'links/video/all.links', 'default_value': {},
                              'extra_values': {'link_type': 'PRESENTATION', 'link_sub_type': 'NA'},
                              'subparts': ['url', 'title'], 'multiline': True}
data_files['librarycatalog'] = {'path': 'links/library/all.links', 'default_value': {},
                                'extra_values': {'link_type': 'LIBRARYCATALOG', 'link_sub_type': 'NA'},
                                'subparts': ['url', 'title'], 'multiline': True}
data_files['inspire'] = {'path': 'links/spires/all.links', 'default_value': {},
                         'extra_values': {'link_type': 'INSPIRE', 'link_sub_type': 'NA'},
                         'subparts': [['url']], 'multiline': True}
data_files['toc'] = {'path': 'links/toc/all.links', 'default_value': False,
                     'extra_values': {'link_type': 'TOC', 'link_sub_type': 'NA'}}
                    #  'subparts': ['url']}
data_files['data_link'] = {'path': 'links/facet_datasources/datasources.links', 'default_value': {},
                           'extra_values': {'link_type': 'DATA', 'property': ['DATA']},
                           'subparts': ['link_sub_type', 'item_count', ['url'], ['title']]}
# data_files['ejournal_link'] = {'path': 'electr/all.links'}

