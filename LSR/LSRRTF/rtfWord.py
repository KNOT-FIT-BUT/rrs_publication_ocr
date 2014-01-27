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
tmp_content = ""

class rtfWord():
    def __init__(self):
        self.members = {"_self":obj_list["OMNIWORD"], 
                                   "_raw":"", 
                                   "_content":"", 
                                   "_bottom":"", 
                                   "_top":"", 
                                   "_left":"", 
                                   "_right":""}
    
    def set_raw(self, raw):
        global tmp_bottom
        global tmp_top
        global tmp_left
        global tmp_right
        global tmp_content
        
        self.members["_raw"] = raw
        
        self.parse(raw)
        
        self.members["_bottom"] = tmp_bottom
        self.members["_top"] = tmp_top
        self.members["_left"] = tmp_left
        self.members["_right"] = tmp_right
        
        self.members["_content"] = tmp_content
    
    def get_raw(self):
        return self.members["_raw"]
    
    def parse(self, raw):
        global tmp_bottom
        global tmp_top
        global tmp_left
        global tmp_right
        global tmp_content
        
        #Get <word> node attributes
        tmp_bottom = re.search(r"b=\"(\d+)\"", raw).group(1)
        tmp_top = re.search(r"t=\"(\d+)\"", raw).group(1)
        tmp_left = re.search(r"l=\"(\d+)\"", raw).group(1)
        tmp_right = re.search(r"r=\"(\d+)\"", raw).group(1)
        
        #muze nastat situace, kdyz se odebere cokoli, co neni tisknutelne v EN a tim padem zustane prazdny retezec
        try:
            tmp_content = re.search(r"^<wd[^>]*>(.*)</wd>(\n)?$", raw).group(1)
        except AttributeError:
            sys.stderr.write("rtfWord.py - parse(): No word found\n")
            tmp_content = ""
        tmp_content = re.sub(r"^\s+|\s+$", "", tmp_content)
        tmp_content = re.sub(r"<", "&lt", tmp_content)
        tmp_content = re.sub(r">", "&gt", tmp_content)
        tmp_content = re.sub(r"\s+&\s+", "&amp", tmp_content)
    
    def get_name(self):
        return self.members["_self"]
        
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
        
    def GetNodeAttr(self, node, attr):
        return node.att(attr) if node.att(attr) else ""
        
    def SetNodeAttr(self, attr, value):
        node.set_att(attr, value)
        
    def GetNodeText(self):
        return node.text
        
    def SetNodeText(self, node, value):
        node.set_text(value)
