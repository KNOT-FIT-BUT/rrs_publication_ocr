#!/usr/bin/python

import sys
import re
import os
import codecs

""" MAIN """
def main():
    
    path = "/mnt/minerva1/nlp-in/athena3/rrs/reresearch.ocr/"
    #path = "./test_fld/"
    files = os.listdir(path)
    files = sorted(files)
    
    #print files
    #sys.exit(0)
    
    #otevreni, precteni a uzavreni souboru
    try:
        file = open("classPassed.dat", "rt")
    except IOError:
        sys.stderr.write("Chyba pri otevirani souboru\n")
        sys.exit(2)
    
    #nacteni dat ze souboru
    try:
        filedata = file.read()
        #print filedata
        file.close()
    except UnicodeDecodeError:
        sys.stderr.write("Chyba: Nelze nacist vstupni soubor\n")
        sys.exit(255)
    
    #ziskani informace o posledni klasifikovane slozce
    fileList = re.split(r"\n", filedata)
    
    #poznaceni slozky
    fld = fileList[0]
    
    #poznaceni podslozky
    subFld = fileList[1]
    
    subPath = ""
    prefOut = "./outClass/"
    for item in files:
        #print "ITEM"
        #print item
        if item >= fld and os.path.isdir(path + item):
            #print "Slozka nalezena"
            #sys.exit(0)
            subPath = path + item + "/"
            subFiles = os.listdir(subPath)
            subFiles = sorted(subFiles)
            
            if not os.path.exists(prefOut + item):
                os.makedirs(prefOut + item)
            
            #sys.exit(0)
            
            #otevreni, logovaciho souboru souboru
            try:
                fileLog = open("outClass.log", "a+")
            except IOError:
                sys.stderr.write("Chyba pri otevirani souboru\n")
                sys.exit(2)
            
            #nacteni dat ze souboru
            try:
                fileLogData = fileLog.write(item + "\n")
                #print filedata
                fileLog.close()
            except UnicodeDecodeError:
                sys.stderr.write("Chyba: Nelze ulozit vstupni soubor\n")
                sys.exit(255)
            
            for itemSub in subFiles:
                if itemSub >= subFld and os.path.isdir(subPath + itemSub):
                    finalPath = subPath + itemSub + "/"
                    finalFiles = os.listdir(finalPath)
                    
                    if not os.path.exists(prefOut + item + "/" + itemSub):
                        os.makedirs(prefOut + item + "/" + itemSub)
                    
                    #print finalFiles
                    
                    #otevreni, logovaciho souboru souboru
                    try:
                        fileLog = open("outClass.log", "a+")
                    except IOError:
                        sys.stderr.write("Chyba pri otevirani souboru\n")
                        sys.exit(2)
                    
                    #nacteni dat ze souboru
                    try:
                        fileLogData = fileLog.write(itemSub + "\n")
                        #print filedata
                        fileLog.close()
                    except UnicodeDecodeError:
                        sys.stderr.write("Chyba: Nelze ulozit vstupni soubor\n")
                        sys.exit(255)
                    
                    #otevreni, precteni a uzavreni souboru
                    try:
                        file = open("classPassed.dat", "wt")
                    except IOError:
                        sys.stderr.write("Chyba pri otevirani souboru\n")
                        sys.exit(2)
                    
                    #nacteni dat ze souboru
                    try:
                        filedata = file.write(item + "\n" + itemSub)
                        #print filedata
                        file.close()
                    except UnicodeDecodeError:
                        sys.stderr.write("Chyba: Nelze ulozit vstupni soubor\n")
                        sys.exit(255)
                    
                    for itemFinal in finalFiles:
                        sys.stderr.write("Zpracovavam " + itemFinal + "\n")
                        item_out = re.sub(r"\w+$", "out.xml", itemFinal)
                        
                        cmd = "./lsr.py --input " + finalPath + itemFinal + " -m extract_nocit -i rtf > " + prefOut + item + "/" + itemSub + "/" + item_out
                        result = os.system(cmd)
                        
                        #otevreni, logovaciho souboru souboru
                        try:
                            fileLog = open("outClass.log", "a+")
                        except IOError:
                            sys.stderr.write("Chyba pri otevirani souboru\n")
                            sys.exit(2)
                        
                        if result == 0:
                            #nacteni dat ze souboru
                            try:
                                fileLogData = fileLog.write(itemFinal + "\t\t" + "OK\n")
                                #print filedata
                                fileLog.close()
                            except UnicodeDecodeError:
                                sys.stderr.write("Chyba: Nelze ulozit vstupni soubor\n")
                                sys.exit(255)
                        else:
                            #nacteni dat ze souboru
                            try:
                                fileLogData = fileLog.write(itemFinal + "\t\t" + "ERR\n")
                                #print filedata
                                fileLog.close()
                            except UnicodeDecodeError:
                                sys.stderr.write("Chyba: Nelze ulozit vstupni soubor\n")
                                sys.exit(255)
                        
                        #print result
                    #sys.exit(0)
            

main()
