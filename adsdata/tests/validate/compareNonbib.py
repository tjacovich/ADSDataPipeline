
import json


# sample data from master for 2020yCat..51580229M
# {"property": ["ASSOCIATED", "DATA", "NONARTICLE", "NOT REFEREED"],
#  "total_link_counts": 1,
#  "bibcode": "2020yCat..51580229M",
#  "data": ["Vizier:1"],
#  "data_links_rows": [{"url": ["2019AJ....158..229M", "2020yCat..51580229M"], "title": ["Source Paper", "Catalog Description"], "link_type": "ASSOCIATED", "link_sub_type": "NA"},
#                      {"url": ["http://$VIZIER$/viz-bin/VizieR?-source=J/AJ/158/229"], "title": [""], "item_count": 1, "link_type": "DATA", "link_sub_type": "Vizier"}]}


def compare(file1, file2):
    with open(file1) as f1, open(file2) as f2:
        for x, y in zip(f1, f2):
            try:
                l1 = x.strip()
                l2 = y.strip()
                if len(l1) > 0 or len(l2) > 0:
                    d1 = json.loads(l1)
                    d2 = json.loads(l2)
                    fail = False
                    for k in d1:
                        fail = compare_aux(k, d1, d2)
                        if fail is False:
                            print('success!! {}'.format(d1['bibcode']))
            except json.decoder.JSONDecodeError:
                print('error parsing input file, \nline 1 = {} \nline 2 = {}\n\n'.format(x, y))

def compare_aux(k, d1, d2):
    fail = False
    if k == 'property':
        if d1[k].sort() != d2[k].sort():
            fail = True
            print('property fail {}, {}, {}, {}.  {}, {}'.format(d1['bibcode'], k, len(d1[k]), len(d2[k]), d1[k].sort(), d2[k].sort()))

    if k in d1 and k in d2:
        if type(d1[k]) != type(d2[k]):
            print('fail type mismatch: {}, {}, {}'.format(d1['bibcode'], type(d1[k]), type(d2[k])))
            fail = True
        elif type(d1[k]) is list:
            if type(d1[k][0]) is dict:
                x = sorted(d1[k], key=get_url)
                y = sorted(d2[k], key=get_url)
                if x != y:
                    print('fail list {} {}, lengths {} {}, {} {}'.format(d1['bibcode'], k, len(x), len(y), x, y))
                    fail = True
            else:
                x = sorted(d1[k])
                y = sorted(d2[k])
                if x != y:
                    print('fail list {} {}, lengths {}  {}, {}, {}'.format(d1['bibcode'], k, len(x), len(y), x, y))
                    fail = True
                    
        elif d1[k] != d2[k]:
            print('fail {} {}, {}, {}'.format(d1['bibcode'], k, d1[k], d2[k]))
            fail = True
    return fail


def get_url(d):
    return d.get('url', None)


if __name__ == '__main__':
    compare('/Users/smcdonald/tmp/solrDelta/20200826/newNonbibChanged.20200826', '/Users/smcdonald/tmp/solrDelta/20200826/oldNonbibChanged.20200826')

