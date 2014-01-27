from time import time
import re
import codecs
import sys
import os

# based on SectLabel

crf_test = "./crfpp/crf_test"

dict = {}
func_word = {}
keywords = {}
bigrams = {}
trigrams = {}
fourthgrams = {}

all_tags = {
                "title":0,
                "address":0, 
                "affiliation":1, 
                "keyword":0, 
                "note":1, 
                "copyright":1, 
                "category":0, 
                "reference":1, 
                "author":0, 
                "email":0, 
                "page":0, 
                "sectionHeader":1, 
                "subsectionHeader":0, 
                "subsubsectionHeader":0, 
                "bodyText":0, 
                "footnote":0, 
                "figureCaption":0, 
                "tableCaption":0, 
                "listItem":0, 
                "figure":0, 
                "table":0, 
                "equation":0, 
                "construct":0}
                
config = {
                "1token":0, 
                "2token":0, 
                "3token":0, 
                "4token":0, 
                #token-level features
                "cit":0, 
                "cit_char":0, 
                "tokenCapital":0, 
                "tokenNumber":0, 
                "tokenName":0, 
                "tokenPunct":0, 
                "tokenKeyword":0, 
                "1gram":0, 
                "2gram":0, 
                "3gram":0, 
                "4gram":0, 
                "lineNum":0, 
                "linePunct":0, 
                "linePos":0, 
                "lineLength":0, 
                "lineCapital":0, 
                #Pos
                "xmlLoc":0, 
                "xmlAlign":0, 
                "xmlIndent":0, 
                #Format
                "xmlFontSize":0, 
                "xmlBold":0, 
                "xmlItalic":0, 
                #Object
                "xmlPic":0, 
                "xmlTable":0, 
                "xmlBullet":0, 
                #Bigram differential features
                "bi_xmlA":0, 
                "bi_xmlS":0, 
                "bi_xmlF":0, 
                "bi_xmlSF":0, 
                "bi_xmlSFBI":0, 
                "bi_xmlSFBIA":0, 
                "bi_xmlPara":0, 
                #unused
                "xmlSpace":0}
                
tag_map = {
                "lineLevel":"UL", 
                "xml":"UX", 
                "bi_xml":"B",  #bigram
                "1token":"U1", 
                "2token":"U2", 
                "3token":"U3", 
                "4token":"U4", 
                "1gram":"U5", 
                "2gram":"U6", 
                "3gram":"U7", 
                "4gram":"U8", 
                "capital":"U9", 
                "number":"UA0", 
                "punct":"UA1", 
                "func":"UA2", 
                "binary":"UA3"}

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
    
def LoadListHash(infile, hash):
    #debug docasne
    debug = 1
    #otevreni func
    infile_fd = ""
    try:
        infile_fd = codecs.open(infile, 'r', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + infile)
        sys.exit(1)
        
    tmpWhileBuf = infile_fd.readline()
    while(tmpWhileBuf):
        hash[tmpWhileBuf] = 1
        tmpWhileBuf = infile_fd.readline()
        
    #if debug:
        #print "Func done!!!"
    infile_fd.close()
    
def LoadConfigFile(infile, configs):
    #debug docasne
    debug = 1
    #otevreni konfiguracniho souboru
    infile_fd = ""
    try:
        infile_fd = codecs.open(infile, 'r', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + infile)
        sys.exit(1)
    
    tmpWhileBuf = infile_fd.readline()
    while(tmpWhileBuf):
        if re.match(r".+=.+$", tmpWhileBuf) != None:
            tmpRes = re.match(r"([^=]*)", tmpWhileBuf)
            name = tmpRes.group(0)
            #print "Name: ", name
            tmpRes = re.search(r"(=.+$)", tmpWhileBuf)
            value = tmpRes.group(0)
            value = re.sub(r"=", "", value)
            #print "Value: ", value
            configs[name] = value
        tmpWhileBuf = infile_fd.readline()
    
    #if debug:
        #print "Config done!!!"
    infile_fd.close()

