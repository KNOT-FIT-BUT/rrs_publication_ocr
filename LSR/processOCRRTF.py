#!/usr/bin/python

import sys
import re
import os
import codecs
import htmlentitydefs

out_file = ""
is_decode = 1
is_debug = 0
address = 1

#Mark page, para, line, word
g_page_hash = {}

#Mark paragraph
g_para = []

#RTF features
#Location feature
g_pos_hash = []
g_maxpos = 0
g_minpos = 1000000
#Align feature
g_align = []
#Bold feature
g_bold = []
#Italic feature
g_italic = []
#Pic feature
g_pic = []
#Table feature
g_table = []
#Bullet feature
g_bullet = []
#Font size feature
g_font_size_hash = {}
g_font_size = []
#Font face feature
g_font_face_hash = {}
g_font_face = []

#Find header part
header_length = 0
body_length = 0
body_start_id = 0

#All lines
lines = []
#and their address
lines_addr = []

obj_list = {"OMNIDOC":"document", 
                 "OMNIPAGE":"page", 
                 "OMNICOL":"column", 
                 "OMNIDD":"DD", 
                 "OMNITABLE":"table", 
                 "OMNIIMG":"image", 
                 "OMNIPARA":"paragraph", 
                 "OMNILINE":"line", 
                 "OMNIRUN":"run", 
                 "OMNIWORD":"word", 
                 "OMNIFRAME":"frame"}

#def ProcessFile(rtf, input):
def ProcessFile(xml, input):
    #print xml
    #sys.exit(0)
    xml = re.sub(r"<\?xml.+?>\n", "", xml, 1)
    xml = "<?xml version=\"1.0\"?>\n<root>\n" + xml + "\n</root>"
    
    sys.path.append("./LSRRTF/")
    import rtfDoc
    doc = rtfDoc.rtfDoc()
    doc.set_raw(xml)
    #print doc.get_content()
    #sys.exit(0)
    
    #current position
    current = {}
    
    #All pages in the document
    pages = doc.get_objs_ref()
    
    #From page, To page
    start_page = 0
    end_page = len(pages)
    
    #Image area flag
    is_pic = 0
    
    #Tree traveling is 'not' fun. Seriously.
    #This is like a dungeon seige.
    for x in range(start_page, end_page):
        #current position
        current["L1"] = x
        
        #Column or dd
        level_2 = pages[x].get_objs_ref()
        start_l2 = 0
        end_l2 = len(level_2) 
        
        for y in range(start_l2, end_l2):
            if level_2[y].get_name() == obj_list["OMNIDD"]:
                is_pic = 1
            else:
                is_pic = 0
        
            #current position
            current["L2"] = y
            
            #Table or paragraph
            level_3 = level_2[y].get_objs_ref()
            start_l3 = 0
            end_l3 = len(level_3) 
            
            for z in range(start_l3, end_l3):
                #current position
                current["L3"] = z
                
                #Is a paragraph
                if level_3[z].get_name() == obj_list["OMNIPARA"]:
                    ProcessPara(level_3[z], is_pic, current)
                #or a table
                elif level_3[z].get_name() == obj_list["OMNITABLE"]:
                    ProcessTable(level_3[z], is_pic, current, 0)
                elif level_3[z].get_name() == obj_list["OMNIFRAME"]:
                    #Frame contains multiple paragraph?
                    ProcessFrame(level_3[z], is_pic, current)
    
    return doc.get_content()

