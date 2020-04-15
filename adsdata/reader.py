
from adsputils import setup_logging, load_config


class ADSClassicInputStream(object):
    """file like object used to read nonbib column data files

    provides a useful wrapper around python file object
    """

    def __init__(self, file_):
        self._file = file_
        self.read_count = 0   # needed for logging
        ## self.logger = setup_logging('AdsDataSqlSync', 'DEBUG')
        ## self.logger.info('nonbib file ingest, file {}'.format(self._file))
        self.config = {}
        ## self.config.update(load_config())
        self.dottab_file = self._file.endswith('.tab')
        self._iostream = open(file_, 'r')

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
            self.logger.debug('nonbib file ingest, count = {}'.format(self.read_count))
            
        line = self._iostream.readline()
        if len(line) == 0 or (self.config['MAX_ROWS'] > 0 and self.read_count > self.config['MAX_ROWS']):
            self.logger.info('nonbib file ingest, processed {}, contained {} lines'.format(self._file, self.read_count))
            return ''
        return self.process_line(line)
    
    def readline(self):
        # consider changing to call read
        self.read_count += 1
        line = self._iostream.readline()
        return self.process_line(line)
    
    def process_line(self, line):
        return line
    
   
class BibcodeFileReader(ADSClassicInputStream):
    """add id field to bibcode"""
    
    def __init__(self, file_):
        super(BibcodeFileReader, self).__init__(file_)

    def process_line(self, line):
        return line.strip()
    
    def read_bibcode(self):
        bibcode = self.readline()
        if bibcode:
            bibcode = bibcode.strip()
        return bibcode
    

class StandardFileReader(ADSClassicInputStream):
    """reads most nonbib column files

    can read files where for a bibcode is on one line or on consecutive lines
    """

    def __init__(self, file_, data_type=list):
        super(StandardFileReader, self).__init__(file_)
        self.data_type = data_type

    def read_value_for(self, bibcode):
        """return the value from the file for the passed bibcode or None if not in file

        requires file are sorted by bibcode
        the file may not info for the requested bibcode
        some files repeat a bibcode on consecutive lines to provide multiple values
        other files do not repeat a bibcode and provide multiple values on a single line

        """
        # first, skip over lines in file
        # until we either find the passed bibcode or determine it isn't in the file
        start_location = self._iostream.tell()
        current_location = start_location
        current_line = self._iostream.readline()
        if not current_line:
            print 'already at eof, bibcode = {}'.format(bibcode)
            return None    # eof
        current_line = current_line.strip()
        while current_line[:19].strip() < bibcode:
            current_location = self._iostream.tell()
            current_line = self._iostream.readline().strip()
            if not current_line:
                return None    # eof

        # at this point, we have either read to the desired bibcode
        # or it doesn't exist and we read past it
        if bibcode != current_line[:19]:
            # bibcode not in file
            self._iostream.seek(start_location)    # perhaps this backs up more than needed, I'm not sure
            self._get_absent_value()

        # at this point, we have the first line with the bibcode in it
        # roll up other values on adjacent lines in file        
        value = []
        while (current_line is not None) and (bibcode == current_line[:19]):  # is true at least once
            value.append(current_line[20:].strip())
            current_location = self._iostream.tell()
            current_line = self._iostream.readline()

        # at this point we have read beyond the desired bibcode, must back up
        self._iostream.seek(current_location)
        # if file had no value for the bibcode (e.g., refereed) generate default value
        return self.process_value(value)
        
    def process_value(self, value):
        """convert file value to something more useful"""
        if isinstance(value, str) and '\x00' in value:
            # there should not be nulls in strings
            self.logger.error('in columnFileIngest.process_value with null value in string: {}', value)
            value = value.replace('\x00', '')

        return_value = value
        if return_value == ['']:
            # here when the file did not have a value (e.g., refereed, etc.)
            return_value = self._get_default_value()

        elif len(return_value) == 1 and isinstance(return_value[0], str) and '\t' in return_value[0]:
            # tab separator in string means we need to convert to array
            # if the array has more than one element it is an error
            # print('error processing file {}, there were multiple lines in file containing tabs {}, first line was used'.format(self._file, value))
            return_value = return_value[0].split('\t')
            if return_value[0].replace('.', '', 1).isdigit():   #  and not self.dottab_file:
                t = []
                for i in return_value:
                    if i.isdigit():
                        t.append(int(i))
                    else:
                        t.append(float(i))
                # t = [int(i) for i in return_value]
                return_value = t
        return return_value

    def _get_absent_value(self):
        if self.data_type is bool:
            return False
        elif self.data_type is list:
            return []

    def _get_default_value(self):
        # for these boolean file we assign a default value of True
        if self.data_type is bool:
            return True
        elif self.data_type is list:
            return []


# for datalinks table entries that may or may not have a link_sub_type
# that includes ARTICLE types that do have sub_type and
# for example PRESENTATION, LIBRARYCATALOG, and INSPIRE	 that do not
# note that these entries do not have a title
class DataLinksFileReader(StandardFileReader):

    def __init__(self, file_type_, file_, link_type_, link_sub_type_):
        super(DataLinksFileReader, self).__init__(file_type_, file_)
        self.link_type = link_type_
        self.link_sub_type = link_sub_type_

    def process_line(self, bibcode, value):
        as_array = self.file_type in self.array_types
        quote_value = self.file_type in self.quote_values
        tab_separator = self.file_type in self.tab_separated_values
        value = [v.replace('"', '').replace('\r', '') for v in value]
        processed_url = self.process_value(value, as_array, quote_value, tab_separator)
        row = '{}\t{}\t{}\t{}\t{}\t{}\n'.format(bibcode, self.link_type, self.link_sub_type, processed_url, "{""}", 0)
        return row

