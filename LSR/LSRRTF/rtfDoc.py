#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
import sys
import codecs

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
                 
tmp_content = ""
tmp_pages = []

class rtfDoc:
    def __init__(self):
        self.pages = []
        self.members = {"_self":obj_list["OMNIDOC"], 
                                    "_raw":"", 
                                    "_content":"", 
                                    "_pages":self.pages}
        
    def set_raw(self, raw):
        global tmp_content
        global tmp_pages
        
        tmpDoc = raw
        tmpAllDocs = ""
        while re.search(r"<document", tmpDoc) != None:
            indexDocStart = tmpDoc.index("<document>")
            indexDocEnd = tmpDoc.index("</document>") + len("</document>")
            
            tmpAllDocs += tmpDoc[indexDocStart:indexDocEnd] + "\n"
            tmpDoc = tmpDoc[:indexDocStart] + tmpDoc[indexDocEnd+1:]
        
        tmpAllDocs = re.sub(r"<document>\n|</document>\n", "", tmpAllDocs)
        tmpAllDocs = "<document>\n" + tmpAllDocs + "</document>"
        
        self.members["_raw"] = tmpAllDocs
        self.parse(tmpAllDocs)
        
        #Copy information from temporary variables to class members
        
        #Copy all pages
        self.members["_pages"] = tmp_pages
        
        #Copy content
        self.members["_content"] = tmp_content
        
    def get_raw(self):
        return self.members["_raw"]
        
    def parse(self, raw):
        global tmp_content
        global tmp_pages
        
        all_pages = []
        tmpXml = re.sub(r"<document>\n|</document>\n", "", raw)
        
        #rozdeleni XML na stranky
        while re.search(r"^<page", tmpXml) != None:
            indexStart = tmpXml.index("<page>")
            indexEnd = tmpXml.index("</page>") + len("</page>")
            all_pages.append(tmpXml[indexStart:indexEnd])
            tmpXml = tmpXml[(indexEnd+1):]
        
        #pro kazdou stranku vytvorime objekt a vlozime do nej udaje o strance    
        sys.path.append("./LSRRTF/")
        import rtfPage
        
        for item in all_pages:
            page = rtfPage.rtfPage()
            
            #Set raw content
            page.set_raw(item)
            
            #Update page list
            tmp_pages.append(page)
            
            #Update content
            tmp_content += page.get_content() + "\n"
        
    def get_name(self):
        return self.members["_self"]
        
    def get_objs_ref(self):
        return self.members["_pages"]
        
    def get_content(self):
        return self.members["_content"]
        
    def GetNodeAttr(self, node, attr):
        return node.att(attr) if node.att(attr) else ""
        
    def SetNodeAttr(self, attr, value):
        node.set_att(attr, value)
        
    def GetNodeText(self):
        return node.text
        
    def SetNodeText(self, node, value):
        node.set_text(value)