def Initialize(dict_file, func_file, config_file):
    ReadDict(dict_file)
    #pozor, func_word se mozna vrati prazdne, tak kdyztak osetrit!!!!
    LoadListHash(func_file, func_word)
    #pozor, config se mozna vrati prazdne, tak kdyztak osetrit!!!!
    LoadConfigFile(config_file, config)

#vytvoreni tmp souboru
def BuildTmpFile(filename):
    return "/tmp/" + filename + str(int(time()))
    
def GetDocLineCounts(text_lines,  count_map):
    count = 0
    doc_id = 0
    flag = 0
    
    for index in range(len(text_lines)):
        tmp_lines = text_lines[index]
        tmp_lines = re.sub(r"\n$", "", tmp_lines, 1)
        count += 1
        
        #prazdne radky znaci novy dokument
        if re.match(r"\s*$",  tmp_lines) != None:
            flag = 1
            
            count_map[doc_id] = count
            
            count = 0
            doc_id += 1
        
    if not flag:
        count_map[doc_id] = count

def GetCapFeature(tokens):
    
    cap = "OtherCaps"
    n = 0
    count = 0
    count1 = 0
    line = ""
    
    is_skip = 0
    for index in range(len(tokens)):
        token = tokens[index]
        if re.match(r"[^\32-\151]*$",  token) != None:
            continue
            
        #k identifikaci ne-slov ci slov jako as a an the on in atd.
        if len(token) < 4:
            if index == 0 and re.search(r"\d",  token) != None:
                is_skip = 1
            continue
        
        #capitalized
        if re.match(r"[A-Z][A-Za-z]*$",  token) != None:
            count += 1
            line += token + " "
        
        n += 1
    
    #pouze v pripade, ze pouze jedno slovo zacina velkym pismenem
    if count > 0:
        if count == n:
            cap = "Most" if is_skip else "All"
            
            if re.search(r"[a-z]", line) != None:
                cap += "InitCaps"
            else:
                cap += "CharCaps"
            
            #pokud prvni token obsahuje cislo
            if re.search(r"\d", tokens[0]) != None:
                cap = "number"+cap
            elif count == 1:
                cap = "OtherCaps"
        
    return cap

def GenerateLineFeature(line, tokens, index,  num_lines,  is_abstract,  is_intro,  feats,  msg, label, templates, feature_counts):
    
    #CRFPP template
    templates.append(msg)
    prev_size = len(feats)
    if(not feature_counts.has_key(label)):
        feature_counts[label] = {}
        feature_counts[label]["start"] = prev_size
    #feature_counts[label]["start"] = prev_size
    
    #editor
    has_possible_editor = ""
    if re.search(r"[^A-Za-z](ed\.|editor|editors|eds\.)",  line) != None:
        has_possible_editor = "possibleEditors"
    else:
        has_possible_editor = "noEditors"
    feats.append(has_possible_editor)
    
    if config["lineNum"] == '1':
        word = tokens[0]
        num = ""
        
        if(len(tokens) > 1):
            if re.match(r"[1-9]\.[1-9]\.?$",  word) != None:
                num = "posSubsec"
            elif re.match(r"[1-9]\.[1-9]\.[1-9]\.?$",  word) != None:
                num = "posSubsubsec"
            elif re.match(r"\w\.[1-9]\.[1-9]\.?$",  word) != None:
                num = "posCategory"
                
        if not num:
            if re.match(r"[1-9][A-Za-z]\w*$",  word) != None:
                num = "numFootnote"
            elif re.match(r"[1-9]\s*(http|www)", word) != None:
                num = "numWebfootnote"
            else:
                num = "lineNumOthers"
        
        feats.append(num)
        
    if config["linePunct"] == '1':
        punct = ""
        if re.search(r"@\w+\.", line) != None:
            punct = "possibleEmail"
        elif re.search(r"(www|http)", line) != None:
            punct = "possibleWeb"
        elif re.search(r"\(\d\d?\)\s*$", line) != None:
            punct = "endNumbering"
        else:
            punct = "linePunctOthers"
        
        feats.append(punct)
    
    if config["lineCapital"] == '1':
        cap = GetCapFeature(tokens)
        feats.append(cap)
    
    if config["linePos"] == '1':
        position = "POS-"+str(int(index*8.0/num_lines))
        feats.append(position)
        
    if config["lineLength"] == '1':
        num_words = 0
        tokensArr = re.split("\s+", line)
        #jelikoz se splituje jen mezerou a text muze obsahovat vice mezer mezi slovy,
        #je treba prebytek odstranit. Zaroven spocteme pocet slov v textu
        for indexFor in range(len(tokensArr)):
            tokensArr[indexFor] = re.sub(r"\s+", "", tokensArr[indexFor])
            if re.match(r"[\.\,\;\?\!\:\'\"\}\{\(\)-]*[a-zA-Z]+[\.\,\;\?\!\:\'\"\}\{\(\)-]*$", tokensArr[indexFor]) != None:
                num_words += 1
        
        word_length = "5+Words" if num_words >= 5 else str(num_words) + "Words"
        feats.append(word_length)
    
    #pro CRFPP sablonu
    cur_size = len(feats)
    feature_counts[label]["end"] = cur_size
    
    i = 0
    for indexFor in range(prev_size, cur_size):
        templates.append(label+str(i)+":%x[0,"+str(indexFor)+"]\n")
        i += 1
        
    templates.append("\n")
    
    #retArray = []
    #retArray.append(tokens)
    #retArray.append(templates)
    #retArray.append(feature_counts)
    #return retArray
    

