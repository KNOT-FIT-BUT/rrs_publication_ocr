#!/usr/bin/python
# -*- coding: utf-8 -*-

import optparse
import sys
import re
import os
import codecs
import subprocess
import xmlParser
import rtfParser
import rtfParserNew

from time import time

debug = False
test = True

LSRCIT = 1
LSRHED = 2
LSRLABEL = 4

default_input_type = "raw"
output_version = "131024"
#biblio_script
default_mode = LSRLABEL

tmpfile = "LSR"
input = ""
opt_m = ""
opt_t = ""
opt_i = ""
output_file = ""

# CTRL-C handler
def quitHandler():
    sys.stderr.write("Recieved a SIGINT!\n")
    
#================== KONTROLA ARGUMENTU ==================
def checkArguments():
    global input
    global opt_m
    global opt_i
    global output_file

    arg = optparse.OptionParser(add_help_option=False)
    arg.disable_interspersed_args()

    arg.add_option("--help", action="store_true", dest="help",
            help="tisk napovedy", default=False)
    arg.add_option("--input", dest="input", help="vstupni RTF soubor",
            metavar="input", default=False)
    arg.add_option("-m", dest="m", help="mode",
            metavar="m", default=False)
    arg.add_option("-i", dest="i", help="input type",
            metavar="i", default=False)
    arg.add_option("--output", dest="output", help="vystupni XML soubor",
    		metavar="output", default=False)

    (options, args) = arg.parse_args()
    if options.help:
        if len(sys.argv) > 2:
            sys.stderr.write("Spatne zadani parametru!\n")
            sys.exit(1)
        else:
            arg.print_help()
            sys.exit(0)
            
    if options.input == False:
        sys.stderr.write("Nebyl zadan parametr input!\n")
        sys.exit(1)

    input = options.input
    if options.m:
        opt_m = options.m
    
    output_file = options.output
    if options.i:
        opt_i = options.i
    return

def RemoveTopLines(input, top_n):
    #remove first line <?xml/>
    input = re.sub(r".*", "", input, top_n)
    return input

def ParseMode(arg):
    if arg == "extract_meta":
        return (LSRCIT | LSRHED)
    elif arg == "extract_header":
        return LSRHED
    elif arg == "extract_citations":
        return LSRCIT
    elif arg == "extract_section":
        return LSRLABEL
    elif arg == "extract_all":
        return (LSRHED | LSRCIT | LSRLABEL)
    elif arg == "extract_nocit":
        return (LSRHED|LSRLABEL)
    else:
        sys.stderr.write("Spatne zadany parametr mode\n")
        sys.exit(1)

#Funkce nastavuje, ktery model pro CRF system bude pouzit, dale mapuje
#slovniky a konfiguracni soubory(ty by mely byt nevyuzity)
#Jako posledni vola funkci ExtractSection() v modulu Controller, kde se provadi
#rizeni klasifikace. Pozn.: Kod je napsan tak, ze for_cit je vzdy 0 a vystup bude
#vzdy v XML formatu
#
#@param1 vstupni soubor
#@param2 zda se pracuje s RTF souborem nebo jen se surovym textem
#@param3 vzdy 0
#@return pole, kde prvni prvek je vysledek predany modulem Controller
def LSRLabel(text_file, is_rtf_input, for_cit):
    sys.path.append("./LSRLabel/")
    import Config
    import Controller
    
    is_xml_output = 1
    
    #namapovani modelu CRF
    if is_rtf_input:
        model_file = "./LSRLabel/Resources/sectLabel.modelXml.v2"
    else:
        model_file = "./LSRLabel/Resources/sectLabel.model"
    
    #namapovani slovniku
    dict_file = "./LSRLabel/Resources/parsCitDict.txt"
    
    #namapovani func
    func_file = "./LSRLabel/Resources/funcWord"
    
    #namapovani konfiguracniho souboru
    if is_rtf_input:
        config_file = "LSRLabel/Resources/sectLabel.configXml"
    else:
        config_file = "LSRLabel/Resources/sectLabel.config"
    
    #sekce klasifikace
    retArray = []
    if not for_cit:
        retArray = Controller.ExtractSection(text_file, is_xml_output, model_file, dict_file, func_file, config_file, is_rtf_input, for_cit)
        return retArray
    else:
        retArray = Controller.ExtractSection(text_file, is_xml_output, model_file, dict_file, func_file, config_file, is_rtf_input, for_cit)
        return retArray

