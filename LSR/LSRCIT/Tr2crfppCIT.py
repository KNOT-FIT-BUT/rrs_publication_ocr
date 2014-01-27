import re
import codecs
import sys
import os

tmpDir = "tmp"
crf_test = "./LSRLabel/Resources/crf_test"
dictFile = "./LSRLabel/Resources/parsCitDict.txt"
modelFile = "./LSRLabel/Resources/parsCit/parsCit.model"
splitModelFile = "./LSRLabel/Resources/parsCit/parsCit.split.model"

dict = {}

obj_list = {
                "OMNIDOC":"document", 
                "OMNIPAGE":"page", 
                "OMNICOL":"column", 
                "OMNIDD":"dd", 
                "OMNITABLE":"table", 
                "OMNIIMG":"image", 
                "OMNIPARA":"paragraph", 
                "OMNILINE":"line", 
                "OMNIRUN":"run", 
                "OMNIWORD":"word", 
                "OMNIFRAME":"frame"}

def ReadDict(dictFileLoc):
    #debug docasne
    debug = 1
    mode = 0
     #otevreni slovniku
    dictFileLoc_fd = ""
    try:
        dictFileLoc_fd = codecs.open(dictFileLoc, 'r', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + dictFileLoc)
        sys.exit(1)
    
    tmpWhileBuf = dictFileLoc_fd.readline()
    while(tmpWhileBuf):
        if re.match(r"\#\# Male", tmpWhileBuf) != None:
            mode = 1
        elif re.match(r"\#\# Female", tmpWhileBuf) != None:
            mode = 2
        elif re.match(r"\#\# Last", tmpWhileBuf) != None:
            mode = 4
        elif re.match(r"\#\# Chinese", tmpWhileBuf) != None:
            mode = 4
        elif re.match(r"\#\# Months", tmpWhileBuf) != None:
            mode = 8
        elif re.match(r"\#\# Place", tmpWhileBuf) != None:
            mode = 16
        elif re.match(r"\#\# Publisher", tmpWhileBuf) != None:
            mode = 32
        elif re.match(r"\#", tmpWhileBuf) != None:
            tmpWhileBuf = dictFileLoc_fd.readline()
            continue
        else:
            key = tmpWhileBuf
            val = 0
            
            #pokud klic obsahuje i hodnotu pravdepodobnosti vyskytu
            if re.search(r"\t", key) != None:
                val = key
                key = re.sub(r"\t.*$", "", key, 1)
                val = re.sub(r"^.*\t", "", val, 1)
            
            if re.search(r"\n", key) != None:
                key = re.sub(r"\n", "", key, 1)
            if val and re.search(r"\n", val) != None:
                val = re.sub(r"\n", "", val, 1)
            
            #Jiz oznacene (nektere vstupy se mohou objevit ve stejne casti slovniku vice jak jednou)
            if not dict.has_key(key):
                dict[key] = mode
            else:
                if dict.has_key(key) and dict[key] >= mode:
                    tmpWhileBuf = dictFileLoc_fd.readline()
                    continue
                #zatim neoznacene
                else:
                    if dict.has_key(key):
                        dict[key] +=mode
        
        tmpWhileBuf = dictFileLoc_fd.readline()
    #uzavreni souboru
    #if debug:
        #print "Dictionary done!!!"
    dictFileLoc_fd.close()

