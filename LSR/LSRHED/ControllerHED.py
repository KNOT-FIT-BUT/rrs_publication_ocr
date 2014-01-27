import sys
import os
import re
import codecs

def extractHeader(text_file, is_token_level):
    
    conf_level = 1
    retArray = []
    retArray = extractHeaderImpl(text_file, is_token_level, conf_level)
    status = retArray[0]
    msg = retArray[1]
    xml = retArray[2]
    
    if status > 0:
        return xml
    else:
        return "Error: " + msg
        
def extractHeaderImpl(text_file, is_token_level, conf_level):
    
    status = 1
    msg = ""
    
    import StringIO
    #sys.stderr.write("ControllerHED::opravit\n")
    #print text_file
    #sys.exit(0)
    bufText = StringIO.StringIO(text_file)
    
    buf = ""
    tmp = bufText.readline()
    while(tmp):
        if re.search(r"^\#", tmp) != None:
            tmp = bufText.readline()
            continue
        elif re.search(r"^\s+$",  tmp) != None:
            tmp = bufText.readline()
            continue
        else:
            #sample RE for header stop
            if re.search(r"INTRODUCTION", tmp, re.I) != None:
                break
                
            if is_token_level:
                buf += tmp
                buf += " +L+ "
            else:
                buf += tmp+"\n"
                
        tmp = bufText.readline()
        
    #For compatible reason
    if is_token_level:
        buf = "<title> " + buf + " </title>\n"
        
    #Run tr2crfpp to prepare feature files
    sys.path.append("./LSRHED/")
    
    tmpfile = ""
    if is_token_level:
        import Tr2crfppHED_token
        tmpfile = Tr2crfppHED_token.prepData(buf, text_file)
    else:
        import Tr2crfppHED
        tmpfile = Tr2crfppHED.prepData(buf, text_file)
        
    xml = ""
    #run crf_test, output2xml
    outfile = tmpfile+"_out"
    
    import PostProcessHED
    if is_token_level:
        if Tr2crfppHED_token.decode(tmpfile, outfile):
            xml = PostProcessHED.wrapHeaderXml(outfile, 0, is_token_level)
    else:
        #print outfile
        #sys.exit(0)
        if Tr2crfppHED.decode(tmpfile, outfile, conf_level):
            xml = PostProcessHED.wrapHeaderXml(outfile, conf_level, "")
            #print "XML!!!"
            #print xml
          
    #sys.exit(1)
    os.remove(tmpfile)
    os.remove(outfile)
    retArray = []
    retArray.append(status)
    retArray.append(msg)
    retArray.append(xml)
    return retArray