#TODO: Okomentovat a pripadne odstranit nepotrebne veci
def CorSection(xmlData):
    xml = xmlParser.XMLUnit()
    xml.ParseXML(xmlData)
    
    sectionLabel = {"NUM":0, 
                              "ROME":0, 
                              "NONE":0}
    
    subsectionLabel = {"NUMPNUM": 0, 
                                   "ALPHA":0}
    
    knownSections = {"ABSTRACT":"", 
                                  "INTRODUCTION":"", 
                                  "REFERENCES":"", 
                                  "ACKNOWLEDGMENT":"", 
                                  "ACKNOWLEDGEMENT":"", 
                                  "ACKNOWLEDGMENTS":"", 
                                  "ACKNOWLEDGEMENTS":"", 
                                  "CONCLUSION":"", 
                                  "CONCLUSIONS":"", 
                                  "CONCLUSION AND FUTURE WORK":"", 
                                  "CATEGORIES AND SUBJECT DESCRIPTORS":"", 
                                  "GENERAL TERMS":"", 
                                  "KEYWORDS":"", 
                                  "DISCUSSION":"", 
                                  "RESULTS":"", 
                                  "RESULTS AND DISCUSSION":"", 
                                  "LITERATURVERZEICHNIS":"", 
                                  "EXPERIMENT":""}
    
    #ziskani vysledky jednotlivych casti klasifikace
    algorithm = xml.Select(xml, "algorithm", [])
    
    #obecna klasifikace
    if algorithm == []:
        sys.stderr.write("Korekce nadpisu: Nic ke zmene\n")
        #sys.stdout.write("Korekce nadpisu: XML_No_alg\n")
        return xmlData
    else:
        xmlAlg = algorithm[0]
    
    #ziskani vsech nadpisu
    sections = xml.Select(xml, "sectionHeader", [])
    
    if sections == []:
        sys.stderr.write("Korekce nadpisu: Nic ke zmene\n")
        #sys.stdout.write("Korekce nadpisu: XML_No_Sec\n")
        return xmlData
    
    #ziskani formy nadpisu
    knownCnt = 0
    for itemSec in sections:
        #sys.stderr.write("ziskani formy nadpisu\n")
        #ziskani nadpisu
        xmlSectionsText = itemSec.child[1]
        
        #ziskani textu reference
        xmlSectionsTextData = xmlSectionsText.text
        
        #print xmlSectionsTextData.encode('utf-8').strip()
        
        #NUM
        if re.search(r"^\s*\d+((\.\s*)|(\s+))(([A-Z](\-)?([a-zA-Z]+)?|\d(\-)?D)\s*)?(\()?[a-zA-Z](\w+\s*)+", xmlSectionsTextData):
            #print "NUM +1"
            sectionLabel["NUM"] += 1
        #ROME
        elif re.search(r"^\s*(IX|IV|V?I{0,3})((\.\s*)|(\s+))(([A-Z](\-)?([a-zA-Z]+)?|\d(\-)?D)\s*)?(\()?[a-zA-Z](\w+\s*)+", xmlSectionsTextData):
            #print "ROME +1"
            sectionLabel["ROME"] += 1
        else:
            tmpSec = xmlSectionsTextData
            tmpSec  = re.sub(r"^\s*", "", tmpSec, 1)
            tmpSec = re.sub(r"\s*$", "", tmpSec, 1)
            
            if knownSections.has_key(tmpSec):
                knownCnt += 1
        #NONE
        #elif re.search(r"^\s*\w{5,}", xmlSectionsTextData):
        #    #print "!!!" + xmlSectionsTextData
        #    sectionLabel["NONE"] += 1
    
    sectionLabel = sorted(sectionLabel.items(), key=lambda x:x[1])
    
    #print sectionLabel
    #print sectionLabel[-1][0] + "\n"
    
    labelSec = sectionLabel[-1][0]
    
    if sectionLabel[-1][1] == 0:
        sys.stderr.write("Korekce nadpisu: Nic ke zmene\n")
        #sys.stdout.write("Korekce nadpisu: Spatny tvar nadpisu\n")
        return xmlData
    
    #oprava nadpisu na bodyText
    changeBadSec = False
    
    #print "oprava nadpisu na bodyText"
    if ((float(int(sectionLabel[-1][1]) + knownCnt))/float(len(sections))) > 0.25:
        itemCnt = 0
        for itemSec in sections:
            #sys.stderr.write("oprava nadpisu na bodyText\n")
            #sys.stderr.write(itemSubSec.data)
            xmlSectionsText = itemSec.child[1]
            
            xmlSectionsTextData = xmlSectionsText.text
            
            #print xmlSectionsTextData.encode('utf-8').strip()
            #sys.stderr.write(xmlSectionsTextData.encode('utf-8').strip()+"\n")
            
            #if ((labelSec == "ROME" and not re.search(r"^\s*M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})((\.\s*)|(\s+))\w{3,}", xmlSectionsTextData)) or (labelSec == "NUM" and not re.search(r"^\s*\d+((\.\s*)|(\s+))[a-zA-Z]{3,}", xmlSectionsTextData))):
            if ((labelSec == "ROME" and not re.search(r"^\s*(IX|IV|V?I{0,3})((\.\s*)|(\s+))(([A-Z](\-)?([a-zA-Z]+)?|\d(\-)?D)\s*)?(\()?[a-zA-Z](\w+\s*)+", xmlSectionsTextData)) or (labelSec == "NUM" and not re.search(r"^\s*\d+((\.\s*)|(\s+))(([A-Z](\-)?([a-zA-Z]+)?|\d(\-)?D)\s*)?(\()?[a-zA-Z](\w+\s*)+", xmlSectionsTextData))):
                #sys.stderr.write("IF DONE\n")
                #sys.stderr.write(xmlSectionsTextData.encode('utf-8').strip()+"\n")
                xmlSectionsTextData = re.sub(r"^\s*", "", xmlSectionsTextData, 1)
                xmlSectionsTextData = re.sub(r"\s*$", "", xmlSectionsTextData, 1)
                xmlSectionsTextData = xmlSectionsTextData.upper()
                #print "SECUPPER"
                #print xmlSectionsTextData.encode('utf-8').strip()
                
                if not (knownSections.has_key(xmlSectionsTextData) or re.search(r"^APPENDIX\s+[A-Z]$", xmlSectionsTextData)):
                    changeBadSec = True
                    if itemCnt == 0:
                        #sys.stderr.write("SPATNY NADPIS NALEZENO - Zmena na titul\n")
                        #sys.stdout.write("SPATNY NADPIS NALEZENO - Zmena na titul\n")
                        itemSec.text = "title"
                    else:
                        #sys.stderr.write("SPATNY NADPIS NALEZENO\n")
                        #sys.stdout.write("SPATNY NADPIS NALEZENO\n")
                        itemSec.text = "bodyText"
            itemCnt += 1
    
    #print ""
    
    #ziskani vsech podnadpisu
    subsections = xml.Select(xml, "subsectionHeader", [])
    
    if subsections == []:
        sys.stderr.write("Korekce nadpisu: Podnadpisy nenalezeny\n")
        #sys.stdout.write("Korekce nadpisu: XML_No_SubSec\n")
        if changeBadSec:
            sys.stderr.write("Korekce nadpisu: Korekce provedeny\n")
            secStr = xml.GetXMLStr(xml, 0, "")
            secStr = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + secStr
            return secStr
        
        return xmlData
    
    #ziskani formy podnadpisu
    for itemSubSec in subsections:
        #sys.stderr.write("ziskani formy podnadpisu\n")
        #ziskani nadpisu
        xmlSubSectionsText = itemSubSec.child[1]
        
        xmlSubSectionsTextData = xmlSubSectionsText.text
        
        #print xmlSubSectionsTextData.encode('utf-8').strip()
        
        #NUMPNUM
        if re.search(r"^\s*\d+\.\d+((\.\s*)|(\s+))(([A-Z](\-)?([a-zA-Z]+)?|\d(\-)?D)\s*)?(\()?[a-zA-Z](\w+\s*)+", xmlSubSectionsTextData):
            #print "NUMPNUM +1"
            subsectionLabel["NUMPNUM"] += 1
        #ALPHA
        elif re.search(r"^\s*[A-E]((\.\s*)|(\s+))(([A-Z](\-)?([a-zA-Z]+)?|\d(\-)?D)\s*)?(\()?[a-zA-Z](\w+\s*)+", xmlSubSectionsTextData):
            #print "ALPHA +1"
            subsectionLabel["ALPHA"] += 1
        #NONE
        #elif re.search(r"^\s*\w{5,}", xmlSectionsTextData):
        #    #print "!!!" + xmlSectionsTextData
        #    sectionLabel["NONE"] += 1
    
    subsectionLabel = sorted(subsectionLabel.items(), key=lambda x:x[1])
    
    #print subsectionLabel
    #print subsectionLabel[-1][0] + "\n"
    
    labelSubSec = subsectionLabel[-1][0]
    
    if subsectionLabel[-1][1] == 0:
        sys.stderr.write("Korekce nadpisu: Nic ke zmene\n")
        #sys.stdout.write("Korekce nadpisu: Spatny tvar nadpisu\n")
        if changeBadSec:
            sys.stderr.write("Korekce nadpisu: Korekce provedeny\n")
            secStr = xml.GetXMLStr(xml, 0, "")
            secStr = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + secStr
            return secStr
        
        return xmlData
    
    #ziskani formy podnadpisu na bodyText
    changeBadSubSec = False
    for itemSubSec in subsections:
        #sys.stderr.write("ziskani formy podnadpisu na bodyText\n")
        #sys.stdout.write("ziskani formy podnadpisu na bodyText\n")
        
        #ziskani nadpisu
        xmlSubSectionsText = itemSubSec.child[1]
        
        xmlSubSectionsTextData = xmlSubSectionsText.text
        
        #print xmlSubSectionsTextData.encode('utf-8').strip()
        
        if ((labelSec == "ROME" and not re.search(r"^\s*(IX|IV|V?I{0,3})((\.\s*)|(\s+))(([A-Z](\-)?([a-zA-Z]+)?|\d(\-)?D)\s*)?(\()?[a-zA-Z](\w+\s*)+", xmlSubSectionsTextData)) or (labelSec == "NUM" and not re.search(r"^\s*\d+((\.\s*)|(\s+))(([A-Z](\-)?([a-zA-Z]+)?|\d(\-)?D)\s*)?(\()?[a-zA-Z](\w+\s*)+", xmlSubSectionsTextData))):
            if (labelSubSec == "NUMPNUM" and not re.search(r"^\s*\d+\.\d+((\.\s*)|(\s+))(([A-Z](\-)?([a-zA-Z]+)?|\d(\-)?D)\s*)?(\()?[a-zA-Z](\w+\s*)+", xmlSubSectionsTextData)) or (labelSubSec == "ALPHA" and not re.search(r"^\s*[A-E]((\.\s*)|(\s+))(([A-Z](\-)?([a-zA-Z]+)?|\d(\-)?D)\s*)?(\()?[a-zA-Z](\w+\s*)+", xmlSubSectionsTextData)):
                #sys.stderr.write(xmlSectionsTextData.encode('utf-8').strip()+"\n")
                xmlSubSectionsTextData = re.sub(r"^\s*", "", xmlSubSectionsTextData, 1)
                xmlSubSectionsTextData = re.sub(r"\s*$", "", xmlSubSectionsTextData, 1)
                xmlSubSectionsTextData = xmlSubSectionsTextData.upper()
                #print "SUBUPPER"
                #print xmlSubSectionsTextData.encode('utf-8').strip()
                
                if knownSections.has_key(xmlSubSectionsTextData) or re.search(r"^APPENDIX\s+[A-Z]$", xmlSubSectionsTextData):
                    changeBadSubSec = True
                    #sys.stderr.write("KNOWNSEC NALEZENO\n")
                    #sys.stdout.write("KNOWNSEC NALEZENO\n")
                    itemSubSec.text = "sectionHeader"
                else:
                    changeBadSubSec = True
                    #sys.stderr.write("SPATNY PODNADPIS NALEZENO\n")
                    #sys.stdout.write("SPATNY PODNADPIS NALEZENO\n")
                    itemSubSec.text = "bodyText"
    
    #oprava nadpisu
    changeSec = False
    #print "oprava nadpisu"
    for itemSubSec in subsections:
        #sys.stderr.write("oprava nadpisu\n")
        #sys.stderr.write(itemSubSec.data)
        xmlSubSectionsText = itemSubSec.child[1]
        
        xmlSubSectionsTextData = xmlSubSectionsText.text
        
        #print xmlSubSectionsTextData.encode('utf-8').strip()
        
        if labelSec == "ROME" and re.search(r"^\s*(IX|IV|V?I{0,3})((\.\s*)|(\s+))(([A-Z](\-)?([a-zA-Z]+)?|\d(\-)?D)\s*)?(\()?[a-zA-Z](\w+\s*)+", xmlSubSectionsTextData):
            changeSec = True
            #sys.stderr.write("ROME NALEZENO\n")
            #sys.stdout.write("ROME NALEZENO\n")
            itemSubSec.text = "sectionHeader"
        
        elif labelSec == "NUM" and re.search(r"^\s*\d+((\.\s*)|(\s+))(([A-Z](\-)?([a-zA-Z]+)?|\d(\-)?D)\s*)?(\()?[a-zA-Z](\w+\s*)+", xmlSubSectionsTextData):
            changeSec = True
            #sys.stderr.write("NUM NALEZENO\n")
            #sys.stdout.write("NUM NALEZENO\n")
            itemSubSec.text = "sectionHeader"
    
    #oprava podnadpisu
    #TODO: Pripadne udelat novy dotaz v XML, at se vyradi ty jiz opravene nadpisy na bodyText
    changeSubSec = False
    #print "oprava podnadpisu"
    for itemSec in sections:
        #sys.stderr.write("oprava podnadpisu\n")
        #sys.stderr.write(itemSubSec.data)
        xmlSectionsText = itemSec.child[1]
        
        xmlSectionsTextData = xmlSectionsText.text
        
        #print xmlSectionsTextData.encode('utf-8').strip()
        
        if labelSubSec == "NUMPNUM" and re.search(r"^\s*\d+\.\d+((\.\s*)|(\s+))(([A-Z](\-)?([a-zA-Z]+)?|\d(\-)?D)\s*)?(\()?[a-zA-Z](\w+\s*)+", xmlSectionsTextData):
            changeSubSec = True
            #sys.stderr.write("NUMPNUM NALEZENO\n")
            #sys.stdout.write("NUMPNUM NALEZENO\n")
            itemSec.text = "subsectionHeader"
        
        elif labelSubSec == "ALPHA" and re.search(r"^\s*[A-E]((\.\s*)|(\s+))(([A-Z](\-)?([a-zA-Z]+)?|\d(\-)?D)\s*)?(\()?[a-zA-Z](\w+\s*)+", xmlSectionsTextData):
            changeSubSec = True
            #sys.stderr.write("ALPHA NALEZENO\n")
            #sys.stdout.write("ALPHA NALEZENO\n")
            itemSec.text = "subsectionHeader"
        
        #elif ((labelSec == "ROME" and not re.search(r"^\s*M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})((\.\s*)|(\s+))\w{3,}", xmlSectionsTextData)) or (labelSec == "NUM" and not re.search(r"^\s*\d+((\.\s*)|(\s+))[a-zA-Z]{3,}", xmlSectionsTextData))):
        #    #sys.stderr.write(xmlSectionsTextData+"\n")
        #    section = re.search(r"^[a-zA-Z]+((\s*\w+)+)?$", xmlSectionsTextData).group(0)
        #    section = section.upper()
        #    print "SECUPPER"
        #    print section
        #    if not knownSections.has_key(section):
        #        changeSubSec = True
        #        sys.stderr.write("SPATNY NADPIS NALEZENO\n")
        #        sys.stdout.write("SPATNY NADPIS NALEZENO\n")
        #        itemSec.text = "bodyText"
    
    secStr = xml.GetXMLStr(xml, 0, "")
    secStr = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + secStr
    #secStr = re.sub(r"(\n)+</algorithms>(\n)+", "", secStr)
    if changeSec or changeSubSec or changeBadSec or changeBadSubSec:
        sys.stderr.write("Korekce nadpisu: Korekce provedeny\n")
        #sys.stdout.write("Korekce nadpisu: Korekce provedeny\n")
        #print secStr.encode('utf-8').strip()
        #print "\n\n"
        return secStr
        #a=raw_input()
    else:
        sys.stderr.write("Korekce nadpisu: Nic ke zmene\n")
        #sys.stdout.write("Korekce nadpisu: Nic ke zmene\n")
    
    #sys.exit(0)
    return xmlData

