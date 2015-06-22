import sys, os, re
from fileNameCleaner import clean as cleanString
from common import *
import string
from trie import Trie
fsTrie = Trie('')
def splitTrackNumber2(path):
    """
    splits into prefix_data, trackNumber, trackName
    extra points for
    tno[.-_]
    tno <letter>
    len(tno) == 2 and < 15
    <num>tno
    """
    path = path.strip()
    votes = [0]*len(path)
    for idx in range(len(path)):
        if (idx == 0 or path[idx-1] in (' ', '-', '_', '.')) and path[idx] in string.digits:
            prev, next = path[:idx].strip(), path[idx:]
            matchGroup = re.match(r'^(\d{1,3})[ \-_.]+[^(\[ \-_.]', next)
            if matchGroup == None:
                continue
            votes[idx] += 1 # a track number exists
            trackNumber = matchGroup.group(1)
            if re.match(r'^\d{1,3} *[\-_.]', next) != None:
                votes[idx] += 1 # less likely to be part of the track name
            if re.match(r'^\d{1,3} *[\-_.]? *[^0-9]', next) != None:
                votes[idx] += 0.25 # a letter next to track number is more probable
            if len(trackNumber) == 2:
                votes[idx] += 1
                if 1 <= int(trackNumber) < 15:
                    votes[idx] += 0.25
                if 1 <= int(trackNumber) < 10:
                    votes[idx] += 1
            elif len(trackNumber) == 1:
                votes[idx] += 0.25
    result = [(score, idx) for idx, score in enumerate(votes)]
    result.sort()
    res = result[-1]
    if res[0] >= 1:
        pre, suff = path[:res[1]].strip(), path[res[1]:]
        matchGroup = re.match(r'^(\d{1,3}) *[\-_.]? *(.*)$', suff)
        prefixData = pre
        trackNumber = matchGroup.group(1)
        trackName = matchGroup.group(2)
    else:
        trackName = path
        prefixData = trackNumber = None
    
    return {
            'trackNumber': trackNumber,
            'prefixData': prefixData,
            'trackName': trackName
            }

def analyseFileName(fileName):
    res = splitTrackNumber2(fileName)
    return res['trackNumber'], None, res['trackName']

def guessMusicDetails(path):
    path = os.path.split(path)
    dirStructure, fileName = path[:-1], path[-1]
    dirStructure = apply(cleanString, dirStructure)
    originalFileName = fileName
    fileName, ext = os.path.splitext(fileName)
    fileName = cleanString(fileName, subSpace=[])
    trackNumber, trackNumberSeparator, trackName = analyseFileName(fileName)
    if trackName == '':
        trackNumber, trackNumberSeparator, trackName = analyseFileName(originalFileName)
    trackName = re.sub('_', ' ', trackName)
    trackName = trackName.decode('utf-8')
    return trackNumber, trackNumberSeparator, trackName.strip()

def isMusicFile(fname):
    return os.path.splitext(fname)[1] in ('.mp3',)

def analyzePath(path, trieNode):
    """
    based on path analysis returns a dict containing keys 'artist', 'album', 'disc'
    Rules
        - Artist comes before Album
        - Discard all parts before "music" folder
        - 
    """
    fsTrieNode = fsTrie.query(path)
    pass

def getCommonPrefix(fileSet, trieNode, separator='-_'):
    debug = False
    # debug = ('killswitch engage - temple from the within.mp3' in fileSet)
    root = Trie('$$')
    for f in fileSet:
        root.insert(list(trieNode.children[f].key))
    prefixList = []
    def dfs(trieNode, curStr=''):
        if debug:
            print curStr, trieNode.num_successors, int(0.8*len(fileSet))
        if (trieNode.num_successors >= int(0.8*len(fileSet)) and trieNode.num_successors > 1) or trieNode.num_successors >= 3:
            res = False
            for k in trieNode.children:
                res = (dfs(trieNode.children[k], curStr+k) or res)
            if res:
                return True
            elif trieNode.key in separator:
                prefixList.append((curStr, trieNode.num_successors))
                return True
            else:
                return False
        else:
            return False
    dfs(root)
    # if len(prefixList) > 0:
    #     print prefixList, "->\n", '\n\t'.join(fileSet)
    return prefixList

def preProcessFileSet(fileSet, path, trieNode):
    """
    fileSet is the list of music files with their extensions
    the function updates the path elements with role assignments based on the fileset
        - Common prefix information
        - Check immediate parent for disc categorization
        - check next immediate unassigned parent for album categorization
            - number of siblings and their album role score
            - parent's artist role score
    """
    def cleanMusicFile(f):
        return os.path.splitext(f)[0].lower().strip()
    for f in fileSet:
        trieNode.children[f].key = cleanMusicFile(f)
    commonPrefix = getCommonPrefix(fileSet, trieNode)
    for pre, cnt in commonPrefix:
        regex = re.compile(r'^'+re.escape(commonPrefix))
        def sub(s):
            return regex.sub('', s).strip()
        for f in fileSet.children:
            fileSet.children[f].key = sub(fileSet.children[f].key)

def traverseFsTrie(trie, curPath):
    """
    3 levels of categorization
        - artist level
        - album level
        - disc level
    """
    retList = []
    for k in trie.children:
        if isMusicFile(k):
            retList.append(trie.children[k].key)

    num_musicFiles = len(retList)
    num_directories = len(trie.children) - num_musicFiles

    for k in trie.children:
        if not isMusicFile(k):
            fileSet = traverseFsTrie(trie.children[k], curPath+(k,))

    if len(retList) > 0:
        preProcessFileSet(retList, curPath, trie)

    return None if len(retList) == 0 else retList

def splitPath(path):
    folders = []
    while True:
        path, file = os.path.split(path)
        if file != "":
            folders.append(file)
        else:
            if path != "" and path != '/':
                folders.append(path)
            break
    folders.reverse()
    return folders

if __name__ == '__main__':
    infile = open(sys.argv[1])
    for line in infile.read().splitlines():
        fsTrie.insert(splitPath(cleanString(line.lower().strip(), subSpace=[])))
    traverseFsTrie(fsTrie, ())
