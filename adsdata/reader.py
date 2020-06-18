
import traceback
from adsdata import tasks
from adsdata.file_defs import data_files

app = tasks.app


class ADSClassicInputStream(object):
    """file like object used to read nonbib column data files

    provides a useful wrapper around python file object
    """

    def __init__(self, filetype, filename):
        self.filename = filename
        self.filetype = filetype
        self.read_count = 0   # used in logging
        self.config = {}
        self.dottab_file = self.filename.endswith('.tab')
        self._iostream = open(filename, 'r', encoding='utf-8')

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()
    
    def __iter__(self):
        return self
    
    def next(self):
        return self._iostream.next()
    
    @classmethod
    def open(cls, file_):
        return cls(file_)

    def close(self):
        self._iostream.close()
        del self._iostream

    def read(self, size=-1):
        """called by iterators, use for column files where bibcodes are not repeated"""
        self.read_count += 1
        if self.read_count % 100000 == 0:
            app.logger.debug('nonbib file ingest, count = {}'.format(self.read_count))
            
        line = self._iostream.readline()
        #if len(line) == 0 or (self.config['MAX_ROWS'] > 0 and self.read_count > self.config['MAX_ROWS']):
        #    app.logger.info('nonbib file ingest, processed {}, contained {} lines'.format(self.filename, self.read_count))
        #    return ''
        return self.process_line(line)
    
    def readline(self):
        # consider changing to call read
        self.read_count += 1
        line = self._iostream.readline()
        return self.process_line(line)
    
    def process_line(self, line):
        return line


