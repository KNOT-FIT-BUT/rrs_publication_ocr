#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re
import os
import codecs
import xmlParser

"""
DEFINICE:
    readedData - obsah jakehokoli souboru
    retArray - readedData
                 - navratova hodn. fce
    file - seznam obsahujici jednotlive casti dokumentu ziskane z manualni klasifikace. Tyto casti jsou porovnavany s totoznymi castmi ziskanymi klasifikacnim systemem.
"""

#================== Globalni promenne ==================
marked = {"realCount":{}, 
                  "wellMarked":{}, 
                  "marked":{}}

errCode = {"AllOk":0,
                  "parseErr":1, 
                  "fileErr":2, 
                  "summarizeErr":3, 
                  "processErr":4
           }

cntClassTitle = 0
cntAll = 0

globSuccRatio = 0.75

#urcuje, ktere sada se bude vyhodnocovat
FIRST = 1
SECOND = 2

"""
Funkce tiskne hlavicku tabulky pro vypis uspesnosti klasifikace. Hlavicka tabulky obsahuje pouze jmeno souboru.

@param fileName - jmeno souboru
"""
def PrintFileInfo(fileName):
    print "+==================+===========================================================+"
    print "|File              |          "+ fileName                                               +"         |"
    print "+==================+===========================================================+"
    sys.stderr.write(fileName + "\n")

"""
Funkce ziska jmeno dokumentu

@param readedData
@return retArray
"""
def File(readedData):
    global errCode
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\s*\"file\"\s*\:\s*\"", "", readedData, 1)
    
    #ziskani jmena dokumentu i s priponou
    try:
        fileName = re.search(r"^[^\"]+", readedData).group(0)
    except AttributeError as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Nelze precist nazev souboru!\n")
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    readedData = re.sub(r"^[^\"]+", "", readedData, 1)
    
    #odstraneni pripony
    fileName = re.sub(r"\.\w+$", "", fileName, 1)
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\",\s*", "", readedData, 1)
    
    #tisk na stdout a stderr
    PrintFileInfo(fileName)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(fileName)
    return retArray

"""
Funkce pro zvysovani citacu pro jednotlive tridy u opravdu se vyskytujicich, oznacenych a dobre oznacenych.
POZOR!! Funkce vyzaduje globalni seznam, ve kterem se nachazi prislusne citace.

@param type          - oznacuje, kde se bude citac zvysovat, jestli u vyskytujicich se, nebo oznacenych nebo dobre oznacenych
@param className - oznacuje tridu, pro kterou se bude zvysovat hodnota citace
"""
def AddToMarked(type, className, count):
    global marked
    
    if marked[type].has_key(className):
        marked[type][className] += count
    else:
        marked[type][className] = count

"""
Funkce pro ziskani titulu dokumentu.

@param readedData
@return retArray
"""
def Title(readedData):
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\"title\"\s*\:\s*\"", "", readedData, 1)
    
    #ziskani titulu dokumentu
    try:
        title = re.search(r"^[^\"]+", readedData).group(0)
    except AttributeError as e:
        sys.stderr.write("Nelze precist titul dokumentu!\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    readedData = re.sub(r"^[^\"]+", "", readedData, 1)
    
    #pokud se v titulu nachazeji uvozovky, je treba donacist zbytek titulu
    while title[-1] == "\\":
        readedData = re.sub(r"^\"", "", readedData, 1)
        title += "\""
        try:
            title += re.search(r"^[^\"]+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze precist titul dokumentu!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            print readedData
            sys.exit(errCode["parseErr"])
        readedData = re.sub(r"^[^\"]+", "", readedData, 1)
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\"\s*,\s*", "", readedData, 1)
    
    #pricti titul do marked k realCount
    AddToMarked("realCount", "title", 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(title)
    return retArray

"""
Funkce pro ziskani informaci o jmene autora dokumentu.

@param readedData
@return retArray
"""
def AuthorName(readedData):
    global errCode
    
    try:
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\"name\"\s*\:\s*\"", "", readedData, 1)
            
        #ziskani jmena autora
        author = re.search(r"^[^\"]+", readedData).group(0)
        readedData = re.sub(r"^[^\"]+", "", readedData, 1)
            
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\",\s*", "", readedData, 1)
    except AttributeError as e:
        sys.stderr.write("Nelze nacist jmeno autora!\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
        
    #zvyseni citace jmena autora
    AddToMarked("realCount", "author", 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(author)
    return retArray

"""
Funkce pro ziskani informaci o pricleneni autora dokumentu.

@param readedData
@return retArray
"""
def AuthorAffiliation(readedData):
    global errCode
    
    try:
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\"organization\"\s*\:\s*(\")?", "", readedData, 1)
        
        #ziskani pricleneni autora. Pricleneni muze byt nevyplneno.
        if re.search(r"^null", readedData):
            org = "null"
            readedData = re.sub(r"^null(\")?,\s*", "", readedData, 1)
        else:
            org = re.search(r"^[^\"]+", readedData).group(0)
            readedData = re.sub(r"^[^\"]+", "", readedData, 1)
            
            #pricleneni muze obsahovat uvozovky
            while org[-1] == "\\":
                org += "\""
                readedData = re.sub(r"\"", "", readedData, 1)
                
                if readedData[0] == "\"":
                    break
                
                org += re.search(r"^[^\"]+", readedData).group(0)
                readedData = re.sub(r"^[^\"]+", "", readedData, 1)
            
            #odstraneni nepotrebne casti
            readedData = re.sub(r"^\"\s*,\s*", "", readedData, 1)
            
            #zvyseni citace pricleneni
            AddToMarked("realCount", "affiliation", 1)
    except AttributeError as e:
        sys.stderr.write("Nelze nacist organizaci!\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(org)
    return retArray

def AuthorEmail(readedData):
    global errCode
    
    try:
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\"email\"\s*\:\s*(\")?", "", readedData, 1)
        
        #ziskani emailu autora. Email muze byt nevyplnen.
        if re.search(r"^null", readedData):
            email = "null"
            readedData = re.sub(r"^null(\")?\s*", "", readedData, 1)
        else:
            email = re.search(r"^[^\"]+", readedData).group(0)
            readedData = re.sub(r"^[^\"]+", "", readedData, 1)
            
            #odstraneni nepotrebne casti
            readedData = re.sub(r"^\"\s*", "", readedData, 1)
            
            #zvyseni citace emailu
            AddToMarked("realCount", "email", 1)
    except AttributeError as e:
        sys.stderr.write("Nelze precist e-mail!\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(email)
    return retArray

"""
Funkce pro ziskani informaci o autorech dokumentu. Tzn. jmena, emailu a pricleneni.

@param readedData
@return retArray
"""
def Authors(readedData):
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\"authors\"\s*\:\s*\[\s*", "", readedData, 1)
    
    #pole autoru
    authors = []
    
    
    while not re.search(r"^\]", readedData):
        #seznam informaci o autorovi
        author = {}
        
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\{\s*", "", readedData, 1)
        
        #jmeno
        retArray = AuthorName(readedData)
        readedData = retArray[0]
        author["name"] = retArray[1]
        
        #pricleneni
        retArray = AuthorAffiliation(readedData)
        readedData = retArray[0]
        author["organization"] = retArray[1]
        
        #emailu
        retArray = AuthorEmail(readedData)
        readedData = retArray[0]
        author["email"] = retArray[1]
        
        #ulozeni autora
        authors.append(author)
        
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\s*\}\s*,?\s*", "", readedData, 1)
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\s*\]\s*,\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(authors)
    return retArray