def ProcessTable(omnitable, is_pic, line_addr, lindex):
    global g_page_hash
    global g_para
    global g_pos_hash
    global g_maxpos
    global g_minpos
    global g_align
    global g_bold
    global g_italic
    global g_pic
    global g_table
    global g_bullet
    global g_font_size_hash
    global g_font_size
    global g_font_face_hash
    global g_font_face
    global lines
    global lines_addr
    
    # Table attributes
    left = ""
    top = ""
    right = ""
    bottom = ""
    
    left = omnitable.get_left_pos()
    right = omnitable.get_right_pos()
    top = omnitable.get_top_pos()
    bottom = omnitable.get_bottom_pos()
    # Table attributes
    align = omnitable.get_alignment()
    
    # Thang's code
    pos = float(top + bottom) / 2.0
    # Set new min and max position
    if pos < g_minpos:
        g_minpos = pos
    if pos > g_maxpos:
        g_maxpos = pos
    # End Thangs's code
    
    # All row in the table
    rows = omnitable.get_row_content()
    # For each row in the table
    for i in range(0, len(rows)):
        row_lines = re.split(r"\n", rows[i])
        # For each line in the row
        for j in range(0, len(row_lines)):
            # Save the line
            lines.append(row_lines[j])
            # Save the line's address
            tmpLineAddr = {}
            tmpLineAddr = line_addr.copy()
            tmpLineAddr["L4"] = lindex
            lines_addr.append(tmpLineAddr)
            # Point to the next line in the whole table
            lindex += 1
            
            if j == 0 and i == 0:
                g_para.append("yes")
            else:
                g_para.append("no")
            
            # Table feature
            g_table.append("yes")
            
            # Pic feature
            if is_pic:
                g_pic.append("yes")
            else:
                g_pic.append("no")
            
            # Update xml pos value
            g_pos_hash.append(pos)
            # Update xml alignment value
            g_align.append(align)
            
            # Fontsize feature
            g_font_size.append(-1)
            # Fontface feature
            g_font_face.append("none")
            # Bold feature
            g_bold.append("no")
            #Italic feature
            g_italic.append("no")
            # Bullet feature
            g_bullet.append("no")
    return lindex
    
def ProcessPara(paragraph, is_pic, line_addr):
    global g_page_hash
    global g_para
    global g_pos_hash
    global g_maxpos
    global g_minpos
    global g_align
    global g_bold
    global g_italic
    global g_pic
    global g_table
    global g_bullet
    global g_font_size_hash
    global g_font_size
    global g_font_face_hash
    global g_font_face
    global lines
    global lines_addr

    #Paragraph attributes
    align = paragraph.get_alignment()

    sys.stderr.write("doplnit do odstavce space before\n")
    space = paragraph.get_space_before()
    #Line attributes
    left = ""
    top = ""
    right = ""
    bottom = ""
    #Run attributes
    bold_count = 0
    italic_count = 0
    font_size_hash = {}
    font_face_hash = {}
    
    #Lines
    omnilines = paragraph.get_objs_ref()
    start_l = 0
    end_l = len(omnilines)
    
    #Lines
    for t in range(start_l, end_l):
        #Skip blank line
        lcontent = omnilines[t].get_content()
        lcontent = re.sub(r"^\s+|\s+$", "", lcontent)
        if not lcontent:
            continue
        
        #Save the line
        lines.append(omnilines[t].get_content())
        #Save the line's address
        tmpLineAddr = {}
        tmpLineAddr = line_addr.copy()
        #line_addr["L4"+str(t)] = t
        #lines_addr.append(line_addr)
        tmpLineAddr["L4"] = t
        lines_addr.append(tmpLineAddr)
        
        #Line attributes
        left = omnilines[t].get_left_pos()
        right = omnilines[t].get_right_pos()
        top = omnilines[t].get_top_pos()
        bottom = omnilines[t].get_bottom_pos()
        
        #Runs
        runs = omnilines[t].get_objs_ref()
        start_r = 0
        end_r = len(runs)-1
        
        #Total number of words in a line
        words_count = 0
        
        for u in range(start_r, end_r+1):
            rcontent = ""
            #Get run content
            rcontent = runs[u].get_content()
            #Trim
            rcontent = re.sub(r"^\s+|\s+$", "", rcontent)
            #Split to words
            words = re.split("\s+", rcontent)
            
            #Update the number of words
            words_count += len(words)
            
            #XML format
            font_size = int(runs[u].get_font_size())
            font_size_hash[int(font_size)] = font_size_hash[int(font_size)] + len(words) if font_size_hash.has_key(int(font_size)) else len(words)
            #XML format
            font_face = runs[u].get_font_face()
            font_face_hash[font_face] = font_face_hash[font_face] + len(words) if font_face_hash.has_key(font_face) else len(words)
            #XML format
            if runs[u].get_bold() == "true":
                bold_count += len(words)
            #XML format
            if runs[u].get_italic() == "true":
                italic_count += len(words)
        
        #Line attributes - relative position in paragraph
        if t == start_l:
            g_para.append("yes")
        else:
            g_para.append("no")
        
        #Line attributes - line position
        pos = int(top) + int(bottom)
        #Compare to global min and max position
        if pos < g_minpos:
            g_minpos = pos
        if pos > g_maxpos:
            g_maxpos = pos
        #Pos feature
        g_pos_hash.append(pos)
        #Alignment feature
        g_align.append(align)
        #Table feature
        g_table.append("no")
        
        if is_pic:
            g_pic.append("yes")
            #Not assign value if line in image area
            g_bold.append("no")
            g_italic.append("no")
            g_bullet.append("no")
            g_font_size.append(-1)
            g_font_face.append("none")
        else:
            g_pic.append("no")
            #print "font_size_hash"
            #print font_size_hash
            #print "font_face_hash"
            #print font_face_hash
            #sys.exit(0)
            UpdateXMLFontFeature(font_size_hash, font_face_hash)
            UpdateXmlFeatures(bold_count, italic_count, words_count, omnilines[t].get_bullet, space)
        
        #Reset hash
        font_size_hash = {}
        font_face_hash = {}
        #Reset
        bold_count = 0
        italic_count = 0

