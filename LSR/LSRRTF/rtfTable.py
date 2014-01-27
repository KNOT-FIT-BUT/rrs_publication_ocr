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

class rtfTable():
    def __init__(self):
        # Objs: a table can have many cells
        self.objs = []
        
        # Grid coordinates
        self.grid_cols = []
        self.grid_rows = []
        
        # Content of all rows in the table
        self.rcontent = []
        
        self.members = {"_self":obj_list["OMNITABLE"], 
                                   "_raw":"", 
                                   "_content":"", 
                                   "_rcontent":self.rcontent, 
                                   "_bottom":"", 
                                   "_top":"", 
                                   "_left":"", 
                                   "_right":"", 
                                   "_alignment":"", 
                                   "_grid_cols":self.grid_cols, 
                                   "_grid_rows":self.grid_rows, 
                                   "_objs":self.objs}
    
    def set_raw(self, raw):
        # Save the raw xml <table> ... </table>
        self.members["_raw"] = raw
        
        # Parse the raw string
        self.parse(raw)
    
    def get_raw(self):
        return self.members["_raw"]
    
    def parse(self, raw):
        # At first, content is blank
        tmp_content = ""
        tmp_rcontent = []
        # because there's no object
        tmp_objs = []
        # and no coordinate
        tmp_grid_cols = []
        tmp_grid_rows = []
        
        # Get <table> node attributes
        tmp_bottom = re.search(r"b=\"(\d+)\"", raw).group(1)
        tmp_top = re.search(r"t=\"(\d+)\"", raw).group(1)
        tmp_left = re.search(r"l=\"(\d+)\"", raw).group(1)
        tmp_right = re.search(r"r=\"(\d+)\"", raw).group(1)
        try:
            tmp_alignment = re.search(r"alignment=\"(\w+)\"", raw).group(1)
        except AttributeError:
            print raw
            sys.exit(0)
        
        tmpRaw = raw
        tmpRaw = re.sub(r"^<table[^>]*>\n", "", tmpRaw)
        tmpRaw = re.sub(r"</table>(\n)?$", "", tmpRaw)
        
        indexGridTableStart = tmpRaw.index("<gridTable")
        indexGridTableEnd = tmpRaw.index("</gridTable>") + len("</gridTable>")
        
        tmpGridTableRaw = tmpRaw[indexGridTableStart:indexGridTableEnd]
        tmpGridTableRaw = re.sub(r"^<gridTable[^>]*>\n", "", tmpGridTableRaw)
        tmpGridTableRaw = re.sub(r"</gridTable>(\n)?$", "", tmpGridTableRaw)
        
        tmpRawTmp = tmpRaw
        tmpRaw = tmpRawTmp[:indexGridTableStart] + tmpRawTmp[indexGridTableEnd+1:]
        
        while True:
            if re.search(r"^<gridCol", tmpGridTableRaw) != None:
                indexGridColEnd = tmpGridTableRaw.index("</gridCol>") + len("</gridCol>")
                
                tmpGridColRaw = tmpGridTableRaw[:indexGridColEnd]
                tmpGridTableRaw = tmpGridTableRaw[indexGridColEnd+1:]
                
                tmpGridColRaw = re.sub(r"^<gridCol[^>]*>\n", "", tmpGridColRaw, 1)
                tmpGridColRaw = re.sub(r"</gridCol>(\n)?$", "", tmpGridColRaw, 1)
                
                tmp_grid_cols.append(tmpGridColRaw)
            elif re.search(r"^<gridRow", tmpGridTableRaw) != None:
                indexGridRowEnd = tmpGridTableRaw.index("</gridRow>") + len("</gridRow>")
                
                tmpGridRowRaw = tmpGridTableRaw[:indexGridRowEnd]
                tmpGridTableRaw = tmpGridTableRaw[indexGridRowEnd+1:]
                
                tmpGridRowRaw = re.sub(r"^<gridRow[^>]*>\n", "", tmpGridRowRaw, 1)
                tmpGridRowRaw = re.sub(r"</gridRow>(\n)?$", "", tmpGridRowRaw, 1)
                
                tmp_grid_rows.append(tmpGridRowRaw)
            else:
                break
        
        tmpRaw = re.sub(r"<leftBorder[^>]*>\n", "", tmpRaw, 1)
        tmpRaw = re.sub(r"<rightBorder[^>]*>\n", "", tmpRaw, 1)
        tmpRaw = re.sub(r"<topBorder[^>]*>\n", "", tmpRaw, 1)
        tmpRaw = re.sub(r"<bottomBorder[^>]*>\n", "", tmpRaw, 1)
        
        sys.path.append("./LSRRTF/")
        import rtfCell
        
        # All cells
        all_cells = []
        while re.search(r"^<cell", tmpRaw) != None:
            indexCellEnd = tmpRaw.index("</cell>") + len("</cell>")
            
            tmpCellRaw = tmpRaw[:indexCellEnd]
            tmpRaw = tmpRaw[indexCellEnd+1:]
            
            obj = rtfCell.rtfCell()
            
            # Set raw content
            obj.set_raw(tmpCellRaw)
            all_cells.append(tmpCellRaw)
            # Update cell list
            tmp_objs.append(obj)
        
        # Unformatted table
        if len(tmp_grid_cols) == 0 or len(tmp_grid_rows) == 0:
            # Just append cell content
            for itemCell in tmp_objs:
                tmp_content += itemCell.get_content() + "\n"
        #Formatted table
        else:
            # Table content
            content_matrix = []
            
            # Matrix initialization
            for i in range(0, len(tmp_grid_rows)):
                # Empty rows
                row = []
                # Update the row
                for j in range(0, len(tmp_grid_cols)):
                    row.append("")
                # Save the row
                content_matrix.append(row)
            
            # Update table content
            for itemCell in tmp_objs:
                row_index = itemCell.get_grid_row_from()
                #print "get_grid_row_from"
                #print itemCell.get_grid_row_from()
                col_index = itemCell.get_grid_col_from()
                #print "get_grid_col_from"
                #print itemCell.get_grid_col_from()
                
                # Check index and update
                #print "len(content_matrix)"
                #print len(content_matrix)
                #print "len(content_matrix[row_index])"
                #print len(content_matrix[int(row_index)])
                if int(row_index) < len(content_matrix) and int(col_index) < len(content_matrix[int(row_index)]):
                    #print "row_index < len(content_matrix)"
                    #print str(row_index) + " < " + str(len(content_matrix))
                    #print "col_index < len(content_matrix[row_index])"
                    #print str(col_index) + " < " + str(len(content_matrix[int(row_index)]))
                #print itemCell.get_grid_row_from()
                
                #print itemCell.get_grid_col_from()
                    cell_content = ""
                    #Get content
                    cell_content = itemCell.get_content()
                    #Trimm
                    cell_content = re.sub(r"^\s+|\s+$", "", cell_content)
                    #Remove blank line
                    cell_content = re.sub(r"\n\s*\n", "\n", cell_content)
                    
                    content_matrix[int(row_index)][int(col_index)] = cell_content
                    #print content_matrix[int(row_index)]
                    #print "-------------------------------"
            #print content_matrix
            
            for row in content_matrix:
                # This is used to handle the case in which a cell have multiple lines
                lines = []
                lines.append("")
                # Foreach cell in the row, get its content
                for itemCell in row:
                    #local_lines = re.split(r"\n", itemCell)
                    #for i in range(0, len(local_lines)):
                    #if i == len(lines):
                    #lines.append("")
                        #    lines[i] = lines[i]+local_lines[i]+"\t"
                    lines[0] += itemCell+"\t"
                
                row_content = ""
                # Add a new row to the table content and the row content
                for itemLine in lines:
                    row_content += itemLine + "\n"
                    tmp_content += itemLine + "\n"
                
                #row_content = re.sub(r"\t\n", "\n", row_content)
                #tmp_content = re.sub(r"\t\n", "\n", tmp_content)
                
                # Save row content
                tmp_rcontent.append(row_content)
        #print tmp_rcontent
        # Copy information from temporary variables to class members
        self.members["_bottom"] = tmp_bottom
        self.members["_top"] = tmp_top
        self.members["_left"] = tmp_left
        self.members["_right"] = tmp_right
        
        # Copy all cells
        self.members["_objs"] = tmp_objs
        
        #Copy all grid columns
        self.members["_grid_cols"] = tmp_grid_cols
        # Copy all grid rows
        self.members["_grid_rows"] = tmp_grid_rows
        
        # Copy content
        self.members["_content"] = tmp_content
        #print "content"
        #print tmp_content
        # Copy row content
        self.members["_rcontent"] = tmp_rcontent
        #print "rcontent"
        #print tmp_rcontent
    
    def get_name(self):
        return self.members["_self"]
    
    def get_objs_ref(self):
        return self.members["_objs"]
    
    def get_content(self):
        return self.members["_content"]
    
    def get_row_content(self):
        return self.members["_rcontent"]
    
    def get_bottom_pos(self):
        return self.members["_bottom"]
    
    def get_top_pos(self):
        return self.members["_top"]
    
    def get_left_pos(self):
        return self.members["_left"]
    
    def get_right_pos(self):
        return self.members["_right"]
    
    def get_alignment(self):
        return self.members["_alignment"]
    
    
