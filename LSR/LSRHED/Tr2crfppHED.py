import re
import codecs
import sys
import os

tmpDir = "tmp"
crf_test = "./crfpp/crf_test"
dictFile = "./LSRLabel/Resources/parsCitDict.txt"
keywordFile = "./LSRLabel/Resources/parsHed/keywords"
bigramFile = "./LSRLabel/Resources/parsHed/bigram"
modelFile = "./LSRLabel/Resources/parsHed/parsHed.model"

# Flags for different types of CRF features for line-level training
isFullFormToken = 1;
isFirstToken= 1;
isLastToken = 1;
isSecondToken	= 1;
isSecondLastToken = 1;
isBack1 = 1;
isForw1 = 1;
isKeyword	= 1;
isBigram = 0;

dict = {}
keywords = {}
bigrams = {}

#list of tags trained in parsHed
#those with value 0 do not have frequent keyword features
#tags = {
#            "abstract":1,
#            "address":1,  
#            "affiliation":1, 
#            "author":0, 
#            "date":0, 
#            "degree":1, 
#            "email":0, 
#            "intro":1, 
#            "keyword":1, 
#            "note":1, 
#            "page":1, 
#            "phone":0, 
#            "pubnum":1, 
#            "title":1, 
#            "web":0}

tags = {
            "keyword":1, 
            "page":1, 
            "degree":1, 
            "intro":1, 
            "date":0, 
            "author":0, 
            "phone":0, 
            "note":1, 
            "web":0, 
            "email":0,
            "pubnum":1, 
            "title":1, 
            "abstract":1, 
            "address":1, 
            "affiliation":1}

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
    #if debug:
        #print "Dictionary done!!!"
    dictFileLoc_fd.close()

def readKeywordDict(inFile, keywords):
    inFile_fd = ""
    try:
        inFile_fd = codecs.open(inFile, 'r', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + inFile)
        sys.exit(1)
    
    tmpWhileBuf = inFile_fd.readline()
    while(tmpWhileBuf):
        #print tmpWhileBuf
        if re.search(r"^(.+?): (.+)$", tmpWhileBuf) != None:
            #tmpStr = re.search(r"^(.+?): (.+)$", tmpWhileBuf)
            tmpStr = re.search(r"^(.+?):", tmpWhileBuf)
            tmpStr = tmpStr.group(0)
            tag = re.sub(r":", "", tmpStr)
            #tag = tmpStr.group(0)
            #tady to muze byt spatne, v perlu je misto mezery regular \s+,zkouska, zda to taky jde
            tmpStr = re.search(r": (.+)$", tmpWhileBuf)
            tmpStr = tmpStr.group(0)
            #print tmpStr
            tmpStr = re.sub(r":\s+", "", tmpStr)
            #print tmpStr
            tokens = tmpStr.split(" ")
            keywords[tag] = {}
            for index in range(len(tokens)):
                #print tag, "!!!"
                #print tokens[index]
                keywords[tag][tokens[index]] = 1
        tmpWhileBuf = inFile_fd.readline()
    inFile_fd.close()

def prepData(rCiteText, filename):
    tmpfile = "/tmp/prepData"
    
    readDict(dictFile)
    readKeywordDict(keywordFile, keywords)
    readKeywordDict(bigramFile, bigrams)
    
    tmpfile_fd = ""
    try:
        tmpfile_fd = codecs.open(tmpfile, 'w', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + tmpfile)
        sys.exit(1)
    
    #sys.stderr.write("TADY JESTE JO\n")
    #process input files
    rCiteTextSplit = rCiteText.split("\n")
    #print rCiteTextSplit
    for index in range(len(rCiteTextSplit)):
        if re.match(r"\#", rCiteTextSplit[index]) != None:
            continue
        elif re.match(r"\s*$", rCiteTextSplit[index]) != None:
            continue
        else:
            tag = "header"
            feats = []
            
            #generate CRF features
            #@returns feats
            crfFeature(rCiteTextSplit[index], tag, feats)
            for splitIndex in range(len(feats)):
                #print type(feats[splitIndex])
                if type(feats[splitIndex]) == type(unicode()):
                    tmpfile_fd.write(feats[splitIndex]+" ")
                elif type(feats[splitIndex]) == type(str()):
                    tmpfile_fd.write(feats[splitIndex].encode("utf-8")+" ")
                else:
                    tmpfile_fd.write(str(feats[splitIndex])+" ")
            #tmpfile_fd.write(" ".join(feats))
            tmpfile_fd.write("\n")
            
    tmpfile_fd.close()
    #in_fd.close()
    
    return tmpfile

