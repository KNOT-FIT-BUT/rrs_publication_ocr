import sys
import os
import re
import codecs
import string

# Main method for processing header data. Specifically, it reads CRF
# output, performs normalization to individual fields, and outputs to
# XML
def wrapHeaderXml(infile, conf_info,  is_token_level):
    
    status = 1
    msg = ""
    xml = ""
    variant = ""
    last_tag = ""
    
    overall_confidence = "1.0"
    
    #output XML file for display
    xml += "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    
    fields = []
    count = 0
    cur_content = ""
    cur_confidence = 0
    
    try:
        infile_fd = codecs.open(infile, 'r', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + infile)
        sys.exit(1)
    
    #print "INFILE!!!!"
    #print infile
    tmp = infile_fd.readline()
    while tmp:
        #overall confidence info
        if re.match(r"\# [\.\d]+", tmp) != None:
            tmpStr = re.search(r"\# ([\.\d]+)",tmp)
            overall_confidence = tmpStr.group(1)
            #print "Confidence!!!"
            #print overall_confidence
            tmp = infile_fd.readline()
            continue
        elif re.match(r"\#", tmp) != None:
            tmp = infile_fd.readline()
            continue
        
        #end of sentence, output (useful to handle multiple document classification
        #predpokladam, ze to nebude potreba
        if re.match(r"\s*$", tmp):
            #add the last field
            AddFieldInfo(fields, last_tag, cur_content, cur_confidence, count)
            #print "FIELDS!!!"
            #print fields
            if variant == "":
                #Benerate XML output
                output = GenerateOutput(fields, conf_info)
                #print "OUTPUT1!!!!"
                #print output
                l_algName = "LSR"
                l_algVersion = "0.1"
                #v pripade potreby dodelat
                xml += "<algorithm name=\"LSRHED\">\n"
                xml += output
                xml += "</algorithm>"
            fields = []
            last_tag = ""
        else:
            tokens = tmp.split("\t")
            #print "JJ"
            #print tokens
            token = tokens[0]
            sys_prom = tokens[-1]
            gold = tokens[-2]
            confidence = 0
            
            if not is_token_level:
                tokens = token.split("\|\|\|")
                token = " ".join(tokens)
                
                if conf_info:
                    if re.match(r".+\/[\d\.]+$",  sys_prom):
                        tmpStr = re.match(r"(.+)\/([\d\.]+)$",  sys_prom)
                        sys_prom = tmpStr.group(1)
                        confidence += float(tmpStr.group(2))
                    else:
                        sys.stderr.write("wrapDocumentXml() : incorrect format\n")
                        sys.exit(1)
                        
            
            if sys_prom != last_tag and last_tag != "":
                #@returns fields
                AddFieldInfo(fields, last_tag, cur_content, cur_confidence, count)
                
                #reset the value
                cur_content = ""
                cur_confidence = 0
                count = 0
                
            if is_token_level and token == "+L+":
                tmp = infile_fd.readline()
                continue
            
            cur_content += token + " "
            cur_confidence +=confidence
            count += 1
            
            last_tag = sys_prom
            
        tmp = infile_fd.readline()
        
    infile_fd.close()
    return xml

#to add per-field info
def AddFieldInfo(fields, last_tag, cur_content, cur_confidence, count):
    
    tmp_hash = {}
    tmp_hash["tag"] = last_tag
    tmp_hash["content"] = cur_content
    
    #confidence info
    if count > 0:
        tmp_hash["confidence"] = cur_confidence/count
        
    fields.append(tmp_hash)
    
