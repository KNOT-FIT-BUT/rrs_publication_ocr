#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re
import os
import codecs
import time

#TODO: projit vsechny fce a zjistit, zda se nejmenuji nektere stejne
#TODO: projit vsechny fce a pripadne doplnit korektnost vstupu, cili, ze vstupni retezec zacina tak, jak ma
#TODO: pro dulezita <> vytvorit slovnik, protoze jinak muze nespravne kl. slovo propadnout hodne hluboko bez hlaseni chyby
#TODO: pro fce pri pruchodu kontrolovat, zda jsou zabezpecena, aby tyto funkce neurezavali z readedData data neco, co k nim vubec nepatri
#TODO: projit jednotlive casti parseru a rozhodnout, co vse se ma ukladat
#TODO: projit jednotlive casti parseru a rozhodnout, kde se ma co ukladat
#TODO: asi zmenit logiku ukladani textu s informacemi. Mam pocit, ze ted se muze ulozit vice textu s jednim nastavenim, pritom se tam muze ukryvat napr jedno slovo italic stylem

#globalni promenne
#<character set>
characterSet = ""
ansicpg = 0
#<deffont>
deff = 0
adeff = 0
stshfdbch = 0
stshfloch = 0
stshfhich = 0
stshfbi = 0
#<deflang>
deflang = 0
deflangfe = 0
adeflang = 0
#<fonttbl>
globFonttbl = []

plain = {"deflang":""}

pard = {}

errCode = {"AllOk":0,
                  "parseErr":1, 
                  "fileErr":2, 
                  "summarizeErr":3, 
                  "processErr":4, 
                  "notImplemented":5
           }

#TODO: Pozor, to ze nejaky slovnik kl. slov je nazvan napr. brdrdef jeste neznamena, ze obsahuje vsechna kl. slova
#slova jsou vkladana podle potreby
globBrdrdef = {"brdrt":"", 
                         "brdrb":"", 
                         "brdrl":"", 
                         "brdrr":"", 
                         "brdrbtw":"", 
                         "brdrbar":"", 
                         "box":""}

globParfmt = {"par":"", 
                        "pard":"", 
                        "spv":"", 
                        "hyphpar":"", 
                        "intbl":"", 
                        "itap":"", 
                        "keep":"", 
                        "keepn":"", 
                        "level":"", 
                        "noline":"", 
                        "nowidctlpar":"", 
                        "widctlpar":"", 
                        "outlinelevel":"", 
                        "pagebb":"", 
                        "sbys":"", 
                        "s":"", 
                        "yts":"", 
                        "tscfirstrow":"", 
                        "tsclastrow":"", 
                        "tscfirstcol":"", 
                        "tsclastcol":"", 
                        "tscbandhorzodd":"", 
                        "tscbandhorzeven":"", 
                        "tscbandvertodd":"", 
                        "tscbandverteven":"", 
                        "tscnwcell":"", 
                        "tscnecell":"", 
                        "tscswcell":"", 
                        "tscsecell":"", 
                        "qc":"", 
                        "qj":"", 
                        "ql":"", 
                        "qr":"", 
                        "qd":"", 
                        "qk":"", 
                        "qt":"", 
                        "faauto":"", 
                        "fahang":"", 
                        "facenter":"", 
                        "faroman":"", 
                        "favar":"", 
                        "fafixed":"", 
                        "fi":"", 
                        "cufi":"", 
                        "li":"", 
                        "lin":"", 
                        "culi":"", 
                        "ri":"", 
                        "rin":"", 
                        "curi":"", 
                        "adjustright":"", 
                        "indmirror":"", 
                        "sb":"", 
                        "sa":"", 
                        "sbauto":"", 
                        "saauto":"", 
                        "lisb":"", 
                        "lisa":"", 
                        "sl":"", 
                        "slmult":"", 
                        "nosnaplinegrid":"", 
                        "contextualspace":"", 
                        "subdocument":"", 
                        "prauth":"", 
                        "prdate":"", 
                        "rtlpar":"", 
                        "ltrpar":"", 
                        "nocwrap":"", 
                        "nowwrap":"", 
                        "nooverflow":"", 
                        "aspalpha":"", 
                        "aspnum":"", 
                        "collapsed":"", 
                        "txbxtwno":"", 
                        "txbxtwalways":"", 
                        "txbxtwfirstlast":"", 
                        "txbxtwfirst":"", 
                        "txbxtwlast":"", 
                        "cbpat":""}

globApoctl = {"absw":"", 
                        "absh":"", 
                        "absnoovrlp":"", 
                        "nowrap":"", 
                        "dxfrtext":"", 
                        "dfrmtxtx":"", 
                        "dfrmtxty":"", 
                        "overlay":"", 
                        "wrapdefault":"", 
                        "wraparound":"", 
                        "wraptight":"", 
                        "wrapthrough":"", 
                        "dropcapli":"", 
                        "dropcapt":"", 
                        "phmrg":"", 
                        "phpg":"", 
                        "phcol":"", 
                        "posx":"", 
                        "posnegx":"", 
                        "posxc":"", 
                        "posxi":"", 
                        "posxo":"", 
                        "posxl":"", 
                        "posxr":"", 
                        "pvmrg":"", 
                        "pvpg":"", 
                        "pvpara":"", 
                        "posy":"", 
                        "posnegy":"", 
                        "posyt":"", 
                        "posyil":"", 
                        "posyb":"", 
                        "posyc":"", 
                        "posyin":"", 
                        "posyout":"", 
                        "abslock":"", 
                        "frmtxlrtb":"", 
                        "frmtxtbrl":"", 
                        "frmtxbtlr":"", 
                        "frmtxlrtbv":"", 
                        "frmtxtbrlv":""}

globTabdef = {"tx":"", 
                        "tb":"", 
                        "tqr":"", 
                        "tqc":"", 
                        "tqdec":"", 
                        "tldot":"", 
                        "tlmdot":"", 
                        "tlhyph":"", 
                        "tlul":"", 
                        "tlth":"", 
                        "tleq":""}

globShading = {"shading":"", 
                            "bghoriz":"", 
                            "bgvert":"", 
                            "bgfdiag":"", 
                            "bgbdiag":"", 
                            "bgcross":"", 
                            "bgdcross":"", 
                            "bgdkhoriz":"", 
                            "bgdkvert":"", 
                            "bgdkfdiag":"", 
                            "bgdkbdiag":"", 
                            "bgdkcross":"", 
                            "bgdkdcross":"", 
                            "cfpat":"", 
                            "cbpat":""}

#TODO: afs podle specifikace v <chrfmt> neni, ale OCR to tam stejne dal
globChrfmt = {"plain":"", 
                        "animtext":"", 
                        "accnone":"", 
                        "accdot":"", 
                        "acccomma":"", 
                        "acccircle":"", 
                        "accunderdot":"", 
                        "b":"", 
                        "caps":"", 
                        "cb":"", 
                        "cchs":"", 
                        "cf":"", 
                        "charscalex":"", 
                        "cs":"", 
                        "cgrid":"", 
                        "g":"", 
                        "gcw":"", 
                        "gridtbl":"", 
                        "dn":"", 
                        "embo":"", 
                        "expnd":"", 
                        "expndtw":"", 
                        "fittext":"", 
                        "f":"", 
                        "fs":"", 
                        "afs":"", 
                        "i":"", 
                        "impr":"", 
                        "kerning":"", 
                        "langfe":"", 
                        "langfenp":"", 
                        "lang":"", 
                        "langnp":"", 
                        "ltrch":"", 
                        "noproof":"", 
                        "nosupersub":"", 
                        "nosectexpand":"", 
                        "rtlch":"", 
                        "outl":"", 
                        "scaps":"", 
                        "shad":"", 
                        "strike":"", 
                        "striked1":"", 
                        "sub":"", 
                        "super":"", 
                        "ul":"", 
                        "ulc":"", 
                        "uld":"", 
                        "uldash":"", 
                        "uldashd":"", 
                        "uldashdd":"", 
                        "uldb":"", 
                        "ulhwave":"", 
                        "ulldash":"", 
                        "ulnone":"", 
                        "ulth":"", 
                        "ulthd":"", 
                        "ulthdash":"", 
                        "ulthdashd":"", 
                        "ulthdashdd":"", 
                        "ulthldash":"", 
                        "ululdbwave":"", 
                        "ulw":"", 
                        "ulwave":"", 
                        "up":"", 
                        "v":"", 
                        "webhidden":"", 
                        "ls":"", 
                        "ilvl":""} 

globSpec = {
                        "chdate":"", 
                        "chdpl":"", 
                        "chdpa":"", 
                        "chtime":"", 
                        "chpgn":"", 
                        "sectnum":"", 
                        "chftn":"", 
                        "chatn":"", 
                        "chftnsep":"", 
                        "chftnsepc":"", 
                        "cell":"", 
                        "nestcell":"", 
                        "row":"", 
                        "nestrow":"", 
                        "par":"", 
                        "sect":"", 
                        "page":"", 
                        "column":"", 
                        "line":"", 
                        "lbr":"", 
                        "softpage":"", 
                        "softcol":"", 
                        "softline":"", 
                        "softlheight":"", 
                        "tab":"", 
                        "emdash":"", 
                        "endash":"", 
                        "emspace":"", 
                        "enspace":"", 
                        "qmspace":"", 
                        "bullet":"", 
                        "lquote":"", 
                        "rquote":"", 
                        "ldblquote":"", 
                        "rdblquote":"", 
                        "ltrmark":"", 
                        "rtlmark":"", 
                        "zwbo":"", 
                        "zwnbo":"", 
                        "zwj":"", 
                        "zwnj":""}

globCelldef = {"clmgf":"", 
                        "clmrg":"", 
                        "clvmgf":"", 
                        "clvmrg":"", 
                        "cldglu":"", 
                        "celldgl":"", 
                        "clvertalt":"", 
                        "clvertalc":"", 
                        "clvertalb":"", 
                        "clbrdrt":"", 
                        "clbrdrl":"", 
                        "clbrdrr":"", 
                        "clbghoriz":"", 
                        "clbgvert":"", 
                        "clbgfdiag":"", 
                        "clbgbdiag":"", 
                        "clbgcross":"", 
                        "clbgdcross":"", 
                        "clbgdkhor":"", 
                        "clbgdkvert":"", 
                        "clbgdkfdiag":"", 
                        "clbgdkbdiag":"", 
                        "clbgdkcross":"", 
                        "clbgdkdcross":"", 
                        "clcfpat":"", 
                        "clcbpat":"", 
                        "clshdng":"", 
                        "cltxlrtb":"", 
                        "cltxtbrl":"", 
                        "cltxbtlr":"", 
                        "cltxlrtbv":"", 
                        "cltxtbrlv":"", 
                        "clFitText":"", 
                        "clNoWrap":"", 
                        "clftsWidth":"", 
                        "clwWidth":"", 
                        "clhidemark":"", 
                        "clmrgd":"", 
                        "clmrgdr":"", 
                        "clsplit":"", 
                        "clsplitr":"", 
                        "clmrgdauth":"", 
                        "clmrgddttm":"", 
                        "clins":"", 
                        "clinsauth":"", 
                        "clinsdttm":"", 
                        "cldel":"", 
                        "cldelauth":"", 
                        "cldeldttm":"", 
                        "clpadl":"", 
                        "clpadfl":"", 
                        "clpadt":"", 
                        "clpadft":"", 
                        "clpadb":"", 
                        "clpadfb":"", 
                        "clpadr":"", 
                        "clpadfr":"", 
                        "clspl":"", 
                        "clspfl":"", 
                        "clspt":"", 
                        "clspft":"", 
                        "clspb":"", 
                        "clspfb":"", 
                        "clspr":"", 
                        "clspfr":"", 
                        "cellx":"", 
                        "clbrdrb":""}

globPara = {}
globChr = {}
globForBrdrdef = {}
globForApoctl = {}
globForTabdef = {}
globForShading = {}
globTbl = {}
globDoc = {}
globSec = {}
globStyledef = {}
globStylename = {}
globStylesheet = []
globDefchp = {} #vicemene defaultni globChr
globDefpap = {} #vicemene defaultni globPara
globDefSec = {} #TODO: Zjistit defaultni nastaveni section
globNestrow = False
globTitle = ""
globSubject = ""
globAuthor = ""
globManager = ""
globCompany = ""
globOperator = ""
globComment = ""
globKeywords = ""
globCategory = ""
globDoccomm = ""

#pro odliseni zacatku tabulky a poznani, ze byla vlozena svorka
globTableBracer = False

#pro ukladani textu a informaci o nem
globTextData = []

#v urcitych pripadech by doslo k duplikaci textu
globWriteEnable = True

globPrintFunctionName = True

#pro ulozeni odstavcu vcetne dulezitych informaci
globParaList = []

#pro ulozeni odstavcu
globRawText = ""

#pro ulozeni sekci
globSectList = []

#seznam, kde se bude ukladat nastaveni odstavcu
globStack = []

#tabulka pro konverzi znaku
globExtASCIITable = {"09":u"",
                                    "52":u"R", 
                                    "72":u"r", 
                                    "80":u"€", 
                                    "81":u"", 
                                    "82":u"‚", 
                                    "83":u"",
                                    "84":u"„",
                                    "85":u"…", 
                                    "86":u"†", 
                                    "87":u"‡", 
                                    "88":u"", 
                                    "89":u"‰", 
                                    "8A":u"Š", 
                                    "8B":u"‹", 
                                    "8C":u"Ś", 
                                    "8D":u"Ť", 
                                    "8E":u"Ž", 
                                    "8F":u"Ź", 
                                    "90":u"", 
                                    "91":u"‘", 
                                    "92":u"’", 
                                    "93":u"“", 
                                    "94":u"”",
                                    "95":u"•",
                                    "96":u"–", 
                                    "97":u"—", 
                                    "98":u"", 
                                    "99":u"™", 
                                    "9A":u"š", 
                                    "9B":u"›", 
                                    "9C":u"ś", 
                                    "9D":u"ť", 
                                    "9E":u"ž", 
                                    "9F":u"ź", 
                                    "A0":u" ", 
                                    "A1":u"ˇ", 
                                    "A2":u"˘", 
                                    "A3":u"Ł", 
                                    "A4":u"¤", 
                                    "A5":u"Ą", 
                                    "A6":u"¦", 
                                    "A7":u"§",
                                    "A8":u"¨", 
                                    "A9":u"©", 
                                    "AA":u"Ş", 
                                    "AB":u"«", 
                                    "AC":u"¬", 
                                    "AD":u"", 
                                    "AE":u"®", 
                                    "AF":u"Ż", 
                                    "B0":u"°", 
                                    "B1":u"±", 
                                    "B2":u"˛", 
                                    "B3":u"ł", 
                                    "B4":u"´", 
                                    "B5":u"µ", 
                                    "B6":u"¶", 
                                    "B7":u"·", 
                                    "B8":u"¸", 
                                    "B9":u"ą", 
                                    "BA":u"ş", 
                                    "BB":u"»",
                                    "BC":u"Ľ", 
                                    "BD":u"˝", 
                                    "BE":u"ľ", 
                                    "BF":u"ż", 
                                    "C0":u"Ŕ", 
                                    "C1":u"Á", 
                                    "C2":u"Â", 
                                    "C3":u"Ă", 
                                    "C4":u"Ä", 
                                    "C5":u"Ĺ", 
                                    "C6":u"Ć", 
                                    "C7":u"Ç", 
                                    "C8":u"Č", 
                                    "C9":u"É", 
                                    "CA":u"Ę", 
                                    "CB":u"Ë", 
                                    "CC":u"Ě", 
                                    "CD":u"Í", 
                                    "CE":u"Î", 
                                    "CF":u"Ď", 
                                    "D0":u"Đ", 
                                    "D1":u"Ń", 
                                    "D2":u"Ň", 
                                    "D3":u"Ó", 
                                    "D4":u"Ô", 
                                    "D5":u"Ő", 
                                    "D6":u"Ö", 
                                    "D7":u"×", 
                                    "D8":u"Ř", 
                                    "D9":u"Ů", 
                                    "DA":u"Ú", 
                                    "DB":u"Ű", 
                                    "DC":u"Ü", 
                                    "DD":u"Ý", 
                                    "DE":u"Ţ", 
                                    "DF":u"ß", 
                                    "E0":u"ŕ", 
                                    "E1":u"á", 
                                    "E2":u"â", 
                                    "E3":u"ă", 
                                    "E4":u"ä", 
                                    "E5":u"ĺ", 
                                    "E6":u"ć", 
                                    "E7":u"ç", 
                                    "E8":u"č", 
                                    "E9":u"é", 
                                    "EA":u"ę", 
                                    "EB":u"ë", 
                                    "EC":u"ě", 
                                    "ED":u"í", 
                                    "EE":u"î", 
                                    "EF":u"ď", 
                                    "F0":u"đ", 
                                    "F1":u"ń", 
                                    "F2":u"ň", 
                                    "F3":u"ó", 
                                    "F4":u"ô", 
                                    "F5":u"ő", 
                                    "F6":u"ö", 
                                    "F7":u"÷", 
                                    "F8":u"ř", 
                                    "F9":u"ů", 
                                    "FA":u"ú", 
                                    "FB":u"ű", 
                                    "FC":u"ü", 
                                    "FD":u"ý", 
                                    "FE":u"ţ", 
                                    "FF":u"˙"}

#Performance
startTime = 0
endTime = 0

def TimeMeasureStart():
    global startTime
    
    startTime = time.time()
    return

#TODO: dokoncit!!
def TimeMeasureEnd():
    global startTime
    global endTime
    
    endTime = time.time()
    return

def PushToSectList():
    global errCode
    global globParaList
    global globSectList
    
    globSectList.append(globParaList)
    
    globParaList = []
    
    return

def PushToParaList():
    global errCode
    global globParaList
    global globTextData
    global globForApoctl
    global globForBrdrdef
    global globForShading
    global globForTabdef
    global globChr
    global globPara
    
    paraListItem = {}
    
    paraListItem["apoctl"] = globForApoctl.copy()
    paraListItem["brdrdef"] = globForBrdrdef.copy()
    paraListItem["shading"] = globForShading.copy()
    paraListItem["tabdef"] = globForTabdef.copy()
    paraListItem["chrfmt"] = globChr.copy()
    paraListItem["parfmt"] = globPara.copy()
    paraListItem["text"] = globTextData
    
    globTextData = []
    
    globParaList.append(paraListItem.copy())
    
    return

def PushToStack():
    global errCode
    global globStack
    global globForApoctl
    global globForBrdrdef
    global globForShading
    global globForTabdef
    global globChr
    global globPara
    
    stackItem = {}
    
    stackItem["apoctl"] = globForApoctl.copy()
    stackItem["brdrdef"] = globForBrdrdef.copy()
    stackItem["shading"] = globForShading.copy()
    stackItem["tabdef"] = globForTabdef.copy()
    stackItem["chrfmt"] = globChr.copy()
    stackItem["parfmt"] = globPara.copy()
    
    globStack.append(stackItem.copy())
    
    return

#TODO: Zde pozor, aby se pri del nesmazal i obsah nove nastavenych globalnich hodnot!!
def TopPopFromStack():
    global errCode
    global globStack
    global globForApoctl
    global globForBrdrdef
    global globForShading
    global globForTabdef
    global globChr
    global globPara
    
    globForApoctl = globStack[-1]["apoctl"]
    globForBrdrdef = globStack[-1]["brdrdef"]
    globForShading = globStack[-1]["shading"]
    globForTabdef = globStack[-1]["tabdef"]
    globChr = globStack[-1]["chrfmt"]
    globPara = globStack[-1]["parfmt"]
    
    del globStack[-1]
    
    return

#inicializace plain parametru a v pripade vyskytu \plain se nastavi tyto hodnoty
#TODO: dokoncit!
def InitPlain():
    global plain

#inicializace par parametru a v pripade vyskytu \pard se nastavi tyto hodnoty
#TODO: dokoncit!
def InitPard():
    global pard

#<character set>
#(\ansi | \mac | \pc | \pca)? \ansicpgN?
#@profile
def CharacterSet(readedData):
    global characterSet
    global ansicpg
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stdout.write("CharacterSet()\n")
        sys.stderr.write("CharacterSet()\n")
    
    #priznak nalezeni klicoveho slova pro kodovani
    charSet = False
    
    if re.match(r"\\ansi", readedData):
        charSet = True
        characterSet = "ansi"
        readedData = re.sub(r"^\\ansi\s*", "", readedData, 1)
    
    elif re.match(r"\\mac", readedData):
        charSet = True
        characterSet = "mac"
        readedData = re.sub(r"^\\mac\s*", "", readedData, 1)
    
    elif re.match(r"\\pc", readedData):
        charSet = True
        characterSet = "pc"
        readedData = re.sub(r"^\\pc\s*", "", readedData, 1)
    
    elif re.match(r"\\pca", readedData):
        charSet = True
        characterSet = "pca"
        readedData = re.sub(r"^\\pca\s*", "", readedData, 1)
    
    #ziskani typu kodovani
    if charSet and re.match(r"\\ansicpg", readedData):
        try:
            ansicpg = int(re.match(r"\\ansicpg\s*(\d+)", readedData).group(1))
        except AttributeError as e:
            sys.stderr.write("Chyba pri ansicpg!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        readedData = re.sub(r"^\\ansicpg\s*\d+\s*", "", readedData, 1)
    
    #nepatri do <character set>, ale v header se muze vyskytnout, protoze osetreno zde
    if re.match(r"\\uc", readedData):
        readedData = re.sub(r"^\\uc\s*\d+\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<from>?
#\fromtext | \fromhtml
#pro ucely NLP/KNOT nepotrebne
#@profile
def From(readedData):
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("From()\n")
        sys.stdout.write("From()\n")
    
    if re.match(r"\\fromtext\s*", readedData):
        readedData = re.sub(r"^\\fromhtml\s*(\d+)?\s*", "", readedData, 1)
    
    if re.match(r"\\fromhtml\s*(\d+)?\s*", readedData):
        readedData = re.sub(r"^\\fromhtml\s*(\d+)?\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<deffont>
#\deffN? \adeffN? (\stshfdbchN \stshflochN \stshfhichN \stshfbiN)?
#@profile
def Deffont(readedData):
    global deff
    global adeff
    global stshfdbch
    global stshfloch
    global stshfhich
    global stshfbi
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Deffont()\n")
        sys.stdout.write("Deffont()\n")
    
    if re.match(r"\\deff", readedData):
        try:
            deff = int(re.match(r"\\deff\s*(\d+)", readedData).group(1))
        except AttributeError as e:
            sys.stderr.write("Chyba pri deff!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        readedData = re.sub(r"^\\deff\s*\d+\s*", "", readedData, 1)
    
    if re.match(r"\\adeff", readedData):
        try:
            adeff = int(re.match(r"\\adeff\s*(\d+)", readedData).group(1))
        except AttributeError as e:
            sys.stderr.write("Chyba pri adeff!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        readedData = re.sub(r"^\\adeff\s*\d+\s*", "", readedData, 1)
    
    #Mam pocit, ze tuto cast OCR system moc nedodrzoval, takze budu postupovat,
    #jak kdyby klicova slova mohla byt v jakemkoli poradi
    if re.match(r"\\(stshfdbch|stshfloch|stshfhich|stshfbi)", readedData):
        #stshfdbch
        try:
            stshfdbch = int(re.search(r"\\stshfdbch\s*(\d+)", readedData).group(1))
        except AttributeError as e:
            sys.stderr.write("Chyba pri stshfdbch!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        readedData = re.sub(r"\\stshfdbch\s*\d+\s*", "", readedData, 1)
        
        #stshfloch
        try:
            stshfloch = int(re.match(r"\\stshfloch\s*(\d+)", readedData).group(1))
        except AttributeError as e:
            sys.stderr.write("Chyba pri stshfloch!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        readedData = re.sub(r"^\\stshfloch\s*\d+\s*", "", readedData, 1)
        
        #stshfhich
        try:
            stshfhich = int(re.match(r"\\stshfhich\s*(\d+)", readedData).group(1))
        except AttributeError as e:
            sys.stderr.write("Chyba pri stshfhich!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        readedData = re.sub(r"^\\stshfhich\s*\d+\s*", "", readedData, 1)
        
        #stshfbi
        try:
            stshfbi = int(re.match(r"\\stshfbi\s*(\d+)", readedData).group(1))
        except AttributeError as e:
            sys.stderr.write("Chyba pri stshfbi!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        readedData = re.sub(r"^\\stshfbi\s*\d+\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<deflang>
#\deflangN? \deflangfeN? \adeflangN?
#@profile
def Deflang(readedData):
    global deflang
    global deflangfe
    global adeflang
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Deflang()\n")
        sys.stdout.write("Deflang()\n")
    
    if re.match(r"\\deflang", readedData):
        try:
            deflang = int(re.match(r"\\deflang\s*(\d+)", readedData).group(1))
        except AttributeError as e:
            sys.stderr.write("Chyba pri deflang!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        readedData = re.sub(r"^\\deflang\s*\d+\s*", "", readedData, 1)
    
    if re.match(r"\\deflangfe", readedData):
        try:
            deflangfe = int(re.match(r"\\deflangfe\s*(\d+)", readedData).group(1))
        except AttributeError as e:
            sys.stderr.write("Chyba pri deflangfe!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        readedData = re.sub(r"^\\deflangfe\s*\d+\s*", "", readedData, 1)
    
    if re.match(r"\\adeflang", readedData):
        try:
            adeflang = int(re.match(r"\\adeflang\s*(\d+)", readedData).group(1))
        except AttributeError as e:
            sys.stderr.write("Chyba pri adeflang!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        readedData = re.sub(r"^\\adeflang\s*\d+\s*", "", readedData, 1)
    
    #Pozor!!! Tohle neni podle specifikace v 1.9.1, OCR si to uklada po svem
    if re.match(r"\\deflangfe", readedData):
        try:
            deflangfe = int(re.match(r"\\deflangfe\s*(\d+)", readedData).group(1))
        except AttributeError as e:
            sys.stderr.write("Chyba pri deflangfe!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        readedData = re.sub(r"^\\deflangfe\s*\d+\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<themefont>
#\flomajor | \fhimajor | \fdbmajor | \fbimajor | \flominor | \fhiminor | \fdbminor |
#\fbiminor
#Pro NLP/KNOT asi nepotrebne, takze jen odstraneni
#@profile
def Themefont(readedData):
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Themefont()\n")
        sys.stdout.write("Themefont()\n")
    
    if re.match(r"\\flomajor\s*", readedData):
        readedData = re.sub(r"^\\flomajor\s*", "", readedData, 1)
    
    if re.match(r"\\fhimajor\s*", readedData):
        readedData = re.sub(r"^\\fhimajor\s*", "", readedData, 1)
    
    if re.match(r"\\fdbmajor\s*", readedData):
        readedData = re.sub(r"^\\fdbmajor\s*", "", readedData, 1)
    
    if re.match(r"\\fbimajor\s*", readedData):
        readedData = re.sub(r"^\\fbimajor\s*", "", readedData, 1)
    
    if re.match(r"\\flominor\s*", readedData):
        readedData = re.sub(r"^\\flominor\s*", "", readedData, 1)
    
    if re.match(r"\\fhiminor\s*", readedData):
        readedData = re.sub(r"^\\fhiminor\s*", "", readedData, 1)
    
    if re.match(r"\\fdbminor\s*", readedData):
        readedData = re.sub(r"^\\fdbminor\s*", "", readedData, 1)
    
    if re.match(r"\\fbiminor\s*", readedData):
        readedData = re.sub(r"^\\fbiminor\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<fontfamily>
#\fnil | \froman | \fswiss | \fmodern | \fscript | \fdecor | \ftech | \fbidi
#@profile
def Fontfamily(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Fontfamily()\n")
        sys.stdout.write("Fontfamily()\n")
    
    #Not applicable
    if re.match(r"\\fnil", readedData):
        fontfamily = "nil"
        readedData = re.sub(r"^\\fnil\s*", "", readedData, 1)
    
    #Times New Roman, Palatino
    elif re.match(r"\\froman", readedData):
        fontfamily = "roman"
        readedData = re.sub(r"^\\froman\s*", "", readedData, 1)
    
    #Arial
    elif re.match(r"\\fswiss", readedData):
        fontfamily = "swiss"
        readedData = re.sub(r"^\\fswiss\s*", "", readedData, 1)
    
    #Courier New, Pica
    elif re.match(r"\\fmodern", readedData):
        fontfamily = "modern"
        readedData = re.sub(r"^\\fmodern\s*", "", readedData, 1)
    
    #Cursive
    elif re.match(r"\\fscript", readedData):
        fontfamily = "script"
        readedData = re.sub(r"^\\fscript\s*", "", readedData, 1)
    
    #Old English, ITC Zapf Chancery
    elif re.match(r"\\fdecor", readedData):
        fontfamily = "decor"
        readedData = re.sub(r"^\\fdecor\s*", "", readedData, 1)
    
    #Symbol, Wingdings
    elif re.match(r"\\ftech", readedData):
        fontfamily = "tech"
        readedData = re.sub(r"^\\ftech\s*", "", readedData, 1)
    
    #Miriam
    elif re.match(r"\\fbidi", readedData):
        fontfamily = "bidi"
        readedData = re.sub(r"^\\fbidi\s*", "", readedData, 1)
    
    else:
        sys.stderr.write("Chyba parseru - Fontfamily\n")
        sys.stderr.write(readedData[:128] + "\n")
        sys.exit(errCode["parseErr"])
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(fontfamily)
    return retArray

#@profile
def UN(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("UN()\n")
        sys.stdout.write("UN()\n")
    
    #nacteni dat
    try:
        data = re.match(r"[^\}]+", readedData).group(0)
    except AttributeError as e:
        sys.stderr.write("Nelze nacist data!\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        sys.exit(errCode["parseErr"])
    readedData = re.sub(r"^[^\}]+", "", readedData, 1)
            
    #muze se stat, ze text bude obsahovat }, nutne tedy osetrit
    while data[-1] == "\\":
        readedData = re.sub(r"^\}", "", readedData, 1)
        data += "\}"
        try:
            data += re.match(r"[^\}]+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist data!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        readedData = re.sub(r"^[^\}]+", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(data)
    return retArray

#<spec>
#@profile
def Spec(readedData):
    global errCode
    global globParaList
    global globSpec
    global globPara
    global globTextData
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Spec()\n")
        sys.stdout.write("Spec()\n")
    
    success = True
    
    #nacteni klicoveho slova
    try:
        keyword = re.match(r"\\([a-zA-Z]+)", readedData).group(1)
    except AttributeError as e:
        sys.stderr.write("Nelze nacist keyword!\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        sys.exit(errCode["parseErr"])
    #readedData = re.sub(r"^[a-zA-Z]+\s*", "", readedData, 1)
    
    sys.stderr.write("Keyword: " + keyword + "\n")
    
    #TODO: pridat akci
    #End of table cell.
    if keyword == "cell":
        if globPara.has_key("Intbl"):
            success = False
        
        else:
            sys.stderr.write("Doimplementovat!\n")
            sys.exit(0)
    
    #End of paragraph.
    elif keyword == "par":
        PushToParaList()
        
        readedData = re.sub(r"^\\par\s*", "", readedData, 1)
    
    #End of section and paragraph.
    elif keyword == "sect":
        PushToSectList()
        
        readedData = re.sub(r"^\\sect\s*", "", readedData, 1)
    
    #TODO: pridat akci
    #Tab character.
    elif keyword == "tab":
        #TODO: Doslo k padu na podivnem miste, ze ulozeni mimo index u souboru
        #ab11fc47fc26a5050364d14a7489b8795e3bdd2e.rtf
        #kdyztak prozkoumat blize
        if globTextData != []:
            globTextData[-1]["text"] += "\t"
        
        readedData = re.sub(r"^\\tab\s*", "", readedData, 1)
    
    #ostatni klic. slova jsou pro projekt NLP/KNOT nepotrebne
    elif globSpec.has_key(keyword):
        sys.stderr.write("Upozorneni: klicove slovo ze <spec> je vynechano a odstraneno, pokud je jeho vyznam dulezity, doimplementovat!\n")
        readedData = re.sub(r"^" + keyword + r"\s*", "", readedData, 1)
    
    else:
        #sys.stderr.write("Keyword " + keyword + " neodpovida <spec> viz. RTF dokumentace\n")
        #sys.exit(errCode["parseErr"])
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append("")
    retArray.append(success)
    return retArray

#<do>
#'{\*' \do <dohead> <dpinfo> '}'
#Pro projekt NLP/KNOT nepotrebne
#@profile
def Do(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Do()\n")
        sys.stdout.write("Do()\n")
    
    data = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\\do\s*", "", readedData, 1)
    
    if re.search(r"\\dptxbxmar", readedData):
        sys.stderr.write("Doimplementovat <do>\n")
        sys.exit(errCode["parseErr"])
    
    #odstraneni zbytku
    readedData = re.sub(r"^[^\}]+", "", readedData, 1)
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(data)
    return retArray

#<annot>
#<annotid> <atnauthor> <atntime>? \chatn <atnicn>? <annotdef>
#@profile
def Annot(readedData):
    sys.stderr.write("Doimplementovat <annot>\n")
    sys.exit(errCode["parseErr"])

#<bookmark>
#<bookstart> | <bookend>
#@profile
def Bookmark(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Bookmark()\n")
        sys.stdout.write("Bookmark()\n")
    
    data = {}
    
    data["name"] = "bookmark"
    
    #<bookstart>
    #'{\*' \bkmkstart (\bkmkcolfN? & \bkmkcollN?) #PCDATA '}'
    if re.match(r"\{\\\*\\bkmkstart", readedData):
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\{\\\*\\bkmkstart\s*", "", readedData, 1)
        
        #odstraneni klicovych slov
        while re.match(r"\\(bkmkcolf|bkmkcoll)", readedData):
            readedData =re.sub(r"^\\(bkmkcolf|bkmkcoll)\s*\d+\s*", "", readedData, 1)
        
        #nazev bookmarku
        bookmarkName = re.match(r"[^\}]+", readedData).group(0)
        readedData = re.sub(r"^[^\}]+", "", readedData, 1)
        
        #odstraneni nepotrebne casti
        readedData = re.sub(r"\}\s*", "", readedData, 1)
    
    #<bookend>
    #'{\*' \bkmkend #PCDATA '}'
    elif re.match(r"\{\\\*\\bkmkend", readedData):
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\{\\\*\\bkmkend\s*", "", readedData, 1)

        readedData = re.sub(r"^[^\}]+", "", readedData, 1)
        
        #odstraneni nepotrebne casti
        readedData = re.sub(r"\}\s*", "", readedData, 1)
    
    else:
        sys.stderr.write("Chyba parseru - Bookmark\n")
        sys.stderr.write(readedData[:128] + "\n")
        sys.exit(errCode["parseErr"])
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(data)
    return retArray

#<pict>
#'{' \pict (<pictdata> | <shpdata>) '}'
def Pict(readedData):
    global errCode
    
    data = {}
    
    data["name"] = "pict"
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\pict\s*", "", readedData, 1)
    
    sys.stderr.write("<pict> neimplementovan!!!\n")
    sys.exit(errCode["notImplemented"])
    
    #<pictdata>
    #if not re.search(r"\{\\\*\\picprop")
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(data)
    return retArray

#<obj>
#('{' \object (<objtype> & <objmod>? & <objclass>? & <objname>? & <objtime>? &
#<objsize>? & <rsltmod>?) <objclsid> ? <objdata> <result> '}' ) | <pubobject>
def Obj(readedData):
    global errCode
    
    data = {}
    
    data["name"] = "obj"
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\object\s*", "", readedData, 1)
    
    sys.stderr.write("<obj> neimplementovan!!!\n")
    sys.exit(errCode["notImplemented"])
    
    #<pictdata>
    #if not re.search(r"\{\\\*\\picprop")
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(data)
    return retArray

#<brdrdef>
#(<brdrseg> <brdr> )+
#TODO: nejak mi to tu nesedi
#moc klicovych a malo z nich se zpracovalo
#@profile
def Brdrdef(readedData):
    global globPara
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Brdrdef()\n")
        sys.stdout.write("Brdrdef()\n")
    
    #nastaveni brdrdef
    brdr = []
    
    brdrkKyes = {"brdrs":"",
                          "brdrth":"",
                          "brdrsh":"",
                          "brdrdb":"",
                          "brdrdot":"",
                          "brdrdash":"",
                          "brdrhair":"",
                          "brdrinset":"",
                          "brdrdashsm":"",
                          "brdrdashd":"",
                          "brdrdashdd":"",
                          "brdrdashdot":"",
                          "brdrdashdotdot":"",
                          "brdrtriple":"",
                          "brdrtnthsg":"",
                          "brdrthtnsg":"",
                          "brdrtnthtnsg":"",
                          "brdrtnthmg":"",
                          "brdrthtnmg":"",
                          "brdrtnthtnmg":"",
                          "brdrtnthlg":"",
                          "brdrthtnlg":"",
                          "brdrtnthtnlg":"",
                          "brdrwavy":"",
                          "brdrwavydb":"",
                          "brdrdashdotstr":"",
                          "brdremboss":"",
                          "brdrengrave":"",
                          "brdroutset":"",
                          "brdrnone":"",
                          "brdrtbl":"",
                          "brdrnil":""
                 }
    
    while re.match(r"\\(brdrt|brdrb|brdrl|brdrr|brdrbtw|brdrbar|box)", readedData):
        global globForBrdrdef
        global errCode
        
        #<brdrseg>
        try:
            brdrseg = re.match(r"\\(brdrt|brdrb|brdrl|brdrr|brdrbtw|brdrbar|box)", readedData).group(1)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <brdrseg>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni nastaveni
        globForBrdrdef["brdrseg"] = brdrseg
        
        #odstraneni nacteneho kl. slova
        readedData = re.sub(r"^\\(brdrt|brdrb|brdrl|brdrr|brdrbtw|brdrbar|box)\s*", "", readedData, 1)
        
        #<brdr>
        #<brdrk>
        try:
            tmpKey = re.match(r"\\([a-zA-Z]+)", readedData).group(1)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <brdrk>!\n")
            sys.stderr.write(readedData[:128] + "\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #kontrola kl. slova
        if brdrkKyes.has_key(tmpKey):
            #ulozeni nastaveni
            globForBrdrdef["brdrk"] = tmpKey
            
            #odstraneni nacteneho kl. slova
            readedData = re.sub(r"^\\[a-zA-Z]+\s*", "", readedData, 1)
        
        else:
            sys.stderr.write("Chyba pri cteni klicoveho slova ze skupiny <brdrk>!\n")
            sys.exit(errCode["parseErr"])
        
        #\brdrwN?
        if re.match(r"\\brdrw", readedData):
            #odstraneni nepotrebne casti
            readedData = re.sub(r"^\\brdrw\s*", "", readedData, 1)
            
            #ziskani hodnoty
            try:
                brdrw = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Nelze nacist keyword z <brdr>!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                sys.exit(errCode["parseErr"])
            
            #ulozeni nastaveni
            globForBrdrdef["brdrw"] = brdrw
            
            #odstraneni pouzite casti
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        #\brspN?
        if re.match(r"\\brsp", readedData):
            #odstraneni nepotrebne casti
            readedData = re.sub(r"^\\brsp\s*", "", readedData, 1)
            
            #ziskani hodnoty
            try:
                brsp = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Nelze nacist keyword z <brdr>!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                sys.exit(errCode["parseErr"])
            
            #ulozeni nastaveni
            globForBrdrdef["brsp"] = brsp
            
            #odstraneni pouzite casti
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        #\brdrcfN?
        if re.match(r"\\brdrcf", readedData):
            #odstraneni nepotrebne casti
            readedData = re.sub(r"^\\brdrcf\s*", "", readedData, 1)
            
            #ziskani hodnoty
            try:
                brdrcf = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Nelze nacist keyword z <brdr>!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                sys.exit(errCode["parseErr"])
            
            #ulozeni nastaveni
            globForBrdrdef["brdrcf"] = brdrcf
            
            #odstraneni pouzite casti
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

"""
#<parfmt>
# @return success - vraci informaci o tom, zda se podarilo nacist kl. slovo ze skupiny <parfmt>
def Parfmt(readedData):
    global globPara
    global globDefpap
    global errCode
    
    sys.stderr.write("Parfmt()\n")
    
    success = True
    
    if re.match(r"\\pard", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\pard\s*", "", readedData, 1)
        
        #resetovani nastaveni odstavcu
        #TODO: doimplementovat
        #InitPard()
        globPara = globDefpap.copy()
    
    elif re.match(r"\\par", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\par\s*", "", readedData, 1)
        
        #ulozeni nastaveni na zasobnik
        #TODO: doimplementovat
        sys.stderr.write("\\par konec <parfmt>")
        sys.exit(0)
        #PushPar()
    
    #pravdepodobne nema vyuziti
    elif re.match(r"\\(spv|hyphpar)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(spv|hyphpar)\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (spv nebo hyphpar) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    #TODO: Odstavec je soucasti tabulky
    elif re.match(r"\\(intbl|itab)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(intbl|(itab\s*(\-)?\d+))\s*", "", readedData, 1)
        
        globPara["Intbl"] = True
        
        #sys.stderr.write("Vyznam klicoveho (intbl nebo itab) slova neimplementovan!\n")
        #sys.exit(errCode["notImplemented"])
    
    elif re.match(r"\\(keep(n)?|level|noline|widctlpar|nowidctlpar|outlinelevel|pagebb|sbys)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(keep(n)?|keepn|(level\s*(\-)?\d+)|noline|widctlpar|nowidctlpar|(outlinelevel\s*(\-)?\d+)|pagebb|sbys)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        #sys.stderr.write("Vyznam klicoveho (keep|keepn|level|noline|widctlpar|nowidctlpar|outlinelevel|pagebb|sbys) slova neimplementovan!\n")
        #sys.exit(errCode["notImplemented"])
    
    elif re.match(r"\\s\s*\d+", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\s\s*", "", readedData, 1)
        
        try:
            s = re.match(r"\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \s z <parfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni nastaveni
        globPara["s"] = s
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^\d+\s*", "", readedData)
    
    #Table Style Specific
    elif re.match(r"\\(yts|tscfirstrow|tsclastrow|tscfirstcol|tsclastcol|tscbandhorzodd|tscbandhorzeven|tscbandvertodd|tscbandverteven|tscnwcell|tscnecell|tscswcell|tscsecell)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\((yts\s*(\-)?\d+)|tscfirstrow|tsclastrow|tscfirstcol|tsclastcol|tscbandhorzodd|tscbandhorzeven|tscbandvertodd|tscbandverteven|tscnwcell|tscnecell|tscswcell|tscsecell)\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (yts|tscfirstrow|tsclastrow|tscfirstcol|tsclastcol|tscbandhorzodd|tscbandhorzeven|tscbandvertodd|tscbandverteven|tscnwcell|tscnecell|tscswcell|tscsecell) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    #Alignment
    elif re.match(r"\\qc", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\qc\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["alignment"] = "qc"
    
    elif re.match(r"\\qj", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\qj\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["alignment"] = "qj"
    
    elif re.match(r"\\ql", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ql\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["alignment"] = "ql"
    
    elif re.match(r"\\qr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\qr\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["alignment"] = "qr"
    
    elif re.match(r"\\(qk|qt)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\((qk\s*(\-)?\d+)|qt)\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (keep|keepn|level|noline|widctlpar|nowidctlpar|outlinelevel|pagebb|sbys) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    #Font alignment
    elif re.match(r"\\faauto", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\faauto\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["faauto"] = ""
    
    elif re.match(r"\\(fahang|facenter|faroman|favar|fafixed)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(fahang|facenter|faroman|favar|fafixed)\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (fahang|facenter|faroman|favar|fafixed) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    #Indentation
    elif re.match(r"\\adjustright", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\adjustright\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["adjustright"] = ""
    
    elif re.match(r"\\li(\-)?\d+", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\li\s*", "", readedData, 1)
        
        try:
            li = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri li!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["li"] = li
    
    elif re.match(r"\\ri(\-)?\d+", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ri\s*", "", readedData, 1)
        
        try:
            ri = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri ri!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["ri"] = ri
    
    elif re.match(r"\\fi(\-)?\d+", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\fi\s*", "", readedData, 1)
        
        try:
            fi = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri fi!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["fi"] = fi
    
    elif re.match(r"\\(cufi|lin|culi|rin|curi|indmirror)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(cufi|lin|culi|rin|curi|indmirror)\s*", "", readedData, 1)
        
        #odstraneni ciselne hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (cufi|lin|culi|rin|curi|indmirror) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    #Spacing
    elif re.match(r"\\sb\s*(\-)?\d+", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sb\s*", "", readedData, 1)
        
        try:
            sb = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \sb z <parfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni nastaveni
        globPara["sb"] = sb
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\sa\s*(\-)?\d+", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sa\s*", "", readedData, 1)
        
        try:
            sa = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \sa z <parfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni nastaveni
        globPara["sa"] = sa
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\sl\s*(\-)?\d+", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sl\s*", "", readedData, 1)
        
        try:
            sl = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \sl z <parfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni nastaveni
        globPara["sl"] = sl
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\slmult\s*(\-)?\d+", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\slmult\s*", "", readedData, 1)
        
        try:
            slmult = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \slmult z <parfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni nastaveni
        globPara["slmult"] = slmult
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\(sbauto|saauto|lisb|lisa)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(sbauto|saauto|lisb|lisa)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        sys.stderr.write("Vyznam klicoveho (sbauto|saauto|lisb|lisa) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    elif re.match(r"\\(nosnaplinegrid|contextualspace)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(nosnaplinegrid|contextualspace)\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (nosnaplinegrid|contextualspace) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    #Subdocuments
    #Revision Tracking
    elif re.match(r"\\(subdocument|prauth|prdate)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(subdocument|prauth|prdate)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        sys.stderr.write("Vyznam klicoveho(subdocument|prauth|prdate) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    #Bidirectional Controls
    elif re.match(r"\\ltrpar", readedData):
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ltrpar\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["ltrpar"] = ""
    
    elif re.match(r"\\rtlpar", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\rtlpar\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["rtlpar"] = ""
    
    #Bidirectional Controls
    elif re.match(r"\\aspalpha", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\aspalpha\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["aspalpha"] = ""
    
    elif re.match(r"\\aspalpha", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\aspalpha\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["aspalpha"] = ""
    
    elif re.match(r"\\aspnum", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\aspnum\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["aspnum"] = ""
    
    elif re.match(r"\\(nocwrap|nowwrap|nooverflow)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(nocwrap|nowwrap|nooverflow)\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (nocwrap|nowwrap|nooverflow) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    #Pocket Word
    #Paragraphs Surrounding Text Box Wrapping
    elif re.match(r"\\(collapsed|txbxtwno|txbxtwalways|txbxtwfirstlast|txbxtwfirst|txbxtwlast)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(collapsed|txbxtwno|txbxtwalways|txbxtwfirstlast|txbxtwfirst|txbxtwlast)\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (collapsed|txbxtwno|txbxtwalways|txbxtwfirstlast|txbxtwfirst|txbxtwlast) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    else:
        success = False
    
    #sys.stderr.write(readedData[:128] + "\n")
    #sys.stderr.write("<parfmt> konec\n")
    #sys.exit(0)
    
    #print globPara
    #print ""
    
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray
"""

#<parfmt>
#@profile
def Parfmt(readedData):
    global globPara
    global globParfmt
    global globDefpap
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Parfmt()\n")
        sys.stdout.write("Parfmt()\n")
    
    success = True
    
    if not re.match(r"\\([a-zA-Z]+)", readedData):
        success = False
        
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    #nacteni klicoveho slova
    try:
        keyword = re.match(r"\\([a-zA-Z]+)", readedData).group(1)
    except AttributeError as e:
        sys.stderr.write(readedData[:128] + "\n")
        sys.stderr.write("Nelze nacist keyword!\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        sys.exit(errCode["parseErr"])
    #readedData = re.sub(r"^[a-zA-Z]+\s*", "", readedData, 1)
    
    sys.stderr.write("Keyword: " + keyword + "\n")
    
    if not globParfmt.has_key(keyword):
        success = False
        
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    if keyword == "pard":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\pard\s*", "", readedData, 1)
        
        #resetovani nastaveni odstavcu
        #TODO: doimplementovat
        #InitPard()
        globPara = globDefpap.copy()
    
    elif keyword == "par":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\par\s*", "", readedData, 1)
        
        #ulozeni nastaveni na zasobnik
        #TODO: doimplementovat
        sys.stderr.write("\\par konec <parfmt>")
        sys.exit(0)
    
    #TODO: presunuto kvuli urychleni
    elif keyword == "li":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\li\s*", "", readedData, 1)
        
        try:
            li = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri li!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["li"] = li
    
    #TODO: presunuto kvuli urychleni
    elif keyword == "qc":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\qc\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["alignment"] = "qc"
    
    elif keyword == "qj":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\qj\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["alignment"] = "qj"
    
    elif keyword == "ql":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ql\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["alignment"] = "ql"
    
    elif keyword == "qr":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\qr\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["alignment"] = "qr"
    
    #TODO: presunuto kvuli urychleni
    elif keyword == "sl":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sl\s*", "", readedData, 1)
        
        try:
            sl = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \sl z <parfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni nastaveni
        globPara["sl"] = sl
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif keyword == "slmult":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\slmult\s*", "", readedData, 1)
        
        try:
            slmult = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \slmult z <parfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni nastaveni
        globPara["slmult"] = slmult
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #pravdepodobne nema vyuziti
    elif keyword == "spv" or keyword == "hyphpar":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(spv|hyphpar)\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (spv nebo hyphpar) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    #TODO: Odstavec je soucasti tabulky
    elif keyword == "intbl" or keyword == "itab":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(intbl|(itab\s*(\-)?\d+))\s*", "", readedData, 1)
        
        globPara["Intbl"] = True
        
        #sys.stderr.write("Vyznam klicoveho (intbl nebo itab) slova neimplementovan!\n")
        #sys.exit(errCode["notImplemented"])
    
    elif keyword == "keep" or keyword == "keepn" or keyword == "level" or keyword == "noline" or keyword == "widctlpar" or keyword == "nowidctlpar" or keyword == "pagebb" or keyword == "outlinelevel" or keyword == "sbys":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(keep(n)?|keepn|(level\s*(\-)?\d+)|noline|widctlpar|nowidctlpar|(outlinelevel\s*(\-)?\d+)|pagebb|sbys)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        #sys.stderr.write("Vyznam klicoveho (keep|keepn|level|noline|widctlpar|nowidctlpar|outlinelevel|pagebb|sbys) slova neimplementovan!\n")
        #sys.exit(errCode["notImplemented"])
    
    elif keyword == "s":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\s\s*", "", readedData, 1)
        
        try:
            s = re.match(r"\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \s z <parfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni nastaveni
        globPara["s"] = s
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^\d+\s*", "", readedData)
    
    #Table Style Specific
    elif keyword == "yts" or keyword == "tscfirstrow" or keyword == "tsclastrow" or keyword == "tscfirstcol" or keyword == "tsclastcol" or keyword == "tscbandhorzodd" or keyword == "tscbandhorzeven" or keyword == "tscbandvertodd" or keyword == "tscbandverteven" or keyword == "tscnwcell" or keyword == "tscnecell" or keyword == "tscswcell" or keyword == "tscsecell":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\((yts\s*(\-)?\d+)|tscfirstrow|tsclastrow|tscfirstcol|tsclastcol|tscbandhorzodd|tscbandhorzeven|tscbandvertodd|tscbandverteven|tscnwcell|tscnecell|tscswcell|tscsecell)\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (yts|tscfirstrow|tsclastrow|tscfirstcol|tsclastcol|tscbandhorzodd|tscbandhorzeven|tscbandvertodd|tscbandverteven|tscnwcell|tscnecell|tscswcell|tscsecell) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    #Alignment
    #TODO: Presunuto kvuli urychleni
    
    elif keyword == "qk" or keyword == "qt":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\((qk\s*(\-)?\d+)|qt)\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (qk|qt) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    #Font alignment
    elif keyword == "faauto":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\faauto\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["faauto"] = ""
    
    elif keyword == "fahang" or keyword == "facenter" or keyword == "faroman" or keyword == "favar" or keyword == "fafixed":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(fahang|facenter|faroman|favar|fafixed)\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (fahang|facenter|faroman|favar|fafixed) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    #Indentation
    elif keyword == "adjustright":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\adjustright\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["adjustright"] = ""
    
    elif keyword == "ri":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ri\s*", "", readedData, 1)
        
        try:
            ri = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri ri!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["ri"] = ri
    
    elif keyword == "fi":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\fi\s*", "", readedData, 1)
        
        try:
            fi = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri fi!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["fi"] = fi
    
    elif keyword == "cufi" or keyword == "lin" or keyword == "culi" or keyword == "rin" or keyword == "curi" or keyword == "indmirror":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(cufi|lin|culi|rin|curi|indmirror)\s*", "", readedData, 1)
        
        #odstraneni ciselne hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (cufi|lin|culi|rin|curi|indmirror) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    #Spacing
    elif keyword == "sb":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sb\s*", "", readedData, 1)
        
        try:
            sb = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \sb z <parfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni nastaveni
        globPara["sb"] = sb
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif keyword == "sa":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sa\s*", "", readedData, 1)
        
        try:
            sa = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \sa z <parfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni nastaveni
        globPara["sa"] = sa
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif keyword == "sbauto" or keyword == "saauto" or keyword == "lisb" or keyword == "lisa":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(sbauto|saauto|lisb|lisa)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        sys.stderr.write("Vyznam klicoveho (sbauto|saauto|lisb|lisa) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    elif keyword == "nosnaplinegrid" or keyword == "contextualspace":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(nosnaplinegrid|contextualspace)\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (nosnaplinegrid|contextualspace) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    #Subdocuments
    #Revision Tracking
    elif keyword == "subdocument" or keyword == "prauth" or keyword == "prdate":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(subdocument|prauth|prdate)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        sys.stderr.write("Vyznam klicoveho(subdocument|prauth|prdate) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    #Bidirectional Controls
    elif keyword == "ltrpar":
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ltrpar\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["ltrpar"] = ""
    
    elif keyword == "rtlpar":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\rtlpar\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["rtlpar"] = ""
    
    #Bidirectional Controls
    elif keyword == "aspalpha":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\aspalpha\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["aspalpha"] = ""
    
    elif keyword == "aspnum":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\aspnum\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globPara["aspnum"] = ""
    
    elif keyword == "nocwrap" or keyword == "nowwrap" or keyword == "nooverflow":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(nocwrap|nowwrap|nooverflow)\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (nocwrap|nowwrap|nooverflow) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    #TODO: vyjimecne zarazeno, patri do <shading>
    elif keyword == "cbpat":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cbpat\s*", "", readedData, 1)
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #Pocket Word
    #Paragraphs Surrounding Text Box Wrapping
    elif keyword == "collapsed" or keyword == "txbxtwno" or keyword == "txbxtwalways" or keyword == "txbxtwfirstlast" or keyword == "txbxtwfirst" or keyword == "txbxtwlast":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(collapsed|txbxtwno|txbxtwalways|txbxtwfirstlast|txbxtwfirst|txbxtwlast)\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (collapsed|txbxtwno|txbxtwalways|txbxtwfirstlast|txbxtwfirst|txbxtwlast) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    else:
        success = False
    
    #sys.stderr.write(readedData[:128] + "\n")
    #sys.stderr.write("<parfmt> konec\n")
    #sys.exit(0)
    
    #print globPara
    #print ""
    
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<framesize>
#\abswN? & \abshN?
#@profile
def Framesize(readedData):
    global globForApoctl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Framesize()\n")
        sys.stdout.write("Framesize()\n")
    
    success = False
    
    if re.match(r"\\absw", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\absw\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            absw = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \absw z <framesize>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globForApoctl["absw"] = absw
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        success = True
    
    if re.match(r"\\absh", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\absh\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            absh = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \absh z <framesize>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globForApoctl["absh"] = absh
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        success = True
    
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<hframe>
#\phmrg? | \phpg? | \phcol?
#@profile
def Hframe(readedData):
    global globForApoctl
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Hframe()\n")
        sys.stdout.write("Hframe()\n")
    
    success = False
    
    if re.match(r"\\phmrg", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\phmrg\s*", "", readedData, 1)
        
        globForApoctl["hframe"] = "phmrg"
        
        success = True
    
    elif re.match(r"\\phpg", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\phpg\s*", "", readedData, 1)
        
        globForApoctl["hframe"] = "phpg"
        
        success = True
    
    elif re.match(r"\\phcol", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\phcol\s*", "", readedData, 1)
        
        globForApoctl["hframe"] = "phcol"
        
        success = True
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<hdist>
#\posxN? | \posnegxN? | \posxc? | \posxi? | \posxo? | \posxl? | \posxr?
#@profile
def Hdist(readedData):
    global globForApoctl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Hdist()\n")
        sys.stdout.write("Hdist()\n")
    
    success = False
    
    if re.match(r"\\posx", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\posx\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            posx = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \posx z <hdist>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globForApoctl["posx"] = posx
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        success = True
    
    elif re.match(r"\\posnegx", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\posnegx\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            posnegx = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \posx z <hdist>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globForApoctl["posnegx"] = posnegx
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        success = True
    
    elif re.match(r"\\(posxc|posxi|posxo|posxl|posxr)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(posxc|posxi|posxo|posxl|posxr)\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (posxc|posxi|posxo|posxl|posxr) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<horzpos>
#<hframe> & <hdist>
#@profile
def Horzpos(readedData):
    global globForApoctl
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Horzpos()\n")
        sys.stdout.write("Horzpos()\n")
    
    success = False
    
    #<hframe>
    retArray = Hframe(readedData)
    readedData = retArray[0]
    success = retArray[1]
    
    if success:
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    #<hdist>
    retArray = Hdist(readedData)
    readedData = retArray[0]
    success = retArray[1]
    
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<vframe>
#\pvmrg? | \pvpg? | \pvpara?
#@profile
def Vframe(readedData):
    global globForApoctl
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Vframe()\n")
        sys.stdout.write("Vframe()\n")
    
    success = False
    
    if re.match(r"\\pvmrg", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\pvmrg\s*", "", readedData, 1)
        
        globForApoctl["vframe"] = "pvmrg"
        
        success = True
    
    elif re.match(r"\\pvpg", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\pvpg\s*", "", readedData, 1)
        
        globForApoctl["vframe"] = "pvpg"
        
        success = True
    
    elif re.match(r"\\pvpara", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\pvpara\s*", "", readedData, 1)
        
        globForApoctl["vframe"] = "pvpara"
        
        success = True
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<vdist>
#\posyN? | \posnegyN? | \posyt? | \posyil? | \posyb? | \posyc? | \posyin? | \posyout? &
#\abslockN?
#@profile
def Vdist(readedData):
    global globForApoctl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Vdist()\n")
        sys.stdout.write("Vdist()\n")
    
    success = False
    
    if re.match(r"\\posy", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\posy\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            posy = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \posy z <vdist>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globForApoctl["posy"] = posy
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        success = True
    
    elif re.match(r"\\posnegy", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\posnegy\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            posnegy = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \posnegy z <vdist>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globForApoctl["posnegy"] = posnegy
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        success = True
    
    elif re.match(r"\\(posyt|posyil|posyb|posyc|posyin|posyout)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(posyt|posyil|posyb|posyc|posyin|posyout)\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (posyt|posyil|posyb|posyc|posyin|posyout) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    elif re.match(r"\\abslock", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\abslock\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        sys.stderr.write("Vyznam klicoveho abslock slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<vertpos>
#<vframe> & <vdist>
#@profile
def Vertpos(readedData):
    global globForApoctl
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Vertpos()\n")
        sys.stdout.write("Vertpos()\n")
    
    success = False
    
    #<vframe>
    retArray = Vframe(readedData)
    readedData = retArray[0]
    success = retArray[1]
    
    if success:
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    #<vdist>
    retArray = Vdist(readedData)
    readedData = retArray[0]
    success = retArray[1]
    
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<wrap>
#\wrapdefault? | \wraparound? | \wraptight? | \wrapthrough?
#@profile
def Wrap(readedData):
    global globForApoctl
    global errCode
    global globParaList
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Wrap()\n")
        sys.stdout.write("Wrap()\n")
    
    success = True
    
    if re.match(r"\\wrapdefault", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\wrapdefault\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globForApoctl["wrap"] = "wrapdefault"
    
    elif re.match(r"\\wraparound", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\wraparound\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globForApoctl["wrap"] = "wraparound"
    
    elif re.match(r"\\wraptight", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\wraptight\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globForApoctl["wrap"] = "wraptight"
    
    elif re.match(r"\\wrapthrough", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\wrapthrough\s*", "", readedData, 1)
        
        #ulozeni nastaveni
        globForApoctl["wrap"] = "wrapthrough"
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<txtwrap>
#\nowrap? & \dxfrtextN? & \dfrmtxtxN? & \dfrmtxtyN? & <wrap>?
#@profile
def Txtwrap(readedData):
    global globForApoctl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Txtwrap()\n")
        sys.stdout.write("Txtwrap()\n")
    
    success = False
    
    if re.match(r"\\nowrap", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\nowrap\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho nowrap slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
        
        success = True
    
    if re.match(r"\\(dxfrtext|dfrmtxtx|dfrmtxty)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(dxfrtext|dfrmtxtx|dfrmtxty)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        sys.stderr.write("Vyznam klicoveho (dxfrtext|dfrmtxtx|dfrmtxty) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
        
        success = True
    
    retArray = Wrap(readedData)
    readedData = retArray[0]
    success = retArray[1]
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<dropcap>
#\dropcapli? & \dropcapt?
#@profile
def Dropcap(readedData):
    global globForApoctl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Dropcap()\n")
        sys.stdout.write("Dropcap()\n")
    
    success = False
    
    if re.match(r"\\(dropcapli|dropcapt)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(dropcapli|dropcapt)\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (dropcapli|dropcapt) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
        
        success = True
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<txtflow>
#\frmtxlrtb | \frmtxtbrl | \frmtxbtlr | \frmtxlrtbv | \frmtxtbrlv
#@profile
def Txtflow(readedData):
    global globForApoctl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Txtflow()\n")
        sys.stdout.write("Txtflow()\n")
    
    success = False
    
    #TODO: Nepokladam za dulezite, zatim vynechavam.
    if re.match(r"\\(frmtxlrtb|frmtxtbrl|frmtxbtlr|frmtxlrtbv|frmtxtbrlv)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(frmtxlrtb|frmtxtbrl|frmtxbtlr|frmtxlrtbv|frmtxtbrlv)\s*", "", readedData, 1)
        
        #sys.stderr.write("Vyznam klicoveho (frmtxlrtb|frmtxtbrl|frmtxbtlr|frmtxlrtbv|frmtxtbrlv) slova neimplementovan!\n")
        #sys.exit(errCode["notImplemented"])
        
        success = True
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<apoctl>
#<framesize> & <horzpos> & <vertpos> & <txtwrap> & <dropcap> & <txtflow> &
#\absnoovrlpN?
# @return success - vraci informaci o tom, zda se podarilo nacist kl. slovo ze skupiny <apoctl>
#@profile
def Apoctl(readedData):
    global globForApoctl
    global globApoctl
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Apoctl()\n")
        sys.stdout.write("Apoctl()\n")
    
    success = True
    
    if not re.match(r"\\([a-zA-Z]+)", readedData):
        success = False
        
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    #nacteni klicoveho slova
    try:
        keyword = re.match(r"\\([a-zA-Z]+)", readedData).group(1)
    except AttributeError as e:
        sys.stderr.write(readedData[:128] + "\n")
        sys.stderr.write("Nelze nacist keyword!\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        sys.exit(errCode["parseErr"])
    #readedData = re.sub(r"^[a-zA-Z]+\s*", "", readedData, 1)
    
    sys.stderr.write("Keyword: " + keyword + "\n")
    
    if not globApoctl.has_key(keyword):
        success = False
        
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    if re.match(r"\\overlay", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\overlay\s*", "", readedData, 1)
        
        #sys.stderr.write("Vyznam klicoveho overlay slova neimplementovan!\n")
        #sys.exit(errCode["notImplemented"])
        
        success = True
        
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    #<framesize>
    retArray = Framesize(readedData)
    readedData = retArray[0]
    success = retArray[1]
    if success:
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    #<horzpos>
    retArray = Horzpos(readedData)
    readedData = retArray[0]
    success = retArray[1]
    if success:
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    #<vertpos>
    retArray = Vertpos(readedData)
    readedData = retArray[0]
    success = retArray[1]
    if success:
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    #<txtwrap>
    retArray = Txtwrap(readedData)
    readedData = retArray[0]
    success = retArray[1]
    if success:
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    #<dropcap>
    retArray = Dropcap(readedData)
    readedData = retArray[0]
    success = retArray[1]
    if success:
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    #<txtflow>
    retArray = Txtflow(readedData)
    readedData = retArray[0]
    success = retArray[1]
    if success:
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    if re.match(r"\\absnoovrlp", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\absnoovrlp\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        sys.stderr.write("Vyznam klicoveho absnoovrlp slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
        
        success = True
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<tabkind>
#\tqr | \tqc | \tqdec
#@profile
def Tabkind(readedData):
    global globForTabdef
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Tabkind()\n")
        sys.stdout.write("Tabkind()\n")
    
    #Nepokladam za dulezite, zatim pouze mazu
    if re.match(r"\\(tqr|tqc|tqdec)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(tqr|tqc|tqdec)\s*", "", readedData, 1)
        
        #sys.stderr.write("Vyznam klicoveho (tqr|tqc|tqdec) slova neimplementovan!\n")
        #sys.exit(errCode["notImplemented"])
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<tablead>
#\tldot | \tlmdot | \tlhyph | \tlul | \tlth | \tleq
#@profile
def Tablead(readedData):
    global globForTabdef
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Tablead()\n")
        sys.stdout.write("Tablead()\n")
    
    #TODO: Moc tomu nerozumim, vynechavam
    if re.match(r"\\(tldot|tlmdot|tlhyph|tlul|tlth|tleq)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(tldot|tlmdot|tlhyph|tlul|tlth|tleq)\s*", "", readedData, 1)
        
        #sys.stderr.write("Vyznam klicoveho (tldot|tlmdot|tlhyph|tlul|tlth|tleq) slova neimplementovan!\n")
        #sys.exit(errCode["notImplemented"])
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<tab>
#<tabkind>? <tablead>? \txN
#@profile
def Tab(readedData):
    global globForTabdef
    global errCode
    global globRawText
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Tab()\n")
        sys.stdout.write("Tab()\n")
    
    success = False
    
    #<tabkind>
    retArray = Tabkind(readedData)
    readedData =retArray[0]
    
    #<tablead>
    retArray = Tablead(readedData)
    readedData = retArray[0]
    
    #print globRawText
    
    if re.match(r"\\tx", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tx\s*", "", readedData, 1)
        
        try:
            tx = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri tx!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globForTabdef["tx"] = tx
        
        success = True
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<bartab>
#<tablead>? \tbN
#@profile
def Bartab(readedData):
    global globForTabdef
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Bartab()\n")
        sys.stdout.write("Bartab()\n")
    
    success = False
    
    #<tablead>
    retArray = Tablead(readedData)
    readedData = retArray[0]
    
    if re.match(r"\\tb", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tb\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        sys.stderr.write("Vyznam klicoveho tb slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
        
        success = True
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<tabdef>
#(<tab> | <bartab>)+
#@profile
def Tabdef(readedData):
    global globForTabdef
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Tabdef()\n")
        sys.stdout.write("Tabdef()\n")
    
    hit = True
    while hit:
        retArray = Tab(readedData)
        readedData = retArray[0]
        hit = retArray[1]
        
        if hit:
            continue
        
        retArray = Bartab(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<shading>
#(\shadingN | <pat>) \cfpatN? \cbpatN?
#@profile
def Shading(readedData):
    global globForShading
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Shading()\n")
        sys.stdout.write("Shading()\n")
    
    #TODO: Shading ma definici shadingN!!!
    if re.match(r"\\(shading|bghoriz|bgvert|bgfdiag|bgbdiag|bgcross|bgdcross|bgdkhoriz|bgdkvert|bgdkfdiag|bgdkbdiag|bgdkcross|bgdkdcross)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(shading|bghoriz|bgvert|bgfdiag|bgbdiag|bgcross|bgdcross|bgdkhoriz|bgdkvert|bgdkfdiag|bgdkbdiag|bgdkcross|bgdkdcross)\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho (shading|bghoriz|bgvert|bgfdiag|bgbdiag|bgcross|bgdcross|bgdkhoriz|bgdkvert|bgdkfdiag|bgdkbdiag|bgdkcross|bgdkdcross) slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    if re.match(r"\\cfpat", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cfpat\s*", "", readedData, 1)
        
        try:
            cfpat = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri cfpat!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globForShading["cfpat"] = cfpat
    
    if re.match(r"\\cbpat", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cbpat\s*", "", readedData, 1)
        
        try:
            cbpat = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri cbpat!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globForShading["cbpat"] = cbpat
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

"""
#<chrfmt>
def Chrfmt(readedData):
    #global globPara
    global globChr
    global globDefchp
    global errCode
    
    sys.stderr.write("Chrfmt()\n")
    sys.stderr.write(readedData[:64] + "\n")
    success = True
    
    if re.match(r"\\plain", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\plain\s*", "", readedData, 1)
        
        globChr = globDefchp.copy()
        
        #print globChr
        #sys.stderr.write("Vyznam klicoveho plain slova neimplementovan!\n")
        #sys.exit(errCode["notImplemented"])
    
    elif re.match(r"\\animtext", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\animtext\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\(accnone|accdot|acccomma|acccircle|accunderdot)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(accnone|accdot|acccomma|acccircle|accunderdot)\s*", "", readedData, 1)
    
    elif re.match(r"\\b0?(\s+|\\)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\b\s*", "", readedData, 1)
        
        if re.match(r"0", readedData):
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
            
            #ulozeni hodnoty
            globChr["b"] = False
        else:
            #ulozeni hodnoty
            globChr["b"] = True
    
    elif re.match(r"\\caps", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\caps\s*", "", readedData, 1)
        
        if re.match(r"0", readedData):
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
            
            #ulozeni hodnoty
            globChr["caps"] = False
        else:
            #ulozeni hodnoty
            globChr["caps"] = True
    
    elif re.match(r"\\cb", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cb\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\cchs", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cchs\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        #TODO: Doimplementovat
        sys.stderr.write("Vyznam klicoveho cchs slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    elif re.match(r"\\cf", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cf\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    #TODO: Podle specifikace by za kl. slovem nemela nasledovat hodnota, ale nasleduje, mozna chyba ve specifikaci
    elif re.match(r"\\charscalex", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\charscalex\s*", "", readedData, 1)
        
        try:
            charscalex = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri charscalex!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["charscalex"] = charscalex
    
    elif re.match(r"\\cs", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cs\s*", "", readedData, 1)
        
        try:
            cs = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri cs!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["cs"] = cs
    
    elif re.match(r"\\cgrid", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cgrid\s*", "", readedData, 1)
        
        if re.match(r"(\-)?\d+", readedData):
            try:
                cgrid = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Chyba pri cgrid!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
            
            globChr["cgrid"] = cgrid
        
        else:
            globChr["cgrid"] = ""
    
    elif re.match(r"\\g(\s*(\\|(\-)?\d+))", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\g\s*", "", readedData, 1)
    
    elif re.match(r"\\(gcw|gridtbl|dn|embo|expnd(tw)?|fittext)", readedData):
        #sys.stderr.write(readedData[:128] + "\n")
        #sys.exit(0)
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(gcw|gridtbl|dn|embo|expnd(tw)?|fittext)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\ls(\s*(\\|(\-)?\d+))", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ls\s*", "", readedData, 1)
        
        try:
            ls = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri ls!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["ls"] = ls
    
    elif re.match(r"\\ilvl(\s*(\\|(\-)?\d+))", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ilvl\s*", "", readedData, 1)
        
        try:
            ilvl = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri ilvl!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["ilvl"] = ilvl
    
    elif re.match(r"\\f(\s*(\\|(\-)?\d+))", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\f\s*", "", readedData, 1)
        
        try:
            f = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri f!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["f"] = f
    
    elif re.match(r"\\fs(\s*(\\|(\-)?\d+))", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\fs\s*", "", readedData, 1)
        
        try:
            fs = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri fs!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["fs"] = fs
    
    elif re.match(r"\\afs(\s*(\\|(\-)?\d+))", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\afs\s*", "", readedData, 1)
        
        try:
            afs = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri afs!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["afs"] = afs
    
    elif re.match(r"\\i0?(\s+|\\)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\i\s*", "", readedData, 1)
        
        if re.match(r"0", readedData):
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
            
            #ulozeni hodnoty
            globChr["i"] = False
        else:
            #ulozeni hodnoty
            globChr["i"] = True
    
    elif re.match(r"\\(impr|kerning|langfe|langfenp|lang|langnp|ltrch|noproof|nosupersub|nosectexpand|rtlch|outl|scaps)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(impr|kerning|langfe|langfenp|lang|langnp|ltrch|noproof|nosupersub|nosectexpand|rtlch|outl|scaps)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\(shad|strike|striked1|sub|super)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(shad|strike|striked1|sub|super)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\ul0?(\s+|\\)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ul\s*", "", readedData, 1)
        
        if re.match(r"0", readedData):
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
            
            #ulozeni hodnoty
            globChr["ul"] = False
        else:
            #ulozeni hodnoty
            globChr["ul"] = True
    
    elif re.match(r"\\(ulc|uld|uldash|uldashd|uldashdd|uldb|ulhwave|ulldash|ulnone|ulth|ulthd|ulthdash|ulthdashd|ulthdashdd|ulthldash|ululdbwave|ulw|ulwave|up|webhidden|v0?(\s+|\\))", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(ulc|uld|uldash|uldashd|uldashdd|uldb|ulhwave|ulldash|ulnone|ulth|ulthd|ulthdash|ulthdashd|ulthdashdd|ulthldash|ululdbwave|ulw|ulwave|up|webhidden|v)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    else:
        success = False
    
    #sys.stderr.write(readedData[:128] + "\n")
    #sys.stderr.write("<chrfmt> konec\n")
    #sys.exit(0)
    
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray
"""

#<chrfmt>
#@profile
def Chrfmt(readedData):
    #global globPara
    global globChr
    global globChrfmt
    global globDefchp
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Chrfmt()\n")
        sys.stdout.write("Chrfmt()\n")
    
    #sys.stderr.write(readedData[:64] + "\n")
    success = True
    
    if not re.match(r"\\([a-zA-Z]+)", readedData):
        success = False
        
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    #nacteni klicoveho slova
    try:
        keyword = re.match(r"\\([a-zA-Z]+)", readedData).group(1)
    except AttributeError as e:
        sys.stderr.write(readedData[:128] + "\n")
        sys.stderr.write("Nelze nacist keyword!\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        sys.exit(errCode["parseErr"])
    #readedData = re.sub(r"^[a-zA-Z]+\s*", "", readedData, 1)
    
    sys.stderr.write("Keyword: " + keyword + "\n")
    
    if not globChrfmt.has_key(keyword):
        success = False
        
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    if keyword == "plain":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\plain\s*", "", readedData, 1)
        
        globChr = globDefchp.copy()
        
        #print globChr
        #sys.stderr.write("Vyznam klicoveho plain slova neimplementovan!\n")
        #sys.exit(errCode["notImplemented"])
    
    #TODO: Presunuto kvuli urychleni
    elif keyword == "cs":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cs\s*", "", readedData, 1)
        
        try:
            cs = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri cs!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["cs"] = cs
    
    #TODO: Presunuto kvuli urychleni
    elif keyword == "b":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\b\s*", "", readedData, 1)
        
        if re.match(r"0", readedData):
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
            
            #ulozeni hodnoty
            globChr["b"] = False
        else:
            #ulozeni hodnoty
            globChr["b"] = True
    
    #TODO: Presunuto kvuli urychleni
    elif keyword == "f":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\f\s*", "", readedData, 1)
        
        try:
            f = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri f!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["f"] = f
    
    elif keyword == "fs":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\fs\s*", "", readedData, 1)
        
        try:
            fs = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri fs!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["fs"] = fs
    
    elif keyword == "afs":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\afs\s*", "", readedData, 1)
        
        try:
            afs = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri afs!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["afs"] = afs
    
    elif keyword == "i":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\i\s*", "", readedData, 1)
        
        if re.match(r"0", readedData):
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
            
            #ulozeni hodnoty
            globChr["i"] = False
        else:
            #ulozeni hodnoty
            globChr["i"] = True
    
    elif keyword == "ul":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ul\s*", "", readedData, 1)
        
        if re.match(r"0", readedData):
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
            
            #ulozeni hodnoty
            globChr["ul"] = False
        else:
            #ulozeni hodnoty
            globChr["ul"] = True
    
    #TODO: Podle specifikace by za kl. slovem nemela nasledovat hodnota, ale nasleduje, mozna chyba ve specifikaci
    #TODO: Presunuto kvuli urychleni
    elif keyword == "charscalex":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\charscalex\s*", "", readedData, 1)
        
        try:
            charscalex = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri charscalex!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["charscalex"] = charscalex
    
    else:
        readedData = re.sub(r"^\\([a-zA-Z]+)((\-)?\d+)?\s*", "", readedData, 1)
    
    """
    elif keyword == "impr" or keyword == "kerning" or keyword == "langfe" or keyword == "langfenp" or keyword == "lang" or keyword == "langnp" or keyword == "ltrch" or keyword == "noproof" or keyword == "nosupersub" or keyword == "nosectexpand" or keyword == "rtlch" or keyword == "outl" or keyword == "scaps":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(impr|kerning|langfe|langfenp|lang|langnp|ltrch|noproof|nosupersub|nosectexpand|rtlch|outl|scaps)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    #TODO: Presunuto kvuli urychleni
    elif keyword == "shad" or keyword == "strike" or keyword == "striked1" or keyword == "sub" or keyword == "super":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(shad|strike|striked1|sub|super)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    #TODO: Presunuto kvuli urychleni
    elif keyword == "gcw" or keyword == "gridtbl" or keyword == "dn" or keyword == "embo" or keyword == "expnd" or keyword == "expndtw" or keyword == "fittext":
        #sys.stderr.write(readedData[:128] + "\n")
        #sys.exit(0)
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(gcw|gridtbl|dn|embo|expnd(tw)?|fittext)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif keyword == "cf":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cf\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif keyword == "animtext":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\animtext\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif keyword == "accnone" or keyword == "accdot" or keyword == "acccomma" or keyword == "acccircle" or keyword == "accunderdot":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(accnone|accdot|acccomma|acccircle|accunderdot)\s*", "", readedData, 1)
    
    elif keyword == "caps":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\caps\s*", "", readedData, 1)
        
        if re.match(r"0", readedData):
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
            
            #ulozeni hodnoty
            globChr["caps"] = False
        else:
            #ulozeni hodnoty
            globChr["caps"] = True
    
    elif keyword == "cb":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cb\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif keyword == "cchs":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cchs\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        #TODO: Doimplementovat
        sys.stderr.write("Vyznam klicoveho cchs slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    elif keyword == "cgrid":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cgrid\s*", "", readedData, 1)
        
        if re.match(r"(\-)?\d+", readedData):
            try:
                cgrid = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Chyba pri cgrid!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
            
            globChr["cgrid"] = cgrid
        
        else:
            globChr["cgrid"] = ""
    
    elif keyword == "g":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\g\s*", "", readedData, 1)
    
    elif keyword == "ls":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ls\s*", "", readedData, 1)
        
        try:
            ls = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri ls!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["ls"] = ls
    
    elif keyword == "ilvl":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ilvl\s*", "", readedData, 1)
        
        try:
            ilvl = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri ilvl!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globChr["ilvl"] = ilvl
    
    elif keyword == "ulc" or keyword == "uld" or keyword == "uldash" or keyword == "uldashd" or keyword == "uldashdd" or keyword == "uldb" or keyword == "ulhwave" or keyword == "ulldash" or keyword == "ulnone" or keyword == "ulth" or keyword == "ulthd" or keyword == "ulthdash" or keyword == "ulthdashd" or keyword == "ulthdashdd" or keyword == "ulthldash" or keyword == "ululdbwave" or keyword == "ulw" or keyword == "ulwave" or keyword == "up" or keyword == "webhidden" or keyword == "v":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(ulc|uld|uldash|uldashd|uldashdd|uldb|ulhwave|ulldash|ulnone|ulth|ulthd|ulthdash|ulthdashd|ulthdashdd|ulthldash|ululdbwave|ulw|ulwave|up|webhidden|v)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    else:
        success = False
    """
    #sys.stderr.write(readedData[:128] + "\n")
    #sys.stderr.write("<chrfmt> konec\n")
    #sys.exit(0)
    
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<chshading>
#(\chshdngN | <pat>) \chcfpatN? \chcbpatN?
#@profile
def Chshading(readedData):
    global globChr
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Chshading()\n")
        sys.stdout.write("Chshading()\n")
    
    success = False
    
    if re.match(r"\\chshdng", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\chshdng\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        success = True
    
    #<pat>
    elif re.match(r"\\(chbghoriz|chbgvert|chbgfdiag|chbgbdiag|chbgcross|chbgdcross|chbgdkhoriz|chbgdkvert|chbgdkfdiag|chbgdkbdiag|chbgdkcross|chbgdkdcross)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(chbghoriz|chbgvert|chbgfdiag|chbgbdiag|chbgcross|chbgdcross|chbgdkhoriz|chbgdkvert|chbgdkfdiag|chbgdkbdiag|chbgdkcross|chbgdkdcross)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        success = True
    
    if re.match(r"\\(chcfpat|chcbpat)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\chshdng\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        success = True
    
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<chrev>
#\revised? \revauthN? \revdttmN? \crauthN? \crdateN? \deleted? \revauthdelN?
#\revdttmdelN? \mvf? \mvt? \mvauthN? \mvdateN?
#@profile
def Chrev(readedData):
    global globChr
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Chrev()\n")
        sys.stdout.write("Chrev()\n")
    
    success = False
    
    if re.match(r"\\(revised|revauth|revdttm|crauth|crdate|deleted|revauthdel|revdttmdel|mvf|mvt|mvauth|mvdate)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(revised|revauth|revdttm|crauth|crdate|deleted|revauthdel|revdttmdel|mvf|mvt|mvauth|mvdate)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        success = True
    
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<ptext>
#((<chrfmt> | <chshading> | <chrev>)* <data>+ )+
#TODO: Pro me z neznameho duvodu se mezi <chrfmt> a <data> jeste vklada <parfmt>. Podle specifikace <ptext> to neni pripustne, ale samotna specifikace ukazuje priklady s touto moznosti.
#Pokud to rozlousku, prepracuji, zatim davam do <ptext> zpracovani i <parfmt>
#TODO: Tak stejno <apoctl>
#@profile
def Ptext(readedData):
    global globPara
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Ptext()\n")
        sys.stdout.write("Ptext()\n")
    
    successPtext = False
    
    #Vsechno se muze opakovat
    successAll = True
    while successAll:
        #pouze <data> jsou nutna, takze pokud se vyskytnou, pak se successAll zmeni na true
        # a cely Ptext() je true.
        successAll = False
        #<chrfmt>, <chshading>, <chrev> se mohou opakovat
        successCCC = True
        while successCCC:
            #Prepnuti successCCC na false, protoze ze z zadne tridy kl. slovo vyskytovat nemusi
            # a tak zalezi na kl. slovech, jestli nektere z nich zase nastavi successCCC na true
            successCCC = False
            
            #<chrfmt>
            successChrfmt = True
            while successChrfmt:
                retArray = Chrfmt(readedData)
                readedData = retArray[0]
                successChrfmt = retArray[1]
                
                if successChrfmt:
                    successCCC = True
                    #TODO: Pouze zkusebne menim tvrzeni syntaxu <ptext> z ((<chrfmt> | <chshading> | <chrev>)* <data>+ )+ na ((<chrfmt> | <chshading> | <chrev>)* <data>* )+
                    #Pri zpracovani tabulky se totiz nasla situace, kdy (<chrfmt> | <chshading> | <chrev>)* existovalo, ale <data> tam nebyla. Pokud to nebude fungovat, zkusit presunout <chrfmt>* i do <textpar>
                    successPtext = True
            
            #<chshading>
            successChshading = True
            while successChshading:
                retArray = Chshading(readedData)
                readedData = retArray[0]
                successChshading = retArray[1]
                
                if successChshading:
                    successCCC = True
                    successPtext = True
            
            #<chrev>
            successChrev = True
            while successChrev:
                retArray = Chrev(readedData)
                readedData = retArray[0]
                successChrev = retArray[1]
                
                if successChrev:
                    successCCC = True
                    successPtext = True
        
        #<data>+
        successData = True
        while successData:
            retArray = Data(readedData)
            readedData = retArray[0]
            data = retArray[1]
            successData = retArray[2]
            
            if successData:
                successAll = True
                successPtext = True
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(successPtext)
    return retArray

"""
def Ptext(readedData):
    global globPara
    global errCode
    
    sys.stderr.write("Ptext()\n")
    
    successData = True
    successChrfmt = True
    successChshading = True
    successChrev = True
    successParfmt = True
    successAll = False
    successDataAll = False
    
    while successData:
        #(<chrfmt> | <chshading> | <chrev>)*
        successCCC = True
        while successCCC: 
            successCCC = False
            #<chrfmt>
            successChrfmt = True
            while successChrfmt:
                retArray = Chrfmt(readedData)
                readedData = retArray[0]
                successChrfmt = retArray[1]
                
                if successChrfmt:
                    successCCC = True
                    successAll = True
            
            #<chshading>
            successChshading = True
            while successChshading:
                retArray = Chshading(readedData)
                readedData = retArray[0]
                successChshading = retArray[1]
                
                if successChshading:
                    successCCC = True
                    successAll = True
            
            #<chrev>
            successChrev = True
            while successChrev:
                retArray = Chrev(readedData)
                readedData = retArray[0]
                successChrev = retArray[1]
                
                if successChrev:
                    successCCC = True
                    successAll = True
        
        if successAll:
            successAll = False
            #<data>+
            successData = True
            while successData:
                retArray = Data(readedData)
                readedData = retArray[0]
                data = retArray[1]
                successData = retArray[2]
                
                if successData:
                    successDataAll = True
                
                #TODO: Zatim se mi to <data>+ nelibi, nastavuju docasne na <data>
                #break
        
        #sys.stderr.write("Zarazka pro upravu <data>\n")
        #sys.exit(errCode["notImplemented"])
        #break
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(successDataAll)
    return retArray
"""

#<aprops>
#@profile
def Aprops(readedData):
    global globChr
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Aprops()\n")
        sys.stdout.write("Aprops()\n")
    
    success = True
    
    if re.match(r"\\ab0?(\s+|\\)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ab\s*", "", readedData, 1)
        
        if re.match(r"0", readedData):
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
            
            #ulozeni hodnoty
            globChr["ab"] = False
        else:
            #ulozeni hodnoty
            globChr["ab"] = True
    
    elif re.match(r"\\acaps0?(\s+|\\)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\acaps\s*", "", readedData, 1)
        
        if re.match(r"0", readedData):
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
            
            #ulozeni hodnoty
            globChr["acaps"] = False
        else:
            #ulozeni hodnoty
            globChr["acaps"] = True
    
    elif re.match(r"\\(acf\s*(\-)?\d+|adn\s*(\-)?\d+|aexpnd)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(acf|adn|aexpnd)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.search(r"\\af(\s+|\\)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\af\s*", "", readedData, 1)
        
        try:
            af = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri af!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        globChr["af"] = af
    
    elif re.search(r"\\afs(\s+|\\)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\afs\s*", "", readedData, 1)
        
        try:
            afs = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri afs!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        globChr["afs"] = afs
    
    elif re.match(r"\\ai0?(\s+|\\)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ai\s*", "", readedData, 1)
        
        if re.match(r"0", readedData):
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
            
            #ulozeni hodnoty
            globChr["ai"] = False
        else:
            #ulozeni hodnoty
            globChr["ai"] = True
    
    elif re.match(r"\\(alang|aoutl)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(alang|aoutl)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\ascaps0?(\s+|\\)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ascaps\s*", "", readedData, 1)
        
        if re.match(r"0", readedData):
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
            
            #ulozeni hodnoty
            globChr["ascaps"] = False
        else:
            #ulozeni hodnoty
            globChr["ascaps"] = True
    
    elif re.match(r"\\(ashad|astrike)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(ashad|astrike)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\aul0?(\s+|\\)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\aul\s*", "", readedData, 1)
        
        if re.match(r"0", readedData):
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
            
            #ulozeni hodnoty
            globChr["aul"] = False
        else:
            #ulozeni hodnoty
            globChr["aul"] = True
    
    elif re.match(r"\\(auld|auldb|aulnone|aulw|aup(\-)?\d+|fcs(\-)?\d+|loch|hich|dbch)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(auld|auldb|aulnone|aulw|aup|fcs|loch|hich|dbch)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<atext>
#<ltrrun> | <rtlrun> | <sarun> | <nonsarun> | <saltrrun> | <nonsaltrrun> |
#<nonsartlrun> | <losbrun> | <hisbrun> | <dbrun>
#@profile
def Atext(readedData):
    global globPara
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Atext()\n")
        sys.stdout.write("Atext()\n")
    
    success = True
    
    #<ltrrun> \rtlch \afN & <aprops>* \ltrch <ptext>
    #<rtlrun> \ltrch \afN & <aprops>* \rtlch <ptext>
    #<sarun> \fcs0 \afN & <aprops>* \fcs1 <ptext>
    #<nonsarun> \fcs1 \afN & <aprops>* \fcs0 <ptext>
    #<saltrrun> \rtlch \fcs0 \af & <aprops>* \ltrch \fcs1 <ptext>
    #<nonsaltrrun> \rtlch \fcs1 \af & <aprops>* \ltrch \fcs0 <ptext>
    #<nonsartlrun> \ltrch \fcs1 \af & <aprops>* \rtlch \fcs0 <ptext>
    if re.match(r"\\(rtlch|ltrch|fcs0|fcs1)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(rtlch|ltrch|fcs0|fcs1)\s*", "", readedData, 1)
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(fcs0|fcs1)\s*", "", readedData, 1)
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\\af\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #<aprops>*
        hit = True
        while hit:
            retArray = Aprops(readedData)
            readedData = retArray[0]
            hit = retArray[1]
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\\af\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(rtlch|ltrch|fcs0|fcs1)\s*", "", readedData, 1)
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(fcs0|fcs1)\s*", "", readedData, 1)
        
        retArray = Ptext(readedData)
        readedData = retArray[0]
    
    #<losbrun> \hich \afN & <aprops> \dbch \afN & <aprops> \loch <ptext>
    #<hisbrun> \loch \afN & <aprops> \dbch \afN & <aprops> \hich <ptext>
    #<dbrun> \loch \afN & <aprops> \hich \afN & <aprops> \dbch <ptext>
    elif re.match(r"\\(hich|loch)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(hich|loch)\s*", "", readedData, 1)
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\\af\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        retArray = Aprops(readedData)
        readedData = retArray[0]
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\\af\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(dbch|hich)\s*", "", readedData, 1)
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\\af\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        retArray = Aprops(readedData)
        readedData = retArray[0]
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\\af\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(dbch|hich|loch)\s*", "", readedData, 1)
        
        retArray = Ptext(readedData)
        readedData = retArray[0]
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<char>
#<ptext> | <atext> | '{' <char> '}'
#@profile
def Char(readedData):
    global globPara
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Char()\n")
        sys.stdout.write("Char()\n")
    
    successAll = False
    
    if re.match(r"(\{)\\trowd", readedData):
        successAll = False
        #sys.stderr.write("Parser se dostal do spatneho mista\n")
        #sys.exit(errCode["parseErr"])
    
    elif not re.match(r"\{", readedData) or re.match(r"\{\\\*", readedData) or re.match(r"\{\\field", readedData) or re.match(r"\{\\listtext", readedData) or re.match(r"\{\\shp", readedData):
        #<ptext>
        retArray = Ptext(readedData)
        readedData = retArray[0]
        success = retArray[1]
        
        if success:
            successAll = True
        
        #<atext>
        retArray = Atext(readedData)
        readedData = retArray[0]
        success = retArray[1]
        
        if success:
            successAll = True
        
    else:
        #TODO: ten if je tu mozna zbytecne
        if not re.match(r"\{\\\*", readedData):
            sys.stderr.write("Prechazi na Char() {}\n")
            #odstraneni nepotrebne casti
            readedData = re.sub(r"^\{\s*", "", readedData, 1)
            
            #ulozeni nastaveni na zasobnik
            PushToStack()
            
            #<char>
            retArray = Char(readedData)
            readedData = retArray[0]
            success = True
            
            #odstraneni nepotrebne casti
            readedData = re.sub(r"^\}\s*", "", readedData, 1)
            
            if success:
                successAll = True
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(successAll)
    return retArray

#<textpar>
#<pn>? <brdrdef>? <parfmt>* <apoctl>* <tabdef>? <shading>? (\v \spv)?
#(\subdocumentN | <char>+) (\par <para>)?
#@profile
def Textpar(readedData):
    global globPara
    global globChr
    global globDefchp
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Textpar()\n")
    
    #sys.stderr.write(readedData[:128] + "\n")
    #sys.stderr.write("<Textpar> konec\n")
    #sys.stderr.write("Pokracovat...\n")
    #a=raw_input()
    
    success = False
    
    #<pn>?
    if re.match(r"\{(\\\*\\pnseclvl)|(\\pntext)", readedData):
        sys.stderr.write("<pn> neimplementovan!!!\n")
        sys.exit(errCode["notImplemented"])
    
    #<brdrdef>?
    if re.match(r"\\(brdrt|brdrb|brdrl|brdrr|brdrbtw|brdrbar|box)", readedData):
        retArray = Brdrdef(readedData)
        readedData = retArray[0]
    
    #<parfmt>*
    hit = True
    while hit:
        retArray = Parfmt(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #TODO: Primo ve specifikaci to neni, ale priklady poukazuji na to, ze tahle situace muze nastat a taky nastava
    if re.match(r"\\plain", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\plain\s*", "", readedData, 1)
        
        globChr = globDefchp.copy()
        
        #print globChr
        #sys.stderr.write("Vyznam klicoveho plain slova neimplementovan!\n")
        #sys.exit(errCode["notImplemented"])
    
    hitAll = True
    while hitAll:
        hitAll = False
        
        #<parfmt>*
        hit = True
        while hit:
            retArray = Parfmt(readedData)
            readedData = retArray[0]
            hit = retArray[1]
            
            if hit:
                hitAll = True
        
        #<apoctl>*
        hit = True
        while hit:
            retArray = Apoctl(readedData)
            readedData = retArray[0]
            hit = retArray[1]
            
            if hit:
                hitAll = True
    
    #Zde podle standardu uz by se <parfmt> nemel vyskytovat, nicmene OCR system to nedodrzuje
    #<parfmt>*
    #hit = True
    #while hit:
    #    retArray = Parfmt(readedData)
    #    readedData = retArray[0]
    #    hit = retArray[1]
    
    #<tabdef>?
    if re.match(r"\\(tqr|tqc|tqdec|tldot|tlmdot|tlhyph|tlul|tlth|tleq|tb|tx)", readedData):
        retArray = Tabdef(readedData)
        readedData = retArray[0]
    
    hitAll = True
    while hitAll:
        hitAll = False
        
        #<parfmt>*
        hit = True
        while hit:
            retArray = Parfmt(readedData)
            readedData = retArray[0]
            hit = retArray[1]
            
            if hit:
                hitAll = True
        
        #<apoctl>*
        hit = True
        while hit:
            retArray = Apoctl(readedData)
            readedData = retArray[0]
            hit = retArray[1]
            
            if hit:
                hitAll = True
    
    #<shading>?
    if re.match(r"\\(shading|bghoriz|bgvert|bgfdiag|bgbdiag|bgcross|bgdcross|bgdkhoriz|bgdkvert|bgdkfdiag|bgdkbdiag|bgdkcross|bgdkdcross)", readedData):
        retArray = Shading(readedData)
        readedData = retArray[0]
    
    if re.match(r"\\v\s*\\spv",  readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\v\s*\\spv\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho v nebo spv slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    if re.match(r"\\subdocument", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\subdocument\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        sys.stderr.write("Vyznam klicoveho v nebo spv slova neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    else:
        hit = True
        while hit:
            retArray = Char(readedData)
            readedData = retArray[0]
            hit = retArray[1]
            
            if hit:
                success = True
    
    #sys.stderr.write(readedData[:128] + "\n")
    #sys.stderr.write("<Textpar> pred kl.sl. par konec\n")
    #sys.stderr.write("Pokracovat...\n")
    #a=raw_input()
    
    if re.match(r"\\par\s*(\\|\{|\})", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\par\s*", "", readedData, 1)
        
        sys.stderr.write(readedData[:128] + "\n")
        sys.stderr.write("<Textpar> konec\n")
        sys.exit(0)
        
        retArray = Para(readedData)
        readedData = retArray[0]
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowjust>
#\trql | \trqr | \trqc
#@profile
def Rowjust(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowjust()\n")
    
    success = True
    
    if re.match(r"\\trql", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trql\s*", "", readedData, 1)
        
        globTbl["rowjust"] = "trql"
    
    elif re.match(r"\\trqr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trqr\s*", "", readedData, 1)
        
        globTbl["rowjust"] = "trqr"
    
    elif re.match(r"\\trqc", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trqc\s*", "", readedData, 1)
        
        globTbl["rowjust"] = "trqc"
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowwrite> 
#\ltrrow | \rtlrow
#@profile
def Rowwrite(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowwrite()\n")
    
    success = True
    
    if re.match(r"\\ltrrow", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ltrrow\s*", "", readedData, 1)
        
        globTbl["rowwrite"] = "ltrrow"
    
    elif re.match(r"\\rtlrow", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\rtlrow\s*", "", readedData, 1)
        
        globTbl["rowwrite"] = "rtlrow"
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#@profile
def Brdrk(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Brdrk()\n")
    
    brdrkKyes = {"brdrs":"",
                          "brdrth":"",
                          "brdrsh":"",
                          "brdrdb":"",
                          "brdrdot":"",
                          "brdrdash":"",
                          "brdrhair":"",
                          "brdrinset":"",
                          "brdrdashsm":"",
                          "brdrdashd":"",
                          "brdrdashdd":"",
                          "brdrdashdot":"",
                          "brdrdashdotdot":"",
                          "brdrtriple":"",
                          "brdrtnthsg":"",
                          "brdrthtnsg":"",
                          "brdrtnthtnsg":"",
                          "brdrtnthmg":"",
                          "brdrthtnmg":"",
                          "brdrtnthtnmg":"",
                          "brdrtnthlg":"",
                          "brdrthtnlg":"",
                          "brdrtnthtnlg":"",
                          "brdrwavy":"",
                          "brdrwavydb":"",
                          "brdrdashdotstr":"",
                          "brdremboss":"",
                          "brdrengrave":"",
                          "brdroutset":"",
                          "brdrnone":"",
                          "brdrtbl":"",
                          "brdrnil":""
                 }
    
    try:
        tmpKey = re.match(r"\\([a-zA-Z]+)", readedData).group(1)
    except AttributeError as e:
        sys.stderr.write("Nelze nacist keyword z <brdrk>!\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        sys.exit(errCode["parseErr"])
    
    #kontrola kl. slova
    if brdrkKyes.has_key(tmpKey):
        #ulozeni nastaveni
        brdrk = tmpKey
        
        #odstraneni nacteneho kl. slova
        readedData = re.sub(r"^\\[a-zA-Z]+\s*", "", readedData, 1)
    
    else:
        sys.stderr.write("Chyba pri cteni klicoveho slova ze skupiny <brdrk>!\n")
        sys.exit(errCode["parseErr"])
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(brdrk)
    return retArray

#<brdr>
#<brdrk> \brdrwN? \brspN? \brdrcfN?
#@profile
def Brdr(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Brdr()\n")
    
    brdr = {}
    
    #<brdrk>
    retArray = Brdrk(readedData)
    readedData = retArray[0]
    brdrk = retArray[1]
    
    brdr["brdrk"] = brdrk
    
    #\brdrwN?
    if re.match(r"\\brdrw", readedData):
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\\brdrw\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            brdrw = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <brdr>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni nastaveni
        brdr["brdrw"] = brdrw
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    #\brspN?
    if re.match(r"\\brsp", readedData):
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\\brsp\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            brsp = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <brdr>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni nastaveni
        brdr["brsp"] = brsp
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    #\brdrcfN?
    if re.match(r"\\brdrcf", readedData):
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\\brdrcf\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            brdrcf = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <brdr>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
    
        #ulozeni nastaveni
        brdr["brdrcf"] = brdrcf
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(brdr)
    return retArray

#<rowtop> 
#\trbrdrt <brdr>
#@profile
def Rowtop(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowtop()\n")
    
    success = True
    
    if re.match(r"\\trbrdrt", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trbrdrt\s*", "", readedData, 1)
        
        #<brdr>
        retArray = Brdr(readedData)
        readedData = retArray[0]
        brdr = retArray[1]
        
        globTbl["rowtop"] = brdr
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowbot> 
#\trbrdrb <brdr>
#@profile
def Rowbot(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowbot()\n")
    
    success = True
    
    if re.match(r"\\trbrdrb", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trbrdrb\s*", "", readedData, 1)
        
        #<brdr>
        retArray = Brdr(readedData)
        readedData = retArray[0]
        brdr = retArray[1]
        
        globTbl["rowbot"] = brdr
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowleft> 
#\trbrdrl <brdr>
#@profile
def Rowleft(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowleft()\n")
    
    success = True
    
    if re.match(r"\\trbrdrl", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trbrdrl\s*", "", readedData, 1)
        
        #<brdr>
        retArray = Brdr(readedData)
        readedData = retArray[0]
        brdr = retArray[1]
        
        globTbl["rowleft"] = brdr
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowright> 
#\trbrdrr <brdr>
#@profile
def Rowright(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowright()\n")
    
    success = True
    
    if re.match(r"\\trbrdrr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trbrdrr\s*", "", readedData, 1)
        
        #<brdr>
        retArray = Brdr(readedData)
        readedData = retArray[0]
        brdr = retArray[1]
        
        globTbl["rowright"] = brdr
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowhor> 
#\trbrdrh <brdr>
#@profile
def Rowhor(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowhor()\n")
    
    success = True
    
    if re.match(r"\\trbrdrh", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trbrdrh\s*", "", readedData, 1)
        
        #<brdr>
        retArray = Brdr(readedData)
        readedData = retArray[0]
        brdr = retArray[1]
        
        globTbl["rowhor"] = brdr
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowvert> 
#\trbrdrv <brdr>
#@profile
def Rowvert(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowvert()\n")
    
    success = True
    
    if re.match(r"\\trbrdrv", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trbrdrv\s*", "", readedData, 1)
        
        #<brdr>
        retArray = Brdr(readedData)
        readedData = retArray[0]
        brdr = retArray[1]
        
        globTbl["rowvert"] = brdr
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowhframe>
#\phmrg? | \phpg? | \phcol?
#@profile
def Rowhframe(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowhframe()\n")
    
    success = True
    
    if re.match(r"\\phmrg", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\phmrg\s*", "", readedData, 1)
        
        globTbl["rowhframe"] = "phmrg"
    
    elif re.match(r"\\phpg", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\phpg\s*", "", readedData, 1)
        
        globTbl["rowhframe"] = "phpg"
    
    elif re.match(r"\\phcol", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\phcol\s*", "", readedData, 1)
        
        globTbl["rowhframe"] = "phcol"
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowhdist>
#\tposxN? | \tposnegxN? | \tposxc? | \tposxi? | \tposxo? | \tposxl? | \tposxr?
#@profile
def Rowhdist(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowhdist()\n")
    
    success = True
    
    if re.match(r"\\tposx", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tposx\s*", "", readedData, 1)
        
        rowhdist = []
        
        #ziskani hodnoty
        try:
            tposx = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowhdist>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
    
        #ulozeni nastaveni
        rowhdist["name"] = "tposx"
        rowhdist["data"] = tposx
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globTbl["rowhdist"] = rowhdist
    
    elif re.match(r"\\tposnegx", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tposnegx\s*", "", readedData, 1)
        
        rowhdist = []
        
        #ziskani hodnoty
        try:
            tposnegx = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowhdist>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
    
        #ulozeni nastaveni
        rowhdist["name"] = "tposnegx"
        rowhdist["data"] = tposnegx
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globTbl["rowhdist"] = rowhdist
    
    elif re.match(r"\\tposxc", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tposxc\s*", "", readedData, 1)
        
        globTbl["rowhdist"] = "tposxc"
    
    elif re.match(r"\\tposxi", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tposxi\s*", "", readedData, 1)
        
        globTbl["rowhdist"] = "tposxi"
    
    elif re.match(r"\\tposxo", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tposxo\s*", "", readedData, 1)
        
        globTbl["rowhdist"] = "tposxo"
    
    elif re.match(r"\\tposxl", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tposxl\s*", "", readedData, 1)
        
        globTbl["rowhdist"] = "tposxl"
    
    elif re.match(r"\\tposxr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tposxr\s*", "", readedData, 1)
        
        globTbl["rowhdist"] = "tposxr"
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowhorzpos>
#<rowhframe>& <rowhdist>
#@profile
def Rowhorzpos(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowhorzpos()\n")
    
    success = False
    
    #<rowhframe>
    retArray = Rowhframe(readedData)
    readedData = retArray[0]
    success = retArray[1]
    
    if success:
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    #<rowhdist>
    retArray = Rowhdist(readedData)
    readedData = retArray[0]
    success = retArray[1]
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowvframe>
#\tpvmrg? | \tpvpg? | \tpvpara?
#@profile
def Rowvframe(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowvframe()\n")
    
    success = True
    
    if re.match(r"\\tpvmrg", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tpvmrg\s*", "", readedData, 1)
        
        globTbl["rowvframe"] = "tpvmrg"
    
    elif re.match(r"\\tpvpg", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tpvpg\s*", "", readedData, 1)
        
        globTbl["rowvframe"] = "tpvpg"
    
    elif re.match(r"\\tpvpara", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tpvpara\s*", "", readedData, 1)
        
        globTbl["rowvframe"] = "tpvpara"
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowvdist>
#\tposyN? | \tposnegyN? | \tposyt? | \tposyil? | \tposyb? | \tposyc? | \tposyin |
#\tposyout?
#@profile
def Rowvdist(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowvdist()\n")
    
    success = True
    
    if re.match(r"\\tposy", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tposy\s*", "", readedData, 1)
        
        rowvdist = []
        
        #ziskani hodnoty
        try:
            tposy = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowvdist>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
    
        #ulozeni nastaveni
        rowvdist["name"] = "tposy"
        rowvdist["data"] = tposy
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globTbl["rowvdist"] = rowvdist
    
    elif re.match(r"\\tposnegy", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tposnegy\s*", "", readedData, 1)
        
        rowvdist = []
        
        #ziskani hodnoty
        try:
            tposnegy = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowvdist>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
    
        #ulozeni nastaveni
        rowvdist["name"] = "tposnegy"
        rowvdist["data"] = tposnegy
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globTbl["rowvdist"] = rowvdist
    
    elif re.match(r"\\tposyt", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tposyt\s*", "", readedData, 1)
        
        globTbl["rowvdist"] = "tposyt"
    
    elif re.match(r"\\tposyil", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tposyil\s*", "", readedData, 1)
        
        globTbl["rowvdist"] = "tposyil"
    
    elif re.match(r"\\tposyb", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tposyb\s*", "", readedData, 1)
        
        globTbl["rowvdist"] = "tposyb"
    
    elif re.match(r"\\tposyc", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tposyc\s*", "", readedData, 1)
        
        globTbl["rowvdist"] = "tposyc"
    
    elif re.match(r"\\tposyin", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tposyin\s*", "", readedData, 1)
        
        globTbl["rowvdist"] = "tposyin"
    
    elif re.match(r"\\tposyout", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tposyout\s*", "", readedData, 1)
        
        globTbl["rowvdist"] = "tposyout"
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowvertpos>
#<rowvframe>& <rowvdist>
#@profile
def Rowvertpos(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowvertpos()\n")
    
    success = False
    
    #<rowvframe>
    retArray = Rowvframe(readedData)
    readedData = retArray[0]
    success = retArray[1]
    
    if success:
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    #<rowvdist>
    retArray = Rowvdist(readedData)
    readedData = retArray[0]
    success = retArray[1]
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowwrap>
#\tdfrmtxtLeftN? & \tdfrmtxtRightN? & \tdfrmtxtTopN? & \tdfrmtxtBottomN?
#@profile
def Rowwrap(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowwrap()\n")
    
    success = True
    
    if re.match(r"\\tdfrmtxtLeft", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tdfrmtxtLeft\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            tdfrmtxtLeft = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowwrap>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\tdfrmtxtRight", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tdfrmtxtRight\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            tdfrmtxtRight = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowwrap>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\tdfrmtxtTop", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tdfrmtxtTop\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            tdfrmtxtTop = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowwrap>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\tdfrmtxtBottom", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\tdfrmtxtBottom\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            tdfrmtxtBottom = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowwrap>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowwidth>
#\trftsWidthN & \trwWidthN?
#@profile
def Rowwidth(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowwidth()\n")
    
    success = True
    
    if re.match(r"\\trftsWidth", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trftsWidth\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trftsWidth = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowwidth>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trwWidth", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trwWidth\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trwWidth = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowwidth>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowinv>
#(\trftsWidthBN & \trwWidthBN?)? & (\trftsWidthAN & \trwWidthAN?)?
#@profile
def Rowinv(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowinv()\n")
    
    success = True
    
    if re.match(r"\\trftsWidthB", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trftsWidthB\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trftsWidthB = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowinv>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trwWidthB", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trwWidthB\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trwWidthB = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowinv>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trftsWidthA", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trftsWidthA\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trftsWidthA = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowinv>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trwWidthA", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trwWidthA\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trwWidthA = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowinv>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowpos>
#<rowhorzpos> & <rowvertpos> & <rowwrap> & \tabsnoovrlp?
#@profile
def Rowpos(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowpos()\n")
    
    success = True
    successAll = False
    
    while success:
        #<rowhorzpos>
        retArray = Rowhorzpos(readedData)
        readedData = retArray[0]
        success = retArray[1]
        
        if success:
            successAll = True
            continue
        
        #<rowvertpos>
        retArray = Rowvertpos(readedData)
        readedData = retArray[0]
        success = retArray[1]
        
        if success:
            successAll = True
            continue
        
        #<rowwrap>
        retArray = Rowwrap(readedData)
        readedData = retArray[0]
        success = retArray[1]
        
        if success:
            successAll = True
            continue
        
        if re.match(r"\\tabsnoovrlp", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\tabsnoovrlp\s*", "", readedData, 1)
            
            success = True
            successAll = True
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(successAll)
    return retArray

#<rowspc>
#(\trspdlN & \trspdflN?)? & (\trspdtN & \trspdftN?)? & (\trspdbN & \trspdfbN?)? &
#(\trspdrN & \trspdfrN?)?
#@profile
def Rowspc(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowspc()\n")
    
    success = True
    
    if re.match(r"\\trspdl", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trspdl\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trspdl = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowspc>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trspdfl", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trspdfl\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trspdfl = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowspc>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trspdt", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trspdt\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trspdt = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowspc>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trspdft", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trspdft\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trspdft = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowspc>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trspdb", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trspdb\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trspdb = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowspc>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trspdfb", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trspdfb\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trspdfb = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowspc>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trspdr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trspdr\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trspdr = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowspc>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trspdfr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trspdfr\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trspdfr = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowspc>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowpad>
#(\trpaddlN & \trpaddflN?)? & (\trpaddtN & \trpaddftN?)? & (\trpaddbN & \trpaddfbN?)?
#& (\trpaddrN & \trpaddfrN?)?
#@profile
def Rowpad(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowpad()\n")
    
    success = True
    
    if re.match(r"\\trpaddl", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trpaddl\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trpaddl = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowpad>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trpaddfl", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trpaddfl\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trpaddfl = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowpad>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trpaddt", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trpaddt\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trpaddt = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowpad>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trpaddft", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trpaddft\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trpaddft = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowpad>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trpaddb", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trpaddb\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trpaddb = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowpad>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trpaddfb", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trpaddfb\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trpaddfb = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowpad>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trpaddr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trpaddr\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trpaddr = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowpad>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trpaddfr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trpaddfr\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trpaddfr = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowpad>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowspcout>
#(\trspolN & \trspoflN?)? & (\trspotN & \trspoftN?)? & (\trspobN & \trspofbN?)? &
#(\trsporN & \trspofrN?)?
#@profile
def Rowspcout(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowspcout()\n")
    
    success = True
    
    if re.match(r"\\trspol", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trspol\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trspol = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowspcout>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trspofl", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trspofl\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trspofl = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowspcout>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trspot", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trspot\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trspot = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowspcout>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trspoft", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trspoft\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trspoft = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowspcout>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trspob", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trspob\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trspob = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowspcout>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trspofb", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trspofb\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trspofb = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowspcout>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trspor", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trspor\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trspor = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowspcout>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trspofr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trspofr\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trspofr = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowspcout>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<rowpadout>
#(\trpadolN & \trpadoflN?)? & (\trpadotN & \trpadoftN?)? & (\trpadobN & \trpadofbN?)?
#& (\trpadorN & \trpadofrN?)?
#@profile
def Rowpadout(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rowpadout()\n")
    
    success = True
    
    if re.match(r"\\trpadol", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trpadol\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trpadol = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowpadout>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trpadofl", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trpadofl\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trpadofl = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowpadout>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trpadot", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trpadot\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trpadot = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowpadout>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trpadoft", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trpadoft\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trpadoft = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowpadout>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trpadob", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trpadob\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trpadob = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowpadout>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trpadofb", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trpadofb\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trpadofb = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowpadout>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trpador", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trpador\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trpador = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowpadout>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\trpadofr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trpadofr\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trpadofr = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <rowpadout>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<trrevision>
#\trauthN \trdateN
#@profile
def Trrevision(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Trrevision()\n")
    
    success = True
    
    if re.match(r"\\trauth", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trauth\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trauth = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <trrevision>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trdate\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            trdate = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <trrevision>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<tflags>
#\tbllkborder & \tbllkshading & \tbllkfont & \tbllkcolor & \tbllkbestfit & \tbllkhdrrows &
#\tbllklastrow & \tbllkhdrcols & \tbllklastcol & \ tbllknorowband & \ tbllknocolband
#@profile
def Tflags(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Tflags()\n")
    
    success = True
    
    if re.match(r"\\(\tbllkborder|tbllkshading|tbllkfont|tbllkcolor|tbllkbestfit|tbllkhdrrows|tbllklastrow|tbllkhdrcols|tbllklastcol|tbllknorowband|tbllknocolband)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(\tbllkborder|tbllkshading|tbllkfont|tbllkcolor|tbllkbestfit|tbllkhdrrows|tbllklastrow|tbllkhdrcols|tbllklastcol|tbllknorowband|tbllknocolband)\s*", "", readedData, 1)
        
        sys.stderr.write("Vyznam klicoveho slova (\tbllkborder|tbllkshading|tbllkfont|tbllkcolor|tbllkbestfit|tbllkhdrrows|tbllklastrow|tbllkhdrcols|tbllklastcol|tbllknorowband|tbllknocolband) neimplementovan!\n")
        sys.exit(errCode["notImplemented"])
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<celldgu>
#\cldglu <brdr>
#@profile
def Celldgu(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Celldgu()\n")
    
    success = True
    
    if re.match(r"\\cldglu", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cldglu\s*", "", readedData, 1)
        
        #<brdr>
        retArray = Brdr(readedData)
        readedData = retArray[0]
        brdr = retArray[1]
        
        globTbl["celldgu"] = brdr
        
        sys.stderr.write(readedData[:128] + "\n")
        sys.stderr.write("<Celldgu> konec\n")
        sys.exit(0)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<celldgl>
#\cldgll <brdr>
#@profile
def Celldgl(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Celldgl()\n")
    
    success = True
    
    if re.match(r"\\celldgl", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\celldgl\s*", "", readedData, 1)
        
        #<brdr>
        retArray = Brdr(readedData)
        readedData = retArray[0]
        brdr = retArray[1]
        
        globTbl["celldgl"] = brdr
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<cellalign>
#\clvertalt | \clvertalc | \clvertalb
#@profile
def Cellalign(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Cellalign()\n")
    
    success = True
    
    if re.match(r"\\clvertalt", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clvertalt\s*", "", readedData, 1)
        
        globTbl["cellalign"] = "clvertalt"
    
    elif re.match(r"\\clvertalc", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clvertalc\s*", "", readedData, 1)
        
        globTbl["cellalign"] = "clvertalc"
    
    elif re.match(r"\\clvertalb", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clvertalb\s*", "", readedData, 1)
        
        globTbl["cellalign"] = "clvertalb"
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<celltop>
#\clbrdrt <brdr>
#@profile
def Celltop(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Celltop()\n")
    
    success = True
    
    if re.match(r"\\clbrdrt", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clbrdrt\s*", "", readedData, 1)
        
        #<brdr>
        retArray = Brdr(readedData)
        readedData = retArray[0]
        brdr = retArray[1]
        
        globTbl["clbrdrt"] = brdr
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<cellleft>
#\clbrdrl <brdr>
#@profile
def Cellleft(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Cellleft()\n")
    
    success = True
    
    if re.match(r"\\clbrdrl", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clbrdrl\s*", "", readedData, 1)
        
        #<brdr>
        retArray = Brdr(readedData)
        readedData = retArray[0]
        brdr = retArray[1]
        
        globTbl["clbrdrl"] = brdr
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<cellbot>
#\clbrdrb <brdr>
#@profile
def Cellbot(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Cellbot()\n")
    
    success = True
    
    if re.match(r"\\clbrdrb", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clbrdrb\s*", "", readedData, 1)
        
        #<brdr>
        retArray = Brdr(readedData)
        readedData = retArray[0]
        brdr = retArray[1]
        
        globTbl["clbrdrb"] = brdr
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<cellright>
#\clbrdrr <brdr>
#@profile
def Cellright(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Cellright()\n")
    
    success = True
    
    if re.match(r"\\clbrdrr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clbrdrr\s*", "", readedData, 1)
        
        #<brdr>
        retArray = Brdr(readedData)
        readedData = retArray[0]
        brdr = retArray[1]
        
        globTbl["clbrdrr"] = brdr
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<cellpat>
#\clbghoriz | \clbgvert | \clbgfdiag | \clbgbdiag | \clbgcross | \clbgdcross | \clbgdkhor
#| \clbgdkvert | \clbgdkfdiag | \clbgdkbdiag | \clbgdkcross | \clbgdkdcross
#@profile
def Cellpat(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Cellpat()\n")
    
    success = True
    
    if re.match(r"\\clbghoriz", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clbghoriz\s*", "", readedData, 1)
        
        globTbl["cellpat"] = "clbghoriz"
    
    elif re.match(r"\\clbgvert", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clbgvert\s*", "", readedData, 1)
        
        globTbl["cellpat"] = "clbgvert"
    
    elif re.match(r"\\clbgfdiag", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clbgfdiag\s*", "", readedData, 1)
        
        globTbl["cellpat"] = "clbgfdiag"
    
    elif re.match(r"\\clbgbdiag", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clbgbdiag\s*", "", readedData, 1)
        
        globTbl["cellpat"] = "clbgbdiag"
    
    elif re.match(r"\\clbgcross", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clbgcross\s*", "", readedData, 1)
        
        globTbl["cellpat"] = "clbgcross"
    
    elif re.match(r"\\clbgdcross", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clbgdcross\s*", "", readedData, 1)
        
        globTbl["cellpat"] = "clbgdcross"
    
    elif re.match(r"\\clbgdkhor", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clbgdkhor\s*", "", readedData, 1)
        
        globTbl["cellpat"] = "clbgdkhor"
    
    elif re.match(r"\\clbgdkvert", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clbgdkvert\s*", "", readedData, 1)
        
        globTbl["cellpat"] = "clbgdkvert"
    
    elif re.match(r"\\clbgdkfdiag", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clbgdkfdiag\s*", "", readedData, 1)
        
        globTbl["cellpat"] = "clbgdkfdiag"
    
    elif re.match(r"\\clbgdkbdiag", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clbgdkbdiag\s*", "", readedData, 1)
        
        globTbl["cellpat"] = "clbgdkbdiag"
    
    elif re.match(r"\\clbgdkcross", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clbgdkcross\s*", "", readedData, 1)
        
        globTbl["cellpat"] = "clbgdkcross"
    
    elif re.match(r"\\clbgdkdcross", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clbgdkdcross\s*", "", readedData, 1)
        
        globTbl["cellpat"] = "clbgdkdcross"
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<cellshad>
#<cellpat>? \clcfpatN? & \clcbpatN? & \clshdngN
#@profile
def Cellshad(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Cellshad()\n")
    
    success = True
    
    #<cellpat>
    if re.match(r"\\(clbghoriz|clbgvert|clbgfdiag|clbgbdiag|clbgcross|clbgdcross|clbgdkhor|clbgdkvert|clbgdkfdiag|clbgdkbdiag|clbgdkcross|clbgdkdcross)", readedData):
        retArray = Cellpat(readedData)
        readedData = retArray[0]
        success = retArray[1]
    
    elif re.match(r"\\clcfpat(\-)?\d+", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clcfpat\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clcfpat = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellshad>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\clcbpat(\-)?\d+", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clcbpat\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clcbpat = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellshad>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\clshdng(\-)?\d+", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clshdng\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clshdng = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellshad>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<cellflow>
#\cltxlrtb | \cltxtbrl | \cltxbtlr | \cltxlrtbv | \cltxtbrlv
#@profile
def Cellflow(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Cellflow()\n")
    
    success = True
    
    if re.match(r"\\cltxlrtb", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cltxlrtb\s*", "", readedData, 1)
        
        globTbl["cellflow"] = "cltxlrtb"
    
    elif re.match(r"\\cltxtbrl", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cltxtbrl\s*", "", readedData, 1)
        
        globTbl["cellflow"] = "cltxtbrl"
    
    elif re.match(r"\\cltxbtlr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cltxbtlr\s*", "", readedData, 1)
        
        globTbl["cellflow"] = "cltxbtlr"
    
    elif re.match(r"\\cltxlrtbv", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cltxlrtbv\s*", "", readedData, 1)
        
        globTbl["cellflow"] = "cltxlrtbv"
    
    elif re.match(r"\\cltxtbrlv", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cltxtbrlv\s*", "", readedData, 1)
        
        globTbl["cellflow"] = "cltxtbrlv"
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<cellwidth>
#\clftsWidthN & \clwWidthN? & \clhidemark?
#@profile
def Cellwidth(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Cellwidth()\n")
    
    success = True
    
    if re.match(r"\\clftsWidth", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clftsWidth\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clftsWidth = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellwidth>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\clwWidth", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clwWidth\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clwWidth = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellwidth>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\clhidemark", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clhidemark\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clhidemark = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellwidth>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<cellrevauth>
#\clmrgdauthN
#@profile
def Cellrevauth(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Cellrevauth()\n")
    
    success = True
    
    if re.match(r"\\clmrgdauth", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clmrgdauth\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clmrgdauth = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellrevauth>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<cellrevdate>
#\clmrgddttmN
#@profile
def Cellrevdate(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Cellrevdate()\n")
    
    success = True
    
    if re.match(r"\\clmrgddttm", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clmrgddttm\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clmrgddttm = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellrevdate>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<cellrev>
#\clmrgd | \clmrgdr | \ clsplit | \clsplitr & <cellrevauth>? & <cellrevdate>?
#@profile
def Cellrev(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Cellrev()\n")
    
    success = True
    
    if re.match(r"\\clmrgd", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clmrgd\s*", "", readedData, 1)
        
        globTbl["cellrev"] = "clmrgd"
    
    elif re.match(r"\\clmrgdr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clmrgdr\s*", "", readedData, 1)
        
        globTbl["cellrev"] = "clmrgdr"
    
    elif re.match(r"\\clsplit", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clsplit\s*", "", readedData, 1)
        
        globTbl["cellrev"] = "clsplit"
    
    elif re.match(r"\\clsplitr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clsplitr\s*", "", readedData, 1)
        
        globTbl["cellrev"] = "clsplitr"
    
    elif re.match(r"\\clmrgdauth", readedData):
        retArray = Cellrevauth(readedData)
        readedData = retArray[0]
        #hit = retArray[1]
    
    elif re.match(r"\\clmrgddttm", readedData):
        retArray = Cellrevdate(readedData)
        readedData = retArray[0]
        #hit = retArray[1]
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<cellinsauth>
#\clinsauthN
#@profile
def Cellinsauth(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Cellinsauth()\n")
    
    success = True
    
    if re.match(r"\\clinsauth", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clinsauth\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clinsauth = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellinsauth>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<cellinsdttm>
#\clinsdttmN
#@profile
def Cellinsdttm(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Cellinsdttm()\n")
    
    success = True
    
    if re.match(r"\\clinsdttm", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clinsdttm\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clinsdttm = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellinsdttm>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<cellins>
#\clins & <cellinsauth>? & <cellinsdttm>?
#@profile
def Cellins(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Cellins()\n")
    
    success = True
    
    if re.match(r"\\clins", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clins\s*", "", readedData, 1)
        
        globTbl["cellins"] = "clins"
    
    elif re.match(r"\\clinsauth", readedData):
        retArray = Celldelauth(readedData)
        readedData = retArray[0]
        #hit = retArray[1]
    
    elif re.match(r"\\clinsdttm", readedData):
        retArray = Celldeldttm(readedData)
        readedData = retArray[0]
        #hit = retArray[1]
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<celldelauth>
#\cldelauth
#@profile
def Celldelauth(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Celldelauth()\n")
    
    success = True
    
    if re.match(r"\\cldelauth", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cldelauth\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            cldelauth = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <celldelauth>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<celldeldttm>
#\cldeldttmN
#@profile
def Celldeldttm(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Celldeldttm()\n")
    
    success = True
    
    if re.match(r"\\cldeldttm", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cldeldttmN\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            cldeldttmN = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <celldeldttm>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<celldel>
#\cldel & <celldelauth>? & <celldeldttm>?
#@profile
def Celldel(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Celldel()\n")
    
    success = True
    
    if re.match(r"\\cldel", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cldel\s*", "", readedData, 1)
        
        globTbl["celldel"] = "cldel"
    
    elif re.match(r"\\cldelauth", readedData):
        retArray = Celldelauth(readedData)
        readedData = retArray[0]
        #hit = retArray[1]
    
    elif re.match(r"\\cldeldttm", readedData):
        retArray = Celldeldttm(readedData)
        readedData = retArray[0]
        #hit = retArray[1]
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<cellpad>
#(\clpadlN & \clpadflN?)? & (\clpadtN & \clpadftN?)? & (\clpadbN & \clpadfbN?)? &
#(\clpadrN & \clpadfrN?)?
#@profile
def Cellpad(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Cellpad()\n")
    
    success = True
    
    if re.match(r"\\clpadl", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clpadl\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clpadl = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellpad>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\clpadfl", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clpadfl\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clpadfl = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellpad>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\clpadt", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clpadt\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clpadt = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellpad>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\clpadft", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clpadft\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clpadft = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellpad>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\clpadb", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clpadb\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clpadb = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellpad>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\clpadfb", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clpadfb\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clpadfb = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellpad>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\clpadr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clpadr\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clpadr = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellpad>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\clpadfr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clpadfr\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clpadfr = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellpad>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<cellsp>
#(\clsplN & \clspflN?)? & (\clsptN & \clspftN?)? & (\clspbN & \clspfbN?)? & (\clsprN &
#\clspfrN?)?
#@profile
def Cellsp(readedData):
    global globTbl
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Cellsp()\n")
    
    success = True
    
    if re.match(r"\\clspl", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clspl\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clspl = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellsp>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\clspfl", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clspfl\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clspfl = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellsp>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\clspt", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clspt\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clspt = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellsp>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\clspft", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clspft\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clspft = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellsp>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\clspb", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clspb\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clspb = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellsp>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\clspfb", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clspfb\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clspfb = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellsp>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\clspr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clspr\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clspr = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellsp>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    elif re.match(r"\\clspfr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clspfr\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            clspfr = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <cellsp>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

"""
#<celldef>
#(\clmgf? & \clmrg? & \clvmgf? & \clvmrg? <celldgu>? & <celldgl>? & <cellalign>? &
#<celltop>? & <cellleft>? & <cellbot>? & <cellright>? & <cellshad>? & <cellflow>? & clFitText?
#& clNoWrap? & <cellwidth>? <cellrev>? & <cellins>? & <celldel>? & <cellpad>? & <cellsp>?)
#\cellxN
#TODO: success je zbytecny, pokud uz projde regular, tak je jasne, ze bude success
def Celldef(readedData):
    global errCode
    global globTbl
    
    sys.stderr.write("Celldef()\n")
    
    success = True
    
    if re.match(r"\\(clmgf|clmrg|clvmgf|clvmrg)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(clmgf|clmrg|clvmgf|clvmrg)\s*", "", readedData, 1)
    
    #<celldgu>
    elif re.match(r"\\cldglu", readedData):
        retArray = Celldgu(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<celldgl>
    elif re.match(r"\\celldgl", readedData):
        retArray = Celldgl(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellalign>
    elif re.match(r"\\(clvertalt|clvertalc|clvertalb)", readedData):
        retArray = Cellalign(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<celltop>
    elif re.match(r"\\clbrdrt", readedData):
        retArray = Celltop(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellleft>
    elif re.match(r"\\clbrdrl", readedData):
        retArray = Cellleft(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellbot>
    elif re.match(r"\\clbrdrb", readedData):
        retArray = Cellbot(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellright>
    elif re.match(r"\\clbrdrr", readedData):
        retArray = Cellright(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellshad>
    elif re.match(r"\\(clbghoriz|clbgvert|clbgfdiag|clbgbdiag|clbgcross|clbgdcross|clbgdkhor|clbgdkvert|clbgdkfdiag|clbgdkbdiag|clbgdkcross|clbgdkdcross|clcfpat(\-)?\d+|clcbpat(\-)?\d+|clshdng(\-)?\d+)", readedData):
        retArray = Cellshad(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellflow>
    elif re.match(r"\\(cltxlrtb|cltxtbrl|cltxbtlr|cltxlrtbv|cltxtbrlv)", readedData):
        retArray = Cellflow(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    elif re.match(r"\\clFitText", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clFitText\s*", "", readedData, 1)
        
        globTbl["clFitText"] = True
    
    elif re.match(r"\\clNoWrap", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clNoWrap\s*", "", readedData, 1)
        
        globTbl["clNoWrap"] = True
    
    #<cellwidth>
    elif re.match(r"\\(clftsWidth|clwWidth|clhidemark)", readedData):
        retArray = Cellwidth(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellrev>
    elif re.match(r"\\(clmrgd|clmrgdr|clsplit|clsplitr|clmrgdauth|clmrgddttm)", readedData):
        retArray = Cellrev(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellins>
    elif re.match(r"\\(clins|clinsauth|clinsdttm)", readedData):
        retArray = Cellins(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<celldel>
    elif re.match(r"\\(cldel|cldelauth|cldeldttm)", readedData):
        retArray = Celldel(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellpad>
    elif re.match(r"\\(clpadl|clpadfl|clpadt|clpadft|clpadb|clpadfb|clpadr|clpadfr)", readedData):
        retArray = Cellpad(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellsp>
    elif re.match(r"\\(clspl|clspfl|clspt|clspft|clspb|clspfb|clspr|clspfr)", readedData):
        retArray = Cellsp(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    elif re.match(r"\\cellx", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cellx\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            cellx = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <celldef>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globTbl["cellx"] = cellx
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray
"""

#<celldef>
#(\clmgf? & \clmrg? & \clvmgf? & \clvmrg? <celldgu>? & <celldgl>? & <cellalign>? &
#<celltop>? & <cellleft>? & <cellbot>? & <cellright>? & <cellshad>? & <cellflow>? & clFitText?
#& clNoWrap? & <cellwidth>? <cellrev>? & <cellins>? & <celldel>? & <cellpad>? & <cellsp>?)
#\cellxN
#TODO: success je zbytecny, pokud uz projde regular, tak je jasne, ze bude success
#@profile
def Celldef(readedData):
    global errCode
    global globTbl
    global globCelldef
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Celldef()\n")
    
    success = True
    
    if not re.match(r"\\([a-zA-Z]+)", readedData):
        success = False
        
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    #nacteni klicoveho slova
    try:
        keyword = re.match(r"\\([a-zA-Z]+)", readedData).group(1)
    except AttributeError as e:
        sys.stderr.write(readedData[:128] + "\n")
        sys.stderr.write("Nelze nacist keyword!\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        sys.exit(errCode["parseErr"])
    #readedData = re.sub(r"^[a-zA-Z]+\s*", "", readedData, 1)
    
    sys.stderr.write("Keyword: " + keyword + "\n")
    
    if not globCelldef.has_key(keyword):
        success = False
        
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    if keyword == "clmgf" or keyword == "clmrg" or keyword == "clvmgf" or keyword == "clvmrg":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(clmgf|clmrg|clvmgf|clvmrg)\s*", "", readedData, 1)
    
    #<celldgu>
    elif keyword == "cldglu":
        retArray = Celldgu(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<celldgl>
    elif keyword == "celldgl":
        retArray = Celldgl(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellalign>
    elif keyword == "clvertalt" or keyword == "clvertalc" or keyword == "clvertalb":
        retArray = Cellalign(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<celltop>
    elif keyword == "clbrdrt":
        retArray = Celltop(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellleft>
    elif keyword == "clbrdrl":
        retArray = Cellleft(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellbot>
    elif keyword == "clbrdrb":
        retArray = Cellbot(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellright>
    elif keyword == "clbrdrr":
        retArray = Cellright(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellshad>
    elif keyword == "clbghoriz" or keyword == "clbgvert" or keyword == "clbgfdiag" or keyword == "clbgbdiag" or keyword == "clbgcross" or keyword == "clbgdcross" or keyword == "clbgdkhor" or keyword == "clbgdkvert" or keyword == "clbgdkfdiag" or keyword == "clbgdkbdiag" or keyword == "clbgdkcross" or keyword == "clbgdkdcross" or keyword == "clcfpat" or keyword == "clcbpat" or keyword == "clshdng":
        retArray = Cellshad(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellflow>
    elif keyword == "cltxlrtb" or keyword == "cltxtbrl" or keyword == "cltxbtlr" or keyword == "cltxlrtbv" or keyword == "cltxtbrlv":
        retArray = Cellflow(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    elif keyword == "clFitText":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clFitText\s*", "", readedData, 1)
        
        globTbl["clFitText"] = True
    
    elif keyword == "clNoWrap":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\clNoWrap\s*", "", readedData, 1)
        
        globTbl["clNoWrap"] = True
    
    #<cellwidth>
    elif keyword == "clftsWidth" or keyword == "clwWidth" or keyword == "clhidemark":
        retArray = Cellwidth(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellrev>
    elif keyword == "clmrgd" or keyword == "clmrgdr" or keyword == "clsplit" or keyword == "clsplitr" or keyword == "clmrgdauth" or keyword == "clmrgddttm":
        retArray = Cellrev(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellins>
    elif keyword == "clins" or keyword == "clinsauth" or keyword == "clinsdttm":
        retArray = Cellins(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<celldel>
    elif keyword == "cldel" or keyword == "cldelauth" or keyword == "cldeldttm":
        retArray = Celldel(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellpad>
    elif keyword == "clpadl" or keyword == "clpadfl" or keyword == "clpadt" or keyword == "clpadft" or keyword == "clpadb" or keyword == "clpadfb" or keyword == "clpadr" or keyword == "clpadfr":
        retArray = Cellpad(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<cellsp>
    elif keyword == "clspl" or keyword == "clspfl" or keyword == "clspt" or keyword == "clspft" or keyword == "clspb" or keyword == "clspfb" or keyword == "clspr" or keyword == "clspfr":
        retArray = Cellsp(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    elif keyword == "cellx":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cellx\s*", "", readedData, 1)
        
        #ziskani hodnoty
        try:
            cellx = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist keyword z <celldef>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #odstraneni pouzite casti
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        globTbl["cellx"] = cellx
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<tbldef>
#\trowd \irowN \irowbandN \tsN \trgaphN & <rowjust>? & <rowwrite>? & <rowtop>? &
#<rowbot>? & <rowleft>? & <rowright>? & <rowhor>? & <rowvert>? & <rowpos> ? & \trleft? &
#\trrhN? \trhdr? & \trkeep? & <rowwidth>? & <rowinv>? & \trautofit? & <rowspc>? &
#<rowpad>? & <rowspcout>? & <rowpadout>? & \taprtl? <trrevision>? <tflags>? <celldef>+
#@profile
def Tbldef(readedData):
    global errCode
    global globTbl
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Tbldef()\n")
    
    if re.match(r"\\trowd", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\trowd\s*", "", readedData, 1)
    else:
        retArray = []
        retArray.append(readedData)
        return retArray
    
    if re.match(r"\\irow", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\irow\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    if re.match(r"\\irowband", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\irowband\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    if re.match(r"\\ts", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ts\s*", "", readedData, 1)
        
        try:
            ts = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri ts!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        globTbl["ts"] = ts
    
    hit = True
    while hit:
        hit = False
        if re.match(r"\\irowband", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\irowband\s*", "", readedData, 1)
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
            
            hit = True
        
        #TODO: Z duvodu urychleni parsace zamerne presunuto zde
        elif re.match(r"\\clcbpatraw", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\clcbpatraw\s*", "", readedData, 1)
            
            try:
                clcbpatraw = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Chyba pri clcbpatraw!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
            globTbl["clcbpatraw"] = clcbpatraw
            
            hit = True
        
        #TODO: Z duvodu urychleni parsace zamerne presunuto zde
        elif re.match(r"\\trrh", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\trrh\s*", "", readedData, 1)
            
            try:
                trrh = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Chyba pri trrh!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
            globTbl["trrh"] = trrh
            
            hit = True
        
        #<rowjust>
        #TODO: Zde je success zrejmy a tedy zbytecny
        elif re.match(r"\\(trql|trqr|trqc)", readedData):
            retArray = Rowjust(readedData)
            readedData = retArray[0]
            hit = retArray[1]
        
        #<rowwrite>
        elif re.match(r"\\(ltrrow|rtlrow)", readedData):
            retArray = Rowwrite(readedData)
            readedData = retArray[0]
            hit = retArray[1]
        
        #<rowtop>
        elif re.match(r"\\trbrdrt", readedData):
            retArray = Rowtop(readedData)
            readedData = retArray[0]
            hit = retArray[1]
        
        #<rowbot>
        elif re.match(r"\\trbrdrb", readedData):
            retArray = Rowbot(readedData)
            readedData = retArray[0]
            hit = retArray[1]
        
        #<rowleft>
        elif re.match(r"\\trbrdrl", readedData):
            retArray = Rowleft(readedData)
            readedData = retArray[0]
            hit = retArray[1]
        
        #<rowright>
        elif re.match(r"\\trbrdrr", readedData):
            retArray = Rowright(readedData)
            readedData = retArray[0]
            hit = retArray[1]
        
        #<rowhor>
        elif re.match(r"\\trbrdrh", readedData):
            retArray = Rowhor(readedData)
            readedData = retArray[0]
            hit = retArray[1]
        
        #<rowvert>
        elif re.match(r"\\trbrdrv", readedData):
            retArray = Rowvert(readedData)
            readedData = retArray[0]
            hit = retArray[1]
        
        #<rowpos>
        elif re.match(r"\\(tdfrmtxtLeft|tdfrmtxtRight|tdfrmtxtTopN|tdfrmtxtBottom|phmrg|phpg|phcol|tposx|tposnegx|tposxc|tposxi|tposxo|tposxl|tposxr|tpvmrg|tpvpg|tpvpara|tposy|tposnegy|tposyt|tposyil|tposyb|tposyc|tposyin|tposyout|tabsnoovrlp)", readedData):
            retArray = Rowpos(readedData)
            readedData = retArray[0]
            hit = retArray[1]
        
        elif re.match(r"\\trleft", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\trleft\s*", "", readedData, 1)
            
            hit = True
        
        #TODO: Zde by mohl byt problem s tim, ze ve specifikaci neni ukazano, ze se jedna o kl. slovo s hodnotou
        elif re.match(r"\\trhdr", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\trhdr\s*", "", readedData, 1)
            
            hit = True
        
        elif re.match(r"\\trkeep", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\trkeep\s*", "", readedData, 1)
            
            hit = True
        
        #<rowwidth>
        elif re.match(r"\\(trftsWidth|trwWidth)", readedData):
            retArray = Rowwidth(readedData)
            readedData = retArray[0]
            hit = retArray[1]
        
        #<rowinv>
        elif re.match(r"\\(trftsWidthB|trwWidthB|trftsWidthA|trwWidthA)", readedData):
            retArray = Rowinv(readedData)
            readedData = retArray[0]
            hit = retArray[1]
        
        elif re.match(r"\\trautofit", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\trautofit\s*", "", readedData, 1)
            
            hit = True
        
        #<rowspc>
        elif re.match(r"\\(trspdl|trspdfl|trspdt|trspdft|trspdb|trspdfb|trspdr|trspdfr)", readedData):
            retArray = Rowspc(readedData)
            readedData = retArray[0]
            hit = retArray[1]
        
        #<rowpad>
        elif re.match(r"\\(trpaddl|trpaddfl|trpaddt|trpaddft|trpaddb|trpaddfb|trpaddr|trpaddfr)", readedData):
            retArray = Rowpad(readedData)
            readedData = retArray[0]
            hit = retArray[1]
        
        #<rowspcout>
        elif re.match(r"\\(trspol|trspofl|trspot|trspoft|trspob|trspofb|trspor|trspofr)", readedData):
            retArray = Rowspcout(readedData)
            readedData = retArray[0]
            hit = retArray[1]
        
        #<rowpadout>
        elif re.match(r"\\(\trpadol|trpadofl|trpadot|trpadoft|trpadob|trpadofb|trpador|trpadofr)", readedData):
            retArray = Rowpadout(readedData)
            readedData = retArray[0]
            hit = retArray[1]
        
        elif re.match(r"\\taprtl", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\taprtl\s*", "", readedData, 1)
            
            hit = True
        
        #<trrevision>
        elif re.match(r"\\trauth", readedData):
            retArray = Trrevision(readedData)
            readedData = retArray[0]
            hit = retArray[1]
        
        #<tflags>
        elif re.match(r"\\(\tbllkborder|tbllkshading|tbllkfont|tbllkcolor|tbllkbestfit|tbllkhdrrows|tbllklastrow|tbllkhdrcols|tbllklastcol|tbllknorowband|tbllknocolband)", readedData):
            retArray = Tflags(readedData)
            readedData = retArray[0]
            hit = retArray[1]
        
        elif re.match(r"\\clcfpatraw", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\clcfpatraw\s*", "", readedData, 1)
            
            try:
                clcfpatraw = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Chyba pri clcfpatraw!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
            globTbl["clcfpatraw"] = clcfpatraw
            
            hit = True
        
        elif re.match(r"\\clshdngraw", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\clshdngraw\s*", "", readedData, 1)
            
            try:
                clshdngraw = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Chyba pri clshdngraw!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
            globTbl["clshdngraw"] = clshdngraw
            
            hit = True
        
        else:
            #<celldef>+
            hitCell = True
            while hitCell:
                #sys.stderr.write(readedData[:64] + "\n")
                retArray = Celldef(readedData)
                readedData = retArray[0]
                hitCell = retArray[1]
                
                if hitCell:
                    hit = True
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<nestcell>
#<textpar>+ \nestcell
#@profile
def Nestcell(readedData):
    global errCode
    global globTbl
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Nestcell()\n")
    
    nestcell = False
    
    #<textpar>+
    hit = True
    while hit:
        retArray = Textpar(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    if re.match(r"\\nestcell", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\nestcell\s*", "", readedData, 1)
        
        nestcell = True
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(nestcell)
    return retArray

#<nestrow>
#<nestcell>+ '{\*' \nesttableprops <tbldef> \nestrow '}'
#@profile
def Nestrow(readedData):
    global errCode
    global globTbl
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Nestrow()\n")
    
    nestrow = False
    
    #<nestcell>+
    hit = True
    while hit:
        retArray = Nestcell(readedData)
        readedData = retArray[0]
        hit = retArray[1]
        
        if hit:
            nestrow = True
    
    #'{\*' \nesttableprops <tbldef> \nestrow '}'
    if nestrow:
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\{\\\*\s\\nesttableprops\s*", "", readedData, 1)
        
        #<tbldef>
        retArray = Tbldef(readedData)
        readedData = retArray[0]
        
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\\nestrow\s*\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(nestrow)
    return retArray

#<cell>
#(<nestrow>? <tbldef>?) & <textpar>+ \cell
#@profile
def Cell(readedData):
    global errCode
    global globTbl
    global globPrintFunctionName
    global globSectList
    global globTextData
    
    if globPrintFunctionName:
        sys.stderr.write("Cell()\n")
    
    #print globSectList
    
    success = True
    while success:
        #<nestrow>?
        retArray = Nestrow(readedData)
        readedData = retArray[0]
        success = retArray[1]
        
        #if success:
        #<tbldef>?
        retArray = Tbldef(readedData)
        readedData = retArray[0]
        
        #<textpar>+
        hit = True
        while hit:
            retArray = Textpar(readedData)
            readedData = retArray[0]
            hit = retArray[1]
    
    #sys.stderr.write(readedData[:128] + "\n")
    #sys.stderr.write("<Cell> konec\n")
    #sys.stderr.write("Pokracovat...\n")
    #a=raw_input()
    
    if re.match(r"\\cell", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cell\s*", "", readedData, 1)
    
    else:
        sys.stderr.write(readedData[:64] + "\n")
        sys.stderr.write("Chyba pri cell!\n")
        sys.exit(errCode["parseErr"])
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<row>
#(<tbldef> <cell>+ <tbldef> \row) | (<tbldef> <cell>+ \row) | (<cell>+ <tbldef> \row)
#TODO: Zde si to pohlidat, \trowd bude resetovat nastaveni globTbl. Ale nemusi to tak ve skutecnosti byt.
#@profile
def Row(readedData):
    global globPara
    global errCode
    global globTbl
    global globSectList
    global globTextData
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Row()\n")
    
    success = False
    
    #print globSectList
    
    #<tbldef> 
    retArray = Tbldef(readedData)
    readedData = retArray[0]
    
    #<cell>+
    while not re.match(r"\\row", readedData):
        retArray = Cell(readedData)
        readedData = retArray[0]
        
        #<tbldef> 
        #Podle definice sem <tbldef> nepatri, ale je to jedinna moznost, jak rozlisit, zda <tbldef> patri do <cell> anebo do <row>
        retArray = Tbldef(readedData)
        readedData = retArray[0]
    
    if re.match(r"\\row", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\row\s*", "", readedData, 1)
        
        #TODO: Zde mozna ma byt jen jedno lomitko, ale moc to nechapu kvuli ridicim znakum
        if globTextData != []:
            globTextData[-1]["text"] += "\\line"
        
        success = True
    
    else:
        sys.stderr.write("Chyba pri row!\n")
        sys.exit(errCode["parseErr"])
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<para>
#<textpar> | <row>
#@profile
def Para(readedData):
    global errCode
    global globTableBracer
    global globPrintFunctionName
    
    para = {}
    
    if globPrintFunctionName:
        sys.stderr.write("Para()\n")
    
    success = False
    
    #<textpar>
    if not re.match(r"(\{)?\\trowd", readedData):
        retArray = Textpar(readedData)
        readedData = retArray[0]
        success = retArray[1]
        
        #para = retArray[1]
    
    #<row>
    #if not para:
    else:
        #sys.stderr.write(readedData[:128] + "\n")
        #sys.stderr.write("<Para> konec\n")
        #sys.stderr.write("Pokracovat...\n")
        #a=raw_input()
    
        if re.match(r"\{", readedData):
            #print "Table bracers ON"
            readedData = re.sub(r"^\{\s*", "", readedData, 1)
            globTableBracer = True
        
        retArray = Row(readedData)
        readedData = retArray[0]
        success = retArray[1]
        
        if globTableBracer and re.match(r"\}", readedData):
            #print "Table bracers OFF"
            readedData = re.sub(r"^\}\s*", "", readedData, 1)
            globTableBracer = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<footnote>
#'{' \footnote \ftnalt? <para>+ '}'
#TODO: Footnote by se mel nejak vyuzit, protoze to pomuze k lepsi klasifikaci
#@profile
def Footnote(readedData):
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Footnote()\n")
    
    data = {}
    #paras = []
    
    data["name"] = "footnote"
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\footnote\s*", "", readedData, 1)
    
    #\ftnalt
    if re.match(r"\\ftnalt", readedData):
        readedData = re.sub(r"^\\ftnalt\s*", "", readedData, 1)
    
    #<para>+
    while not re.match(r"\}", readedData):
        retArray = Para(readedData)
        readedData = retArray[0]
        #para = retArray[1]
        
        #paras.append(para)
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(data)
    return retArray

#<fieldmod>
#\flddirty? & \fldedit? & \fldlock? & \fldpriv?
#@profile
def Fieldmod(readedData):
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Fieldmod()\n")
    
    while re.match(r"\\(flddirty|fldedit|fldlock|fldpriv)", readedData):
        readedData = re.sub(r"^(flddirty|fldedit|fldlock|fldpriv)\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<datetime>
#'CREATEDATE' | 'DATE' | 'EDITTIME' | 'PRINTDATE' | 'SAVEDATE' | 'TIME'
#@profile
def Datetime(readedData):
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Datetime()\n")
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^(CREATEDATE|DATE|EDITTIME|PRINTDATE|SAVEDATE|TIME)\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<docauto>
#'COMPARE' | 'DOCVARIABLE' | 'GOTOBUTTON' | 'IF' | 'MACROBUTTON' | 'PRINT''
#@profile
def Docauto(readedData):
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Docauto()\n")
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^(COMPARE|DOCVARIABLE|GOTOBUTTON|IF|MACROBUTTON|PRINT)\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<docinfo>
#'AUTHOR' | 'COMMENTS' | 'DOCPROPERTY' | 'FILENAME' | 'FILESIZE' | 'INFO' | 'KEYWORDS' |
#'LASTSAVEDBY' | 'NUMCHARS' | 'NUMPAGES' | 'NUMWORDS' | 'SUBJECT' | 'TEMPLATE' | 'TITLE'
#@profile
def Docinfo(readedData):
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Docinfo()\n")
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^(AUTHOR|COMMENTS|DOCPROPERTY|FILENAME|FILESIZE|INFO|KEYWORDS|LASTSAVEDBY|NUMCHARS|NUMPAGES|NUMWORDS|SUBJECT|TEMPLATE|TITLE)\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<form>
#'FORMTEXT' | 'FORMCHECKBOX' | 'FORMDROPDOWN'
#@profile
def Form(readedData):
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Form()\n")
        
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^(FORMTEXT|FORMCHECKBOX|FORMDROPDOWN)\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<formulas>
#('=' <formula>) | 'ADVANCE' | 'EQ' | 'SYMBOL'
#@profile
def Formulas(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Formulas()\n")
    
    if re.match(r"=", readedData):
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^=\s*", "", readedData, 1)
        
        #<formula>
        sys.stderr.write("<formula> neimplementovano!\n")
        sys.exit(errCode["notImplemented"])
    
    else:
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^(ADVANCE|EQ|SYMBOL)\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<indextables>
#'INDEX' | 'RD' | 'TA' | 'TC' | 'TOA' | 'TOC' | 'XE'
#@profile
def Indextables(readedData):
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Indextables()\n")
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^(INDEX|RD|TA|TC|TOA|TOC|XE)\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<links>
#'AUTOTEXT' | 'AUTOTEXTLIST' | 'HYPERLINK' | 'INCLUDEPICTURE' | 'INCLUDETEXT' | 'LINK' |
#'NOTEREF' | 'PAGEREF' | 'QUOTE' | 'REF' | 'STYLEREF'
#@profile
def Links(readedData):
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Links()\n")
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^(AUTOTEXT|AUTOTEXTLIST|HYPERLINK|INCLUDEPICTURE|INCLUDETEXT|LINK|NOTEREF|PAGEREF|QUOTE|REF|STYLEREF)\s*", "", readedData, 1)
    
    #TODO: Zde pozor, tohle by tu nemelo byt, ale na zkousku to tu davam, nejak mi to totiz nesedi podle specifikace
    readedData = re.sub(r"^[^\}]+\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<mailmerge>
#'ADDRESSBLOCK' | 'ASK' | 'COMPARE' | 'DATABASE' | 'FILLIN' | 'GREETINGLINE' | 'IF' |
#'MERGEFIELD' | 'MERGEREC' | 'MERGESEQ' | 'NEXT' | 'NEXTIF' | 'SET' | 'SKIPIF'
#@profile
def Mailmerge(readedData):
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Mailmerge()\n")
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^(ADDRESSBLOCK|ASK|COMPARE|DATABASE|FILLIN|GREETINGLINE|IF|MERGEFIELD|MERGEREC|MERGESEQ|NEXT|NEXTIF|SET|SKIPIF)\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<numbering>
#'AUTONUM' | 'AUTONUMLGL' | 'AUTONUMOUT' | 'BARCODE' | 'LISTNUM' | 'PAGE' | 'REVNUM' |
#'SECTION' | 'SECTIONPAGES' | 'SEQ'
#@profile
def Numbering(readedData):
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Numbering()\n")
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^(AUTONUM|AUTONUMLGL|AUTONUMOUT|BARCODE|LISTNUM|PAGE|REVNUM|SECTION|SECTIONPAGES|SEQ)\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<userinfo>
#'USERADDRESS' | 'USERINITIALS' | 'USERNAME'
#@profile
def Userinfo(readedData):
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Userinfo()\n")
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^(USERADDRESS|USERINITIALS|USERNAME)\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<fieldtype>
#<datetime> | <docauto> | <docinfo> | <form> | <formulas> | <indextables> | <links> |
#<mailmerge> | <numbering> | <userinfo>
#@profile
def Fieldtype(readedData):
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Fieldtype()\n")
    
    #<datetime>
    if re.match(r"(\{\s*)?(CREATEDATE|DATE|EDITTIME|PRINTDATE|SAVEDATE|TIME)", readedData):
        bracers = False
        
        if re.match(r"\{", readedData):
            bracers = True
            readedData = re.sub(r"^\{\s*", "", readedData, 1)
        
        retArray = Datetime(readedData)
        readedData = retArray[0]
        
        if bracers:
            readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #<docauto>
    elif re.match(r"(\{\s*)?(COMPARE|DOCVARIABLE|GOTOBUTTON|IF|MACROBUTTON|PRINT)", readedData):
        bracers = False
        
        if re.match(r"\{", readedData):
            bracers = True
            readedData = re.sub(r"^\{\s*", "", readedData, 1)
        
        retArray = Docauto(readedData)
        readedData = retArray[0]
        
        if bracers:
            readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #<docinfo>
    elif re.match(r"(\{\s*)?(AUTHOR|COMMENTS|DOCPROPERTY|FILENAME|FILESIZE|INFO|KEYWORDS|LASTSAVEDBY|NUMCHARS|NUMPAGES|NUMWORDS|SUBJECT|TEMPLATE|TITLE)", readedData):
        bracers = False
        
        if re.match(r"\{", readedData):
            bracers = True
            readedData = re.sub(r"^\{\s*", "", readedData, 1)
        
        retArray = Docinfo(readedData)
        readedData = retArray[0]
        
        if bracers:
            readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #<form>
    elif re.match(r"(\{\s*)?(FORMTEXT|FORMCHECKBOX|FORMDROPDOWN)", readedData):
        bracers = False
        
        if re.match(r"\{", readedData):
            bracers = True
            readedData = re.sub(r"^\{\s*", "", readedData, 1)
        
        retArray = Form(readedData)
        readedData = retArray[0]
        
        if bracers:
            readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #<formulas>
    elif re.match(r"(\{\s*)?(=|ADVANCE|EQ|SYMBOL)", readedData):
        bracers = False
        
        if re.match(r"\{", readedData):
            bracers = True
            readedData = re.sub(r"^\{\s*", "", readedData, 1)
        
        retArray = Formulas(readedData)
        readedData = retArray[0]
        
        if bracers:
            readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #<indextables>
    elif re.match(r"(\{\s*)?(INDEX|RD|TA|TC|TOA|TOC|XE)", readedData):
        bracers = False
        
        if re.match(r"\{", readedData):
            bracers = True
            readedData = re.sub(r"^\{\s*", "", readedData, 1)
        
        retArray = Indextables(readedData)
        readedData = retArray[0]
        
        if bracers:
            readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #<links>
    elif re.match(r"(\{\s*)?(AUTOTEXT|AUTOTEXTLIST|HYPERLINK|INCLUDEPICTURE|INCLUDETEXT|LINK|NOTEREF|PAGEREF|QUOTE|REF|STYLEREF)", readedData):
        bracers = False
        
        if re.match(r"\{", readedData):
            bracers = True
            readedData = re.sub(r"^\{\s*", "", readedData, 1)
        
        retArray = Links(readedData)
        readedData = retArray[0]
        
        if bracers:
            readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #<mailmerge>
    elif re.match(r"(\{\s*)?(ADDRESSBLOCK|ASK|COMPARE|DATABASE|FILLIN|GREETINGLINE|IF|MERGEFIELD|MERGEREC|MERGESEQ|NEXT|NEXTIF|SET|SKIPIF)", readedData):
        bracers = False
        
        if re.match(r"\{", readedData):
            bracers = True
            readedData = re.sub(r"^\{\s*", "", readedData, 1)
        
        retArray = Mailmerge(readedData)
        readedData = retArray[0]
        
        if bracers:
            readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #<numbering>
    elif re.match(r"(\{\s*)?(AUTONUM|AUTONUMLGL|AUTONUMOUT|BARCODE|LISTNUM|PAGE|REVNUM|SECTION|SECTIONPAGES|SEQ)", readedData):
        bracers = False
        
        if re.match(r"\{", readedData):
            bracers = True
            readedData = re.sub(r"^\{\s*", "", readedData, 1)
        
        retArray = Numbering(readedData)
        readedData = retArray[0]
        
        if bracers:
            readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #<userinfo>
    elif re.match(r"(\{\s*)?(USERADDRESS|USERINITIALS|USERNAME)", readedData):
        bracers = False
        
        if re.match(r"\{", readedData):
            bracers = True
            readedData = re.sub(r"^\{\s*", "", readedData, 1)
        
        retArray = Userinfo(readedData)
        readedData = retArray[0]
        
        if bracers:
            readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    else:
        #TODO: <fieldtype> by mel byt sice povinny, ale ve skutecnosti neni, proto jen return
        retArray = []
        retArray.append(readedData)
        return retArray
        
        #sys.stderr.write("Chyba pri <fieldtype>!\n")
        #sys.exit(errCode["parseErr"])
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<datafield>
#'{' \*\datafield #SDATA '}'
#@profile
def Datafield(readedData):
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\datafield\s*", "", readedData, 1)
    
    #SDATA
    sys.stderr.write("<datafield> neimplementovano!\n")
    sys.exit(errCode["notImplemented"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<formparams>
#\fftypeN? \ffownhelpN? \ffownstatN? \ffprotN? \ffsizeN? \fftypetxtN? \ffrecalcN?
#\ffhaslistboxN? \ffhaslistboxN? \ffmaxlenN? \ffhpsN? \ffdefresN? \ffresN?
#@profile
def Formparams(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Formparams()\n")
    
    formparams = {}
    
    if re.match(r"\\fftype", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\fftype\s*", "", readedData, 1)
        
        try:
            fftype = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <formparams>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        formparams["fftype"] = fftype
    
    if re.match(r"\\ffownhelp", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ffownhelp\s*", "", readedData, 1)
        
        try:
            ffownhelp = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <formparams>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        formparams["ffownhelp"] = ffownhelp
    
    if re.match(r"\\ffownstat", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ffownstat\s*", "", readedData, 1)
        
        try:
            ffownstat = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <formparams>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        formparams["ffownstat"] = ffownstat
    
    if re.match(r"\\ffprot", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ffprot\s*", "", readedData, 1)
        
        try:
            ffprot = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <formparams>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        formparams["ffprot"] = ffprot
    
    if re.match(r"\\ffsize", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ffsize\s*", "", readedData, 1)
        
        try:
            ffsize = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <formparams>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        formparams["ffsize"] = ffsize
    
    if re.match(r"\\fftypetxt", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\fftypetxt\s*", "", readedData, 1)
        
        try:
            fftypetxt = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <formparams>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        formparams["fftypetxt"] = fftypetxt
    
    if re.match(r"\\ffrecalc", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ffrecalc\s*", "", readedData, 1)
        
        try:
            ffrecalc = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <formparams>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        formparams["ffrecalc"] = ffrecalc
    
    if re.match(r"\\ffhaslistbox", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ffhaslistbox\s*", "", readedData, 1)
        
        try:
            ffhaslistbox = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <formparams>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        formparams["ffhaslistbox"] = ffhaslistbox
    
    if re.match(r"\\ffmaxlen", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ffmaxlen\s*", "", readedData, 1)
        
        try:
            ffmaxlen = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <formparams>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        formparams["ffmaxlen"] = ffmaxlen
    
    if re.match(r"\\ffhps", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ffhps\s*", "", readedData, 1)
        
        try:
            ffhps = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <formparams>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        formparams["ffhps"] = ffhps
    
    if re.match(r"\\ffdefres", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ffdefres\s*", "", readedData, 1)
        
        try:
            ffdefres = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <formparams>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        formparams["ffdefres"] = ffdefres
    
    if re.match(r"\\ffres", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ffres\s*", "", readedData, 1)
        
        try:
            ffres = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <formparams>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        formparams["ffres"] = ffres
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<ffname>
#'{' \ffname #PCDATA '}'
#@profile
def Ffname(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Ffname()\n")
    
    ffname = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\ffname\s*", "", readedData, 1)
    
    try:
        ffname = re.match(r"[^\}]+", readedData).group(0)
        readedData = re.sub(r"^[^\}]+", "", readedData, 1)
        
        #abstrakt muze obsahovat uvozovky, nutne osetrit
        while ffname[-1] == "\\":
            ffname += "}"
            readedData = re.sub(r"^\}", "", readedData, 1)
            
            #teoreticky muze nastat situace \"", takze proto *
            subffnamet = re.match(r"[^\}]*", readedData).group(0)
            if subffnamet == "":
                break
            else:
                readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                ffname += subffnamet
    
    except AttributeError as e:
        sys.stderr.write("Nelze precist <ffname>\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<ffdeftext>
#'{' \ffdeftext #PCDATA '}'
#@profile
def Ffdeftext(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Ffdeftext()\n")
    
    ffdeftext = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\ffdeftext\s*", "", readedData, 1)
    
    try:
        ffdeftext = re.match(r"[^\}]+", readedData).group(0)
        readedData = re.sub(r"^[^\}]+", "", readedData, 1)
        
        #abstrakt muze obsahovat uvozovky, nutne osetrit
        while ffdeftext[-1] == "\\":
            ffdeftext += "}"
            readedData = re.sub(r"^\}", "", readedData, 1)
            
            #teoreticky muze nastat situace \"", takze proto *
            subffdeftext = re.match(r"[^\}]*", readedData).group(0)
            if subffdeftext == "":
                break
            else:
                readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                ffdeftext += subffdeftext
    
    except AttributeError as e:
        sys.stderr.write("Nelze precist <ffdeftext>\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<ffformat>
#'{' \ffformat #PCDATA '}'
#@profile
def Ffformat(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Ffformat()\n")
    
    ffformat = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\ffformat\s*", "", readedData, 1)
    
    try:
        ffformat = re.match(r"[^\}]+", readedData).group(0)
        readedData = re.sub(r"^[^\}]+", "", readedData, 1)
        
        #abstrakt muze obsahovat uvozovky, nutne osetrit
        while ffformat[-1] == "\\":
            ffformat += "}"
            readedData = re.sub(r"^\}", "", readedData, 1)
            
            #teoreticky muze nastat situace \"", takze proto *
            subffformat = re.match(r"[^\}]*", readedData).group(0)
            if subffformat == "":
                break
            else:
                readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                ffformat += subffformat
    
    except AttributeError as e:
        sys.stderr.write("Nelze precist <ffformat>\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<ffhelptext>
#'{' \ffhelptext #PCDATA '}'
#@profile
def Ffhelptext(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Ffhelptext()\n")
    
    ffhelptext = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\ffhelptext\s*", "", readedData, 1)
    
    try:
        ffhelptext = re.match(r"[^\}]+", readedData).group(0)
        readedData = re.sub(r"^[^\}]+", "", readedData, 1)
        
        #abstrakt muze obsahovat uvozovky, nutne osetrit
        while ffhelptext[-1] == "\\":
            ffhelptext += "}"
            readedData = re.sub(r"^\}", "", readedData, 1)
            
            #teoreticky muze nastat situace \"", takze proto *
            subffhelptext = re.match(r"[^\}]*", readedData).group(0)
            if subffhelptext == "":
                break
            else:
                readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                ffhelptext += subffhelptext
    
    except AttributeError as e:
        sys.stderr.write("Nelze precist <ffhelptext>\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<ffstattext> 
#{' \ffstattext #PCDATA '}'
#@profile
def Ffstattext(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Ffstattext()\n")
    
    ffstattext = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\ffstattext\s*", "", readedData, 1)
    
    try:
        ffstattext = re.match(r"[^\}]+", readedData).group(0)
        readedData = re.sub(r"^[^\}]+", "", readedData, 1)
        
        #abstrakt muze obsahovat uvozovky, nutne osetrit
        while ffstattext[-1] == "\\":
            ffstattext += "}"
            readedData = re.sub(r"^\}", "", readedData, 1)
            
            #teoreticky muze nastat situace \"", takze proto *
            subffstattext = re.match(r"[^\}]*", readedData).group(0)
            if subffstattext == "":
                break
            else:
                readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                ffstattext += subffstattext
    
    except AttributeError as e:
        sys.stderr.write("Nelze precist <ffstattext>\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<ffentrymcr>
#'{' \ffentrymcr #PCDATA '}'
#@profile
def Ffentrymcr(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Ffentrymcr()\n")
    
    ffentrymcr = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\ffentrymcr\s*", "", readedData, 1)
    
    try:
        ffentrymcr = re.match(r"[^\}]+", readedData).group(0)
        readedData = re.sub(r"^[^\}]+", "", readedData, 1)
        
        #abstrakt muze obsahovat uvozovky, nutne osetrit
        while ffentrymcr[-1] == "\\":
            ffentrymcr += "}"
            readedData = re.sub(r"^\}", "", readedData, 1)
            
            #teoreticky muze nastat situace \"", takze proto *
            subffentrymcr = re.match(r"[^\}]*", readedData).group(0)
            if subffentrymcr == "":
                break
            else:
                readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                ffentrymcr += subffentrymcr
    
    except AttributeError as e:
        sys.stderr.write("Nelze precist <ffentrymcr>\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#'<ffexitmcr> 
#{' \ffexitmcr #PCDATA '}'
#@profile
def Ffexitmcr(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Ffexitmcr()\n")
    
    ffexitmcr = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\ffexitmcr\s*", "", readedData, 1)
    
    try:
        ffexitmcr = re.match(r"[^\}]+", readedData).group(0)
        readedData = re.sub(r"^[^\}]+", "", readedData, 1)
        
        #abstrakt muze obsahovat uvozovky, nutne osetrit
        while ffexitmcr[-1] == "\\":
            ffexitmcr += "}"
            readedData = re.sub(r"^\}", "", readedData, 1)
            
            #teoreticky muze nastat situace \"", takze proto *
            subffexitmcr = re.match(r"[^\}]*", readedData).group(0)
            if subffexitmcr == "":
                break
            else:
                readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                ffexitmcr += subffexitmcr
    
    except AttributeError as e:
        sys.stderr.write("Nelze precist <ffexitmcr>\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<ffl>
#'{\*' \ffl #PCDATA '}'
#@profile
def Ffl(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Ffl()\n")
    
    ffl = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\ffl\s*", "", readedData, 1)
    
    try:
        ffl = re.match(r"[^\}]+", readedData).group(0)
        readedData = re.sub(r"^[^\}]+", "", readedData, 1)
        
        #abstrakt muze obsahovat uvozovky, nutne osetrit
        while ffl[-1] == "\\":
            ffl += "}"
            readedData = re.sub(r"^\}", "", readedData, 1)
            
            #teoreticky muze nastat situace \"", takze proto *
            subffl = re.match(r"[^\}]*", readedData).group(0)
            if subffl == "":
                break
            else:
                readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                ffl += subffl
    
    except AttributeError as e:
        sys.stderr.write("Nelze precist <ffl>\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<formstrings>
#<ffname>? <ffdeftext>? <ffformat>? <ffhelptext>? <ffstattext>? <ffentrymcr>? <ffexitmcr>?
#<ffl>*
#@profile
def Formstrings(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Formstrings()\n")
    
    #<ffname>?
    if re.match(r"\{\\ffname", readedData):
        retArray = Ffname(readedData)
        readedData = retArray[0]
    
    #<ffdeftext>?
    if re.match(r"\{\\ffdeftext", readedData):
        retArray = Ffname(readedData)
        readedData = retArray[0]
    
    #<ffformat>?
    if re.match(r"\{\\ffformat", readedData):
        retArray = Ffformat(readedData)
        readedData = retArray[0]
    
    #<ffhelptext>?
    if re.match(r"\{\\ffhelptext", readedData):
        retArray = Ffhelptext(readedData)
        readedData = retArray[0]
    
    #<ffstattext>?
    if re.match(r"\{\\ffstattext", readedData):
        retArray = Ffstattext(readedData)
        readedData = retArray[0]
    
    #<ffentrymcr>?
    if re.match(r"\{\\ffentrymcr", readedData):
        retArray = Ffentrymcr(readedData)
        readedData = retArray[0]
    
    #<ffexitmcr>?
    if re.match(r"\{\\ffexitmcr", readedData):
        retArray = Ffexitmcr(readedData)
        readedData = retArray[0]
    
    #<ffl>*
    while re.match(r"\{\\ffl", readedData):
        retArray = Ffl(readedData)
        readedData = retArray[0]
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<formfield>
#'{' \*\formfield '{' <formparams> <formstrings> '}}'
#@profile
def Formfield(readedData):
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Formfield()\n")
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\formfield\s*", "", readedData, 1)
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\s*", "", readedData, 1)
    
    #<formparams>
    retArray = Formparams(readedData)
    readedData = retArray[0]
    
    #<formstrings>
    retArray = Formstrings(readedData)
    readedData = retArray[0]
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<fieldinst>
#'{\*' \fldinst <fieldtype><para>+ \fldalt? <datafield>? <formfield>? '}'
#TODO: Pozor! V nekterych regularech se nemusi objevit mezera mezi * a \klSlovo
#@profile
def Fieldinst(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Fieldinst()\n")
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\fldinst\s*", "", readedData, 1)
    
    #<fieldtype>
    retArray = Fieldtype(readedData)
    readedData = retArray[0]
    
    #<para>+
    success = True
    while success:
    #while not re.match(r"(\\fldalt|\{\\\*\s*\\datafield|\{\\\*\s*\\formfield|\})", readedData):
        retArray = Para(readedData)
        readedData = retArray[0]
        success = retArray[1]
    
    if re.match(r"\\fldalt", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\fldalt", "", readedData, 1)
    
    #<datafield>?
    if re.match(r"\{\\\*\s*\\datafield", readedData):
        retArray = Datafield(readedData)
        readedData = retArray[0]
    
    #<formfield>?
    if re.match(r"\{\\\*\s*\\formfield", readedData):
        retArray = Formfield(readedData)
        readedData = retArray[0]
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<fieldrslt>
#'{' \fldrslt <para>+ '}'
#@profile
def Fieldrslt(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Fieldrslt()\n")
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\fldrslt\s*", "", readedData, 1)
    
    bracers = False
    if re.match(r"\{\s*", readedData):
        bracers = True
        
        readedData = re.sub(r"^\{\s*", "", readedData, 1)
    
    #TODO: Toto odstranit
    #sys.stderr.write(readedData[:128] + "\n")
    
    #<para>+
    success = True
    while success:
    #while not re.match(r"\}", readedData):
        retArray = Para(readedData)
        readedData = retArray[0]
        success = retArray[1]
    
    if bracers:
        readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<listtext>
#'{' \listtext <para>+ '}'
#TODO: Cista improvizace, primy syntax ve specifikaci neni
#@profile
def Listtext(readedData):
    global errCode
    global globParaList
    global globTextData
    global globPrintFunctionName
    
    data = {}
    #paras = []
    
    if globPrintFunctionName:
        sys.stderr.write("Listtext()\n")
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\listtext\s*", "", readedData, 1)
    
    #ulozeni nastaveni odstavce. Mam podezreni, ze i kdyz se v <listtext> vyskytuji \plain a \pard, tak predchozi nastaveni by melo zustat uchovano a obnoveno po dokonceni
    PushToStack()
    
    #<para>+
    success = True
    while success:
        retArray = Para(readedData)
        readedData = retArray[0]
        success = retArray[1]
    
    TopPopFromStack()
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(data)
    return retArray

#<field>
#'{' \field <fieldmod>? <fieldinst> <fieldrslt> '}'
#TODO: Kdyztak to ifovat, na odchytavani chyb
#@profile
def Field(readedData):
    global errCode
    global globParaList
    global globPrintFunctionName
    global globWriteEnable
    
    data = {}
    #paras = []
    
    if globPrintFunctionName:
        sys.stderr.write("Field()\n")
    
    data["name"] = "field"
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\field\s*", "", readedData, 1)
    
    #<fieldmod>?
    retArray = Fieldmod(readedData)
    readedData = retArray[0]
    
    #vypnuti zapisu do globTextData
    globWriteEnable = False
    
    #<fieldinst>
    retArray = Fieldinst(readedData)
    readedData = retArray[0]
    
    #vypnuti zapisu do globTextData
    globWriteEnable = True
    
    #<fieldrslt>
    retArray = Fieldrslt(readedData)
    readedData = retArray[0]
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(data)
    return retArray

#<shpinfo>
#\shpleftN? \shptopN? \shpbottomN? \shprightN? \shplidN? \shpzN? \shpfhdrN?
#\shpbxpage ? \shpbxmargin ? \shpbxcolumn? \shpbxignore? \shpbypage ?
#\shpbymargin ? \shpbypara? \shpbyignore? \shpwrN? \shpwrkN? \shpfblwtxtN?
#\shplockanchor? \shptxt?
#@profile
def Shpinfo(readedData):
    global errCode
    global globParaList
    global globTextData
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Shpinfo()\n")
    
    shpinfoDic = {"shpleft":"", 
                            "shptop":"", 
                            "shpbottom":"", 
                            "shpright":"", 
                            "shplid":"", 
                            "shpz":"", 
                            "shpfhdr":"", 
                            "shpbxpage":"", 
                            "shpbxmargin":"", 
                            "shpbxcolumn":"", 
                            "shpbxignore":"", 
                            "shpbypage":"", 
                            "shpbymargin":"", 
                            "shpbypara":"", 
                            "shpbyignore":"", 
                            "shpwr":"", 
                            "shpwrk":"", 
                            "shpfblwtxt":"", 
                            "shplockanchor":"", 
                            "shptxt":""}
    
    while re.match(r"\\[a-zA-Z]+", readedData):
        #nacteni klicoveho slova
        try:
            keyword = re.match(r"\\([a-zA-Z]+)", readedData).group(1)
        except AttributeError as e:
            sys.stderr.write(readedData[:128] + "\n")
            sys.stderr.write("Nelze nacist keyword!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        #readedData = re.sub(r"^[a-zA-Z]+\s*", "", readedData, 1)
        
        sys.stderr.write("Keyword: " + keyword + "\n")
        
        if not shpinfoDic.has_key(keyword):            
            retArray = []
            retArray.append(readedData)
            return retArray
        
        else:
            readedData = re.sub(r"^\\[a-zA-Z]+\s*", "", readedData, 1)
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<sn>
#'{' \sn ... '}'
#@profile
def Sn(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Sn()\n")
    
    if not re.match(r"\{\\sn", readedData):        
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\sn\s*", "", readedData, 1)
    readedData = re.sub(r"^[^\}]+\s*", "", readedData, 1)
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<sv>
#'{' \sv ... '}'
#@profile
def Sv(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Sv()\n")
    
    if not re.match(r"\{\\sv", readedData):        
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\sv\s*", "", readedData, 1)
    readedData = re.sub(r"^[^\}]+\s*", "", readedData, 1)
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<hsv>
#'{\*' \hsv <accent> & \ctintN & \cshadeN '}'
#@profile
def Hsv(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Hsv()\n")
    
    if not re.match(r"\{\\\*\\hsv", readedData):        
        retArray = []
        retArray.append(readedData)
        return retArray
    
    sys.stderr.write("Hsv() neimplementovano!\n")
    sys.exit(errCode["notImplemented"])

#<sp>
#'{' \sp <sn> <sv> <hsv>? '}'
#@profile
def Sp(readedData):
    global errCode
    global globParaList
    global globTextData
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Sp()\n")
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\sp\s*", "", readedData, 1)
    
    #<sn>
    retArray = Sn(readedData)
    readedData = retArray[0]
    
    #<sv>
    retArray = Sv(readedData)
    readedData = retArray[0]
    
    #<hsv>?
    retArray = Hsv(readedData)
    readedData = retArray[0]
    
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<shpinst>
#'{\*' \shpinst <sp>+ '}'
#@profile
def Shpinst(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Shpinst()\n")
    
    if not re.match(r"\{\\\*\\shpinst", readedData):        
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\\shpinst\s*", "", readedData, 1)
    
    #<shpinfo>
    #TODO: Neni ve specifikaci, ale OCR jej dava sem
    retArray = Shpinfo(readedData)
    readedData = retArray[0]
    
    #<sp>+
    while re.match(r"\{\\sp", readedData):
        retArray = Sp(readedData)
        readedData = retArray[0]
    
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<shprslt>
#'{\*' \shprslt ... '}'
#@profile
def Shprslt(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Shprslt()\n")
    
    if not re.match(r"\{\\\*\\shprslt", readedData):        
        retArray = []
        retArray.append(readedData)
        return retArray
    
    sys.stderr.write("Shprslt() neimplementovano!\n")
    sys.exit(errCode["notImplemented"])

#<shape>
#'{' \shp <shpinfo> <shpinst> <shprslt> '}'
#@profile
def Shape(readedData):
    global errCode
    global globParaList
    global globTextData
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Shape()\n")
    
    data = []
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\shp\s*", "", readedData, 1)
    
    #<shpinfo>
    retArray = Shpinfo(readedData)
    readedData = retArray[0]
    
    #<shpinst>
    retArray = Shpinst(readedData)
    readedData = retArray[0]
    
    #<shprslt>
    retArray = Shprslt(readedData)
    readedData = retArray[0]
    
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(data)
    return retArray

#<data>
#PCDATA | <uN> | <spec> | <pict> | <obj> | <do> | <footnote> | <annot> | <field> |
#<idx> | <toc> | <bookmark>
#TODO: Umele pridan i <listtext>, zaroven <listtext> je umele vytvorena trida pro destinaci zacinajici {\listtext...
#TODO: Data se nijak nezpracovavaji
#@profile
def Data(readedData):
    global errCode
    global globTextData
    global globRawText
    global globWriteEnable
    global globChr
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Data()\n")
    
    success = False
    
    sys.stderr.write(readedData[:128] + "\n")
    
    #<uN> | <spec>
    if re.match(r"\\", readedData):
        #<uN>
        #if re.match(r"\\u", readedData):
        #    retArray = UN(readedData)
        #    readedData = retArray[0]
        #    data = retArray[1]
        #    
        #    success = True
        
        #Jedna se o PCDATA, ktera jsou vyjimecna svym pocatecnim znakem
        #PCDATA
        if re.match(r"\\'", readedData) or re.match(r"\\\}", readedData)  or re.match(r"\\line", readedData) or re.match(r"\\\{", readedData)  or re.match(r"\\u(\d{4}|\d{3}\?)", readedData):
            sys.stderr.write("PCDATA\n")
            #sys.stderr.write(readedData[:128] + "\n")
            
            try:
                sys.stderr.write("True\n")
                #sys.stderr.write(readedData[:128] + "\n")
                data = re.match(r"[^\}]+", readedData).group(0)
                readedData = re.sub(r"^[^\}]+", "", readedData, 1)
                
                #abstrakt muze obsahovat uvozovky, nutne osetrit
                #TODO: Popremyslet nad tim jeste
                while data[-1] == "\\":
                    i = -2
                    cnt = 1
                    while True:
                        if abs(i) > len(data):
                            break
                        
                        if data[i] == "\\":
                            i = i - 1
                            cnt += 1
                        else:
                            break
                    
                    if cnt % 2 == 1:
                        data += "}"
                        readedData = re.sub(r"^\}", "", readedData, 1)
                        
                        #teoreticky muze nastat situace \"", takze proto *
                        subdata = re.match(r"[^\}]*", readedData).group(0)
                        if subdata == "":
                            break
                        else:
                            readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                            data += subdata
                    else:
                        break
            
            except AttributeError as e:
                sys.stderr.write(readedData[:128] + "\n")
                sys.stderr.write("Nelze precist <data>\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                print readedData
                sys.exit(errCode["parseErr"])
            
            success = True
            
            #print data
            if globWriteEnable:
                globTextDataItem = {}
                globTextDataItem["text"] = data
                globTextDataItem["data"] = globChr.copy()
                globTextData.append(globTextDataItem.copy())
                #globTextData += data
                globRawText += data
        
        #PCDATA
        elif re.match(r"\\\\", readedData):
            sys.stderr.write("PCDATA\n")
            #sys.stderr.write(readedData[:128] + "\n")
            
            try:
                sys.stderr.write("True\n")
                #sys.stderr.write(readedData[:128] + "\n")
                data = re.match(r"[^\}]+", readedData).group(0)
                readedData = re.sub(r"^[^\}]+", "", readedData, 1)
                
                #abstrakt muze obsahovat uvozovky, nutne osetrit
                while data[-1] == "\\":
                    i = -2
                    cnt = 1
                    while True:
                        if abs(i) > len(data):
                            break
                        
                        if data[i] == "\\":
                            i = i - 1
                            cnt += 1
                        else:
                            break
                    
                    if cnt % 2 == 1:
                        data += "}"
                        readedData = re.sub(r"^\}", "", readedData, 1)
                        
                        #teoreticky muze nastat situace \"", takze proto *
                        subdata = re.match(r"[^\}]*", readedData).group(0)
                        if subdata == "":
                            break
                        else:
                            readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                            data += subdata
                    else:
                        break
            
            except AttributeError as e:
                sys.stderr.write(readedData[:128] + "\n")
                sys.stderr.write("Nelze precist <data>\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                print readedData
                sys.exit(errCode["parseErr"])
            
            success = True
            #sys.stderr.write("PCDATA\n")
            #sys.stderr.write(readedData[:128] + "\n")
            #sys.exit(0)
            
            #print data
            if globWriteEnable:
                globTextDataItem = {}
                globTextDataItem["text"] = data
                globTextDataItem["data"] = globChr.copy()
                globTextData.append(globTextDataItem.copy())
                #globTextData += data
                globRawText += data
        
        #<spec>
        else:
            retArray = Spec(readedData)
            readedData = retArray[0]
            data = retArray[1]
            success = retArray[2]
    
    #<pict> | <obj> | <do> | <footnote> | <annot> | <field> | <idx> | <toc> | <bookmark>
    elif re.match(r"\{", readedData):
        #<do> | <annot> | <bookmark>
        if re.match(r"\{\\\*", readedData):
            #<do>
            if re.match(r"\{\\\*\\do", readedData):
                retArray = Do(readedData)
                readedData = retArray[0]
                data = retArray[1]
                
                success = True
            
            #<annot>
            elif re.match(r"\{\\\*\\atnid", readedData):
                retArray = Annot(readedData)
                readedData = retArray[0]
                data = retArray[1]
                
                success = True
            
            #<bookmark>
            elif re.match(r"\{\\\*\\(bkmkstart|bkmkend)", readedData):
                retArray = Bookmark(readedData)
                readedData = retArray[0]
                data = retArray[1]
                
                success = True
            
            else:
                #return
                retArray = []
                retArray.append(readedData)
                retArray.append([])
                retArray.append(success)
                
                return retArray
                #sys.stderr.write("Chyba parseru - Data\n")
                #sys.stderr.write(readedData[:128] + "\n")
                #sys.exit(errCode["parseErr"])
                #TODO: Zde spise vracet success = False, jinak to asi nepujde
        #<pict> | <obj> | <footnote> | <field> | <idx> | <toc> | <listtext>
        else:
            #<pict>
            if re.match(r"\{\\pict", readedData):
                retArray = Pict(readedData)
                readedData = retArray[0]
                data = retArray[1]
                
                success = True
            
            #<obj>
            elif re.match(r"\{\\object", readedData):
                retArray = Obj(readedData)
                readedData = retArray[0]
                data = retArray[1]
                
                success = True
            
            #<footnote>
            elif re.match(r"\{\\footnote", readedData):
                retArray = Footnote(readedData)
                readedData = retArray[0]
                data = retArray[1]
                
                success = True
            
            #<field>
            elif re.match(r"\{\\field", readedData):
                retArray = Field(readedData)
                readedData = retArray[0]
                data = retArray[1]
                
                success = True
            
            #<listtext>
            elif re.match(r"\{\\listtext", readedData):
                retArray = Listtext(readedData)
                readedData = retArray[0]
                data = retArray[1]
                
                success = True
            
            #<idx>
            elif re.match(r"\{\\xe", readedData):
                sys.stderr.write("<idx> neimplementovano!\n")
                sys.exit(errCode["notImplemented"])
            
            #<toc>
            elif re.match(r"\{\\(tc|tcn)", readedData):
                sys.stderr.write("<toc> neimplementovano!\n")
                sys.exit(errCode["notImplemented"])
            
            #<shape>
            elif re.match(r"\{\\shp", readedData):
                retArray = Shape(readedData)
                readedData = retArray[0]
                data = retArray[1]
                
                success = True
                #sys.stderr.write("<shape> neimplementovano!\n")
                #sys.exit(errCode["notImplemented"])
            
            else:
                #return
                retArray = []
                retArray.append(readedData)
                retArray.append([])
                retArray.append(success)
                
                return retArray
                
                #sys.stderr.write("Chyba parseru - Data\n")
                #sys.stderr.write(readedData[:128] + "\n")
                #sys.exit(errCode["parseErr"])
    
    #PCDATA
    else:
        sys.stderr.write("PCDATA\n")
        #sys.stderr.write(readedData[:128] + "\n")
        if re.match(r"\}", readedData):
            sys.stderr.write("False\n")
            #return
            retArray = []
            retArray.append(readedData)
            retArray.append([])
            retArray.append(success)
            
            return retArray
        
        try:
            sys.stderr.write("True\n")
            #sys.stderr.write(readedData[:128] + "\n")
            data = re.match(r"[^\}]+", readedData).group(0)
            readedData = re.sub(r"^[^\}]+", "", readedData, 1)
            #sys.stderr.write("DATA:")
            
            #abstrakt muze obsahovat uvozovky, nutne osetrit
            while data[-1] == "\\":
                i = -2
                cnt = 1
                while True:
                    if abs(i) > len(data):
                        break
                    
                    if data[i] == "\\":
                        i = i - 1
                        cnt += 1
                    else:
                        break
                
                if cnt % 2 == 1:
                    data += "}"
                    readedData = re.sub(r"^\}", "", readedData, 1)
                    
                    #teoreticky muze nastat situace \"", takze proto *
                    subdata = re.match(r"[^\}]*", readedData).group(0)
                    if subdata == "":
                        break
                    else:
                        readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                        data += subdata
                else:
                    break
                #sys.stderr.write(str(cnt) + "\n")
                #sys.stderr.write("readedData: " + readedData[:128] + "\n")
                #sys.stderr.write("DATA: " + data + "\n")
                #sys.exit(0)
            #while data[-1] == "\\" and not re.search(r"\\\\$", data):
            #    data += "}"
            #    readedData = re.sub(r"^\}", "", readedData, 1)
            #    
            #    #teoreticky muze nastat situace \"", takze proto *
            #    subdata = re.match(r"[^\}]*", readedData).group(0)
            #    if subdata == "":
            #        break
            #    else:
            #        readedData = re.sub(r"^[^\}]*", "", readedData, 1)
            #        data += subdata
        
        except AttributeError as e:
            sys.stderr.write(readedData[:128] + "\n")
            sys.stderr.write("Nelze precist <data>\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            print readedData
            sys.exit(errCode["parseErr"])
        
        success = True
        
        #print data
        if globWriteEnable:
            globTextDataItem = {}
            globTextDataItem["text"] = data
            globTextDataItem["data"] = globChr.copy()
            globTextData.append(globTextDataItem.copy())
            #globTextData += data
            globRawText += data
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(data)
    retArray.append(success)
    return retArray

#<panose>
#'{\*' \panose <data> '}'
#@profile
def Panose(readedData):
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Panose()\n")
    
    if re.match(r"\{\\\*\\panose", readedData):
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\{\\\*\\panose\s*", "", readedData, 1)
        
        #<data>
        #TODO: v pripade vyskytu overit, co se dava do dat!
        retArray = Data(readedData)
        readedData = retArray[0]
        #data = retArray[1]
        
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<nontaggedname>
#'{\*' \fname #PCDATA ';}'
#@profile
def Nontaggedname(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Nontaggedname()\n")
    
    if not re.match(r"\{\\\*\s*\\fname", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    fname = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\fname\s*", "", readedData, 1)
    
    try:
        fname = re.match(r"[^\}]+", readedData).group(0)
        readedData = re.sub(r"^[^\}]+", "", readedData, 1)
        
        #abstrakt muze obsahovat uvozovky, nutne osetrit
        while fname[-1] == "\\":
            fname += "}"
            readedData = re.sub(r"^\}", "", readedData, 1)
            
            #teoreticky muze nastat situace \"", takze proto *
            subfname = re.match(r"[^\}]*", readedData).group(0)
            if subfname == "":
                break
            else:
                readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                fname += subfname
    
    except AttributeError as e:
        sys.stderr.write("Nelze precist <nontaggedname>\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^;\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<fonttype>
#\ftnil | \fttruetype
#@profile
def Fonttype(readedData):
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Fonttype()\n")
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^(ftnil|fttruetype)\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<fontfname>
#'{\*' \fontfile \cpgN? #PCDATA '}'
#@profile
def Fontfname(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Fontfname()\n")
    
    if not re.match(r"\{\\\*\s*\\fontfile", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    fontfile = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\fontfile\s*", "", readedData, 1)
    
    if re.match(r"\\cpg", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cpg\s*", "", readedData, 1)
        
        try:
            cpg = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <fontfname>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #formparams["fftypetxt"] = fftypetxt
        #TODO: Hodnota se neuklada
    
    try:
        fontfile = re.match(r"[^\}]+", readedData).group(0)
        readedData = re.sub(r"^[^\}]+", "", readedData, 1)
        
        #abstrakt muze obsahovat uvozovky, nutne osetrit
        while fontfile[-1] == "\\":
            fontfile += "}"
            readedData = re.sub(r"^\}", "", readedData, 1)
            
            #teoreticky muze nastat situace \"", takze proto *
            subfontfile = re.match(r"[^\}]*", readedData).group(0)
            if subfontfile == "":
                break
            else:
                readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                fontfile += subfontfile
    
    except AttributeError as e:
        sys.stderr.write("Nelze precist <fontfname>\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<fontemb>
#'{\*' \fontemb <fonttype> <fontfname>? <data>? '}'
#@profile
def Fontemb(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Fontemb()\n")
    
    if not re.match(r"\{\\\*\s*\\fontemb", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\fontemb\s*", "", readedData, 1)
    
    #<fonttype>
    retArray = Fonttype(readedData)
    readedData = retArray[0]
    
    #<fontfname>?
    retArray = Fontfname(readedData)
    readedData = retArray[0]
    
    #<data>?
    retArray = Fontfname(readedData)
    readedData = retArray[0]
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<fontname>
#PCDATA
#@profile
def Fontname(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Fontname()\n")
    
    fontname = ""
    
    try:
        fontname = re.match(r"(\s*\w+)+\s*", readedData).group(0)
    except AttributeError as e:
        sys.stderr.write("Chyba pri <fontname>!\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
    readedData = re.sub(r"^(\s*\w+)+\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(fontname)
    return retArray

#<fontaltname>
#'{\*' \falt #PCDATA '}'
#@profile
def Fontaltname(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Fontaltname()\n")
    
    if not re.match(r"\{\\\*\s*\\fontemb", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    falt = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\falt\s*", "", readedData, 1)
    
    try:
        falt = re.match(r"[^\}]+", readedData).group(0)
        readedData = re.sub(r"^[^\}]+", "", readedData, 1)
        
        #abstrakt muze obsahovat uvozovky, nutne osetrit
        while falt[-1] == "\\":
            falt += "}"
            readedData = re.sub(r"^\}", "", readedData, 1)
            
            #teoreticky muze nastat situace \"", takze proto *
            subfalt = re.match(r"[^\}]*", readedData).group(0)
            if subfname == "":
                break
            else:
                readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                falt += subfalt
    
    except AttributeError as e:
        sys.stderr.write("Nelze precist <fontaltname>\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<fontinfo>
#<themefont>? \fN <fontfamily> \fcharsetN? \fprq? <panose>? <nontaggedname>?
#<fontemb>? \cpgN? <fontname> <fontaltname>? ';'
#@profile
def Fontinfo(readedData):
    global globPrintFunctionName
    
    fonttblItem = {}
    
    if globPrintFunctionName:
        sys.stderr.write("Fontinfo()\n")
    
    #<themefont>?
    retArray = Themefont(readedData)
    readedData = retArray[0]
    #fonttblItem = retArray[1]
    
    #\fN
    try:
        fonttblItem["f"] = re.match(r"\\f\s*(\d+)", readedData).group(1)
    except AttributeError as e:
        sys.stderr.write("Chyba pri f!\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
    
    readedData = re.sub(r"^\\f\s*(\d+)\s*", "", readedData, 1)
    
    #<fontfamily>
    retArray = Fontfamily(readedData)
    readedData = retArray[0]
    fonttblItem["fontfamily"] = retArray[1]
    
    #\fcharsetN?
    if re.match(r"\\fcharset", readedData):
        try:
            fonttblItem["fcharset"] = int(re.match(r"\\fcharset\s*(\d+)", readedData).group(1))
        except AttributeError as e:
            sys.stderr.write("Chyba pri fcharset!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        readedData = re.sub(r"^\\fcharset\s*(\d+)\s*", "", readedData, 1)
    
    #\fprq?
    if re.match(r"\\fprq", readedData):
        fonttblItem["fprq"] = True
        readedData = re.sub(r"^\\fprq\s*", "", readedData, 1)
    
    #<panose>?
    retArray = Panose(readedData)
    readedData = retArray[0]
    #fonttblItem = retArray[1]
    
    #<nontaggedname>?
    #retArray = Nontaggedname(readedData, fonttblItem)
    retArray = Nontaggedname(readedData)
    readedData = retArray[0]
    #fonttblItem = retArray[1]
    
    #<fontemb>?
    #retArray = Nontaggedname(readedData, fonttblItem)
    retArray = Fontemb(readedData)
    readedData = retArray[0]
    
    if re.match(r"\\cpg", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cpg\s*", "", readedData, 1)
        
        try:
            cpg = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <fontfname>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #<fontname>
    #retArray = Nontaggedname(readedData, fonttblItem)
    retArray = Fontname(readedData)
    readedData = retArray[0]
    fonttblItem["fontname"] = retArray[1]
    
    #<fontaltname>
    #retArray = Nontaggedname(readedData, fonttblItem)
    retArray = Fontaltname(readedData)
    readedData = retArray[0]
    
    readedData = re.sub(r"^;\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(fonttblItem)
    return retArray

#<fonttbl>?
#'{' \fonttbl (<fontinfo> | ('{' <fontinfo> '}'))+ '}'
#TODO: POZOR! Pred <fonttbl> se muze nachazet <themedata> a <colormapping>
#@profile
def Fonttbl(readedData):
    global globFonttbl
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Fonttbl()\n")
    
    bracers = False
    
    if not re.match(r"\{\\fonttbl", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\fonttbl\s*", "", readedData, 1)
    
    #<fontinfo>
    while not re.match(r"\}", readedData):
        #odstraneni nepotrebne casti
        if re.match(r"\{", readedData):
            readedData = re.sub(r"^\{\s*", "", readedData, 1)
            bracers = True
        
        retArray = Fontinfo(readedData)
        readedData = retArray[0]
        
        #ziskani polozky tabulky fontu a jeji ulozeni do tabulky
        globFonttbl.append(retArray[1].copy())
        
        if bracers:
            #odstraneni nepotrebne casti
            readedData = re.sub(r"^\}\s*", "", readedData, 1)
            bracers = False
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<filesource>
#\fvalidmac | \fvaliddos | \fvalidntfs | \fvalidhpfs | \fnetwork | \fnonfilesys
#@profile
def Filesource(readedData):
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Filesource()\n")
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^(fvalidmac|fvaliddos|fvalidntfs|fvalidhpfs|fnetwork|fnonfilesys)\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<file name>
#PCDATA
#@profile
def Filename(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Filename()\n")
    
    filename = ""
    
    try:
        filename = re.match(r"[^\}]+", readedData).group(0)
        readedData = re.sub(r"^[^\}]+", "", readedData, 1)
        
        #abstrakt muze obsahovat uvozovky, nutne osetrit
        while filename[-1] == "\\":
            filename += "}"
            readedData = re.sub(r"^\}", "", readedData, 1)
            
            #teoreticky muze nastat situace \"", takze proto *
            subfilename = re.match(r"[^\}]*", readedData).group(0)
            if subfilename == "":
                break
            else:
                readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                filename += subfilename
    
    except AttributeError as e:
        sys.stderr.write("Nelze precist <file name>\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<fileinfo>
#\file \fidN \frelativeN? \fosnumN? <filesource>+ <file name>
#@profile
def Fileinfo(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Fileinfo()\n")
    
    fileinfo = {}
    
    if not re.match(r"\\file", readedData):
        sys.stderr.write("Chyba parsovani - <fileinfo>!\n")
        sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\\file\s*", "", readedData, 1)
    
    if re.match(r"\\fid", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\fid\s*", "", readedData, 1)
        
        try:
            fid = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <fileinfo>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        fileinfo["fid"] = fid
    
    if re.match(r"\\frelative", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\frelative\s*", "", readedData, 1)
        
        try:
            frelative = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <fileinfo>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        fileinfo["frelative"] = frelative
    
    if re.match(r"\\fosnum", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\fosnum\s*", "", readedData, 1)
        
        try:
            fosnum = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <fileinfo>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        fileinfo["fosnum"] = fosnum
    
    #<filesource>+
    while re.match(r"\\(fvalidmac|fvaliddos|fvalidntfs|fvalidhpfs|fnetwork|fnonfilesys)", readedData):
        retArray = Fileinfo(readedData)
        readedData = retArray[0]
    
    #<file name>
    retArray = Filename(readedData)
    readedData = retArray[0]
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<filetbl>
#'{\*' \filetbl ('{' <fileinfo> '}')+ '}'
#@profile
def Filetbl(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Filetbl()\n")
    
    if not re.match(r"\{\\\*\s*\\filetbl", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\filetbl\s*", "", readedData, 1)
    
    #<fileinfo>
    while not re.match(r"\}", readedData):
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\{\s*", "", readedData, 1)
        
        retArray = Fileinfo(readedData)
        readedData = retArray[0]
        
        #ziskani polozky tabulky fontu a jeji ulozeni do tabulky
        #fonttbl.append(retArray[1])
        
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<themecolor>
#\cmaindarkone | \cmainlightone | \cmaindarktwo | \cmainlighttwo |
#\caccentone | \caccenttwo | \caccentthree | \caccentfour | \caccentfive |
#\caccentsix | \chyperlink | \cfollowedhyperlink | \cbackgroundone |
#\ctextone | \cbackgroundtwo | \ctexttwo
#@profile
def Themecolor(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Themecolor()\n")
    
    themecolor = ""
    
    #success = False
    
    if re.match(r"\\cmaindarkone", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cmaindarkone\s*", "", readedData, 1)
        
        themecolor= "cmaindarkone"
    
    elif re.match(r"\\cmainlightone", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cmainlightone\s*", "", readedData, 1)
        
        themecolor = "cmainlightone"
    
    elif re.match(r"\\cmaindarktwo", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cmaindarktwo\s*", "", readedData, 1)
        
        themecolor = "cmaindarktwo"
    
    elif re.match(r"\\cmainlighttwo", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cmainlighttwo\s*", "", readedData, 1)
        
        themecolor = "cmainlighttwo"
    
    elif re.match(r"\\caccentone", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\caccentone\s*", "", readedData, 1)
        
        themecolor = "caccentone"
    
    elif re.match(r"\\caccenttwo", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\caccenttwo\s*", "", readedData, 1)
        
        themecolor = "caccenttwo"
    
    elif re.match(r"\\caccentthree", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\caccentthree\s*", "", readedData, 1)
        
        themecolor = "caccentthree"
    
    elif re.match(r"\\caccentfour", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\caccentfour\s*", "", readedData, 1)
        
        themecolor = "caccentfour"
    
    elif re.match(r"\\caccentfive", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\caccentfive\s*", "", readedData, 1)
        
        themecolor = "caccentfive"
    
    elif re.match(r"\\caccentsix", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\caccentsix\s*", "", readedData, 1)
        
        themecolor = "caccentsix"
    
    elif re.match(r"\\chyperlink", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\chyperlink\s*", "", readedData, 1)
        
        themecolor = "chyperlink"
    
    elif re.match(r"\\cfollowedhyperlink", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cfollowedhyperlink\s*", "", readedData, 1)
        
        themecolor = "cfollowedhyperlink"
    
    elif re.match(r"\\cbackgroundone", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cbackgroundone\s*", "", readedData, 1)
        
        themecolor = "cbackgroundone"
    
    elif re.match(r"\\ctextone", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ctextone\s*", "", readedData, 1)
        
        themecolor = "ctextone"
    
    elif re.match(r"\\cbackgroundtwo", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cbackgroundtwo\s*", "", readedData, 1)
        
        themecolor = "cbackgroundtwo"
    
    elif re.match(r"\\ctexttwo", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ctexttwo\s*", "", readedData, 1)
        
        themecolor = "ctexttwo"
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<colordef>
#<themecolor>? & \ctintN? & \cshadeN? \redN? & \greenN? & \blueN? ';'
#@profile
def Colordef(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Colordef()\n")
    
    while re.match(r"\\(cmaindarkone|cmainlightone|cmaindarktwo|cmainlighttwo|caccentone|caccenttwo|caccentthree|caccentfour|caccentfive|caccentsix|chyperlink|cfollowedhyperlink|cbackgroundone|ctextone|cbackgroundtwo|ctexttwo|ctint|cshade|red|green|blue)", readedData):
        if re.match(r"\\(cmaindarkone|cmainlightone|cmaindarktwo|cmainlighttwo|caccentone|caccenttwo|caccentthree|caccentfour|caccentfive|caccentsix|chyperlink|cfollowedhyperlink|cbackgroundone|ctextone|cbackgroundtwo|ctexttwo)", readedData):
            retArray = Themecolor(readedData)
            readedData = retArray[0]
        
        if re.match(r"\\ctint", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\ctint\s*", "", readedData, 1)
            
            try:
                ctint = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Chyba pri <colordef>!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
            
            #fileinfo["fosnum"] = fosnum
        
        if re.match(r"\\cshade", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\cshade\s*", "", readedData, 1)
            
            try:
                cshade = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Chyba pri <colordef>!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
            
            #fileinfo["fosnum"] = fosnum
        
        if re.match(r"\\red", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\red\s*", "", readedData, 1)
            
            try:
                red = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Chyba pri <colordef>!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
            
            #fileinfo["fosnum"] = fosnum
        
        if re.match(r"\\green", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\green\s*", "", readedData, 1)
            
            try:
                green = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Chyba pri <colordef>!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
            
            #fileinfo["fosnum"] = fosnum
        
        if re.match(r"\\blue", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\blue\s*", "", readedData, 1)
            
            try:
                blue = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Chyba pri <colordef>!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
            
            #fileinfo["fosnum"] = fosnum
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^;\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<colortbl>
#'{' \colortbl <colordef>+ '}'
#@profile
def Colortbl(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Colortbl()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\colortbl", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\colortbl\s*", "", readedData, 1)
    
    #odstraneni nepotrebne casti
    #POZOR!!! Tohle neni podle specifikace, ale OCR jako prvni vlozi ';' a pak az klicova slova
    #To sice je podle specifikace mozne, protoze kazda polozka <colordef> je volitelna, jen ';'
    #je povinny. Ale to neni podle me ciste. Osetruji tedy osamoceny ';' v <colortbl>
    readedData = re.sub(r"^;\s*", "", readedData, 1)
    
    #<colordef>
    while not re.match(r"\}", readedData):        
        retArray = Colordef(readedData)
        readedData = retArray[0]
        
        #ziskani polozky tabulky fontu a jeji ulozeni do tabulky
        #fonttbl.append(retArray[1])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<styledef>
#\sN | \*\csN | \*\dsN | \*\tsN \tsrowd
#@profile
def Styledef(readedData):
    global errCode
    global globStyledef
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Styledef()\n")
    
    if re.match(r"\\s", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\s\s*", "", readedData, 1)
        
        try:
            s = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <styledef>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        globStyledef["s"] = s
    
    elif re.match(r"\\\*\\cs", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\\*\\cs\s*", "", readedData, 1)
        
        try:
            cs = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <styledef>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        globStyledef["cs"] = cs
    
    elif re.match(r"\\\*\\ds", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\\*\\ds\s*", "", readedData, 1)
        
        try:
            ds = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <styledef>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        globStyledef["ds"] = ds
    
    elif re.match(r"\\\*\\ts", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\\*\\ts\s*", "", readedData, 1)
        
        try:
            ts = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <styledef>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        globStyledef["ts"] = ts
    
    #odstraneni kl. slova
    readedData = re.sub(r"^\\tsrowd\s*", "", readedData)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<key>
#\fnN | #PCDATA
#@profile
def Key(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Key()\n")
    
    if re.match(r"\\fn", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\fn\s*", "", readedData, 1)
        
        try:
            fn = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <key>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        styledef["fn"] = fn
    
    else:
        try:
            fn = re.match(r"[^\}]+", readedData).group(0)
            readedData = re.sub(r"^[^\}]+", "", readedData, 1)
            
            #abstrakt muze obsahovat uvozovky, nutne osetrit
            while fn[-1] == "\\":
                fn += "}"
                readedData = re.sub(r"^\}", "", readedData, 1)
                
                #teoreticky muze nastat situace \"", takze proto *
                subfn = re.match(r"[^\}]*", readedData).group(0)
                if subfn == "":
                    break
                else:
                    readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                    fn += subfn
        
        except AttributeError as e:
            sys.stderr.write("Nelze precist <key>\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            print readedData
            sys.exit(errCode["parseErr"])
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<keys>
#(\shift? & \ctrl? & \alt?) <key>
#@profile
def Keys(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Keys()\n")
    
    while re.match(r"\\(shift|ctrl|alt)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(shift|ctrl|alt)\s*", "", readedData)
    
    retArray = Key(readedData)
    readedData = retArray[0]
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<keycode>
#'{' \keycode <keys> '}'
#@profile
def Keycode(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Keycode()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\keycode", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\keycode\s*", "", readedData, 1)
    
    #<keys>     
    retArray = Keys(readedData)
    readedData = retArray[0]
        
    #ziskani polozky tabulky fontu a jeji ulozeni do tabulky
    #fonttbl.append(retArray[1])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<formatting>
#TODO: Domyslet, jak to ukladat, protoze se to tyka jen <stylesheet>, ale pouziva to vsechna nastaveni
#(<brdrdef> | <parfmt> | <apoctl> | <tabdef> | <shading> | <chrfmt>)+
#@profile
def Formatting(readedData):
    global errCode
    global globPrintFunctionName
    
    #odstraneni hodnoty kl. slova
    #readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    if globPrintFunctionName:
        sys.stderr.write("Formatting()\n")
    
    hit = True
    while hit and re.match(r"\\", readedData):
        try:
            formatting = re.match(r"\\([a-zA-Z]+)", readedData).group(1)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <formatting>!\n")
            sys.stderr.write(readedData[:128] + "\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        sys.stderr.write(formatting + "\n")
        
        #<brdrdef>
        if globBrdrdef.has_key(formatting):
            sys.stderr.write("brdrdef Keyword konec\n")
            sys.exit(0)
            retArray = Brdrdef(readedData)
            readedData = retArray[0]
        
        #<parfmt>
        elif globParfmt.has_key(formatting):
            #sys.stderr.write("parfmt Keyword konec\n")
            #sys.exit(0)
            sys.stderr.write("parfmt Keyword\n")
            retArray = Parfmt(readedData)
            readedData = retArray[0]
        
        #<apoctl>
        elif globApoctl.has_key(formatting):
            sys.stderr.write("apoctl Keyword konec\n")
            sys.exit(0)
            retArray = Apoctl(readedData)
            readedData = retArray[0]
        
        #<tabdef>
        elif globTabdef.has_key(formatting):
            sys.stderr.write("tabdef Keyword konec\n")
            sys.exit(0)
            retArray = Tabdef(readedData)
            readedData = retArray[0]
        
        #<shading>
        elif globShading.has_key(formatting):
            #sys.stderr.write("shading Keyword konec\n")
            #sys.exit(0)
            retArray = Shading(readedData)
            readedData = retArray[0]
        
        #<chrfmt>
        elif globChrfmt.has_key(formatting):
            #sys.stderr.write(readedData[:128] + "\n")
            #sys.stderr.write("chrfmt Keyword konec\n")
            #sys.exit(0)
            sys.stderr.write("chrfmt Keyword\n")
            retArray = Chrfmt(readedData)
            readedData = retArray[0]
        
        else:
            hit = False
        
        #else:
        #    sys.stderr.write("Chyba parsovani - <formatting>!\n")
        #    sys.stderr.write(readedData[:128] + "\n")
        #    sys.exit(errCode["parseErr"])
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<stylename>
#\lsdpriorityN ? \lsdunhideusedN ? \lsdsemihiddenN ? \lsdqformatN ? \lsdlockedN ?
#PCDATA
#@profile
def Stylename(readedData):
    global errCode
    global globStylename
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Stylename()\n")
    
    if re.match(r"\\lsdpriority", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\lsdpriority\s*", "", readedData, 1)
        
        try:
            lsdpriority = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <stylename>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        globStylename["lsdpriority"] = lsdpriority
    
    if re.match(r"\\lsdunhideused", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\lsdunhideused\s*", "", readedData, 1)
        
        try:
            lsdunhideused = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <stylename>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        globStylename["lsdunhideused"] = lsdunhideused
    
    if re.match(r"\\lsdsemihidden", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\lsdsemihidden\s*", "", readedData, 1)
        
        try:
            lsdsemihidden = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <stylename>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        globStylename["lsdsemihidden"] = lsdsemihidden
    
    if re.match(r"\\lsdqformat", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\lsdqformat\s*", "", readedData, 1)
        
        try:
            lsdqformat = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <stylename>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        globStylename["lsdqformat"] = lsdqformat
    
    if re.match(r"\\lsdlocked", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\lsdlocked\s*", "", readedData, 1)
        
        try:
            lsdlocked = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <stylename>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        globStylename["lsdlocked"] = lsdlocked
    
    try:
        stylename = re.match(r"[^\;]+", readedData).group(0)
    except AttributeError as e:
        sys.stderr.write("Chyba pri <stylename>!\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
    
    readedData = re.sub(r"^[^\;]+\s*", "", readedData, 1)
    
    globStylename["stylename"] = stylename
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<style>
#'{' <styledef>? <keycode>? <formatting> \additive? \sbasedonN? \snextN? \sautoupd?
#\slinkN? \sqformat? \spriorityN? \sunhideusedN? \slocked? \shidden? \ssemihiddenN?
#\spersonal? \scompose? \sreply? \styrsidN? <stylename>? ';}'
#@profile
def Style(readedData):
    global errCode
    global globChr
    global globPara
    global globForApoctl
    global globForBrdrdef
    global globForShading
    global globForTabdef
    global globStylename
    global globStyledef
    global Stylesheet
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Style()\n")
    
    style = {}
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\s*", "", readedData, 1)
    
    #<styledef>?
    if re.match(r"\\(s|\*\\cs|\*\\ds|\*\\ts)", readedData):
        retArray = Styledef(readedData)
        readedData = retArray[0]
    
    #<keycode>?
    if re.match(r"\\{\s*\\keycode", readedData):
        retArray = Keycode(readedData)
        readedData = retArray[0]
    
    #TODO: Podle specifikace ma byt additive az za <formatting>, ale OCR jej dava pred
    if re.match(r"\\additive", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\additive\s*", "", readedData, 1)
        
        style["additive"] = ""
    
    #<formatting>
    retArray = Formatting(readedData)
    readedData = retArray[0]
    
    if re.match(r"\\additive", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\additive\s*", "", readedData, 1)
        
        style["additive"] = ""
    
    if re.match(r"\\sbasedon", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sbasedon\s*", "", readedData, 1)
        
        try:
            sbasedon = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <style>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        style["sbasedon"] = sbasedon
    
    if re.match(r"\\snext", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\snext\s*", "", readedData, 1)
        
        try:
            snext = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <style>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        style["snext"] = snext
    
    if re.match(r"\\sautoupd", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sautoupd\s*", "", readedData, 1)
        
        style["sautoupd"] = ""
    
    if re.match(r"\\slink", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\slink\s*", "", readedData, 1)
        
        try:
            slink = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <style>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        style["slink"] = slink
    
    if re.match(r"\\sqformat", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sqformat\s*", "", readedData, 1)
        
        style["sqformat"] = ""
    
    if re.match(r"\\spriority", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\spriority\s*", "", readedData, 1)
        
        try:
            spriority = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <style>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        style["spriority"] = spriority
    
    if re.match(r"\\sunhideused", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sunhideused\s*", "", readedData, 1)
        
        try:
            sunhideused = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <style>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        style["sunhideused"] = sunhideused
    
    if re.match(r"\\slocked", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\slocked\s*", "", readedData, 1)
        
        style["slocked"] = ""
    
    if re.match(r"\\shidden", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\shidden\s*", "", readedData, 1)
        
        style["shidden"] = ""
    
    if re.match(r"\\ssemihidden", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ssemihidden\s*", "", readedData, 1)
        
        try:
            ssemihidden = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <style>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        style["ssemihidden"] = ssemihidden
    
    if re.match(r"\\spersonal", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\spersonal\s*", "", readedData, 1)
        
        style["spersonal"] = ""
    
    if re.match(r"\\scompose", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\scompose\s*", "", readedData, 1)
        
        style["scompose"] = ""
    
    if re.match(r"\\sreply", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sreply\s*", "", readedData, 1)
        
        style["sreply"] = ""
    
    if re.match(r"\\styrsid", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\styrsid\s*", "", readedData, 1)
        
        try:
            styrsid = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Chyba pri <style>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        style["styrsid"] = styrsid
    
    # muze dojit k situaci, kdy je hned jako pocatecni znak nazvu stylu nektery
    # ze znaku rozsirene asci
    if re.match(r"(\w+)|(\\\')", readedData):
        retArray = Stylename(readedData)
        readedData = retArray[0]
    elif re.match(r"\\", readedData):
        sys.stderr.write("Style() - chyba parsovani!\nKl.nerozpoznano\n")
        sys.stderr.write(readedData[:128] + "\n")
        sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^;\}\s*", "", readedData, 1)
    
    style["apoctl"] = globForApoctl.copy()
    style["brdrdef"] = globForBrdrdef.copy()
    style["chrfmt"] = globChr.copy()
    style["parfmt"] = globPara.copy()
    style["shading"] = globForShading.copy()
    style["tabdef"] = globForTabdef.copy()
    style["stylename"] = globStylename.copy()
    style["styledef"] = globStyledef.copy()
    
    globStylesheet.append(style.copy())
    
    style["apoctl"] = {}
    style["brdrdef"] = {}
    style["chrfmt"] = {}
    style["parfmt"] = {}
    style["shading"] = {}
    style["tabdef"] = {}
    style["stylename"] = {}
    style["styledef"] = {}
    
    #print "Stylesheet"
    #print globStylesheet
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<stylesheet>
#'{' \stylesheet <style>+ '}'
#@profile
def Stylesheet(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Stylesheet()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\stylesheet", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\stylesheet\s*", "", readedData, 1)
    
    #<style>
    while not re.match(r"\}", readedData):        
        retArray = Style(readedData)
        readedData = retArray[0]
        
        #ziskani polozky tabulky fontu a jeji ulozeni do tabulky
        #fonttbl.append(retArray[1])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<stylenames>
#<stylename> ';'
#@profile
def Stylenames(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Stylenames()\n")
    
    #<stylename>
    retArray = Stylename(readedData)
    readedData = retArray[0]
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^;\s*", "", readedData, 1)
    
    sys.stderr.write(readedData[:128] + "\n")
    sys.stderr.write("<stylenames> konec\n")
    sys.exit(0)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<exceptions>
#'{' \lsdlockedexcept <stylenames>+ '}'
#@profile
def Exceptions(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Exceptions()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\lsdlockedexcept", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\lsdlockedexcept\s*", "", readedData, 1)
    
    #<stylenames>
    while not re.match(r"\}", readedData):        
        retArray = Stylenames(readedData)
        readedData = retArray[0]
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<stylerestrictions>
#'{\*' \latentstyles \lsdstimaxN \lsdlockeddefN \lsdsemihiddendefN
#\lsdunhideuseddefN \lsdqformatdefN \lsdprioritydefN <exceptions>? '}'
#@profile
def Stylerestrictions(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Stylerestrictions()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\\*\s*\\latentstyles", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\latentstyles\s*", "", readedData, 1)
    
    if re.match(r"\\lsdstimax", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\lsdstimax\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            lsdstimax = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \lsdstimax z <stylerestrictions>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        #globPara["lsdstimax"] = posx
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    if re.match(r"\\lsdlockeddef", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\lsdlockeddef\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            lsdlockeddef = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \lsdlockeddef z <stylerestrictions>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        #globPara["lsdstimax"] = posx
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    if re.match(r"\\lsdsemihiddendef", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\lsdsemihiddendef\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            lsdsemihiddendef = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \lsdsemihiddendef z <stylerestrictions>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        #globPara["lsdstimax"] = posx
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    if re.match(r"\\lsdunhideuseddef", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\lsdunhideuseddef\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            lsdunhideuseddef = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \lsdunhideuseddef z <stylerestrictions>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        #globPara["lsdstimax"] = posx
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    if re.match(r"\\lsdqformatdef", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\lsdqformatdef\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            lsdqformatdef = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \lsdqformatdef z <stylerestrictions>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        #globPara["lsdstimax"] = posx
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    if re.match(r"\\lsdprioritydef", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\lsdprioritydef\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            lsdprioritydef = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \lsdprioritydef z <stylerestrictions>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        #globPara["lsdstimax"] = posx
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    #<exceptions>?
    if re.match(r"\{\\lsdlockedexcept", readedData):     
        retArray = Exceptions(readedData)
        readedData = retArray[0]
        
        #ziskani polozky tabulky fontu a jeji ulozeni do tabulky
        #fonttbl.append(retArray[1])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<rsidtable>
#'{\*' \rsidtbl \rsidN+ '}'
#@profile
def Rsidtable(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Rsidtable()\n")
    
    rsid = []
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\\*\s*\\rsidtbl", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\rsidtbl\s*", "", readedData, 1)
    
    #\rsidN+
    if re.match(r"\\rsid", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\rsid\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            rsid.append(re.match(r"(\-)?\d+", readedData).group(0))
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \rsid z <rsidtable>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        #globPara["lsdstimax"] = posx
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<mathprops>
#'{\*' \mmathPr <mathPr>* '}'
#@profile
def Mathprops(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Mathprops()\n")
    
    rsid = []
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\\*\s*\\mmathPr", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\mmathPr\s*", "", readedData, 1)
    
    sys.stderr.write("<mathprops> neimplementovano!!!\n")
    sys.exit(errCode["notImplemented"])
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<generator>
#'{\*' \generator <name> ';}'
#@profile
def Generator(readedData):
    global errCode
    
    rsid = []
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\\*\s*\\generator", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\generator\s*", "", readedData, 1)
    
    sys.stderr.write("<generator> neimplementovano!!!\n")
    sys.exit(errCode["notImplemented"])
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#Tato fce je improvizace. Vychazim z toho, jak je to podle OCR systemu
#@profile
def Defchp(readedData):
    global errCode
    global globDefchp
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Defchp()\n")
    
    if not re.match(r"\{\\\*\s*\\defchp", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\defchp\s*", "", readedData, 1)
    
    if re.match(r"\\fs", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\fs\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            fs = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \fs z Defchp()!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globDefchp["fs"] = fs
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    if re.match(r"\\afs", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\afs\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            afs = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \afs z Defchp()!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globDefchp["afs"] = afs
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    globDefchp["note"] = "loch,hich,dbch obsahuji hodnoty k nim pridruzenym kl. slov af"
    
    #POZOR!!!! k loch, hich atd vzdy patri af!
    if re.match(r"\\loch", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\loch\s*", "", readedData, 1)
    
        if re.match(r"\\af", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\af\s*", "", readedData, 1)
            
            #ziskani hodnoty kl. slova
            try:
                af = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Nelze nacist hodnotu keyword \af z Defchp()!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                sys.exit(errCode["parseErr"])
            
            #ulozeni hodnoty kl. slova
            globDefchp["loch"] = af
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    if re.match(r"\\hich", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\hich\s*", "", readedData, 1)
        
        if re.match(r"\\af", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\af\s*", "", readedData, 1)
            
            #ziskani hodnoty kl. slova
            try:
                af = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Nelze nacist hodnotu keyword \af z Defchp()!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                sys.exit(errCode["parseErr"])
            
            #ulozeni hodnoty kl. slova
            globDefchp["hich"] = af
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    if re.match(r"\\dbch", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\dbch\s*", "", readedData, 1)
        
        if re.match(r"\\af", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\af\s*", "", readedData, 1)
            
            #ziskani hodnoty kl. slova
            try:
                af = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Nelze nacist hodnotu keyword \af z Defchp()!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                sys.exit(errCode["parseErr"])
            
            #ulozeni hodnoty kl. slova
            globDefchp["dbch"] = af
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#Tato fce je improvizace. Vychazim z toho, jak je to podle OCR systemu
#@profile
def Defpap(readedData):
    global errCode
    global globDefpap
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Defpap()\n")
    
    if not re.match(r"\{\\\*\s*\\defpap", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\defpap\s*", "", readedData, 1)
    
    if re.match(r"\\aspalpha", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\aspalpha\s*", "", readedData, 1)
        
        globDefpap["aspalpha"] = ""
    
    if re.match(r"\\aspnum", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\aspnum\s*", "", readedData, 1)
        
        globDefpap["aspnum"] = ""
    
    if re.match(r"\\faauto", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\faauto\s*", "", readedData, 1)
        
        globDefpap["faauto"] = ""
    
    if re.match(r"\\adjustright", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\adjustright\s*", "", readedData, 1)
        
        globDefpap["adjustright"] = ""
    
    if re.match(r"\\cgrid", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cgrid\s*", "", readedData, 1)
        
        globDefpap["cgrid"] = ""
    
    if re.match(r"\\li", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\li\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            li = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \li z Defpap()!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globDefpap["li"] = li
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    if re.match(r"\\ri", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ri\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            ri = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \ri z Defpap()!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globDefpap["ri"] = ri
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    if re.match(r"\\ltrpar", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ltrpar\s*", "", readedData, 1)
        
        globDefpap["ltrpar"] = ""
    
    if re.match(r"\\ql", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ql\s*", "", readedData, 1)
        
        globDefpap["ql"] = ""
    
    if re.match(r"\\fi", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\fi\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            fi = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \fi z Defpap()!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globDefpap["fi"] = fi
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    if re.match(r"\\sb", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sb\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            sb = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \sb z Defpap()!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globDefpap["sb"] = sb
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    if re.match(r"\\sa", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sa\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            sa = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \sa z Defpap()!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globDefpap["sa"] = sa
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    if re.match(r"\\sl", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sl\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            sl = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \sl z Defpap()!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globDefpap["sl"] = sl
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    if re.match(r"\\slmult", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\slmult\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            slmult = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \slmult z Defpap()!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globDefpap["slmult"] = slmult
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<listpicture>
#'{\*' \listpicture <shppictlist> '}'
#@profile
def Listpicture(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Listpicture()\n")
    
    if not re.match(r"\{\\\*\s*\\listpicture", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\listpicture\s*", "", readedData, 1)
    
    sys.stderr.write("<listpicture> je treba doimplementovat\n")
    sys.exit(errCode["notImplemented"])
    
    #<shppictlist>
    retArray = Shppictlist(readedData)
    readedData = retArray[0]
    
    #TODO: Zde pokracovat!!!

#<number>
#\levelnfcN | \levelnfcnN | (\levelnfcN & \levelnfcnN)
#@profile
def Number(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Number()\n")
    
    success = True
    
    if re.match(r"\\(levelnfc|levelnfcn|levelnfc)", readedData):
        readedData = re.sub(r"^\\(levelnfc|levelnfcn|levelnfc)\s*", "", readedData, 1)
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<justification>
#\leveljcN | \leveljcnN | (\leveljcN & \leveljcnN)
#@profile
def Justification(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Justification()\n")
    
    success = True
    
    if re.match(r"\\(leveljc|leveljcn)", readedData):
        readedData = re.sub(r"^\\((leveljc|leveljcn)\s*", "", readedData, 1)
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<listlevel>
#'{' \listlevel <number> <justification> & \levelfollowN & \levelstartatN & \lvltentative?
#(\leveloldN & \levelprevN? & \levelprevspaceN? & \levelspaceN? & \levelindentN?)? &
#<leveltext> & <levelnumbers> & \levellegalN? & \levelnorestartN? & <chrfmt>? &
#\levelpictureN & \liN? & \fiN? & (\jclisttab \txN)? & \linN? '}'
#@profile
def Listlevel(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Listlevel()\n")
    
    if not re.match(r"\{\\listlevel", readedData):
        success = False
        
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    else:
        success = True
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\listlevel\s*", "", readedData, 1)
    
    #<number>+
    #hitNum = True
    #while hitNum:
    #    retArray = Number(readedData)
    #    readedData = retArray[0]
    #    hitNum = retArray[1]
    
    hitAll = True
    while hitAll:      
        #<justification>+
        #hitJust = True
        #while hitJust:
        #    retArray = Justification(readedData)
        #    readedData = retArray[0]
        #    hitJust = retArray[1]
        #    
        #    if hitJust:
        #        hitAll = True
        
        #hitKeys = True
        #while hitKeys:
        #    hitKeys = False
        #    
        #    if re.match(r"\\[a-zA-Z]+", readedData):
        #        readedData = re.sub(r"^\\[a-zA-Z]+\s*", "", readedData, 1)
        #        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        #        
        #        hitKeys = True
        
        #TODO: Jelikoz toto neni pro klasifikator vubec dulezite, proste vsechno odstranuji
        if re.match(r"\\[a-zA-Z]+", readedData):
            readedData = re.sub(r"^\\[a-zA-Z]+\s*", "", readedData, 1)
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
            
            hitAll = True
        
        #<leveltext>
        elif re.match(r"\{\\leveltext", readedData):
            readedData = re.sub(r"^\{\\leveltext\s*", "", readedData, 1)
            readedData = re.sub(r"^[^\}]+\s*", "", readedData, 1)
            readedData = re.sub(r"^\}\s*", "", readedData, 1)
            
            hitAll = True
        
        #<levelnumbers>
        elif re.match(r"\{\\levelnumbers", readedData):
            readedData = re.sub(r"^\{\\levelnumbers\s*", "", readedData, 1)
            readedData = re.sub(r"^[^\}]+\s*", "", readedData, 1)
            readedData = re.sub(r"^\}\s*", "", readedData, 1)
            
            hitAll = True
        
        else:
            hitAll = False
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<list>
#\list \listemplateid & (\listsimple | \listhybrid)? & <listlevel>+ & \listrestarthdn &
#\listidN & (\listname #PCDATA ';') \liststyleidN? \liststylename?
#@profile
def List(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("List()\n")
    
    bracers = False
    
    if not re.match(r"(\{)?\\list", readedData):
        success = False
        
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    else:
        success = True
    
    if re.match(r"\{", readedData):
        bracers = True
        
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\{\s*", "", readedData, 1)
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\\list\s*", "", readedData, 1)
    
    hitList = True
    while hitList:      
        if re.match(r"\\listtemplateid", readedData):
            readedData = re.sub(r"^\\listtemplateid\s*", "", readedData, 1)
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
            
            hitList = True
        
        elif re.match(r"\\(listsimple|listhybrid)", readedData):
            readedData = re.sub(r"^\\(listsimple|listhybrid)\s*", "", readedData, 1)
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
            
            hitList = True
        
        elif re.match(r"\{\s*\\listlevel", readedData):
            hitListLevel = True
            while hitListLevel:
                retArray = Listlevel(readedData)
                readedData = retArray[0]
                hitListLevel = retArray[1]
                
                if hitListLevel:
                    hitList = True
        
        elif re.match(r"\\listrestarthdn", readedData):
            readedData = re.sub(r"^\\listrestarthdn\s*", "", readedData, 1)
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
            
            hitList = True
        
        elif re.match(r"\\listid", readedData):
            readedData = re.sub(r"^\\listid\s*", "", readedData, 1)
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
            
            hitList = True
        
        elif re.match(r"(\{)?\\listname", readedData):
            bracersListName = False
            if re.match(r"\{", readedData):
                readedData = re.sub(r"^\{\s*", "", readedData, 1)
                
                bracersListName = True
            
            readedData = re.sub(r"^\\listname\s*", "", readedData, 1)
            readedData = re.sub(r"^[^\;]+\s*", "", readedData, 1)
            readedData = re.sub(r"^\;\s*", "", readedData, 1)
            
            if bracersListName:
                readedData = re.sub(r"^\}\s*", "", readedData, 1)
            
            hitList = True
        
        elif re.match(r"\\liststyleid", readedData):
            readedData = re.sub(r"^\\liststyleid\s*", "", readedData, 1)
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
            
            hitList = True
        
        elif re.match(r"\\liststylename", readedData):
            readedData = re.sub(r"^\\liststylename\s*", "", readedData, 1)
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
            
            hitList = True
        
        else:
            hitList = False
    
    if bracers:
        readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<listtable>
#'{\*' \listtable <listpicture>? <list>+ '}'
#@profile
def Listtable(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Listtable()\n")
    
    if not re.match(r"\{\\\*\s*\\listtable", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\listtable\s*", "", readedData, 1)
    
    #<listpicture>?
    retArray = Listpicture(readedData)
    readedData = retArray[0]
    
    #<list>+
    hit = True
    while hit:
        retArray = List(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<listoverride>
#'{' \listoverride & \listidN & \listoverridecountN & \lsN <lfolevel>? '}'
#@profile
def Listoverride(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Listoverride()\n")
    
    if not re.match(r"\{\\listoverride", readedData):
        success = False
        
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    success = True
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\s*", "", readedData, 1)
    
    #TODO: Pripadne doimplementovat
    cnt = 0
    while not re.match(r"\}", readedData):
        cnt += 1
        readedData = re.sub(r"^\\[a-zA-Z]+\s*", "", readedData, 1)
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData, 1)
        
        if cnt > 50:
            sys.stderr.write(readedData[:128] + "\n")
            sys.stderr.write("Listoverride() potrebuje doimplementovat\n")
            sys.exit(errCode["notImplemented"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<listoverridetable>
#'{\*' \listoverridetable <listoverride>+ '}'
#@profile
def Listoverridetable(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Listoverridetable()\n")
    
    if not re.match(r"\{\\\*\s*\\listoverridetable", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\listoverridetable\s*", "", readedData, 1)
    
    hit = True
    while hit:
        retArray = Listoverride(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<header>
#\rtf1 \fbidis? <character set> <from>? <deffont> <deflang> <fonttbl>? <filetbl>?
#<colortbl>? <stylesheet>? <stylerestrictions>? <listtables>? <revtbl>? <rsidtable>?
#<mathprops>? <generator>?
#TODO: POZOR!!! Mezi header castmi muze byt defaultni nastaveni dokumentu!
#@profile
def Header(readedData):
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Header()\n")
    
    if not re.match(r"\\rtf",  readedData):
        sys.stderr.write("This file is not in RTF format\n")
        sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\\rtf\d\s*(\\fbidis)?\s*", "", readedData, 1)
    
    #<character set>
    retArray = CharacterSet(readedData)
    readedData = retArray[0]
    
    #<from>?
    retArray = From(readedData)
    readedData = retArray[0]
    
    #<deffont>
    retArray = Deffont(readedData)
    readedData = retArray[0]
    
    #<deflang>
    retArray = Deflang(readedData)
    readedData = retArray[0]
    
    #Pozor!!! Tohle neni podle specifikace v 1.9.1, nicmene OCR system nejdrive ulozi <deflang> a az pote <deffont>
    #<deffont>
    retArray = Deffont(readedData)
    readedData = retArray[0]
    
    #<fonttbl>?
    retArray = Fonttbl(readedData)
    readedData = retArray[0]
    
    #<filetbl>?
    retArray = Filetbl(readedData)
    readedData = retArray[0]
    
    #<colortbl>?
    retArray = Colortbl(readedData)
    readedData = retArray[0]
    
    #POZOR!!! Specifikace rika, ze se kdekoli v header mohou nachazet nastaveni znaku a odstavcu, OCR to uklada zde,
    #proto i implementuji zde. I ve specifikaci to poukazuje na toto misto
    retArray = Defchp(readedData)
    readedData = retArray[0]
    
    retArray = Defpap(readedData)
    readedData = retArray[0]
    
    #<stylesheet>?
    retArray = Stylesheet(readedData)
    readedData = retArray[0]
    
    #<stylerestrictions>?
    retArray = Stylerestrictions(readedData)
    readedData = retArray[0]
    
    #<listtable>?
    retArray = Listtable(readedData)
    readedData = retArray[0]
    
    #<listoverridetable>
    retArray = Listoverridetable(readedData)
    readedData = retArray[0]
    
    #sys.stderr.write(readedData[:128] + "\n")
    #sys.stderr.write("<header> konec\n")
    #sys.exit(errCode["parseErr"])
    
    #<revtbl>?
    #Neni uvedeno ve specifikaci
    #retArray = Revtbl(readedData)
    #readedData = retArray[0]
    
    #<rsidtable>?
    retArray = Rsidtable(readedData)
    readedData = retArray[0]
    
    #<mathprops>?
    retArray =Mathprops(readedData)
    readedData = retArray[0]
    
    #<generator>?
    retArray = Generator(readedData)
    readedData = retArray[0]
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<title>
#'{' \title #PCDATA '}'
#@profile
def Title(readedData):
    global errCode
    global globTitle
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Title()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\title", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    title = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\title\s*", "", readedData, 1)
    
    if re.match(r"\}", readedData):
        title = ""
    
    else:
        try:
            title = re.match(r"[^\}]+", readedData).group(0)
            readedData = re.sub(r"^[^\}]+", "", readedData, 1)
            
            #abstrakt muze obsahovat uvozovky, nutne osetrit
            while title[-1] == "\\":
                title += "}"
                readedData = re.sub(r"^\}", "", readedData, 1)
                
                #teoreticky muze nastat situace \"", takze proto *
                subtitle = re.match(r"[^\}]*", readedData).group(0)
                if subtitle == "":
                    break
                else:
                    readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                    title += subtitle
        
        except AttributeError as e:
            sys.stderr.write("Nelze precist <title>\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            print readedData
            sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    globTitle = title
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<subject>
#'{' \subject #PCDATA '}'
#@profile
def Subject(readedData):
    global errCode
    global globSubject
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Subject()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\subject", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    subject = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\subject\s*", "", readedData, 1)
    
    if re.match(r"\}", readedData):
        subject = ""
    
    else:
        try:
            subject = re.match(r"[^\}]+", readedData).group(0)
            readedData = re.sub(r"^[^\}]+", "", readedData, 1)
            
            #abstrakt muze obsahovat uvozovky, nutne osetrit
            while subject[-1] == "\\":
                subject += "}"
                readedData = re.sub(r"^\}", "", readedData, 1)
                
                #teoreticky muze nastat situace \"", takze proto *
                subsubject = re.match(r"[^\}]*", readedData).group(0)
                if subsubject == "":
                    break
                else:
                    readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                    subject += subsubject
        
        except AttributeError as e:
            sys.stderr.write("Nelze precist <subject>\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            print readedData
            sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    globSubject = subject
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<author>
#'{' \author #PCDATA '}'
#@profile
def Author(readedData):
    global errCode
    global globAuthor
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Author()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\author", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    author = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\author\s*", "", readedData, 1)
    
    if re.match(r"\}", readedData):
        author = ""
    
    else:
        try:
            author = re.match(r"[^\}]+", readedData).group(0)
            readedData = re.sub(r"^[^\}]+", "", readedData, 1)
            
            #abstrakt muze obsahovat uvozovky, nutne osetrit
            while author[-1] == "\\":
                author += "}"
                readedData = re.sub(r"^\}", "", readedData, 1)
                
                #teoreticky muze nastat situace \"", takze proto *
                subauthor = re.match(r"[^\}]*", readedData).group(0)
                if subauthor == "":
                    break
                else:
                    readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                    author += subauthor
        
        except AttributeError as e:
            sys.stderr.write("Nelze precist <author>\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            print readedData
            sys.exit(errCode["parseErr"])
    
    globAuthor = author
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<manager>
#'{' \manager #PCDATA '}'
#@profile
def Manager(readedData):
    global errCode
    global globManager
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Manager()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\manager", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    manager = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\manager\s*", "", readedData, 1)
    
    if re.match(r"\}", readedData):
        manager = ""
    
    else:
        try:
            manager = re.match(r"[^\}]+", readedData).group(0)
            readedData = re.sub(r"^[^\}]+", "", readedData, 1)
            
            #abstrakt muze obsahovat uvozovky, nutne osetrit
            while manager[-1] == "\\":
                manager += "}"
                readedData = re.sub(r"^\}", "", readedData, 1)
                
                #teoreticky muze nastat situace \"", takze proto *
                submanager = re.match(r"[^\}]*", readedData).group(0)
                if submanager == "":
                    break
                else:
                    readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                    manager += submanager
        
        except AttributeError as e:
            sys.stderr.write("Nelze precist <manager>\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            print readedData
            sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    globManager = manager
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<company>
#'{' \company #PCDATA '}'
#@profile
def Company(readedData):
    global errCode
    global globCompany
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Company()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\company", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    company = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\company\s*", "", readedData, 1)
    
    if re.match(r"\}", readedData):
        company = ""
    
    else:
        try:
            company = re.match(r"[^\}]+", readedData).group(0)
            readedData = re.sub(r"^[^\}]+", "", readedData, 1)
            
            #abstrakt muze obsahovat uvozovky, nutne osetrit
            while company[-1] == "\\":
                company += "}"
                readedData = re.sub(r"^\}", "", readedData, 1)
                
                #teoreticky muze nastat situace \"", takze proto *
                subcompany = re.match(r"[^\}]*", readedData).group(0)
                if subcompany == "":
                    break
                else:
                    readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                    company += subcompany
        
        except AttributeError as e:
            sys.stderr.write("Nelze precist <company>\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            print readedData
            sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    globCompany = company
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<operator>
#'{' \operator #PCDATA '}'
#@profile
def Operator(readedData):
    global errCode
    global globOperator
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Operator()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\operator", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    operator = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\operator\s*", "", readedData, 1)
    
    if re.match(r"\}", readedData):
        operator = ""
    
    else:
        try:
            operator = re.match(r"[^\}]+", readedData).group(0)
            readedData = re.sub(r"^[^\}]+", "", readedData, 1)
            
            #abstrakt muze obsahovat uvozovky, nutne osetrit
            while operator[-1] == "\\":
                operator += "}"
                readedData = re.sub(r"^\}", "", readedData, 1)
                
                #teoreticky muze nastat situace \"", takze proto *
                suboperator = re.match(r"[^\}]*", readedData).group(0)
                if suboperator == "":
                    break
                else:
                    readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                    operator += suboperator
        
        except AttributeError as e:
            sys.stderr.write("Nelze precist <operator>\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            print readedData
            sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    globOperator = operator
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<category>
#'{' \category #PCDATA '}'
#@profile
def Category(readedData):
    global errCode
    global globCategory
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Category()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\category", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    category = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\category\s*", "", readedData, 1)
    
    if re.match(r"\}", readedData):
        category = ""
    
    else:
        try:
            category = re.match(r"[^\}]+", readedData).group(0)
            readedData = re.sub(r"^[^\}]+", "", readedData, 1)
            
            #abstrakt muze obsahovat uvozovky, nutne osetrit
            while category[-1] == "\\":
                category += "}"
                readedData = re.sub(r"^\}", "", readedData, 1)
                
                #teoreticky muze nastat situace \"", takze proto *
                subcategory = re.match(r"[^\}]*", readedData).group(0)
                if subcategory == "":
                    break
                else:
                    readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                    category += subcategory
        
        except AttributeError as e:
            sys.stderr.write("Nelze precist <category>\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            print readedData
            sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    globCategory = category
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<keywords>
#'{' \keywords #PCDATA '}'
#@profile
def Keywords(readedData):
    global errCode
    global globKeywords
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Keywords()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\keywords", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    keywords = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\keywords\s*", "", readedData, 1)
    
    if re.match(r"\}", readedData):
        keywords = ""
    
    else:
        try:
            keywords = re.match(r"[^\}]+", readedData).group(0)
            readedData = re.sub(r"^[^\}]+", "", readedData, 1)
            
            #abstrakt muze obsahovat uvozovky, nutne osetrit
            while keywords[-1] == "\\":
                keywords += "}"
                readedData = re.sub(r"^\}", "", readedData, 1)
                
                #teoreticky muze nastat situace \"", takze proto *
                subkeywords= re.match(r"[^\}]*", readedData).group(0)
                if subkeywords == "":
                    break
                else:
                    readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                    keywords += subkeywords
        
        except AttributeError as e:
            sys.stderr.write("Nelze precist <keywords>\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            print readedData
            sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    globKeywords = keywords
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<comment>
#'{' \comment #PCDATA '}'
#@profile
def Comment(readedData):
    global errCode
    global globComment
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Comment()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\comment", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    comment = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\comment\s*", "", readedData, 1)
    
    if re.match(r"\}", readedData):
        comment = ""
    
    else:
        try:
            comment = re.match(r"[^\}]+", readedData).group(0)
            readedData = re.sub(r"^[^\}]+", "", readedData, 1)
            
            #abstrakt muze obsahovat uvozovky, nutne osetrit
            while comment[-1] == "\\":
                comment += "}"
                readedData = re.sub(r"^\}", "", readedData, 1)
                
                #teoreticky muze nastat situace \"", takze proto *
                subcomment = re.match(r"[^\}]*", readedData).group(0)
                if subcomment == "":
                    break
                else:
                    readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                    comment += subcomment
        
        except AttributeError as e:
            sys.stderr.write("Nelze precist <comment>\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            print readedData
            sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    globComment = comment
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<doccomm>
#'{' \doccomm #PCDATA '}'
#@profile
def Doccomm(readedData):
    global errCode
    global globDoccomm
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Doccomm()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\doccomm", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    doccomm = ""
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\doccomm\s*", "", readedData, 1)
    
    if re.match(r"\}", readedData):
        doccomm = ""
    
    else:
        try:
            doccomm = re.match(r"[^\}]+", readedData).group(0)
            readedData = re.sub(r"^[^\}]+", "", readedData, 1)
            
            #abstrakt muze obsahovat uvozovky, nutne osetrit
            while doccomm[-1] == "\\":
                doccomm += "}"
                readedData = re.sub(r"^\}", "", readedData, 1)
                
                #teoreticky muze nastat situace \"", takze proto *
                subdoccomm = re.match(r"[^\}]*", readedData).group(0)
                if subdoccomm == "":
                    break
                else:
                    readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                    doccomm += subdoccomm
        
        except AttributeError as e:
            sys.stderr.write("Nelze precist <doccomm>\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            print readedData
            sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    globDoccomm = doccomm
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<time>
#\yrN? \moN? \dyN? \hrN? \minN? \secN?
#@profile
def Time(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Time()\n")
    
    time = {}
    
    if re.match(r"\\yr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\yr\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            yr = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \yr z <time>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        time["yr"] = yr
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    if re.match(r"\\mo", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\mo\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            mo = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \mo z <time>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        time["mo"] = mo
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    if re.match(r"\\dy", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\dy\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            dy = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \dy z <time>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        time["dy"] = dy
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    if re.match(r"\\hr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\hr\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            hr = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \hr z <time>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        time["hr"] = hr
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    if re.match(r"\\min", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\min\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            min = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \min z <time>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        time["min"] = min
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    if re.match(r"\\sec", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sec\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            sec = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \sec z <time>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        time["sec"] = sec
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(time)
    return retArray

#<creatim>
#'{' \creatim <time> '}'
#@profile
def Creatim(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Creatim()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\creatim", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\creatim\s*", "", readedData, 1)
    
    #<time>
    retArray = Time(readedData)
    readedData = retArray[0]
    time = retArray[1]
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<revtim>
#'{' \revtim <time> '}'
#@profile
def Revtim(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Revtim()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\revtim", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\revtim\s*", "", readedData, 1)
    
    #<time>
    retArray = Time(readedData)
    readedData = retArray[0]
    time = retArray[1]
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<printim>
#'{' \printim <time> '}'
#@profile
def Printim(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Printim()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\printim", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\printim\s*", "", readedData, 1)
    
    #<time>
    retArray = Time(readedData)
    readedData = retArray[0]
    time = retArray[1]
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<buptim>
#'{' \buptim <time> '}'
#@profile
def Buptim(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Buptim()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\buptim", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\buptim\s*", "", readedData, 1)
    
    #<time>
    retArray = Time(readedData)
    readedData = retArray[0]
    time = retArray[1]
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<info>
#'{' \info <title>? & <subject>? & <author>? & <manager>? & <company>? <operator>? &
#<category>? & <keywords>? & <comment>? & \versionN? & <doccomm>? & \vernN? &
#<creatim>? & <revtim>? & <printim>? & <buptim>? & \edminsN? & \nofpagesN? &
#\nofwordsN? \nofcharsN? & \idN? '}'
#@profile
def Info(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Info()\n")
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\info\s*", "", readedData, 1)
    
    while re.match(r"(\{\\(title|subject|author|manager|company|operator|category|keywords|comment|doccomm|hlinkbase|creatim|revtim|printim|buptim)|version|vern|edmins|nofpages|nofwords|nofchars|id)", readedData):
        #<title>?
        if re.match(r"\{\\title", readedData):
            retArray = Title(readedData)
            readedData = retArray[0]
        
        #<subject>?
        if re.match(r"\{\\subject", readedData):
            retArray = Subject(readedData)
            readedData = retArray[0]
        
        #<author>?
        if re.match(r"\{\\author", readedData):
            retArray = Author(readedData)
            readedData = retArray[0]
        
        #<manager>?
        if re.match(r"\{\\manager", readedData):
            retArray = Manager(readedData)
            readedData = retArray[0]
        
        #<company>?
        if re.match(r"\{\\company", readedData):
            retArray = Company(readedData)
            readedData = retArray[0]
        
        #<operator>?
        if re.match(r"\{\\operator", readedData):
            retArray = Operator(readedData)
            readedData = retArray[0]
        
        #<category>?
        if re.match(r"\{\\category", readedData):
            retArray = Category(readedData)
            readedData = retArray[0]
        
        #<keywords>?
        if re.match(r"\{\\keywords", readedData):
            retArray = Keywords(readedData)
            readedData = retArray[0]
        
        #<comment>?
        if re.match(r"\{\\comment", readedData):
            retArray = Comment(readedData)
            readedData = retArray[0]
        
        if re.match(r"\\version", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\version\s*", "", readedData, 1)
            
            #ziskani hodnoty kl. slova
            try:
                version = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Nelze nacist hodnotu keyword \version z <info>!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                sys.exit(errCode["parseErr"])
            
            #ulozeni hodnoty kl. slova
            #globPara["lsdstimax"] = posx
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
            
            #success = True
        
        #<doccomm>?
        if re.match(r"\{\\doccomm", readedData):
            retArray = Doccomm(readedData)
            readedData = retArray[0]
        
        if re.match(r"\\vern", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\vern\s*", "", readedData, 1)
            
            #ziskani hodnoty kl. slova
            try:
                vern = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Nelze nacist hodnotu keyword \vern z <info>!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                sys.exit(errCode["parseErr"])
            
            #ulozeni hodnoty kl. slova
            #globPara["lsdstimax"] = posx
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
            
            #success = True
        
        #<creatim>?
        if re.match(r"\{\\creatim", readedData):
            retArray = Creatim(readedData)
            readedData = retArray[0]
        
        #<revtim>?
        if re.match(r"\{\\revtim", readedData):
            retArray = Revtim(readedData)
            readedData = retArray[0]
        
        #<printim>?
        if re.match(r"\{\\printim", readedData):
            retArray = Printim(readedData)
            readedData = retArray[0]
        
        #<buptim>?
        if re.match(r"\{\\buptim", readedData):
            retArray = Buptim(readedData)
            readedData = retArray[0]
        
        if re.match(r"\\edmins", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\edmins\s*", "", readedData, 1)
            
            #ziskani hodnoty kl. slova
            try:
                edmins = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Nelze nacist hodnotu keyword \edmins z <info>!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                sys.exit(errCode["parseErr"])
            
            #ulozeni hodnoty kl. slova
            #globPara["lsdstimax"] = posx
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
            
            #success = True
        
        if re.match(r"\\nofpages", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\nofpages\s*", "", readedData, 1)
            
            #ziskani hodnoty kl. slova
            try:
                nofpages = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Nelze nacist hodnotu keyword \nofpages z <info>!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                sys.exit(errCode["parseErr"])
            
            #ulozeni hodnoty kl. slova
            #globPara["lsdstimax"] = posx
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
            
            #success = True
        
        if re.match(r"\\nofwords", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\nofwords\s*", "", readedData, 1)
            
            #ziskani hodnoty kl. slova
            try:
                nofwords = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Nelze nacist hodnotu keyword \nofwords z <info>!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                sys.exit(errCode["parseErr"])
            
            #ulozeni hodnoty kl. slova
            #globPara["lsdstimax"] = posx
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
            
            #success = True
        
        if re.match(r"\\nofchars", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\nofchars\s*", "", readedData, 1)
            
            #ziskani hodnoty kl. slova
            try:
                nofchars = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Nelze nacist hodnotu keyword \nofchars z <info>!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                sys.exit(errCode["parseErr"])
            
            #ulozeni hodnoty kl. slova
            #globPara["lsdstimax"] = posx
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
            
            #success = True
        
        if re.match(r"\\id", readedData):
            #odstraneni kl. slova
            readedData = re.sub(r"^\\id\s*", "", readedData, 1)
            
            #ziskani hodnoty kl. slova
            try:
                id = re.match(r"(\-)?\d+", readedData).group(0)
            except AttributeError as e:
                sys.stderr.write("Nelze nacist hodnotu keyword \id z <info>!\n")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
                sys.exit(errCode["parseErr"])
            
            #ulozeni hodnoty kl. slova
            #globPara["lsdstimax"] = posx
            
            #odstraneni hodnoty kl. slova
            readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
            
            #success = True
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<xmlnsdecl>
#@profile
def Xmlnsdecl(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Xmlnsdecl()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\xmlns", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    xmlnsdecl = ""
    
    if re.match(r"\{\\xmlns", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\{\\xmlns\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            xmlns = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \\xmlns z <xmlnsdecl>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        #globPara["lsdstimax"] = posx
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    try:
        xmlnsdecl = re.match(r"[^\}]+", readedData).group(0)
        readedData = re.sub(r"^[^\}]+", "", readedData, 1)
        
        #abstrakt muze obsahovat uvozovky, nutne osetrit
        while xmlnsdecl[-1] == "\\":
            xmlnsdecl += "}"
            readedData = re.sub(r"^\}", "", readedData, 1)
            
            #teoreticky muze nastat situace \"", takze proto *
            subxmlnsdecl= re.match(r"[^\}]*", readedData).group(0)
            if subxmlnsdecl == "":
                break
            else:
                readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                xmlnsdecl += subxmlnsdecl
    
    except AttributeError as e:
        sys.stderr.write("Nelze precist <xmlnsdecl>\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        print readedData
        sys.exit(errCode["parseErr"])
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<xmlnstbl>
#'{\*' \\xmlnstbl <xmlnsdecl>* '}'
#@profile
def Xmlnstbl(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Xmlnstbl()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\\*\s*\\xmlnstbl", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\\\*\s*\\xmlnstbl\s*", "", readedData, 1)
    
    #<xmlnsdecl>*
    while re.match(r"\{\\xmlns", readedData):
        retArray = Xmlnsdecl(readedData)
        readedData = retArray[0]
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<docfmt>
#@profile
def Docfmt(readedData):
    global errCode
    global globDoc
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Docfmt()\n")
    
    success = True
    
    if re.match(r"\\deftab", readedData):
        sys.stderr.write("deftab\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\deftab\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            deftab = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \deftab z <docfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globDoc["deftab"] = deftab
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\(hyphhotz|hyphconsec|hyphcaps|hyphauto|linestart|fracwidth|makebackup|muser|defformat|psover)", readedData):
        sys.stderr.write("(hyphhotz|hyphconsec|hyphcaps|hyphauto|linestart|fracwidth|makebackup|muser|defformat|psover)\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(hyphhotz|hyphconsec|hyphcaps|hyphauto|linestart|fracwidth|makebackup|muser|defformat|psover)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\((\*\\nextfile)|(\*\\template)|doctemp|windowcaption)", readedData):
        sys.stderr.write("((\*\\nextfile)|(\*\\template)|doctemp|windowcaption) neimplementovano!\n")
        sys.exit(errCode["notImplemented"])
    
    elif re.match(r"\\(doctype|ilfomacatclnup|horzdoc|vertdoc|jcompress|jexpand|lnongrid|grfdocevents|themelang|themelangfe|themelangcs|relyonvml|validatexml)", readedData):
        sys.stderr.write("(doctype|ilfomacatclnup|horzdoc|vertdoc|jcompress|jexpand|lnongrid|grfdocevents|themelang|themelangfe|themelangcs|relyonvml|validatexml)\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(doctype|ilfomacatclnup|horzdoc|vertdoc|jcompress|jexpand|lnongrid|grfdocevents|themelang|themelangfe|themelangcs|relyonvml|validatexml)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\\*\\xform", readedData):
        sys.stderr.write("\\xform neimplementovano!\n")
        sys.exit(errCode["notImplemented"])
    
    elif re.match(r"\\(donotembedsysfont|donotembedlingdata|showplaceholdtext|trackmoves|trackformatting|ignoremixedcontent|saveinvalidxml|showxmlerrors|stylelocktheme|stylelockqfset|usenormstyforlist)", readedData):
        sys.stderr.write("(donotembedsysfont|donotembedlingdata|showplaceholdtext|trackmoves|trackformatting|ignoremixedcontent|saveinvalidxml|showxmlerrors|stylelocktheme|stylelockqfset|usenormstyforlist)\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(donotembedsysfont|donotembedlingdata|showplaceholdtext|trackmoves|trackformatting|ignoremixedcontent|saveinvalidxml|showxmlerrors|stylelocktheme|stylelockqfset|usenormstyforlist)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\\*\\wgrffmtfilter", readedData):
        sys.stderr.write("\wgrffmtfilter neimplementovano!\n")
        sys.exit(errCode["notImplemented"])
    
    elif re.match(r"\\(readonlyrecommended|stylesortmethod)", readedData):
        sys.stderr.write("(readonlyrecommended|stylesortmethod)\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(readonlyrecommended|stylesortmethod)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\\*\\(writereservhash|writereservation)", readedData):
        sys.stderr.write("\(writereservhash|writereservation) neimplementovano!\n")
        sys.exit(errCode["notImplemented"])
    
    elif re.match(r"\\(saveprevpict|viewkind|viewscale|viewzk|viewbksp|private)", readedData):
        sys.stderr.write("(saveprevpict|viewkind|viewscale|viewzk|viewbksp|private)\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(saveprevpict|viewkind|viewscale|viewzk|viewbksp|private)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\fet", readedData):
        sys.stderr.write("fet\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\fet\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            fet = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \fet z <docfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globDoc["fet"] = fet
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\{\\\*\\ftnsep\s*", readedData):
        sys.stderr.write("General\n")
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\{\\\*\\ftnsep\s*", "", readedData, 1)
        
        #odstraneni vnitrni casti, ktera je nepotrebna
        readedData = re.sub(r"^\{\s*[^\}]+\s*\}\s*", "", readedData, 1)
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    elif re.match(r"\\\*\\ftnsepc", readedData):
        sys.stderr.write("General\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ftnsepc\s*", "", readedData, 1)
        
        globDoc["ftnsepc"] = ""
    
    elif re.match(r"\{\\\*\\aftnsep\s*", readedData):
        sys.stderr.write("General\n")
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\{\\\*\\aftnsep\s*", "", readedData, 1)
        
        #odstraneni vnitrni casti, ktera je nepotrebna
        readedData = re.sub(r"^\{\s*[^\}]+\s*\}\s*", "", readedData, 1)
        
        #odstraneni kl. slova
        readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    elif re.match(r"\\ftncn", readedData):
        sys.stderr.write("ftncn\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ftncn\s*", "", readedData, 1)
        
        globDoc["ftncn"] = ""
    
    elif re.match(r"\\aendnotes", readedData):
        sys.stderr.write("aendnotes\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\aendnotes\s*", "", readedData, 1)
        
        globDoc["aendnotes"] = ""
    
    elif re.match(r"\\aenddoc", readedData):
        sys.stderr.write("aenddoc\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\aenddoc\s*", "", readedData, 1)
        
        globDoc["aenddoc"] = ""
    
    elif re.match(r"\\aftnbj", readedData):
        sys.stderr.write("aftnbj\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\aftnbj\s*", "", readedData, 1)
        
        globDoc["aftnbj"] = ""
    
    elif re.match(r"\\aftntj", readedData):
        sys.stderr.write("aftntj\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\aftntj\s*", "", readedData, 1)
        
        globDoc["aftntj"] = ""
    
    elif re.match(r"\\(ftnstart|aftnstart|ftnrstpg|ftnrestart|ftnrstcont|aftnrestart|aftnrstcont|ftnnar|ftnnalc|ftnnauc|ftnnrlc|ftnnruc|ftnnchi|ftnnchosung|ftnncnum|ftnndbnum|ftnndbnumd|ftnndbnumt|ftnndbnumk|ftnndbar|ftnnganada|ftnngbnum|ftnngbnumd|ftnngbnuml|ftnngbnumk|ftnnzodiac|ftnnzodiacd|ftnnzodiacl|aftnnar|aftnnalc|aftnnauc|aftnnrlc|aftnnruc|aftnnchi|aftnnchosung|aftnncnum|aftnndbnum|aftnndbnumd|aftnndbnumt|aftnndbnumk|aftnndbar|aftnnganada|aftnngbnum|aftnngbnumd|aftnngbnuml|aftnngbnumk|aftnnzodiac|aftnnzodiacd|aftnnzodiacl)", readedData):
        sys.stderr.write("(ftnstart|aftnstart|ftnrstpg|ftnrestart|ftnrstcont|aftnrestart|aftnrstcont|ftnnar|ftnnalc|ftnnauc|ftnnrlc|ftnnruc|ftnnchi|ftnnchosung|ftnncnum|ftnndbnum|ftnndbnumd|ftnndbnumt|ftnndbnumk|ftnndbar|ftnnganada|ftnngbnum|ftnngbnumd|ftnngbnuml|ftnngbnumk|ftnnzodiac|ftnnzodiacd|ftnnzodiacl|aftnnar|aftnnalc|aftnnauc|aftnnrlc|aftnnruc|aftnnchi|aftnnchosung|aftnncnum|aftnndbnum|aftnndbnumd|aftnndbnumt|aftnndbnumk|aftnndbar|aftnnganada|aftnngbnum|aftnngbnumd|aftnngbnuml|aftnngbnumk|aftnnzodiac|aftnnzodiacd|aftnnzodiacl)\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(ftnstart|aftnstart|ftnrstpg|ftnrestart|ftnrstcont|aftnrestart|aftnrstcont|ftnnar|ftnnalc|ftnnauc|ftnnrlc|ftnnruc|ftnnchi|ftnnchosung|ftnncnum|ftnndbnum|ftnndbnumd|ftnndbnumt|ftnndbnumk|ftnndbar|ftnnganada|ftnngbnum|ftnngbnumd|ftnngbnuml|ftnngbnumk|ftnnzodiac|ftnnzodiacd|ftnnzodiacl|aftnnar|aftnnalc|aftnnauc|aftnnrlc|aftnnruc|aftnnchi|aftnnchosung|aftnncnum|aftnndbnum|aftnndbnumd|aftnndbnumt|aftnndbnumk|aftnndbar|aftnnganada|aftnngbnum|aftnngbnumd|aftnngbnuml|aftnngbnumk|aftnnzodiac|aftnnzodiacd|aftnnzodiacl)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\paperw", readedData):
        sys.stderr.write("paperw\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\paperw\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            paperw = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \paperw z <docfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globDoc["paperw"] = paperw
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\paperh", readedData):
        sys.stderr.write("paperh\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\paperh\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            paperh = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \paperh z <docfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globDoc["paperh"] = paperh
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\psz", readedData):
        sys.stderr.write("psz\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\psz\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            psz = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \psz z <docfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globDoc["psz"] = psz
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\margl", readedData):
        sys.stderr.write("margl\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\margl\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            margl = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \margl z <docfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globDoc["margl"] = margl
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\margr", readedData):
        sys.stderr.write("margr\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\margr\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            margr = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \margr z <docfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globDoc["margr"] = margr
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\margt", readedData):
        sys.stderr.write("margt\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\margt\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            margt = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \margt z <docfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globDoc["margt"] = margt
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\margb", readedData):
        sys.stderr.write("margb\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\margb\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            margb = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \margb z <docfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globDoc["margb"] = margb
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\(facingp|gutter|ogutter|rtlgutter|gutterprl|margmirror|landscape|pgnstart|widowctrl|twoonone|bookfold|bookfoldrev|bookfoldsheets|linkstyles|notabind|wraptrsp|prcolbl|noextrasprl|nocolbal|cvmme|sprstsp|sprsspbf|otblrul|transmf|swpbdr|brkfrm|sprslnsp|subfontbysize|truncatefontheight|truncex|bdbfhdr|dntblnsbdb|expshrtn|lytexcttp|lytprtmet|msmcap|nolead|nospaceforul|noultrlspc|noxlattoyen|oldlinewrap|sprsbsp|sprstsm|wpjst|wpsp|wptab|splytwnine|ftnlytwnine|htmautsp|useltbaln|alntblind|lytcalctblwd|lyttblrtgr|oldas|lnbrkrule)", readedData):
        sys.stderr.write("(facingp|gutter|ogutter|rtlgutter|gutterprl|margmirror|landscape|pgnstart|widowctrl|twoonone|bookfold|bookfoldrev|bookfoldsheets|linkstyles|notabind|wraptrsp|prcolbl|noextrasprl|nocolbal|cvmme|sprstsp|sprsspbf|otblrul|transmf|swpbdr|brkfrm|sprslnsp|subfontbysize|truncatefontheight|truncex|bdbfhdr|dntblnsbdb|expshrtn|lytexcttp|lytprtmet|msmcap|nolead|nospaceforul|noultrlspc|noxlattoyen|oldlinewrap|sprsbsp|sprstsm|wpjst|wpsp|wptab|splytwnine|ftnlytwnine|htmautsp|useltbaln|alntblind|lytcalctblwd|lyttblrtgr|oldas|lnbrkrule)\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(facingp|gutter|ogutter|rtlgutter|gutterprl|margmirror|landscape|pgnstart|widowctrl|twoonone|bookfold|bookfoldrev|bookfoldsheets|linkstyles|notabind|wraptrsp|prcolbl|noextrasprl|nocolbal|cvmme|sprstsp|sprsspbf|otblrul|transmf|swpbdr|brkfrm|sprslnsp|subfontbysize|truncatefontheight|truncex|bdbfhdr|dntblnsbdb|expshrtn|lytexcttp|lytprtmet|msmcap|nolead|nospaceforul|noultrlspc|noxlattoyen|oldlinewrap|sprsbsp|sprstsm|wpjst|wpsp|wptab|splytwnine|ftnlytwnine|htmautsp|useltbaln|alntblind|lytcalctblwd|lyttblrtgr|oldas|lnbrkrule)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\(bdrrlswsix|nolnhtadjtbl|ApplyBrkRules|rempersonalinfo|remdttm|snaptogridincell|wrppunct|asianbrkrule|nobrkwrptbl|toplinepunct|viewnobound|donotshowmarkup|donotshowcomments|donotshowinsdel|donotshowprops|allowfieldendsel|nocompatoptions|nogrowautofit|newtblstyruls)", readedData):
        sys.stderr.write("(bdrrlswsix|nolnhtadjtbl|ApplyBrkRules|rempersonalinfo|remdttm|snaptogridincell|wrppunct|asianbrkrule|nobrkwrptbl|toplinepunct|viewnobound|donotshowmarkup|donotshowcomments|donotshowinsdel|donotshowprops|allowfieldendsel|nocompatoptions|nogrowautofit|newtblstyruls)\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(bdrrlswsix|nolnhtadjtbl|ApplyBrkRules|rempersonalinfo|remdttm|snaptogridincell|wrppunct|asianbrkrule|nobrkwrptbl|toplinepunct|viewnobound|donotshowmarkup|donotshowcomments|donotshowinsdel|donotshowprops|allowfieldendsel|nocompatoptions|nogrowautofit|newtblstyruls)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\\*\\(background)", readedData):
        sys.stderr.write("\(background) neimplementovano!\n")
        sys.exit(errCode["notImplemented"])
    
    elif re.match(r"\\(nouicompat|nofeaturethrottle|forceupgrade|noafcnsttbl|noindnmbrts|felnbrelev|indrlsweleven|nocxsptable|notcvasp|notvatxbx|spltpgpar|hwelev|afelev|cachedcolbal|utinl|notbrkcnstfrctbl|krnprsnet|usexform)", readedData):
        sys.stderr.write("(nouicompat|nofeaturethrottle|forceupgrade|noafcnsttbl|noindnmbrts|felnbrelev|indrlsweleven|nocxsptable|notcvasp|notvatxbx|spltpgpar|hwelev|afelev|cachedcolbal|utinl|notbrkcnstfrctbl|krnprsnet|usexform)\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(nouicompat|nofeaturethrottle|forceupgrade|noafcnsttbl|noindnmbrts|felnbrelev|indrlsweleven|nocxsptable|notcvasp|notvatxbx|spltpgpar|hwelev|afelev|cachedcolbal|utinl|notbrkcnstfrctbl|krnprsnet|usexform)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #sys.stderr.write(readedData[:128] + "\n")
        #sys.exit(0)
    
    #Forms
    elif re.match(r"\\(formprot|allprot|formshade|formdisp|printdata)", readedData):
        sys.stderr.write("Forms\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(formprot|allprot|formshade|formdisp|printdata)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #Revision Marks
    elif re.match(r"\\(revprot|revisions|revprop|revbar)", readedData):
        sys.stderr.write("Revision Marks\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(revprot|revisions|revprop|revbar)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #Write Protection (Document is Read-only)
    #Comment Protection (Only Annotations are Editable)
    #Style and Formatting Protection
    #Tables
    elif re.match(r"\\(readprot|annotprot|stylelock|stylelockenforced|stylelockbackcomp|autofmtoverride|enforceprot|protlevel|tsd)", readedData):
        sys.stderr.write("Write Protection (Document is Read-only)\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(readprot|annotprot|stylelock|stylelockenforced|stylelockbackcomp|autofmtoverride|enforceprot|protlevel|tsd)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #Bidirectional Controls
    #Click-and-Type
    #Kinsoku Characters (Asia)
    elif re.match(r"\\(rtldoc|ltrdoc|cts|jsksu|ksulang|nojkernpunct)", readedData):
        sys.stderr.write("Bidirectional Controls\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(rtldoc|ltrdoc|cts|jsksu|ksulang|nojkernpunct)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\\*\\(fchars|lchars)", readedData):
        sys.stderr.write("\(fchars|lchars) neimplementovano!\n")
        sys.exit(errCode["notImplemented"])
    
    #Drawing Grid
    elif re.match(r"\\(dghspace|dgvspace|dghorigin|dgvorigin|dghshow|dgvshow|dgsnap|dgmargin)", readedData):
        sys.stderr.write("Drawing Grid\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(dghspace|dgvspace|dghorigin|dgvorigin|dghshow|dgvshow|dgsnap|dgmargin)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #Page Borders
    #TODO: Zde nevim, jestli to bude potreba
    elif re.match(r"\\(pgbrdrhead|pgbrdrfoot|pgbrdrt|pgbrdrb|pgbrdrl|pgbrdrr|brdrart|pgbrdropt|pgbrdrsnap)", readedData):
        sys.stderr.write("Page Borders\n")
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(pgbrdrhead|pgbrdrfoot|pgbrdrt|pgbrdrb|pgbrdrl|pgbrdrr|brdrart|pgbrdropt|pgbrdrsnap)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    else:
        success = False
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

"""
#<secfmt>
def Secfmt(readedData):
    global errCode
    global globSec
    global globDefSec
    
    sys.stderr.write("Secfmt()\n")
    
    success = True
    
    if re.match(r"\\sect(\s+|\\|((\-)?\d+))", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sect\s*", "", readedData, 1)
        
        globSec["sect"] = ""
        
        #TODO: implementovat
        sys.stderr.write("Implementovat fci \\sect!\n")
        sys.exit(errCode["notImplemented"])
    
    elif re.match(r"\\sectd", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sectd\s*", "", readedData, 1)
        
        globSec["sectd"] = ""
        
        globSec = globDefSec
        #sys.stderr.write("Implementovat fci \\sectd!\n")
        #sys.exit(errCode["notImplemented"])
    
    elif re.match(r"\\endnhere", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\endnhere\s*", "", readedData, 1)
        
        globSec["endnhere"] = ""
        
        #TODO: implementovat
        sys.stderr.write("Implementovat fci \\endnhere!\n")
        sys.exit(errCode["notImplemented"])
    
    elif re.match(r"\\(binfsxn|binsxn|pnseclvl|sectunlocked)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(binfsxn|binsxn|pnseclvl|sectunlocked)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\ds", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ds\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            ds = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \ds z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["ds"] = ds
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    #Section Break
    elif re.match(r"\\(sbknone|sbkcol|sbkpage|sbkeven|sbkodd)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(sbknone|sbkcol|sbkpage|sbkeven|sbkodd)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #Columns
    elif re.match(r"\\cols(\-)?\d+", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cols\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            cols = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \cols z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["cols"] = cols
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\colsx", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\colsx\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            colsx = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \colsx z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["colsx"] = colsx
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\colno", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\colno\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            colno = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \colno z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["colno"] = colno
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\colsr", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\colsr\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            colsr = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \colsr z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["colsr"] = colsr
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\colw", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\colw\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            colw = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \colw z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["colw"] = colw
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\linebetcol", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\linebetcol\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\sftntj", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sftntj\s*", "", readedData, 1)
        
        globSec["sftntj"] = ""
    
    elif re.match(r"\\sftnbj", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sftnbj\s*", "", readedData, 1)
        
        globSec["sftnbj"] = ""
    
    elif re.match(r"\\sftnstart", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sftnstart\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\saftnstart", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\saftnstart\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\(sftnrstpg|sftnrestart|sftnrstcont|saftnrestart|saftnrstcont|sftnnar|sftnnalc|sftnnauc|sftnnrlc|sftnnruc|sftnnchi|sftnnchosung|sftnncnum|sftnndbnum|sftnndbnumd|sftnndbnumt|sftnndbnumk|sftnndbar|sftnnganada|sftnngbnum|sftnngbnumd|sftnngbnuml|sftnngbnumk|sftnnzodiac|sftnnzodiacd|sftnnzodiacl|saftnnar|saftnnalc|saftnnauc|saftnnrlc|saftnnruc|saftnnchi|saftnnchosung|saftnncnum|saftnndbnum|saftnndbnumd|saftnndbnumt|saftnndbnumk|saftnndbar|saftnnganada|saftnngbnum|saftnngbnumd|saftnngbnuml|saftnngbnumk|saftnnzodiac|saftnnzodiacd|saftnnzodiacl)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(sftnrstpg|sftnrestart|sftnrstcont|saftnrestart|saftnrstcont|sftnnar|sftnnalc|sftnnauc|sftnnrlc|sftnnruc|sftnnchi|sftnnchosung|sftnncnum|sftnndbnum|sftnndbnumd|sftnndbnumt|sftnndbnumk|sftnndbar|sftnnganada|sftnngbnum|sftnngbnumd|sftnngbnuml|sftnngbnumk|sftnnzodiac|sftnnzodiacd|sftnnzodiacl|saftnnar|saftnnalc|saftnnauc|saftnnrlc|saftnnruc|saftnnchi|saftnnchosung|saftnncnum|saftnndbnum|saftnndbnumd|saftnndbnumt|saftnndbnumk|saftnndbar|saftnnganada|saftnngbnum|saftnngbnumd|saftnngbnuml|saftnngbnumk|saftnnzodiac|saftnnzodiacd|saftnnzodiacl)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #Line Numbering
    elif re.match(r"\\linemod", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\linemod\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\linex", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\linex\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            colw = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \linex z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["linex"] = linex
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\(linestarts|linerestart|lineppage|linecont)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(linestarts|linerestart|lineppage|linecont)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #Page Information
    elif re.match(r"\\pgwsxn", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\pgwsxn\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            pgwsxn = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \pgwsxn z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["pgwsxn"] = pgwsxn
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\pghsxn", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\pghsxn\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            pghsxn = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \pghsxn z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["pghsxn"] = pghsxn
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\marglsxn", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\marglsxn\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            marglsxn = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \marglsxn z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["marglsxn"] = marglsxn
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\margrsxn", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\margrsxn\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            margrsxn = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \margrsxn z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["margrsxn"] = margrsxn
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\margtsxn", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\margtsxn\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            margtsxn = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \margtsxn z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["margtsxn"] = margtsxn
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\margbsxn", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\margbsxn\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            margbsxn = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \margbsxn z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["margbsxn"] = margbsxn
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\(guttersxn|margmirsxn|lndscpsxn|titlepg)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(guttersxn|margmirsxn|lndscpsxn|titlepg)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\headery", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\headery\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            headery = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \headery z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["headery"] = headery
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif re.match(r"\\footery", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\footery\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            footery = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \footery z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["footery"] = footery
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    #Page Numbers
    elif re.match(r"\\(pgnstarts|pgncont|pgnrestart|pgnx|pgny|pgndec|pgnucrm|pgnlcrm|pgnucltr|pgnlcltr|pgnbidia|pgnbidib|pgnchosung|pgncnum|pgndbnum|pgndbnumd|pgndbnumt|pgndbnumk|pgndecd|pgnganada|pgngbnum|pgngbnumd|pgngbnuml|pgngbnumk|pgnzodiac|pgnzodiac|pgnzodiacl|pgnhindia|pgnhindib|pgnhindic|pgnhindid|pgnthaia|pgnthaib|pgnthaic|pgnvieta|pgnid|pgnhn|pgnhnsh|pgnhnsp|pgnhnsc)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(pgnstarts|pgncont|pgnrestart|pgnx|pgny|pgndec|pgnucrm|pgnlcrm|pgnucltr|pgnlcltr|pgnbidia|pgnbidib|pgnchosung|pgncnum|pgndbnum|pgndbnumd|pgndbnumt|pgndbnumk|pgndecd|pgnganada|pgngbnum|pgngbnumd|pgngbnuml|pgngbnumk|pgnzodiac|pgnzodiac|pgnzodiacl|pgnhindia|pgnhindib|pgnhindic|pgnhindid|pgnthaia|pgnthaib|pgnthaic|pgnvieta|pgnid|pgnhn|pgnhnsh|pgnhnsp|pgnhnsc)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\(pgnhnsm|pgnhnsn)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(pgnhnsm|pgnhnsn)\s*", "", readedData, 1)
        
        sys.stderr.write("(pgnhnsm|pgnhnsn) neimplementovano!\n")
        sys.exit(errCode["notImplemented"])
    
    #Vertical Alignment
    elif re.match(r"\\vertal", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\vertal\s*", "", readedData, 1)
        
        globSec["vertal"] = ""
    
    elif re.match(r"\\vertalt", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\vertalt\s*", "", readedData, 1)
        
        globSec["vertalt"] = ""
    
    elif re.match(r"\\vertalb", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\vertalb\s*", "", readedData, 1)
        
        globSec["vertalb"] = ""
    
    elif re.match(r"\\vertalc", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\vertalc\s*", "", readedData, 1)
        
        globSec["vertalc"] = ""
    
    elif re.match(r"\\vertalj", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\vertalj\s*", "", readedData, 1)
        
        globSec["vertalj"] = ""
    
    #Revision Tracking
    #Bidirectional Controls
    #Asian Controls
    elif re.match(r"\\(srauth|srdate|rtlsect|ltrsect|horzsect|vertsect)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(srauth|srdate|rtlsect|ltrsect|horzsect|vertsect)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #Text Flow
    elif re.match(r"\\stextflow", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\stextflow\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            stextflow = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \stextflow z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["stextflow"] = stextflow
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    #Page Borders
    #TODO: Spise nepotrebne
    elif re.match(r"\\(pgbrdrhead|pgbrdrfoot|pgbrdrt|pgbrdrb|pgbrdrl|pgbrdrr|brdrart|pgbrdropt|pgbrdrsnap)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(pgbrdrhead|pgbrdrfoot|pgbrdrt|pgbrdrb|pgbrdrl|pgbrdrr|brdrart|pgbrdropt|pgbrdrsnap)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #Line and Character Grid
    elif re.match(r"\\sectexpand", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sectexpand\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            sectexpand = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \sectexpand z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["sectexpand"] = sectexpand
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\sectlinegrid", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sectlinegrid\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            sectlinegrid = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \sectlinegrid z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["sectlinegrid"] = sectlinegrid
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif re.match(r"\\(sectdefaultcl|sectspecifycl|sectspecifyl|sectspecifygen)", readedData):
        sys.stderr.write("(sectdefaultcl|sectspecifycl|sectspecifyl|sectspecifygen) neimplementovano!\n")
        sys.exit(errCode["notImplemented"])
    
    else:
        success = False
    
    #TODO: Pozor, pry plno klicovych slov z <parfmt> se muze v <secfmt> vyskytnout!
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray
"""

#<secfmt>
#@profile
def Secfmt(readedData):
    global errCode
    global globSec
    #global globSecfmt
    global globDefSec
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Secfmt()\n")
    
    success = True
    
    if not re.match(r"\\([a-zA-Z]+)", readedData):
        success = False
        
        retArray = []
        retArray.append(readedData)
        retArray.append(success)
        return retArray
    
    #nacteni klicoveho slova
    try:
        keyword = re.match(r"\\([a-zA-Z]+)", readedData).group(1)
    except AttributeError as e:
        sys.stderr.write(readedData[:128] + "\n")
        sys.stderr.write("Nelze nacist keyword!\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
        sys.exit(errCode["parseErr"])
    #readedData = re.sub(r"^[a-zA-Z]+\s*", "", readedData, 1)
    
    sys.stderr.write("Keyword: " + keyword + "\n")
    
    if keyword == "sect":        
        PushToSectList()
        
        readedData = re.sub(r"^\\sect\s*", "", readedData, 1)
    
    elif keyword == "sectd":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sectd\s*", "", readedData, 1)
        
        #globSec["sectd"] = ""
        
        globSec = globDefSec
        #sys.stderr.write("Implementovat fci \\sectd!\n")
        #sys.exit(errCode["notImplemented"])
    
    #TODO: Presunuto zde kvuli urychleni
    elif keyword == "srauth" or keyword == "srdate" or keyword == "rtlsect" or keyword == "ltrsect" or keyword == "horzsect" or keyword == "vertsect":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(srauth|srdate|rtlsect|ltrsect|horzsect|vertsect)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #TODO: Presunuto zde kvuli urychleni
    elif keyword == "headery":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\headery\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            headery = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \headery z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["headery"] = headery
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif keyword == "footery":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\footery\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            footery = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \footery z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["footery"] = footery
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif keyword == "endnhere":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\endnhere\s*", "", readedData, 1)
        
        globSec["endnhere"] = ""
        
        #TODO: implementovat
        sys.stderr.write("Implementovat fci \\endnhere!\n")
        sys.exit(errCode["notImplemented"])
    
    elif keyword == "binfsxn" or keyword == "binsxn" or keyword == "pnseclvl" or keyword == "sectunlocked":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(binfsxn|binsxn|pnseclvl|sectunlocked)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif keyword == "ds":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\ds\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            ds = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \ds z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["ds"] = ds
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    #Section Break
    elif keyword == "sbknone" or keyword == "sbkcol" or keyword == "sbkpage" or keyword == "sbkeven" or keyword == "sbkodd":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(sbknone|sbkcol|sbkpage|sbkeven|sbkodd)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #Columns
    elif keyword == "cols":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\cols\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            cols = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \cols z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["cols"] = cols
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif keyword == "colsx":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\colsx\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            colsx = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \colsx z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["colsx"] = colsx
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif keyword == "colno":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\colno\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            colno = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \colno z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["colno"] = colno
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif keyword == "colsr":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\colsr\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            colsr = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \colsr z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["colsr"] = colsr
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif keyword == "colw":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\colw\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            colw = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \colw z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["colw"] = colw
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif keyword == "linebetcol":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\linebetcol\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif keyword == "sftntj":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sftntj\s*", "", readedData, 1)
        
        globSec["sftntj"] = ""
    
    elif keyword == "sftnbj":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sftnbj\s*", "", readedData, 1)
        
        globSec["sftnbj"] = ""
    
    elif keyword == "sftnstart":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sftnstart\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif keyword == "saftnstart":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\saftnstart\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif keyword == "sftnrstpg" or keyword == "sftnrestart" or keyword == "sftnrstcont" or keyword == "saftnrestart" or keyword == "saftnrstcont" or keyword == "sftnnar" or keyword == "sftnnalc" or keyword == "sftnnauc" or keyword == "sftnnrlc" or keyword == "sftnnruc" or keyword == "sftnnchi" or keyword == "sftnnchosung" or keyword == "sftnncnum" or keyword == "sftnndbnum" or keyword == "sftnndbnumd":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(sftnrstpg|sftnrestart|sftnrstcont|saftnrestart|saftnrstcont|sftnnar|sftnnalc|sftnnauc|sftnnrlc|sftnnruc|sftnnchi|sftnnchosung|sftnncnum|sftnndbnum|sftnndbnumd|)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif keyword == "sftnndbnumt" or keyword == "sftnndbnumk" or keyword == "sftnndbar" or keyword == "sftnnganada" or keyword == "sftnngbnum" or keyword == "sftnngbnumd" or keyword == "sftnngbnuml" or keyword == "sftnngbnumk" or keyword == "sftnnzodiac" or keyword == "sftnnzodiacd" or keyword == "sftnnzodiacl" or keyword == "saftnnar" or keyword == "saftnnalc" or keyword == "saftnnauc" or keyword == "saftnnrlc":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(sftnndbnumt|sftnndbnumk|sftnndbar|sftnnganada|sftnngbnum|sftnngbnumd|sftnngbnuml|sftnngbnumk|sftnnzodiac|sftnnzodiacd|sftnnzodiacl|saftnnar|saftnnalc|saftnnauc|saftnnrlc)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif keyword == "saftnnruc" or keyword == "saftnnchi" or keyword == "saftnnchosung" or keyword == "saftnncnum" or keyword == "saftnndbnum" or keyword == "saftnndbnumd" or keyword == "saftnndbnumt" or keyword == "saftnndbnumk" or keyword == "saftnndbar" or keyword == "saftnnganada" or keyword == "saftnngbnum" or keyword == "saftnngbnumd" or keyword == "saftnngbnuml" or keyword == "saftnngbnumk" or keyword == "saftnnzodiac" or keyword == "saftnnzodiacd" or keyword == "saftnnzodiacl":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(saftnnruc|saftnnchi|saftnnchosung|saftnncnum|saftnndbnum|saftnndbnumd|saftnndbnumt|saftnndbnumk|saftnndbar|saftnnganada|saftnngbnum|saftnngbnumd|saftnngbnuml|saftnngbnumk|saftnnzodiac|saftnnzodiacd|saftnnzodiacl)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #Line Numbering
    elif keyword == "linemod":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\linemod\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif keyword == "linex":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\linex\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            colw = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \linex z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["linex"] = linex
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif keyword == "linestarts" or keyword == "linerestart" or keyword == "lineppage" or keyword == "linecont":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(linestarts|linerestart|lineppage|linecont)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #Page Information
    elif keyword == "pgwsxn":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\pgwsxn\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            pgwsxn = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \pgwsxn z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["pgwsxn"] = pgwsxn
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif keyword == "pghsxn":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\pghsxn\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            pghsxn = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \pghsxn z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["pghsxn"] = pghsxn
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif keyword == "marglsxn":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\marglsxn\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            marglsxn = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \marglsxn z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["marglsxn"] = marglsxn
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif keyword == "margrsxn":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\margrsxn\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            margrsxn = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \margrsxn z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["margrsxn"] = margrsxn
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif keyword == "margtsxn":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\margtsxn\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            margtsxn = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \margtsxn z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["margtsxn"] = margtsxn
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif keyword == "margbsxn":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\margbsxn\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            margbsxn = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \margbsxn z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["margbsxn"] = margbsxn
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    elif keyword == "guttersxn" or keyword == "margmirsxn" or keyword == "lndscpsxn" or keyword == "titlepg":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(guttersxn|margmirsxn|lndscpsxn|titlepg)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #Page Numbers
    elif keyword == "pgnstarts" or keyword == "pgncont" or keyword == "pgnrestart" or keyword == "pgnx" or keyword == "pgny" or keyword == "pgndec" or keyword == "pgnucrm" or keyword == "pgnlcrm" or keyword == "pgnucltr" or keyword == "pgnlcltr":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(pgnstarts|pgncont|pgnrestart|pgnx|pgny|pgndec|pgnucrm|pgnlcrm|pgnucltr|pgnlcltr)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif keyword == "pgnbidia" or keyword == "pgnbidib" or keyword == "pgnchosung" or keyword == "pgncnum" or keyword == "pgndbnum" or keyword == "pgndbnumd" or keyword == "pgndbnumt" or keyword == "pgndbnumk" or keyword == "pgndecd" or keyword == "pgnganada":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(pgnbidia|pgnbidib|pgnchosung|pgncnum|pgndbnum|pgndbnumd|pgndbnumt|pgndbnumk|pgndecd|pgnganada)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif keyword == "pgngbnum" or keyword == "pgngbnumd" or keyword == "pgngbnuml" or keyword == "pgngbnumk" or keyword == "pgnzodiac" or keyword == "pgnzodiacl" or keyword == "pgnhindia" or keyword == "pgnhindib" or keyword == "pgnhindic" or keyword == "pgnhindid" or keyword == "pgnthaia" or keyword == "pgnthaib" or keyword == "pgnthaic" or keyword == "pgnvieta" or keyword == "pgnid" or keyword == "pgnhn" or keyword == "pgnhnsh" or keyword == "pgnhnsp" or keyword == "pgnhnsc":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(pgngbnum|pgngbnumd|pgngbnuml|pgngbnumk|pgnzodiac|pgnzodiacl|pgnhindia|pgnhindib|pgnhindic|pgnhindid|pgnthaia|pgnthaib|pgnthaic|pgnvieta|pgnid|pgnhn|pgnhnsh|pgnhnsp|pgnhnsc)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif keyword == "pgnhnsm" or keyword == "pgnhnsn":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(pgnhnsm|pgnhnsn)\s*", "", readedData, 1)
        
        sys.stderr.write("(pgnhnsm|pgnhnsn) neimplementovano!\n")
        sys.exit(errCode["notImplemented"])
    
    #Vertical Alignment
    elif keyword == "vertal":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\vertal\s*", "", readedData, 1)
        
        globSec["vertal"] = ""
    
    elif keyword == "vertalt":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\vertalt\s*", "", readedData, 1)
        
        globSec["vertalt"] = ""
    
    elif keyword == "vertalb":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\vertalb\s*", "", readedData, 1)
        
        globSec["vertalb"] = ""
    
    elif keyword == "vertalc":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\vertalc\s*", "", readedData, 1)
        
        globSec["vertalc"] = ""
    
    elif keyword == "vertalj":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\vertalj\s*", "", readedData, 1)
        
        globSec["vertalj"] = ""
    
    #Revision Tracking
    #Bidirectional Controls
    #Asian Controls
    #TODO: Presunuto z duvodu urychleni
    
    #Text Flow
    elif keyword == "stextflow":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\stextflow\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            stextflow = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \stextflow z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["stextflow"] = stextflow
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
        
        #success = True
    
    #Page Borders
    #TODO: Spise nepotrebne
    elif keyword == "pgbrdrhead" or keyword == "pgbrdrfoot" or keyword == "pgbrdrt" or keyword == "pgbrdrb" or keyword == "pgbrdrl" or keyword == "pgbrdrr" or keyword == "brdrart" or keyword == "pgbrdropt" or keyword == "pgbrdrsnap":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(pgbrdrhead|pgbrdrfoot|pgbrdrt|pgbrdrb|pgbrdrl|pgbrdrr|brdrart|pgbrdropt|pgbrdrsnap)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #Line and Character Grid
    elif keyword == "sectexpand":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sectexpand\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            sectexpand = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \sectexpand z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["sectexpand"] = sectexpand
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif keyword == "sectlinegrid":
        #odstraneni kl. slova
        readedData = re.sub(r"^\\sectlinegrid\s*", "", readedData, 1)
        
        #ziskani hodnoty kl. slova
        try:
            sectlinegrid = re.match(r"(\-)?\d+", readedData).group(0)
        except AttributeError as e:
            sys.stderr.write("Nelze nacist hodnotu keyword \sectlinegrid z <secfmt>!\n")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            sys.stderr.write("Line: " + str(exc_tb.tb_lineno) + "\n")
            sys.exit(errCode["parseErr"])
        
        #ulozeni hodnoty kl. slova
        globSec["sectlinegrid"] = sectlinegrid
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    elif keyword == "sectdefaultcl" or keyword == "sectspecifycl" or keyword == "sectspecifyl" or keyword == "sectspecifygen":
        sys.stderr.write("(sectdefaultcl|sectspecifycl|sectspecifyl|sectspecifygen) neimplementovano!\n")
        sys.exit(errCode["notImplemented"])
    
    else:
        success = False
    
    #TODO: Pozor, pry plno klicovych slov z <parfmt> se muze v <secfmt> vyskytnout!
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<hdrctl>
#\header | \footer | \headerl | \headerr | \headerf | \footerl | \footerr | \footerf
#@profile
def Hdrctl(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Hdrctl()\n")
    
    if re.match(r"\\(header|footer|headerl|headerr|headerf|footerl|footerr|footerf)", readedData):
        #odstraneni kl. slova
        readedData = re.sub(r"^\\(header|footer|headerl|headerr|headerf|footerl|footerr|footerf)\s*", "", readedData, 1)
        
        #odstraneni hodnoty kl. slova
        readedData = re.sub(r"^(\-)?\d+\s*", "", readedData)
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<hdrftr>
#'{' <hdrctl> <para>+ '}' <hdrftr>?
#@profile
def Hdrftr(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Hdrftr()\n")
    
    #TODO: Tohle zapracovat i do ostatnich fci
    if not re.match(r"\{\\(header|footer|headerl|headerr|headerf|footerl|footerr|footerf)", readedData):
        retArray = []
        retArray.append(readedData)
        return retArray
    
    sys.stderr.write(readedData[:128] + "\n")
    sys.stderr.write("<Hdrftr> konec\n")
    sys.exit(0)
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\s*", "", readedData, 1)
    
    #<hdrctl>
    retArray = Hdrctl(readedData)
    readedData = retArray[0]
    
    #<para>+
    hit = True
    while hit:
        retArray = Para(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    #<hdrftr>?
    if re.match(r"\{\\(header|footer|headerl|headerr|headerf|footerl|footerr|footerf)", readedData):
        retArray = Hdrftr(readedData)
        readedData = retArray[0]
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<section>
#<secfmt>* <hdrftr>? <para>+ (\sect <section>)?
#@profile
def Section(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Section()\n")
    
    success = False
    
    #<secfmt>*
    hit = True
    while hit:
        retArray = Secfmt(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #<hdrftr>?
    if re.match(r"\{\\(header|footer|headerl|headerr|headerf|footerl|footerr|footerf)", readedData):
        retArray = Hdrftr(readedData)
        readedData = retArray[0]
    
    #<para>+
    hit = True
    while hit:
        retArray = Para(readedData)
        readedData = retArray[0]
        hit = retArray[1]
        
        if hit:
            success = True
    
    #(\sect <section>)?
    if re.match(r"\\sect(\s+|\\|((\-)?\d+))", readedData):
        sys.stderr.write(readedData[:128] + "\n")
        sys.stderr.write("<Section> konec\n")
        sys.exit(0)
        
        #odstraneni nepotrebne casti
        readedData = re.sub(r"^\\sect\s*", "", readedData, 1)
        
        retArray = Section(readedData)
        readedData = retArray[0]
    
    #return
    retArray = []
    retArray.append(readedData)
    retArray.append(success)
    return retArray

#<document>
#<info>? <xmlnstbl>? <docfmt>* <section>+
#@profile
def Document(readedData):
    global errCode
    global globDoc
    global globSectList
    global globParaList
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("Document()\n")
    
    #<info>?
    if re.match(r"\{\\info", readedData):     
        retArray = Info(readedData)
        readedData = retArray[0]
    
    #<xmlnstbl>?
    if re.match(r"\{\\\*\s*\\xmlnstbl", readedData):     
        retArray = Xmlnstbl(readedData)
        readedData = retArray[0]
    
    #<docfmt>*
    hit = True
    while hit:
        #sys.stderr.write(readedData[:16] + "\n")
        retArray = Docfmt(readedData)
        readedData = retArray[0]
        hit = retArray[1]
    
    #print globDoc
    
    #<section>+
    #hit = True
    #while hit:
    while not re.match(r"\}", readedData):
        retArray = Section(readedData)
        readedData = retArray[0]
        #hit = retArray[1]
    
    #ulozeni nezpracovaneho textu
    PushToSectList()
    
    #return
    retArray = []
    retArray.append(readedData)
    return retArray

#<File>
#'{' <header> <document> '}'
#@profile
def File(readedData):
    global errCode
    global globPrintFunctionName
    
    if globPrintFunctionName:
        sys.stderr.write("File()\n")
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\{\s*", "", readedData, 1)
    
    #<header>
    retArray = Header(readedData)
    readedData = retArray[0]
    
    #<document>
    retArray = Document(readedData)
    readedData = retArray[0]
    
    #odstraneni nepotrebne casti
    readedData = re.sub(r"^\}\s*", "", readedData, 1)
    
    if not readedData:
        sys.stderr.write("Parsovani dokonceno!!!\n")
    
    else:
        sys.stderr.write("Chyba pri parsovani!\n")
        sys.stderr.write(readedData[:128])
        sys.stderr.write("<File> konec\n")
        sys.exit(errCode["parseErr"])
    
    retArray = MakeXml()
    xml = retArray[0]
    
    #return
    retArray = []
    retArray.append(xml)
    return retArray

#Entry point for parsation
#@profile
def ParseRTF(readedData):
    #Ziskani bohateho textu ze vst. souboru
    retArray = File(readedData)
    xml = retArray[0]
    
    #print xml
    #sys.exit(0)
    
    #return
    return xml

#TODO: Pripadne upravit
#@profile
def LoadRTF(inputFile):
    #otevreni, precteni a uzavreni souboru
    try:
        file = open(inputFile, "rt")
    except IOError:
        sys.stderr.write("Chyba pri otevirani souboru\n")
        sys.exit(2)
    
    #nacteni dat ze souboru
    try:
        filedata = file.read()
        #print filedata
        file.close()
    except UnicodeDecodeError:
        sys.stderr.write("Chyba: Nelze nacist vstupni soubor\n")
        sys.exit(255)
    
    #return
    return filedata

#TODO: Pripadne upravit
#@profile
def FixRichText(rtfArray):
    #TODO: Zde pokracovat!!!
    sys.stderr.write("Implementovat FixRichText()\n")

#TODO: Okomentovat
#@profile
def GetPosAndSizePara(para):
    global globSectList
    global globDefchp
    global globDefpap
    
    dataItem = {}
    
    test = False
    
    #ulozeni pozice odstavce
    dataItem["posx"] = int(para["apoctl"]["posx"])
    dataItem["posy"] = int(para["apoctl"]["posy"])
    
    #ziskani a ulozeni velikosti odstavce
    #pokud ma odstavec zadanou sirku ramce
    if para["apoctl"].has_key("absw"):
        dataItem["width"] = abs(int(para["apoctl"]["absw"]))
    #    dataItem["height"] = abs(int(para["apoctl"]["absh"]))
    #sirku je nutne spocitat manualne
    else:
        dataItem["width"] = 0
        lineCnt = 0
        lineLen = 0
        tmpStr = ""
        for textData in para["text"]:
            tmpTextData = textData["text"]
            
            #print "FS"
            #print textData["data"]["fs"]
            
            #dokud jsou v textu oddelovace radku
            while re.search(r"\\line", tmpTextData):
                #ziskani textu do oddelovace radku
                lineIndex = tmpTextData.index("\\line")
                tmpStr += tmpTextData[:lineIndex]
                
                #zkraceni vychoziho textu o pouzity text
                tmpTextData = tmpTextData[lineIndex+len("\\line"):]
                
                #ziskani delky a vysky textu
                lineWidth = int(float(textData["data"]["fs"])*float(len(tmpStr))*10.0*(25.0/48.0))
                
                #pricteni vysky a sirky odstavce
                dataItem["width"] += lineWidth
                
                #zvyseni citace radku
                lineCnt += 1
                
                tmpStr = ""
            
            tmpStr += tmpTextData
        
        #uprava sirky odstavce
        if tmpStr and lineCnt == 0:
            dataItem["width"] = int(float(textData["data"]["fs"])*float(len(tmpStr))*10.0*(25.0/48.0))
        else:
            dataItem["width"] = dataItem["width"] / lineCnt
        
        if para["parfmt"].has_key("li"):
            dataItem["width"] += int(para["parfmt"]["li"])
        
        if para["parfmt"].has_key("ri"):
            dataItem["width"] += int(para["parfmt"]["ri"])
        
    #Vyska se bude pocitat vzdy manualne
    dataItem["height"] = 0
    lineCnt = 0
    lineLen = 0
    tmpStr = ""
    for textData in para["text"]:
        tmpTextData = textData["text"]
        
        #print "FS"
        #print textData["data"]["fs"]
        
        #dokud jsou v textu oddelovace radku
        while re.search(r"\\line", tmpTextData):
            #ziskani textu do oddelovace radku
            lineIndex = tmpTextData.index("\\line")
            tmpStr += tmpTextData[:lineIndex]
            
            #zkraceni vychoziho textu o pouzity text
            tmpTextData = tmpTextData[lineIndex+len("\\line"):]
            
            #ziskani delky a vysky textu
            #lineHeight = int(float(textData["data"]["fs"])*10.0*(25.0/48.0))
            lineHeight = int(float(textData["data"]["fs"])*10.0)
            
            #pricteni vysky a sirky odstavce
            dataItem["height"] += lineHeight
            
            #print lineHeight
            
            #zvyseni citace radku
            lineCnt += 1
            
            tmpStr = ""
        
        tmpStr += tmpTextData
    
    dataItem["height"] += int(float(160))
    
    #return
    retArray = []
    retArray.append(dataItem)
    return retArray

#TODO: Okomentovat
#@profile
def GetOtherParInfo(para, dataItem):
    global globSectList
    global globDefchp
    global globDefpap
    global globStylesheet
    
    #ulozeni hodnoty mezery za odstavcem
    if para["parfmt"].has_key("sa"):
        dataItem["sa"] = int(para["parfmt"]["sa"])
    else:
        dataItem["sa"] = int(globDefpap["sa"])
    
    #ulozeni left-indentu
    if para["parfmt"].has_key("li"):
        dataItem["li"] = int(para["parfmt"]["li"])
    else:
        dataItem["li"] = int(globDefpap["li"])
    
    #ulozeni odkazu na style type
    if para["parfmt"].has_key("s"):
        dataItem["styleRef"] = int(para["parfmt"]["s"])
    elif globDefpap.has_key("s"):
        dataItem["styleRef"] = int(globDefpap["s"])
    else:
        dataItem["styleRef"] = 0
    
    #ulozeni zarovnani
    if para["parfmt"].has_key("alignment"):
        if para["parfmt"]["alignment"] == "qc":
            dataItem["alignment"] = "centered"
        
        elif para["parfmt"]["alignment"] == "qj":
            dataItem["alignment"] = "justified"
        
        elif para["parfmt"]["alignment"] == "ql":
            dataItem["alignment"] = "left"
        
        elif para["parfmt"]["alignment"] == "qr":
            dataItem["alignment"] = "right"
    
    else:
        dataItem["alignment"] = "centered"
    
    #ulozeni lsp
    if para["parfmt"].has_key("slmult"):
        if int(para["parfmt"]["slmult"]) == 1:
            dataItem["lsp"] = "single"
        else:
            dataItem["lsp"] = "exactly"
            
            if para["parfmt"].has_key("sl"):
                dataItem["lspEcaxt"] = abs(int(para["parfmt"]["sl"]))
            
            else:
                dataItem["lspEcaxt"] = int(para["chrfmt"]["fs"])*10
    else:
        dataItem["lsp"] = "exactly"
        dataItem["lspEcaxt"] = int(para["chrfmt"]["fs"])*10
    
    #language
    dataItem["language"] = "en"
    
    #return
    retArray = []
    retArray.append(dataItem)
    return retArray

#TODO: Okomentovat
#@profile
def GetParData(para, data):
    global globSectList
    global globDefchp
    global globDefpap
    
    #ziskani pozice a velikosti odstavce
    retArray = GetPosAndSizePara(para)
    dataItem = retArray[0]
    
    #ziskani ostatnich informaci o odstavci
    retArray = GetOtherParInfo(para, dataItem)
    dataItem = retArray[0]
    
    #ulozeni textu
    dataItem["text"] = para["text"]
    
    if data != []:
        #kontrola, jestli ma odstavec stejnou pozici jako nektery z predeslych
        for item in data:
            if int(para["apoctl"]["posx"]) == int(item["posx"]) and int(para["apoctl"]["posy"]) == int(item["posy"]):
                dataItem["posy"] = data[-1]["posy"] + data[-1]["height"] + data[-1]["sa"]
                samePos = True
                break
    
    #ulozeni odstavce
    data.append(dataItem.copy())
    #TODO: Odstranit!!!
    #print dataItem
    #print ""
    
    #return
    retArray = []
    retArray.append(data)
    return retArray

#TODO: Okomentovat
#@profile
def GetColumns(data):
    global globSectList
    global globDefchp
    global globDefpap
    
    columns = []
    
    for dataItem in data:
        columnItem = {}
        
        if dataItem["width"] > 6000:
            columnItem["type"] = "ONE"
            columnItem["side"] = "NONE"
            columnItem["data"] = dataItem
        else:
            if dataItem["posx"] < 5000:
                columnItem["type"] = "TWO"
                columnItem["side"] = "LEFT"
                columnItem["data"] = dataItem
            else:
                columnItem["type"] = "TWO"
                columnItem["side"] = "RIGHT"
                columnItem["data"] = dataItem
        
        columns.append(columnItem.copy())
    
    #for item in columns:
    #    print item
    #    print ""
    #sys.exit(0)
    
    #return
    retArray = []
    retArray.append(columns)
    return retArray

#TODO: okomentovat!!!
#@profile
def GetPreRunXML(line, textData):
    global globSectList
    global globDefchp
    global globDefpap
    global globFonttbl
    global globExtASCIITable
    
    #print "GetPreRunXML"
    #print "textData"
    #print textData
    #print ""
    
    xml = ""
    next_t = 0
    
    xml += "<ln "
    xml += "l=\"" + str(line["l"]) + "\" "
    xml += "t=\"" + str(line["t"]) + "\" "
    xml += "r=\"" + str(line["r"]) + "\" "
    xml += "b=\"" + str(line["b"]) + "\""
    
    #bez run
    if len(textData) == 1:
        tmpTextData = textData[0]
        
        #baseLine
        xml += " "
        xml += "baseLine=\"" + str(int((line["t"] + line["b"])/2)) + "\" "
        
        #bold
        if tmpTextData["data"].has_key("b") and tmpTextData["data"]["b"]:
            xml += "bold=\"true\" "
        
        #italic
        if tmpTextData["data"].has_key("i") and tmpTextData["data"]["i"]:
            xml += "italic=\"true\" "
        
        #underlined
        if tmpTextData["data"].has_key("ul") and tmpTextData["data"]["ul"]:
            xml += "underlined=\"true\" "
        else:
            xml += "underlined=\"none\" "
        
        #subsuperscript
        xml += "subsuperscript=\"none\" "
        
        #fontSize
        xml += "fontSize=\"" + str(int(tmpTextData["data"]["fs"])*50) + "\" "
        
        #ziskani udaju o fontu
        #TODO: pokud neni tmpTextData, tak nejdrive projit cs a az pak ostatni
        if tmpTextData["data"].has_key("f"):
            tmpFont = tmpTextData["data"]["f"]
        elif globDefchp.has_key("f"):
            tmpFont = globDefchp["f"]
        else:
            tmpFont = 0
        
        fontStyle = ""
        for itemFont in globFonttbl:
            if int(itemFont["f"]) == int(tmpFont):
                fontStyle = itemFont
                break
        
        #fontFace
        try:
            xml += "fontFace=\"" + fontStyle["fontname"] + "\" "
        except TypeError:
            print textData
            print "FONT TABLE"
            print globFonttbl
            print "FONT STYLE"
            print fontStyle
            sys.exit(0)
        
        #fontFamily
        xml += "fontFamily=\"" + fontStyle["fontfamily"] + "\" "
        
        #fontPitch
        xml += "fontPitch=\"variable\" "
        
        #spacing
        xml += "spacing=\"10\""
        
        xml += ">\n"
        
        #<wd>'s
        tmpStr = tmpTextData["text"]
        
        while re.search(r"\\\'((\d{2})|([A-F]{2})|([A-F]\d)|(\d[A-F]))", tmpStr):
            char = re.search(r"\\\'((\d{2})|([A-F]{2})|([A-F]\d)|(\d[A-F]))", tmpStr).group(1)
            
            tmpStr = re.sub(r"\\\'((\d{2})|([A-F]{2})|([A-F]\d)|(\d[A-F]))", globExtASCIITable[char], tmpStr, 1)
        
        #while re.search(r"\\\'09", tmpStr):
        #if re.search(r"\\\'(\d{2})", tmpStr):
        #    tmpStr = re.sub(r"\\\'09", "", tmpStr)
        
        #while re.search(r"\\\'93", tmpStr):
        #if re.search(r"\\\'(\d{2})", tmpStr):
        #    tmpStr = re.sub(r"\\\'93", u"“", tmpStr)
        
        #while re.search(r"\\\'94", tmpStr):
        #if re.search(r"\\\'(\d{2})", tmpStr):
        #    tmpStr = re.sub(r"\\\'94", u"”", tmpStr)
            
            #num = re.search(r"\\\'(\d{2})", tmpStr).group(1)
            
            #sys.stderr.write(num + "\n")
            
            #if int(num) == 9:
                #sys.stderr.write("Konkretni znak zachycen\n")
            #    tmpStr = re.sub(r"\\\'(\d{2})", "", tmpStr)
            
            #if re.search(r"\\\'\0\9", tmpStr):
            #    sys.stderr.write("Konkretni znak zachycen\n")
            #    tmpStr = re.sub(r"\\\'09", "", tmpStr)
            #else:
            #    sys.stderr.write("Konkretni znak nezachycen\n")
            
            #sys.exit(0)
        
        if re.search(r"\\u(d{4}|d{3}\?)", tmpStr):
            tmpStr = re.sub(r"\\u(d{4}|d{3}\?)", "", tmpStr)
        
        if re.search(r"\\tab", tmpStr):
            #print "TAB"
            #print tmpStr
            #print ""
            indexTab = tmpStr.index("\\tab")
            tmpStr = tmpStr[:indexTab] + " " + tmpStr[indexTab:indexTab+len("\\tab")] + " " + tmpStr[indexTab+len("\\tab"):]
            #tmpStr = re.sub(r"\\tab", " \\tab ", tmpStr)
            #print tmpStr
            #print ""
            #sys.exit(0)
        
        new_l = int(line["l"])
        new_t = int(line["t"])
        while tmpStr:
            word = re.match(r"[^\s]*", tmpStr).group(0)
            
            #<wd>
            if word != "":
                xml += "<wd "
                
                #l
                xml += "l=\"" + str(new_l) + "\" "
                
                #t
                xml += "t=\"" + str(new_t) + "\" "
                
                #r
                r = new_l + int(float(tmpTextData["data"]["fs"])*float(len(word))*10.0*(25.0/48.0))
                xml += "r=\"" + str(r) + "\" "
                new_l = r + 100
                
                #b
                b = new_t + int(tmpTextData["data"]["fs"])*10
                
                if next_t < b+50:
                    next_t = b + 50
                
                xml += "b=\"" + str(line["b"]) + "\""
                
                xml += ">" + word + "</wd>\n"
                
                tmpStr = re.sub(r"^[^\s]*", "", tmpStr, 1)
            
            #<tab/>
            if re.match(r"\s+\\tab\s+", tmpStr):
                tmpStr = re.sub(r"^\s+\\tab\s+", "", tmpStr, 1)
                
                xml += "<tab/>\n"
            
            #<space/>
            elif re.match(r"\s+", tmpStr):
                tmpStr = re.sub(r"^\s+", "", tmpStr, 1)
                
                xml += "<space/>\n"
        
        xml += "</ln>\n"
    
    #run
    else:
        xml += ">\n"
        
        new_l = int(line["l"])
        new_t = int(line["t"])
        for tmpTextData in textData:
            xml += "<run "
            
            #baseLine
            xml += "baseLine=\"" + str(int((line["t"] + line["b"])/2)) + "\" "
            
            #bold
            if tmpTextData["data"].has_key("b") and tmpTextData["data"]["b"]:
                xml += "bold=\"true\" "
            
            #italic
            if tmpTextData["data"].has_key("i") and tmpTextData["data"]["i"]:
                xml += "italic=\"true\" "
            
            #underlined
            if tmpTextData["data"].has_key("ul") and tmpTextData["data"]["ul"]:
                xml += "underlined=\"true\" "
            else:
                xml += "underlined=\"none\" "
            
            #subsuperscript
            xml += "subsuperscript=\"none\" "
            
            #fontSize
            xml += "fontSize=\"" + str(int(tmpTextData["data"]["fs"])*50) + "\" "
            
            #ziskani udaju o fontu
            if tmpTextData["data"].has_key("f"):
                tmpFont = tmpTextData["data"]["f"]
            elif globDefchp.has_key("f"):
                tmpFont = globDefchp["f"]
            else:
                tmpFont = "0"
            
            fontStyle = ""
            for itemFont in globFonttbl:
                if itemFont["f"] == tmpFont:
                    fontStyle = itemFont
                    break
            
            #fontFace
            xml += "fontFace=\"" + fontStyle["fontname"] + "\" "
            
            #fontFamily
            xml += "fontFamily=\"" + fontStyle["fontfamily"] + "\" "
            
            #fontPitch
            xml += "fontPitch=\"variable\" "
            
            #spacing
            xml += "spacing=\"10\""
            
            xml += ">\n"
            
            #<wd>'s
            tmpStr = tmpTextData["text"]
            
            while re.search(r"\\\'((\d{2})|([A-F]{2})|([A-F]\d)|(\d[A-F]))", tmpStr):
                char = re.search(r"\\\'((\d{2})|([A-F]{2})|([A-F]\d)|(\d[A-F]))", tmpStr).group(1)
                
                tmpStr = re.sub(r"\\\'((\d{2})|([A-F]{2})|([A-F]\d)|(\d[A-F]))", globExtASCIITable[char], tmpStr, 1)
            
            #while re.search(r"\\\'09", tmpStr):
            #if re.search(r"\\\'(\d{2})", tmpStr):
            #    tmpStr = re.sub(r"\\\'09", "", tmpStr)
            
            #while re.search(r"\\\'93", tmpStr):
            #if re.search(r"\\\'(\d{2})", tmpStr):
            #    tmpStr = re.sub(r"\\\'93", u"“", tmpStr)
            
            #while re.search(r"\\\'94", tmpStr):
            #if re.search(r"\\\'(\d{2})", tmpStr):
            #    tmpStr = re.sub(r"\\\'94", u"”", tmpStr)
            
            if re.search(r"\\u(d{4}|d{3}\?)", tmpStr):
                tmpStr = re.sub(r"\\u(d{4}|d{3}\?)", "", tmpStr)
            
            if re.search(r"\\tab", tmpStr):
                #print "TAB"
                #print tmpStr
                #print ""
                indexTab = tmpStr.index("\\tab")
                tmpStr = tmpStr[:indexTab] + " " + tmpStr[indexTab:indexTab+len("\\tab")] + " " + tmpStr[indexTab+len("\\tab"):]
                #tmpStr = re.sub(r"\\tab", " \\tab ", tmpStr)
                #print tmpStr
                #print ""
                #sys.exit(0)
            
            while tmpStr:
                word = re.match(r"[^\s]*", tmpStr).group(0)
                
                #<wd>
                if word != "":
                    xml += "<wd "
                    
                    #l
                    xml += "l=\"" + str(new_l) + "\" "
                    
                    #t
                    xml += "t=\"" + str(new_t) + "\" "
                    
                    #r
                    r = new_l + int(float(tmpTextData["data"]["fs"])*float(len(word))*10.0*(25.0/48.0))
                    xml += "r=\"" + str(r) + "\" "
                    new_l = r + 100
                    
                    #b
                    b = new_t + int(tmpTextData["data"]["fs"])*10
                    
                    if next_t < b+50:
                        next_t = b + 50
                    
                    xml += "b=\"" + str(line["b"]) + "\""
                    
                    xml += ">" + word + "</wd>\n"
                    
                    tmpStr = re.sub(r"^[^\s]*", "", tmpStr, 1)
                
                #<tab/>
                if re.match(r"\s+\\tab\s+", tmpStr):
                    tmpStr = re.sub(r"^\s+\\tab\s+", "", tmpStr, 1)
                    
                    xml += "<tab/>\n"
                
                #<space/>
                elif re.match(r"\s+", tmpStr):
                    tmpStr = re.sub(r"^\s+", "", tmpStr, 1)
                    
                    xml += "<space/>\n"
            
            xml += "</run>\n"
        
        xml += "</ln>\n"
    
    #return
    retArray = []
    retArray.append(xml)
    retArray.append(next_t)
    return retArray

#TODO: okomentovat!!!
#@profile
def GetPreLinesXML(para):
    global globSectList
    global globDefchp
    global globDefpap
    
    #print "GetPreLinesXML"
    
    preLinesXML = {}
    
    textData = para["data"]["text"]
    
    lines = []
    actLine = {}
    preLine = {}
    tmpStr = ""
    prevText = []
    next_t = 0
    for item in textData:
        #odstraneni zbytecnosti
        item["text"] = re.sub(r"\r\n", "", item["text"])
        
        #ulozeni textu
        tmpStr = item["text"]
        
        #ziskani casti radku, pripadne celeho radku
        while re.search(r"\\line", tmpStr):
            #index, na kterem se nachazi oddelovat radku
            indexLine = tmpStr.index("\\line")
            
            #ulozeni retezce radku
            tmpText = tmpStr[:indexLine]
            
            #odstraneni retezce radku
            tmpStr = tmpStr[indexLine+len("\\line"):]
            
            #ulozeni informaci o textu radku
            tmpData = {}
            tmpData["text"] = tmpText
            tmpData["data"] = item["data"]
            
            #ulozeni ke zbytku radku
            prevText.append(tmpData.copy())
            
            if len(lines) != 0:
                actLine["t"] = lines[-1]["b"]
            else:
                #print "PARA"
                #print para
                actLine["t"] = para["data"]["posy"]
                #actLine["t"] = next_t
            
            actLine["l"] = para["data"]["posx"]
            actLine["r"] = para["data"]["posx"] + para["data"]["width"]
            actLine["b"] = actLine["t"] + int(float(tmpData["data"]["fs"])*10.0)
            #actLine["text"] = prevText
            
            retArray = GetPreRunXML(actLine, prevText)
            actLine["text"] = retArray[0]
            
            #ulozeni radku
            lines.append(actLine.copy())
            
            #vycisteni
            prevText = []
            actLine = {}
        
        tmpData = {}
        tmpData["text"] = tmpStr
        tmpData["data"] = item["data"]
        
        prevText.append(tmpData.copy())
    
    if len(lines) != 0:
        actLine["t"] = lines[-1]["b"]
    else:
        actLine["t"] = para["data"]["posy"]
    
    actLine["l"] = para["data"]["posx"]
    actLine["r"] = para["data"]["posx"] + para["data"]["width"]
    
    try:
        actLine["b"] = actLine["t"] + int(float(item["data"]["fs"])*10.0)
    except UnboundLocalError:
        print "Exception err"
        print para
        sys.exit(0)
    
    retArray = GetPreRunXML(actLine, prevText)
    actLine["text"] = retArray[0]
    
    lines.append(actLine.copy())
    
    #print "LINES"
    #for item in lines:
    #    print item["text"]
    #print lines
    #print ""
    
    #return
    retArray = []
    retArray.append(lines)
    return retArray
    
    #print "LINE"
    #print lines
    #sys.exit(0)
    

#TODO: okomentovat!!!
#@profile
def GetPreParaXML(para):
    global globSectList
    global globDefchp
    global globDefpap
    
    xml = ""
    
    #print "GetPreParaXML"
    
    preParaXML = {}
    
    #ulozeni informaci o pozici a velikosti
    preParaXML["t"] = para["data"]["posy"]
    preParaXML["l"] = para["data"]["posx"]
    preParaXML["r"] = para["data"]["posx"] + para["data"]["width"]
    preParaXML["b"] = para["data"]["posy"] + para["data"]["height"]
    
    #ulozeni dalsich informaci
    preParaXML["li"] = para["data"]["li"]
    preParaXML["sa"] = para["data"]["sa"]
    preParaXML["alignment"] = para["data"]["alignment"]
    preParaXML["lsp"] = para["data"]["lsp"]
    
    if para["data"].has_key("lspEcaxt"):
        preParaXML["lspEcaxt"] = para["data"]["lspEcaxt"]
    
    preParaXML["language"] = para["data"]["language"]
    preParaXML["styleRef"] = para["data"]["styleRef"]
    
    #zpracovani textu
    retArray = GetPreLinesXML(para)
    preParaXML["lines"] = retArray[0]
    
    xml += "<para "
    xml += "l=\"" + str(preParaXML["l"]) + "\" "
    xml += "t=\"" + str(preParaXML["t"]) + "\" "
    xml += "r=\"" + str(preParaXML["r"]) + "\" "
    xml += "b=\"" + str(preParaXML["b"]) + "\" "
    xml += "li=\"" + str(preParaXML["li"]) + "\" "
    xml += "sa=\"" + str(preParaXML["sa"]) + "\" "
    xml += "alignment=\"" + str(preParaXML["alignment"]) + "\" "
    xml += "lsp=\"" + str(preParaXML["lsp"]) + "\" "
    
    if preParaXML.has_key("lspEcaxt"):
        xml += "lspEcaxt=\"" + str(preParaXML["lspEcaxt"]) + "\" "
    
    xml += "language=\"" + str(preParaXML["language"]) + "\" "
    xml += "styleRef=\"" + str(preParaXML["styleRef"]) + "\">\n"
    
    for line in preParaXML["lines"]:
        xml += line["text"]
    
    xml += "</para>\n"
    
    preParaXML["text"] = xml
    
    #return
    retArray = []
    retArray.append(preParaXML)
    return retArray

#TODO: okomentovat!!!
#@profile
def MakeXmlSection(xml, section):
    global globSectList
    global globDefchp
    global globDefpap
    
    #print "Defchp"
    #print globDefchp
    #sys.exit(0)
    
    """
    firstPara = section[0]
    xml += "<section l=\"" + str(firstPara["apoctl"]["posx"]) + "\" t=\"" + str(firstPara["apoctl"]["posy"]) + "\" "
    
    #RTF dokument obsahoval informace o velikosti odstavce
    if firstPara["apoctl"].has_key("absw"):
        xml += "r=\"" + str(int(firstPara["apoctl"]["posx"]) + abs(int(firstPara["apoctl"]["absw"]))) + "\" "
        xml += "b=\"" + str(int(firstPara["apoctl"]["posy"]) + abs(int(firstPara["apoctl"]["absh"]))) +"\">\n"
        
        #<column>
        xml += "<column l=\"" + str(firstPara["apoctl"]["posx"]) + "\" t=\"" + str(firstPara["apoctl"]["posy"]) + "\" "
        xml += "r=\"" + str(int(firstPara["apoctl"]["posx"]) + abs(int(firstPara["apoctl"]["absw"]))) + "\" "
        xml += "b=\"" + str(int(firstPara["apoctl"]["posy"]) + abs(int(firstPara["apoctl"]["absh"]))) +"\">\n"
    
    else:
        #Kdyz nebyl zadan udaj o velikosti odstavce, je nutne jej spocitat.
        #Proto je nutne nejdrive ziskat delku radku odstavce ve znacich.
        tmpStr = ""
        lineSize = 0
        lineFounded = False
        for para in section:
            for textData in para["text"]:
                if not re.search(r"\\line", textData["text"]):
                    tmpStr += textData["text"]
                
                else:
                    lineSize = textData["text"].index("\\line") + len(tmpStr)
                    lineFounded = True
                    break
            
            if lineFounded:
                break
        
        sys.stderr.write("Kontrolni ukonceni MakeXml()\n")
        print "Delka radku je:"
        print lineSize
        sys.exit(0)
        
        #pokud odstavec pbsahoval informace o velikosti fontu
        #TODO: Opravit bottom, je hloupost, aby section mel velikost prave jednoho radku
        if firstPara["chrfmt"].has_key("fs"):
            lineSize = int(float(firstPara["chrfmt"]["fs"])*float(lineSize)*10.0*(25.0/48.0))
            lineHeight = int(float(firstPara["chrfmt"]["fs"])*10.0*(25.0/48.0))
        
        else:
            lineSize = int(float(globDefchp["fs"])*float(lineSize)*10.0*(25.0/48.0))
            lineHeight = int(float(globDefchp["fs"])*10.0*(25.0/48.0))
                
        xml += "r=\"" + str(int(firstPara["apoctl"]["posx"]) + lineSize) + "\" "
        xml += "b=\"" + str(int(firstPara["apoctl"]["posy"]) + lineHeight) +"\">\n"
            
        #<column>
        xml += "<column l=\"" + str(firstPara["apoctl"]["posx"]) + "\" t=\"" + str(firstPara["apoctl"]["posy"]) + "\" "
        xml += "r=\"" + str(int(firstPara["apoctl"]["posx"]) + lineSize) + "\" "
        xml += "b=\"" + str(int(firstPara["apoctl"]["posy"]) + lineHeight) +"\">\n"
    """
    
    #<para>
    data = []
    #print "DATA"
    for para in section:
        #print "PARA"
        #print para
        #odstavce je nutne nejdrive upravit, aby mel kazdy svou vlastni polohu.
        retArray = GetParData(para, data)
        data = retArray[0]
    #sys.exit(0)
    
    #rozdeleni na sloupce
    retArray = GetColumns(data)
    columns = retArray[0]
    
    #print "COLUMNs"
    #print columns
    
    #rozdeleni na sekce
    type = "NONE"
    side = "UNDEF"
    sections = []
    actSection = {}
    columnsArr = []
    actColumn = {}
    prePara = {}
    for para in columns:
        #print "TYPE"
        #print type
        #print "SIDE"
        #print side
        #print "PARA"
        #print para
        #print ""
        #zmena typu odstavce, musi se vytvorit novy section
        if para["type"] != type or (para["side"] == "LEFT" and side == "RIGHT"):
            #print "ZMENA SEKCE"
            #section a column by mely mit bottom hodnotu posledniho odstavce v dane sekci ci sloupci
            #proto se bude ukladat hodnota az pri zmene na jinoou sekci.
            if not prePara == {}:
                #print "PrePara neprazdna!!"
                try:
                    actSection["b"] = prePara["data"]["posy"] + prePara["data"]["height"]
                except KeyError:
                    sys.stderr.write("MakeXmlSection() error\n")
                    print "PREPARA"
                    print prePara
                    sys.exit(0)
                
                actSection["r"] = prePara["data"]["posx"] + prePara["data"]["width"]
                actColumn["b"] = prePara["data"]["posy"] + prePara["data"]["height"]
                
                #ulozeni sloupce do pole sloupcu
                columnsArr.append(actColumn.copy())
                
                #print "COLUMNARR"
                #print columnsArr
                #print ""
                
                #ulozeni sloupcu do aktualni sekce
                actSection["data"].append(columnsArr)
                
                #ulozeni aktualni sekce do pole sekci
                sections.append(actSection.copy())
                
                #vycisteni promennych
                actColumn = {}
                actSection = {}
                columnsArr = []
                
            #naplneni promennych novymi hodnotami
            actSection["t"] = para["data"]["posy"]
            actSection["l"] = para["data"]["posx"]
            actSection["data"] = []
            
            actColumn["t"] = para["data"]["posy"]
            actColumn["l"] = para["data"]["posx"]
            actColumn["r"] = para["data"]["posx"] + para["data"]["width"]
            actColumn["data"] = []
            
            #nastaveni informace o novem sloupci
            type = para["type"]
            side = para["side"]
        
        #meni se sloupce
        elif para["side"] == "RIGHT" and side == "LEFT":
            #print "ZMENA SLOUPCE"
            if not prePara == {}:
                #print "prePara neprazdna!!"
                try:
                    actColumn["b"] = prePara["data"]["posy"] + prePara["data"]["height"]
                except KeyError:
                    sys.stderr.write("MakeXmlSection() error\n")
                    print "PREPARA"
                    print prePara
                    sys.exit(0)
                
                #ulozeni sloupce do pole sloupcu
                columnsArr.append(actColumn.copy())
                
                #vycisteni promennych
                actColumn = {}
                
            #naplneni promennych novymi hodnotami                
            actColumn["t"] = para["data"]["posy"]
            actColumn["l"] = para["data"]["posx"]
            actColumn["r"] = para["data"]["posx"] + para["data"]["width"]
            actColumn["data"] = []
            
            #nastaveni informace o novem sloupci
            side = para["side"]
        
        if para["data"]["text"] != []:
            retArray = GetPreParaXML(para)
            preParaXML = retArray[0]
            #print "PREPARA XML OUT"
            #print preParaXML
            #print ""
            
            actColumn["data"].append(preParaXML)
            #actColumn["data"].append(para)
            prePara = para.copy()
    
    #ulozeni zbytku
    try:
        actSection["b"] = prePara["data"]["posy"] + prePara["data"]["height"]
    except KeyError:
        sys.stderr.write("MakeXmlSection() error\n")
        print section
        print "COLUMNs"
        print columns
        print "PREPARA"
        print prePara
        sys.exit(0)
    
    actSection["r"] = prePara["data"]["posx"] + prePara["data"]["width"]
    actColumn["b"] = prePara["data"]["posy"] + prePara["data"]["height"]
                
    #ulozeni sloupce do pole sloupcu
    columnsArr.append(actColumn.copy())
                
    #print columnsArr
    #print ""
                
    #ulozeni sloupcu do aktualni sekce
    actSection["data"].append(columnsArr)
                
    #ulozeni aktualni sekce do pole sekci
    sections.append(actSection.copy())
    
    #print "SECTIONS"
    #print sections
    
    xml = ""
    
    #print "SECTIONS OUT"
    for itemSec in sections:
        #print "SECTION"
        xml += "<section "
        xml += "l=\"" + str(itemSec["l"]) + "\" "
        xml += "t=\"" + str(itemSec["t"]) + "\" "
        xml += "r=\"" + str(itemSec["r"]) + "\" "
        xml += "b=\"" + str(itemSec["b"]) + "\">\n"
        for itemCols in itemSec["data"]:
            #print "COLUMNs"
            for itemCol in itemCols:
                #print itemCol
                #print "COLUMN"
                #print itemCol
                #sys.exit(0)
                xml += "<column "
                xml += "l=\"" + str(itemCol["l"]) + "\" "
                xml += "t=\"" + str(itemCol["t"]) + "\" "
                xml += "r=\"" + str(itemCol["r"]) + "\" "
                xml += "b=\"" + str(itemCol["b"]) + "\">\n"
                for itemPara in itemCol["data"]:
                    #print itemPara
                    #sys.exit(0)
                    xml += itemPara["text"]
                    #print itemPara
                    #print ""
                
                xml += "</column>\n"
        xml += "</section>\n"
    
    #print xml.encode('utf-8').strip()
    
    #return
    retArray = []
    retArray.append(xml)
    return retArray
    
    #print xml
    #sys.exit(0)

#TODO: Pripadne upravit
#@profile
def MakeXml():
    global globSectList
    global globDefchp
    global globDefpap
    
    
    xml = "<document>\n"
    #<section>
    for section in globSectList:
        if section:
            xml += "<page>\n"
            xml += "<body>\n"
            retArray = MakeXmlSection(xml, section)
            xml += retArray[0]
            xml += "</body>\n"
            xml += "</page>\n"
    
    xml += "</document>"
    
    #return
    retArray = []
    retArray.append(xml)
    return retArray

"""
def main():
    #input = "./aaaa83f2a1c88eb9c5d0e8a2bcc67980dba996d6_new.rtf"
    #input = "./aaaa15efd6d20b278a9b9ec862ef3124a9b750bf_new.rtf"
    input = "./aaaa15efd6d20b278a9b9ec862ef3124a9b750bf.rtf"
    readedData = LoadRTF(input)
    #print readedData
    #sys.exit(0)
    ParseRTF(readedData)

main()
"""
