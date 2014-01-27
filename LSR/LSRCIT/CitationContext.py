import os
import sys
import re
import codecs

context_radius = 200
max_contexts = 5

#pravdepodobne nebude treba, protoze modul re ma na to sve fce
def MakeSafe(marker):
    
    if not marker:
        return ""
    
    marker = re.sub(r"\\", "\\\\", marker)
    marker = re.sub(r"-", "\\-", marker)
    #marker = re.sub(r)

def GuessPossibleMarkers(marker):
    
    print "MARKER"
    print marker
    if re.search(r"^([\[\(])([A-Za-z-\d]+)([\]\)])", marker) != None:
        tmpStr = re.search(r"^([\[\(])([A-Za-z-\d]+)([\]\)])", marker)
        #print "JJJ"
        #open = MakeSafe(tmpStr.group(1))
        #mark = MakeSafe(tmpStr.group(2))
        #close = MakeSafe(tmpStr.group(3))
        open = tmpStr.group(1)
        mark = tmpStr.group(2)
        close = tmpStr.group(3)
        
        #ref_indicator = re.escape(open+"([A-Za-z-\d]+[;,] *)*"+mark+"([;,] *[A-Za-z-\d]+)*"+close)
        ref_indicator = re.escape(open) + "([A-Za-z\-\d]+[;,] *)*" + mark + "([;,] *[A-Za-z\-\d]+)*" + re.escape(close)
        #print ref_indicator
        retArray = []
        retArray.append(0)
        retArray.append(ref_indicator)
        return retArray
        
    if re.search(r"^(\d+)\.?", marker) != None:
        #print "JO zde"
        tmpStr = re.search(r"^(\d+)\.?", marker)
        square = "\\[(\\d+[,;] *)*" + tmpStr.group(1)+"([;,] *\\d+)*\\]"
        paren = "\\((\\d+[,;] *)*" + tmpStr.group(1)+"([;,] *\\d+)*\\)"
        #print square
        #print paren
        retArray = []
        retArray.append(1)
        retArray.append(square)
        retArray.append(paren)
        return retArray
        
    if re.search(r"^([A-Za-z-\.\']+(, )*)+\d{4}", marker) != None:
        tokens = re.split(r", ", marker)
        year = tokens[-1]
        names = tokens[0:-1]
        #print "NAMES!!!"
        #print names
        possible_markers = []
        
        if len(names)-1 == 0:
            possible_markers.append(names[0]+",? \\(?"+year+"\\)?")
        
        if len(names)-1 == 1:
            possible_markers.append(names[0]+" and "+names[1]+",? \\(?"+year+"\\)?")
            possible_markers.append(names[0]+" & "+names[1]+",? \\(?"+year+"\\)?")
            
        if len(names)-1 > 1:
            for item in names:
                item += ","
            
            last_auth1 = " and "+names[-1]
            last_auth2 = " & "+names[-1]
            
            tmpRet = " ".join(names[0:-1]) + last_auth1 + " " + year
            possible_markers.append(tmpRet)
            tmpRet = " ".join(names[0:-1]) + last_auth2 + " " + year
            possible_markers.append(tmpRet)
            
            possible_markers.append(names[0]+"? et al\\\.?,? \\(?"+year+"\\)?")
            
        retArray = []
        retArray.append(0)
        retArray.append(possible_markers)
        #print "MARKERS"
        #print possible_markers
        return retArray
    #print "TISK TOTO!!"
    retArray = []
    retArray.append(re.escape(marker))
    return retArray

def CountTokens(text):
    
    trim_text = text
    trim_text = re.sub(r"^\s+", "", trim_text)
    trim_text = re.sub(r"\s+$", "", trim_text)
    
    tokens = re.split(r"\s+", trim_text)
    return len(tokens)

def GetCitationContext(rbody_text, pos_array, marker):
    
    #print marker
    retArray = []
    markers = []
    retArray = GuessPossibleMarkers(marker)
    print "LEN!!!!"
    print len(retArray)
    if len(retArray) > 1:
        prioritize = retArray[0]
        if len(retArray) == 2:
            if type(retArray[1]) == type(list()):
                markers = retArray[1]
            else:
                markers.append(retArray[1])
        else:
            markers.append(retArray[1])
            markers.append(retArray[2])
        #print "Markers ret"
        #print markers
    else:
        if type(retArray[0]) == type(list()):
            markers = retArray[0]
        else:
            markers.append(retArray[0])
        prioritize = ""
    #print "MARKERS!!!"
    #print marker
    #print markers
    
    matches = []
    cit_strs = []
    start_word_positions = []
    end_word_positions = []
    
    positions = []
    position = ""
    contexts_found = 0
    
    for mark in markers:
        tmpRbodyText = rbody_text
        #print mark
        #print tmpRbodyText
        #print "Content_radius"
        #print context_radius
        print "Mark"
        print mark
        sys.exit(0)
        while (contexts_found < max_contexts) and re.search(r"(.{"+str(context_radius)+"}("+str(mark)+").{"+str(context_radius)+"})", tmpRbodyText, re.S):
            tmpStr = re.search(r"(.{"+str(context_radius)+"}("+mark+").{"+str(context_radius)+"})", tmpRbodyText, re.S)
            #tmpRbodyText = re.sub(r"(.{"+str(context_radius)+"}("+mark+").{"+str(context_radius)+"})", "", tmpRbodyText, re.S)
            cit_str = tmpStr.group(2)
            cit_length = CountTokens(cit_str)
            
            if cit_length == 0:
                continue
            
            #print "VYSL"
            #print tmpStr.group(1).encode("utf-8")
            #print tmpRbodyText.index(tmpStr.group(1))
            positions.append((tmpRbodyText.index(tmpStr.group(1))-context_radius))
            matches.append(tmpStr.group(1))
            
            before_mark = tmpRbodyText[0:tmpRbodyText.index(tmpStr.group(1))-context_radius-len(cit_str)]
            before_length = CountTokens(before_mark)
            
            if re.search(r" $", before_mark) != None or re.search(r"^ ", cit_str) != None:
                start_word_positions.append(before_length)
                end_word_positions.append(before_length+cit_length-1)
            else:
                start_word_positions.append(before_length-1)
                end_word_positions.append(before_length-1+cit_length-1)
            
            if re.search(r"\(.+\)$", cit_str) == None and re.search(r"\)$", cit_str) != None:
                cit_str = re.sub(r"\)$","", cit_str)
            cit_strs.append(cit_str)
            
            contexts_found += 1
            tmpRbodyText = re.sub(re.escape(tmpStr.group(1)), "", tmpRbodyText, re.S)
        
        if prioritize > 0 and len(matches)-1 >= 0:
            break
    
    retArray = []
    retArray.append(matches)
    retArray.append(positions)
    retArray.append(start_word_positions)
    retArray.append(end_word_positions)
    retArray.append(cit_strs)
    return retArray