"""
Funkce pro ziskani eventu. Tato informace se momentalne pri hodnoceni klasifikatoru nepouziva.

@param readedData
@return retArray
"""
def Event(readedData):
    global errCode
    
    try:
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\"event\"\s*\:\s*(\")?", "", readedData, 1)
        
        #ziskani eventu. Event muze byt nevyplnen
        if re.search(r"^null", readedData):
            event = "null"
            readedData = re.sub(r"^null(\")?,\s*", "", readedData, 1)
        else:
            event = re.search(r"^[^\"]+", readedData).group(0)
            readedData = re.sub(r"^[^\"]+", "", readedData, 1)
            
            #odstraneni nepotrebne casti
            readedData = re.sub(r"^\"\s*,\s*", "", readedData, 1)
    except AttributeError as e:
        sys.stderr.write("Nelze precist Event!\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(event)
    return retArray

"""
Funkce pro ziskani stranek dokumentu. Tato informace se momentalne pri hodnoceni klasifikatoru nepouziva.

@param readedData
@return retArray
"""
def Pages(readedData):
    global errCode
    
    try:
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\"pages\"\s*\:\s*(\")?", "", readedData, 1)
        
        #ziskani stranek dokumentu. Stranky mohou byt nevyplneny
        if re.search(r"^null", readedData):
            pages = "null"
            readedData = re.sub(r"^null(\")?,\s*", "", readedData, 1)
        else:
            pages = re.search(r"^[^\"]+", readedData).group(0)
            readedData = re.sub(r"^[^\"]+", "", readedData, 1)
            
            #odstraneni nepotrebne casti
            readedData = re.sub(r"^\"\s*,\s*", "", readedData, 1)
    except AttributeError as e:
        sys.stderr.write("Nelze precist Pages!\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(pages)
    return retArray

"""
Funkce pro ziskani roku uverejneni dokumentu. Tato informace se momentalne pri hodnoceni klasifikatoru nepouziva.

@param readedData
@return retArray
"""
def Year(readedData):
    global errCode
    
    try:
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\"year\"\s*\:\s*(\")?", "", readedData, 1)
        
        #ziskani roku uverejneni dokumentu. Rok muze byt nevyplnen.
        if re.search(r"^null", readedData):
            year = "null"
            readedData = re.sub(r"^null(\")?,\s*", "", readedData, 1)
        else:
            year = re.search(r"^[^\"]+", readedData).group(0)
            readedData = re.sub(r"^[^\"]+", "", readedData, 1)
            
            #odstraneni nepotrebne casti
            readedData = re.sub(r"^\"\s*,\s*", "", readedData, 1)
    except AttributeError as e:
        sys.stderr.write("Nelze precist Year\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(year)
    return retArray

"""
Funkce pro ziskani abstraktu dokumentu.

@param readedData
@return retArray
"""
def Abstract(readedData):
    global errCode
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\"abstract\"\s*\:\s*(\")?", "", readedData, 1)
    
    #ziskani abstraktu. Abstrakt muze byt nevyplnen
    if re.search(r"^null",  readedData) != None:
        readedData = re.sub(r"^null(\")?\s*,\s*", "", readedData, 1)
        abstract = "null"
    else:
        try:
            abstract = re.search(r"^[^\"]+", readedData).group(0)
            readedData = re.sub(r"^[^\"]+", "", readedData, 1)
            
            #abstrakt muze obsahovat uvozovky, nutne osetrit
            while abstract[-1] == "\\":
                abstract += "\""
                readedData = re.sub(r"^\"", "", readedData, 1)
                
                #teoreticky muze nastat situace \"", takze proto *
                subAbstract = re.search(r"^[^\"]*", readedData).group(0)
                if subAbstract == "":
                    break
                else:
                    readedData = re.sub(r"^[^\"]*", "", readedData, 1)
                    abstract += subAbstract
            
            #odstraneni nepotrebne casti
            readedData = re.sub(r"^\"\s*,\s*", "", readedData, 1)
        except AttributeError as e:
            sys.stderr.write("Nelze precist Abstrakt\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            print readedData
            sys.exit(errCode["parseErr"])
        
        #zvyseni citace abstraktu
        AddToMarked("realCount", "abstract", 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(abstract)
    return retArray

"""
Funkce pro ziskani jmena kapitoly.

@param readedData
@return retArray
"""
def ChapterName(readedData):
    global errCode
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\"name\"\s*\:\s*(\")?", "", readedData, 1)
    
    #TODO: dat si pozor, jestli name nemuze byt null, moc smysl to ale nedava
    #ziskani jmena kapitoly
    try:
        name = re.search(r"^[^\"]+", readedData).group(0)
        readedData = re.sub(r"^[^\"]+", "", readedData, 1)
            
        #jmeno muze obsahovat uvozovky, nutne osetrit
        while name[-1] == "\\":
            name += "\""
            readedData = re.sub(r"^\"", "", readedData, 1)
                
            #teoreticky muze nastat situace \"", takze proto *
            subName = re.search(r"^[^\"]*", readedData).group(0)
            if subName == "":
                break
            else:
                readedData = re.sub(r"^[^\"]*", "", readedData, 1)
                name += subName
            
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\"\s*,\s*", "", readedData, 1)
    except AttributeError as e:
        sys.stderr.write("Nelze precist Jmeno kapitoly!\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #zvyseni citace kapitoly
    AddToMarked("realCount", "sectionHeader", 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(name)
    return retArray

"""
Funkce pro ziskani podkapitol.

@param readedData
@return retArray
"""
def SubChapters(readedData):
    global errCode
    subchapters = []
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\"subchapters\"\s*\:\s*", "", readedData, 1)
    
    #ziskani podkapitol. Podkapitoly mohou byt nevyplneny
    if re.search(r"^(\")?null",  readedData) != None:
        readedData = re.sub(r"^(\")?null(\")?\s*", "", readedData, 1)
    else:
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\[\s*", "", readedData, 1)
        
        while not re.search(r"^\]", readedData):
            #odstraneni nepotrebne casti
            readedData = re.sub(r"^\"", "", readedData, 1)
            
            #ziskani podkapitoly
            try:
                subchapter = re.search(r"^[^\"]+", readedData).group(0)
                readedData = re.sub(r"^[^\"]+", "", readedData, 1)
                    
                #podkapitola muze obsahovat uvozovky, nutne osetrit
                while subchapter[-1] == "\\":
                    subchapter += "\""
                    readedData = re.sub(r"^\"", "", readedData, 1)
                        
                    #teoreticky muze nastat situace \"", takze proto *
                    subSubchapter = re.search(r"^[^\"]*", readedData).group(0)
                    if subSubchapter == "":
                        break
                    else:
                        readedData = re.sub(r"^[^\"]*", "", readedData, 1)
                        subchapter += subSubchapter
                    
                #odstraneni nepotrebne casti
                readedData = re.sub(r"^\"\s*,?\s*", "", readedData, 1)
            except AttributeError as e:
                sys.stderr.write("Nelze precist Jmeno kapitoly!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                print readedData
                sys.exit(errCode["parseErr"])
            
            #zvyseni citace podkapitol
            AddToMarked("realCount", "subsectionHeader", 1)
            
            #ulozeni podkapitoly
            subchapters.append(subchapter)
        
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\]\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(subchapters)
    return retArray

"""
Funkce pro ziskani obsahu kapitol. Tzn. jmena a podkapitol

@param readedData
@return retArray
"""
def Chapters(readedData):
    global errCode
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\"chapters\"\:\s*", "", readedData, 1)
    
    #pole kapitol
    chapters = []
    
    #kapitoly mohou byt nevyplneny
    if re.search(r"^(\")?null", readedData) != None:
        readedData = re.sub(r"^(\")?null(\")?\s*,?\s*", "", readedData, 1)
    else:
        readedData = re.sub(r"^\[\s*", "", readedData, 1)
        #TODO: odstranit radek
        #sys.stderr.write(readedData[:128] + "\n")
        #sys.stderr.write("--------------------------------------------\n")
        #sys.exit(0)
    
        while not re.search(r"^\]", readedData):
            chapter = {}
            
            #odstraneni nepotrebne casti
            readedData = re.sub(r"^\{\s*", "", readedData, 1)
            
            #jmeno
            retArray = ChapterName(readedData)
            readedData = retArray[0]
            chapter["name"] = retArray[1]
            
            #podkapitoly
            retArray = SubChapters(readedData)
            readedData = retArray[0]
            chapter["subsectionHeader"] = retArray[1]
            
            #odstraneni nepotrebne casti
            readedData = re.sub(r"^\}\s*,?\s*", "", readedData, 1)
            
            #ulozeni kapitoly
            chapters.append(chapter)
        
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\]\s*,?\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(chapters)
    return retArray

"""
Funkce pro ziskani textu referenci/citaci.

@param readedData
@return retArray
"""
def CiteText(readedData):
    global errCode
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\"text\"\:\s*\"", "", readedData, 1)
    
    #ziskani textu citace
    #TODO: pripadne zachytavat vyjimky AttributeError
    text_cit = re.search(r"^[^\"]+", readedData).group(0)
    readedData = re.sub(r"^[^\"]+", "", readedData, 1)
    
    #detekce uvozovek v textu
    while re.search(r"\\$", text_cit) != None:
        text_cit += "\""
        readedData = re.sub(r"^\"", "", readedData, 1)
        
        if readedData[0] == "\"":
            break
        
        text_cit += re.search(r"^[^\"]+", readedData).group(0)
        readedData = re.sub(r"^[^\"]+", "", readedData, 1)
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\",\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(text_cit)
    return retArray

