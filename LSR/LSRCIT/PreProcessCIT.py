import os
import sys
import re
import codecs
sys.path.append("./LSRCIT/")
import Citation

marker_types = {
                        "SQUARE":"\[.+?\]", 
                        "PAREN":"\(.+?\)", 
                        "NAKEDNUM":"\d+", 
                        "NAKEDNUMDOT":"\d+\."}

def ExpandBracketMarker(line, pos_array, token_count):
    
    count = 0
    front = ""
    match = ""
    remain = line
    newline = ""
    space_flag = 0
    
    #found = re.findall(r"\[(\d+[,;] *)*((\d+)-(\d+))([,;] *\d+)*\]", line)
    #i = 0
    #tmpFound = found
    """
    while found.group(i) != None:
        #tak to v PERLu netusim, co znamena
        front = "ERR"
        match = "ERR"
        line = "ERR"
        
        # Handle front part
        if space == 1:
            newline += " "
        newline += front
        tokens = front.split("\s+")
        lenght = len(tokens)
        
        for i in range(0,  lenght):
            if i < (lenght - 1) or re.search(r" $", front) != None:
                pos_array.append(token_count)
                token_count += 1
        
        #handle match part
        num_new_tokens = 0
        if re.match(r"\[(\d+[,;] *)*((\d+)-(\d+))([,;] *\d+)*\]$",  match) != None:
            print "Dopis ExpandBracketMarker() : PreProcessCIT\n"
            #kdyztak dopsat, vypada, ze to tudy zatim neprochazi!!!!
            num_new_tokens = "neco"
    """
    if space_flag == 1:
        newline += " "
    newline += line
        
    tokens = re.split("\s+", line)
    tokToDel = []
    for index in range(len(tokens)):
        if not tokens[index]:
            tokToDel.append(index)
    
    for tokToDelItem in tokToDel:
        del tokens[tokToDelItem]
    lenght = len(tokens)
    #print "TOKENS!!!\n", tokens
    #print "LENGHT!!!\n", lenght
    for i in range(0, lenght):
        pos_array.append(token_count)
        token_count += 1
        
    retArray = []
    retArray.append(newline)
    retArray.append(token_count)
    return retArray
    
def NormalizeBodyText(rtext, pos_array):
    
    lines = rtext.split("\n")
    text = ""
    token_count = 0
    
    for line in lines:
        #trip leading spaces
        line = re.sub(r"^\s+", "", line)
        #print "LINE IN!!!!\n", line.encode("utf-8")
        tmp_pos_array = []
        tmpArray = []
        tmpArray = ExpandBracketMarker(line, tmp_pos_array, token_count)
        line = tmpArray[0]
        #print "LINE OUT!!!\n", line.encode("utf-8")
        token_count = tmpArray[1]
        tokens = re.split("\s+", line)
        
        #pak opravit, nemelo by nastat
        tokToDel = []
        for index in range(len(tokens)):
            if not tokens[index]:
                tokToDel.append(index)
    
        for tokToDelItem in tokToDel:
            del tokens[tokToDelItem]
        
        #print "TOK"
        #print tokens
        #print tmp_pos_array
        if len(tokens) != len(tmp_pos_array):
            sys.stderr.write("Proste neco spatne na radku 23 : ParsCIT::Preprocess\n")
            sys.exit(1)
            
        if re.match(r"\s*$", line) != None:
            continue
            
        if re.search(r"[A-Za-z]-$", text) != None:
            tmpStr = re.search(r"([A-Za-z])-$", text)
            text = re.sub(r"[A-Za-z]-$", re.escape(tmpStr.group(1)), text, 1)
            text += line
            del tmp_pos_array[0]
        else:
            if re.search(r"-\s+$", text) == None and text:
                text += " "
            text += line
        
        for item in tmp_pos_array:
            pos_array.append(tmp_pos_array)
        #pos_array.append(tmp_pos_array)
        
    text = re.sub(r"\s{2,}", " ", text)
    #text = re.sub(r"\\-", "", text)
    #print text.encode("utf-8")
    return text
    #if text:
        #return text
    #else:
        #return " "

