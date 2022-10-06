import os
from subprocess import PIPE, Popen

from adsdata.file_defs import data_files, data_files_CC, network_files
from adsdata import tasks

logger = tasks.app.logger

class Diff:
    """use shell commands to generate the list of changed bibcodes
    compares today's nonbib data to yesterday's
    list of changed bibcodes are put in a file"""
    @classmethod
    def compute(cls, CC_records = False):
        logger.info('compute diffs starting')
        cls._sort_input_files(CC_records = CC_records)
        cls._compute_changed_bibcodes(CC_records = CC_records)
        cls._merge_changed_bibcodes(CC_records = CC_records)
        cls._merge_network_files(CC_records = CC_records)
        logger.info('compute diffs completed')

    @classmethod
    def execute(cls, command, **kwargs):
        """execute the passed shell command"""
        logger.info('in diffs, executing shell command {}'.format(command))
        env = os.environ.copy()
        env["LC_ALL"] = "C" # force sorting to be byte-wise (compatible with python string comparison)
        p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, env=env, **kwargs)
        out, err = p.communicate()
        if p.returncode != 0:
            msg = 'error executing command {}, error code = {}, out = {}, err = {}'.format(command, p.returncode, out, err)
            logger.error(msg)
            raise OSError(msg)

    @classmethod
    def _sort_input_files(cls, root_dir='logs/input/', CC_records = False):
        """sort the input files in place"""
        if CC_records: 
            data_bib = data_files_CC 
        else: 
            data_bib = data_files

        for x in data_bib:
            f = root_dir + '/current/' + data_bib[x]['path']
            command = 'sort -o {} {}'.format(f, f)
            logger.info('in diffs, sorting {}'.format(f))
            cls.execute(command)

    @classmethod
    def _compute_changed_bibcodes(cls, root_dir='logs/input/', CC_records=False):
        """generates a list of changed bibcodes by comparing input files in directory named current to directory named previous
        we use comm to compare each old file to corresponding new file, then strip changes down to just the canonical bibcodes
        for every input file we create a file of changed bibcodes"""
        if CC_records: 
            data_bib = data_files_CC 
        else: 
            data_bib = data_files

        for x in data_bib:
            c = root_dir + '/current/' + data_bib[x]['path']
            p = root_dir + '/previous/' + data_bib[x]['path']
            changed_bibs = root_dir + '/current/' + data_bib[x]['path'] + '.changedbibs'
            
            #if the path does not exist in previous/ (possible for CC_records) initialize an empty file.
            if not os.path.isfile(p) and CC_records:
                command = "touch -d {}".format(p)
                cls.execute(command)

            # the process to computed changed bibcodes is:
            #          find changes  | remove comm leading tab, blank lines|get bibcode|dedup|filter out non-canonical  | current, previous, output file, today's canonical bibcodes
            command = "comm -3 {} {} | sed 's/^[ \\t]*//g' | sed '/^$/d' | cut -f 1 | uniq | comm -1 -2 - {}  > {}".format(c, p, root_dir + '/current/' + data_bib['canonical']['path'], changed_bibs)
            logger.info('in diffs, computing changes to {}'.format(c))
            cls.execute(command)

    @classmethod
    def _merge_changed_bibcodes(cls, root_dir='logs/input/', CC_records = False):
        """merge all the small change bibcode files into a single file"""
        if CC_records: 
            data_bib = data_files_CC 
            o = root_dir + '/current/' + 'changedBibcodes_CC.txt'

        else: 
            data_bib = data_files
            o = root_dir + '/current/' + 'changedBibcodes.txt'

        for x in data_bib:
            f = root_dir + '/current/' + data_bib[x]['path'] + '.changedbibs'
            command = 'cat {} >> {}'.format(f, o)
            logger.info('in diffs, concatenating changes from {}'.format(f))
            cls.execute(command)
        command = 'sort --unique -o {} {}'.format(o, o)
        logger.info('in diffs, sorting changed bibcodes {}'.format(o))
        cls.execute(command)

    @classmethod
    def _merge_network_files(cls, root_dir='logs/input/', CC_records = False):
        """Generate merged versions of the citation and reference files. Copy Classic files if CC_records not included."""
        #We only want to generate merged files for ones that CitationCapture records need.
        for x in network_files:
            if x != 'refereed':
                o = root_dir + '/current/' + network_files[x]['path']
                f = root_dir + '/current/' + data_files[x]['path']
                command = 'cat {} > {}'.format(f, o)
                logger.info('in diffs, concatenating changes from {}'.format(f))
                cls.execute(command)
        
        if CC_records:
            for x in network_files:
                if x != 'refereed':
                    o = root_dir + '/current/' + network_files[x]['path']
                    f = root_dir + '/current/' + data_files_CC[x]['path']
                    command = 'cat {} >> {}'.format(f, o)
                    logger.info('in diffs, concatenating changes from {}'.format(f))
                    cls.execute(command)
                    command = 'sort --unique -o {} {}'.format(o, o)
                    logger.info('in diffs, sorting entries in {}'.format(o))
                    cls.execute(command)