#bude se hodit pozdeji
def GenerateXmlFeature(xml_feature, feats, msg, label, biLabel, templates, feature_counts):
    features = []
    if not xml_feature == "":
        features = xml_feature.split(" ")
    count = 0
    type = ""
    
    bi_feature_flag = {}
    
    #print "Features: ",  xml_feature,  "\n"
    #print "Len: ", str(len(features)),  "\n"
    #pokud se pracuje pouze se surovym textem, tak range nebude zadny a cele se to preskoci
    for feature in features:
        if re.match(r"bi_xml",  feature) != None:
            bi_feature_flag[count] = 1
            
        if re.match(r"(bi_)?xml[a-zA-Z]+\_.+$", feature) != None:
            tmpStr = re.match(r"((bi_)?xml[a-zA-Z]+)\_.+$",  feature)
            type = tmpStr.group(1)
            if config[type] == '1':
                feats.append(feature)
                count += 1
        else:
            print "No, tak tohle jsem presne nechtel"
            sys.exit(1)
    
    UpdateTemplate(len(feats), count, msg, label, templates, feature_counts, biLabel, bi_feature_flag)

def UpdateTemplate(cur_size,  num_features, msg, label, templates, feature_counts, biLabel, bi_feature_flag):
    
    #CRFpp template
    templates.append(msg)
    prev_size = cur_size - num_features
    if not feature_counts.has_key(label):
        feature_counts[label] = {}
    feature_counts[label]["start"] = prev_size
    feature_counts[label]["end"] = cur_size
    
    i = 0
    for index in range(prev_size,  cur_size):
        if bi_feature_flag.has_key(i) and bi_feature_flag[i] == 1:
            templates.append(biLabel+str(i)+":%x[0,"+str(index)+"]\n")
            i += 1
        else:
            templates.append(label+str(i)+":%x[0,"+str(index)+"]\n")
            i += 1
            
    templates.append("\n")