# Looks for reference section markers in the supplied text and
# separates the citation text from the body text based on these
# indicators.  If it looks like there is a reference section marker
# too early in the document, this procedure will try to find later
# ones.  If the final reference section is still too long, an empty
# citation text string will be returned.  Returns references to
# the citation text, normalized body text, and original body text.
def FindCitationText(rtext, pos_array):
    
    #save the text
    text = rtext
    bodytext = ""
    citetext = text
    
    bodytext = re.match(r"^.+((References?|REFERENCES?|Bibliography|BIBLIOGRAPHY|References?\s+and\s+Notes?|References?\s+Cited|REFERENCES?\s+CITED|REFERENCES?\s+AND\s+NOTES?|LITERATURE?\s+CITED?):?\s*\n+)", text, re.S)
    if bodytext != None:
        bodytext = bodytext.group(0)
        bodytext = re.sub(r"\n+$", "", bodytext)
        #print "BODYTEXT!!!!\n", bodytext.encode("utf-8")
        citetext = re.sub(re.escape(bodytext), "", text, re.S)
        #print "\"" + citetext + "\""
    #if citetext != None:
    #    citetext = citetext.group(0)
    #    citetext = re.sub(r"((References?|REFERENCES?|Bibliography|BIBLIOGRAPHY|References?\s+and\s+Notes?|References?\s+Cited|REFERENCES?\s+CITED|REFERENCES?\s+AND\s+NOTES?|LITERATURE?\s+CITED?):?\s*\n+)", "", text, re.S)
        #print "CITETEXT!!!!\n", citetext.encode("utf-8")
    #citetext = re.sub(r"\b(References?|REFERENCES?|Bibliography|BIBLIOGRAPHY|References?\s+and\s+Notes?|References?\s+Cited|REFERENCES?\s+CITED|REFERENCES?\s+AND\s+NOTES?|LITERATURE?\s+CITED?):?\s*\n+", "", citetext)
    
    #print "BODYTEXT"
    #print bodytext
    #print "CITETEXT"
    #print citetext
    #sys.exit(0)
    retArray = []
    #No citation
    if not citetext or not bodytext:
        sys.stderr.write("Citation text cannot be found: ignoring\n")
        retArray.append(citetext)
        #retArray.append(NormalizeBodyText(bodytext), pos_array)
        retArray.append("")
        retArray.append("")
        return retArray
        
    #Odd case: when citation is longer than the content itself, what should we do?
    if len(citetext) >= 0.8 * len(bodytext):
        sys.stderr.write("Citation text longer then article body: ignoring\n")
        retArray.append(citetext)
        retArray.append(NormalizeBodyText(bodytext), pos_array)
        retArray.append(bodytext)
        return retArray
        
    #Citation stops when another section parts
    scitetext = re.split("^([\s\d\.]+)?(Acknowledge?ments?|Autobiographical|Tables?|Appendix|Exhibit|Annex|Fig|Notes?)(.*?)\n+", citetext, re.S)
    #print scitetext
    if len(scitetext) > 1:
        tmp = scitetext[1]
    else:
        scitetext = scitetext[0]
    
    if len(scitetext) > 0:
        citetext = scitetext
        
    #No citation exists
    if citetext == '0' or not citetext:
        sys.stderr.write("warning: no citation text found\n")
        
    #Now we have citation text
    retArray.append(NormalizeCiteText(citetext))
    retArray.append(NormalizeBodyText(bodytext, pos_array))
    retArray.append(bodytext)
    return retArray

def NormalizeCiteText(rcitetext):
    
    newlines = []
    #print rcitetext
    lines = rcitetext.split("\n")
    
    oldline = ""
    
    for line in lines:
        line = re.sub(r"^\s*", "", line)
        line = re.sub(r"\s*$", "", line)
        
        if re.match(r"\s*$", line) != None or (re.search(r"-$", oldline) != None and re.match(r"\d*$", line) != None):
            oldline = line
            continue
        
        oldline = line
        newlines.append(line)
        
    newtext = "\n".join(newlines)
    #print newtext.encode("utf-8")
    return newtext

