import os
import sys
import codecs
import re

def ChangeExtension(fn,  ext):
    
    fn = re.sub(r"\..*$", ".", fn)
    fn += ext
    return fn

def WriteSplit(textfile, rcite_text, rbody_text):
    
    citefile = ChangeExtension("raw_data", "cite")
    bodyfile = ChangeExtension("raw_data", "body")
    
    citefile_fd = ""
    try:
        citefile_fd = codecs.open(citefile, 'w', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + citefile)
        sys.exit(1)
    citefile_fd.write(rcite_text)
    citefile_fd.close()
    
    bodyfile_fd = ""
    try:
        bodyfile_fd = codecs.open(bodyfile, 'w', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + bodyfile)
        sys.exit(1)
    bodyfile_fd.write(rbody_text)
    bodyfile_fd.close()
    
    retArray = []
    retArray.append(citefile)
    retArray.append(bodyfile)
    return retArray

def BuildXMLResponse(rcitations):
    
    xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + "<algorithm name=\"LSRCIT\">\n"
    xml += "<citationList>\n"
    
    for citation in rcitations:
        xml += citation.toXML()
    
    xml += "</citationList>\n"
    xml += "</algorithm>\n"
    return xml

# Extract citations from text
def ExtractCitations(text_file,  org_file, is_xml):
    
    #real works are in there
    retArray = []
    retArray = ExtractCitationsImpl(text_file, org_file, is_xml, 0)
    status = retArray[0]
    msg = retArray[1]
    citations = retArray[2]
    body_text = retArray[3]
    
    #check the result status
    if status > 0:
        return BuildXMLResponse(citations)
    else:
        #return error message
        return "Error: " + msg
     

def ExtractCitationsImpl(textfile, orgfile, is_xml, bwrite_split):
    
    if not bwrite_split:
        bwrite_split = 1
        
    status = 1
    msg = ""
    
    #NOTE: What are their purpose?
    citefile = ""
    bodyfile = ""
    pos_array = []
    
    #Reference text, body text, and normalize body text
    rcite_text = ""
    rnorm_body_text = ""
    rbody_text = ""
    #Reference to an array of single reference
    rraw_citations = ""
    
    #Find and separate reference
    if is_xml:
        print "Under construction"
    else:
        sys.path.append("./LSRCIT/")
        import PreProcessCIT
        #textfile_fd = ""
        #try:
        #    textfile_fd = codecs.open(textfile, 'r', "utf-8")
        #except IOError:
        #    sys.stderr.write("Nelze otevrit soubor " + textfile)
        #    sys.exit(1)
        
        text = textfile
        
        retArray = []
        #print "IN!!!\n", text.encode("utf-8")
        retArray = PreProcessCIT.FindCitationText(text, pos_array)
        rcite_text = retArray[0]
        rnorm_body_text = retArray[1]
        rbody_text = retArray[2]
        
        rnorm_body_text = re.sub("\x0D\x0A", "\x0A", rnorm_body_text, re.S)
        #rnorm_body_text = re.sub("(\x0A)+", "\x0A", rnorm_body_text, re.S)
        norm_body_tokens = re.split("\s+", rnorm_body_text)
        #print "r_norm_body_text!!!\n", rnorm_body_text.encode("utf-8")
        body_tokens = re.split("\s+", rbody_text)
        #print norm_body_tokens
        tokToDel = []
        for index in range(len(norm_body_tokens)):
            if not norm_body_tokens[index]:
                tokToDel.append(index)
            
        for tokToDelItem in tokToDel:
            del norm_body_tokens[tokToDelItem]
        #print  "rbody_text!!!!\n", rbody_text.encode("utf-8")
        
        size = len(norm_body_tokens)
        size1 = len(pos_array)
        #print size
        #print size1
        #print "TEST!!!!"
        #print norm_body_tokens
        #print pos_array
        if size != size1:
            sys.stderr.write("ParsCit::Controller::extractCitationsImpl: normBodyText size " + str(size) + "!= posArray size "+ str(size1)+"\n")
            sys.exit(1)
            
        #Filename initialization
        if bwrite_split > 0:
            retArray = []
            retArray = WriteSplit(textfile, rcite_text, rbody_text)
            citefile = retArray[0]
            bodyfile = retArray[1]
          
        #print rcite_text.encode("utf-8")
        if rnorm_body_text:
            rraw_citations = PreProcessCIT.SegmentCitations(rcite_text)
        #print rraw_citations
    citations = []
    valid_citations = []
    
    #process each citation
    import Citation
    
    normalized_cite_text = ""
    for citation in rraw_citations:
        #Tr2crfpp needs an enclosing tag for initial class seed
        cite_string = citation.getString()
        #print cite_string.encode("utf-8")
        if cite_string and re.search(r"^\s*$", cite_string) == None:
            normalized_cite_text += "<title> " + citation.getString() + " </title>\n"
            citations.append(citation)
    
    #Stop - nothing left to do
    if not citations:
        retArray = []
        retArray.append(status)
        retArray.append(msg)
        retArray.append(valid_citations)
        retArray.append(rnorm_body_text)
        return retArray
        
    import Tr2crfppCIT
    tmpfile = Tr2crfppCIT.PrepData(normalized_cite_text, textfile)
    outfile = tmpfile + "_dec"
    
    if Tr2crfppCIT.Decode(tmpfile, outfile):
        import PostProcessCIT
        retArray = []
        retArray = PostProcessCIT.ReadAndNormalize(outfile)
        rraw_xml = retArray[0]
        rcite_info = retArray[1]
        status = retArray[2]
        tmsg = retArray[3]
        
        if status <= 0:
            retArray = []
            retArray.append(status)
            retArray.append(msg)
            retArray.append("")
            retArray.append("")
            return retArray
            
        cite_info = rcite_info
        if len(citations)-1 == len(cite_info)-1:
            for i in range(0, len(citations)):
                citation = citations[i]
                cite_info_tmp = {}
                cite_info_tmp = cite_info[i]
                
                for key in cite_info_tmp:
                    citation.loadDataItem(key, cite_info_tmp[key])
                    
                marker = citation.getMarker()
                if not marker:
                    marker = citation.buildAuthYearMarker()
                    citation.setMarker(marker)
                
                import CitationContext
                tmpArr = []
                tmpArr = CitationContext.GetCitationContext(rnorm_body_text, pos_array, marker)
                rcontexts = tmpArr[0]
                rpositions = tmpArr[1]
                start_word_positions = tmpArr[2]
                end_word_positions = tmpArr[3]
                rcit_strs = tmpArr[4]
                
                for context in rcontexts:
                    citation.addContext(context)
                    
                    position = rpositions[0]
                    del rpositions[0]
                    citation.addPosition(position)
                    
                    cit_str = rcit_strs[0]
                    del rcit_strs[0]
                    citation.addCitStr(cit_str)
                    
                    start_pos = start_word_positions[0]
                    del start_word_positions[0]
                    end_pos = end_word_positions[0]
                    del end_word_positions[0]
                    
                    citation.addStartWordPosition(pos_array[start_pos])
                    citation.addEndWordPosition(pos_array[end_pos])
                
                valid_citations.append(citation)
        else:
            status = -1
            msg = "Mismatch between expected citations and cite info"
    
    os.remove(tmpfile)
    os.remove(outfile)
    
    retArray = []
    retArray.append(status)
    retArray.append(msg)
    retArray.append(valid_citations)
    retArray.append(rbody_text)
    retArray.append(citefile)
    retArray.append(bodyfile)
    return retArray