class StandardFileReader(ADSClassicInputStream):
    """reads nonbib column files

    processing is based on the file's properties dict
    requires file are sorted by bibcode
    """

    def __init__(self, filetype, filename):
        super(StandardFileReader, self).__init__(filetype, filename)
        self.filetype = filetype
        self.buffer = None  # holds at most one line of text
        self.default_value = False,
        if 'default_value' in data_files[filetype]:
            self.default_value = data_files[filetype]['default_value']

    def pushline(self, s):
        if self.buffer:
            app.logger.error('in file {}, {}, pushline called when buffer is not None: {}'.format(self.filetype, self.filename, self.buffer))
        self.buffer = s

    def getline(self):
        if self.buffer:
            x = self.buffer
            self.buffer = None
            return x
        else:
            return self._iostream.readline()

    def read_value_for(self, bibcode):
        """return the value from the file for the passed bibcode
        returns default value if bibcoce is not in file

        return value is a dict with the key of self.filetype
          dicts from reads on multiple files can be easily merged

        some files repeat a bibcode on consecutive lines to provide multiple values
        other files do not repeat a bibcode and provide multiple values on a single line
        other files (e.g., relevance/docmetrics.tab) have multiple values
        this reader handles all cases based on the file property dict
        """
        # first, are we at eof
        current_line = self.getline()
        if not current_line:
            # here if we are already at eof, bibcode isn't in file
            # app.logger.info('at eof for {} and {}'.format(self.filetype, bibcode))
            return self.convert_value(self.default_value)

        # next, skip over lines in file until we:
        #   either find the passed bibcode or determine it isn't in the file
        skip_count = 0
        current_line = current_line.strip()
        while current_line[:19].strip() < bibcode:
            current_line = self.getline().strip()
            skip_count = skip_count + 1
            if not current_line:
                return self.convert_value(self.default_value)

        # at this point, we have either read to the desired bibcode
        # or it doesn't exist and we read past it
        if bibcode != current_line[:19]:
            # bibcode not in file
            self.pushline(current_line)
            return self.convert_value(self.default_value)

        if isinstance(self.default_value, bool):
            return self.convert_value(True)  # boolean files hold singleton values

        # at this point, we have the first line with the bibcode in it
        # roll up possible other values on adjacent lines in file

        value = []
        value.append(current_line[20:].strip())
        current_line = self.getline()
        while data_files[self.filetype].get('multiline', False) and (current_line is not None) and (bibcode == current_line[:19]):
            value.append(current_line[20:].strip())
            current_line = self.getline()
        # app.logger.info('number of read lines = {} for {}'.format(len(value), self.filetype))
            
        # at this point we have read beyond the desired bibcode, must back up
        # app.logger.info('file adjust going from {} to {} for {}'.format(self._iostream.tell(), current_location, self.filetype))
        self.pushline(current_line)
        # finally, convert raw input into something useful
        return self.convert_value(value)
        
    def convert_value(self, value):
        """convert file string line to something more useful
        
        return a dict with filetype as key and value converted
        """

        if isinstance(value, str) and '\x00' in value:
            # there should not be nulls in strings
            app.logger.error('in columnFileIngest.convert_value` with null value in string: {}', value)
            value = value.replace('\x00', '')

        return_value = value
        if isinstance(value, bool):
            return_value = value
        elif (len(value) > 0 and '\t' in value[0] and not data_files[self.filetype].get('tabs_to_spaces', False)):
            # tab separator in string means we need to convert elements to array
            z = []
            for r in value:
                x = r.split('\t')
                if data_files[self.filetype].get('string_to_number', True):
                    # convert valid ints and floats to numeric representation
                    t = []
                    try:
                        for y in x:
                            if y.isdigit():
                                t.append(int(y))
                            elif isFloat(y):
                                t.append(float(y))
                            else:
                                # value is a string
                                t.append(y.strip())
                        z.append(t)
                    except ValueError as e:
                        app.logger.error('ValueError in reader.proces_value, value: {}, default_value: {}, {}'.format(value, self.default_value, str(e)))
                        app.logger.error(traceback.format_exc())
                        z.append(self.default_value)
            return_value = z
            if len(return_value) == 1:
                return_value = return_value[0]
                    
        elif (len(value) > 1) and 'interleave' in data_files[self.filetype]:
            # here on multi-line dict (e.g., associations)
            # interleave data on successive lines e.g., merge first element in each array, second element, etc.
            #   since they also have subparts, these arrays will then put in dict with the cooresponding key
            x = {}
            for k in data_files[self.filetype]['subparts']:
                x[k] = []
            for r in value:
                parts = r.split(' ', 1)
                ks = data_files[self.filetype]['subparts']
                for i in range(len(parts)):
                    k = ks[i]
                    if i >= len(x):
                        v = ''
                    v = parts[i].strip()
                    x[k].append(v)
            return_value = x
        elif (data_files[self.filetype].get('tabs_to_spaces', False)):
            # files like simbad_objects have tabs that we simply convert to spaces
            x = []
            for a in value:
                x.append(a.replace('\t', ' '))
            return_value = x
        elif (len(value) > 1):
            x = []
            for r in value:
                x.append(r.replace('\t', ' ').strip())
            return_value = x
        # convert array to dict if needed
        if 'subparts' in data_files[self.filetype] and return_value != data_files[self.filetype]['default_value'] and 'interleave' not in data_files[self.filetype]:
            if type(return_value[0]) is list:
                x = []
                for r in return_value:
                    x.append(self.convert_subparts(r))
            else:
                x = self.convert_subparts(return_value)
            return_value = x

        # are there extra_values to add to dict
        if 'extra_values' in data_files[self.filetype]:
            self.add_extra_values(return_value)
        return {self.filetype: return_value}

    def add_extra_values(self, current):
        if current != data_files[self.filetype]['default_value'] and type(current) is dict:
            current.update(data_files[self.filetype]['extra_values'])
        elif current != data_files[self.filetype]['default_value'] and type(current) is list:
            # here with array of dicts, put extra_values in each dict
            for x in current:
                v = data_files[self.filetype]['extra_values']
                if type(v) is dict and type(x) is dict:
                    x.update(v)
                else:
                    app.logger.error('serious error in reader.add_extra_values, non dict value, bibcode = {}, x = {}, value = {}, current = {}'.format(current.get('canonical', 'not available'), x, v, current))

    def convert_subparts(self, current):
        d = {}
        for i in range(len(data_files[self.filetype]['subparts'])):
            k = data_files[self.filetype]['subparts'][i]
            if type(k) is list:
                # here if key is in a list by itself which means values should be in a list
                k = k[0]
                v = ''
                if i < len(current):
                    v = current[i]
                v = [v]
            else:
                v = ''  # default value when file only contains first n values (e.g, 'title' value often not in line)
                if i < len(current):
                    v = current[i]
            d[k] = v
        return d


def isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class TestFileReader(StandardFileReader):

    def __init__(self, filetype, filename):
        super(StandardFileReader, self).__init__(filetype, filename)

    def read_value_for(self, bibcode):
        current_line = self._iostream.readline()
        return current_line