# Uses a list of regular expressions that match common citation
# markers to count the number of matches for each type in the
# text.  If a sufficient number of matches to a particular type
# are found, we can be reasonably sure of the type.
def GuessMarkerType(rcite_text):
    
    global marker_types
    marker_type = 'UNKNOWN'
    marker_observations = {}
    
    for type in marker_types:
        marker_observations[type] = 0
        
    cite_text = "\n" + rcite_text
    
    #spocteni radku
    import StringIO
    
    i = 0
    buf = StringIO.StringIO(cite_text)
    tmp = buf.readline()
    while(tmp):
        i += 1
        tmp = buf.readline()
    n_lines = i
    
    tmpCite = cite_text
    #if re.search("\n\s*"+marker_types["SQUARE"]+"[^\n]{10}", cite_text) != None:
    if re.search(r"\n\s*\[.+?\][^\n]{10}", tmpCite, re.S) != None:
        tmpCite = re.subn(r"\n\s*\[.+?\][^\n]{10}", "", tmpCite, re.S)
        #cnt_cite_text = re.findall("(\n\s*"+marker_types["SQUARE"]+"[^\n]{10})", cite_text)
        #cnt_cite_text = len(cnt_cite_text.group())
        #print tmpCite[1]
        marker_observations["SQUARE"] += tmpCite[1]
    
    tmpCite = cite_text
    if re.search(r"\n\s*\(.+?\)[^\n]{10}", tmpCite, re.S) != None:
        tmpCite = re.subn(r"\n\s*\(.+?\)[^\n]{10}", "", tmpCite, re.S)
        #cnt_cite_text = re.findall("(\n\s*"+marker_types["PAREN"]+"[^\n]{10})", cite_text)
        #cnt_cite_text = len(cnt_cite_text.group())
        marker_observations["PAREN"] += tmpCite[1]
    
    tmpCite = cite_text
    #print tmpCite.encode("utf-8")
    if re.search(r"\n\s*\d+[^\n]{10}", tmpCite, re.S) != None:
        tmpCite = re.subn(r"\n\s*\d+[^\n]{10}", "", tmpCite, re.S)
    #    #cnt_cite_text = len(cnt_cite_text.group())
        marker_observations["NAKEDNUM"] += tmpCite[1]
    
    tmpCite = cite_text
    if re.search(r"\n\s*\d+\.[^\n]{10}", tmpCite, re.S) != None:
        tmpCite = re.subn(r"\n\s*\d+\.[^\n]{10}", "", tmpCite, re.S)
        #cnt_cite_text = len(cnt_cite_text.group())
        marker_observations["NAKEDNUMDOT"] += tmpCite[1]
    
    #sorted_observations = marker_observations.sort()
    #sorted_observations =  marker_observations.items()
    #sorted_observations.sort()
    sorted_observations = list(sorted(marker_observations, key=marker_observations.__getitem__, reverse=True))
    #print "SORTED"
    #print sorted_observations
    #print "SQUARE"
    #print marker_observations["SQUARE"]
    #print "PAREN"
    #print marker_observations["PAREN"]
    #print "NAKEDNUM"
    #print marker_observations["NAKEDNUM"]
    #print "NAKEDNUMDOT"
    #print marker_observations["NAKEDNUMDOT"]
    
    min_markers = float(n_lines-2)/6.0
    #print "n_lines"
    #print n_lines
    #print "min_markers"
    #print min_markers
    #print "Proste nechapu"
    #print marker_observations[sorted_observations[0]]
    if float(marker_observations[sorted_observations[0]]) >= min_markers:
        marker_type = sorted_observations[0]
    
    #print "MARKER TYPE!!!\n", marker_type
    return marker_type

# Segments citations that have explicit markers in the
# reference section.  Whenever a new line starts with an
# expression that matches what we'd expect of a marker,
# a new citation is started.  Returns a reference to a
# list of citation objects.
def SplitCitationsByMarker(rcite_text, marker_type):
    
    citations = []
    current_citation = Citation.Citation()
    current_citation_string = ""
    
    for line in re.split("\n", rcite_text):
        if re.search(r"^\s*(" + marker_types[marker_type] + ")\s*(.*)$", line) != None:
            tmpStr = re.search(r"^\s*(" + marker_types[marker_type] + ")\s*(.*)$", line)
            marker = tmpStr.group(1)
            cite_string = tmpStr.group(2)
            
            if current_citation_string:
                current_citation.setString(current_citation_string)
                citations.append(current_citation)
                
            current_citation = Citation.Citation()
            current_citation.setMarkerType(marker_type)
            current_citation.setMarker(marker)
            current_citation_string = cite_string
        else:
            if current_citation_string and re.search(r"[A-Za-z]-$", current_citation_string) != None:
                current_citation_string = re.sub(r"-$", "", current_citation_string)
                current_citation_string += line
            else:
                if not current_citation_string or re.search(r"[A-Za-z]-$", current_citation_string) != None:
                    current_citation_string += " "
                current_citation_string += line
    
    #Last citation
    if current_citation and current_citation_string:
        current_citation.setString(current_citation_string)
        citations.append(current_citation)
        
    # Now, we have an array of separated citations
    return citations