def GetNgrams(line,  num_ngram, ngrams):
    #pozor na vice mezer mezi slovy
    tmp_tokens = line.split(" ")
    #k filtraci prazdnych tokenu
    tokens = []
    
    for index in range(len(tmp_tokens)):
        token = tmp_tokens[index]
        if token:
            token = re.sub(r"^\s+", "", token)
            token = re.sub(r"\s+$", "", token)
            token = re.sub(r"^[^\32-\151]+", "", token)
            token = re.sub(r"[^\32-\151]+$", "", token)
            #canocalize number into "0"
            token = re.sub(r"\d", "0", token)
            
            #normalizace emailu
            if re.search(r"\w.*@.*\..*", token):
                tmpStr = re.search(r"(\w.*)@(.*\..*)", token)
                token = tmpStr.group(0)
                
                remain = tmpStr.group(1)
                token = re.sub(r"\w+", "x", token)
                token = re.sub(r"\d+", "0", token)
                token += "@" + remain
                
                if token:
                    tokens.append(token)
    print "Tokens: ", tokens
    
    count = 0
    #pozor, tady si to pohlidat, v perlu to bylo <=, takze to tady delam taky tak
    for index in range(len(tokens)+1):
        #not enough ngrams
        if len(tokens) - index + 1 < num_ngram:
            break
            
        ngram = ""
        for indexFor in range(index,  index+num_ngram-1):
            token = tokens[indexFor]
            
            if indexFor < i+num_ngram-1:
                ngram += token+"-"
            else:
                ngram += token
        
        #preskocime prazdne radky
        if re.match(r"\s*$",  ngram):
            continue
        #preskocime radky pouze z cislic
        if re.match(r"\d*$",  ngram):
            continue
        #skip function words, matter for ngram = 1
        if func_word[ngram]:
            continue
            
        ngrams.append(ngram)
        count += 1
        if count == 4:
            break

def GenerateKeywordFeature(tokens, feats, keywords, msg, label, templates, feature_counts):
    #CRFpp template
    templates.append(msg)
    prev_size = len(feats)
    if not feature_counts.has_key(label):
        feature_counts[label] = {}
    feature_counts[label]["start"] = prev_size
    
    for item in all_tags:
        if all_tags[item] == 0:
            continue
        
        i = 0
        for i in range(len(tokens)):
            if keywords[item][tokens[i]]:
                feats.append(item+"-"+tokens[i])
                break
                
        #tady pozor, protoze i se zvetsuje do range, kdezto v perlu je tam i++, takze zde to bude o 1 mene
        if(i == len(tokens)-1):
            feats.append("none")
            
    cur_size = len(feats)
    feature_counts[label]["end"] = cur_size
    
    i = 0
    for j in range(prev_size, cur_size):
        templates.append(label+str(i)+":%x[0,"+str(j)+"]\n")
        
    templates.append("\n")

