import Config
import Tr2crfpp
import PostProcess
import codecs
import os
import sys
import re

#debug mode
debug = 1
#zatim nevim, k cemu to slouzi
generic_sect_path = ""

#metoda pro generovani vystupniho XML dokumentu
def ExtractSection(text_file, is_xml_output, model_file, dict_file, func_file, config_file, is_rtf_input, for_cit):
    tmpArray = []
    if not for_cit:
        tmpArray = ExtractSectionImpl(text_file, is_xml_output, model_file, dict_file, func_file, config_file, is_rtf_input,  for_cit)
        retArray = []
        #!!!!Pamatovat si, ze kdyz dostanu pak pole o delce 1, je to chyba, ostatni OK!!!!
        status = int(tmpArray[0])
        if status > 0:
            retArray.append(tmpArray[2])
            retArray.append(tmpArray[3])
            retArray.append(tmpArray[4])
            return retArray
        else:
            retArray.append(tmpArray[1])
    else:
        tmpArray = ExtractSectionImpl(text_file, is_xml_output, model_file, dict_file, func_file, config_file, is_rtf_input,  for_cit)
        return tmpArray

###
# Thang v100401: method to get generic headers give a list of headers
###
def GetGenericHeaders(headers, generic_headers):
    
    #no header
    if not headers:
        return
        
    num_headers = len(headers)
    
    #put the list of headers to file
    header_file = "/tmp/header"
    generic_sect_path = "./LSRLabel/genericSectExtract.rb"
    try:
        header_file_fd = codecs.open(header_file, 'w', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + header_file)
        sys.exit(1)
        
    for i in range(0, num_headers):
        tmpHed = re.sub(r"\|\|\|", " ", headers[i])
        header_file_fd.write(tmpHed+"\n")
    
    header_file_fd.close()
    
    #get a list of generic headers
    cmd = generic_sect_path + " " + header_file + " " + header_file + ".out"
    os.system(cmd)
    sys.stderr.write("RUBY DONE\n")

    try:
        header_file_fd = codecs.open(header_file+".out", 'r', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + header_file)
        sys.exit(1)
        
    generic_count = 0
    tmp = header_file_fd.readline()
    while(tmp):
        generic_header = tmp
        
        #Temporarily add in, to be removed once Emma's code updated
        if generic_header == "related_works":
            generic_header = "related_work"
            
        generic_headers.append(generic_header)
        generic_count += 1
        tmp = header_file_fd.readline()
    
    header_file_fd.close()

    if num_headers != num_headers:
        sys.stderr.write("GetGenericHeaders() : different in number of headers")
        sys.exit(1)
        
    os.remove(header_file)
    os.remove(header_file+".out")

###
# Thang v100401: method to insert generic headers into previous label XML output (ids given for checking purpose)
###
def InsertGenericHeaders(xml, headers, generics, line_ids):
    
    lines = xml.split("\n")
    num_lines = len(lines)
    
    text_id = -1
    header_count = 0
    
    i = 0
    while i < num_lines:
        line = lines[i]

        #header line
        if re.match(r"<sectionHeader confidence=\"([\.\d]+)\">$", line) != None:
            tmpStr = re.search(r"([\.\d]+)", line)
            confidence = tmpStr.group(0)
            
            #header line
            i += 1
            line = lines[i]
        
            #sanity check
            #after increase, text_id is the current line id (base 0)
            text_id += 1
            if line_ids[header_count] != text_id:
                sys.stderr.write("InsertGenericHeaders() : different ids" + str(line_ids[header_count]) + "\n")
                sys.exit(1)
            
            generic_header = generics[header_count]
            generic_header = re.sub(r"\n", "", generic_header)
            lines[i-1] = "<sectionHeader confidence=\"" + confidence + "\" genericHeader=\"" + generic_header + "\">"
            #after increase, header_count is the number of header lines readline
            header_count += 1
        
            #Finish reading all header lines (incase of multiple line header)
            #A text line
            while re.match(r"<[\/\?]?[a-zA-Z]+", lines[i+1]) == None:
                i += 1
                header_count += 1
                text_id += 1
        
        #A text line
        elif re.match(r"<[\/\?]?[a-zA-Z]+", line) == None:
            text_id += 1
        
        i += 1
    return "\n".join(lines)

###
# Main script for actually walking through the steps of document processing.
# Returns a status code (0 for failure), an error message (may be blank if 
# no error), a reference to an XML document.
#
# is_token_level: flag to enable previous token-level model (for performance 
# comparison)
#
# TODO: catch errors and return status < 0
###
def ExtractSectionImpl(text_file, is_xml_output, model_file, dict_file, func_file, config_file, is_rtf_input, for_cit):
    status = 1
    msg = ""
    
    #seznam radku suroveho textu
    text_lines = []
    #hash tabulka prazdnych radku
    blank_lines = {}
    #citadlo radku
    line_id = -1
    
    #preskoceni prazdnych radku
    import StringIO
    
    buf = StringIO.StringIO(text_file)
    tmp = buf.readline()
    while(tmp):
        line_id += 1
        if re.search(r"^\s*$",  tmp) != None:
            blank_lines[line_id] = 1
            tmp = buf.readline()
            continue
        else:
            text_lines.append(tmp)
        
        tmp = buf.readline()
    
    #spusteni tr2crfpp
    tmp_file = ""
    tmp_file = Tr2crfpp.ExtractTestFeatures(text_lines, text_file, dict_file, func_file, config_file, debug)
    
    #run crf_test, output2xml
    out_file = tmp_file + "_dec"
    xml = ""
    if Tr2crfpp.Decode(tmp_file, model_file, out_file):
        
        section_headers = {}
        
        # Array of section headers
        section_headers["header"] = []
        
        # Array of corresponding line ids (0-based)
        section_headers["lineId"] = []
        
        #pravdepodobne se toto nevyuzije, ukladat se bude vzdy do XML
        if not is_xml_output:
            xml = PostProcess.WrapDocument(out_file, blank_lines)
        else:
            xml = PostProcess.WrapDocumentXml(out_file, section_headers)
            
            # Array of generic headers
            #section_headers["generic"] = []
            
            #GetGenericHeaders(section_headers["header"], section_headers["generic"])
            
            #xml = InsertGenericHeaders(xml, section_headers["header"], section_headers["generic"], section_headers["lineId"])
    else:
        sys.stderr.write("LSRLabel::Controller::Decode is false!\n")
        sys.exit(0)
    
    #provide input for parscit
    #nevyuzite, for_cit vzdy = 0
    if for_cit:
        retArray = []
        retArray = PostProcess.GenerateCitInput(out_file)
        all_text = retArray[0]
        cit_lines = retArray[1]
        
        os.remove(tmp_file)
        os.remove(out_file)
        
        retArray = []
        retArray.append(all_text)
        retArray.append(cit_lines)
        return retArray
    else:
        retArray = []
        retArray = PostProcess.GenerateAuthorAffiliation(out_file)
        aut_lines = retArray[0]
        aff_lines = retArray[1]
        
        os.remove(tmp_file)
        os.remove(out_file)
        
        retArray = []
        retArray.append(status)
        retArray.append(msg)
        retArray.append(xml)
        retArray.append(aut_lines)
        retArray.append(aff_lines)
        return retArray
    
