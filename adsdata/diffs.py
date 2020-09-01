
from subprocess import PIPE, Popen

from adsdata.file_defs import data_files
from adsdata import tasks

logger = tasks.app.logger

    #  - _sort_input_files(root_dir='logs/input/'):
    #  - _compute_changed_bibcodes(root_dir='logs/input/'):
    #  - _merge_changed_bibcodes(root_dir='logs/input/'):
    #  - _execute(command, **kwargs):


class Diff:
    """use shell commands to generate the list of changed bibcodes
    
    compares today's nonbib data to yesterday's
    list of changed bibcodes are put in a file"""

    @classmethod
    def compute(cls):
        logger.info('compute diffs starting')
        cls._sort_input_files()
        cls._compute_changed_bibcodes()
        cls._merge_changed_bibcodes()
        logger.info('compute diffs completed')

    @classmethod
    def execute(cls, command, **kwargs):
        """execute the passed shell command"""
        logger.info('in diffs, executing shell command {}'.format(command))
        p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, **kwargs)
        out, err = p.communicate()
        if p.returncode != 0:
            msg = 'error executing command {}, error code = {}, out = {}, err = {}'.format(command, p.returncode, out, err)
            logger.error(msg)
            raise OSError(msg)

    @classmethod
    def _sort_input_files(cls, root_dir='logs/input/'):
        """sort the input files in place"""
        for x in data_files:
            f = root_dir + '/current/' + data_files[x]['path']
            command = 'sort -o {} {}'.format(f, f)
            logger.info('in diffs, sorting {}'.format(f))
            cls.execute(command)

    @classmethod
    def _compute_changed_bibcodes(cls, root_dir='logs/input/'):
        """generates a list of changed bibcoces by comparing input files in directory named current to directory named previous

        we use comm to compare each old file to corresponding new file, then strip changes down to just the canonical bibcodes
        for every input file we create a file of changed bibcodes"""
        for x in data_files:
            c = root_dir + '/current/' + data_files[x]['path']
            p = root_dir + '/previous/' + data_files[x]['path']
            changed_bibs = root_dir + '/current/' + data_files[x]['path'] + '.changedbibs'
            # the process to computed changed bibcodes is:
            #          find changes  | remove comm leading tab, blank lines|get bibcode|dedup|filter out non-canonical  | current, previous, output file, today's canonical bibcodes
            command = "comm -3 {} {} | sed 's/^[ \\t]*//g' | sed '/^$/d' | cut -f 1 | uniq | comm -1 -2 - {}  > {}".format(c, p, root_dir + '/current/' + data_files['canonical']['path'], changed_bibs)
            logger.info('in diffs, computing changes to {}'.format(c))
            cls.execute(command)

    @classmethod
    def _merge_changed_bibcodes(cls, root_dir='logs/input/'):
        """merge all the small change bibcode files into a single file"""
        o = root_dir + '/current/' + 'changedBibcodes.txt'
        for x in data_files:
            f = root_dir + '/current/' + data_files[x]['path'] + '.changedbibs'
            command = 'cat {} >> {}'.format(f, o)
            logger.info('in diffs, concatenating changes from {}'.format(f))
            cls.execute(command)
        command = 'sort --unique -o {} {}'.format(o, o)
        logger.info('in diffs, sorting changed bibcodes {}'.format(o))
        cls.execute(command)