def GenerateTokenFeature(tokens, index, keywords, feats, msg, label, templates, feature_counts):
    
    num_tokens = len(tokens)
    token = "EMPTY"
    if num_tokens > index:
        token = tokens[index]
        
    #CRFpp template
    templates.append(msg)
    prev_size = len(feats)
    if not feature_counts.has_key(label):
        feature_counts[label] = {}
    feature_counts[label]["start"] = prev_size
    
    #prep
    word = token
    word_lc = token.lower()
    
    #no punctation
    word_np = token
    word_np = re.sub(r"[^\w]", "", word_np)
    if re.match(r"\s*$", word_np):
        word_np = "EMPTY"
        
    #lowercased word, no punctation
    word_lcnp = word_np.lower()
    if re.match(r"\s*$", word_lcnp):
        word_lcnp = "EMPTY"
        
    feats.append("TOKEN-"+word)
    feats.append(word_lc)
    feats.append(word_lcnp)
    
    #parscit char feature
    if config["parscit"] == '1':
        #print "Jeste stalo JOJOJO"
        #parscit_char
        if config["parscit_char"] == '1':
            chars = []
            for indexFor in range(len(word)):
                chars.append(word[indexFor])
            #chars = word.split("")
            #print word.encode("utf-8")
            #print chars
            #print len(chars)
            last_char = chars[-1]
            #print last_char
            
            if re.search(r"[a-z]", last_char):
                last_char = 'a'
            elif re.search(r"[A-Z]", last_char):
                last_char ='A'
            elif re.search(r"[0-9]", last_char):
                last_char = '0'
            
            # 1 = last char
            feats.append(last_char)
            
            for indexFor in range(len(chars), 4):
                chars.append('|')
            
            #2 = first char
            feats.append(chars[0])
            #3 = first 2 chars
            feats.append(chars[0]+chars[1])
            #4 = first 3 chars
            feats.append(chars[0]+chars[1]+chars[2])
            #5 = first 4 chars
            feats.append(chars[0]+chars[1]+chars[2]+chars[3])
            
            #6 = last char
            feats.append(chars[-1])
            #7 = last 2 chars
            feats.append(chars[-2]+chars[-1])
            #8 = last 3 chars
            feats.append(chars[-3]+chars[-2]+chars[-1])
            #9 = last 4 chars
            feats.append(chars[-4]+chars[-3]+chars[-2]+chars[-1])
            
    #capitalization features
    if config["tokenCapital"] == '1':
        ortho = ""
        if re.search(r"^[A-Z]$", word_np) != None:
            ortho = "singleCap"
        elif re.search(r"^[A-Z][a-z]+", word_np) != None:
            ortho = "InitCap"
        elif re.search(r"^[A-Z}]+$", word_np) != None:
            ortho = "AllCap"
        else:
            ortho = "others"
        feats.append(ortho)
        
    if config["tokenNumber"] == '1':
        num = ""
        
        #mozna to pak trochu predelat, protoze vetsina se dela tak jako tak
        if config["parscit"] == '1':
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
        else:
            if re.match(r"[1-9]+\.$",  word) != None:
                num = "endDot"
            elif re.match(r"[1-9]+:$", word) != None:
                num = "endCol"
            elif re.match(r"(19|20)[0-9][0-9]$", word_np) != None:
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
        
        feats.append(num)
    
    #Gazetteer (names) features
    if config["tokenName"] == '1':
        dict_status = dict[word_lcnp] if dict.has_key(word_lcnp) else 0
        
        is_in_dict = dict_status
        publisher_name = ""
        place_name = ""
        month_name = ""
        last_name = ""
        female_name = ""
        male_name = ""
        
        if dict_status >= 32:
            dict_status -= 32
            publisher_name = "publisherName"
        else:
            publisher_name = "no"
            
        if dict_status >= 16:
            dict_status -= 16
            place_name = "placeName"
        else:
            place_name = "no"
            
        if dict_status >= 8:
            dict_status -= 8
            month_name = "monthName"
        else:
            month_name = "no"
            
        if dict_status >=4:
            dict_status -= 4
            last_name = "lastName"
        else:
            last_name = "no"
            
        if dict_status >= 2:
            dict_status -= 2
            female_name = "femaleName"
        else:
            female_name = "no"
            
        if dict_status >= 1:
            dict_status -= 1
            male_name = "maleName"
        else:
            male_name = "no"
        
        #13 = name status
        feats.append(is_in_dict)
        #14 = male name
        feats.append(male_name)
        #15 = female name
        feats.append(female_name)
        #16 = last name
        feats.append(last_name)
        #17 = month name
        feats.append(month_name)
        #18 = place name
        feats.append(place_name)
        #19 = publisher name
        feats.append(publisher_name)
        
    #punctation features
    if config["tokenPunct"] == '1':
        punct = ""
    
        if config["cit"] == '1':
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
        else:
            if re.match(r"[a-z]\d$",  word) != None:
                punct = "possibleVar"
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
        
        feats.append(punct)
        
    if config["tokenKeyword"] == '1':
        keyword_fea = "noKeyword"
        token = word
        
        token = re.sub(r"^[^\32-\151]+", "", token)
        token = re.sub(r"[^\32-\151]+$", "", token)
        token = re.sub(r"\d", "0", token)
        
        for item in all_tags:
            if all_tags[item] == 0:
                continue
            
            if keywords and keywords[item][token]:
                keyword_fea = "keyword-"+item
                break
                
        feats.append(keyword_fea)
        
    #for CRFpp template
    cur_size = len(feats)
    feature_counts[label]["end"] = cur_size
    
    i = 0
    for j in range(prev_size, cur_size):
        templates.append(label+str(i)+":%x[0,"+str(j)+"]\n")
        i += 1
        
    templates.append("\n")
    
    #print "Debug feats: ",  feats, "\n"
    #print "Debug templates: ", templates, "\n"