"""
Funkce pro ziskani titulu citovaneho dila.

@param readedData
@return retArray
"""
def CiteTitle(readedData):
    global errCode
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\"title\"\:(\")?", "", readedData, 1)
    
    #ziskani titulu
    try:
        if re.search(r"^null", readedData):
            title_cit = "null"
            readedData = re.sub(r"^null(\")?", "", readedData, 1)
        else:
            title_cit = re.search(r"^[^\"]+", readedData).group(0)
            readedData = re.sub(r"^[^\"]+", "", readedData, 1)
            
            #detekce uvozovek v textu
            while re.search(r"\\$", title_cit) != None:
                title_cit += "\""
                readedData = re.sub(r"^\"", "", readedData, 1)
                
                if readedData[0] == "\"":
                    break
                
                title_cit += re.search(r"^[^\"]+", readedData).group(0)
                readedData = re.sub(r"^[^\"]+", "", readedData, 1)
    except AttributeError as e:
        sys.stderr.write("Nepodarilo se naparsovat titul citace!\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^(\")?,\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(title_cit)
    return retArray

"""
Funkce pro ziskani eventu citace.

@param readedData
@return retArray
"""
def CiteEvent(readedData):
    global errCode
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\"event\"\:(\")?", "", readedData, 1)
    
    #ziskani eventu
    #TODO: pripadne zachytavat vyjimky AttributeError
    if re.search(r"^null", readedData):
        event_cit = "null"
        readedData = re.sub(r"^null(\")?", "", readedData, 1)
    else:
        event_cit = re.search(r"^[^\"]+", readedData).group(0)
        readedData = re.sub(r"^[^\"]+", "", readedData, 1)
    
        #detekce uvozovek v textu
        while re.search(r"\\$", event_cit) != None:
            event_cit += "\""
            readedData = re.sub(r"^\"", "", readedData, 1)
            
            if readedData[0] == "\"":
                break
            
            event_cit += re.search(r"^[^\"]+", readedData).group(0)
            readedData = re.sub(r"^[^\"]+", "", readedData, 1)
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^(\")?,\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(event_cit)
    return retArray

"""
Funkce pro ziskani roku citovaneho dila.

@param readedData
@return retArray
"""
def CiteYear(readedData):
    global errCode
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\"year\"\:(\")?", "", readedData, 1)
    
    #ziskani roku
    #TODO: pripadne zachytavat vyjimky AttributeError
    if re.search(r"^null", readedData):
        year_cit = "null"
        readedData = re.sub(r"^null(\")?", "", readedData, 1)
    else:
        year_cit = re.search(r"^[^\"]+", readedData).group(0)
        readedData = re.sub(r"^[^\"]+", "", readedData, 1)
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^(\")?,\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(year_cit)
    return retArray

"""
Funkce pro ziskani autora citace.

@param readedData
@return retArray
"""
def CiteAuthor(readedData):
    global errCode
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\"name\"\:(\")?",  "",  readedData, 1)
    
    #ziskani autora
    #TODO: pripadne zachytavat vyjimky AttributeError
    if re.search(r"^null", readedData):
        author_cit = "null"
        readedData = re.sub(r"^null(\")?", "", readedData, 1)
    else:
        author_cit = re.search(r"^[^\"]+", readedData).group(0)
        readedData = re.sub(r"^[^\"]+\"\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(author_cit)
    return retArray

"""
Funkce pro ziskani autoru citace.

@param readedData
@return retArray
"""
def CiteAuthors(readedData):
    global errCode
    authors_cit = []
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\"authors\"\s*\:\s*\[\s*", "", readedData, 1)
    
    #zpracovani autoru
    while not re.search(r"^\]",  readedData):
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\{\s*",  "",  readedData, 1)
        
        #ziskani autora citovaneho dila
        retArray = CiteAuthor(readedData)
        readedData = retArray[0]
        author_cit = retArray[1]
        
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\s*\}\s*,?\s*", "", readedData, 1)
        
        #ulozeni autora
        authors_cit.append(author_cit)
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\]\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(authors_cit)
    return retArray

"""
Funkce pro ziskani referenci/citaci. Reference nejsou momentalne automatickym vyhodnocenim zpracovavany.

@param readedData
@return retArray
"""
def References(readedData):
    global errCode
    references = []
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\"references\"\s*\:\s*\[\s*", "", readedData, 1)
    
    while not re.search(r"^\]", readedData):
        reference = {}
        
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\{\s*", "", readedData, 1)
        
        #text citace
        retArray = CiteText(readedData)
        readedData = retArray[0]
        reference["text"] = retArray[1]
        
        #titul citovaneho dila
        retArray = CiteTitle(readedData)
        readedData = retArray[0]
        reference["title"] = retArray[1]
        
        #event
        retArray = CiteEvent(readedData)
        readedData = retArray[0]
        reference["event"] = retArray[1]
        
        #year
        retArray = CiteYear(readedData)
        readedData = retArray[0]
        reference["year"] = retArray[1]
        
        #autori citovaneho dila
        retArray = CiteAuthors(readedData)
        readedData = retArray[0]
        reference["authors"] = retArray[1]
        
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\}\s*,?\s*", "", readedData, 1)
        
        #ulozeni referenci
        references.append(reference)
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\]\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(references)
    return retArray

"""
Funkce pro ziskani metadat. Hlavni funkci teto funkce je volat ostatni funkce.

@param readedData
@return retArray
"""
def Metadata(readedData, refBool):
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\s*\"metadata\"\s*\:\s*\{\s*", "", readedData, 1)
    
    #titul
    retArray = Title(readedData)
    readedData = retArray[0]
    title = retArray[1]
    
    #autori
    retArray = Authors(readedData)
    readedData = retArray[0]
    authors = retArray[1]
    
    #event
    retArray = Event(readedData)
    readedData = retArray[0]
    event = retArray[1]
    
    #pages
    retArray = Pages(readedData)
    readedData = retArray[0]
    pages = retArray[1]
    
    #year
    retArray = Year(readedData)
    readedData = retArray[0]
    year = retArray[1]
    
    #abstract
    retArray = Abstract(readedData)
    readedData = retArray[0]
    abstract = retArray[1]
    
    #chapters
    retArray = Chapters(readedData)
    readedData = retArray[0]
    chapters = retArray[1]
    
    #referenes (v cesku citace)
    if refBool:
        retArray = References(readedData)
        readedData = retArray[0]
        referenes = retArray[1]
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    file = {}
    file["title"] = title
    file["authors"] = authors
    file["event"] = event
    file["pages"] = pages
    file["year"] = year
    file["abstract"] = abstract
    file["chapters"] = chapters
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(file)
    return retArray

"""
Funkce pro vyhodnoceni klasifikace titulu.

@param file
@param xmlLabel - obecna klasifikace
@param xmlHeader - klasifikace hlavicky
@return 
"""
def TitleCheck(file, xmlLabel, xmlHeader):
    #indikator nalezeni titulu
    xmlTitleFound = False
    
    #pokus o nalezeni titulu v klasifikaci hlavicky dokumentu
    xmlTitle = xmlHeader.SearchElemText(xmlHeader, "title")
    
    #muze se stat, ze klasifikace v xmlHeader se nezdari
    #zde je pokus o zachranu z xmlLabel
    if not xmlTitle:
        xmlTitle = xmlLabel.SearchElemText(xmlLabel, "title")
    
    #v pripade nalezeni titulu
    if xmlTitle:
        xmlTitle = re.sub(r"&gt", ">", xmlTitle)
        #TODO: Vyresit kodovani
        #odstraneni znaku, ktere mohou ovlivnit porovnani
        xmlTitle = re.sub(r"&ec", u"\u0233", xmlTitle)
        xmlTitle = re.sub(r"&uu", u"\u0252", xmlTitle)
        xmlTitle = re.sub(r"\\\"","", xmlTitle)
        xmlTitle = re.sub(r"\"","", xmlTitle)
        xmlTitle = re.sub(r"\/","", xmlTitle)
        xmlTitle = re.sub(r"\?","", xmlTitle)
        xmlTitle = re.sub(r"\-","", xmlTitle)
        xmlTitle = re.sub(r"\s+","", xmlTitle)
        file["title"] = re.sub(r"\\\"","", file["title"])
        file["title"] = re.sub(r"\'","", file["title"])
        file["title"] = re.sub(r"\-","", file["title"])
        file["title"] = re.sub(r"\?","", file["title"])
        file["title"] = re.sub(r"\/","", file["title"])
        file["title"] = re.sub(r"\s+","", file["title"])
        
        #TODO: IFovat
        #xmlTitle = re.sub(r"\\u(d{4}|d{3}\?)", "", xmlTitle)
        xmlTitle = re.sub(r"[^a-zA-Z]", "", xmlTitle)
        file["title"] = re.sub(r"[^a-zA-Z]", "", file["title"])
        
        #print "LSR"
        #print xmlTitle
        #print "Manual"
        #print file["title"]
        
        #porovnani titulu z klasifikace a manualni klasifikace
        if re.search(re.escape(xmlTitle), file["title"]) != None or re.search(re.escape(file["title"]), xmlTitle) != None:
            #nastaveni indikatoru
            xmlTitleFound = True
            
            #informovani uzivatele o nalezeni titulu
            #sys.stdout.write("Titul nalezen\n")
            sys.stderr.write("Titul nalezen\n")
            
            #zvyseni citace oznacenych titulu
            AddToMarked("marked", "title", 1)
            
            #zvyseni citace dobre oznacenych titulu
            AddToMarked("wellMarked", "title", 1)
        #titul klasifikovan, ale neuspesne porovnan s manualni klasifikaci. Tento krok by tu nemusel byt, ale pro pochopeni je lepsi, kdyz tu je
        else:
            #zvyseni citace oznacenych titulu
            AddToMarked("marked", "title", 1)
    
    #teoreticky muze nastat situace, kdy dokument nebude mit titul, coz neni pokryto, ale prijde mi to tak nepravdepodobne, ze jsem to neresil
    if xmlTitleFound:
        PrintClassInfo("Title", 1, 1, True)
    else:
        PrintClassInfo("Title", 1, 0, True)

