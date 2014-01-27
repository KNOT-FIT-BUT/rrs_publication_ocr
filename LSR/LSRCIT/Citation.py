import os
import sys
import re
import codecs

class Citation:
    def __init__(self):
        
        self.authors = []
        self.contexts = []
        
        # Huydhn: volume is now an array of subvolume
        self.volumes = []
        
        self.positions = []
        self.citStrs = []
        
        self.startWordPositions = []
        self.endWordPositions = []
        
        self.selfArray = {
                            "_rawString":"", 
                            "_markerType":"", 
                            "_marker":"", 
                            "_authors":self.authors, 
                            "_title":"", 
                            "_year":"", 
                            "_publisher":"", 
                            "_location":"", 
                            "_booktitle":"", 
                            "_journal":"", 
                            "_pages":"", 
                            "_volume":self.volumes, 
                            "_number":"", 
                            "_contexts":self.contexts, 
                            "_tech":"", 
                            "_institution":"", 
                            "_editor":"", 
                            "_note":"", 
                            "_positions":self.positions, 
                            "_citStrs":self.citStrs, 
                            "_startWordPositions":self.startWordPositions, 
                            "_endWordPositions":self.endWordPositions}

    def getString(self):
        return self.selfArray["_rawString"]
        
    def setString(self, str):
        self.selfArray["_rawString"] = str
        
    def getMarkerType(self):
        return self.selfArray["_markerType"]
        
    def setMarkerType(self, marker_type):
        self.selfArray["_markerType"] = marker_type
        
    def setMarker(self, marker):
        self.selfArray["_marker"] = marker
        
    def getMarker(self):
        return self.selfArray["_marker"]
        
    def getAuthors(self):
        return self.selfArray["_authors"]
        
    def addAuthor(self, author):
        authors = self.selfArray["_authors"]
        authors.append(author)
        self.selfArray["_authors"] = authors
        
    def getContexts(self):
        return self.selfArray["_contexts"]
        
    def addContext(self, context):
        contexts = self.selfArray["_contexts"]
        contexts.append(context)
        self.selfArray["_contexts"] = contexts
        
    def getVolumes(self):
        return self.selfArray["_volume"]
        
    def addVolume(self, volume):
        volumes = self.selfArray["_volume"]
        volumes.append(volume)
        self.selfArray["_volume"] = volumes
        
    def getTitle(self):
        return self.selfArray["_title"]
        
    def setTitle(self, title):
        self.selfArray["_title"] = title
        
    def getTech(self):
        return self.selfArray["_tech"]
        
    def setTech(self, tech):
        self.selfArray["_tech"] = tech
        
    def getNote(self):
        return self.selfArray["_note"]
        
    def setNote(self, note):
        self.selfArray["_note"] = note
        
    def getDate(self):
        return self.selfArray["_year"]
        
    def setDate(self, date):
        self.selfArray["_year"] = date
        
    def getLocation(self):
        return self.selfArray["_location"]
        
    def setLocation(self, location):
        self.selfArray["_location"] = location
        
    def getPublisher(self):
        return self.selfArray["_publisher"]
        
    def setPublisher(self, publisher):
        self.selfArray["_publisher"] = publisher
        
    def getBooktitle(self):
        return self.selfArray["_booktitle"]
        
    def setBooktitle(self, booktitle):
        self.selfArray["_booktitle"] = booktitle
        
    def getJournal(self):
        return self.selfArray["_journal"]
        
    def setJournal(self, journal):
        self.selfArray["_journal"] = journal
        
    def getPages(self):
        return self.selfArray["_pages"]
        
    def setPages(self, pages):
        self.selfArray["_pages"] = pages
        
    def getEditor(self):
        return self.selfArray["_editor"]
        
    def setEditor(self, editor):
        self.selfArray["_editor"] = editor
        
    def getInstitution(self):
        return self.selfArray["_institution"]
        
    def setInstitution(self, institution):
        self.selfArray["_institution"] = institution
        
    def setMarker(self, marker):
        self.selfArray["_marker"] = marker
        
    def isValid(self):
        authors = self.getAuthors()
        title = self.getTitle()
        venue = self.getJournal()
        date = self.getDate()
        
        rawString = self.getString()
        
        if not date:
            return 0
        
        if len(rawString) > 400:
            return 0
        
        if not venue:
            venue = self.getBooktitle()
        
        if len(authors)-1 >= 0 and (title or date):
            return 1
        
        if venue and date:
            return 1
        
        if title:
            return 1
        
        return 0
        
    def loadDataItem(self, tag, data):
        if tag == "authors":
            authors = data
            for auth in authors:
                self.addAuthor(auth)
        
        if tag == "contexts":
            contexts = data
            for context in contexts:
                self.addContext(context)
        
        if tag == "title":
            self.setTitle(data)
        
        if tag == "date":
            self.setDate(data)
        
        if tag == "journal":
            self.setJournal(data)
        
        if tag == "booktitle":
            self.setBooktitle(data)
        
        if tag == "tech":
            self.setTech(data)
        
        if tag == "location":
            self.setLocation(data)
        
        if tag == "volume":
            volumes = data
            for vol in volumes:
                self.addVolume(vol)
        
        if tag == "note":
            self.setNote(data)
        
        if tag == "editor":
            self.setEditor(data)
        
        if tag == "publisher":
            self.setPublisher(data)
        
        if tag == "pages":
            self.setPages(data)
        
        if tag == "institution":
            self.setInstitution(data)
        
        if tag == "marker":
            self.setMarker(data)
            
    def buildAuthYearMarker(self):
        authors = self.getAuthors()
        last_names = []
        
        for auth in authors:
            toks = re.split(r"\s+", auth)
            last_names.append(toks[-1])
        
        year = self.getDate()
        rtnTmp = ""
        for last_name in last_names:
            if last_name == "":
                continue
            rtnTmp += last_name + ", "
        #print rtnTmp.encode("utf-8")
        return rtnTmp + year
        
    def toXML(self):
        valid = self.isValid()
        
        if valid > 0:
            valid = "true"
        else:
            valid = "false"
            
        xml = "<citation valid=\"" + valid + "\">\n"
        
        authors = self.getAuthors()
        
        if len(authors)-1 >= 0:
            xml += "<authors>\n"
            
            for auth in authors:
                #TOHLE OPRAVIT, nemelo by nastat
                if re.search(r"^\s*$", auth) != None:
                    continue
                xml += "<author>" + auth + "</author>\n"
        
            xml += "</authors>\n"
        
        title = self.getTitle()
        if title:
            xml += "<title>" + title + "</title>\n";
        
        date = self.getDate()
        if date:
            xml += "<date>" + date + "</date>\n"
        
        journal = self.getJournal()
        if journal:
            xml += "<journal>" + journal + "</journal>\n"
        
        booktitle = self.getBooktitle()
        if booktitle:
            xml += "<booktitle>" + booktitle + "</booktitle>\n"
        
        tech = self.getTech()
        if tech:
            xml += "<tech>" + tech + "</tech>\n"
        
        volumes = self.getVolumes()
        if len(volumes) > 0:
            xml +=  "<volume>" + volumes[0] + "</volume>\n"
            
            for i in range(1, len(volumes)):
                xml += "<issue>" + volumes[i] + "</issue>\n"
        
        pages = self.getPages()
        if pages:
            xml += "<pages>" + pages + "</pages>\n"
        
        editor = self.getEditor()
        if editor:
            xml += "<editor>" + editor + "</editor>\n"
        
        publisher = self.getPublisher()
        if publisher:
            xml += "<publisher>" + publisher + "</publisher>\n"
        
        institution = self.getInstitution()
        if institution:
            xml += "<institution>" + institution + "</institution>\n"
        
        location = self.getLocation()
        if location:
            xml += "<location>" + location + "</location>\n"
        
        note = self.getNote()
        if note:
            xml += "<note>" + note + "</note>\n"
        
        contexts = self.getContexts()
        positions = self.getPositions()
        
        cit_strs = self.getCitStrs()
        
        start_wd_positions = self.getStartWordPositions()
        #print "Start wd positions"
        #print start_wd_positions
        end_word_positions = self.getEndWordPositions()
        
        if len(contexts)-1 >= 0:
            xml += "<contexts>\n"
            
            for context in contexts:
                pos = positions[0]
                del positions[0]
                
                cit_str = cit_strs[0]
                del cit_strs[0]
                start_wd_position = start_wd_positions[0]
                #print "Start wd position"
                #print start_wd_position
                del start_wd_positions[0]
                
                end_wd_position = end_word_positions[0]
                del end_word_positions[0]
                
                xml += "<context"
                xml += " position=\"" + str(pos) + "\""
                xml += " citStr=\"" + cit_str + "\""
                xml += " startWordPosition=\"" + str(start_wd_position) + "\""
                xml += " endWordPosition=\"" + str(end_wd_position) + "\""
                xml += ">" + context + "</context>\n"
            xml += "</contexts>\n"
        
        marker = self.getMarker()
        if marker:
            xml += "<marker>" + marker + "</marker>\n"
        
        rawString = self.getString()
        if rawString:
            xml += "<rawString>" + rawString + "</rawString>\n"
        
        xml += "</citation>\n"
        return xml
        
    def getPositions(self):
        return self.selfArray["_positions"]
        
    def addPosition(self, position):
        positions = self.selfArray["_positions"]
        positions.append(position)
        self.selfArray["_positions"] = positions
        
    def getCitStrs(self):
        return self.selfArray["_citStrs"]
        
    def addCitStr(self, cit_str):
        cit_strs = self.selfArray["_citStrs"]
        cit_strs.append(cit_str)
        self.selfArray["_citStrs"] = cit_strs
        
    def getStartWordPositions(self):
        return self.selfArray["_startWordPositions"]
        
    def addStartWordPosition(self, start_wd_position):
        #print "addStartWordPosition"
        #print start_wd_position
        start_wd_positions = self.selfArray["_startWordPositions"]
        for start_wd_positionItem in start_wd_position:
            start_wd_positions.append(start_wd_positionItem)
        self.selfArray["_startWordPositions"] = start_wd_positions
        
    def getEndWordPositions(self):
        return self.selfArray["_endWordPositions"]
        
    def addEndWordPosition(self, end_word_position):
        end_word_positions = self.selfArray["_endWordPositions"]
        for end_word_positionItem in end_word_position:
            end_word_positions.append(end_word_positionItem)
        #end_word_positions.append(end_word_position)
        self.selfArray["_endWordPositions"] = end_word_positions