# for datalinks table entries that have titles, but no link_sub_type
# right now only link_type = ASSOCIATED belongs to this category
class DataLinksWithTitleFileReader(StandardFileReader):

    def __init__(self, file_type_, file_, link_type_):
        super(DataLinksWithTitleFileReader, self).__init__(file_type_, file_)
        self.link_type = link_type_

    def split(self, value):
        # value is a list of strings with two fields,
        # find the first space and split on that
        # create two lists of url and titles and return them
        url_list = []
        title_list = []
        for v in value:
            [url, title] = v.split(' ', 1)
            url_list.append(url.replace('"', ""))
            title_list.append(title.replace('"', "'"))
        return url_list, title_list

    def process_line(self, bibcode, value):
        as_array = self.file_type in self.array_types
        quote_value = self.file_type in self.quote_values
        tab_separator = self.file_type in self.tab_separated_values
        [url_list, title_list] = self.split(value)
        processed_url = self.process_value(url_list, as_array, quote_value, tab_separator)
        processed_title = self.process_value(title_list, as_array, quote_value, tab_separator)
        row = '{}\t{}\t{}\t{}\t{}\t{}\n'.format(bibcode, self.link_type, "NA", processed_url, processed_title, 0)
        return row


# for datalinks table entries that have may or may not have title but they do have link_sub_type
# that we are calling target, right now only link_type = DATA belongs to this category
class DataLinksWithTargetFileReader(StandardFileReader):

    def __init__(self, file_type_, file_, link_type_):
        super(DataLinksWithTargetFileReader, self).__init__(file_type_, file_)
        self.link_type = link_type_

    def _separate(self, line):
        if (len(line) == 0):
            return ['', '', '']
        parts = line.split('\t', 2)
        return [parts[0], parts[1], parts[1]+'\t'+parts[2]]

    def _bibcode_linktype_match(self, bibcode, liketype):
        """ peek ahead to next line for bibcode and check for mactch"""
        file_location = self._iostream.tell()
        next_line = self._iostream.readline()
        self._iostream.seek(file_location)
        next_bib, next_type, therest = self._separate(next_line)
        if bibcode == next_bib and liketype == next_type:
            return True
        return False

    def read(self, size=-1):
        """returns the data from the file for the next bibcode

        peeks ahead in file and concatenates data if its bibcode matches
        makes at least one and potentially multiple readline calls on iostream """
        self.read_count += 1
        if self.read_count % 100000 == 0:
            self.logger.debug('nonbib file ingest, processing {}, count = {}'.format(self.file_type, self.read_count))
        line = self._iostream.readline()
        if len(line) == 0 or (self.config['MAX_ROWS'] > 0 and self.read_count > self.config['MAX_ROWS']):
            self.logger.info('nonbib file ingest, processed {}, contained {} lines'.format(self._file, self.read_count))
            return ''

        bibcode, linktype, therest = self._separate(line)
        while ' ' in bibcode or len(bibcode) != 19:
            self.logger.error('invalid bibcode {} in file {}'.format(bibcode, self._file))
            line = self._iostream.readline()
            bibcode, linktype, therest = self._separate(line)
        value = therest

        # does the next line match the current bibcode?
        match = self._bibcode_linktype_match(bibcode, linktype)

        if self.file_type in (self.array_types):
            value = [value]
        while match:
            line = self._iostream.readline()
            bibcode, linktype, therest = self._separate(line)
            value.append(therest)
            match = self._bibcode_linktype_match(bibcode, linktype)
        return self.process_line(bibcode, value)

    def split(self, value):
        # SIMBAD	1	http://$SIMBAD$/simbo.pl?bibcode=1907ApJ....25...59C	SIMBAD Objects (1)
        # value is a list of strings with four elements,
        # split on tab, create 4 lists and return them

        url_list = []
        title_list = []
        target_list = set()
        count_list = []
        sum_count = 0
        for v in value:
            [target, count, url, title] = v.split('\t', 3)
            url_list.append(url.replace('"', ""))
            title_list.append(title.replace('"', "'").replace('\n', ''))
            target_list.add(target)
            sum_count += int(count)
        count_list.append(str(sum_count))
        return url_list, title_list, list(target_list), count_list

    def process_line(self, bibcode, value):
        as_array = self.file_type in self.array_types
        quote_value = self.file_type in self.quote_values
        tab_separator = self.file_type in self.tab_separated_values
        [url_list, title_list, target_list, count_list] = self.split(value)
        processed_url = self.process_value(url_list, as_array, quote_value, tab_separator)
        processed_title = self.process_value(title_list, as_array, quote_value, tab_separator)
        processed_target = self.process_value(target_list, False, False, tab_separator)
        processed_count = self.process_value(count_list, False, False, tab_separator)
        row = '{}\t{}\t{}\t{}\t{}\t{}\n'.format(bibcode, self.link_type, processed_target, processed_url, processed_title, processed_count)
        return row
