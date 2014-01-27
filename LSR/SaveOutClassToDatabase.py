#!/usr/bin/python
# -*- coding: utf-8 -*-

import optparse
import psycopg2
import sys
import re
import os
import codecs
import xmlParser
import psycopg2

# Funkce pro ziskani titulu z XML
#@param1 vysledek klasifikace hlavicky reprezentovan v XML
#@param2 vysledek obecne klasifikace reprezentovan v XML
#@return pole obsahujici titul dokumentu
def GetTitle(xmlHeader, xmlLabel):
    
    xmlTitle = xmlHeader.SearchElemText(xmlHeader, "title")
    
    # Muze se stat, ze klasifikace titulu v xmlHeader se nezdari
    # zde je pokus o zachranu v xmlLabel
    if not xmlTitle:
        xmlTitle = xmlLabel.SearchElemText(xmlLabel, "title")
    
    #########################################
    #TODO: Zde je mozne provest filtraci nesmyslnych znaku a slov #
    #########################################
    
    #return
    retArray = []
    retArray.append(xmlTitle)
    return retArray

# Funkce pro ziskani autoru z XML
#@param1 vysledek klasifikace hlavicky reprezentovan v XML
#@param2 vysledek obecne klasifikace reprezentovan v XML
#@return pole obsahujici autory dokumentu
def GetAuthors(xmlHeader, xmlLabel):
    authors = []
    
    xmlAuthorsName = xmlHeader.Select(xmlHeader, "author", [])
    
    # Ve vysledku klasifikace se muze nachazet vice casti klasifikovanych jako nazev autoru
    for item in xmlAuthorsName:
        # Ziskani textu z XML podstromu obsahujici jmena autoru
        xmlAuthorName = item.SearchElemText(item, "author")
        
        # Odstraneni and, ktere by zpusobilo oznaceni dvou autoru jako jednoho
        xmlAuthorName = re.sub(r"(\,)?\s+and\s+", ",", xmlAuthorName)
        
        #########################################
        #TODO: Zde je mozne provest filtraci nesmyslnych znaku a slov #
        #########################################
        
        # V jedne oznacene casti se muze nachazet vice autoru
        while re.search(r"^[^\,]+", xmlAuthorName):
            # Ziskani autora
            tmpAuthor = re.search(r"^[^\,]+", xmlAuthorName).group(0)
            
            # Odstraneni autora ze souboru autoru
            xmlAuthorName = re.sub(r"^[^\,]+\s*\,?\s*", "", xmlAuthorName, 1)
            
            # Ulozeni autora do pole
            authors.append(tmpAuthor)
    
    #return
    retArray = []
    retArray.append(authors)
    return retArray

# Funkce pro ziskani pricleneni z XML
#@param1 vysledek klasifikace hlavicky reprezentovan v XML
#@param2 vysledek obecne klasifikace reprezentovan v XML
#@return pole obsahujici pricleneni dokumentu
def GetAffiliations(xmlHeader, xmlLabel):
    affiliations = []
    xmlAddresses = []
    
    xmlAuthorAffiliationSelect = xmlHeader.Select(xmlHeader, "affiliation", [])
    
    # Zachrana z obecne klasifikace
    if not xmlAuthorAffiliationSelect:
        xmlAuthorAffiliationSelect = xmlLabel.Select(xmlLabel, "affiliation", [])
    
    # Ziskani adres (je tak z duvodu, ze do databaze se uklada pricleneni + adresa, ale klasifikator tyto dve casti dokumentu rozlisuje)
    xmlAddressSelect = xmlHeader.Select(xmlHeader, "address", [])
    
    # Ulozeni vsech adres
    if xmlAddressSelect:
        for i in range(len(xmlAddressSelect)):
            xmlAddresses.append(xmlAddressSelect[i].SearchElemText(xmlAddressSelect[i], "address"))
    
    # Ulozeni vsech pricleneni
    for i in range(len(xmlAuthorAffiliationSelect)):
        # Ziskani pricleneni
        xmlAuthorAffiliation = xmlAuthorAffiliationSelect[i].SearchElemText(xmlAuthorAffiliationSelect[i], "affiliation")
        
        # Existuje adresa, ktera pravdepodobne patri k pricleneni
        if len(xmlAddresses) > i :
            xmlAuthorAffiliation += " " + xmlAddresses[i]
        
        #########################################
        #TODO: Zde je mozne provest filtraci nesmyslnych znaku a slov #
        #########################################
        
        # Ulozeni pricleneni
        affiliations.append(xmlAuthorAffiliation)
    
    #return
    retArray = []
    retArray.append(affiliations)
    return retArray

