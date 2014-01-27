import sys
import re
import os
import codecs

###
# Utilities for normalizing the output of CRF++ into standard
# representations.
###

def GenerateCitInput(in_file):
    
    cit_lines = []
    line_index = 0
    all_text = ""
    
    #this file is the output from CRF++ for sectlabel
    try:
        in_file_fd = codecs.open(in_file, 'r', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + in_file)
        sys.exit(1)
    
    tmp = in_file_fd.readline()
    while tmp:
        # Overall confidence line, do not care about this
        if re.match(r"\# [\.\d]+", tmp) != None:
            continue
        
        #Remove end of line and blank line
        tmp = re.sub(r"\n", "", tmp)
        line = tmp
        line = re.sub(r"^\s+|\s+$", tmp)
        if line:
            continue
        
        #split the line, the last token is the category provide by sectlabel
        tokens = line.split("\t")
        #A line's category
        sys_prom = tokens[-1]
        
        #process confidence info in the format e.g., sectionHeader/0.989046
        if re.match(r"(.+)\/([\d\.]+)$", sys_prom) != None:
            tmpStr = re.match(r"(.+)\/([\d\.]+)$", sys_prom)
            sys_prom = tmpStr.group(0)
        else:
            sys.stderr.write("GenerateCitInput() : incorrect format\n")
            sys.exit(1)
            
        #Only keep lines in the reference for parscit
        if sys_prom == "reference":
            cit_lines.append(line_index)
            
        content = tokens[0]
        #Train at line level, get the original line
        tokens = content.split("\|\|\|")
        content = " ".join(tokens)
        
        #save the line
        all_text = all_text + content + "\n"
        
        #point to the next line
        line_index += 1
        tmp = in_file_fd.readline()
        
    in_file_fd.close()
    
    #Done
    retArray = []
    retArray.append(all_text)
    retArray.append(cit_lines)
    
def GenerateAuthorAffiliation(in_file):
    
    aut_lines = []
    aff_lines = []
    line_index = 0
    
    #This file is the output from CRF++ for  sectlabel
    try:
        in_file_fd = codecs.open(in_file, 'r', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + in_file)
        sys.exit(1)
    
    tmp = in_file_fd.readline()
    while tmp:
        # Overall confidence line, do not care about this
        if re.match(r"\# [\.\d]+", tmp) != None:
            tmp = in_file_fd.readline()
            continue
        
        #Remove end of line and blank line
        tmp = re.sub(r"\n", "", tmp)
        line = tmp
        line = re.sub(r"^\s+|\s+$", "", tmp)
        if not line:
            tmp = in_file_fd.readline()
            continue
        
        #split the line, the last token is the category provide by sectlabel
        tokens = line.split("\t")
        #A line's category
        sys_prom = tokens[-1]
        
        #process confidence info in the format e.g., sectionHeader/0.989046
        #print "SYS_PROM!!!!"
        #print sys_prom
        if re.match(r"(.+)\/([\d\.]+)$", sys_prom) != None:
            tmpStr = re.match(r"(.+)\/", sys_prom)
            sys_prom = tmpStr.group(0)
            sys_prom = re.sub(r"\/", "", sys_prom)
            #print sys_prom
        else:
            sys.stderr.write("GenerateAuthorAffiliation() : incorrect format\n")
            sys.exit(1)
        
        #Only keep lines in the reference for parscit
        if sys_prom == "author":
            aut_lines.append(line_index)
        elif sys_prom == "affiliation":
            aff_lines.append(line_index)
            
        #point to the next line
        line_index += 1
        tmp = in_file_fd.readline()
        
    in_file_fd.close()
    
    #Done
    retArray = []
    retArray.append(aut_lines)
    retArray.append(aff_lines)
    #print aut_lines
    #print aff_lines
    return retArray

def NormalizeDocumentField(tag, content, isEscape):
    #Remove trailing spaces
    content = re.sub(r"\s+$", "", content, 1)
    
    #Escape XML characters
    if isEscape:
        #content = re.sub(u"[^\x20-\x7f]+",u"",content)
        content = re.sub("\|\|\|", " ", content)
    
    retArray = []
    retArray.append(tag)
    retArray.append(content)
    return retArray

def WrapDocument(in_file,  blank_lines,  is_token_level):
    
    msg = ""
    xml = ""
    status = 1
    variant = ""
    confidence = "1.0"
    
    #vystupni XML
    fields = []
    cur_content = []
    
    try:
        in_file_fd = codecs.open(in_file, 'r', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + in_file)
        sys.exit(1)
        
    line_id = -1
    
    tmp = in_file_fd.readline()
    while tmp:
        #overall confidence info
        if re.match(r"\# [\.\d]+", tmp) != None:
            continue
            
        line_id += 1
        while(blank_lines.has_key(line_id) and blank_lines[line_id]):
            sys.stderr.write("#! Insert none label for line id "+line_id+"\n")
            xml += "none\n"
            line_id += 1
            
        if re.match(r"\s*$", tmp) != None:
            line_id = -1
        #in a middle of a document
        else:
            tokens = tmp.split("\t")
            line = tokens[0]
            sys_prom = tokens[-1]
            gold = tokens[-2]
            
            #train at line level, get the original line
            tokens = line.split("\|\|\|")
            line = " ".join(tokens)
            
            #process confidence info in the format e.g, sectionHeader/0.989046
            if re.match(r".+\/[\d\.]+$", sys_prom) != None: 
                tmpStr = re.match(r"(.+)\/[\d\.]+$", sys_prom)
                sys_prom = tmpStr.group(0)
            else:
                sys.stderr.write("wrapDocument(): incorrect format")
                sys.exit(1)
                
            retArray = []
            retArray = NormalizeDocumentField(sys_prom, line, 0)
            sys_prom = retArray[0]
            line = retArray[1]
            xml += sys_prom+line+"\n"
            
        tmp = in_file_fd.readline()    
        
    in_file_fd.close()
    return xml