def PrepData(rcite_text, filename):
    #toto pak zmenit!!!!
    tmpfile = "/tmp/"+"prepDataCIT"
    
    ReadDict(dictFile)
    
    tmpfile_fd = ""
    try:
        tmpfile_fd = codecs.open(tmpfile, 'w', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + tmpfile)
        sys.exit(1)
    
    for item in rcite_text.split("\n"):
        #print item.encode("utf-8")
        if re.search(r"^\s*$", item) != None:
            continue
        
        tag = ""
        tokens = re.split(" +", item)
        #print tokens
        feats = []
        tmpFeats = []
        hasPossibleEditor = "possibleEditors" if re.search(r"ed\.|editor|editors|eds\.",  item) != None else "noEditors"
        j = 0
        #feats[j].append([])
        #feats.append([])
        for i in range(0, len(tokens)):
            if re.search(r"^\s*$", tokens[i]) != None:
                continue
            if re.search(r"^\<\/([a-zA-Z]+)", tokens[i]) != None:
                continue
            if re.search(r"^\<([a-zA-Z]+)", tokens[i]) != None:
                tmpStr = re.search(r"^\<([a-z]+)", tokens[i])
                tag = tmpStr.group(1)
                continue
        
            #prep
            word = tokens[i]
            #no punctation
            wordNP = tokens[i]
            wordNP = re.sub(r"[^\w]", "", wordNP)
            if re.search(r"^\s*$", wordNP) != None:
                wordNP = "EMPTY"
            #lowercased    
            wordLCNP = wordNP.lower()
            if re.search(r"^\s*$", wordLCNP) != None:
                wordLCNP = "EMPTY"
            
            # feature generation
            # 0 = lexical word
            tmpFeats.append(word)
            chars = list(word)
            chars_len = len(chars)
            lastChar = chars[-1]
            if re.search(r"[a-z]", lastChar) != None:
                lastChar = 'a'
            elif re.search(r"[A-Z]", lastChar) != None:
                lastChar = 'A'
            elif re.search(r"[0-9]", lastChar) != None:
                lastChar= '0'
            
            #1 = last char
            tmpFeats.append(lastChar)
            
            #2 = first char
            tmpFeats.append(chars[0])
            #3 = first 2 chars
            if chars_len >= 2:
                tmpFeats.append(chars[0]+chars[1])
            else:
                tmpFeats.append(chars[0])
            
            #4 = first 3 chars
            if chars_len >= 3:
                tmpFeats.append(chars[0]+chars[1]+chars[2])
            elif chars_len >= 2:
                tmpFeats.append(chars[0]+chars[1])
            else:
                tmpFeats.append(chars[0])
                
            #5 = first 4 chars
            if chars_len >= 4:
                tmpFeats.append(chars[0]+chars[1]+chars[2]+chars[3])
            elif chars_len >= 3:
                tmpFeats.append(chars[0]+chars[1]+chars[2])
            elif chars_len >= 2:
                tmpFeats.append(chars[0]+chars[1])
            else:
                tmpFeats.append(chars[0])
                
            #6 = last char
            tmpFeats.append(chars[-1])
            
            #7 = last 2 chars
            if chars_len >= 2:
                tmpFeats.append(chars[-2]+chars[-1])
            else:
                tmpFeats.append(chars[-1])
                
            #8 = last 3 chars
            if chars_len >= 3:
                tmpFeats.append(chars[-3]+chars[-2]+chars[-1])
            elif chars_len >= 2:
                tmpFeats.append(chars[-2]+chars[-1])
            else:
                tmpFeats.append(chars[-1])
            
            #9 = last 4 chars
            if chars_len >= 4:
                tmpFeats.append(chars[-4]+chars[-3]+chars[-2]+chars[-1])
            elif chars_len >= 3:
                tmpFeats.append(chars[-3]+chars[-2]+chars[-1])
            elif chars_len >= 2:
                tmpFeats.append(chars[-2]+chars[-1])
            else:
                tmpFeats.append(chars[-1])
            
            #10 = lowercased word, no punct
            tmpFeats.append(wordLCNP)
            
            #11 = capitalization
            ortho = ""
            if re.search(r"^[A-Z]$", wordNP) != None:
                ortho = "singleCap"
            elif re.search(r"^[A-Z][a-z]+", wordNP) != None:
                ortho = "InitCap"
            elif re.search(r"^[A-Z]+$", wordNP) != None:
                ortho = "AllCap"
            else:
                ortho = "others"
            tmpFeats.append(ortho)
            
            #12 = numbers
            num = ""
            if re.match(r"(19|20)[0-9][0-9]$", wordNP) != None:
                num = "year"
            elif re.search(r"[0-9]-[0-9]", word) !=None:
                num = "possiblePage"
            elif re.search(r"[0-9]\([0-9]+\)", word) != None:
                num = "possibleVol"
            elif re.match(r"[0-9]$", wordNP) != None:
                num = "1dig" 
            elif re.match(r"[0-9][0-9]$", wordNP) != None:
                num = "2dig"
            elif re.match(r"[0-9][0-9][0-9]$", wordNP) != None:
                num = "3dig"
            elif re.match(r"[0-9]+$", wordNP) != None:
                num = "4+dig"
            elif re.match(r"[0-9]+(th|st|nd|rd)$", wordNP) != None:
                num = "ordinal"
            elif re.search(r"[0-9]", wordNP) != None:
                num = "hasDig"
            else:
                num = "nonNum"
            tmpFeats.append(num)
            
            #names
            dictStatus = dict[wordLCNP] if dict.has_key(wordLCNP) else 0
            
            isInDict = dictStatus
            
            publisherName = ""
            placeName = ""
            monthName = ""
            lastName = ""
            femaleName = ""
            maleName = ""
            
            if dictStatus >= 32:
                dictStatus -= 32
                publisherName = "publisherName"
            else:
                publisherName = "no"
            
            if dictStatus >= 16:
                dictStatus -= 16
                placeName = "placeName"
            else:
                placeName = "no"
            
            if dictStatus >= 8:
                dictStatus -= 8
                monthName = "monthName"
            else:
                monthName = "no"
            
            if dictStatus >=4:
                dictStatus -= 4
                lastName = "lastName"
            else:
                lastName = "no"
            
            if dictStatus >= 2:
                dictStatus -= 2
                femaleName = "femaleName"
            else:
                femaleName = "no"
            
            if dictStatus >= 1:
                dictStatus -= 1
                maleName = "maleName"
            else:
                maleName = "no"
            
            #13 = name status
            tmpFeats.append(isInDict)
            #14 = male name
            tmpFeats.append(maleName)
            #15 = female name
            tmpFeats.append(femaleName)
            #16 = last name
            tmpFeats.append(lastName)
            #17 = month name
            tmpFeats.append(monthName)
            #18 = place name
            tmpFeats.append(placeName)
            #19 = publisher name
            tmpFeats.append(publisherName)
            
            #20 = possible editor
            tmpFeats.append(hasPossibleEditor)
            
            #not accurate (len(tokens counts tags too)
            if tokens == []:
                continue
                
            location = int(float(j)/float((len(tokens)-1))*12.0)
            #print "VYPOCET!!!!"
            #print j
            #print str(len(tokens)-1)
            #print location
            
            #21 = relative location
            tmpFeats.append(location)
            
            #22 = punctation
            punct = ""
            if re.match(r"[\"\'\`]", word) != None:
                punct = "leadQuote"
            elif re.search(r"[\"\'\`][^s]?$", word) != None:
                punct = "endQuote"
            elif re.search(r"-.*-", word)  != None:
                punct = "multiHyphen"
            elif re.search(r"[-\,\:\;]$",  word) != None:
                punct = "contPunct"
            elif re.search(r"[\!\?\.\"\']$",  word) != None:
                punct = "stopPunct"
            elif re.search(r"^[\(\[\{\<].+[\)\]\}\>].?$",  word) != None:
                punct = "braces"
            elif re.search(r"^[0-9]{2-5}\([0-9]{2-5}\).?$",  word) != None:
                punct = "possibleVol"
            else:
                punct = "others"
            tmpFeats.append(punct)
            
            #output tag
            tmpFeats.append(tag)
            feats.append(tmpFeats)
            tmpFeats = []
            j += 1
        
        #export output; print
        #print feats
        #for index in range(len(feats)):
        #    for splitIndex in range(len(feats[index])):
        #        if type(feats[splitIndex]) == type(unicode()):
        #            tmpfile_fd.write(feats[splitIndex]+" ")
        #        elif type(feats[splitIndex]) == type(str()):
        #            tmpfile_fd.write(feats[splitIndex].encode("utf-8")+" ")
        #        else:
        #            tmpfile_fd.write(str(feats[splitIndex])+" ")
            #tmpfile_fd.write(" ".join(feats[j]))
        #    tmpfile_fd.write("\n")
        #tmpfile_fd.write("\n")
        for index in range(len(feats)):
            for splitIndex in range(len(feats[index])):
                if type(feats[index][splitIndex]) == type(unicode()):
                    tmpfile_fd.write(feats[index][splitIndex]+" ")
                elif type(feats[index][splitIndex]) == type(str()):
                    tmpfile_fd.write(feats[index][splitIndex].encode("utf-8")+" ")
                else:
                    tmpfile_fd.write(str(feats[index][splitIndex])+" ")
            #tmpfile_fd.write(" ".join(feats[j]))
            tmpfile_fd.write("\n")
        tmpfile_fd.write("\n")
        
    tmpfile_fd.close()
    
    return tmpfile

