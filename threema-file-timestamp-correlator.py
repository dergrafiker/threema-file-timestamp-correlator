import argparse
import os.path
import shutil
from datetime import datetime


def getSubstringBetween(line, leftChar, rightChar):
    startIndex = line.find(leftChar) + 1  # omit found char
    endIndex = line.find(rightChar)
    return line[startIndex:endIndex]


def lineHasChars(line, leftChar, rightChar):
    leftIndex = line.find(leftChar)
    rightIndex = line.find(rightChar)
    return leftIndex > 0 and rightIndex > 0


def handleFileNameCollision(my_dict, copyTo, filesOutputLocation, dateConverted, fileExtension):
    print(copyTo + " already exists")
    counter = my_dict.get(dateConverted)
    if counter is None:
        counter = 1
    else:
        counter += 1
    my_dict[dateConverted] = counter
    newCopyTo = filesOutputLocation + dateConverted + '-' + str(counter) + fileExtension
    print("new filename => " + newCopyTo)
    return newCopyTo


parser = argparse.ArgumentParser(description='Rename files from a threema backup to the timestamp of the message that references them.')
parser.add_argument('--rootPath', help='root path', required=True)
args = parser.parse_args()

rootPath = args.rootPath
print("rootPath is " + rootPath)

messageFile = rootPath + '/messages.txt'
filesLocation = rootPath + '/files/'
filesOutputLocation = rootPath + '/filesOut/'
my_dict = {}

with open(messageFile) as f:
    for line in f:
        if lineHasChars(line, '<', '>'):  # print only lines with a file
            dateBaseString = getSubstringBetween(line, '[', ']')
            dateConverted = datetime.strptime(dateBaseString, '%d/%m/%Y, %H:%M').strftime('%Y-%m-%dT%H%M')

            fileBaseString = getSubstringBetween(line, '<', '>')
            fileExtension = os.path.splitext(fileBaseString)[1]

            # debug output
            print(dateBaseString + " => " + dateConverted)
            print(fileBaseString + " => " + fileExtension)
            print(line)

            copyFrom = filesLocation + fileBaseString
            copyTo = filesOutputLocation + dateConverted + fileExtension

            if os.path.isfile(copyFrom):
                print(copyFrom + " => " + copyTo)
                if os.path.isfile(copyTo):  # destination exists - find a new filename
                    copyTo = handleFileNameCollision(my_dict, copyTo, filesOutputLocation, dateConverted, fileExtension)
                shutil.copy(copyFrom, copyTo)
