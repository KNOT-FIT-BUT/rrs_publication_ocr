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

class rtfCol():
    def __init__(self):
        # Column: a column can have many paragraphs, dd, tables, or pictures
        self.objs = []
        
        #Class members
        self.members = {"_self":obj_list["OMNICOL"], 
                                   "_raw":"", 
                                   "_content":"", 
                                   "_bottom":"", 
                                   "_top":"", 
                                   "_left":"", 
                                   "_right":"", 
                                   "_objs":self.objs}
    
    def set_raw(self, raw):
        # Save the raw xml <column> ... </column>
        self.members["raw"] = raw
        
        self.parse(raw)
    
    def get_raw(self):
        return self.members["_raw"]
    
    def parse(self, raw):
        #At first, content is blank
        tmp_content = ""
        #because there's no object
        tmp_objs = []
        
        #Get <column> node attributes
        tmp_bottom = re.search(r"b=\"(\d+)\"", raw).group(1)
        tmp_top = re.search(r"t=\"(\d+)\"", raw).group(1)
        tmp_left = re.search(r"l=\"(\d+)\"", raw).group(1)
        tmp_right = re.search(r"r=\"(\d+)\"", raw).group(1)
        
        tmpRaw = raw
        tmpRaw = re.sub(r"^<column[^>]*>\n", "", tmpRaw)
        tmpRaw = re.sub(r"</column>(\n)?$", "", tmpRaw)
        
        sys.path.append("./LSRRTF/")
        import rtfPara
        import rtfTable
        
        while True:
            if re.search(r"^<para", tmpRaw) != None:
                para = rtfPara.rtfPara()
                
                indexParaEnd = tmpRaw.index("</para>") + len("</para>")
                tmpParaRaw = tmpRaw[:indexParaEnd]
                tmpRaw = tmpRaw[indexParaEnd+1:]
                
                #Set raw content
                para.set_raw(tmpParaRaw)
                
                #Update paragraph list
                tmp_objs.append(para)
                
                #Update content
                tmp_content = tmp_content + para.get_content() + "\n"
            elif re.search(r"^<dd", tmpRaw) != None:
                sys.strerr.write("Para::dd::Neimplementovano\n")
                indexDdEnd = tmpRaw.index("</dd>") + len("</dd>")
                #tmpDdRaw = tmpRaw[:indexDdEnd]
                tmpRaw = tmpRaw[indexDdEnd+1:]
            elif re.search(r"^<table", tmpRaw) != None:
                import rtfTable
                table = rtfTable.rtfTable()
                
                indexTableEnd = tmpRaw.index("</table>") + len("</table>")
                tmpTableRaw = tmpRaw[:indexTableEnd]
                tmpRaw = tmpRaw[indexTableEnd+1:]
                
                #Set raw content
                table.set_raw(tmpTableRaw)
                
                #Update paragraph list
                tmp_objs.append(table)
                
                #Update content
                tmp_content = tmp_content + table.get_content() + "\n"
            elif re.search(r"^<image", tmpRaw) != None:
                #import rtfImage
                #table = rtfTable.rtfTable()
                
                indexImageEnd = tmpRaw.index("</image>") + len("</image>")
                #tmpTableRaw = tmpRaw[:indexTableEnd]
                tmpRaw = tmpRaw[indexImageEnd+1:]
                
                #Set raw content
                #table.set_raw(tmpTableRaw)
                
                #Update paragraph list
                #tmp_objs.append(table)
                
                #Update content
                #tmp_content = tmp_content + table.get_content() + "\n"
            elif re.search(r"^<frame", tmpRaw) != None:
                import rtfFrame
                frame = rtfFrame.rtfFrame()
                
                indexFrameEnd = tmpRaw.index("</frame>") + len("</frame>")
                tmpFrameRaw = tmpRaw[:indexFrameEnd]
                tmpRaw = tmpRaw[indexFrameEnd+1:]
                
                #Set raw content
                frame.set_raw(tmpFrameRaw)
                
                #Update paragraph list
                tmp_objs.append(frame)
                
                #Update content
                tmp_content = tmp_content + frame.get_content() + "\n"
            else:
                break
        
        self.members["_bottom"] = tmp_bottom
        self.members["_top"] = tmp_top
        self.members["_left"] = tmp_left
        self.members["_right"] = tmp_right
        self.members["_objs"] = tmp_objs
        self.members["_content"] = tmp_content
    
    def get_name(self):
        return self.members["_self"]
        
    def get_objs_ref(self):
        return self.members["_objs"]
        
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