def ModifyReferences(xmlData):
    xml = xmlParser.XMLUnit()
    xml.ParseXML(xmlData)
    
    #ziskani vysledky jednotlivych casti klasifikace
    algorithm = xml.Select(xml, "algorithm", [])
    
    #obecna klasifikace
    if algorithm == []:
        return xmlData
    else:
        xmlLabel = algorithm[0]
    
    #ziskani xmlPodstromu s referencemi
    #xmlReferences = xmlLabel.SearchElem(xmlLabel, "reference")
    xmlReferences = xmlLabel.Select(xmlLabel, "reference", [])
    #print len(xmlReferences)
    #sys.exit(0)
    
    if not xmlReferences:
        sys.stderr.write("Reference nenalezeny...\n")
        return xmlData
    
    for itemRefs in xmlReferences:
        #ziskani reference
        xmlReferencesText = itemRefs.child[1]
        
        #ziskani textu reference
        xmlReferencesTextData = xmlReferencesText.text
        #print xmlReferencesTextData
        #sys.exit(0)
        
        #rozdeleni referenci
        #1.
        if re.search(r"^\d+\.\s+", xmlReferencesTextData):
            #ziskani indexu referenci
            indexArray = re.findall(r"\n\d+\.\s+", xmlReferencesTextData)
            indexArray.insert(0, "")
            
            #rozdeleni referenci
            refArray = re.split(r"\n\d+\.\s+", xmlReferencesTextData)
            #refArray[0] = re.sub(r"^\d+\.\s+", "", refArray[0])
        #[1]
        elif re.search(r"(^\[\d+\]\s+)|(\n\[\d+\]\s+)", xmlReferencesTextData):
            xmlReferencesTextData = re.sub(r"\n\[\s*(?P<index>\d+)\s*\]", "\n[\g<index>] ", xmlReferencesTextData)
            xmlReferencesTextData = re.sub(r"\n(?P<index>\d+)\]", "\n[\g<index>] ", xmlReferencesTextData)
            xmlReferencesTextData = re.sub(r"\n\[(?P<index>\d+)\n", "\n[\g<index>] ", xmlReferencesTextData)
            xmlReferencesTextData = re.sub(r"^\[lj", "[1] ", xmlReferencesTextData)
            #print xmlReferencesTextData
            #sys.exit(0)
            
            #ziskani indexu referenci
            indexArray = re.findall(r"\n\[\d+\]\s+", xmlReferencesTextData)
            indexArray.insert(0, "")
            #print indexArray
            
            #rozdeleni referenci
            refArray = re.split(r"\n\[\d+\]\s+", xmlReferencesTextData)
            #refArray[0] = re.sub(r"^\[\d+\]\s+", "", refArray[0])
        #(1)
        elif re.search(r"^\(\d+\)\s+", xmlReferencesTextData):
            #ziskani indexu referenci
            indexArray = re.findall(r"\n\(\d+\)\s+", xmlReferencesTextData)
            indexArray.insert(0, "")
            
            #rozdeleni referenci
            refArray = re.split(r"\n\(\d+\)\s+", xmlReferencesTextData)
            #refArray[0] = re.sub(r"^\(\d+\)\s+", "", refArray[0])
        else:
            sys.stderr.write("Jiny zapis reference!!!\n")
            continue
        
        for indexCnt in range(len(indexArray)):
            indexArray[indexCnt] = re.sub(r"^\n", "", indexArray[indexCnt])
        #sys.exit(0)
        
        #odstraneni potomka, ktery se bude nahrazovat
        del itemRefs.child[1]
        
        #vytvoreni podstromu XML s jednotlivymi referencemi
        cnt = 0
        for item in refArray:
            #tag
            refTag = xmlParser.XMLUnit()
            refTag.data = 3
            refTag.text = "referenceItem"
            
            #text
            newRef = xmlParser.XMLUnit()
            newRef.data = 6
            #newRef.text = "[" + str(cnt) + "]\t" + item
            newRef.text = indexArray[cnt] + item
            
            refTag.child.append(newRef)
            itemRefs.child.append(refTag)
            cnt += 1
    
    resStr = xml.GetXMLStr(xml, 0, "")
    resStr = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + resStr
    resStr = re.sub(r"(\n)+</algorithms>(\n)+", "", resStr)
    return resStr

