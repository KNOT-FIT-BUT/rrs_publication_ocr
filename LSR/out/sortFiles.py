#!/usr/bin/python

import sys
import re
import os
import codecs

""" MAIN """
def main():
    #Zde si dej cestu, odkud to budes brat
    path = "./"
    files = os.listdir(path)
    
    fileList = {}
    #pocitadlo souboru v slozce
    itemCnt = len(files)
    cnt = 1
    for item in files:
        sys.stderr.write(str(cnt) + "/" + str(itemCnt) + ": Zpracovavam " + item + "\n")
        item_out = re.sub(r"(\.\w+)*$", "", item)
        if not fileList.has_key(item_out):
            fileList[item_out] = 1
        else:
            fileList[item_out] += 1
        cnt += 1
    
    #vypis seznamu
    for item in fileList:
        print item + ": " + str(fileList[item])

main()