def UpdateXMLFontFeature(font_size_hash, font_face_hash):
    global g_font_size_hash
    global g_font_face_hash
    #Font size feature
    if len(font_size_hash) == 0:
        g_font_size.append(-1)
    else:
        #sortovani podle klice
        #sorted_fonts = [x for x in font_size_hash.iteritems()]
        #sorted_fonts.sort(key=lambda x: x[0])
        #sorted_fonts = sorted(font_size_hash.iteritems(), key=lambda (k,v): (v,k))
        #sorted(font_size_hash.iteritems(), key=lambda (k,v): (v,k))
        #print sorted_fonts
        sorted_fonts = sorted(font_size_hash.iteritems(), key=lambda (k,v):(v,k), reverse=True)
        #sorted_fonts = font_size_hash.items()
        #sorted_fonts.sort()
        #sorted_fonts.reverse()
        
        font_size = ""
        # If two font sizes are equal in number, get the larger one
        #print "font_size_hash"
        #print font_size_hash
        if len(sorted_fonts) != 1 and font_size_hash[int(sorted_fonts[0][0])] == font_size_hash[int(sorted_fonts[1][0])]:
            font_size = int(sorted_fonts[0][0]) if int(sorted_fonts[0][0]) > int(sorted_fonts[1][0]) else int(sorted_fonts[1][0])
        else:
            font_size = int(sorted_fonts[0][0])
        
        if not font_size:
            font_size = 0
        
        g_font_size.append(font_size)
        g_font_size_hash[int(font_size)] = g_font_size_hash[int(font_size)] +1 if g_font_size_hash.has_key(int(font_size)) else 1
    
    #Font face feature
    if len(font_face_hash) == 0:
        g_font_face.append("none")
    else:
        #sorted_fonts = font_size_hash.keys()
        #sorted_fonts.sort()
        #sorted_fonts.reverse()
        sorted_fonts = sorted(font_face_hash.iteritems(), key=lambda (k,v):(v,k), reverse=True)
        
        font_face = sorted_fonts[0][0]
        g_font_face.append(font_face)
        
        g_font_face_hash[font_face] = g_font_face_hash[font_face] + 1 if g_font_face_hash.has_key(font_face) else 1

def UpdateXmlFeatures(bold_count, italic_count, words_count, is_bullet, space):
    #Bold feature
    bold_feature = ""
    if words_count != 0 and (float(bold_count)/float(words_count) >= 0.667):
        bold_feature = "yes"
    else:
        bold_feature = "no"
    g_bold.append(bold_feature)
    
    #Italic feature
    italic_feature = ""
    if words_count != 0 and (float(italic_count)/float(words_count) >= 0.667):
        italic_feature = "yes"
    else:
        italic_feature = "no"
    g_italic.append(italic_feature)
    
    #Bullet feature
    if is_bullet == "true":
        g_bullet.append("yes")
    else:
        g_bullet.append("no")