"""
Funkce pro ziskani jmen autoru z klasifikace.

@param xmlHeader
@return authorCnt - pocet nalezenych autoru
"""
def AuthorNameCheck(xmlHeader):
    authorCnt = 0
    
    #ziskani vsech klasifikovanych autoru
    xmlAuthorsName = xmlHeader.Select(xmlHeader, "author", [])
    
    #pole autoru
    authors = []
    
    for item in xmlAuthorsName:
        #ziskani textu z XML podstromu obsahujici jmena autoru
        xmlAuthorName = item.SearchElemText(item, "author")
        
        #odstraneni and, ktere by zpusobilo oznaceni dvou autoru jako jednoho
        xmlAuthorName = re.sub(r"(\,)?\s+and\s+", ",", xmlAuthorName)
        
        #odstraneni rusivych znaku
        xmlAuthorName = re.sub(r"(\,)+", ",", xmlAuthorName)
        xmlAuthorName = re.sub(r"\,\s+\,", ",", xmlAuthorName)
        xmlAuthorName = re.sub(r"\.\s*", ". ", xmlAuthorName)
        
        while re.search(r"^[^\,]+", xmlAuthorName):
            #ziskani autora
            tmpAuthor = re.search(r"^[^\,]+", xmlAuthorName).group(0)
            
            #odstraneni autora ze souboru autoru
            xmlAuthorName = re.sub(r"^[^\,]+\s*\,?\s*", "", xmlAuthorName, 1)
            
            #ulozeni autora do pole
            #muze nastat situace jako napr.: Salvatore D. Morgera, Fellow, IEEE, kdy se tento autor rozdeli na 3, protoze se zde vyskyji carky. To je treba eliminovat
            #take misto Fellow tam muze byt neco jako Student Member atd.
            if re.search(r"\s+", tmpAuthor) and not re.search(r"^Student Member$", tmpAuthor) and not re.search(r"^Senior Member$", tmpAuthor):
                authors.append(tmpAuthor)
    
    #return
    return authors

"""
Funkce pro porovnani jmen autoru z klasifikace a manualni klasifikace.

@param xmlHeader
@return bool
"""
def AuthorNameCompare(authorName, authors):
    #porovnani kazdeho autora z klasifikace
    for item in authors:
        #uprava textu klasifikace i manualni klasifikace
        item = re.sub(r"\s+", "", item)
        item = re.sub(r"\-", "", item)
        item = re.sub(r"\.", "", item)
        item = re.sub(r"\,", "", item)
        item = re.sub(r"\*", "", item)
        item = re.sub(r"\^", "", item)
        item = re.sub(r"\[", "", item)
        item = re.sub(r"\]", "", item)
        item = re.sub(r"\(", "", item)
        item = re.sub(r"\)", "", item)
        authorName = re.sub(r"\s+", "", authorName)
        authorName = re.sub(r"\-", "", authorName)
        authorName = re.sub(r"\.", "", authorName)
        #kvuli odstraneni takovych veci jako , JR. (junior)
        authorName = re.sub(r"\,\w+", "", authorName)
        
        #TODO: IFovat
        item = re.sub(r"[^a-zA-Z]", "", item)
        authorName = re.sub(r"[^a-zA-Z]", "", authorName)
        
        #porovnani hodnot
        #print "LSR"
        #print item
        #print "Manual"
        #print authorName
        
        if re.search(re.escape(authorName), item) != None or re.search(item, re.escape(authorName)) != None:
            #sys.stdout.write("Autor nalezen\n")
            sys.stderr.write("Autor nalezen\n")
            
            #zvyseni citace oznacenych autoru
            AddToMarked("marked", "author", 1)
            
            #zvyseni citace dobre oznacenych autoru
            AddToMarked("wellMarked", "author", 1)
            
            return True
    
    return False

"""
Funkce pro generovani mezer.

@param count - pocet mezer
@return tmpStr - retezec
"""
def GetSpaces(count):
    tmpStr = ""
    
    while count:
        tmpStr += " "
        count -= 1
    
    #return
    return tmpStr

"""
Funkce pro tisk vysledku klasifikace.

@param className - jmeno tridy
@param all - pocet casti v manualni klasifikaci
@param cnt - pocet casti uspesne klasifikovanych klasifikatorem
@param singleton - oznacuje, zda se pracuje s casti dokumentu, ktera se v nem muze vyskytnout pouze jednou
@return
""" 
def PrintClassInfo(className, all, cnt, singleton):
    #pr. |title
    tmpStr = "|" + className
    #pr. |Title             |
    tmpStr += GetSpaces((18 - len(className))) + "|"
    #tmpStr = re.sub(r"\s*$", "\s{" + str(18 - len(className)) + "}|", tmpStr, 1)
    
    if singleton:
        if not all:
            tmpStr += GetSpaces(10) + "NEPRITOMEN" + GetSpaces(9) + "|" + GetSpaces(14) + "X" + GetSpaces(14) + "|"
        elif cnt:
            tmpStr += GetSpaces(10) + "PRITOMEN" + GetSpaces(11) + "|" + GetSpaces(10) + "NALEZEN" + GetSpaces(12) + "|"
            #tmpStr = re.sub(r"\s*$", "\s{10}PRITOMEN\s{11}|\s{10}NALEZEN\s{12}|", tmpStr, 1)
        else:
            tmpStr += GetSpaces(10) + "PRITOMEN" + GetSpaces(11) + "|" + GetSpaces(10) + "NENALEZEN" + GetSpaces(10) + "|"
            #tmpStr = re.sub(r"\s*$", "\s{10}PRITOMEN\s{11}|\s{10}NENALEZEN\s{10}|", tmpStr, 1)
    else:
        if not all:
            tmpStr += GetSpaces(10) + "NEPRITOMEN" + GetSpaces(9) + "|" + GetSpaces(14) + "X" + GetSpaces(14) + "|"
            #tmpStr = re.sub(r"\s*$", "\s{10}NEPRITOMEN\s{9}|\s{14}X\s{14}|", tmpStr, 1)
        elif tmpStr:
            tmpStr += GetSpaces(10) + "PRITOMEN - " + str(all) + "x" + GetSpaces((29 - 10 - len("PRITOMEN - ") - len(str(all)) - 1)) + "|" + GetSpaces(10) + "NALEZEN - " + str(cnt) + "x" + GetSpaces((29 - 10 - len("NALEZEN - ") - len(str(cnt)) - 1)) + "|"
            #tmpStr = re.sub(r"\s*$", "\s{10}PRITOMEN \- " + str(all) + "x\s{" + str(29 - 10 - len("PRITOMEN") - len(str(all)) - 1) + "}|\s{10}NALEZEN \- " + str(cnt) + "x\s{" + str(29 - 10 - len("NALEZEN") - len(str(cnt)) - 1) + "}|", tmpStr, 1)
        else:
            tmpStr += GetSpaces(10) + "PRITOMEN - " + str(all) + "x" + GetSpaces((29 - 10 - len("PRITOMEN - ") - len(str(all)) - 1)) + "|" + GetSpaces(10) + "NENALEZEN - " + str(cnt) + "x" + GetSpaces((29 - 10 - len("NENALEZEN - ") - len(str(cnt)) - 1)) + "|"
            #tmpStr = re.sub(r"\s*$", "\s{10}PRITOMEN \- " + str(all) + "x\s{" + str(29 - 10 - len("PRITOMEN") - len(str(all)) - 1) + "}|\s{10}NENALEZEN\s{" + str(29 - 10 - len("NENALEZEN")) + "}|", tmpStr, 1)
        
    #samotny tisk formatovaneho vystupu
    print tmpStr
    print "+------------------+-----------------------------+-----------------------------+"

"""
Funkce pro ziskani poctu emailu v manualni klasifikaci.

@param authors - seznam autoru a informaci o nich
@return emailAll - pocet emailu v manualni klasifikaci pro dany dokument
"""
def GetAffiliationCnt(authors):
    #pocet emailu v manualni klasifikaci pro dany dokument
    affiliationAll = 0
    
    for item in authors:
        if item["organization"] != "null":
            affiliationAll += 1
    
    #return
    return affiliationAll

"""
Funkce pro ziskani poctu emailu v manualni klasifikaci.

@param authors - seznam autoru a informaci o nich
@return emailAll - pocet emailu v manualni klasifikaci pro dany dokument
"""
def GetEmailCnt(authors):
    #pocet emailu v manualni klasifikaci pro dany dokument
    emailAll = 0
    
    for item in authors:
        if item["email"] != "null":
            emailAll += 1
    
    #return
    return emailAll

