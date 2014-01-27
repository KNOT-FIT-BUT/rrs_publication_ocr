#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys

tag_list = {"DOCUMENT":"document", 
                  "PAGE":"page", 
                  "COLUMN":"column", 
                  "DESC":"description", 
                  "SRC":"source", 
                  "LANGUAGE":"language", 
                  "STYLE":"style", 
                  "STYLE-TABLE":"styleTable", 
                  "THEO-PAGE":"theoreticalPage", 
                  "BODY":"body", 
                  "SECTION":"section", 
                  "COL":"column", 
                  "PARA":"para", 
                  "LINE":"ln", 
                  "WORD":"wd", 
                  "SPACE":"space", 
                  "RUN":"run", 
                  "BULLET":"bullet", 
                  "TABLE":"table", 
                  "GRID":"gridTable", 
                  "GRID-COL":"gridCol", 
                  "GRID-ROW":"gridRow", 
                  "CELL":"cell", 
                  "BOTTOM-CELL":"bottomBorder", 
                  "TOP-CELL":"topBorder", 
                  "LEFT-CELL":"leftBorder", 
                  "RIGHT-CELL":"rightBorder", 
                  "NEWLINE":"nl", 
                  "TAB":"tab", 
                  "DD":"dd", 
                  "PICTURE":"picture", 
                  "FRAME":"frame"}

att_list = {"ALIGN":"alignment", 
                 "FONTFACE":"fontFace", 
                 "FONTFAMILY":"fontFamily", 
                 "FONTPITCH":"fontPitch", 
                 "FONTSIZE":"fontSize", 
                 "UNDERLINE":"underline", 
                 "SPACING":"spacing", 
                 "SCALE":"scale", 
                 "BOTTOM":"b", 
                 "TOP":"t", 
                 "LEFT":"l", 
                 "RIGHT":"r", 
                 "LANGUAGE":"language", 
                 "SUSCRIPT":"subsuperscript", 
                 "BASELINE":"baseline", 
                 "BOLD":"bold", 
                 "ITALIC":"italic", 
                 "SPACEB":"spaceBefore", 
                 #These attribute usually go with <dd> tag
                 "BOTTOMDIST":"bottomDistance", 
                 "TOPDIST":"topDistance", 
                 "LEFTDIST":"leftDistance", 
                 "RIGHTDIST":"rightDistance", 
                 #These attribute usually go with <cell> tag
                 "GROWFROM":"gridRowFrom", 
                 "GROWTO":"gridRowTill", 
                 "GCOLFROM":"gridColFrom", 
                 "GCOLTO":"gridColTill", 
                 "VALIGN":"verticalAlignment"}

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

#Temporary variables
tmp_content = ""
tmp_bottom = ""
tmp_top = ""
tmp_left = ""
tmp_right = ""
tmp_language = ""
tmp_alignment = ""
tmp_spaceb = ""
tmp_lines = []

class rtfPara:
    def __init__(self):
        #Lines: a paragraph can have multiple lines
        self.lines = []
        
        #Class members
        self.members = {"_self":obj_list["OMNIPARA"], 
                                   "_raw":"", 
                                   "_content":"", 
                                   "_bottom":"", 
                                   "_top":"", 
                                   "_left":"", 
                                   "_right":"", 
                                   "_language":"", 
                                   "_alignment":"", 
                                   "_spaceb":"", 
                                   "_lines":self.lines}
    
    def set_raw(self, raw):
        global tmp_content
        global tmp_bottom
        global tmp_top
        global tmp_left
        global tmp_right
        global tmp_language
        global tmp_alignment
        global tmp_spaceb
        global tmp_lines

        #Save the raw xml <para> ... </para>
        self.members["_raw"] = raw
        
        self.parse(raw)
        
        #Copy information from temporary variables to class members
        self.members["_bottom"] = tmp_bottom
        self.members["_top"] = tmp_top
        self.members["_left"] = tmp_left
        self.members["_right"] = tmp_right
        self.members["_language"] = tmp_language
        self.members["_alignment"] = tmp_alignment
        self.members["_spaceb"] = tmp_spaceb
        
        #Copy all lines
        self.members["_lines"] = tmp_lines
        
        #Copy content
        self.members["_content"] = tmp_content
    
    def get_raw(self):
        return self.members["_raw"]
    
    def parse(self, raw):
        global tmp_content
        global tmp_bottom
        global tmp_top
        global tmp_left
        global tmp_right
        global tmp_language
        global tmp_alignment
        global tmp_spaceb
        global tmp_lines
        
        #At first, content is blank
        tmp_content = ""
        #because there's no line
        tmp_lines = []
        
        #Get <para> node attributes
        tmp_bottom = re.search(r"b=\"(\d+)\"", raw).group(1)
        tmp_top = re.search(r"t=\"(\d+)\"", raw).group(1)
        tmp_left = re.search(r"l=\"(\d+)\"", raw).group(1)
        tmp_right = re.search(r"r=\"(\d+)\"", raw).group(1)
        tmp_language = re.search(r"language=\"(\w+)\"", raw).group(1)
        try:
            tmp_alignment = re.search(r"alignment=\"(\w+)\"", raw).group(1)
        except AttributeError:
            print raw
            sys.exit(1)
        
        if re.search(r"sb=\"(\d+)\"", raw) != None:
            tmp_spaceb = re.search(r"sb=\"(\d+)\"", raw).group(1)
        
        #Check if there's any line
        all_lines = []
        tmpRaw = raw
        tmpRaw = re.sub(r"^<para[^>]*>\n", "", tmpRaw)
        tmpRaw = re.sub(r"</para>(\n)?$", "", tmpRaw)
        
        sys.path.append("./LSRRTF/")
        import rtfLine
        
        while re.search(r"^<ln", tmpRaw) != None:
            line = rtfLine.rtfLine()
            
            try:
                indexEndLn = tmpRaw.index("</ln>") + len("</ln>")
            except ValueError:
                print tmpRaw
            tmpLnRaw = tmpRaw[:indexEndLn]
            tmpRaw = tmpRaw[indexEndLn+1:]
            
            #Set raw content
            line.set_raw(tmpLnRaw)
            
            #Pozor!! Moznost Bullet
            
            #Update line list
            tmp_lines.append(line)
            
            #Update content
            tmp_content = tmp_content + line.get_content() + "\n"
    
    def get_name(self):
        return self.members["_self"]
        
    def get_objs_ref(self):
        return self.members["_lines"]
        
    def get_content(self):
        return self.members["_content"]
        
    def get_bottom_pos(self):
        return self.members["_bottom"]
        
    def get_top_pos(self):
        return self.members["_top"]
        
    def get_left_pos(self):
        return self.members["_left"]
        
    def get_right_pos(self):
        return self.members["_right"]
        
    def get_language(self):
        return self.members["_language"]
        
    def get_alignment(self):
        return self.members["_alignment"]
        
    def get_space_before(self):
        return self.members["_spaceb"]
        
    def GetNodeAttr(self, node, attr):
        return node.att(attr) if node.att(attr) else ""
        
    def SetNodeAttr(self, attr, value):
        node.set_att(attr, value)
        
    def GetNodeText(self):
        return node.text
        
    def SetNodeText(self, node, value):
        node.set_text(value)
