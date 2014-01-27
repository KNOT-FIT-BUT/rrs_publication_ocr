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
tmp_font_face = ""
tmp_font_family = ""
tmp_font_pitch = ""
tmp_font_size = ""
tmp_spacing = ""
tmp_su_script = ""
tmp_underline = ""
tmp_bold = ""
tmp_italic = ""
tmp_words = []

class rtfRun():
    def __init__(self):
        # Words: a run can have multiple words
        self.words = []
        
        self.members = {"_self":obj_list["OMNIRUN"], 
                                   "_raw":"", 
                                   "_content":"", 
                                   "_font_face":"", 
                                   "_font_family":"", 
                                   "_font_pitch":"", 
                                   "_font_size":"", 
                                   "_spacing":"", 
                                   "_su_script":"", 
                                   "_underline":"", 
                                   "_bold":"", 
                                   "_italic":"", 
                                   "_words":self.words}
    
    def set_raw(self, raw):
        global tmp_content
        global tmp_font_face
        global tmp_font_family
        global tmp_font_pitch
        global tmp_font_size
        global tmp_spacing
        global tmp_su_script
        global tmp_underline
        global tmp_bold
        global tmp_italic
        global tmp_words

        # Save the raw xml <run> ... </run>
        self.members["_raw"] = raw
        
        self.parse(raw)
        
        # Copy information from temporary variables to class members
        self.members["_font_face"] = tmp_font_face
        self.members["_font_family"] = tmp_font_family
        self.members["_font_pitch"] = tmp_font_pitch
        self.members["_font_size"] = tmp_font_size
        self.members["_spacing"] = tmp_spacing
        self.members["_su_script"] = tmp_su_script
        self.members["_underline"] = tmp_underline
        self.members["_bold"] = tmp_bold
        self.members["_italic"] = tmp_italic
        
        #Copy all words
        self.members["_words"] = tmp_words
        
        #Copy content
        self.members["_content"] = tmp_content
    
    def get_raw(self):
        return self.members["_raw"]
    
    def parse(self, raw):
        global tmp_content
        global tmp_font_face
        global tmp_font_family
        global tmp_font_pitch
        global tmp_font_size
        global tmp_spacing
        global tmp_su_script
        global tmp_underline
        global tmp_bold
        global tmp_italic
        global tmp_words
        
        #Get <run> node attributes
        tmp_font_face = re.search(r"fontFace=\"(\w+|\s+)+\"", raw).group(1)
        tmp_font_family = re.search(r"fontFamily=\"(\w+)\"", raw).group(1)
        tmp_font_pitch = re.search(r"fontPitch=\"(\w+)\"", raw).group(1)
        tmp_font_size = re.search(r"fontSize=\"(\w+)\"", raw).group(1)
        tmp_spacing = re.search(r"spacing=\"(\w+)\"", raw).group(1)
        tmp_su_script = re.search(r"subsuperscript=\"(\w+)\"", raw).group(1)
        try:
            tmp_underline = re.search(r"underlined=\"(\w+)\"", raw).group(1)
        except AttributeError:
            print raw
            sys.exit(0)
        tmp_bold = ""
        if re.search(r"bold=\"(\w+)\"", raw) != None:
            tmp_bold = re.search(r"bold=\"(\w+)\"", raw).group(1)
        tmp_italic = ""
        if re.search(r"italic=\"(\w+)\"", raw) != None:
            tmp_italic = re.search(r"italic=\"(\w+)\"", raw).group(1)
        
        #At first, content is blank
        tmp_content = ""
        #because there's no word
        tmp_words = []
        
        tmpRaw = raw
        tmpRaw = re.sub(r"^<run[^>]*>\n", "", tmpRaw)
        tmpRaw = re.sub(r"</run>\n$", "", tmpRaw)

        # #PCDATA$
        if re.search(r"^[^<]", tmpRaw) != None:
            sys.stderr.write("rtfRun::<run> obsahuje data mimo tagy\n")
            sys.exit(1)
        else:
            sys.path.append("./LSRRTF/")
            import rtfWord
            
            while True:
                if re.search(r"^<wd", tmpRaw) != None:
                    word = rtfWord.rtfWord()
                    
                    #Set raw content
                    try:
                        indexEndWord = tmpRaw.index("</wd>") + len("</wd>")
                    except ValueError:
                        print "RAW"
                        print raw
                        print "TMPRAW"
                        print tmpRaw
                        sys.exit(0)
                    
                    tmpWordRaw = tmpRaw[:indexEndWord]
                    tmpRaw = tmpRaw[indexEndWord+1:]
                    
                    word.set_raw(tmpWordRaw)
                    
                    #Update word list
                    tmp_words.append(word)
                    
                    #Update content
                    tmp_content += word.get_content()
                elif re.search(r"^<space/>", tmpRaw) != None:
                    tmpRaw = re.sub(r"^<space/>\n", "", tmpRaw)
                    tmp_content += " "
                elif re.search(r"^<tab/>", tmpRaw) != None:
                    tmpRaw = re.sub(r"^<tab/>\n", "", tmpRaw)
                    tmp_content += "\t"
                else:
                    break
    
    def add_word(self, word):
        self.members["_words"].append(word)
    
    def get_name(self):
        return self.members["_self"]
        
    def get_objs_ref(self):
        return self.members["_objs"]
        
    def get_content(self):
        return self.members["_content"]
    
    def get_font_face(self):
        return self.members["_font_face"]
    
    def get_font_family(self):
        return self.members["_font_family"]
    
    def get_font_pitch(self):
        return self.members["_font_pitch"]
    
    def get_font_size(self):
        return self.members["_font_size"]
    
    def get_spacing(self):
        return self.members["_spacing"]
    
    def get_suscript(self):
        return self.members["_su_script"]
    
    def get_underline(self):
        return self.members["_underline"]
    
    def get_bold(self):
        return self.members["_bold"]
    
    def get_italic(self):
        return self.members["_italic"]
    
    def GetNodeAttr(self, node, attr):
        return node.att(attr) if node.att(attr) else ""
        
    def SetNodeAttr(self, attr, value):
        node.set_att(attr, value)
        
    def GetNodeText(self):
        return node.text
        
    def SetNodeText(self, node, value):
        node.set_text(value)