"""
Funkce pro ziskani emailu z klasifikace dokumentu.

@param xmlHeader
@return emailCnt - pocet emailu uspesne porovnanych s manualni klasifikaci
"""
def AuthorEmailCheck(xmlHeader, xmlLabel):
    global errCode
    
    #citac uspesne nalezenych emailu
    emailCnt = 0
    
    #ziskani klasifikovanych emailu
    xmlAuthorsEmail = xmlHeader.Select(xmlHeader, "email", [])
    
    #zachrana z obecne klasifikace
    if not xmlAuthorsEmail:
        xmlAuthorsEmail = xmlLabel.Select(xmlLabel, "email", [])
    
    #pole obsahujici emaily
    emails = []
    
    for item in xmlAuthorsEmail:
        #ziskani textu z XML podstromu obsahujici email
        xmlAuthorEmail = item.SearchElemText(item, "email")
        
        if not re.search(r"@", xmlAuthorEmail):
            continue
        
        #odstraneni rusivych znaku
        xmlAuthorEmail = re.sub(r"\\", "", xmlAuthorEmail)
        xmlAuthorEmail = re.sub(r"\.\s+", ".", xmlAuthorEmail)
        xmlAuthorEmail = re.sub(r"\s+@", "@", xmlAuthorEmail)
        
        #{name1(,|/) name2(,|/) ...}@domain
        while re.search(r"\{[^\}]+\}",  xmlAuthorEmail) != None:
            #nacteni celeho souboru emailu
            try:
                tmpEmail = re.search(r"(\{([^\}]+)\}@(\.)?\w+((\-|\.)\w+)*\.\w+)|(\{([^\}]+)\})",  xmlAuthorEmail).group(0)
                if not re.search(r"\}@", tmpEmail):
                    tmpEmail = re.sub(r"\}", "", tmpEmail)
                    tmpEmail = re.sub(r"@", "}@", tmpEmail)
            except AttributeError as e:
                sys.stderr.write("Nastala vyjimka pri zpracovani emailu!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                sys.stderr.write("Orig: " + tmpOrig + "\n")
                sys.exit(errCode["processErr"])
            
            #ulozeni casti pred @
            try:
                tmpEmailPreAt = re.search(r"\{([^\}]*)\}", tmpEmail).group(0)
            except AttributeError:
                sys.stderr.write("Nastala vyjimka pri zpracovani emailu!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                sys.stderr.write("Orig: " + tmpOrig + "\n")
                sys.exit(errCode["processErr"])
            
            #ulozeni casti po @ vcetne
            tmpEmailPostAt = re.search(r"@(\.)?\w+((\-|\.)\w+)*\.\w+", tmpEmail).group(0)
            
            #odstraneni tohoto souboru emailu
            xmlAuthorEmail = re.sub(r"(\{([^\}]+)\}@(\.)?\w+((\-|\.)\w+)*\.\w+)|(\{([^\}]+)\})", "",  xmlAuthorEmail, 1)
            
            #ziskani jednotlivych emailu ze souboru emailu
            #odstraneni svorek
            tmpEmailPreAt = re.sub(r"(\{|\})", "", tmpEmailPreAt, 2)
            
            #ziskani jmena
            while tmpEmailPreAt:
                try:
                    tmpName = re.search(r"^\w+((\-|\.)\w+)*", tmpEmailPreAt).group(0)
                except AttributeError:
                    sys.stderr.write("Nastala vyjimka pri zpracovani emailu!\n")
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                    sys.stderr.write("Email: " + tmpEmail + "\n")
                    sys.stderr.write("Post: " + tmpEmailPostAt + "\n")
                    sys.stderr.write("After: " + xmlAuthorEmail + "\n")
                    sys.exit(errCode["processErr"])
                tmpEmailPreAt = re.sub(r"^\w+((\-|\.)\w+)*\s*(\,|/)?\s*", "", tmpEmailPreAt, 1)
                
                #slouceni jmena a koncovky
                tmpEmailDone = tmpName + tmpEmailPostAt
                
                #ulozeni do pole
                emails.append(tmpEmailDone)
        #name@domain
        while re.search(r"\w+((\-|\.)\w+)*@(\.)?\w+((\-|\.)\w+)*\.\w+", xmlAuthorEmail):
            #ziskani emailu
            tmpEmail = re.search(r"\w+((\-|\.)\w+)*@(\.)?\w+((\-|\.)\w+)*\.\w+", xmlAuthorEmail).group(0)
            
            #odstraneni emailu ze souboru mailu
            xmlAuthorEmail = re.sub(r"\w+((\-|\.)\w+)*@(\.)?\w+((\-|\.)\w+)*\.\w+", "", xmlAuthorEmail, 1)
            
            #ulozeni emailu
            emails.append(tmpEmail)
    
    #return
    return emails

"""
Funkce pro porovnani emailu z klasifikace dokumentu s manualni klasifikaci.

@param authorEmail - email manualni klasifikace
@param emails - pole emailu z klasifikace
@return bool
"""
def AuthorEmailCompare(authorEmail, emails):
    #porovnani vysledku klasifikace s manualni klasifikaci
    if authorEmail != "null":
        for item in emails:
            #odstraneni prebytecnych bilych znaku
            authorEmail = re.sub(r"\s+", "", authorEmail)
            item = re.sub(r"\s+", "", item)
            
            #TODO: IFovat
            item = re.sub(r"[^a-zA-Z]", "", item)
            authorEmail = re.sub(r"[^a-zA-Z]", "", authorEmail)
            
            #porovnani hodnot
            #print "LSR"
            #print item
            #print "Manual"
            #print authorEmail
            
            #porovnani vysledku
            if re.search(re.escape(authorEmail), item) != None:
                #sys.stdout.write("Email nalezen\n")
                sys.stderr.write("Email nalezen\n")
                
                #zvyseni citace oznacenych emailu
                AddToMarked("marked", "email", 1)
                
                #zvyseni citace dobre oznacenych emailu
                AddToMarked("wellMarked", "email", 1)
                
                return True
    
    return False

"""
Funkce pro ziskani pricleneni z klasifikace dokumentu.

@param xmlHeader
@return affiliations - pole pricleneni
"""
def AuthorAffiliationCheck(xmlHeader, xmlLabel):
    #ziskani pricleneni
    xmlAuthorAffiliationSelect = xmlHeader.Select(xmlHeader, "affiliation", [])
    
    #zachrana z obecne klasifikace
    if not xmlAuthorAffiliationSelect:
        xmlAuthorAffiliationSelect = xmlLabel.Select(xmlLabel, "affiliation", [])
    
    #ziskani adres
    xmlAddressSelect = xmlHeader.Select(xmlHeader, "address", [])
    
    #pole adres, ktere se budou pozdeji pridruzovat k pricleneni
    xmlAddresses = []
    
    #pole pricleneni
    affiliations = []
    
    #ulozeni vsech adres
    if xmlAddressSelect:
        for i in range(len(xmlAddressSelect)):
            xmlAddresses.append(xmlAddressSelect[i].SearchElemText(xmlAddressSelect[i], "address"))
    
    #ulozeni vsech pricleneni
    for i in range(len(xmlAuthorAffiliationSelect)):
        #ziskani pricleneni
        xmlAuthorAffiliation = xmlAuthorAffiliationSelect[i].SearchElemText(xmlAuthorAffiliationSelect[i], "affiliation")
        
        #existuje adresa, ktera pravdepodobne patri k pricleneni
        if len(xmlAddresses) > i :
            xmlAuthorAffiliation += " " + xmlAddresses[i]
        
        #ulozeni pricleneni
        affiliations.append(xmlAuthorAffiliation)
    
    #return
    return affiliations
 
"""
Funkce pro porovnani pricleneni z klasifikace dokumentu s manualni klasifikaci.

@param authorAffiliation - pricleneni manualni klasifikace
@param affiliations - pole pricleneni z klasifikace
@return bool
""" 
def AuthorAffiliationCompare(authorAffiliation, affiliations):
    global errCode
    global globSuccRatio
    
    #porovnani vsech pricleneni z klasifikace
    for item in affiliations:
        #odstraneni rusivych znaku
        item = re.sub(r"\,", "", item)
        item = re.sub(r"\.", "", item)
        item = re.sub(r"\"", "", item)
        item = re.sub(r"\'", "", item)
        item = re.sub(r"\-", "", item)
        item = re.sub(r"\s+", "", item)
        item = re.sub(r"\*", "", item)
        authorAffiliation = re.sub(r"\,", "", authorAffiliation)
        authorAffiliation = re.sub(r"\.", "", authorAffiliation)
        authorAffiliation = re.sub(r"\\\"", "", authorAffiliation)
        authorAffiliation = re.sub(r"\'", "", authorAffiliation)
        authorAffiliation = re.sub(r"\-", "", authorAffiliation)
        authorAffiliation = re.sub(r"\s+", "", authorAffiliation)
        authorAffiliation = re.sub(r"\*", "", authorAffiliation)
        
        #TODO: IFovat
        item = re.sub(r"[^a-zA-Z]", "", item)
        authorAffiliation = re.sub(r"[^a-zA-Z]", "", authorAffiliation)
        
        #porovnani
        tmpLen = float(len(item)/float(len(authorAffiliation)))
        #print "tmpLen"
        #print tmpLen
        if re.search(re.escape(authorAffiliation), item) != None or (re.search(item, re.escape(authorAffiliation)) != None and tmpLen >= globSuccRatio):
                sys.stderr.write("affiliation nalezen\n")
                
                #zvyseni citace oznacenych pricleneni
                AddToMarked("marked", "affiliation", 1)
                
                #zvyseni citace dobre oznacenych pricleneni
                AddToMarked("wellMarked", "affiliation", 1)
                
                return True
    
    return False

"""
Funkce pro vyhodnoceni klasifikace Autoru, coz zahrnuje jejich jmena, emaily a organizace.

@param file
@param xmlLabel
@param xmlHeader
@return
"""
def AuthorsCheck(file, xmlLabel, xmlHeader):
    #pocet autoru v manualni klasifikaci
    authorAll = len(file["authors"])
    
    #pocet emailu v manualni klasifikaci
    emailAll = GetEmailCnt(file["authors"])
    
    #pocet pricleneni v manualni klasifikaci
    affiliationAll = GetAffiliationCnt(file["authors"])
    
    #pocet autoru v klasifikaci
    authorCnt = 0
    
    #pocet emailu v klasifikaci
    emailCnt = 0
    
    #pocet pricleneni v klasifikaci
    affiliationCnt = 0
    
    #ziskani pole jmen klasifikace
    authors = AuthorNameCheck(xmlHeader)
    
    #ziskani pole emailu klasifikace
    emails = AuthorEmailCheck(xmlHeader, xmlLabel)
    
    #ziskani pole pricleneni klasifikace
    affiliations = AuthorAffiliationCheck(xmlHeader, xmlLabel)
    
    for author in file["authors"]:
        #vyhodnoceni jmen autoru
        if AuthorNameCompare(author["name"], authors):
            authorCnt += 1
        
        #vyhodnoceni emailu autoru
        if AuthorEmailCompare(author["email"], emails):
            emailCnt += 1
        
        #vyhodnoceni pricleneni autoru
        if AuthorAffiliationCompare(author["organization"], affiliations):
            affiliationCnt += 1
    
    #pokud klasifikace oznacila vice casti dokumentu nez bylo nalezeno, je treba provest korekci. Tzn. zvysit citace oznacenych casti.
    #korekce jmen autoru
    if len(authors) > authorCnt:
        AddToMarked("marked", "author", (len(authors) - authorCnt))
    
    #korekce emailu
    if len(emails) > emailCnt:
        AddToMarked("marked", "email", (len(emails) - emailCnt))
    
    #korekce affiliation
    if len(affiliations) > affiliationCnt:
        AddToMarked("marked", "affiliation", (len(affiliations) - affiliationCnt))
    
    #tisk vysledku klasifikace
    #jmena autoru
    className = "Author"
    PrintClassInfo(className, authorAll, authorCnt, False)
    
    #jmena autoru
    PrintClassInfo("Email", emailAll, emailCnt, False)
    
    #jmena autoru
    PrintClassInfo("Affiliation", affiliationAll, affiliationCnt, False)

"""
Funkce pro vyhodnoceni klasifikace abstrakt.

@param file
@param xmlLabel
@param xmlHeader
@return
"""
def AbstractCheck(file, xmlLabel, xmlHeader):
    globSuccRatio
    #ziskani abstraktu z klasifikace hlavicky
    xmlAbstract = xmlHeader.SearchElemText(xmlHeader, "abstract")
    
    #zachrana, pokud v klasifikaci hlavicky nebyl abstrakt nalezen
    if not xmlAbstract:
        xmlAbstract = xmlLabel.SearchElemText(xmlLabel, "abstract")
    
    #TODO: odstranit radek
    #print "ABSTRACT"
    #print xmlAbstract
    
    if file["abstract"] != "null":
        if xmlAbstract:
            #odstraneni rusivych znaku
            xmlAbstract = re.sub(r"\-(\s+)?", "", xmlAbstract)
            xmlAbstract = re.sub(r"\"", "", xmlAbstract)
            xmlAbstract = re.sub(r"\n", " ", xmlAbstract)
            xmlAbstract = re.sub(r"\,", "", xmlAbstract)
            xmlAbstract = re.sub(r"\.", "", xmlAbstract)
            xmlAbstract = re.sub(r"\'", "", xmlAbstract)
            xmlAbstract = re.sub(r"&gt", ">", xmlAbstract)
            xmlAbstract = re.sub(r"Abstract", "", xmlAbstract)
            xmlAbstract = re.sub(r"ABSTRACT", "", xmlAbstract)
            xmlAbstract = re.sub(r"\s+", "", xmlAbstract)
            xmlAbstract = re.sub(r"\^", "", xmlAbstract)
            file["abstract"] = re.sub(r"\\\"", "", file["abstract"])
            file["abstract"] = re.sub(r"\n", " ", file["abstract"])
            file["abstract"] = re.sub(r"\-(\s+)?", "", file["abstract"])
            file["abstract"] = re.sub(r"\.", "", file["abstract"])
            file["abstract"] = re.sub(r"\,", "", file["abstract"])
            file["abstract"] = re.sub(r"\'", "", file["abstract"])
            file["abstract"] = re.sub(r"\^", "", file["abstract"])
            file["abstract"] = re.sub(r"\s+", "", file["abstract"])
            
            #TODO: IFovat
            xmlAbstract = re.sub(r"[^a-zA-Z]", "", xmlAbstract)
            file["abstract"] = re.sub(r"[^a-zA-Z]", "", file["abstract"])
            
            #tisk
            #print "LSR"
            #print xmlAbstract
            #print "Manual"
            #print file["abstract"]
            
            #porovnani
            tmpLen = float(len(xmlAbstract)/float(len(file["abstract"])))
            #print "tmpLen"
            #print tmpLen
            if (re.search(re.escape(file["abstract"]), xmlAbstract) != None) or (re.search(re.escape(xmlAbstract), file["abstract"]) != None and tmpLen >= globSuccRatio):
                sys.stderr.write("Abstract nalezen\n")
                #sys.stdout.write("Abstract nalezen\n")
                
                #zvyseni citace oznacenych abstraktu
                AddToMarked("marked", "abstract", 1)
                
                #zvyseni citace oznacenych abstraktu
                AddToMarked("wellMarked", "abstract", 1)
                
                #vypis vysledku klasifikace
                PrintClassInfo("Abstract", 1, 1, True)
            else:
                #zvyseni citace oznacenych abstraktu
                AddToMarked("marked", "abstract", 1)
                
                #vypis vysledku klasifikace
                PrintClassInfo("Abstract", 1, 0, True)
    else:
        if xmlAbstract:
            #zvyseni citace oznacenych abstraktu
            AddToMarked("marked", "abstract", 1)
            
            #vypis vysledku klasifikace
            PrintClassInfo("Abstract", 0, 1, True)
        else:
            #vypis vysledku klasifikace
            PrintClassInfo("Abstract", 0, 0, True)

"""
Funkce pro ziskani kapitol klasifikace.

@param xmlLabel
@return chapters - pole kapitol
"""
def ChaptersCheck(xmlLabel):
    #pole nadpisu
    chapters = []
    
    #ziskani nadpisu klasifikace
    xmlSectionHeaderSelect = xmlLabel.Select(xmlLabel, "sectionHeader", [])
    
    for item in xmlSectionHeaderSelect:
        #ziskani textu nadpisu z podstromu XML
        xmlSectionHeader = item.SearchElemText(item, "sectionHeader")
        
        #ulozeni nadpisu
        chapters.append(xmlSectionHeader)
    
    #return
    return chapters

"""
Funkce pro ziskani podkapitol klasifikace.

@param xmlLabel
@return chapters - pole kapitol
"""
def SubChaptersCheck(xmlLabel):
    #pole podnadpisu
    subchapters = []
    
    #ziskani podnadpisu klasifikace
    xmlSubSectionHeaderSelect = xmlLabel.Select(xmlLabel, "subsectionHeader", [])
    
    for item in xmlSubSectionHeaderSelect:
        #ziskani textu podnadpisu z podstromu XML
        xmlSubSectionHeader = item.SearchElemText(item, "subsectionHeader")
        
        #ulozeni podnadpisu
        subchapters.append(xmlSubSectionHeader)
    
    #return
    return subchapters

"""
Funkce pro porovnani kapitol z klasifikace dokumentu s manualni klasifikaci.

@param chapterName - kapitola manualni klasifikace
@param chapters - pole kapitol z klasifikace
@return bool
""" 
def ChaptersCompare(chapterName, chapters):
    global globSuccRatio
    
    if chapterName:
        #porovnani kapitoly manualni klasifikace s kazdou kapitolou klasifikace
        for item in chapters:
            item = re.sub(r"\n", " ", item)
            item = re.sub(r"\s+", "", item)
            item = re.sub(r"\-", "", item)
            item = re.sub(r"^\d+\.?", "", item)
            item = re.sub(r"&gt\s?", "", item)
            chapterName = re.sub(r"\s+", "", chapterName)
            chapterName = re.sub(r"\-", "", chapterName)
            chapterName = re.sub(r"^\d+\.?", "", chapterName)
            
            #TODO: IFovat
            item = re.sub(r"[^a-zA-Z]", "", item)
            chapterName = re.sub(r"[^a-zA-Z]", "", chapterName)
            
            if item:
                #tisk
                #print "LSR"
                #print item
                #print "Manual"
                #print chapterName
                
                tmpLen = float(len(item)/float(len(chapterName)))
                #print "tmpLen"
                #print tmpLen
                if re.search(re.escape(chapterName), item) != None or (re.search(re.escape(item), chapterName) != None and tmpLen >= globSuccRatio):
                    sys.stderr.write("sectionHeader nalezen\n")
                    #sys.stdout.write("sectionHeader nalezen\n")
                    
                    #zvyseni citace oznacenych kapitol
                    AddToMarked("marked", "sectionHeader", 1)
                    
                    #zvyseni citace dobre oznacenych kapitol
                    AddToMarked("wellMarked", "sectionHeader", 1)
                    
                    return True
            
            #print "\n"
    
    return False

"""
Funkce pro porovnani podkapitol z klasifikace dokumentu s manualni klasifikaci.

@param subchapterName - podkapitola manualni klasifikace
@param subchapters - pole podkapitol z klasifikace
@return bool
""" 
def SubChaptersCompare(subchapterName, subchapters):
    global globSuccRatio
    
    if subchapterName:
        #porovnani podkapitoly manualni klasifikace s kazdou podkapitolou klasifikace
        for item in subchapters:
            item = re.sub(r"\n", " ", item)
            item = re.sub(r"\s+", "", item)
            item = re.sub(r"\-", "", item)
            item = re.sub(r"_", "", item)
            item = re.sub(r"\,", "", item)
            item = re.sub(r"^\d+\.\d+", "", item)
            item = re.sub(r"\'", "", item)
            subchapterName = re.sub(r"\s+", "", subchapterName)
            subchapterName = re.sub(r"\-", "", subchapterName)
            subchapterName = re.sub(r"_", "", subchapterName)
            subchapterName = re.sub(r"\,", "", subchapterName)
            subchapterName = re.sub(r"\'", "", subchapterName)
            subchapterName = re.sub(r"^\d+\.\d+", "", subchapterName)
            
            #TODO: IFovat
            item = re.sub(r"[^a-zA-Z]", "", item)
            subchapterName = re.sub(r"[^a-zA-Z]", "", subchapterName)
            
            #tisk
            #print "LSR"
            #print item
            #print "Manual"
            #print subchapterName
                
            tmpLen = float(len(item)/float(len(subchapterName)))
            #print "tmpLen"
            #print tmpLen
            
            if re.search(re.escape(subchapterName), item) != None or (re.search(re.escape(item), subchapterName) != None and tmpLen >= globSuccRatio):
                sys.stderr.write("subsectionHeader nalezen\n")
                #sys.stdout.write("subsectionHeader nalezen\n")
                #print "\n"
                
                #zvyseni citace oznacenych podkapitol
                AddToMarked("marked", "subsectionHeader", 1)
                
                #zvyseni citace dobre oznacenych podkapitol
                AddToMarked("wellMarked", "subsectionHeader", 1)
                
                return True
    
    return False

"""
Funkce pro ziskani poctu podkapitol manualni klasifikace.

@param chapters - pole kapitol
@return subchapterAll
"""
def GetSubChapters(chapters):
    #citac podkapitol
    subchapterAll = 0
    
    for item in chapters:
        subchapterAll += len(item["subsectionHeader"])
    
    #return
    return subchapterAll

"""
Funkce pro vyhodnoceni klasifikace kapitol a podkapitol.

@param file
@param xmlLabel
@param xmlHeader
@return
"""
def Sub_ChaptersCheck(file, xmlLabel, xmlHeader):
    #citac uspesne porovnanych kapitol
    chapterCnt = 0
    
    #pocet kapitol v dokumentu ziskany z manualni klasifikace
    chapterAll = len(file["chapters"])
    
    #citac uspesne porovnanych podkapitol
    subchapterCnt = 0
    
    #pocet podkapitol v dokumentu ziskany z manualni klasifikace
    subchapterAll = GetSubChapters(file["chapters"])    
    
    #ziskani kapitol
    chapters = ChaptersCheck(xmlLabel)
    
    #ziskani podkapitol
    subchapters = SubChaptersCheck(xmlLabel)
    
    #vyhodnoceni klasifikace
    for item in file["chapters"]:
        #vyhodnoceni kapitoly
        if ChaptersCompare(item["name"], chapters):
            chapterCnt += 1
        
        #podkapitoly se prochazi jednotlive
        for subchapter in item["subsectionHeader"]:
            #vyhodnoceni podkapitoly
            if SubChaptersCompare(subchapter, subchapters):
                subchapterCnt += 1
    
    #korekce citace oznacenych kapitol
    if len(chapters) > chapterCnt:
        AddToMarked("marked", "sectionHeader", (len(chapters) - chapterCnt))
    
    #korekce citace oznacenych podkapitol
    if len(subchapters) > subchapterCnt:
        AddToMarked("marked", "subsectionHeader", (len(subchapters) - subchapterCnt))
    
    #vypis vysledku
    #vypis kapitol
    PrintClassInfo("SectionHeader", chapterAll, chapterCnt, False)
    
    #vypis podkapitol
    PrintClassInfo("SubSectionHeader", subchapterAll, subchapterCnt, False)

"""
Funkce pro vyhodnoceni klasifikace porovnanim s manualni klasifikaci.

@param file
@param refBool - znaci, ktera sada se aktualne zkouma
@return 
"""
def CheckClassification(file, refBool):
    global errCode
    global marked
    
    #Prvni sada
    if not refBool:
        try:
            with open("out/" + file["fileName"] + ".out.xml") as f: pass
        except IOError as e:
            sys.stderr.write("Oh dear.\n")
            return
        
        xml = xmlParser.XMLUnit()
        xml.LoadFile("out/" + file["fileName"] + ".out.xml")
    #Druha sada
    else:
        try:
            with open("out2/" + file["fileName"] + ".out.xml") as f: pass
        except IOError as e:
            sys.stderr.write("Oh dear.\n")
            return
        
        xml = xmlParser.XMLUnit()
        xml.LoadFile("out2/" + file["fileName"] + ".out.xml")
    
    #ziskani vysledky jednotlivych casti klasifikace
    algorithm = xml.Select(xml, "algorithm", [])
    
    #pri klasifikaci doslo k chybe a tak nebyla zadna cast klasifikace nalezena
    if not algorithm:
        return
    
    #obecna klasifikace
    xmlLabel = algorithm[0]
    
    #klasifikace hlavicky dokumentu
    xmlHeader = algorithm[1]
    
    #Vyhodnoceni titulu
    TitleCheck(file, xmlLabel, xmlHeader)
    
    #Vyhodnoceni autoru
    AuthorsCheck(file, xmlLabel, xmlHeader)
    
    #Vyhodnoceni abstraktu
    AbstractCheck(file, xmlLabel, xmlHeader)
    
    #Vyhodnoceni kapitol a podkapitol
    Sub_ChaptersCheck(file, xmlLabel, xmlHeader)

#================== Parsovani manualni klasifikace ==================
def ParseAndCheckFiles(readedData, refBool):
    global errCode
    fileCnt = 0
    
    readedData = re.sub(r"^\[\s*", "", readedData, 1)
    
    while readedData:
        
        if re.search(r"^\s*\]\s*$", readedData):
            break
        
        readedData = re.sub(r"^\{\s*", "", readedData, 1)
        
        #jmeno souboru
        retArray = File(readedData)
        readedData = retArray[0]
        fileName = retArray[1]
        
        #zvyseni citace souboru
        fileCnt += 1
        
        retArray = Metadata(readedData, refBool)
        readedData = retArray[0]
        file = retArray[1]
        file["fileName"] = fileName
        
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\}\s*,?\s*", "", readedData, 1)
        
        #proved vyhodnoceni klasifikace
        CheckClassification(file, refBool)
        
        #citac zpracovanych souboru
        if fileCnt < 10:
            print "                                                                            "+str(fileCnt) + "\n"
        elif fileCnt < 100:
            print "                                                                           "+str(fileCnt)+ "\n"
        else:
            print "                                                                          "+str(fileCnt) + "\n"
    
    #TODO: odstranit radek
    #sys.exit(0)

def PrintResults():
    global marked
    
    #Spocteni Precision, Recall a FScore
    try:
        precisionTitle = (float(marked["wellMarked"]["title"]))  /  float(marked["marked"]["title"])
    except KeyError:
        sys.stderr.write("marked - KeyError\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print "WELLMARKET"
        print marked["wellMarked"]
        print ""
        print "MARKET"
        print marked["marked"]
        sys.exit(errCode["summarizeErr"])
        
    recallTitle = (float(marked["wellMarked"]["title"])) / float(marked["realCount"]["title"])
    titleFScore = 2*((precisionTitle*recallTitle)/(precisionTitle+recallTitle)) * 100
    
    precisionAuthor = (float(marked["wellMarked"]["author"]))  /  float(marked["marked"]["author"])
    recallAuthor = (float(marked["wellMarked"]["author"])) / float(marked["realCount"]["author"])
    authorFScore = 2*((precisionAuthor*recallAuthor)/(precisionAuthor+recallAuthor)) * 100
    
    precisionEmail = (float(marked["wellMarked"]["email"]))  /  float(marked["marked"]["email"])
    recallEmail = (float(marked["wellMarked"]["email"])) / float(marked["realCount"]["email"])
    emailFScore = 2*((precisionEmail*recallEmail)/(precisionEmail+recallEmail)) * 100
    
    precisionSection = (float(marked["wellMarked"]["sectionHeader"]))  /  float(marked["marked"]["sectionHeader"])
    recallSection = (float(marked["wellMarked"]["sectionHeader"])) / float(marked["realCount"]["sectionHeader"])
    sectionFScore = 2*((precisionSection*recallSection)/(precisionSection+recallSection)) * 100
    
    precisionSubSection = (float(marked["wellMarked"]["subsectionHeader"]))  /  float(marked["marked"]["subsectionHeader"])
    recallSubSection = (float(marked["wellMarked"]["subsectionHeader"])) / float(marked["realCount"]["subsectionHeader"])
    subsectionFScore = 2*((precisionSubSection*recallSubSection)/(precisionSubSection+recallSubSection)) * 100
    
    precisionAbstract = (float(marked["wellMarked"]["abstract"]))  /  float(marked["marked"]["abstract"])
    recallAbstract = (float(marked["wellMarked"]["abstract"])) / float(marked["realCount"]["abstract"])
    abstractFScore = 2*((precisionAbstract*recallAbstract)/(precisionAbstract+recallAbstract)) * 100
    
    precisionAffiliation = (float(marked["wellMarked"]["affiliation"]))  /  float(marked["marked"]["affiliation"])
    recallAffiliation = (float(marked["wellMarked"]["affiliation"])) / float(marked["realCount"]["affiliation"])
    affiliationFScore = 2*((precisionAffiliation*recallAffiliation)/(precisionAffiliation+recallAffiliation)) * 100
    
    print "+==================+===================="+                "+==================="+                "+==================="+                "+=============="+                                                                           "+=============="+                                                                      "+=============="+                                                                              "+"
    print "|Class             |   F-Measure Score  "+                "|     Precision     "+                "|       Recall      "+                "|  Real Count  "+                                                                           "|    Marked    "+                                                                      "|  Well-Marked "+                                                                              "|"
    print "+==================+===================="+                "+==================="+                "+==================="+                "+=============="+                                                                           "+=============="+                                                                      "+=============="+                                                                              "+"
    print "|Title             |   " + "{0:2.10f}".format(titleFScore) +           "    |   " + "{0:2.10f}".format(precisionTitle) +          "    |   " + "{0:2.10f}".format(recallTitle)+           "    |      " + str(marked["realCount"]["title"]) .zfill(4)                   + "    |      " + str(marked["marked"]["title"]).zfill(4)                    + "    |      " + str(marked["wellMarked"]["title"]).zfill(4)                    + "    |"
    print "|Author            |   " + "{0:2.10f}".format(authorFScore) +       "    |   " + "{0:2.10f}".format(precisionAuthor) +      "    |   " + "{0:2.10f}".format(recallAuthor)+       "    |      " + str(marked["realCount"]["author"]).zfill(4)                  + "    |      " + str(marked["marked"]["author"]).zfill(4)                   + "    |      " + str(marked["wellMarked"]["author"]).zfill(4)                   + "    |"
    print "|E-Mail            |   " + "{0:2.10f}".format(emailFScore) +         "    |   " + "{0:2.10f}".format(precisionEmail)+         "    |   " + "{0:2.10f}".format(recallEmail)  +        "    |      " + str(marked["realCount"]["email"]) .zfill(4)                   + "    |      " + str(marked["marked"]["email"]).zfill(4)                     + "    |      " + str(marked["wellMarked"]["email"]).zfill(4)                    + "    |"
    print "|Affiliation       |   " + "{0:2.10f}".format(affiliationFScore) +    "    |   " + "{0:2.10f}".format(precisionAffiliation)+   "    |   " + "{0:2.10f}".format(recallAffiliation) +   "    |      " + str(marked["realCount"]["affiliation"]) .zfill(4)         + "    |      " + str(marked["marked"]["affiliation"]).zfill(4)          + "    |      " + str(marked["wellMarked"]["affiliation"]).zfill(4)          + "    |"
    print "|Abstract          |   " + "{0:2.10f}".format(abstractFScore) +     "    |   " + "{0:2.10f}".format(precisionAbstract)+    "    |   " + "{0:2.10f}".format(recallAbstract)    + "    |      " + str(marked["realCount"]["abstract"]) .zfill(4)               + "    |      " + str(marked["marked"]["abstract"]).zfill(4)              + "    |      " + str(marked["wellMarked"]["abstract"]).zfill(4)              + "    |"
    print "|Section Header    |   " + "{0:2.10f}".format(sectionFScore) +       "    |   " + "{0:2.10f}".format(precisionSection) +    "    |   " + "{0:2.10f}".format(recallSection)  +     "    |      "  + str(marked["realCount"]["sectionHeader"]).zfill(4)      + "    |      "   + str(marked["marked"]["sectionHeader"]).zfill(4)       + "    |      " + str(marked["wellMarked"]["sectionHeader"]).zfill(4)      + "    |"
    print "|SubSection Header |   " + "{0:2.10f}".format(subsectionFScore) + "    |   " + "{0:2.10f}".format(precisionSubSection)+"    |   " + "{0:2.10f}".format(recallSubSection) +"    |      " + str(marked["realCount"]["subsectionHeader"]).zfill(4) + "    |      " + str(marked["marked"]["subsectionHeader"]).zfill(4) + "    |      " + str(marked["wellMarked"]["subsectionHeader"]).zfill(4) + "    |"
    print "+------------------+--------------------"+                 "+-------------------"+                 "+-------------------"+                 "+--------------"+                                                                          "+--------------"+                                                                       "+--------------"+                                                                              "+"

def InitMarked():
    global marked
    
    #inicializace marked seznamu
    marked["marked"]["title"] = 0
    marked["marked"]["author"] = 0
    marked["marked"]["email"] = 0
    marked["marked"]["sectionHeader"] = 0
    marked["marked"]["subsectionHeader"] = 0
    marked["marked"]["abstract"] = 0
    marked["marked"]["affiliation"] = 0
    
    #inicializace marked seznamu
    marked["wellMarked"]["title"] = 0
    marked["wellMarked"]["author"] = 0
    marked["wellMarked"]["email"] = 0
    marked["wellMarked"]["sectionHeader"] = 0
    marked["wellMarked"]["subsectionHeader"] = 0
    marked["wellMarked"]["abstract"] = 0
    marked["wellMarked"]["affiliation"] = 0

#================== Main ==================
def main():
    mode = FIRST | SECOND
    #mode = FIRST
    #mode = SECOND
    
    #inicializace seznamu
    InitMarked()
    
    #manualClassification.txt
    if mode & FIRST == FIRST:
        readedData = ""
        text_fd = ""
        try:
            #text_fd = codecs.open("manualClassification.txt", 'r', "utf-8")
            text_fd = codecs.open("manualClassification.txt", 'r')
        except IOError:
            sys.stderr.write("Nelze otevrit soubor " + "manualClassification.txt\n")
            sys.exit(errCode["fileErr"])
            
        readedData = text_fd.read()
        text_fd.close()
        
        #Naparsovani manualni klasifikace a vyhodnoceni
        ParseAndCheckFiles(readedData, False)
    
    #manualClassificationWithReferences
    if mode & SECOND == SECOND:
        readedData = ""
        text_fd = ""
        try:
            text_fd = codecs.open("manualClassificationWithReferences.txt", 'r')
        except IOError:
            sys.stderr.write("Nelze otevrit soubor " + "manualClassificationWithReferences.txt\n")
            sys.exit(errCode["fileErr"])
            
        readedData = text_fd.read()
        text_fd.close()
        
        #Naparsovani manualni klasifikace a vyhodnoceni
        ParseAndCheckFiles(readedData, True)
    
    #tisk vysledku
    PrintResults()
    
    #ukonceni programu
    sys.exit(errCode["AllOk"])

#================== Entry point ==================
main()
