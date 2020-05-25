
from subprocess import PIPE, Popen

from adsdata.file_defs import data_files
from adsdata import tasks

logger = tasks.app.logger


def execute(command, **kwargs):
    logger.debug('in diffs, executing shell command {}'.format(command))
    print('command = {}'.format(command))
    p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, **kwargs)
    out, err = p.communicate()
    return (p.returncode, out, err)


def sort_input_files(root_dir='logs/input/'):
    """the input files sorted in place to compute diffs"""
    # on my laptop, sorting bibcodes.list.can takes 30 seconds
    for x in data_files:
        f = root_dir + '/current/' + data_files[x]['path']
        command = 'sort -o {} {}'.format(f, f)
        logger.info('in diffs, sorting {}'.format(f))
        execute(command)


def compute_changed_bibcodes(root_dir='logs/input/'):
    """generates a list of changed bibcoces by comparing input files in directory named current to directory named previous

    we use comm to compare the old and new files, then strip changes down to just the canonical bibcodes
    for every input file we create a list of changed bibcodes, then we merge these changed bibcoes files"""
    for x in data_files:
        c = root_dir + '/current/' + data_files[x]['path']
        p = root_dir + '/previous/' + data_files[x]['path']
        changed_bibs = root_dir + '/current/' + data_files[x]['path'] + '.changedbibs'
        #          find changes  | remove comm leading tab, blanks|only bib  | dedup| filter out non-canonical
        command = "comm -3 {} {} | sed $'s/^[ \t]*//g' -e '/^$/d' | cut -f 1 | uniq | comm -1 -2 - {}  > {}".format(c, p, changed_bibs, root_dir + '/current/' + data_files['canonical']['path'])
        logger.info('in diffs, computing changes to {}'.format(c))
        execute(command)


def merge_changed_bibcodes(root_dir='logs/input/'):
    """merge small change bibcode files into a single file"""
    o = root_dir + '/current/' + 'changedBibcodes.txt'
    for x in data_files:
        f = root_dir + '/current/' + data_files[x]['path'] + '.changedbibs'
        command = 'cat {} >> {}'.format(f, o)
        logger.info('in diffs, concatenating changes from {}'.format(f))
        execute(command)
    command = 'sort --unique -o {} {}'.format(o, o)
    logger.info('in diffs, sorting changed bibcodes {}'.format(o))
    execute(command)

