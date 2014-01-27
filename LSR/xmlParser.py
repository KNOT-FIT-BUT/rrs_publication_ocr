#!/usr/bin/python
#!/usr/bin/python
# -*- coding: utf-8 -*-
#XQR:xbreit00

import optparse
import sys
import re
import codecs

help = ""
input = ""
output = ""
query = ""
qf = ""
n = ""
root = ""
parrent = ""
file = ""
filedata = ""

XML_ROOT = 0;
XML_PROLOG = 1;
XML_TAG = 2;
XML_TAG_SHORT = 3;
XML_ATTR_NAME = 4;
XML_ATTR_DATA = 5;
XML_TEXT = 6;

""" TRIDA PRO PARSER XML """
class XMLUnit:
    def __init__(self):
        self.text = ""
        self.data = 0
        self.style = 0
        self.child = []
        self.childrenCount = 0
        #print "Objekt vytvoren\n"

    def LoadFile(self,inputFile):
        #otevreni, precteni a uzavreni souboru
        try:
            file = open(inputFile, "rt")
        except IOError:
            sys.stderr.write("Chyba pri otevirani souboru\n")
            sys.exit(2)
        try:
            filedata = file.read()
            #print filedata
            file.close()
        except UnicodeDecodeError:
            sys.stderr.write("Chyba: Nelze nacist vstupni soubor\n")
            sys.exit(255)
        #odstrani neporadek na zacatku
        filedata = re.sub(r"\s*<", "<", filedata, 1)
        #odstrani vsechny komentare
        filedata = re.sub(r"<!--[^-]*-->","",filedata)
        #parsovani
        self.ParseXML(filedata)

    def ParseXML(self,readedData):
        self.data = 0
        result = self.LoadXML(self,readedData)

    def LoadXML(self,currentObject,readedData):
        retArray = []
        while True:
            if readedData == "":
                break
            readedData = re.sub("\s*","",readedData,1)
            if re.match(r"<",readedData):
                if re.match(r"</", readedData):
                    readedData = re.sub(r"</[^>]*>","",readedData,1)
                    retArray.append(currentObject)
                    retArray.append(readedData)
                    return retArray
                if re.match(r"<\?", readedData):
                    retObject = self.LoadXML_Prolog(currentObject,readedData)
                    readedData = retObject[1]
                else:
                    retObject = self.LoadXML_Tag(currentObject,readedData)
                    readedData = retObject[1]
            else:
                retObject = self.LoadXML_Text(currentObject, readedData)
                readedData = retObject[1]
        retArray.append(currentObject)
        retArray.append(readedData)
        return retArray

    def LoadXML_Text(self,currentObject,text):
        retArray = []
        result = re.match(r"([^<]*)",text)
        result = result.group(0)
        text = re.sub(r"[^<]*","",text,1)
        result = re.sub(r"\s*$","",result)
        newObject = XMLUnit()
        newObject.Set(result,6)
        currentObject.child.append(newObject)
        currentObject.childrenCount += 1
        retArray.append(newObject)
        retArray.append(text)
        return retArray

    def LoadXML_Prolog(self,currentObject,text):
        retArray = []
        result = re.match(r"(<[^>]*>)",text)
        result = result.group(0)
        text = re.sub(r"<[^>]*>","",text,1)
        result = re.sub(r"<\?","",result)
        result = re.sub(r"\?>","",result)
        temp = XMLUnit()
        temp.text = result
        newObject = self.LoadXML_NameAndAttr(currentObject,temp,1)
        retArray.append(newObject)
        retArray.append(text)
        return retArray

    def LoadXML_Tag(self,currentObject,text):
        retArray = []
        if re.match(r"<[^<]*/>",text) != None:
            retObject = self.LoadXML_Tag_Short(currentObject,text)
        else:
            retObject = self.LoadXML_Tag_Normal(currentObject,text)
        retArray.append(retObject[0])
        retArray.append(retObject[1])
        return retArray

    def LoadXML_Tag_Short(self,currentObject,text):
        retArray = []
        result = re.match(r"(<[^>]*>)",text)
        result = result.group(0)
        text = re.sub(r"<[^>]*>","",text,1)
        result = re.sub(r"<","",result)
        result = re.sub(r">","",result)
        temp = XMLUnit()
        temp.text = result
        newObject = self.LoadXML_NameAndAttr(currentObject,temp,3)
        retArray.append(newObject)
        retArray.append(text)
        return retArray

    def LoadXML_Tag_Normal(self,currentObject,text):
        retArray = []
        result = re.match(r"(<[^>]*>)",text)
        result = result.group(0)
        text = re.sub(r"<[^>]*>","",text,1)
        result = re.sub(r"<","",result)
        result = re.sub(r">","",result)
        temp = XMLUnit()
        temp.text = result
        newObject = self.LoadXML_NameAndAttr(currentObject,temp,3)
        returnResult = self.LoadXML(newObject,text)
        retArray.append(returnResult[0])
        retArray.append(returnResult[1])
        return retArray

    #metoda nacita attributy a jejich hodnoty
    def LoadXML_NameAndAttr(self,currentObject,textObject,data):
        strName = XMLUnit()
        result = re.match(r"(\w+)", textObject.text)
        strName.text = result.group(0)
        textObject.text = re.sub(r"\w+\s*","",textObject.text,1)
        
        newObject = XMLUnit()
        newObject.Set(strName.text,data)

        while True:
            if re.match(r"\w+", textObject.text) != None:
                result = re.match(r"(\w+)",textObject.text)
            else:
                break
            newAttr = XMLUnit()
            newAttr.Set(result.group(0),4)
            
            textObject.text = re.sub(r"\w+\s*=\s*\"","",textObject.text,1)
            result = re.match(r"([^\"]*)",textObject.text)
            newData = XMLUnit()
            newData.Set(result.group(0),5)
            textObject.text = re.sub(r"[^\"]*\"\s*","",textObject.text,1)

            newAttr.child.append(newData)
            newAttr.childrenCount += 1
            
            newObject.child.append(newAttr)
            newObject.childrenCount += 1

        currentObject.child.append(newObject)
        currentObject.childrenCount += 1

        return newObject
    
    def GetXMLStr(self, currentObject, deep, resStr):
        #0 == root
        if not currentObject.data == 0:
            resStr += "<" + currentObject.text
        
        cnt = 0
        for item in currentObject.child:
            if item.data == 4:
                cnt += 1
        
        tmpCnt = 0
        if tmpCnt == cnt and not currentObject.data == 0:
            resStr += ">\n"
        
        for item in currentObject.child:
            #attribut
            if item.data == 4:
                resStr += " " + item.text + "=" + "\"" + item.child[0].text + "\""
                tmpCnt += 1
                
                if tmpCnt == cnt:
                    resStr += ">\n"
            
            #text
            if item.data == 6:
                resStr += item.text + "\n"
            
            #tag
            if item.data == 3:
                resStr = item.GetXMLStr(item, deep+1, resStr)
        
        if not currentObject.data == 0:
            resStr += "</" + currentObject.text + ">\n"
        
        return resStr

    #metoda pro tisk elementu a vsech jeho potomku. Udava se pocatecni
    #objekt tridy XMLUnit, hloubka, ktera znaci, o kolik tabulatoru se ma
    #odsazovat a pocet atributu, ktere dany objekt obsahuje.
    def PrintOutput(self,currentObject,deep,cnt):
        for index in range(len(currentObject.child)):
            cntAttr = 0
            for index2 in range(len(currentObject.child[index].child)):
                if currentObject.child[index].child[index2].data == 4:
                    cntAttr = cntAttr + 1

            if currentObject.child[index].data == 3:
                sys.stdout.write(deep * "" + "<" + currentObject.child[index].text)
                currentObject.PrintOutput(currentObject.child[index],deep+1,cntAttr)
                sys.stdout.write(deep * "" + "</" + currentObject.child[index].text + ">" + "\n")
            if currentObject.child[index].data == 4:
                sys.stdout.write(" " + currentObject.child[index].text + "=")
                currentObject.PrintOutput(currentObject.child[index],deep+1,cntAttr)
                if cnt > 0 and cnt-1 == index and (deep == 1 or deep == 2):
                    sys.stdout.write(">\n")
            if currentObject.child[index].data == 5:
                sys.stdout.write("\"" + currentObject.child[index].text + "\"")
                currentObject.PrintOutput(currentObject.child[index],deep+1,cntAttr)
            if currentObject.child[index].data == 6:
                sys.stdout.write(">\n" + deep * "" + currentObject.child[index].text + "\n")
                currentObject.PrintOutput(currentObject.child[index],deep+1,cntAttr)

    #tisk DOM stromu na standardni vystup
    def PrintChild(self,currentObject,deep):
        #print range(len(currentObject.child))
        for index in range(len(currentObject.child)):
            if currentObject.child[index].data == 1:
                sys.stdout.write(deep * "-" + "<?" + currentObject.child[index].text + ">\n")
            if currentObject.child[index].data == 3:
                sys.stdout.write(deep * "-" + "<" + currentObject.child[index].text + ">\n")
            if currentObject.child[index].data == 4:
                sys.stdout.write(deep * "-" + currentObject.child[index].text + "=\n")
            if currentObject.child[index].data == 5:
                sys.stdout.write(deep * "-" + "\"" + currentObject.child[index].text + "\"\n")
            if currentObject.child[index].data == 6:
                sys.stdout.write(deep * "-" + currentObject.child[index].text + "\n")
            currentObject.PrintChild(currentObject.child[index],deep+1)

    #metoda prohledava strom a hleda element obsahujici attribut s nazvem @name
    def SearchAttr(self,currentObject,name):
        for index in range(len(currentObject.child)):
            if currentObject.child[index].text == name and currentObject.child[index].data == 4:
                return currentObject
            retObject = currentObject.SearchAttr(currentObject.child[index],name)
            if retObject:
                return retObject	

    def SearchAttrW(self,currentObject,name):
        for index in range(len(currentObject.child)):
            if currentObject.child[index].text == name and currentObject.child[index].data == 4:
                return currentObject.child[index].child[0]
            retObject = currentObject.SearchAttrW(currentObject.child[index],name)
            if retObject:
                return retObject
    
    #metoda hleda element s nazvem @name
    def SearchElem(self,currentObject,name):
        if currentObject.data == 3 and currentObject.text == name:
            return currentObject
        for index in range(len(currentObject.child)):
            retObject = currentObject.SearchElem(currentObject.child[index],name)
            if retObject:
                return retObject
    
    """
    #metoda hleda element s nazvem @name a vraci prvni text
    def SearchElemText(self,currentObject,name):
        if currentObject.data == 3 and currentObject.text == name:
            return currentObject
        for index in range(len(currentObject.child)):
            retObject = currentObject.SearchElem(currentObject.child[index],name)
            if retObject:
                for indexChild in range(len(retObject.child)):
                    if retObject.child[indexChild].data == 6:
                        return retObject.child[indexChild].text
    """
    #metoda hleda element s nazvem @name a vraci prvni text
    def SearchElemText(self,currentObject,name):
        if currentObject.data == 3 and currentObject.text == name:
            for indexChild in range(len(currentObject.child)):
                if currentObject.child[indexChild].data == 6:
                    return currentObject.child[indexChild].text
            #return currentObject
        for index in range(len(currentObject.child)):
            retObject = currentObject.SearchElemText(currentObject.child[index],name)
            if retObject:
                return retObject

    #metoda hleda element s nazven @name a pokud jeho prvni potomek je text,
    #pak metoda vraci odkaz na tento text.
    def SearchElemW(self,currentObject,name):
        if currentObject.data == 3 and currentObject.text == name:
            for index in range(len(currentObject.child)):
                if int(index) == 0 and currentObject.child[index].data == 6:
                    return currentObject.child[index]
        for index in range(len(currentObject.child)):
            retObject = currentObject.SearchElemW(currentObject.child[index],name)
            if retObject:
                return retObject

    #metoda hleda elemenent s nazvem @element a atributem @attribut
    def SearchElemAttr(self,currentObject,element,attribut):
        if currentObject.text == element and currentObject.data == 3:
            for index in range(len(currentObject.child)):
                if currentObject.child[index].text == attribut and currentObject.child[index].data == 4:
                    return currentObject
        for index in range(len(currentObject.child)):
            retObject = currentObject.SearchElemAttr(currentObject.child[index],element,attribut)
            if retObject:
                return retObject

    def SearchElemAttrW(self,currentObject,element,attribut):
        if currentObject.text == element and currentObject.data == 3:
            for index in range(len(currentObject.child)):
                if currentObject.child[index].text == attribut and currentObject.child[index].data == 4:
                    return currentObject.child[index].child[0]
        for index in range(len(currentObject.child)):
            retObject = currentObject.SearchElemAttrW(currentObject.child[index],element,attribut)
            if retObject:
                return retObject

    def Set(self,text,data):
        self.text = text
        self.data = data

    #metoda uklada do seznamu vsechny elementy, ktere nesou nazev @element
    def Select(self,currentObject,element,selArray):
        for index in range(len(currentObject.child)):
            if currentObject.child[index].text == element and currentObject.child[index].data == 3:
                selArray.append(currentObject.child[index])
            selArray = currentObject.Select(currentObject.child[index],element,selArray)
        return selArray
    
    #metoda z DOM stromu vytahne vsechny texty a ulozi je do jednoho retezce
    def GetText(self, currentObject):
        retStr = ""
        for index in range(len(currentObject.child)):
            if currentObject.child[index].data == XML_TEXT:
                retStr = retStr + " " + currentObject.child[index].text
            tmpStr = self.GetText(currentObject.child[index])
            if tmpStr:
                retStr = retStr + " " + tmpStr
        return retStr
        
    #metoda pro seznam @currentObject vola metodu GetText
    def GetRaw(self, currentObject):
        retStr = ""
        for index in range(len(currentObject)):
            retStr = retStr + self.GetText(currentObject[index]) + "\n"
        return retStr
            
    
#""" PARSOVANI XML """
#def parseXML():
#	parrent = XMLUnit()
#	parrent.text = "ROOT"
#	parrent.LoadFile(input)
#	return parrent

#""" MAIN """
#def main():
	#parsedXML = parseXML()
