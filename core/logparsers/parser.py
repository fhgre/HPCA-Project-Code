import re
from collections import defaultdict
import pandas as pd
from sys import argv

def has_mo_match(matched_object):
    if matched_object is not None:
        return True
    else:
        return False
        
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

def sanitize_filename(name):
    # TODO For each log file generate a csv file:
    # Sequential/parallel PI logs naming convention:
    # mpi$num_nodes.$num_trials_scientific_notation.log
    # Sequential/parallel MatMul logs naming convention:
    # mpi$num_nodes.$mat_dim.log
    err_list = [False,'']
    if 'mpi' not in name and 'log' not in name:
        return err_list

    # Name looks promising, let's tokenize it
    tokenized_name = name.split('.')
    # try to pop log extension, don't need it
    try:
        tokenized_name.remove('log')
    except ValueError:
        print('DEBUG: tokenized_name doesn\'t contain log keyword')
        return err_list
    
    # ['mpi', '6', '100']
    csv_filename = '{0}.{1}.{2}.csv'.format(tokenized_name[0], tokenized_name[1], tokenized_name[2])
    # return the csv filename to write later on
    return [True, csv_filename]

def log_file_to_dataframe(log_content):
    # Init an empty defaultdict
    measurements = defaultdict(dict)
    # keep track of the number of measurements in the log file
    measurement_counter = 1
    for line in log_content:
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
    return df

filename = argv[1] if len(argv) > 1 else None
print('Your filename is:',filename)
csv_filename = ''
if filename is None:
    print('Usage: python parser.py [log_file_to_parse.log]')
    exit()
else:
    check_name_list = sanitize_filename(filename)
    if check_name_list[0] == False:
        print('Are you sure you\'re using the correct log file? Try again.')
        exit()
    else:
        print('Parsing \'{0}\'...'.format(filename))
        csv_filename = check_name_list[1]
        
print('CSV filename will be:', csv_filename)
log_content = ''
with open(filename) as f:
    log_content = f.readlines()

# stip newline char
log_content = [x.strip('\n') for x in log_content]
# filter out empty strings
log_content = list(filter(None, log_content))

df = log_file_to_dataframe(log_content)
# convert this df to a csv file
df.to_csv(csv_filename, encoding='utf-8-sig')