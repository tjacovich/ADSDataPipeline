
from adsdata import tasks
from adsdata.file_defs import data_files

app = tasks.app


class NonbibFileReader(object):
    """reads nonbib column files

    file reading/parsing is controlled by the file's properties dict in file_defs
    every line must start with a bibcode
    file must be sorted by bibcode
    """

    bibcode_length = 19

    def __init__(self, filetype, filename):
        self.filetype = filetype
        self.filename = filename
        self.read_count = 0   # used in logging
        self.buffer = None  # holds at most one line of text
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

    def pushline(self, s):
        """the buffer is used when we read a line that is behond the desired bibcode
           and we need to unread it"""
        if self.buffer:
            app.logger.error('error in file {}, {}, pushline called when buffer was not empty.  File line number: read line: {}, buffer: {}'.format(self.filetype, self.filename, self.read_count, s, self.buffer))
        self.buffer = s

    def readline(self):
        """used to read file containing list of canonical bibcodes"""
        self.read_count += 1
        line = self._iostream.readline()
        while len(line) > 0 and len(line) < self.bibcode_length:
            app.logger.error('error, invalid short line in readline {} filename: {} at line {}, line length less then length of bibcode, line: {}'.format(self.filetype, self.filename, self.read_count, line))
            self.read_count += 1
            line = self._iostream.readline()
        return line
    
    def getline(self):
        """returns the next valid line or empty string at eof"""
        if self.buffer:
            x = self.buffer
            self.buffer = None
            return x
        elif self._iostream.closed:
            return ''
        
        self.read_count += 1
        x = self._iostream.readline()
        while len(x) > 0 and len(x) < self.bibcode_length:
            app.logger.error('error, invalid short line in file {} filename: {} at line {}, line length less then length of bibcode, line: {}'.format(self.filetype, self.filename, self.read_count, x))
            self.read_count += 1
            x = self._iostream.readline()
        return x

    def read_value_for(self, bibcode):
        """return the value from the file for the passed bibcode
        returns default value if bibcoce is not in file

        return value is a dict with the key of self.filetype

        some files repeat a bibcode on consecutive lines to provide multiple values
        other files do not repeat a bibcode and provide multiple values on a single line
        other files (e.g., relevance/docmetrics.tab) have multiple values
        some files have associated effects on values like property field
        this reader handles all cases based on the file property dict
        """
        # first, are we at eof
        current_line = self.getline()
        if not current_line:
            # here if we are already at eof, bibcode isn't in file
            return self.convert_value(data_files[self.filetype]['default_value'])

        # next, skip over lines in file until we:
        #   either find the passed bibcode or determine it isn't in the file
        skip_count = 0
        while len(current_line) != 0 and self.get_bibcode(current_line) < bibcode:
            current_line = self.getline()
            skip_count = skip_count + 1

        # at this point, we have either read to the desired bibcode
        # or it doesn't exist and we read past it
        if len(current_line) == 0 or bibcode != self.get_bibcode(current_line):
            # bibcode not in file
            self.pushline(current_line)
            return self.convert_value(data_files[self.filetype]['default_value'])

        if isinstance(data_files[self.filetype]['default_value'], bool):
            return self.convert_value(True)  # boolean files only hold bibcodes, all values are True

        # at this point, we have the first line with the bibcode in it
        # roll up possible other values on adjacent lines in file
        value = []
        value.append(self.get_rest(current_line))
        current_line = self.getline()
        while data_files[self.filetype].get('multiline', False) and (current_line is not None) and (bibcode == self.get_bibcode(current_line)):
            value.append(self.get_rest(current_line))
            current_line = self.getline()
            
        # at this point we have read beyond the desired bibcode, must back up
        self.pushline(current_line)
        # finally, convert raw input into something useful
        return self.convert_value(value)
        
    def convert_value(self, value):
        """convert file string line to something more useful
        
        return a dict with filetype as key and value converted
        """

        if isinstance(value, str) and '\x00' in value:
            # there should not be nulls in strings
            app.logger.error('error string contained a null in file {} {}, line number: {}, value: {}'.format(self.filetype, self.filename, self.read_count, value))
            value = value.replace('\x00', '')

        return_value = value
        if isinstance(value, bool):
            d = {self.filetype: return_value}
            if 'extra_values' in data_files[self.filetype] and value != data_files[self.filetype]['default_value']:
                d.update(data_files[self.filetype]['extra_values'])
            return {self.filetype: d}
        elif (len(value) > 0 and '\t' in value[0] and not data_files[self.filetype].get('tabs_to_spaces', False)):
            # tab separator in string means we need to convert elements to array
            z = []
            for r in value:
                x = r.split('\t')
                if data_files[self.filetype].get('string_to_number', True):
                    # convert valid ints and floats to numeric representation
                    t = []
                    for y in x:
                        t.append(self.convert_scalar(y))
                    z.append(t)
            return_value = z
            if len(return_value) == 1:
                return_value = return_value[0]
                    
        elif 'interleave' in data_files[self.filetype] and value != data_files[self.filetype]['default_value']:
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
                    app.logger.error('serious error in reader.add_extra_values, non dict value, value = {}, current = {}'.format(x, v, current))

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

    def get_bibcode(self, s):
        """return the  bibcode from the from of the line"""
        if s is None:
            return None
        if len(s) < self.bibcode_length:
            app.logger.error('error, invalid short line in file {} {} at line {}, line length less then length of bibcode'.format(self.filetype, self.filename, self.read_count, s))
            return s
        return s[:self.bibcode_length].strip()

    def get_rest(self, s):
        """return the text after the bibcode and first tab separator"""
        return s[self.bibcode_length + 1:].strip()
                                 
    def convert_scalar(self, s):
        if s.isdigit():
            return int(s)
        try:
            x = float(s)
            return x
        except ValueError:
            return s.strip()

