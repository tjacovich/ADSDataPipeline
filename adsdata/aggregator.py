
from file_defs import data_files
import reader

class TestAggregator:
    """just read files, used in performace testing"""
    
    def read_next(self):
        bibcode = ''
        values = []
        for x in data_files:
            if x is 'canonical':
                bibcode = data_files['canonical']['file_descriptor'].readline().strip()
                if bibcode is None:
                    return None
            else:
                values.append(data_files[x]['file_descriptor'].readline().strip())
        return ', '.join(values)

    def open_all(root_dir=None):
        """simply open file descriptors to all the input files

    we store these descriptors in the file properties object"""

    root_dir = './adsdata/tests/data1/config/'

    for x in data_files:
        data_files[x]['file_descriptor'] = reader.TestFileReader(x, root_dir + data_files[x]['path'])