def GenerateOutput(fields):
    
    output = ""
    for index in range(len(fields)):
        tag = fields[index]["tag"]
        content = fields[index]["content"]
        conf_str = "confidence=\""+str(fields[index]["confidence"])+"\""
        
        if re.search(r"^\s*$", content) != None:
            continue
            
        retArray = []
        retArray = NormalizeDocumentField(tag, content, 1)
        tag = retArray[0]
        content = retArray[1]
        
        output += "<" + tag + " " + conf_str + ">\n" + content + "\n</" + tag + ">\n"
    
    return output

#to add per-field info
def AddFieldInfo(fields, last_tag, cur_content, cur_confidence, count):
    
    tmp_hash = {}
    tmp_hash["tag"] = last_tag
    tmp_hash["content"] = cur_content
    
    #confidence info
    if count > 0:
        tmp_hash["confidence"] = cur_confidence/count
        
    fields.append(tmp_hash)

###
# Main method for processing document data. Specifically, it reads CRF output, performs normalization to individual fields, and outputs to XML
###
def WrapDocumentXml(in_file, section_headers):
    
    status = 1
    doc_count = 0
    msg = ""
    xml = ""
    variant = ""
    last_tag = ""
    
    overall_confidence = "1.0"
    #for lines of the same label
    cur_confidence = 0
    #count the number of lines in the current same label
    count = 0
    
    #output XML file for display
    xml += "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    
    # Array of hash: each element of fields correspond to a pairs of (tag, content) 
    # accessible through fields[i]["tag"] and fields[i]["content"]
    fields = []
    cur_content = ""
    
    try:
        in_file_fd = codecs.open(in_file, 'r', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + in_file)
        sys.exit(1)
        
    line_id = -1
    
    tmp = in_file_fd.readline()
    while tmp:
        #overall confidence info
        if re.match(r"\# [\.\d]+", tmp) != None:
            tmpStr = re.match(r"\# ([\.\d]+)",tmp)
            overall_confidence = tmpStr.group(0)
            tmp = in_file_fd.readline()
            continue
            
        #end of sentence, output (useful to handle multiple document classification
        #predpokladam, ze to nebude potreba
        if re.match(r"\s*$", tmp):
            #add the last field
            AddFieldInfo(fields, last_tag, cur_content, cur_confidence, count)
            
            if variant == "":
                #Benerate XML output
                output = GenerateOutput(fields)
                #print "OUTPUT!!!"
                #print output.encode("utf-8")
                l_algName = "LSR"
                l_algVersion = "0.1"
                #v pripade potreby dodelat
                xml += "<algorithm name=\"LSRLabel\">\n"
                xml += output
                xml += "</algorithm>"
                
            doc_count += 1
            
            fields = []
            last_tag = ""
            line_id = -1
        else:
            tokens = tmp.split("\t")
            line_id += 1
            
            line = tokens[0]
            sys_prom = tokens[-1]
            gold = tokens[-2]
            
            #for this line
            confidence = 0
            
            #train at line level, get the original line
            tokens = line.split("\|\|\|")
            line = " ".join(tokens)
            
            #process confidence info in the format e.g., sectionHeader/0.989046
            if re.match(r".+\/[\d\.]+$",  sys_prom):
                tmp_sys_prom = sys_prom
                #tmpStr = re.match(r"(.+)\/([\d\.]+)$",  sys_prom)
                tmpStr = re.match(r"(.+)\/", sys_prom)
                sys_prom = tmpStr.group(0)
                sys_prom = re.sub(r"\/$", "", sys_prom)
                #sys_prom = tmpStr.group(0)
                tmpStr = re.search(r"[\d\.]+$",  tmp_sys_prom)
                #print tmpStr.group(0)
                confidence += float(tmpStr.group(0))
            else:
                sys.stderr.write("wrapDocumentXml() : incorrect format\n")
                sys.exit(1)
                
            #start a new tag, not an initial value, output
            if sys_prom != last_tag and last_tag != "":
                #@returns fields
                AddFieldInfo(fields, last_tag, cur_content, cur_confidence, count)
                
                #reset the value
                cur_content = ""
                cur_confidence = 0
                count = 0
                
            #store section headers to classify generic sections later
            if sys_prom == "sectionHeader":
                section_headers["header"].append(line)
                section_headers["lineId"].append(line_id)
                
            cur_content += line+"\n"
            cur_confidence += confidence
            
            count += 1
            #update last_tag
            last_tag = sys_prom
        
        tmp = in_file_fd.readline()
        
    in_file_fd.close()
    return xml
    
