
from subprocess import PIPE, Popen

from file_defs import data_files


def execute(command, **kwargs):
    p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, **kwargs)
    out, err = p.communicate()
    return (p.returncode, out, err)


def sort_input_files(root_dir='logs/input/'):
    """the input files must be sorted to compute diffs"""
    # on my laptop, sorting bibcodes.list.can takes 30 seconds
    for x in data_files:
        f = root_dir + '/current/' + data_files[x]['path']
        c = 'sort -o {} {}'.format(f, f)
        execute(c)

        
def compute_changed_bibcodes(root_dir='logs/input/'):
    # comm -1 -3 bibcodes.list.can.20200428 bibcodes.list.can.20200426
    



# (root_dir=app.conf['INPUT_DATA_ROOT'])
