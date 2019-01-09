import re
from collections import defaultdict
import pandas as pd

text_to_parse = """
Start
Process 8 finished in 7.1139s.

Process 2 finished in 7.1888s.

Process 5 finished in 7.1996s.

Process 6 finished in 8.9562s.

Process 3 finished in 8.9944s.

Process 9 finished in 9.0358s.

Process 7 finished in 10.3570s.

Process 4 finished in 10.4160s.

Process 1 finished in 10.4978s.

End
Start
Process 9 finished in 7.0031s.

Process 3 finished in 7.0874s.

Process 6 finished in 7.0876s.

Process 5 finished in 8.3848s.

Process 8 finished in 8.4303s.

Process 2 finished in 8.4481s.

Process 4 finished in 10.5088s.

Process 1 finished in 10.5558s.

Process 7 finished in 10.5998s.

End
Start
Process 3 finished in 6.5676s.

Process 9 finished in 6.6205s.

Process 6 finished in 6.6859s.

Process 8 finished in 10.0332s.

Process 5 finished in 10.0759s.

Process 2 finished in 10.0980s.

Process 4 finished in 10.3889s.

Process 1 finished in 10.5298s.

Process 7 finished in 10.5578s.

End
"""

def has_mo_match(matched_object):
    if matched_object is not None:
        return True
    else:
        return False
        
# def parse_start(line):
#     matched = re.compile(r'Start').search(line)
#     if has_mo_match(matched):
#         return matched.group()
#     else:
#         return None
        
def parse_pid_time(line):
    matched = re.compile(r'\s(\d+).*?(\d{1,6}\.\d{1,6})').search(line)
    if has_mo_match(matched):
        return matched.group(1), matched.group(2)
    else:
        return None
        
def parse_end(line):
    matched = re.compile(r'End').search(line)
    if has_mo_match(matched):
        return matched.group()
    else:
        return None

# Init an empty defaultdict
measurements = defaultdict(dict)
# keep track of the number of measurements in the log file
measurement_counter = 1
tokenized_text = text_to_parse.splitlines()
for line in tokenized_text:
    if parse_pid_time(line) != None:
        # line contains process id and time, let's save them
        result = parse_pid_time(line)
        pid = 'CPU ' + result[0]
        time = result[1]
        # add the process id and its time to measurements dict
        # at measurement_counter
        measurements[measurement_counter][pid] = time
    elif parse_pid_time(line) is None and parse_end(line) is not None:
        # line contains End marker, increment the measurement_counter by 1
        measurement_counter += 1
# convert the measurements dict to a dataframe
df = pd.DataFrame(measurements).T
# rename the df index to Measurements
df.index.name = 'Measurements'
# convert this df to a csv file
df.to_csv('test.csv', encoding='utf-8')