def GetFontSizeLabels(g_font_size_hash, g_font_size_labels):
    #Sort by value in desccending order
    #print g_font_size_hash
    #sorted_fonts = g_font_size_hash.keys()
    #sorted_fonts.sort()
    #sorted_fonts.reverse()
    sorted_fonts = sorted(g_font_size_hash.iteritems(), key=lambda (k,v):(v,k), reverse=True)
    #print sorted_fonts
    
    #and get the
    common_size = sorted_fonts[0][0]
    #print sorted_fonts[0][0]
    
    #Sort by key in ascending font size
    sorted_fonts = g_font_size_hash.keys()
    sorted_fonts.sort()
    #sys.stderr.write("Najit si, jak se sortuje rostoucne\n")
    #sys.exit(0)
    
    common_index = 0
    for item in sorted_fonts:
        #Found
        if common_size == item:
            break
        common_index += 1
    
    #Small fonts
    for i in range(0, common_index):
        g_font_size_labels[sorted_fonts[i]] = "smaller"
    
    #Common fonts
    g_font_size_labels[common_size] = "common"
    
    #Large fonts
    for i in range(common_index + 1, len(sorted_fonts)):
        if len(sorted_fonts) - i <= 3:
            g_font_size_labels[sorted_fonts[i]] = "largest" + str(i + 1 - len(sorted_fonts))
        else:
            g_font_size_labels[sorted_fonts[i]] = "larger"

def GetDifferentialFeatures(id):
    global body_start_id
    
    align_diff = "bi_xmlA_"
    #AlignChange feature
    if id == 0:
        align_diff += g_align[id]
    elif g_align[id] == g_align[id-1]:
        align_diff += "continue"
    else:
        align_diff += g_align[id]
    
    font_face_diff = "bi_xmlF_"
    #FontFaceChange feature
    if id == 0:
        font_face_diff += "new"
    elif g_font_face[id] == g_font_face[id-1]:
        font_face_diff += "continue"
    else:
        font_face_diff += "new"
    
    font_size_diff = "bi_xmlS_"
    #FontSizeChange feature
    if id == 0:
        font_size_diff += "new"
    elif g_font_size[id] == g_font_size[id-1]:
        font_size_diff += "continue"
    else:
        font_size_diff += "new"
    
    font_sf_diff = "bi_xmlSF_"
    #FontSFChange feature
    if id == 0:
        font_sf_diff += "new"
    elif g_font_size[id] == g_font_size[id-1] and g_font_face[id] == g_font_face[id-1]:
        font_sf_diff += "continue"
    else:
        font_sf_diff += "new"
    
    font_sfbi_diff = "bi_xmlSFBI_"
    #FontSBFIChange feature
    if id == 0:
        font_sfbi_diff += "new"
    elif g_font_size[id] == g_font_size[id-1] and g_font_face[id] == g_font_face[id-1] and g_bold[id] == g_bold[id-1] and g_italic[id] == g_italic[id-1]:
        font_sfbi_diff +=  "continue"
    else:
        font_sfbi_diff += "new"
    
    font_sfbia_diff = "bi_xmlSFBIA_"
    #FontSBFIChange feature
    if id == 0:
        font_sfbia_diff += "new"
    elif g_font_size[id] == g_font_size[id-1] and g_font_face[id] == g_font_face[id-1] and g_bold[id] == g_bold[id-1] and g_italic[id] == g_italic[id-1] and g_align[id] == g_align[id-1]:
        font_sfbia_diff +=  "continue"
    else:
        font_sfbia_diff += "new"
    
    #ParaChange feature
    para_diff = "bi_xmlPara_"
    #Header part, consider each line as a separate paragraph
    if id < body_start_id:
        para_diff += "header"
    else:
        if g_para[id] == "yes":
            para_diff += "new"
        else:
            para_diff += "continue"
    
    retArray = []
    retArray.append(align_diff)
    retArray.append(font_size_diff)
    retArray.append(font_face_diff)
    retArray.append(font_sf_diff)
    retArray.append(font_sfbi_diff)
    retArray.append(font_sfbia_diff)
    retArray.append(para_diff)
    return retArray