def Decode(inFile, outFile):
    os.system(crf_test + " -m " + modelFile + " " + inFile + "> /tmp/crfHed")
    crfHed = "/tmp/crfHed"
    crfHed_fd = ""
    try:
        crfHed_fd = codecs.open(crfHed, 'r', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + crfHed)
        sys.exit(1)
        
    output = crfHed_fd.read()
    crfHed_fd.close()
    #print output.encode("utf-8")
    
    inFile_fd = ""
    try:
        inFile_fd = codecs.open(inFile, 'r', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + inFile)
        sys.exit(1)
    
    codeLines = []
    tmp = inFile_fd.readline()
    while tmp:
        codeLines.append(tmp)
        tmp = inFile_fd.readline()
    
    inFile_fd.close()
    
    outputLines = re.split("\n", output)
    for i in range(0, len(outputLines)):
        #print (len(outputLines)-1)
        if re.search(r"^\s*$", outputLines[i]) != None:
            continue
    
        outputTokens = re.split("\s+", outputLines[i])
        #print outputTokens
        #print len(outputTokens)
        #tady pozor, mozna to bude o 1 nekde jinde
        class_prom = outputTokens[len(outputTokens)-1]
        #print class_prom
        codeTokens = re.split("\s+", codeLines[i])
        #print codeTokens
        if codeTokens == []:
            continue
        codeTokens[-2] = class_prom
        #print codeTokens
        codeLines[i] = "\t".join(codeTokens)
        
    outFile_fd = ""
    try:
        outFile_fd = codecs.open(outFile, 'w', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + outFile)
        sys.exit(1)
    
    for line in codeLines:
        if re.search(r"^\s*$", line) != None:
            outFile_fd.write("\n")
        else:
            outFile_fd.write(line+"\n")
        
    outFile_fd.close()
    return 1
