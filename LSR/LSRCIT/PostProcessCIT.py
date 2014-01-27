import os
import sys
import re
import codecs
import string

def FinishCitation(r_xml, r_current_tag, r_current_tokens):
    #print "Vysledek!!!"
    #print r_current_tag
    #print r_current_tokens
    if r_current_tag:
        r_xml += MakeSegment(r_current_tag, r_current_tokens)
        r_xml += "</citation>\n"
        #print r_xml.encode("utf-8")
        r_current_tag = ""
        return r_xml

def MakeSegment(tag, tokens):
    #print "UZ SKORO"
    #print tag
    #print tokens 
    #if len(tokens) > 1:
    segment = " ".join(tokens)
    #else:
    #    segment = tokens[0]
    return "<" + tag + ">" + segment + "</" + tag + ">\n"

def NormalizeFields(rxml):
    cite_infos = []
    
    tmprxml = rxml
    
    cite_blocks = []
    while re.search(r"<citation>(.*?)<\/citation>", tmprxml, re.S) != None:
        tmpStr= re.search(r"<citation>(.*?)<\/citation>", tmprxml, re.S)
        #print "NALEZENO!!!!\n", tmpStr.group(1).encode("utf-8")
        cite_blocks.append(tmpStr.group(1))
        tmprxml = re.sub(r"<citation>"+re.escape(tmpStr.group(1))+"<\/citation>", "", tmprxml, re.S)
    
    #print cite_blocks
    for block in cite_blocks:
        cite_info = {}
        
        tmpBlock = block
        while re.search(r"<(.*?)>(.*?)<\/\1>", tmpBlock) != None:
            tmpStr = re.search(r"<(.*?)>(.*?)<\/\1>", tmpBlock)
            tag = tmpStr.group(1)
            content = tmpStr.group(2)
            #print "TAG/CONTENT"
            #print tag
            #print content.encode("utf-8")
            if tag == "author":
                tag = "authors"
                content = NormalizeAuthorNames(content)
            elif tag == "date":
                content = NormalizeDate(content)
            elif tag == "volume":
                content = NormalizeVolume(content)
            elif tag == "number":
                content = NormalizeNumber(content)
            elif tag == "pages":
                content = NormalizePages(content)
            else:
                content = StripPunctation(content)
            
            if not cite_info.has_key(tag):
                #print "JJ!!"
                cite_info[tag] = content
            
            tmpBlock = re.sub(r"<(.*?)>(.*?)<\/\1>", "", tmpBlock, 1)
        cite_infos.append(cite_info)
    return cite_infos

def NormalizeVolume(volume_number):
    
    volumes = []
    
    if re.search(r"(\d+)\s*[\(\{\[]+(\d+)[\)\}\]]?", volume_number) != None:
        tmpStr = re.search(r"(\d+)\s*[\(\{\[]+(\d+)[\)\}\]]?", volume_number)
        volumes.append(tmpStr.group(1))
        volumes.append(tmpStr.group(2))
    elif re.search(r"\d+", volume_number) != None:
        tmpStr = re.search(r"\d+", volume_number)
        tmpStr = tmpStr.group(0)
        volumes.append(tmpStr)
    else:
        volumes.append(volume_number)
    
    return volumes

def JoinMultiWordNames(author_text):
    
    author_text = re.sub(r"(?P<res>\b((?:van|von|der|den|de|di|le|el)))", "\g<res>", author_text, re.I)
    return author_text

def RepairAndTokenizeAuthorText(author_text):
    
    #print author_text.encode("utf-8")
    author_text = re.sub(r"et\.? al\.?.*$", "", author_text, 1)
    author_text = re.sub(r"^.*?[A-Za-z][A-Za-z]+\. ", "", author_text, 1)
    author_text = re.sub(r"\(.*?\)", "", author_text)
    author_text = re.sub(r"^.*?\)\.?", "", author_text)
    author_text = re.sub(r"\(.*?$", "", author_text)
    
    author_text = re.sub(r"\[.*?\]", "", author_text)
    author_text = re.sub(r"^.*?\]\.?", "", author_text)
    author_text = re.sub(r"\[.*?$", "", author_text)
    
    author_text = re.sub(r";", ",", author_text)
    author_text = re.sub(r",", ", ", author_text)
    author_text = re.sub(r"\:", " ", author_text)
    author_text = re.sub(r"[\:\"\<\>\/\?\{\}\[\]\+\=\(\)\*\^\%\$\#\@\!\~\_]","",author_text)
    author_text = JoinMultiWordNames(author_text)
    
    orig_tokens = re.split("\s+", author_text)
    #print "Orig tokens!!!"
    #print orig_tokens
    tokens = []
    
    for i in range(0, len(orig_tokens)):
        tok = orig_tokens[i]
        if re.search(r"[A-Za-z&]", tok) == None:
            if i < (len(orig_tokens) - 1)/2:
                tokens = []
                continue
            else:
                break
        
        if re.search(r"^(jr|sr|ph\.?d|m\.?d|esq)\.?\, ?$", tok, re.I) != None:
            if re.search(r"\,$", tokens[len(tokens)-1]):
                continue
        
        if re.search(r"^[IVX][IVX]+\.?\,?$", tok) != None:
            continue
        
        tokens.append(tok)
    return tokens