def generateTokenFeature(token, feats):
    
    #prep
    word = token
    #word.replace(u"\ufb01", "fi")
    word = word
    wordNP = token
    
    #wordNP = re.sub(r"[^\w]", "", wordNP)
    #urezava znaky, ktere se tvari jako normalni znaky
    wordNP = re.sub(r"[^\w]", "", wordNP, re.U)
    
    if re.match(r"\s*$", wordNP):
        wordNP = "EMPTY"
        
    wordLCNP = wordNP.lower()
    if re.match(r"\s*$", wordLCNP):
        wordLCNP = "EMPTY"
     
    #print word
    #print wordNP
    #print wordLCNP
    #Feature generation
    #0 = lexical word
    feats.append("TOKEN-"+word)
    
    chars = list(word)
    #print word
    #print chars
    lastChar = chars[-1]
    if re.search(r"[a-z]", lastChar) != None:
        lastChar = 'a'
    elif re.search(r"[A-Z]", lastChar) != None:
        lastChar = 'A'
    elif re.search(r"[0-9]", lastChar) != None:
        lastChar= '0'
    #1 = last char
    feats.append(lastChar)
    
    chars_len = len(chars)
    
    #2 = first char
    feats.append(chars[0])
    
    #3 = first 2 chars
    if chars_len >= 2:
        feats.append(chars[0]+chars[1])
    else:
        feats.append(chars[0])
    
    #4 = first 3 chars
    if chars_len >= 3:
        feats.append(chars[0]+chars[1]+chars[2])
    elif chars_len >= 2:
        feats.append(chars[0]+chars[1])
    else:
        feats.append(chars[0])
        
    #5 = first 4 chars
    if chars_len >= 4:
        feats.append(chars[0]+chars[1]+chars[2]+chars[3])
    elif chars_len >= 3:
        feats.append(chars[0]+chars[1]+chars[2])
    elif chars_len >= 2:
        feats.append(chars[0]+chars[1])
    else:
        feats.append(chars[0])
        
    #6 = last char
    feats.append(chars[-1])
    
    #7 = last 2 chars
    if chars_len >= 2:
        feats.append(chars[-2]+chars[-1])
    else:
        feats.append(chars[-1])
        
    #8 = last 3 chars
    if chars_len >= 3:
        feats.append(chars[-3]+chars[-2]+chars[-1])
    elif chars_len >= 2:
        feats.append(chars[-2]+chars[-1])
    else:
        feats.append(chars[-1])
    
    #9 = last 4 chars
    if chars_len >= 4:
        feats.append(chars[-4]+chars[-3]+chars[-2]+chars[-1])
    elif chars_len >= 3:
        feats.append(chars[-3]+chars[-2]+chars[-1])
    elif chars_len >= 2:
        feats.append(chars[-2]+chars[-1])
    else:
        feats.append(chars[-1])
        
    #10 = lowercased word, no punct
    feats.append(wordLCNP)
    
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
    feats.append(ortho)
    
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
    feats.append(num)
    
    #names
    dictStatus = dict[wordLCNP] if dict.has_key(wordLCNP) else 0
    #print "DICTSTATUS!!!"
    #print dictStatus
    #print wordLCNP
    
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
    feats.append(isInDict)
    #print isInDict
    #14 = male name
    feats.append(maleName)
    #print maleName
    #15 = female name
    feats.append(femaleName)
    #print femaleName
    #16 = last name
    feats.append(lastName)
    #print lastName
    #17 = month name
    feats.append(monthName)
    #print monthName
    #18 = place name
    feats.append(placeName)
    #print placeName
    #19 = publisher name
    feats.append(publisherName)
    #print publisherName
    
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
    feats.append(punct)

