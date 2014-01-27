import re
import codecs

tmpDir = "tmp"
crf_test = "./LSRLabel/Resources/crf_test"
dictFile = "./LSRLabel/Resources/parsCitDict.txt"
modelFile = "./LSRLabel/Resources/parsHed/parsHed.090316.model"

dict = {}

def readDict(dictFileLoc):
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
    if debug:
        print "Dictionary done!!!"
    dictFileLoc_fd.close()

def prepData(rCiteText, filename):
    
    tmpfile = "/tmp/"+filename
    
    #move inside the method; only load when running
    readDict(dictFile)
    tmpfile_fd = ""
    try:
        tmpfile_fd = codecs.open(tmpfile, 'w', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + tmpfile)
        sys.exit(1)
        
    rCiteTextSplit = rCiteText.split("\n")
    for index in range(len(rCiteTextSplit)):
        if re.match(r"\s*$", rCiteTextSplit[index]) != None:
            continue
        
        tag = ""
        tokens = rCiteTextSplit[index].split(" +")
        feats = []
        hasPossibleEditor = "possibleEditors" if re.search(r"ed\.|editor|editors|eds\.",  rCiteTextSplit[index]) != None else "noEditors"
        j = 0
        for i in range(0, len(tokens)+1):
            if re.search(r"^\s*$", tokens[i]) != None:
                continue
            if re.search(r"^\<\/([\p{IsLower}]+)", tokens[i]) != None:
                continue
            if re.search(r"^\<([\p{IsLower}]+)", tokens[i]) != None:
                tmpStr = re.search(r"^\<([\p{IsLower}]+)", tokens[i])
                tag = tmpStr.group(0)
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
            feats[j][0] = word
            chars = word.split("")
            lastChar = chars[-1]
            if re.search(r"[\p{IsLower}]", lastChar) != None:
                lastChar = 'a'
            elif re.search(r"[\p{IsUpper}]", lastChar) != None:
                lastChar = 'A'
            elif re.search(r"[0-9]", lastChar) != None:
                lastChar= '0'
            
            #1 = last char
            feats[j].append(lastChar)
            
            #2 = first char
            feats[j].append(chars[0])
            #3 = first 2 chars
            feats[j].append(chars[0]+chars[1])
            #4 = first 3 chars
            feats[j].append(chars[0]+chars[1]+chars[2])
            #5 = first 4 chars
            feats[j].append(chars[0]+chars[1]+chars[2]+chars[3])
            
            #6 = last char
            feats[j].append(chars[-1])
            #7 = last 2 chars
            feats[j].append(chars[-2]+chars[-1])
            #8 = last 3 chars
            feats[j].append(chars[-3]+chars[-2]+chars[-1])
            #9 = last 4 chars
            feats[j].append(chars[-4]+chars[-3]+chars[-2]+chars[-1])
            
            #10 = lowercased word, no punct
            feats[j].append(wordLCNP)
            
            #11 = capitalization
            ortho = ""
            if re.search(r"^[\p{IsUpper}]$", wordNP) != None:
                ortho = "singleCap"
            elif re.search(r"^[\p{IsUpper}][\p{IsLower}]+", wordNP) != None:
                ortho = "InitCap"
            elif re.search(r"^[\p{IsUpper}]+$", wordNP) != None:
                ortho = "AllCap"
            else:
                ortho = "others"
            feats[j].append(ortho)
            
            #12 = numbers
            num = ""
            if re.match(r"(19|20)[0-9][0-9]$", word_np) != None:
                num = "year"
            elif re.search(r"[0-9]\-[0-9]", word) !=None:
                num = "possiblePage"
            elif re.search(r"[0-9]\([0-9]+\)", word) != None:
                num = "possibleVol"
            elif re.match(r"[0-9]$", word_np) != None:
                num = "1dig" 
            elif re.match(r"[0-9][0-9]$", word_np) != None:
                num = "2dig"
            elif re.match(r"[0-9][0-9][0-9]$", word_np) != None:
                num = "3dig"
            elif re.match(r"[0-9]+$", word_np) != None:
                num = "4+dig"
            elif re.match(r"[0-9]+(th|st|nd|rd)$", word_np) != None:
                num = "ordinal"
            elif re.search(r"[0-9]", word_np) != None:
                num = "hasDig"
            else:
                num = "nonNum"
            feats[j].append(num)
            
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
            feats[j].append(isInDict)
            #14 = male name
            feats[j].append(maleName)
            #15 = female name
            feats[j].append(femaleName)
            #16 = last name
            feats[j].append(lastName)
            #17 = month name
            feats[j].append(monthName)
            #18 = place name
            feats[j].append(placeName)
            #19 = publisher name
            feats[j].append(publisherName)
            
            #20 = possible editor
            feats[j].append(hasPossibleEditor)
            
            #not accurate (len(tokens counts tags too)
            if len(tokens) <= 0:
                continue
                
            location = int(j/len(tokens)*12)
            #21 = relative location
            feats[j].append(location)
            
            #22 = punctation
            punct = ""
            if re.match(r"[\"\'\`]", word) != None:
                punct = "leadQuote"
            elif re.search(r"[\"\'\`][^s]?$", word) != None:
                punct = "endQuote"
            elif re.search(r"\-.*\-", word)  != None:
                punct = "multiHyphen"
            elif re.search(r"[\-\,\:\;]$",  word) != None:
                punct = "contPunct"
            elif re.search(r"[\!\?\.\"\']$",  word) != None:
                punct = "stopPunct"
            elif re.search(r"^[\(\[\{\<].+[\)\]\}\>].?$",  word) != None:
                punct = "braces"
            elif re.search(r"^[0-9]{2-5}\([0-9]{2-5}\).?$",  word) != None:
                punct = "possibleVol"
            else:
                punct = "others"
            feats[j].append(punct)
            
            #output tag
            feats[j].append(tag)
            
            j += 1
        
        #export output; print
        for j in range(0, len(feats)+1):
            tmpfile_fd.write(" ".join(feats[j]))
            tmpfile_fd.write("\n")
        tmpfile_fd.write("\n")
        
    tmpfile_fd.close()
    
    return tmpfile
    
def decode(inFile, outFile):
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
    
    outputLines = output.split("\n")
    for i in range(0, len(outputLines)+1):
        if re.search(r"^\s*$", outputLines[i]) != None:
            continue
    
        outputTokens = outputLines[i].split("\s+")
        #tady pozor, mozna to bude o 1 nekde jinde
        class_prom = outputTokens[len(outputLines[i])]
        codeTokens = codeLines[i].split("\s+")
        if len(codeTokens < 0):
            continue
        codeTokens[len(codeTokens)] = class_prom
        codeLines[i] = "\t".join(codeTokens)
        
    outFile_fd = ""
    try:
        outFile_fd = codecs.open(outFile, 'w', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + outFile)
        sys.exit(1)
    
    for index in range(len(codeLines)):
        outFile_fd.write(line+"\n")
        
    outFile_fd.close()
    return 1