def SplitUnmarkedCitations(rcite_text):
    #print rcite_text
    rcite_text = re.sub(r"\n\d+$", "\n", rcite_text)
    content = rcite_text.split("\n")
    
    cite_start = 0
    cite_starts = []
    citations = []
    
    last_author_line = ""
    
    for i in range(0, len(content)):
        #print content[i].encode("utf-8")
        if re.search(r"\b\(?[1-2][0-9]{3}[a-z}]?[\)?\s,\.]*(\s|\b)", content[i], re.S):
            #tady si nejsem jisty, ma to byt k > cite_start, k--
            for k in range (i, cite_start, -1):
                #print "RANGE"
                #print i
                #print cite_start
                if re.finditer(r"\s*[A-Z]", content[k]) != None:
                    if last_author_line == k - 1:
                        #print last_author_line, k
                        continue
                    
                    if len(content[k-1]) < 2:
                        #print len(content[k-1])
                        cite_start = k
                        break
                    
                    beginning_author_line = -1
                    
                    for j in range(k -1, cite_start,  -1):
                        if re.search(r"\d", content[j]):
                            break
                        
                        #n_sep = 0
                        #while re.finditer(r"[,;]", content[j]) != None:
                        #    n_sep += 1
                        #print "IN!!!!"
                        #print content[j].encode("utf-8")
                        tmpContent = content[j]
                        n_sep = re.subn(r"(?P<tmp>[,;])", "\g<tmp>", tmpContent)
                        n_sep = n_sep[1]
                        #print "OUT!!!!"
                        #print n_sep
                        
                        if n_sep >= 3:
                            if re.search(r"\.\s*$", content[j - 1]) != None or j == 0:
                                beginning_author_line = j
                        else:
                            break
                    
                    if beginning_author_line >= 0:
                        cite_start = beginning_author_line
                        last_author_line = beginning_author_line
                        break
                    
                    if re.search(r"[^\.].\.\s*$", content[k - 1]) != None and re.search(r"^\d\d\d\d", content[k]) == None:
                        cite_start = k
                        break
            #print content[i].encode("utf-8")
            #if cite_starts != []:
                #print cite_starts
                #print "CITE START!!!\n", cite_starts[len(cite_starts)-1]
            if not((cite_starts != [] and cite_start <= cite_starts[len(cite_starts)-1]) and cite_start != 0):
                #print cite_start
                cite_starts.append(cite_start)
    
    for k in range(0, len(cite_starts)):
        #print "cite_starts!!!"
        #print cite_starts[k]
        first_line = cite_starts[k]
        last_line = len(content)-1 if k == len(cite_starts)-1 else cite_starts[k + 1] - 1
        #print first_line
        #print last_line
        
        tmpArray = []
        #for index in range(first_line, last_line)
        for index in range(first_line, last_line+1):
            tmpArray.append(content[index])
        #tmpArray.append(content[index])
        cite_string = MergeLines("\n".join(tmpArray))
        
        citation = Citation.Citation()
        citation.setString(cite_string)
        citations.append(citation)
    
    return citations

def Trim(text):
    text = re.sub(r"^\s+", "", text)
    text = re.sub(r"\s+$", "", text)
    return text
    
def MergeLines(text):
    
    #print "TEXT!!!\n", text.encode("utf-8")
    lines = text.split("\n")
    merged_text = ""
    
    for line in lines:
        line = Trim(line)
        
        if re.search(r"[A-Za-z]-$", merged_text) != None:
            merged_text = re.sub(r"-$", "", merged_text, 1)
            merged_text  += line
        else:
            if re.search(r"-\s*$", merged_text) == None:
                merged_text += " "
            merged_text += line
    
    #print merged_text
    return Trim(merged_text)

# Controls the process by which citations are segmented, based 
# on the result of trying to guess the type of citation marker 
# used in the reference section.  Returns a reference to a list 
# of citation objects.
def SegmentCitations(rcite_text):
    
    marker_type = GuessMarkerType(rcite_text)
    print "MARKER_TYPE"
    print marker_type
    print "RCITE_TEXT"
    print rcite_text
    rcitations = ""
    if marker_type != "UNKNOWN":
        rcitations = SplitCitationsByMarker(rcite_text, marker_type)
    else:
        rcitations = SplitUnmarkedCitations(rcite_text)
        #print "rcitations"
        #print rcitations
    
    return rcitations
