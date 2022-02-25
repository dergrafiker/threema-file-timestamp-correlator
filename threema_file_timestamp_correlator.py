"""reads a message file line by line and renames found files to the timestamp of the message"""
import argparse
import logging
import os.path
import shutil
from datetime import datetime
import time


def init_logging(log_level):
    """init logging"""
    local_logger = logging.getLogger('threema_file_timestamp_correlator')
    local_logger.setLevel(log_level)
    # create console handler and set level to debug
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to console_handler
    console_handler.setFormatter(formatter)
    # add console_handler to logger
    local_logger.addHandler(console_handler)
    return local_logger


def get_substring_between(line, left_char, right_char):
    """looks for chars in a given line and returns the substring between them"""
    start_index = line.find(left_char) + 1  # omit found char
    end_index = line.find(right_char)
    return line[start_index:end_index]


def line_has_file(line):
    """looks if chars in a given line exist"""
    file_is_present = '<' in line and '>' in line
    if file_is_present:
        logger.info('the line has a file reference: %s', line)
    return file_is_present


def get_next_file_counter(date_converted):
    """lookup counter for given date_converted and increment it"""
    counter = file_collision_counter.get(date_converted)
    if counter is None:
        counter = 1
    else:
        counter += 1
    file_collision_counter[date_converted] = counter
    return counter


def prepare_and_check_root(args):
    """appends slash (when missing) at the end of the rootpath and """
    root_path = args.rootpath
    if not str(root_path).endswith('/'):
        root_path = root_path + '/'
    if not os.path.exists(root_path):
        raise IOError(root_path + ' not found')
    logger.info("root_path is %s", root_path)
    return root_path


def get_date_from(line):
    """extract date from line"""
    date_base_string = get_substring_between(line, '[', ']')
    date_converted = datetime.strptime(date_base_string, '%d/%m/%Y, %H:%M') \
        .strftime('%Y-%m-%dT%H%M')
    logger.debug('date converted from [%s] to %s', date_base_string, date_converted)
    return date_converted


def get_extension(file_base_string):
    """extract extension from file"""
    file_extension = os.path.splitext(file_base_string)[1]
    logger.debug('file found %s (extension is [%s])', file_base_string, file_extension)
    return file_extension


def main():
    """reads a message file line by line and renames found files to the timestamp of the message"""
    parser = argparse.ArgumentParser(description=
                                     'Rename files from a threema backup to the '
                                     'timestamp of the message that references them.')
    parser.add_argument('--rootpath', help='root path', required=True)
    args = parser.parse_args()

    root_path = prepare_and_check_root(args)

    message_file = root_path + 'messages.txt'
    files_location = root_path + 'files/'
    files_output_location = root_path + 'filesOut/'

    with open(message_file, encoding="utf8", errors="surrogateescape") as in_file:
        for line in in_file:
            if line_has_file(line):
                file_base_string = get_substring_between(line, '<', '>')
                copy_from = files_location + file_base_string

                if os.path.isfile(copy_from):
                    date_converted = get_date_from(line)
                    file_extension = get_extension(file_base_string)
                    copy_to = files_output_location + date_converted + file_extension

                    if os.path.isfile(copy_to):  # dest exists - find a new filename
                        logger.info("%s already exists", copy_to)
                        counter = \
                            get_next_file_counter(date_converted)
                        copy_to = files_output_location + date_converted \
                                  + '-' + str(counter) + file_extension
                        logger.info("new filename => %s", copy_to)
                    logger.info('copy %s => %s', copy_from, copy_to)
                    shutil.copy(copy_from, copy_to)


file_collision_counter = {}
logger = init_logging(logging.DEBUG)

if __name__ == '__main__':
    tic = time.perf_counter()
    main()
    toc = time.perf_counter()
    print(f"main finished in {toc - tic:0.4f} seconds")
