
import csv
import json
import sys
from datetime import datetime
import time as mod_time


DATE_COLS = ("closed_date", "created_date", "due_date", "resolution_action_updated_date")
DATE_FORMAT = "%m/%d/%Y %I:%M:%S %p"

def timestamp(dt):
    return int((mod_time.mktime(dt.timetuple()) + dt.microsecond / 1000000.0))



class NYCDataLine(object):
    def __init__(self, headers, line):
        self.line =  line
        self.headers = headers

    def prep_timestamps(self):
        def convert(val):
            return int(timestamp(datetime.strptime(val, DATE_FORMAT)) * 1000) if val else None

        for i in xrange(len(self.line)):
            if self.headers[i] in DATE_COLS: self.line[i] = convert(self.line[i])

        return self

    def prep_nulls(self):
        self.line = map(lambda x: None if not x or x == 'Unspecified' else x, self.line)
        return self

    def to_dict(self):
        return dict(zip(self.headers, self.line))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Please provide a csv file to convert"
        sys.exit(1)
    try:
        with open(sys.argv[1], 'r') as csvfile:
            # Start reading the CSV and use the first line as headers
            reader = csv.reader(csvfile, delimiter=',')
            keys = map(lambda x: x.lower().replace(" ", "_"), next(reader))

            # Turn each line into a dictionary
            # Save to a file
            with open('%s.json' % (sys.argv[1]), 'w') as jsonfile:
                for line in reader:
                    data = NYCDataLine(keys, line)
                    jsonl = data.prep_timestamps().prep_nulls().to_dict()

                    agency = jsonl['agency']
                    del jsonl['agency']

                    jsonl['agency'] = {
                        '3L': agency,
                        'Name': jsonl['agency_name']
                    }

                    if jsonl['longitude'] and jsonl['latitude']:
                        jsonl['geometry'] = [float(jsonl['longitude']), float(jsonl['latitude'])]
                    else:
                        jsonl['geopoint'] = None

                    data = json.dumps(jsonl, ensure_ascii=False)
                    jsonfile.write(str(data))
                    jsonfile.write('\n')
    except IOError:
        print 'Error: could not read input file.'
        sys.exit(1)