def generateKeywordFeature(token, feats, keywords):
    
    i = 0
    #print "TOKEN IN!!!"
    #print token.encode("utf-8")
    #strip out leading punctation
    #token = re.sub(r"^[^\32-\151]+", "", token)
    token = re.sub(r"^[\!\.\,\?]+","", token)
    #strip out trailing punctation
    #token = re.sub(r"[^\32-\151]+$", "", token)
    token = re.sub(r"[\!\.\,\?]+$","", token)
    #token.strip('!,.?')
    
    #canocalize number into "0"
    token = re.sub(r"\d", "0", token)
    #print "TOKEN OUT!!!"
    #print token.encode("utf-8")
    
    #9 tags: feature 1-10
    featsTmp = []
    for item in tags:
        #print "ITEM!!!"
        #print item
        if tags[item] == 0:
            continue
            
        #print item
        #print "TOKEN!!!"
        #print token.encode("utf-8")
        #print "ITEM!!!"
        #print item
        #pozor item je ve slovniku v jinem poradi, nez v PERL
        if keywords[item].has_key(token) and keywords[item][token]:
            featsTmp.append(item+"-" + token)
        else:
            featsTmp.append("none")
    
    #keyword
    feats.append(featsTmp[6])
    #page
    feats.append(featsTmp[9])
    #degree
    feats.append(featsTmp[0])
    #intro
    feats.append(featsTmp[4])
    #date
    #feats.append(featsTmp[7])
    #author
    #feats.append(featsTmp[10])
    #phone
    #feats.append(featsTmp[4])
    #note
    feats.append(featsTmp[8])
    #web
    #feats.append(featsTmp[8])
    #email
    #feats.append(featsTmp[12])
    #pubnum
    feats.append(featsTmp[1])
    #title
    feats.append(featsTmp[7])
    #abstract
    feats.append(featsTmp[3])
    #address
    feats.append(featsTmp[5])
    #affiliation
    feats.append(featsTmp[2])

def crfFeature(line, tag, feats):
    
    token = ""
    
    tmpTokens = re.split("\s+", line)
    #filter out empty token
    tokens = []
    for token in tmpTokens:
        if token != "":
            tokens.append(token)
    
    #print "TOKEN!!!!"
    #print token.encode("utf-8")
    #full form: does not count in crf template file, simply for outputing purpose to get the whole line data
    lineFull = "|||".join(tokens)
    #print lineFull.encode("utf-8")
    feats.append(lineFull)
    
    #fullForm token general features: concatenate the whole line into one token, apply most of Parscit features
    if isFullFormToken:
        #normalize number
        lineFull = re.sub(r"\d", "0", lineFull)
        #strip of the seperator we previously added
        lineFull = re.sub(r"\|\|\|", "", lineFull)
        
        generateTokenFeature(lineFull, feats)
        
    #first token general features: apply most of Parscit features
    if isFirstToken:
        generateTokenFeature(tokens[0], feats)
        
    #first token keyword features
    if isKeyword:
        #print "TOKEN!!!"
        #print tokens[0].encode("utf-8")
        generateKeywordFeature(tokens[0], feats, keywords)
        
    #second token general features: apply most of Parscit features
    if isSecondToken or isBigram:
        token = "EMPTY"
        
        #1 token
        if len(tokens)-1 > 0:
            #print len(tokens)
            token = tokens[1]
            #print token
            
    if isSecondToken:
        generateTokenFeature(token, feats)
        
    #bigram features
    if isBigram:
        nGram = tokens[0]
        nGram = re.sub(r"^[^\32-\151]+", "", nGram)
        nGram = re.sub(r"[^\32-\151]+$", "", nGram)
        nGram = re.sub(r"\d", "0", nGram)
        nGram = nGram.lower()
        
        token = re.sub(r"^[^\32-\151]+", "", token)
        token = re.sub(r"[^\32-\151]+$", "", token)
        token = re.sub(r"\d", "0", token)
        token = token.lower()
        
        nGram += "-"+token
        generateKeywordFeature(nGram, feats, bigrams)
        
    #second last token general features: apply most of Parscit features
    if isSecondLastToken:
        token = "EMPTY"
        
        #only 1 token
        if len(tokens) > 0:
            #mozna jen -1, ale spise takhle
            token = tokens[len(tokens)-2]
    
    if isSecondLastToken:
        generateTokenFeature(token, feats)
        
    #last token general features: apply most of Parscit features
    if isLastToken:
        generateTokenFeature(tokens[len(tokens)-1], feats)
        
    #print "FEATS!!!"
    #print feats
    #output tag
    #print "Pridavam: ", tag, "!!"
    feats.append(tag)

def decode(inFile, outFile, confLevel):
    
    labeledFile = inFile+"_dec"
    if confLevel:
        os.system(crf_test + " -v1 -m " + modelFile + " " + inFile + " > " + labeledFile)
    else:
        os.system(crf_test + " -m " + modelFile + " " + inFile + " > " + labeledFile)
        
    labeledFile_fd = ""
    try:
        labeledFile_fd = codecs.open(labeledFile, 'r', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + labeledFile)
        sys.exit(1)
        
    outFile_fd = ""
    try:
        outFile_fd = codecs.open(outFile, 'w', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + outFile)
        sys.exit(1)
        
    outFile_fd.write(labeledFile_fd.read())
    labeledFile_fd.close()
    outFile_fd.close()
    #sys.exit(0)
    os.remove(labeledFile)
    
    return 1;
