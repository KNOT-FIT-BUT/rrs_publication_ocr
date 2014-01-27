import re
import os
import sys
import codecs

def FindHeaderText(lines, start_id, num_lines):
    if start_id >= num_lines:
        sys.stderr.write("LSRlabel::PreProcess::FindHeaderText - start_id zacina dal nez je pocet radku textu!!!\n")
        sys.exit(0)
    
    body_start_id = start_id
    for body_start_id in range(num_lines):
        if re.search(r"^(.*?)\b(Abstract|ABSTRACT|Introductions?|INTRODUCTIONS?)\b(.*?):?\s*$", lines[body_start_id]) != None:
            #There are trailing text after the word introduction
            tokens = re.search(r"^(.*?)\b(Abstract|ABSTRACT|Introductions?|INTRODUCTIONS?)\b(.*?):?\s*$", lines[body_start_id]).group(3)
            if CountTokens(tokens) > 0:
                #INTRODUCTIONS AND BACKGROUND
                if re.search(r"background", tokens, re.I) != None:
                    break
                else:
                    break
    
    header_length = body_start_id - start_id
    body_length = num_lines - body_start_id
    
    if float(header_length) >= 0.8*float(body_length):
        sys.stderr.write("Header text longer than 80% article body length: ignoring\n")
        
        body_start_id = start_id
        header_length = 0
        body_length = num_lines - body_start_id
    
    if header_length == 0:
        sys.stderr.write("Warning: no header text found\n")
    retArray= []
    retArray.append(header_length)
    retArray.append(body_length)
    retArray.append(body_start_id)
    return retArray

def CountTokens(text):
    text = re.sub(r"^\s+", "", text)
    text = re.sub(r"\s+$", "", text)
    tokens = re.split(r"\s+", text)
    
    return len(tokens)