def Output(lines, out_file):
    output_handle = ""
    try:
        output_handle = codecs.open(out_file, 'w', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + out_file)
        sys.exit(1)
    
    #RTF feature label
    g_font_size_labels = {}
    GetFontSizeLabels(g_font_size_hash, g_font_size_labels)
    
    output = ""
    para_line_id = -1
    para_line_count = 0
    
    #This is the index of the line
    id = 0
    #For each line in the whole document
    #print lines
    #print ""
    #print "LINE"
    for line in lines:
        #print line.encode('utf-8').strip()
        #Remove empty line
        line = re.sub(r"^\s+|\s+$", "", line)
        
        #New paragraph
        if g_para[id] == "yes" and not output == "":
            if is_decode:
                #output = re.sub('&([^;]+);', lambda m: unichr(htmlentitydefs.name2codepoint[m.group(1)]), output)
                
                #Write output to file
                output_handle.write(output)
                output = ""
        
        output += line
        
        loc_feature = ""
        #RTF location feature
        if g_pos_hash[id] != (-1):
            loc_feature = "xmlLoc_" + str(int((int(g_pos_hash[id]) - int(g_minpos))*8.0/(int(g_maxpos)-int(g_minpos) + 1)))
        
        #Align feature
        align_feature = "xmlAlign_" + g_align[id]
        
        font_size_feature = ""
        #Font_size feature
        if g_font_size[id] == "" or g_font_size[id] == -1:
            font_size_feature = "xmlFontSize_none"
        else:
            font_size_feature = "xmlFontSize_" + g_font_size_labels[g_font_size[id]]
        
        #Bold feature
        bold_feature = "xmlBold_" + g_bold[id]
        #Italic feature
        italic_feature = "xmlItalic_" + g_italic[id]
        #Image feature
        pic_feature = "xmlPic_" + g_pic[id]
        #Table feature
        table_feature = "xmlTable_" + g_table[id]
        #Bullet feature
        bullet_feature = "xmlBullet_" + g_bullet[id]
        #Differential features
        tmpArr = GetDifferentialFeatures(id)
        align_diff = tmpArr[0]
        font_size_diff = tmpArr[1]
        font_face_diff = tmpArr[2]
        font_sf_diff = tmpArr[3]
        font_sfbi_diff = tmpArr[4]
        font_sfbia_diff = tmpArr[5]
        para_diff = tmpArr[6]
        
        #Each line and its RTF features
        output += " |XML| "+ loc_feature + " " + bold_feature + " " + italic_feature + " " + font_size_feature + " " + pic_feature + " " + table_feature + " " + bullet_feature + " " + font_sfbia_diff + " " + para_diff + "\n"; 
        
        #Update line index
        id += 1
    
    #New paragraph
    #if not output:
    if output:
        #if is_decode:
        #    output = re.sub('&([^;]+);', lambda m: unichr(htmlentitydefs.name2codepoint[m.group(1)]), output)
        output_handle.write(output)
        output = ""
    
    #Done
    output_handle.close()

""" MAIN """
def Entry(xml, input, out_file):
    global header_length
    global body_length
    global body_start_id
    global lines_addr
    
    contentStr = ProcessFile(xml, input)
    #sys.stderr.write("ContentStr\n")
    #print contentStr.encode('utf-8').strip()
    #sys.exit(0)
    #Find header part
    num_lines = len(lines)
    
    sys.path.append("./LSRLabel/")
    import PreProcess
    tmpArr= PreProcess.FindHeaderText(lines, 0, num_lines)
    header_length = tmpArr[0]
    body_length = tmpArr[1]
    body_start_id = tmpArr[2]
    #Done
    Output(lines, out_file)
    #sys.stderr.write("Lines\n")
    #print lines
    #sys.exit(0)
    
    if address == 1:
        address_handle = ""
        try:
            address_handle = codecs.open(out_file + ".address", 'w', "utf-8")
        except IOError:
            sys.stderr.write("Nelze otevrit soubor " + out_file + ".address")
            sys.exit(1)
        
        for addr in lines_addr:
            address_handle.write(str(addr["L1"]) + " " + str(addr["L2"]) + " " + str(addr["L3"]) + " " + str(addr["L4"]) + "\n")
        
        #Done
        address_handle.close()
    
    return contentStr
    
#""" ZACATEK """
#main()
