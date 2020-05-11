
from datetime import datetime
from mock import patch
from mock import mock_open
import unittest

from adsdata import process, metrics


class TestMetrics(unittest.TestCase):

    def test_trivial_fields(self):
        d = {'canonical': "1998PPGeo..22..553A", 'refereed': False, 'author': ["Arnfield, A. L."],
             'reads': [1, 2, 3, 4], 'download': [0, 1, 2, 3],
             'citations':  ['1998PPGeo..22..553B'], 'id': 11, 'reference': ["1997BoLMe..85..475M"]}
        m = mock_open(read_data='')
        m.return_value.__iter__ = lambda self: iter(self.readline, '')
        with patch('builtins.open', m):
            process.init_cache()
            
            process.get_cache()['citation']['1998PPGeo..22..553A'] = ['1998PPGeo..22..553B']
            met = metrics.compute_metrics(d)
            self.assertEqual(met['bibcode'], d['canonical'])
            self.assertEqual(met['citations'], d['citations'])
            self.assertEqual(met['reads'], d['reads'])
            self.assertEqual(met['downloads'], d['download'])

    def test_num_fields(self):
        d = {'canonical': "1998PPGeo..22..553A", 'refereed': False, 'author': ["Arnfield, A. L."],
             'reads': [1, 2, 3, 4], 'download': [0, 1, 2, 3],
             'citations':  ['1998PPGeo..22..553A'], 'id': 11, 'reference': ["1997BoLMe..85..475M"]}
        m = mock_open(read_data='')
        m.return_value.__iter__ = lambda self: iter(self.readline, '')
        with patch('builtins.open', m):
            process.init_cache()

            process.get_cache()['citation']['1998PPGeo..22..553A'].append('1998PPGeo..22..553B')
            process.get_cache()['reference']['1998PPGeo..22..553A'].append('1998PPGeo..22..553B')
            met = metrics.compute_metrics(d)
            self.assertEqual(met['citation_num'], len(d['citations']))
            self.assertEqual(met['reference_num'], len(d['reference']))
            self.assertEqual(met['author_num'], len(d['author']))
            self.assertEqual(met['refereed_citation_num'], 0)

    def test_with_citations(self):
        d = {'canonical': "1997BoLMe..85..475M", 'refereed': True,
             'author': ["Meesters, A. G. C. A.", "Bink, N. J.",  "Henneken, E. A. C.",
                        "Vugts, H. F.", "Cannemeijer, F."],
             'download': [], 'reads': [],
             'citations': ["1998PPGeo..22..553A", "1999P&SS...47..951S", "2000BoLMe..97..385O",
                           "2001MAP....78..115K", "2002BoLMe.103...49H", "2006QJRMS.132..779R",
                           "2006QJRMS.132...61E", "2008Sci...320.1622D", "2016BoLMe.159..469G"],
             'reference': ["1994BoLMe..71..393V", "1994GPC.....9...53M", "1994GPC.....9...53X"]}
        m = mock_open(read_data='')
        m.return_value.__iter__ = lambda self: iter(self.readline, '')
        with patch('builtins.open', m):
            process.init_cache()
            # init cache
            for bib in d['citations']:
                process.get_cache()['citation']['1997BoLMe..85..475M'].append(bib)
            for bib in d['reference']:
                process.get_cache()['reference']['1997BoLMe..85..475M'].append(bib)
            refereed = ['1997BoLMe..85..475M', "1999P&SS...47..951S", "2000BoLMe..97..385O",
                        "2001MAP....78..115K", "2002BoLMe.103...49H", "2006QJRMS.132..779R",
                        "2006QJRMS.132...61E", "2008Sci...320.1622D", "2016BoLMe.159..469G"]
            for bib in refereed:
                process.get_cache()['refereed'].network.append(bib)
            # 1999P&SS...47..951S
            PSSreferences = ["1973JAtS...30...66B", "1973JAtS...30..749L", "1976JAtS...33..923B",
                             "1977JGR....82.4121B", "1977JGR....82.4249K", "1977JGR....82.4559H",
                             "1978Icar...33..417W", "1978JAtS...35.2346S", "1978JGR....83.1889D",
                             "1979Icar...39..151H", "1979Icar...39..184H", "1979JGR....84.2889J",
                             "1979JGR....84.2929P", "1979Natur.278..531H", "1981GeoRL...8..899R",
                             "1981suma.book.....C", "1982JAtS...39.2701M", "1982JGR....87.9975M",
                             "1982MWRv..110..994A", "1985AdSpR...5...93H", "1985PhDT.........2P",
                             "1985TellA..37..156A", "1985wagp.book.....G", "1987MWRv..115..936Y",
                             "1987MWRv..115.2214P", "1988aitb.book.....S", "1989BAMS...70..738B",
                             "1990JAtS...47..612Y", "1990JGR....95.1359J", "1991ConAP..64..103S",
                             "1992aitd.book.....H", "1992BoLMe..59..141G", "1992JGR....97.7781Z",
                             "1993JAtS...50...77S", "1993JGR....98.3125B", "1994DPS....26.1806G",
                             "1995Icar..113..277M", "1995JGR...100.5277H", "1995MWRv..123.1146H",
                             "1996Icar..122...36C", "1996JGR...10114957S", "1996Sci...271..184S",
                             "1997AdSpR..19.1241S", "1997AdSpR..19.1289M", "1997BoLMe..85..475M",
                             "1997JGR...102.4463W", "1997Sci...278.1758S", "1998Sci...279.1686S"]
            for bib in PSSreferences:
                process.get_cache()['reference']['1999P&SS...47..951S'].append(bib)
                
            met = metrics.compute_metrics(d)
            self.assertEqual(len(met['citations']), len(d['citations']), 'citations check')
            self.assertEqual(met['refereed_citation_num'], len(refereed) - 1)
            self.assertEqual(met['refereed_citations'], refereed[1:])
            rn_citation_data = {"cityear": 1998, "pubyear": 1997, "auth_norm": 0.20000000298023224,
                                "bibcode": "1998PPGeo..22..553A", "ref_norm": 0.20000000298023224}
            rn_citation_data1 = {"cityear": 1999, "pubyear": 1997, "auth_norm": 0.20000000298023224,
                                 "bibcode": "1999P&SS...47..951S", "ref_norm": 0.02083333395421505}
            self.compare_citation_data(met['rn_citation_data'][0], rn_citation_data)
            self.compare_citation_data(met['rn_citation_data'][1], rn_citation_data1)
            
            y = int(d['canonical'][:4])
            today = datetime.today()
            age = max(1.0, today.year - y + 1)
            self.assertAlmostEqual(met['an_refereed_citations'], len(met['refereed_citations'])/float(age), 5)

    def compare_citation_data(self, a, b):
        self.assertEqual(a['bibcode'], b['bibcode'])
        self.assertEqual(a['pubyear'], b['pubyear'])
        self.assertEqual(a['cityear'], b['cityear'])
        self.assertAlmostEqual(a['auth_norm'], b['auth_norm'])
        self.assertAlmostEqual(a['ref_norm'], b['ref_norm'])