# Funkce na ziskani emailu
#@param1 vysledek klasifikace hlavicky reprezentovan v XML
#@param2 vysledek obecne klasifikace reprezentovan v XML
#@return pole obsahujici emaily autoru dokumentu
def GetEmails(xmlHeader, xmlLabel):
    emails = []
    errState = False
    
    xmlAuthorsEmail = xmlHeader.Select(xmlHeader, "email", [])
    
    # Zachrana z obecne klasifikace
    if not xmlAuthorsEmail:
        xmlAuthorsEmail = xmlLabel.Select(xmlLabel, "email", [])
    
    for item in xmlAuthorsEmail:
        # Ziskani textu z XML podstromu obsahujici email
        xmlAuthorEmail = item.SearchElemText(item, "email")
        
        if not re.search(r"@", xmlAuthorEmail):
            continue
        
        # Odstraneni rusivych znaku
        xmlAuthorEmail = re.sub(r"\\", "", xmlAuthorEmail)
        xmlAuthorEmail = re.sub(r"\.\s+", ".", xmlAuthorEmail)
        xmlAuthorEmail = re.sub(r"\s+@", "@", xmlAuthorEmail)
        
        #{name1(,|/) name2(,|/) ...}@domain
        while re.search(r"\{[^\}]+\}",  xmlAuthorEmail) != None:
            # Nacteni celeho souboru emailu
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
                errState = True
                break
            
            # Ulozeni casti pred @
            try:
                tmpEmailPreAt = re.search(r"\{([^\}]*)\}", tmpEmail).group(0)
            except AttributeError:
                sys.stderr.write("Nastala vyjimka pri zpracovani emailu!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                errState = True
                break
            
            # Ulozeni casti po @ vcetne
            try:
                tmpEmailPostAt = re.search(r"@(\.)?\w+((\-|\.)\w+)*\.\w+", tmpEmail).group(0)
            except AttributeError:
                sys.stderr.write("Nastala vyjimka pri zpracovani emailu!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                errState = True
                break
            
            # Odstraneni tohoto souboru emailu
            xmlAuthorEmail = re.sub(r"(\{([^\}]+)\}@(\.)?\w+((\-|\.)\w+)*\.\w+)|(\{([^\}]+)\})", "",  xmlAuthorEmail, 1)
            
            # Ziskani jednotlivych emailu ze souboru emailu
            # odstraneni svorek
            tmpEmailPreAt = re.sub(r"(\{|\})", "", tmpEmailPreAt, 2)
            
            # Ziskani jmena
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
                    errState = True
                    break
                
                tmpEmailPreAt = re.sub(r"^\w+((\-|\.)\w+)*\s*(\,|/|\|)?\s*", "", tmpEmailPreAt, 1)
                
                # Slouceni jmena a koncovky
                tmpEmailDone = tmpName + tmpEmailPostAt
                
                #########################################
                #TODO: Zde je mozne provest filtraci nesmyslnych znaku a slov #
                #########################################
                
                # Ulozeni do pole
                emails.append(tmpEmailDone)
        
        if errState:
            break
        
        #name@domain
        while re.search(r"\w+((\-|\.)\w+)*@(\.)?\w+((\-|\.)\w+)*\.\w+", xmlAuthorEmail):
            # Ziskani emailu
            tmpEmail = re.search(r"\w+((\-|\.)\w+)*@(\.)?\w+((\-|\.)\w+)*\.\w+", xmlAuthorEmail).group(0)
            
            # Odstraneni emailu ze souboru mailu
            xmlAuthorEmail = re.sub(r"\w+((\-|\.)\w+)*@(\.)?\w+((\-|\.)\w+)*\.\w+", "", xmlAuthorEmail, 1)
            
            #########################################
            #TODO: Zde je mozne provest filtraci nesmyslnych znaku a slov #
            #########################################
            
            # Ulozeni emailu
            emails.append(tmpEmail)
    
    #return
    retArray = []
    retArray.append(emails)
    return retArray

# Funkce pro ziskani abstraktu
#@param1 vysledek klasifikace hlavicky reprezentovan v XML
#@param2 vysledek obecne klasifikace reprezentovan v XML
#@return pole obsahujici abstrakt dokumentu
def GetAbstract(xmlHeader, xmlLabel):
    
    #TODO: Opravit mezery v oddelenych slovech
    xmlAbstract = xmlHeader.SearchElemText(xmlHeader, "abstract")
    
    # Zachrana, pokud v klasifikaci hlavicky nebyl abstrakt nalezen
    if not xmlAbstract:
        xmlAbstract = xmlLabel.SearchElemText(xmlLabel, "abstract")
    
    #########################################
    #TODO: Zde je mozne provest filtraci nesmyslnych znaku a slov #
    #########################################
    
    #return
    retArray = []
    retArray.append(xmlAbstract)
    return retArray

# Funkce pro ziskani nadpisu (kapitol)
#@param1 vysledek klasifikace hlavicky reprezentovan v XML
#@param2 vysledek obecne klasifikace reprezentovan v XML
#@return pole obsahujici nadpisy(kapitoly) dokumentu
def GetSectionHeaders(xmlHeader, xmlLabel):
    chapters = []
    
    xmlSectionHeaderSelect = xmlLabel.Select(xmlLabel, "sectionHeader", [])
    
    for item in xmlSectionHeaderSelect:
        # Ziskani textu nadpisu z podstromu XML
        xmlSectionHeader = item.SearchElemText(item, "sectionHeader")
        
        #########################################
        #TODO: Zde je mozne provest filtraci nesmyslnych znaku a slov #
        #########################################
        
        # Ulozeni nadpisu
        chapters.append(xmlSectionHeader)
    
    #return
    retArray = []
    retArray.append(chapters)
    return retArray

# Funkce pro ziskani podnadpisu(podkapitol)
#@param1 vysledek klasifikace hlavicky reprezentovan v XML
#@param2 vysledek obecne klasifikace reprezentovan v XML
#@return pole obsahujici podnadpisy(podkapitoly) dokumentu
def GetSubSectionHeaders(xmlHeader, xmlLabel):
    subchapters = []
    
    xmlSubSectionHeaderSelect = xmlLabel.Select(xmlLabel, "subsectionHeader", [])
    
    for item in xmlSubSectionHeaderSelect:
        # Ziskani textu podnadpisu z podstromu XML
        xmlSubSectionHeader = item.SearchElemText(item, "subsectionHeader")
        
        #########################################
        #TODO: Zde je mozne provest filtraci nesmyslnych znaku a slov #
        #########################################
        
        # Ulozeni podnadpisu
        subchapters.append(xmlSubSectionHeader)
    
    #return
    retArray = []
    retArray.append(subchapters)
    return retArray

# Funkce pro ulozeni titulu
#@param1 session
#@param2 connection
#@param3 titul dokumentu
#@return id titulu, tedy i celeho dokumentu
def SaveTitle(cursor, connection, xmlTitle):
    title_id = ""
    commitNeeded = False
    
    if xmlTitle:
        
        #########################################
        #TODO: Zde je mozne provest filtraci nesmyslnych znaku a slov #
        #########################################
        
        # Prohledani databaze, zda uz se v ni tento titul nenachazi
        cursor.execute("SELECT id FROM data_xbreit00_test.project WHERE title = (%s);", (xmlTitle, ))
        tmp = cursor.fetchone()
        
        # Nenachazi, je treba jej do databaze ulozit
        if tmp == None:
            commitNeeded = True
            
            # Vlozeni titulu
            cursor.execute("""INSERT INTO data_xbreit00_test.project (title) VALUES (%s);""", (xmlTitle, ))
            
            # Potvrzeni zmen v databazi
            connection.commit()
            
            # Ziskani id titulu pro dalsi pouziti
            cursor.execute("SELECT id FROM data_xbreit00_test.project WHERE title = (%s);", (xmlTitle, ))
            title_id = cursor.fetchone()[0]
        
        #Titul v databazi jiz je, ale id muzeme potrebovat
        else:
            title_id = tmp[0]
    
    #return
    retArray = []
    retArray.append(title_id)
    return retArray

#Funkce pro transformaci UNICODE znaku na jejich 7-bit ASCII reprezentaci
#param1 retezec k transformaci
#return transformovany retezec
def TransformToASCII(itemAuthorASCII):
    
    while re.search(r"\xc3|\xc4|\xc5", itemAuthorASCII):
        #A
        itemAuthorASCII = re.sub(r"\xc3\x80", "A", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\x81", "A", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\x82", "A", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\x83", "A", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\x84", "A", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\x85", "A", itemAuthorASCII)
        
        itemAuthorASCII = re.sub(r"\xc4\x80", "A", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x82", "A", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x84", "A", itemAuthorASCII)
        #AE
        itemAuthorASCII = re.sub(r"\xc3\x86", "Ae", itemAuthorASCII)
        #C
        itemAuthorASCII = re.sub(r"\xc3\x87", "C", itemAuthorASCII)
        
        itemAuthorASCII = re.sub(r"\xc4\x86", "C", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x88", "C", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x8a", "C", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x8c", "C", itemAuthorASCII)
        #D
        itemAuthorASCII = re.sub(r"\xc4\x8e", "D", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x90", "D", itemAuthorASCII)
        #E
        itemAuthorASCII = re.sub(r"\xc3\x88", "E", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\x89", "E", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\x8a", "E", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\x8b", "E", itemAuthorASCII)
        
        itemAuthorASCII = re.sub(r"\xc4\x92", "E", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x94", "E", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x96", "E", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x98", "E", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x9a", "E", itemAuthorASCII)
        #G
        itemAuthorASCII = re.sub(r"\xc4\x9c", "G", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x9e", "G", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\xa0", "G", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\xa2", "G", itemAuthorASCII)
        #H
        itemAuthorASCII = re.sub(r"\xc4\xa4", "H", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\xa6", "H", itemAuthorASCII)
        #I
        itemAuthorASCII = re.sub(r"\xc3\x8c", "I", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\x8d", "I", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\x8e", "I", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\x8f", "I", itemAuthorASCII)
        
        itemAuthorASCII = re.sub(r"\xc4\xa8", "I", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\xaa", "I", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\xac", "I", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\xae", "I", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\xb0", "I", itemAuthorASCII)
        #IJ
        itemAuthorASCII = re.sub(r"\xc4\xb2", "Ij", itemAuthorASCII)
        #J
        itemAuthorASCII = re.sub(r"\xc4\xb4", "J", itemAuthorASCII)
        #K
        itemAuthorASCII = re.sub(r"\xc4\xb6", "K", itemAuthorASCII)
        #L
        itemAuthorASCII = re.sub(r"\xc4\xb9", "L", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\xbb", "L", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\xbd", "L", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\xbf", "L", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x81", "L", itemAuthorASCII)
        #ETH
        itemAuthorASCII = re.sub(r"\xc3\x90", "Eth", itemAuthorASCII)
        #N
        itemAuthorASCII = re.sub(r"\xc3\x91", "N", itemAuthorASCII)
        
        itemAuthorASCII = re.sub(r"\xc5\x83", "N", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x85", "N", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x87", "N", itemAuthorASCII)
        #O
        itemAuthorASCII = re.sub(r"\xc3\x92", "O", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\x93", "O", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\x94", "O", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\x95", "O", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\x96", "O", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\x98", "O", itemAuthorASCII)
        
        itemAuthorASCII = re.sub(r"\xc5\x8c", "O", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x8e", "O", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x90", "O", itemAuthorASCII)
        #R
        itemAuthorASCII = re.sub(r"\xc5\x94", "R", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x96", "R", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x98", "R", itemAuthorASCII)
        #S
        itemAuthorASCII = re.sub(r"\xc5\x9a", "S", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x9c", "S", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x9e", "S", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xa0", "S", itemAuthorASCII)
        #T
        itemAuthorASCII = re.sub(r"\xc5\xa2", "T", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xa4", "T", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xa6", "T", itemAuthorASCII)
        #U
        itemAuthorASCII = re.sub(r"\xc3\x99", "U", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\x9a", "U", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\x9b", "U", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\x9c", "U", itemAuthorASCII)
        
        itemAuthorASCII = re.sub(r"\xc5\xa8", "U", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xaa", "U", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xac", "U", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xae", "U", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xb0", "U", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xb2", "U", itemAuthorASCII)
        #W
        itemAuthorASCII = re.sub(r"\xc5\xb4", "W", itemAuthorASCII)
        #Y
        itemAuthorASCII = re.sub(r"\xc3\x9d", "Y", itemAuthorASCII)
        
        itemAuthorASCII = re.sub(r"\xc5\xb6", "Y", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xb8", "Y", itemAuthorASCII)
        #Z
        itemAuthorASCII = re.sub(r"\xc5\xba", "Z", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xbc", "Z", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xbe", "Z", itemAuthorASCII)
        #SS
        itemAuthorASCII = re.sub(r"\xc3\x9f", "ss", itemAuthorASCII)
        #a
        itemAuthorASCII = re.sub(r"\xc3\xa0", "a", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xa1", "a", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xa2", "a", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xa3", "a", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xa4", "a", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xa5", "a", itemAuthorASCII)
        
        itemAuthorASCII = re.sub(r"\xc4\x81", "a", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x83", "a", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x85", "a", itemAuthorASCII)
        #ae
        itemAuthorASCII = re.sub(r"\xc3\xa6", "ae", itemAuthorASCII)
        #c
        itemAuthorASCII = re.sub(r"\xc3\xa7", "c", itemAuthorASCII)
        
        itemAuthorASCII = re.sub(r"\xc4\x87", "c", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x89", "c", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x8b", "c", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x8d", "c", itemAuthorASCII)
        #d
        itemAuthorASCII = re.sub(r"\xc4\x8f", "d", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x91", "d", itemAuthorASCII)
        #e
        itemAuthorASCII = re.sub(r"\xc3\xa8", "e", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xa9", "e", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xaa", "e", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xab", "e", itemAuthorASCII)
        
        itemAuthorASCII = re.sub(r"\xc4\x93", "e", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x95", "e", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x97", "e", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x99", "e", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x9b", "e", itemAuthorASCII)
        #g
        itemAuthorASCII = re.sub(r"\xc4\x9d", "g", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\x9f", "g", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\xa1", "g", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\xa3", "g", itemAuthorASCII)
        #h
        itemAuthorASCII = re.sub(r"\xc4\xa5", "h", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\xa7", "h", itemAuthorASCII)
        #i
        itemAuthorASCII = re.sub(r"\xc3\xac", "i", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xad", "i", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xae", "i", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xaf", "i", itemAuthorASCII)
        
        itemAuthorASCII = re.sub(r"\xc4\xa9", "i", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\xab", "i", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\xad", "i", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\xaf", "i", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\xb1", "i", itemAuthorASCII)
        #ij
        itemAuthorASCII = re.sub(r"\xc4\xb3", "ij", itemAuthorASCII)
        #j
        itemAuthorASCII = re.sub(r"\xc4\xb5", "j", itemAuthorASCII)
        #k
        itemAuthorASCII = re.sub(r"\xc4\xb7", "k", itemAuthorASCII)
        #l
        itemAuthorASCII = re.sub(r"\xc4\xba", "l", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\xbc", "l", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc4\xbe", "l", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x80", "l", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x82", "l", itemAuthorASCII)
        #n
        itemAuthorASCII = re.sub(r"\xc3\xb1", "n", itemAuthorASCII)
        
        itemAuthorASCII = re.sub(r"\xc5\x84", "n", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x86", "n", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x88", "n", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x89", "n", itemAuthorASCII)
        #o
        itemAuthorASCII = re.sub(r"\xc3\xb2", "o", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xb3", "o", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xb4", "o", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xb5", "o", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xb6", "o", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xb8", "o", itemAuthorASCII)
        
        itemAuthorASCII = re.sub(r"\xc5\x8d", "o", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x8f", "o", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x91", "o", itemAuthorASCII)
        #r
        itemAuthorASCII = re.sub(r"\xc5\x95", "r", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x97", "r", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x99", "r", itemAuthorASCII)
        #s
        itemAuthorASCII = re.sub(r"\xc5\x9b", "s", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x9d", "s", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\x9f", "s", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xa1", "s", itemAuthorASCII)
        #t
        itemAuthorASCII = re.sub(r"\xc5\xa3", "t", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xa5", "t", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xa7", "t", itemAuthorASCII)
        #u
        itemAuthorASCII = re.sub(r"\xc3\xb9", "u", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xba", "u", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xbb", "u", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xbc", "u", itemAuthorASCII)
        
        itemAuthorASCII = re.sub(r"\xc5\xa9", "u", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xab", "u", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xad", "u", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xaf", "u", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xb1", "u", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xb3", "u", itemAuthorASCII)
        #w
        itemAuthorASCII = re.sub(r"\xc5\xb5", "w", itemAuthorASCII)
        #y
        itemAuthorASCII = re.sub(r"\xc3\xbd", "y", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc3\xbf", "y", itemAuthorASCII)
        
        itemAuthorASCII = re.sub(r"\xc5\xb7", "y", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xb9", "y", itemAuthorASCII)
        #z
        itemAuthorASCII = re.sub(r"\xc5\xba", "z", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xbd", "z", itemAuthorASCII)
        itemAuthorASCII = re.sub(r"\xc5\xbe", "z", itemAuthorASCII)
    
    #return
    return itemAuthorASCII

#Funkce pro ulozeni autoru
#@param1 session
#@param2 connection
#@param3 pole autoru dokumentu
def SaveAuthors(cursor, connection, authors, title_id):
    author_id = ""
    commitNeeded = False
    
    for itemAuthor in authors:
        if itemAuthor == None:
            continue
        
        #########################################
        #TODO: Zde je mozne provest filtraci nesmyslnych znaku a slov #
        #########################################
        
        # Ziskani jmena
        if re.search(r"[^\s]+", itemAuthor):
            first_name = re.search(r"[^\s]+", itemAuthor).group(0)
        
        # Ziskani prijmeni
        if re.search(r"[^\s]+\s*$", itemAuthor):
            last_name = re.search(r"[^\s]+\s*$", itemAuthor).group(0)
            last_name = re.sub(r"\s+", "", last_name)
        
        # Slouzi k ulozeni jmena autora v 7-bitove ASCII
        itemAuthorASCII = itemAuthor
        
        # Pokud se ve jmene autora nachazi UNICODE znaky, je treba je transformovat na jejich reprezentaci v 7-bit ASCII
        if re.search(r"\xc3|\xc4|\xc5", itemAuthorASCII):
            itemAuthorASCII = TransformToASCII(itemAuthorASCII)
        
        # Prohledani databaze, zda se autor v ni jiz nenachazi
        cursor.execute("SELECT id FROM data_xbreit00_test.person WHERE full_name = (%s);", (itemAuthor, ))
        tmp = cursor.fetchone()
        
        # Autor jeste v databazi neni
        if tmp == None:
            commitNeeded = True
            
            # Ulozeni autora
            cursor.execute("""INSERT INTO data_xbreit00_test.person (first_name, last_name, full_name, full_name_ascii) VALUES (%s, %s, %s, %s);""", (first_name, last_name, itemAuthor.decode('utf-8'), itemAuthorASCII.decode('utf-8')))
            
            # Potvrzeni zmen v databazi
            connection.commit()
            
            # Ziskani id autora
            cursor.execute("SELECT id FROM data_xbreit00_test.person WHERE full_name = (%s);", (itemAuthor, ))
            author_id = cursor.fetchone()[0]
        
        # Autor sice v databazi je, ale id se muze hodit
        else:
            author_id = tmp[0]
        
        # Je nutne navazat autora na dokument, ale nejdrive je nutne overit, zda jiz neni navazany
        if title_id != '':
            cursor.execute("SELECT id FROM data_xbreit00_test.person_meta_xbreit00 WHERE person_id = (%s) AND title_id = (%s);", (author_id, title_id, ))
            tmp = cursor.fetchone()
        else:
            tmp = "err"
        
        #pokud jeste neni navazany
        if tmp == None:
            cursor.execute("""INSERT INTO data_xbreit00_test.person_meta_xbreit00 (person_id,title_id) VALUES (%s,%s);""", (author_id, title_id, ))
            
            connection.commit()
    
    #return
    return

# Funkce pro ulozeni pricleneni
#@param1 session
#@param2 connection
#@param3 pole pricleneni dokumentu
def SaveAffiliations(cursor, connection, affiliations, title_id):
    aff_id = ""
    commitNeeded = False
    
    for itemAff in affiliations:
        
        #########################################
        #TODO: Zde je mozne provest filtraci nesmyslnych znaku a slov #
        #########################################
        
        if len(itemAff) > 255:
            itemAff = itemAff[:128]
        
        # Vyhledani, zda uz se affiliation nenachazi v databazi
        cursor.execute("SELECT id FROM data_xbreit00_test.organization WHERE title = (%s);", (itemAff, ))
        tmp = cursor.fetchone()
        
        # Nenachazi, je treba jej ulozit
        if tmp == None:
            commitNeeded = True
            
            # Ulozeni affiliation do databaze
            cursor.execute("""INSERT INTO data_xbreit00_test.organization (title, title_normalized) VALUES (%s, %s);""", (itemAff, itemAff, ))
            
            # Potvrzeni zmen v databazi
            connection.commit()
            
            # Ziskani id affiliation
            cursor.execute("SELECT id FROM data_xbreit00_test.organization WHERE title = (%s);", (itemAff, ))
            aff_id = cursor.fetchone()[0]
        
        # Affiliation se sice v databazi nachazi, ale id mozna jeste budeme potrebovat
        else:
            aff_id = tmp[0]
        
        # Je nutne navazat affiliation na dokument, ale nejdrive je nutne overit, zda jiz neni navazany
        if title_id != '':
            cursor.execute("SELECT id FROM data_xbreit00_test.organization_meta_xbreit00 WHERE organization_id = (%s) AND title_id = (%s);", (aff_id, title_id, ))
            tmp = cursor.fetchone()
        else:
            tmp = "err"
        
        # Pokud jeste neni navazany
        if tmp == None:
            cursor.execute("""INSERT INTO data_xbreit00_test.organization_meta_xbreit00 (organization_id,title_id) VALUES (%s,%s);""", (aff_id, title_id, ))
            
            connection.commit()
    
    #return
    return

# Funkce pro ulozeni emailu
#@param1 session
#@param2 connection
#@param3 pole emailu dokumentu
def SaveEmails(cursor, connection, emails, title_id):
    email_id = ""
    commitNeeded = False
    
    for itemEmail in emails:
        
        #########################################
        #TODO: Zde je mozne provest filtraci nesmyslnych znaku a slov #
        #########################################
        
        # Kontrola, zda se email uz v databazi nenachazi
        cursor.execute("SELECT id FROM data_xbreit00_test.contact WHERE email = (%s);", (itemEmail, ))
        tmp = cursor.fetchone()
        
        # Nenachazi, je treba jej ulozit
        if tmp == None:
            commitNeeded = True
            
            # Ulozeni emailu do databaze
            cursor.execute("""INSERT INTO data_xbreit00_test.contact (email) VALUES (%s);""", (itemEmail, ))
            
            # Potvrzeni zmen v databazi
            connection.commit()
            
            # Ziskani id emailu
            cursor.execute("SELECT id FROM data_xbreit00_test.contact WHERE email = (%s);", (itemEmail, ))
            email_id = cursor.fetchone()[0]
        
        # Nachazi, ale id muzeme jeste potrebovat
        else:
            email_id = tmp[0]
        
        # Je nutne navazat email na dokument, ale nejdrive je nutne overit, zda jiz neni navazany
        if title_id != '':
            cursor.execute("SELECT id FROM data_xbreit00_test.contact_meta_xbreit00 WHERE contact_id = (%s) AND title_id = (%s);", (email_id, title_id, ))
            tmp = cursor.fetchone()
        else:
            tmp = "err"
        
        # Pokud jeste neni navazany
        if tmp == None:
            cursor.execute("""INSERT INTO data_xbreit00_test.contact_meta_xbreit00 (contact_id,title_id) VALUES (%s,%s);""", (email_id, title_id, ))
            
            connection.commit()
    
    #return
    return

# Funkce pro ulozeni abstraktu
#@param1 session
#@param2 connection
#@param3 abstrakt dokumentu
def SaveAbstract(cursor, connection, xmlAbstract, title_id):
    abstract_id = ""
    commitNeeded = False
    
    if xmlAbstract:
        
        #########################################
        #TODO: Zde je mozne provest filtraci nesmyslnych znaku a slov #
        #########################################
        
        # Kontrola, zda se abstrakt uz v databazi nenachazi
        cursor.execute("SELECT id FROM data_xbreit00_test.annotation_xbreit00 WHERE content = (%s);", (xmlAbstract, ))
        tmp = cursor.fetchone()
        
        # Nenachazi, je treba jej ulozit
        if tmp == None:
            commitNeeded = True
            
            # Ulozeni abstraktu do databaze
            cursor.execute("""INSERT INTO data_xbreit00_test.annotation_xbreit00 (content) VALUES (%s);""", (xmlAbstract, ))
            
            # Potvrzeni zmen v databazi
            connection.commit()
            
            # Ziskani id abstraktu
            cursor.execute("SELECT id FROM data_xbreit00_test.annotation_xbreit00 WHERE content = (%s);", (xmlAbstract, ))
            abstract_id = cursor.fetchone()[0]
        
        # Nachazi, ale id muzeme jeste potrebovat
        else:
            abstract_id = tmp[0]
        
        # Je nutne navazat abstrakt na dokument, ale nejdrive je nutne overit, zda jiz neni navazany
        if title_id != '':
            cursor.execute("SELECT id FROM data_xbreit00_test.annotation_meta_xbreit00 WHERE annotation_id = (%s) AND title_id = (%s);", (abstract_id, title_id, ))
            tmp = cursor.fetchone()
        else:
            tmp = "err"
        
        # Pokud jeste neni navazany
        if tmp == None:
            cursor.execute("""INSERT INTO data_xbreit00_test.annotation_meta_xbreit00 (annotation_id,title_id) VALUES (%s,%s);""", (abstract_id, title_id, ))
        
            connection.commit()
    
    #return
    return

""" MAIN """
def main():
    input = ""
    
    # Nacteni pristupovzch udaju do databaze
    text_fd = ""
    try:
        text_fd = codecs.open("databaseAccess.dat", 'r', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + "databaseAccess.dat" + "\n")
        sys.exit(1)
    
    #host:dbname:user:password
    databaseAccess = text_fd.read()
    
    # Uzavrneni souboru
    text_fd.close()
    
    databaseAccess = re.sub(r"\n", "", databaseAccess)
    datAccArr = re.split(r"\:", databaseAccess)
    
    if len(datAccArr) < 4:
        sys.stderr.write("Soubor databaseAccess.dat je spatne naplnen, neni tak mozne se pripojit k databazi!\n")
        sys.exit(1)
    
    
    # Vytvoreni spojeni
    connection = psycopg2.connect("host=" + datAccArr[0] + " dbname=" + datAccArr[1] + " user=" + datAccArr[2] + " password=" + datAccArr[3])
    cursor = connection.cursor()
    
    # Nacteni jiz ulozenych dokumentu
    text_fd = ""
    try:
        text_fd = codecs.open("OutSavedToDB.dat", 'r', "utf-8")
    except IOError:
        sys.stderr.write("Nelze otevrit soubor " + "OutSavedToDB.dat" + "\n")
        sys.exit(1)
    
    dictData = text_fd.read()
    
    # Rozdeleni dat
    dictArr = re.split(r"\n", dictData)
    del dictArr[-1]
    
    # Ulozeni nazvu dokumentu do slovniku
    dict = {}
    for item in dictArr:
        dict[item] = ""
    
    # Uzavrneni souboru
    text_fd.close()
    
    # Nastaveni cesty ke klasifikovanym dokumentum
    #path = "/mnt/minerva1/nlp-in/athena3/rrs/reresearch.ocr/"
    path = "./outClass/"
    
    # Serazeni souboru a slozek ze zadane cesty
    files = os.listdir(path)
    files = sorted(files)
    
    # Prochazi vsechny slozky ze zadane cesty
    for item in files:
        # Neni-li slozka, preskoc
        if not os.path.isdir(path + item):
            continue
        
        # Serazeni obsahu prochazene slozky
        subPath = path + item + "/"
        subFiles = os.listdir(subPath)
        subFiles = sorted(subFiles)
        
        # Prochazi vsechny slozky z path + item (tzn. aktualne vybrana polozka)
        for itemSub in subFiles:
            # Neni-li slozka, preskoc
            if not os.path.isdir(subPath + itemSub):
                continue
            
            # Serazeni obsahu prochazene slozky
            finalPath = subPath + itemSub + "/"
            finalFiles = os.listdir(finalPath)
            
            # Prochazi vsechny soubory slozky z path + item + itemSub
            for itemFinal in finalFiles:
                #pole autoru
                authors = []
                
                #pole adres, ktere se budou pozdeji pridruzovat k pricleneni
                xmlAddresses = []
                
                #pole pricleneni
                affiliations = []
                
                #pole obsahujici emaily
                emails = []
                
                #pole nadpisu
                chapters = []
                
                #pole podnadpisu
                subchapters = []
                
                # Pokud byl soubor jiz ulozen, neni treba jej ukladat znova
                if dict.has_key(itemFinal):
                    print itemFinal + ": soubor ve slovniku"
                    continue
                else:
                    print itemFinal + ": soubor je zpracovavan"
                
                # Naparsovani daneho dokumentu. Ten je ulozen v XML podobe
                xml = xmlParser.XMLUnit()
                xml.LoadFile(finalPath + "/" + itemFinal)
                
                # Ziskani vysledku jednotlivych klasifikaci
                algorithm = xml.Select(xml, "algorithm", [])
                
                # Pri klasifikaci doslo k chybe a tak neni mozne s dokumentem dale pracovat
                if not algorithm or len(algorithm) < 2:
                    continue
                
                # Ulozeni "ukazatele" na vysledek obecne klasifikace
                xmlLabel = algorithm[0]
                
                # Ulozeni "ukazatele" na vysledek klasifikace hlavicky dokumentu
                xmlHeader = algorithm[1]
                
                #################### Ziskani jednotlivych casti dokumentu, ktere se budou ukladat do databaze ####################
                # Ziskani titulu dokumentu
                retArray = GetTitle(xmlHeader, xmlLabel)
                xmlTitle = retArray[0]
                
                # Ziskani autoru dokumentu
                retArray = GetAuthors(xmlHeader, xmlLabel)
                authors = retArray[0]
                
                # Ziskani pricleneni
                retArray = GetAffiliations(xmlHeader, xmlLabel)
                affiliations = retArray[0]
                
                # Ziskani emailu
                retArray = GetEmails(xmlHeader, xmlLabel)
                emails = retArray[0]
                
                # Ziskani abstraktu
                retArray = GetAbstract(xmlHeader, xmlLabel)
                xmlAbstract = retArray[0]
                
                # Ziskani nadpisu (kapitol)
                # Momentalne se do databaze neuklada
                retArray = GetSectionHeaders(xmlHeader, xmlLabel)
                chapters = retArray[0]
                
                # Ziskani podnadpisu (podkapitol)
                # Momentalne se do databaze neuklada
                retArray = GetSubSectionHeaders(xmlHeader, xmlLabel)
                subchapters = retArray[0]
                
                #################### Ulozeni jednotlivych casti dokumentu do databaze ####################
                # Titul
                retArray = SaveTitle(cursor, connection, xmlTitle)
                title_id = retArray[0]
                
                # Autori
                SaveAuthors(cursor, connection, authors, title_id)
                
                # Pricleneni
                SaveAffiliations(cursor, connection, affiliations, title_id)
                
                # Email
                SaveEmails(cursor, connection, emails, title_id)
                
                # Abstrakt
                SaveAbstract(cursor, connection, xmlAbstract, title_id)
                
                # Otevreni logovaciho souboru souboru
                fileLog = ""
                try:
                    fileLog = open("OutSavedToDB.dat", "a+")
                except IOError:
                    sys.stderr.write("Chyba pri otevirani souboru\n")
                    sys.exit(2)
                
                # Zapis zpracovaneho souboru
                fileLog.write(itemFinal + "\n")
                
                # Uzavrneni souboru
                fileLog.close()
    
    cursor.close()
    connection.close()
    sys.exit(0)

""" Entry point """
main()
