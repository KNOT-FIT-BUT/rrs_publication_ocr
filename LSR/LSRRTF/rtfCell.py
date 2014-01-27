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

# Temporary variables
tmp_content = ""
tmp_alignment = ""
tmp_grid_col_to = ""
tmp_grid_col_from = ""
tmp_grid_row_to = ""
tmp_grid_row_from = ""
tmp_vertical_align = ""

# My observation is that <table> contains <gridTable> and <cell>
# <gridTable> contain the base grid's coordinates
# <cell> contain the cell's position based on <gridTable> coordinates
# and various types of objects: <picture>, <para>, may be even <dd> but
# I'm not quite sure about this
tmp_objs = []

class rtfCell():
    def __init__(self):
        # Objs: a paragraph can have many cells
        self.objs = []
        
        self.members = {"_self":"cell", 
                                   "_raw":"", 
                                   "_content":"", 
                                   "_alignment":"", 
                                   "_row_from":"", 
                                   "_row_to":"", 
                                   "_col_from":"", 
                                   "_col_to":"", 
                                   "_v_alignment":"", 
                                   "_objs":self.objs}
    
    def set_raw(self, raw):
        global tmp_content
        global tmp_alignment
        global tmp_grid_col_to
        global tmp_grid_col_from
        global tmp_grid_row_to
        global tmp_grid_row_from
        global tmp_vertical_align

        # Save the raw xml <cell> ... </cell>
        self.members["_raw"] = raw
        
        # Parse the raw string
        self.parse(raw)
        
        # Copy information from temporary variables to class members
        self.members["_alignment"] = tmp_alignment
        self.members["_row_from"] = tmp_grid_row_from
        self.members["_row_to"] = tmp_grid_row_to
        self.members["_col_from"] = tmp_grid_col_from
        self.members["_col_to"] = tmp_grid_col_to
        self.members["_v_alignment"] = tmp_vertical_align
        
        # Copy all objects
        self.members["_objs"] = tmp_objs
        
        # Copy content
        self.members["_content"] = tmp_content
    
    def get_raw(self):
        return self.members["_raw"]
    
    def parse(self, raw):
        global tmp_content
        global tmp_alignment
        global tmp_grid_col_to
        global tmp_grid_col_from
        global tmp_grid_row_to
        global tmp_grid_row_from
        global tmp_vertical_align
        
        # At first, content is blank
        tmp_content = ""
        # because there's no line
        tmp_objs = []
        
        # Get <cell> node attributes
        tmp_alignment = re.search(r"alignment=\"(\w+)\"", raw).group(1)
        
        tmp_grid_row_from = re.search(r"gridRowFrom=\"(\d+)\"", raw).group(1)
        tmp_grid_row_to = re.search(r"gridRowTill=\"(\d+)\"", raw).group(1)
        tmp_grid_col_from = re.search(r"gridColFrom=\"(\d+)\"", raw).group(1)
        tmp_grid_col_to = re.search(r"gridColTill=\"(\d+)\"", raw).group(1)
        
        # TODO: don't understand, attribute with value = 0 will be returned as undef by twig
        tmp_grid_row_from = tmp_grid_row_from if tmp_grid_row_from else 0
        tmp_grid_row_to = tmp_grid_row_to if tmp_grid_row_to else 0
        tmp_grid_col_from = tmp_grid_col_from if tmp_grid_col_from else 0
        tmp_grid_col_to = tmp_grid_col_to if tmp_grid_col_to else 0
        
        tmp_vertical_align = re.search(r"verticalAlignment=\"(\w+)\"", raw).group(1)
        
        tmpRaw = raw
        tmpRaw = re.sub(r"^<cell[^>]*>\n", "", tmpRaw)
        tmpRaw = re.sub(r"</cell>(\n)?$", "", tmpRaw)
        
        tmpRaw = re.sub(r"<leftBorder[^>]*>\n", "", tmpRaw, 1)
        tmpRaw = re.sub(r"<rightBorder[^>]*>\n", "", tmpRaw, 1)
        tmpRaw = re.sub(r"<topBorder[^>]*>\n", "", tmpRaw, 1)
        tmpRaw = re.sub(r"<bottomBorder[^>]*>\n", "", tmpRaw, 1)
        
        sys.path.append("./LSRRTF/")
        import rtfPara
        
        while True:
            if re.search(r"^<para", tmpRaw) != None:
                para = rtfPara.rtfPara()
                
                indexParaEnd = tmpRaw.index("</para>") + len("</para>")
                tmpParaRaw = tmpRaw[:indexParaEnd]
                tmpRaw = tmpParaRaw[indexParaEnd+1:]
                # Set raw content
                para.set_raw(tmpParaRaw)
                
                # Update paragraph list
                tmp_objs.append(para)
                
                # Update content
                tmp_content += para.get_content() + "\n"
            else:
                break
    
    def get_name(self):
        return self.members["_self"]
    
    def get_objs_ref(self):
        return self.members["_objs"]
    
    def get_content(self):
        return self.members["_content"]
    
    def get_alignment(self):
        return self.members["_alignment"]
    
    def get_grid_row_from(self):
        return self.members["_row_from"]
    
    def get_grid_row_to(self):
        return self.members["_row_to"]
    
    def get_grid_col_from(self):
        return self.members["_col_from"]
    
    def get_grid_col_to(self):
        return self.members["_col_to"]
    
    def get_vertical_alignment(self):
        return self.members["_v_alignment"]