def NormalizeAuthorName(auth_tokens):
    
    if len(auth_tokens) < 1:
        return ""
    
    tmp_str = " ".join(auth_tokens)
    
    if re.search(r".+,\s*.+", tmp_str) != None:
        tmpStr = re.search(r".+,", tmp_str)
        tmpStr = tmpStr.group(0)
        tmpStr = re.sub(r",", "", tmpStr)
        tmp1 = tmpStr
        tmpStr = re.search(r",\s*.+", tmp_str)
        tmpStr = tmpStr.group(0)
        tmpStr = re.sub(r",\s*", "", tmpStr)
        tmpStr = tmpStr + " " + tmp1
    
    tmp_str = re.sub(r"\.\-", "-", tmp_str)
    tmp_str = re.sub(r"[\,\.]", " ", tmp_str)
    tmp_str = re.sub(r" +", " ", tmp_str)
    tmp_str = re.sub(r"^\s+", "", tmp_str)
    tmp_str = re.sub(r"\s+$", "", tmp_str)
    #tmp_str = Trim(tmp_str)
    
    if re.search(r"^[^\s][^\s]+(\s+[^\s]|\s+[^\s]\-[^\s])+$", tmp_str) != None:
        new_tokens = tmp_str.split(" ")
        new_order = []
        for i in range(1, len(new_tokens)):
            new_order.append(new_tokens[i])
        new_order.append(new_tokens[0])
        tmp_str = " ".join(new_order)
    
    return tmp_str

def NormalizeAuthorNames(author_text):
    
    tokens = RepairAndTokenizeAuthorText(author_text)
    #print tokens
    
    authors = []
    current_auth = []
    begin_auth = 1
    
    for tok in tokens:
        if re.search(r"^(&|and)$", tok, re.I) != None:
            if current_auth >= 0:
                auth = NormalizeAuthorName(current_auth)
                authors.append(auth)
            current_auth =[]
            begin_auth = 1
            continue
        
        if begin_auth > 0:
            current_auth.append(tok)
            begin_auth = 0
            continue
        
        if re.search(r",$", tok) != None:
            current_auth.append(tok)
            if len(current_auth) > 1:
                auth = NormalizeAuthorName(current_auth)
                authors.append(auth)
                current_auth = []
                begin_auth = 1
        else:
            current_auth.append(tok)
    
    if len(current_auth) >= 1:
        auth = NormalizeAuthorName(current_auth)
        authors.append(auth)
    
    return authors

#kdyztak overit, nejsem si jist
def NormalizeDate(date_text):
    
    if re.search(r"\d{4}", date_text) != None:
        tmpStr = re.search(r"\d{4}", date_text)
        tmpStr = tmpStr.group(0)
        
        #from time import time
        import time
        current_year = time.strftime("%Y")
        
        if tmpStr <= current_year:
            return tmpStr

def NormalizeNumber(num_text):
    
    if re.search(r"\d+", num_text) != None:
        tmpStr = re.search(r"\d+", num_text)
        tmpStr = tmpStr.group(0)
        return tmpStr
    else:
        return num_text
        

def NormalizePages(pageText):
    #print pageText.encode("utf-8")
    if re.search(r"\d+[^\d]+?\d+", pageText) != None:
        tmpStr = re.search(r"(\d+)[^\d]+?(\d+)", pageText)
        #print tmpStr.group(0).encode("utf-8")
        return tmpStr.group(1) + "--" + tmpStr.group(2)
    elif re.search(r"\d+", pageText) != None:
        tmpStr = re.search(r"\d+", pageText)
        return tmpStr.group(0)
    else:
        return pageText

def StripPunctation(text):
    
    exclude = set(string.punctuation)
    text = ''.join(ch for ch in text if ch not in exclude)
    #text = re.sub(r"\.\s*", " ",text)
    return text

def ReadAndNormalize(infile):
    
    status = 1
    msg = ""
    xml = ""
    
    infile_fd = ""
    try:
        infile_fd = codecs.open(infile, 'r', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + infile)
        sys.exit(1)
        
    current_tag = ""
    current_tokens = []
    new_citation = 1
    
    tmp = infile_fd.readline()
    while tmp:
        #print tmp
        #blank line separates citations
        if re.search(r"^\s*$", tmp):
            if new_citation <= 0:
                #print current_tag
                #print current_tokens
                xml = FinishCitation(xml, current_tag, current_tokens)
                #print xml.encode("utf-8")
                current_tokens = []
                current_tag = ""
                new_citation = 1
                tmp = infile_fd.readline()
                #print tmp.encode("utf-8")
                continue
        
        if new_citation > 0:
            xml += "<citation>\n"
            new_citation = 0
            
        fields = re.split("\s+", tmp)
        #print fields
        token = fields[0]
        #print token.encode("utf-8")
        #pak opravit, ze to pole ma posledni zaznam navic
        tag = fields[-2]
        #print tag.encode("utf-8")
        
        if not current_tag:
            current_tag = tag
        
        if tag == current_tag:
            current_tokens.append(token)
        else:
            #print current_tag.encode("utf-8")
            #print current_tokens
            xml += MakeSegment(current_tag, current_tokens)
            current_tag = tag
            current_tokens = []
            current_tokens.append(token)
        
        tmp = infile_fd.readline()
    
    infile_fd.close()
    #print xml.encode("utf-8")
    if new_citation <= 0:
        FinishCitation(xml, current_tag, current_tokens)
        current_tokens = []
        new_citation = 1
        
    rcite_info = NormalizeFields(xml)
    #print "RCITE_INFO\n", rcite_info
    
    retArray = []
    retArray.append(xml)
    retArray.append(rcite_info)
    retArray.append(status)
    retArray.append(msg)
    return retArray
    
