
import traceback
import tasks
from file_defs import data_files

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
        self._iostream = open(filename, 'r')

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
            return self.process_value(self.default_value)

        # next, skip over lines in file until we:
        #   either find the passed bibcode or determine it isn't in the file
        skip_count = 0
        current_line = current_line.strip()
        while current_line[:19].strip() < bibcode:
            current_line = self.getline().strip()
            skip_count = skip_count + 1
            if not current_line:
                # app.logger.info('skip_count = {} for {}'.format(skip_count, self.filetype))
                return self.process_value(self.default_value)
        # app.logger.info('skip_count = {} for {} '.format(skip_count, self.filetype))

        # at this point, we have either read to the desired bibcode
        # or it doesn't exist and we read past it
        if bibcode != current_line[:19]:
            # bibcode not in file
            self.pushline(current_line)
            return self.process_value(self.default_value)

        if self.default_value is True or self.default_value is False:
            return self.process_value(True)  # boolean files hold singleton values

        # at this point, we have the first line with the bibcode in it
        # roll up possible other values on adjacent lines in file

        value = []
        value.append(current_line[20:].strip())
        current_line = self.getline()
        print('current line is {}'.format(current_line))
        while data_files[self.filetype].get('multiline', False) and (current_line is not None) and (bibcode == current_line[:19]):
            value.append(current_line[20:].strip())
            current_line = self.getline()
        # app.logger.info('number of read lines = {} for {}'.format(len(value), self.filetype))
            
        # at this point we have read beyond the desired bibcode, must back up
        # app.logger.info('file adjust going from {} to {} for {}'.format(self._iostream.tell(), current_location, self.filetype))
        self.pushline(current_line)
        # finally, convert raw input into something useful
        return self.process_value(value)
        
    def process_value(self, value):
        """convert file value to something more useful
        
        passed value is either default or string from file, convert to dict
        """
        if isinstance(value, str) and '\x00' in value:
            # there should not be nulls in strings
            app.logger.error('in columnFileIngest.process_value with null value in string: {}', value)
            value = value.replace('\x00', '')

        return_value = value
        # if return_value == ['']:
        #     # here when the file did not have a value (e.g., refereed, etc.)
        #    return_value = self.default_value 

        if isinstance(value, bool):
            return_value = value
        elif (len(value) == 1 and '\t' in value[0]):
            # tab separator in string means we need to convert elements to array
            return_value = value[0].split('\t')
            if data_files[self.filetype].get('string_to_number', True):
                # convert valid ints and floats to numeric representation
                t = []
                try:
                    for x in return_value:
                        if x.isdigit():
                            t.append(int(x))
                        elif isFloat(x):
                            t.append(float(x))
                        else:
                            # value is a string
                            t.append(x.strip())
                    return_value = t
                except ValueError as e:
                    app.logger.error('ValueError in reader.proces_value, value: {}, default_value: {}, {}'.format(value, self.default_value, str(e)))
                    app.logger.error(traceback.format_exc())
                    return_value = self.default_value

        elif (len(value) > 1) and 'subparts' in data_files[self.filetype]:
            # here on multi-line dict (e.g., associations)
            # interleave data on successive lines e.g., merge first element in each array, second element, etc.
            #   since they also have subparts, these arrays will then put in dict with the cooresponding key
            x = []
            for r in value:
                parts = r.split('\t')
                for i in range(len(parts)):
                    if i >= len(x):
                        x.append([])
                    x[i].append(parts[i].strip())
            return_value = x
        elif (len(value) > 1):
            x = []
            for r in value:
                x.append(r.replace('\t', ' ').strip())
            return_value = x
        # convert array to dict if needed
        if 'subparts' in data_files[self.filetype] and return_value != data_files[self.filetype]['default_value']:
            d = {}
            for i in range(len(data_files[self.filetype]['subparts'])):
                k = data_files[self.filetype]['subparts'][i]
                v = ''  # default value when file only contains first n values (e.g, 'title' value often not in line)
                if i < len(return_value):
                    v = return_value[i]
                d[k] = v
            return_value = d
        if 'extra_values' in data_files[self.filetype] and return_value != data_files[self.filetype]['default_value']:
            d.update(data_files[self.filetype]['extra_values'])
            return_value = d
        return {self.filetype: return_value}


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