#hlavni funkce pro extrakci vlastnosti
def CRFFeature(line, index, num_lines, is_abstract, is_intro , xml_feature, tag, feats):
    token = ""
    templates = []
    feature_counts = {}
    
    tmpTokens = re.split("\s+", line)
    tokens = []
    
    for indexFor in range(len(tmpTokens)):
        token = tmpTokens[indexFor]
        token = re.sub(r"\s+", "", token)
        
        if token:
            tokens.append(token)
            
    lineFull = "|||".join(tokens)
    feats.append(lineFull)
    
    #@returns tokens,templates,feature_counts
    GenerateLineFeature(line, tokens, index,  num_lines,  is_abstract,  is_intro,  feats,  "#Line-level features\n", tag_map["lineLevel"], templates, feature_counts)
    #tokens = retArray[0]
    #templates = retArray[1]
    #feature_counts = retArray[2]
    #print templates
    GenerateXmlFeature(xml_feature, feats,  "#Xml features\n", tag_map["xml"], tag_map["bi_xml"], templates, feature_counts)

    #keyword features
    #5 protoze cyklus jde do max-1 a my prave potrebujeme 4
    for indexFor in range(1, 5):
        if config[str(indexFor)+"gram"] == '1':
            top_tokens = []
            GetNgrams(line, indexFor, top_tokens)
            GenerateKeywordFeature(top_tokens, feats, keywords, "# "+str(indexFor)+"gram features\n", tag_map[str(indexFor)+"gram"],templates,feature_counts)
    
    #token-level features
    for indexFor in range(1, 5):
        if config[str(indexFor)+"token"] == '1':
            GenerateTokenFeature(tokens, indexFor-1,  keywords, feats, "# "+str(indexFor)+"token general features\n", tag_map[str(indexFor)+"token"], templates,feature_counts)
            
    #print "-------FEATS!!!--------"
    #print " ".join(feats)
    #for splitIndex in range(len(feats)):
        #print type(feats[splitIndex])
        #if type(feats[splitIndex]) == type(unicode()):
            #tmpStr = feats[splitIndex]+" "
            #sys.stdout.write(feats[splitIndex].encode("utf-8") + " ")
        #elif type(feats[splitIndex]) == type(str()):
            #sys.stdout.write(feats[splitIndex].encode("utf-8")+" ")
        #else:
            #sys.stdout.write(str(feats[splitIndex])+" ")
    #sys.stdout.write("\n")
    #feature linking
    i = ""
    
    if config.has_key("back1") and config["back1"] == '1':
        FeatureLink(templates, "UA", "#constraint on first token features at -1 relative position \n", feature_counts[tag_map["1token"]]["start"], feature_counts[tag_map["1token"]]["end"], "-1")
    templates.append("\n")

    if config.has_key("back1") and config["forw1"] == '1':
        FeatureLink(templates, "UB", "#constraint on first token features at +1 relative position \n", feature_counts[tag_map["1token"]]["start"], feature_counts[tag_map["1token"]]["end"], "1")
    templates.append("\n")
 
    #output tag
    feats.append(tag)
    #print "Debug feats: ", feats, "\n"
    
    templates.append("# Output\nB0\n")
    return templates

