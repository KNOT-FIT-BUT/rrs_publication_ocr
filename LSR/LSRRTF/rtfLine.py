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
tmp_baseline = ""
tmp_bottom = ""
tmp_top = ""
tmp_left = ""
tmp_right = ""
tmp_objs = []

class rtfLine:
    def __init__(self):
        self.objs = []
        
        #Class members
        self.members = {"_self":obj_list["OMNILINE"], 
                                   "_raw":"", 
                                   "_content":"", 
                                   "_baseline":"", 
                                   "_bottom":"", 
                                   "_top":"", 
                                   "_left":"", 
                                   "_right":"", 
                                   "_bullet":"", 
                                   "_objs":self.objs}
    
    def set_raw(self, raw):
        global tmp_content
        global tmp_baseline
        global tmp_bottom
        global tmp_top
        global tmp_left
        global tmp_right
        global tmp_objs
        
        #Save the raw xml <ln> ... </ln>
        self.members["_raw"] = raw
        
        self.parse(raw)
        
        #Copy information from temporary variables to class members
        self.members["_bottom"] = tmp_bottom
        self.members["_top"] = tmp_top
        self.members["_left"] = tmp_left
        self.members["_right"] = tmp_right
        self.members["_baseline"] = tmp_baseline
        
        #Copy all lines
        self.members["_objs"] = tmp_objs
        
        #Copy content
        self.members["_content"] = tmp_content
    
    def get_raw(self):
        return self.members["_raw"]
    
    def parse(self, raw):
        global tmp_content
        global tmp_baseline
        global tmp_bottom
        global tmp_top
        global tmp_left
        global tmp_right
        global tmp_objs
        
        #At first, content is blank
        tmp_content = ""
        #because there's no run
        tmp_objs = []
        
        #Get <line> node attributes
        tmp_bottom = re.search(r"b=\"(\d+)\"", raw).group(1)
        tmp_top = re.search(r"t=\"(\d+)\"", raw).group(1)
        tmp_left = re.search(r"l=\"(\d+)\"", raw).group(1)
        tmp_right = re.search(r"r=\"(\d+)\"", raw).group(1)
        tmp_baseline = re.search(r"baseLine=\"(\d+)\"", raw).group(1)
        
        #Get <line> node possible attributes
        tmp_font_face = re.search(r"fontFace=\"(\w+|\s+)+\"", raw).group(1)
        tmp_font_family = re.search(r"fontFamily=\"(\w+)\"", raw).group(1)
        tmp_font_pitch = re.search(r"fontPitch=\"(\w+)\"", raw).group(1)
        tmp_font_size = re.search(r"fontSize=\"(\w+)\"", raw).group(1)
        tmp_spacing = re.search(r"spacing=\"(\w+)\"", raw).group(1)
        tmp_su_script = re.search(r"subsuperscript=\"(\w+)\"", raw).group(1)
        tmp_underline = re.search(r"underlined=\"(\w+)\"", raw).group(1)
        tmp_bold = ""
        if re.search(r"bold=\"(\w+)\"", raw) != None:
            tmp_bold = re.search(r"bold=\"(\w+)\"", raw).group(1)
        tmp_italic = ""
        if re.search(r"italic=\"(\w+)\"", raw) != None:
            tmp_italic = re.search(r"italic=\"(\w+)\"", raw).group(1)
        
        #Check if there's any run
        tmpRaw= raw
        tmpRaw = re.sub(r"^<ln[^>]*>\n", "", tmpRaw)
        tmpRaw = re.sub(r"</ln>(\n)?$", "", tmpRaw)
        
        all_runs = ""
        if re.search(r"^<run", tmpRaw) != None:
            all_runs = "yes"
            
        #print all_runs
            
        sys.path.append("./LSRRTF/")
        import rtfRun
        
        #There is not
        if not all_runs:
            output = "<run "
            output += "fontFace=\""+ tmp_font_face +"\" "
            output += "fontFamily=\""+ tmp_font_family +"\" "
            output += "fontPitch=\""+ tmp_font_pitch +"\" "
            output += "fontSize=\""+ tmp_font_size +"\" "
            output += "spacing=\""+ tmp_spacing +"\" "
            output += "subsuperscript=\""+ tmp_su_script +"\" "
            output += "underlined=\""+ tmp_underline +"\" "
            output += "bold=\""+ tmp_bold +"\" "
            output += "italic=\""+ tmp_italic +"\">\n"
            output += tmpRaw
            output += "</run>\n"
            
            #Fake run
            run = rtfRun.rtfRun()
            
            #Set raw content
            run.set_raw(output)
            
            #Update run list
            tmp_objs.append(run)
            
            #Update content
            tmp_content += run.get_content()
            #print tmp_content
            #sys.exit(0)
        else:
            while True:
                if re.search(r"^<run", tmpRaw) != None:
                    run = rtfRun.rtfRun()
                    
                    #Set raw content
                    indexRunEnd = tmpRaw.index("</run>") + len("</run>")
                    tmpRunRaw = tmpRaw[:indexRunEnd]
                    tmpRaw = tmpRaw[indexRunEnd+1:]
                    run.set_raw(tmpRunRaw)
                    
                    #Update object list
                    tmp_objs.append(run)
                    
                    #Update content
                    tmp_content += run.get_content()
                elif re.search(r"^<wd", tmpRaw) != None:
                    sys.stderr("rtfLine:: nalezeno slovo, ktere neni pokryto tagem <run>, nemelo nastat\n")
                    sys.exit(1)
                else:
                    break
        #print tmp_content
        #sys.exit(0)
    
    def get_bullet(self):
        return self.members["_bullet"]
    
    def set_bullet(self, bullet):
        self.members["_bullet"] = bullet
    
    def get_name(self):
        return self.members["_self"]
        
    def get_objs_ref(self):
        return self.members["_objs"]
        
    def get_content(self):
        return self.members["_content"]
    
    def get_baseline(self):
        return self.members["_baseline"]
    
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