def GenerateOutput(fields, conf_info):
    #print fields
    output = ""
    
    for index in range(len(fields)):
        tag = fields[index]["tag"]
        content = fields[index]["content"]
        #print "TAG!!!"
        #print tag.encode("utf-8")
        #print "CONTENT"
        #print content.encode("utf-8")
        
        conf_str = ""
        if conf_info:
            conf_str = " confidence=\"" + str(fields[index]["confidence"]) + "\""
            
        if re.search(r"^\s*$", content) != None:
            continue
        
        #print "IN!!!!"
        #print tag.encode("utf-8")
        #print content.encode("utf-8")
        retArray = []
        retArray = NormalizeHeaderField(tag, content)
        #print "RETARRAY"
        #print retArray
        tag = retArray[0]
        content = retArray[1]
        #print "OUT!!!!"
        #print content
        
        if tag == "authors":
            #for index in range(len(content)):
            #    author = content[index]
            #    content = re.sub(u"[^\x20-\x7f]+",u"",author)
            #    output += "<author" + conf_str + ">" +author + "</author>\n"
            for author in content:
                #author = re.sub(u"[^\x20-\x7f]+",u"",author)
                #if not author:
                #    continue
                output += "<author" + conf_str + ">" +author + "</author>\n"
        elif tag == "emails":
            for index in range(len(content)):
                email = content[index]
                output += "<email" + conf_str + ">" + email + "</email>\n"
        else:
            #print content
            #print tag
            output += "<" + tag + conf_str + ">" + content + "</" + tag + ">\n"
            
    return output
    
def NormalizeHeaderField(tag, content):
    
    sys.path.append("./LSRCIT/")
    import PostProcessCIT
    #Remove keyword at the beginning
    regexp = "^\W*" + tag + "\W+"
    content = re.sub(re.escape(regexp), "", content, re.I)
    #strip leading spaces
    content = re.sub(r"^\s+", "", content)
    #strip trailing spaces
    content = re.sub(r"\s+$", "", content)
    #print "CONTENT IN!!!!"
    #print content
    #unhyphenate
    content = re.sub(r"\|\|\|", " ", content)
    #print "CONTENT!!!!"
    #print content.encode("utf-8")
    #print "CONTENT OUT!!!"
    #print content
    #while re.search(r"\- ([a-z])", content) != None:
    #    tmpStr = re.search(r"\- ([a-z])", content)
    #    content = re.sub(r"\- ([a-z])", tmpStr.group(0), content, 1)
    #print tag
    
    #Normalize author and break into multiple authors (if any)
    if tag == "author":
        tag = "authors"
        content = re.sub(r"\d", "", content)
        tmpCon = []
        tmpCon.append(content)
        content = tmpCon
        # pozor, neni zatim implementovano!!!!!
        #print content
        #content = PostProcessCIT.NormalizeAuthorNames(content)
        #content = re.split(r"(,\s+)", content)
        #print content
        #print "-------------"
    elif tag == "email":
        # Multiple emails of the form {kanmy,luongmin}@nus.edu.sg
        #tmpCon = []
        #tmpCon.append(content)
        #content = tmpCon
        #tag = "emails"
        
        if re.search(r"^\{(.+)\}(.+)$",  content) != None:
            tmpStr = re.search(r"^\{(.+)\}(.+)$",  content)
            begin = tmpStr.group(1)
            end = tmpStr.group(2)
            separator = ","
            
            # Find possible separator of emails, beside ","
            separators = []
            tmpBeg = begin
            while re.search(r"\s+(\S)\s+", tmpBeg) != None:
                tmpStr = re.search(r"\s+(\S)\s+", tmpBeg)
                separators.append(tmpStr.group(1))
                tmpBeg = re.sub(r"\s+(\S)\s+", "", tmpBeg, 1)
                
            if len(separators) > 1:
                cand = separators[0]
                flag = 1
                for index in range(len(separators)):
                    #should be the same
                    if separators[index] != cand:
                        flag = 0
                        break
                        
                # All separator are the same, and the number of separator > 1, update separator
                if flag == 1:
                    separator = cand
            
            tokens = begin.split(separator)
            
            #Remove all white spaces
            end = re.sub(r"\s+", "", end)
            
            #There are actually multiple emails
            if len(tokens) > 1:
                emails = []
                
                for token in tokens:
                    #Remove all white spaces
                    token = re.sub(r"\s+", "", token)
                    emails.append(token + end)
                    
                tag = "emails"
                content = emails
        else:
            #Remove all white spaces
            content = re.sub(r"\s*", "", content)
        
        
    #else:
        #Escape XML characters
        #print "IN!!!"
        #print content
        #content = re.sub(u"[^\x20-\x7f]+",u"",content)
        #content = PostProcessCIT.StripPunctation(content)
        #print "OUT!!!"
        #print content
        
    retArray = []
    retArray.append(tag)
    retArray.append(content)
    return retArray
    
