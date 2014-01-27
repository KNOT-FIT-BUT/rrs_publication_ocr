#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys
import os
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
tmp_objs = []

class rtfPage:
    def __init__(self):
        # Page: a page can have many columns, many tables, or many images
        self.objs = []
        self.members = {"_self":obj_list["OMNIPAGE"], 
                                   "_raw":"", 
                                   "_content":"", 
                                   "_objs":self.objs}
    
    def set_raw(self, raw):
        global tmp_content
        global tmp_objs

        #Save the raw xml <page> ... </page>
        self.members["_raw"] = raw
        self.parse(raw)
        
        #Copy information from temporary variables to class members
        
        #Copy all columns
        self.members["_objs"] = tmp_objs
        
        #Copy content
        self.members["_content"] = tmp_content
    
    def get_raw(self):
        return self.members["_raw"]
    
    def parse(self, raw):
        global tmp_content
        global tmp_objs
        
        # At first, content is blank
        tmp_content = "";
        # because there's no column, table or image
        tmp_objs = [];
        tmpRaw = raw
        tmpRaw = re.sub(r"<page>\n", "", tmpRaw)
        tmpRaw = re.sub(r"</page>(\n)?", "", tmpRaw)
        tmpRaw = re.sub(r"<body>\n", "", tmpRaw)
        tmpRaw = re.sub(r"</body>(\n)?", "", tmpRaw)
        
        #if re.search(r"^<section", tmpRaw) != None:
        #    section_tag = tmpRaw
        #    tmpRaw = re.sub(r"^<section[^>]*>\n", "", tmpRaw)
        #    tmpRaw = re.sub(r"</section>\n", "", tmpRaw, 1)
        sys.path.append("./LSRRTF/")
        import rtfCol
        
        while True:
            if re.search(r"^<section", tmpRaw) != None:
                tmpSecRaw = tmpRaw
                tmpSecRaw = re.sub(r"^<section[^>]*>\n", "", tmpSecRaw)
                tmpSecRaw = re.sub(r"</section>\n", "", tmpSecRaw, 1)
                
                while True:
                    if re.search(r"^<column", tmpSecRaw) != None:
                        column = rtfCol.rtfCol()
                        
                        indexColEnd = tmpSecRaw.index("</column>") + len("</column>")
                        tmpColRaw = tmpSecRaw[:indexColEnd]
                        tmpSecRaw = tmpSecRaw[indexColEnd+1:]
                        
                        #Set raw content
                        column.set_raw(tmpColRaw)
                        
                        #Update column list
                        tmp_objs.append(column)
                        
                        #Update content
                        tmp_content += column.get_content() + "\n"
                        #print tmp_content
                    elif re.search(r"^<dd", tmpSecRaw) != None:
                        import rtfDd
                        dd = rtfDd.rtfDd()
                        
                        indexDdEnd = tmpSecRaw.index("</dd>") + len("</dd>")
                        tmpDdRaw = tmpSecRaw[:indexDdEnd]
                        tmpSecRaw = tmpSecRaw[indexDdEnd+1:]
                        
                        #Set raw content
                        dd.set_raw(tmpDdRaw)
                        
                        #Update dd list
                        tmp_objs.append(dd)
                        
                        #Update content
                        tmp_content += dd.get_content() + "\n"
                    elif re.search(r"^<frame", tmpSecRaw) != None:
                        import rtfFrame
                        frame = rtfFrame.rtfFrame()
                        
                        indexFrameEnd = tmpSecRaw.index("</frame>") + len("</frame>")
                        tmpFrameRaw = tmpSecRaw[:indexFrameEnd]
                        tmpSecRaw = tmpSecRaw[indexFrameEnd+1:]
                        
                        #Set raw content
                        dd.set_raw(tmpFrameRaw)
                        
                        #Update dd list
                        tmp_objs.append(frame)
                        
                        #Update content
                        tmp_content += frame.get_content() + "\n"
                    else:
                        break
                tmpRaw = tmpSecRaw
                #print tmp_content
                #print tmpRaw
                #sys.exit(0)
            elif re.search(r"^<column", tmpSecRaw) != None:
                column = rtfCol.rtfCol()
                
                indexColEnd = tmpRaw.index("</column>") + len("</column>")
                tmpColRaw = tmpRaw[:indexColEnd]
                tmpRaw = tmpRaw[indexColEnd+1:]
                
                #Set raw content
                column.set_raw(tmpColRaw)
                
                #Update column list
                tmp_objs.append(column)
                
                #Update content
                tmp_content += column.get_content() + "\n"
                #print tmp_content
            elif re.search(r"^<dd", tmpSecRaw) != None:
                import rtfDd
                dd = rtfDd.rtfDd()
                
                indexDdEnd = tmpRaw.index("</dd>") + len("</dd>")
                tmpDdRaw = tmpRaw[:indexDdEnd]
                tmpRaw = tmpRaw[indexDdEnd+1:]
                
                #Set raw content
                dd.set_raw(tmpDdRaw)
                
                #Update dd list
                tmp_objs.append(dd)
                
                #Update content
                tmp_content += dd.get_content() + "\n"
            elif re.search(r"^<frame", tmpSecRaw) != None:
                import rtfFrame
                frame = rtfFrame.rtfFrame()
                
                indexFrameEnd = tmpRaw.index("</frame>") + len("</frame>")
                tmpFrameRaw = tmpRaw[:indexFrameEnd]
                tmpRaw = tmpRaw[indexFrameEnd+1:]
                
                #Set raw content
                dd.set_raw(tmpFrameRaw)
                
                #Update dd list
                tmp_objs.append(frame)
                
                #Update content
                tmp_content += frame.get_content() + "\n"
            else:
                break
    
    def get_name(self):
        return self.members["_self"]
        
    def get_objs_ref(self):
        return self.members["_objs"]
        
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