#@text_lines - surova_data po radcich - seznam
#@outfile - tmpfile
def ProcessData(text_lines, outfile, is_generate_template, debug):
    try:
        outfile_fd = codecs.open(outfile, 'w', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + outfile)
        sys.exit(1)
        
    count_map = {}
    GetDocLineCounts(text_lines, count_map)
    #pozor, pokud se bude delat rozsireni, spocitat z count_map, kolik dokumentu tam opravdu je
    num_docs = 1
    
    is_abstract = 0
    is_intro = 0
    doc_id = 0
    tag = "noTag"
    index = -1
    num_lines = count_map[doc_id]
    
    #if debug:
    #    print "Radku: ",  num_lines,  " \n"
        
    xml_feature = ""
    
    for indexFor in range(len(text_lines)):
        tmp_lines = text_lines[indexFor]
        tmp_lines = re.sub(r"\n$", "", tmp_lines, 1)
        index += 1
        
        #podminka by nemela nikdy platit
        if re.match(r"\s*$", tmp_lines) != None:
            print "Skript se dostal do spatneho mista"
            sys.exit(1)
        else:
            if re.match(r".+? \|\|\| .+$", tmp_lines) != None:
                tmpRes = re.match(r"(.+?) \|\|\| (.+$)", tmp_lines)
                tag = tmpRes.group(0)
                tmp_lines = tmpRes.group(1)
                
                if(not all_tags.has_key(tag)):
                    continue
                
            if re.match(r".+? \|XML\| .+?$",  tmp_lines) != None:
                tmpRes = re.match(r"(.+?) \|XML\| (.+?)$", tmp_lines)
                tmp_lines = tmpRes.group(1)
                xml_feature = tmpRes.group(2)
                
            if re.search(r"abstract",  tmp_lines,  re.I):
                is_abstract = 1
                
            elif re.search(r"introduction",  tmp_lines,  re.I):
                is_intro = 1
            else:
                if is_abstract == 1:
                    is_abstract = 2
                if is_intro == 1:
                    is_intro = 2
                    
            feats = []
            #print "Debug Tmp Lines: ", tmp_lines.encode("utf-8")
            templates = CRFFeature(tmp_lines,  index,  num_lines,  is_abstract,  is_intro,  xml_feature,  tag,  feats)
            
            if is_generate_template:
                is_generate_template = 0
                print templates
            
            #print "Debug FEATS!!!!: ", feats
            #sys.exit(1)
            #print outfile
            for splitIndex in range(len(feats)-1):
                #print type(feats[splitIndex])
                if type(feats[splitIndex]) == type(unicode()):
                    outfile_fd.write(feats[splitIndex]+" ")
                elif type(feats[splitIndex]) == type(str()):
                    outfile_fd.write(feats[splitIndex].encode("utf-8")+" ")
                else:
                    outfile_fd.write(str(feats[splitIndex])+" ")
                
            outfile_fd.write(str(feats[len(feats)-1]))
            #outfile_fd.write(" ".join(feats))
            outfile_fd.write("\n")
    
    outfile_fd.close()
    
#entry point
#@text_lines - surova data po radcich - seznam
#@file - surova data
def ExtractTestFeatures(text_lines, file, dict_file, func_file, config_file, debug):
    tmpfile = BuildTmpFile("raw_data")
    Initialize(dict_file, func_file, config_file)
    #if debug:
        #print "Initialize done!"
    
    is_generate_template = 0
    ProcessData(text_lines, tmpfile, is_generate_template, debug)
    
    return tmpfile
    
def Decode(infile, model_file, outfile):
    labeled_file = str(int(time()))
    #print labeled_file
    os.system(crf_test + " -v1 -m " + model_file + " " + infile + " > " + labeled_file)
    
    try:
        labeled_file_fd = codecs.open(labeled_file, 'r', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + labeled_file)
        sys.exit(1)
        
    try:
        outfile_fd = codecs.open(outfile, 'w', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + outfile)
        sys.exit(1)
        
    try:
            outfile_fd.write(labeled_file_fd.read())
    except UnicodeDecodeError:
        sys.stderr.write("Nelze precist data z " + outfile)
        sys.exit(1)
        
    labeled_file_fd.close()
    outfile_fd.close()
    #print infile
    #print labeled_file
    #sys.exit(0)
    os.remove(labeled_file)
    return 1