""" MAIN """
def main():
    global tmpfile
    global input
    global output_file
    
    if not os.path.exists("./tmp"):
        os.makedirs("./tmp")
    
    #While kdyby chtel nekdo v budoucnu timto skriptem zpracovavat
    #vice jak jeden soubor.
    while(True):
        #nastaveni tmp souboru
        tmpfile = "/tmp/" + tmpfile + str(int(time()))
        if debug:
            print "Tmpfile: " + tmpfile
     
        #kontrola parametru
        checkArguments()
    
        #nazev skriptu
        cmd_line = sys.argv[0]
        if debug:
            print "cmd_line: " + cmd_line
        
        #mod parsovani
        mode = default_mode if not opt_m else ParseMode(opt_m)
        if debug:
            print "Debug Mode: " + str(mode)
        
        #vstupni soubor RTF
        is_rtf_input = 1 if opt_i == "rtf" else 0
    
        ph_model = 1 if opt_t else 0
    
        #nastaveni jmena souboru
        input_new = re.search(r"\w+\.\w+$", input).group(0)
        input_new = "./tmp/" + input_new
        #sys.stderr.write(input_new)
        #sys.exit(0)
        out = input_new
        out = re.sub(r"\.\w+$", ".xml", out, 1)
        if debug:
            print "Debug Output: " + out
    
        #output buffer
        rxml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<algorithms version=\"" + output_version + "\">"
    
        doc = ""
        text_file = ""
        rtf = ""
        #pokud je vstup ve formatu RTF
        if is_rtf_input:
            rtf_mode = 2
            #Vytvoreni objektu tridy RTFUnit, nacteni a naparsovani vst. souboru
            #a nasledne jeho vyjadreni v podobe suroveho textu
            if rtf_mode == 1:
                rtf = rtfParser.RTFUnit()
                rtf.LoadFile(input)
                raw_text = rtf.InterpretPlainText(rtf)
                #sys.stderr.write("lsr::opravit\n")
                #sys.exit(0)
                
                xml = rtf.xmlOutput
                
                #print xml.encode('utf-8').strip()
                #sys.exit(0)
            
            else:
                inputData = rtfParserNew.LoadRTF(input)
                xml = rtfParserNew.ParseRTF(inputData)
                
                #print xml.encode('utf-8').strip()
                #sys.exit(0)
            
            #Zpracovani objektu RTFUnit
            import processOCRRTF
            
            raw_text = processOCRRTF.Entry(xml, input, input_new +".feature")
            #raw_text = re.sub(r"\s*", "", raw_text)
            
            #TODO: Zkusit a kdyztak odkomentovat
            #raw_text = re.sub(r"\n\n", "\n", raw_text)
            #print raw_text.encode('utf-8').strip()
            #sys.exit(0)
            is_rtf_input = 1
        else:
            #Nacteni suroveho textu
            text = input
            text_fd = ""
            try:
                text_fd = codecs.open(text, 'r', "utf-8")
            except IOError:
                sys.stderr.write("Nelze otevrit soubor " + text)
                sys.exit(1)
                
            raw_text = text_fd.read()
            if debug:
                print raw_text.encode("utf-8")
            
            text_fd.close()
        
        #uprava textu
        raw_text = re.sub(r"\n\n", "\n", raw_text)
        raw_text = re.sub(r"^\s+", "", raw_text)
        raw_text = re.sub(r"\n\s+", "\n", raw_text)
        raw_text = re.sub(r"(\t| )+", " ", raw_text)
        
        #Obecna klasifikace
        if mode & LSRLABEL == LSRLABEL:
            lsr_label_input = raw_text
            
            #zde je volana klasifikace pro bohaty text
            if is_rtf_input:
                address_file = input_new + ".feature" + ".address"
                address_file_fd = ""
                try:
                    address_file_fd = codecs.open(address_file, 'r', "utf-8")
                except IOError:
                    sys.stderr.write("Nelze otevrit soubor " + address_file_fd)
                    sys.exit(1)
                
                # Read the address file provided by process script
                omni_address = []
                #tmpLine = address_file_fd.readline()
                tmpLine = address_file_fd.read()
                #print tmpLine.encode('utf-8').strip()
                #sys.exit(0)
                while tmpLine:
                    #Save and split the line
                    line = tmpLine
                    element = re.split(r"\s+", line)
                    
                    addr = {}
                    #Address
                    addr["L1"] = element[0]
                    addr["L2"] = element[1]
                    addr["L3"] = element[2]
                    addr["L4"] = element[3]
                    
                    #Save the address
                    omni_address.append(addr)
                    tmpLine = address_file_fd.readline()
                address_file_fd.close()
                os.remove(address_file)
                
                lsr_label_input = input_new + ".feature"
                
                #Nacteni vystupu ze zpracovani objektu RTFUnit
                lsr_label_input_fd = ""
                try:
                    lsr_label_input_fd = codecs.open(lsr_label_input, 'r', "utf-8")
                except IOError:
                    sys.stderr.write("Nelze otevrit soubor " + lsr_label_input)
                    sys.exit(1)
                
                lsr_label_input_text = lsr_label_input_fd.read()
                lsr_label_input_fd.close()
                os.remove(lsr_label_input)
                #Volani obecne klasifikace
                #sys.stderr.write("lsr_label_input_text\n")
                #print lsr_label_input_text.encode('utf-8').strip()
                #sys.exit(0)
                tmpArray = LSRLabel(lsr_label_input_text, is_rtf_input, 0)
                
                #Vysledky
                sl_xml = tmpArray[0]
                #sys.stderr.write("sl_xml exit\n")
                #print sl_xml.encode('utf-8').strip()
                #sys.exit(0)
                if re.search(r"\|XML \|", sl_xml) != None:
                    sys.stderr.write("XML nalezeno\n")
                    sys.exit(0)
                    #sl_xml = re.sub(r"\|XML \|", "", sl_xml)
                    sl_xml = re.sub(r"\|XML \|xmlLoc_\d+ xmlBold_no xmlItalic_no xmlFontSize_none xmlPic_no xmlTable_yes xmlBullet_no bi_xmlSFBIA_(continue|new) bi_xmlPara_(continue|new)\n", "", sl_xml)
                aut_lines = tmpArray[1]
                aff_lines = tmpArray[2]
                
                #Prirazeni vysledku do vysledneho XML vystupu
                rxml += RemoveTopLines(sl_xml, 1)
                
                #Uprava referenci
                #print rxml.encode('utf-8').strip()
                #sys.exit(0)
                rxml = ModifyReferences(rxml)
                rxml = CorSection(rxml)
                #sys.exit(0)
                sys.stderr.write("LSRLABEL DONE - klasifikace zakladnich casti + klasifikace nadpisu\n")
            else:
                retArray = []
                retArray = LSRLabel(lsr_label_input, is_rtf_input, 0)
                sl_xml = retArray[0]
                aut_lines = retArray[1]
                aff_lines = retArray[2]
                rxml += RemoveTopLines(sl_xml, 1)
                sys.stderr.write("LSRLABEL DONE - klasifikace zakladnich casti + klasifikace nadpisu\n")
        
        #Klasifikace hlavicky dokumentu
        if mode & LSRHED == LSRHED:
            #Pripojeni modulu pro rizeni klasifikace hlavicky dokumentu
            sys.path.append("./LSRHED/")
            import ControllerHED
            
            #Volani rizeni klasifikace
            #print raw_text
            #sys.exit(0)
            ph_xml = ControllerHED.extractHeader(raw_text, ph_model)
            rxml += RemoveTopLines(ph_xml, 1) 
            sys.stderr.write("LSRHED DONE - klasifikace hlavicky\n")
        
        #Klasifikace citaci
        if mode & LSRCIT == LSRCIT:
            #Pripojeni modulu pro rizeni klasifikace citaci
            sys.path.append("./LSRCIT/")
            import ControllerCIT
            
            if is_rtf_input:
                print "under construction"
            else:
                pc_xml = ControllerCIT.ExtractCitations(raw_text, input, is_rtf_input)
                
                rxml += RemoveTopLines(pc_xml, 1)
                sys.stderr.write("LSRCIT DONE - klasifikace citaci\n")
        
        #Zakonceni XML vystupu
        rxml += "\n</algorithms>"
        
        #Ulozeni vysledku do souboru
        if output_file:
            output_fd = ""
            try:
                output_fd = codecs.open(output_file, 'w', "utf-8")
            except IOError:
                sys.stderr.write("Nelze otevrit soubor " + output_file)
                sys.exit(1)
                
            output_fd.write(rxml)
            output_fd.close()
        #Vypsani vysledku na STDOUT
        else:
            if re.search(r"&ap",  rxml) != None:
                rxml = re.sub(r"&ap", "'", rxml)
            print rxml.encode("utf-8")
        
        #Ukonceni skriptu
        sys.exit(0)
    #konec while

""" ZACATEK """
main()
