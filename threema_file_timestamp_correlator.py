"""reads a message file line by line and renames found files to the timestamp of the message"""
import argparse
import os.path
import shutil
import sys
from datetime import datetime


def get_substring_between(line, left_char, right_char):
    """looks for chars in a given line and returns the substring between them"""
    start_index = line.find(left_char) + 1  # omit found char
    end_index = line.find(right_char)
    return line[start_index:end_index]


def line_has_chars(line, left_char, right_char):
    """looks if chars in a given line exist"""
    left_index = line.find(left_char)
    right_index = line.find(right_char)
    return left_index > 0 and right_index > 0


def handle_filename_collision(
        file_collision_counter, copy_to, files_output_location, date_converted, file_extension):
    """\
        gets a counter for the given date_converted
        and appends it to the filename (before the extension)
    """
    print(copy_to + " already exists")
    counter = file_collision_counter.get(date_converted)
    if counter is None:
        counter = 1
    else:
        counter += 1
    file_collision_counter[date_converted] = counter
    new_copy_to = files_output_location + date_converted + '-' + str(counter) + file_extension
    print("new filename => " + new_copy_to)
    return new_copy_to


def main():
    """reads a message file line by line and renames found files to the timestamp of the message"""
    parser = argparse.ArgumentParser(description=
                                     'Rename files from a threema backup to the '
                                     'timestamp of the message that references them.')
    parser.add_argument('--root_path', help='root path', required=True)
    args = parser.parse_args()

    root_path = args.rootPath
    if not str(root_path).endswith('/'):
        root_path = root_path + '/'
    if not os.path.exists(root_path):
        print(root_path + ' not found')
        sys.exit(-1)
    print("root_path is " + root_path)

    message_file = root_path + 'messages.txt'
    files_location = root_path + 'files/'
    files_output_location = root_path + 'filesOut/'
    file_collision_counter = {}

    with open(message_file, encoding="utf8", errors="surrogateescape") as file:
        for line in file:
            if line_has_chars(line, '<', '>'):  # print only lines with a file
                date_base_string = get_substring_between(line, '[', ']')
                date_converted = datetime.strptime(date_base_string, '%d/%m/%Y, %H:%M')\
                    .strftime('%Y-%m-%dT%H%M')

                file_base_string = get_substring_between(line, '<', '>')
                file_extension = os.path.splitext(file_base_string)[1]

                # debug output
                print('the line has a file reference: ' + line)
                print('date converted from [' + date_base_string + '] to ' + date_converted)
                print('file found ' + file_base_string + ' (extension is [' + file_extension + '])')

                copy_from = files_location + file_base_string
                copy_to = files_output_location + date_converted + file_extension

                if os.path.isfile(copy_from):
                    if os.path.isfile(copy_to):  # dest exists - find a new filename
                        copy_to = handle_filename_collision(
                            file_collision_counter, copy_to,
                            files_output_location, date_converted, file_extension)
                    print('copying ' + copy_from + " => " + copy_to)
                    shutil.copy(copy_from, copy_to)
                print('\n')


if __name__ == '__main__':
    main()
