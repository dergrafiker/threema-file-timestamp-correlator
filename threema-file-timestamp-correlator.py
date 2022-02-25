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


def handleFileNameCollision(fileCollisionCounter, copyTo, filesOutputLocation, dateConverted, fileExtension):
    print(copyTo + " already exists")
    counter = fileCollisionCounter.get(dateConverted)
    if counter is None:
        counter = 1
    else:
        counter += 1
    fileCollisionCounter[dateConverted] = counter
    newCopyTo = filesOutputLocation + dateConverted + '-' + str(counter) + fileExtension
    print("new filename => " + newCopyTo)
    return newCopyTo


parser = argparse.ArgumentParser(description='Rename files from a threema backup to the timestamp of the message that references them.')
parser.add_argument('--rootPath', help='root path', required=True)
args = parser.parse_args()

rootPath = args.rootPath
if not str(rootPath).endswith('/'):
    rootPath = rootPath + '/'
if not os.path.exists(rootPath):
    print(rootPath + ' not found')
    exit(-1)
print("rootPath is " + rootPath)

messageFile = rootPath + 'messages.txt'
filesLocation = rootPath + 'files/'
filesOutputLocation = rootPath + 'filesOut/'
fileCollisionCounter = {}

with open(messageFile) as f:
    for line in f:
        if lineHasChars(line, '<', '>'):  # print only lines with a file
            dateBaseString = getSubstringBetween(line, '[', ']')
            dateConverted = datetime.strptime(dateBaseString, '%d/%m/%Y, %H:%M').strftime('%Y-%m-%dT%H%M')

            fileBaseString = getSubstringBetween(line, '<', '>')
            fileExtension = os.path.splitext(fileBaseString)[1]

            # debug output
            print('the line has a file reference: ' + line)
            print('date converted from [' + dateBaseString + '] to ' + dateConverted)
            print('file found ' + fileBaseString + ' (extension is [' + fileExtension + '])')

            copyFrom = filesLocation + fileBaseString
            copyTo = filesOutputLocation + dateConverted + fileExtension

            if os.path.isfile(copyFrom):
                if os.path.isfile(copyTo):  # destination exists - find a new filename
                    copyTo = handleFileNameCollision(fileCollisionCounter, copyTo, filesOutputLocation, dateConverted, fileExtension)
                print('copying ' + copyFrom + " => " + copyTo)
                shutil.copy(copyFrom, copyTo)
            print('\n')
