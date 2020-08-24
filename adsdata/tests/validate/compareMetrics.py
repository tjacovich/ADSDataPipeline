
import json

# metrics column from master pipeline records table holds a json formatted string.
# we read two files of exported metrics data (exported from 2 different master pipeline databases)
# this directory includes a script file to create the export data file
# the filenames of the two files to open are currently hardcoded


def compare(file1, file2):
    with open(file1) as f1, open(file2) as f2:
        for x, y in zip(f1, f2):
            l1 = x.strip()
            l2 = y.strip()
            if len(l1) > 0 or len(l2) > 0:
                d1 = json.loads(l1)
                d2 = json.loads(l2)
                d1.pop('modtime', None)
                d2.pop('modtime', None)
                fail = False
                for k in d1:
                    fail = compare_aux(k, d1, d2)
                    if fail is False:
                        print('success!! {}'.format(d1['bibcode']))
                            

def compare_aux(k, d1, d2):
    fail = False
    if k == 'rn_citations_hist':
        for k2 in d1[k]:
            if d1[k][k2] != d2[k][k2]:
                print('fail3 {} {} {} {} {}'.format(d1['bibcode'], k, k2, d1[k][k2], d2[k][k2]))
                fail = True
    elif k == 'rn_citation_data':
        # an array of dicts where bibcode is unique
        # [{"cityear": 1953, "pubyear": 1951, "auth_norm": 0.3333333432674408, "bibcode": "1953PPSB...66..728K", "ref_norm": 0.16666}]
        if len(d1[k]) != len(d2[k]):
            print('fail, rn_citation_data arrays of different length {}, {}, {}.  {} {}'.format(d1['bibcode'], len(d1[k]), len(d2[k]), d1, d2))
            fail = True
        for r1 in d1[k]:
            current_bibcode = r1['bibcode']
            r2 = get_citation_data_dict(current_bibcode, d2[k])
            if r2 is None or r1 is None:
                print('fail, bibcode {} not in rn_citation_data {}'.format(current_bibcode, d2))
                fail = True
            elif r1['cityear'] != r2['cityear']:
                print('fail, cityear does not match{}, {}, {}'.format(d1['bibcode'], r1, r2))
                fail = True
            elif r1['pubyear'] != r2['pubyear']:
                print('fail, pubyear does not match{}, {}, {}'.format(d1['bibcode'], r1, r2))
                fail = True
            elif abs(r1['auth_norm'] - r2['auth_norm']) > r1['auth_norm'] * .05:
                print('fail, auth_norm does not match{}, {}, {}'.format(d1['bibcode'], r1, r2))
                fail = True
            elif abs(r1['ref_norm'] - r2['ref_norm']) > r1['ref_norm'] * .05:
                print('fail, ref_norm does not match{}, {}, {}'.format(d1['bibcode'], r1, r2))
                fail = True
    elif type(d1[k]) in (str, int, bool):
        if d1[k] != d2[k]:
            print('fail1 {} {} {} {}'.format(d1['bibcode'], k, d1[k], d2[k]))
            fail = True
    elif type(d1[k]) is list and k == 'data_links_rows':
        print(k, d1[k])
        print(k, d2[k])
        if sorted(d1[k], key=get_url) != sorted(d2[k], key=get_url):
            print('fail7 {} {} {} {}'.format(d1['bibcode'], k, d1[k], d2[k]))
            fail = True
    elif type(d1[k]) is list:
        if k not in d2:
            print('fail list, key not in both dicts {} {}, {}'.format(d1['bibcode'], k, d1[k]))
            fail = True
        elif d1[k].sort() != d2[k].sort():
            print('fail list on key {}, {}, {}'.format(k, d1[k], d2[k]))
            fail = True
    elif type(d1[k]) is float:
        if abs(d1[k] - d2[k]) > d1[k] * .05:
            print('fail2 {} {} {} {}'.format(d1['bibcode'], k, d1[k], d2[k]))
            fail = True
    elif type(d1[k]) is dict:
        for k2 in d1[k]:
            if type(d1[k][k2]) in (str, int, bool, list):
                if d1[k][k2] != d2[k][k2]:
                    print('fail4 {} {} {} {} {}'.format(d1['bibcode'], k, k2, d1[k][k2], d2[k][k2]))
                    fail = True
            elif type(d1[k]) is float:
                if abs(d1[k], d2[k]) > d1[k] * .05:
                    print('fail5 {} {} {} {}'.format(d1['bibcode'], k, k2, d1[k][k2], d2[k][k2]))
                    fail = True
            else:
                print('in dict, did not handle key:: {} {} {}, {}'.format(k, type(k2), k2, d1['bibcode']))
                fail = True 

    else:
        print('did not handle key {} {} , {}, {}, {}'.format(type(k), k, type(d1[k]), d1['bibcode'], d2['bibcode']))
        fail = True
    return fail


def get_url(d):
    return d.get('url', None)


def get_citation_data_dict(bibcode, a):
    for r in a:
        if r['bibcode'] == bibcode:
            return r
    return None


if __name__ == '__main__':
    compare('/Users/smcdonald/tmp/solrDelta/20200804/newMetricsChanged.20200804', '/Users/smcdonald/tmp/solrDelta/20200804/oldMetricsChanged.20200804')
