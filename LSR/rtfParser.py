#!/usr/bin/python

import sys
import re
import os
import codecs 

#pokud se parser doimplementovava, tak zapnout!!!!!
imp_mode = True
inputLSR = ""
input = sys.argv[1]

RTF_ROOT = 0
RTF_HEADER = 1
RTF_DOCUMENT = 2

""" TRIDA PRO PARSER RTF """
class RTFUnit:
    def __init__(self):
        self.version = 0
        self.characterSet = ""
        self.characterCodePage = 0
        self.unicodeEnabled = False
        self.defLang = 0
        self.adefLang = 0
        self.defLangFe = 0
        self._from = ""
        self.defFont = 0
        self.defAFont = 0
        self.stshfloch = 0
        self.stshfhich = 0
        self.stshfbi = 0
        self.stshfdbch = 0
        self.data = 0
        self.init = True
        #vychozi
        #default properties characters
        self.defFs = 24
        self.defAFs = 24
        self.defLoch = False
        self.defHich = False
        self.defdbch = False
        #default properties paragraph
        self.defCGrid = 0
        self.defLi = 0
        self.defRi = 0
        self.defAF = 0
        self.defBidirectControls = "ltrpar"
        self.defAligment = "ql"
        self.defFi = 0
        self.defSb = 0
        self.defSa = 0
        self.defSl = 0
        self.defSlmult = 1
        self.defAdjustRight = False
        #autospacing DCB english
        self.defAspAlpha = False
        #autospacing DCB num
        self.defAspNum = False
        #Font alignment the default setting for this is auto
        self.defFaAuto = "Auto"
        #FontInfo
        self.fontInfo = []
        #style sheet table
        self.styleSheetTable = []
        #color table
        self.colorTable = []
        #list table
        self.listTable = []
        #list override table
        self.listOverrideTable = []
        #formatting
        self.brdrdef = {
                        "brdrt":"", 
                        "brdrb":"", 
                        "brdrl":"", 
                        "brdrr":"", 
                        "brdrbtw":"", 
                        "brdrbar":"", 
                        "box":"", 
                        "brdrs":"", 
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
                        "brdrtnthtnlg":"", 
                        "brdrwavy":"", 
                        "brdrwavydb":"", 
                        "brdrdashdotstr":"", 
                        "brdremboss":"", 
                        "brdrengrave":"", 
                        "brdroutset":"", 
                        "brdrnone":"", 
                        "brdrtbl":"", 
                        "brdrnil":"", 
                        "brdrw":"", 
                        "brsp":"", 
                        "brdrcf":""}
        #<parfmt>
        self.parfmt = {
                        "par":"", 
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
                        "aspalpha":"", 
                        "aspnum":"", 
                        "faauto":"", 
                        "adjustright":"", 
                        "cgrid":"", 
                        "li":"", 
                        "ri":"", 
                        "ltrpar":"", 
                        "ql":"", 
                        "fi":"", 
                        "sb":"", 
                        "sa":"", 
                        "sl":"", 
                        "slmult":"", 
                        "lang":"", 
                        "langfe":"", 
                        "f":"", 
                        "fs":"", 
                        "afs":"", 
                        "charscalex":"", 
                        "expndtw":"", 
                        "qc":"", 
                        "qj":"", 
                        "qr":""}
        #<apoctl>
        self.apoctl = {
                        "absw":"", 
                        "absh":"", 
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
                        "nowrap":"", 
                        "dxfrtext":"", 
                        "dfrmtxtx":"", 
                        "dfrmtxty":"", 
                        "wrapdefault":"", 
                        "wraparound":"", 
                        "wraptight":"", 
                        "wrapthrough":"", 
                        "dropcapli":"", 
                        "dropcapt":"", 
                        "frmtxbtlr":"", 
                        "frmtxlrtb":"", 
                        "frmtxlrtbv":"", 
                        "frmtxtbrl":"", 
                        "frmtxtbrlv":"", 
                        "absnoovrlp":""}
        #<tabdef>
        self.tabdef = {
                        "tqr":"", 
                        "tqr":"", 
                        "tqdec":"", 
                        "tldot":"", 
                        "tlmdot":"", 
                        "tlhyph":"", 
                        "tlul":"", 
                        "tlth":"", 
                        "tleq":"", 
                        "tx":"", 
                        "tb":"", 
                        "tqc":""}
        #<shading>
        self.shading = {
                                "shading":"", 
                                "bghoriz":"", 
                                "bgvert":"", 
                                "bgfdiag":"", 
                                "bgbdiag":"", 
                                "bgdcross":"", 
                                "bgcross":"", 
                                "bgdkhoriz":"", 
                                "bgdkvert":"", 
                                "bgdkfdiag":"", 
                                "bgdkbdiag":"", 
                                "bgdkcross":"", 
                                "bgdkdcross":"", 
                                "cfpat":"", 
                                "cbpat":""}
        #<chrfmt>
        self.chrfmt = {
                                "cf":"", 
                                "dn":"", 
                                "ul":"", 
                                "b":"", 
                                "i":"", 
                                "strike":"", 
                                "scaps":"", 
                                "plain":"", 
                                "overlay":"", 
                                "cs":"", 
                                "listtext":"", 
                                "ls":"", 
                                "ilvl":"", 
                                "sub":"", 
                                "super":""}
        #<docfmt>
        self.docfmt = {
                                "paperw":"", 
                                "paperh":"", 
                                "margb":"", 
                                "margl":"", 
                                "margr":"", 
                                "margt":"", 
                                "gutter":"", 
                                "viewkind":"", 
                                "viewzk":"", 
                                "fet":"", 
                                "ftnlytwnine":"", 
                                "facingp":"", 
                                "splytwnine":"", 
                                "htmautsp":"", 
                                "useltbaln":"",
                                "alntblind":"", 
                                "lytcalctblwd":"", 
                                "lyttblrtgr":"", 
                                "lnbrkrule":"", 
                                "nobrkwrptbl":"", 
                                "snaptogridincell":"", 
                                "allowfieldendsel":"", 
                                "wrppunct":"", 
                                "asianbrkrule":"", 
                                "newtblstyruls":"", 
                                "nogrowautofit":"", 
                                "usenormstyforlist":"", 
                                "noindnmbrts":"", 
                                "felnbrelev":"", 
                                "nocxsptable":"", 
                                "indrlsweleven":"", 
                                "noafcnsttbl":"", 
                                "afelev":"", 
                                "utinl":"", 
                                "hwelev":"", 
                                "spltpgpar":"", 
                                "notcvasp":"", 
                                "notvatxbx":"", 
                                "krnprsnet":"", 
                                "cachedcolbal":"", 
                                "noxlattoyen":"", 
                                "expshrtn":"", 
                                "noultrlspc":"", 
                                "dntblnsbdb":"", 
                                "nospaceforul":"", 
                                "nolnhtadjtbl":"", 
                                "notbrkcnstfrctbl":"", 
                                "dgmargin":"", 
                                "dghspace":"", 
                                "dgvspace":"", 
                                "dghshow":"", 
                                "dgvshow":""}
        self.secfmt = {
                                "sectd":"", 
                                "ltrsect":"", 
                                "headery":"", 
                                "footery":"", 
                                "colsx":"", 
                                "sectlinegrid":"", 
                                "sftnbj":"", 
                                "sftnrstcont":"", 
                                "sect":"", 
                                "lndscpsxn":""}
        self.spec = {
                                "line":"", 
                                "tab":""}
        self.tbldef = {
                                "tr":"", 
                                "trowd":"", 
                                "trql":"", 
                                "trrh":"", 
                                "clvertalt":"", 
                                "clcbpat":"", 
                                "clcbpatraw":"", 
                                "cellx":"", 
                                "clvertalt":"", 
                                "clbrdrl":"", 
                                "brdrs":"", 
                                "brdrw":"", 
                                "clbrdrt":"", 
                                "clbrdrr":"", 
                                "cell":"", 
                                "row":"", 
                                "clbrdrb":"", 
                                "clvmgf":"", 
                                "clvmrg":"", 
                                "cltxtbrl":""}
        self.hexTable = {
                            "09":"",
                            "80":"", 
                            "84":"", 
                            "8A":"",
                            "8C":"",  
                            "8D":"", 
                            "8E":"", 
                            "91":"", 
                            "92":"", 
                            "93":"", 
                            "94":"", 
                            #TODO: ZMENIT!!!!
                            "95":"", 
                            "97":"",
                            "99":"", 
                            "9A":"", 
                            "9C":"", 
                            "9D":"", 
                            "9E":"", 
                            "9F":"", 
                            "A1":"", 
                            "A3":"", 
                            "A5":"", 
                            "A7":"", 
                            "A9":"", 
                            "AB":"", 
                            "AE":"",
                            "B0":"",
                            "B1":"", 
                            "BB":"", 
                            "BF":"",
                            "C0":"", 
                            "C1":"", 
                            "C2":"", 
                            "C4":"", 
                            "C6":"", 
                            "C7":"", 
                            "C8":"", 
                            "C9":"", 
                            "CA":"", 
                            "CB":"", 
                            "CC":"", 
                            "CD":"", 
                            "CE":"", 
                            "CF":"", 
                            "D1":"", 
                            "D2":"", 
                            "D3":"", 
                            "D4":"", 
                            "D6":"", 
                            "D8":"", 
                            "D9":"", 
                            "DA":"", 
                            "DB":"", 
                            "DC":"", 
                            "DD":"", 
                            "DF":"", 
                            "E0":"", 
                            "E1":"", 
                            "E2":"", 
                            "E4":"", 
                            "E6":"", 
                            "E7":"", 
                            "E8":"", 
                            "E9":"", 
                            "EA":"", 
                            "EB":"", 
                            "EC":"", 
                            "ED":"", 
                            "EE":"", 
                            "EF":"", 
                            "F1":"", 
                            "F2":"", 
                            "F3":"", 
                            "F4":"", 
                            "F6":"", 
                            "F8":"", 
                            "F9":"", 
                            "FA":"",
                            "FB":"", 
                            "FC":"", 
                            "FD":"", 
                            "FF":""}
        #document
        #info
        self.creatim = {}
        self.revtim = {}
        self.printim = {}
        self.buptim = {}
        self.infoDic = {}
        self.ftnsepDic = {}
        self.bookmarks = []
        self.stack = []
        self.plainText = []
        self.richText = []
        self.line = []
        self.linePos = 0
        self.wordPos = 0
        self.par = False
        self.xmlList = []
        self.xmlParaList = []
        self.xmlSortedPars = []
        self.xmlOutput = ""
        self.special = "txt"
        #Nastaveni pro tabulku
        self.tableSettings = {}
    
    def LoadFile(self, inputFile):
        #sys.stderr.write(inputFile+"\n")
        #sys.exit(0)
        global inputLSR
        inputLSR = inputFile
        
        try:
            file = open(inputFile, "rt")
        except IOError:
            sys.stderr.write("RTFParser: Chyba pri otevirani souboru\n")
            sys.exit(1)
        
        try:
            filedata = file.read()
            file.close()
        except UnicodeDecodeError:
            sys.stderr.write("Chyba: Nelze nacist vstupni soubor")
            sys.exit(1)
            
        self.ParseRTF(filedata)
        
    def ParseRTF(self, readedData):
        self.data = 0
        xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        #print readedData
        #sys.exit(0)
        #vyparsovani vychozich hodnot
        self.LoadRTFDef(self, readedData)
        #odstraneni jiz nactenych vychozich hodnot
        readedData = re.sub("^\{[^\{]*", "", readedData, 1)
        #vyparsovani hlavicky a dokumentu RTF souboru
        xml += "<rtf><header>"
        result = self.LoadRTF(self, readedData)
        
    def LoadRTFDef(self, currentObject, readedData):
        #sys.stderr.write(readedData[:64]+"\n")
        try:
            defReadedData = re.search("^\{[^\{]*", readedData).group(0)
        except AttributeError:
            print "Soubor nelze precist!"
            sys.exit(1)
        
        #nastaveni vychozich hodnot
        if re.search(r"^{", defReadedData) != None:
            defReadedData = re.sub(r"^{", "", defReadedData, 1)
            #verze RTF souboru
            if re.search(r"^\\rtf", defReadedData) != None:
                version = re.search(r"^\\rtf(\d+)", defReadedData)
                self.version = version.group(1)
                defReadedData = re.sub(r"^\\rtf\d+(\s{1})?", "", defReadedData, 1)
            else:
                sys.stderr.write("Chyba: Spatny format RTF\n")
                sys.exit(1)
            #\fbidis?
            #character set
            if re.search(r"^\\\w+", defReadedData) != None:
                self.characterSet = re.search(r"^\\(\w+)", defReadedData).group(1)
                defReadedData = re.sub(r"^\\\w+(\s{1})?", "", defReadedData, 1)
                #character code page
                if re.search(r"^\\ansicpg\d+", defReadedData) != None:
                    charCodePage = re.search(r"\\ansicpg(\d+)", defReadedData)
                    self.characterCodePage = charCodePage.group(1)
                    defReadedData = re.sub(r"\\ansicpg\d+(\s{1})?", "", defReadedData, 1)
            else:
                sys.stderr.write("Chyba: Spatny format RTF\n")
                sys.exit(1)
            #unicode enabled
            if re.search(r"^\\uc\d+", defReadedData) != None:
                self.unicodeEnabled = True
                defReadedData = re.sub(r"\\uc\d+(\s{1})?", "", defReadedData, 1)
            #default fonts and languages
            #<from>
            if re.search(r"^\\from(text|html)", defReadedData) != None:
                _from = re.search(r"\\from((text|html))", defReadedData)
                self._from = _from.group(1)
                defReadedData = re.sub(r"\\from(text|html)(\s{1})?", "", defReadedData, 1)
            #problem: Podle definice RTF se nejdrive definuje vychozi font a pak
            #jazyk, ale setkal jsem se i s pripadem, kdy byl jazyk s fontem
            #prohozeny, takze jsem parser napsal tak, aby mu na poradi jazyka
            # a fontu nezalezelo, ale musi tam byt oba pro dodrzeni definice
            defLangFound = False
            defFontFound = False
            #<deffont>
            if re.search(r"(\\deff\d+(\s{1})?)?(\\adeff\d+(\s{1})?)?(\\stshfdbch\d+(\s{1})?\\stshfloch\d+(\s{1})?\\stshfhich\d+(\s{1})?\\stshfbi\d+(\s{1})?)?", defReadedData) != None:
                defFontFound = True
                #default font
                if re.search(r"\\deff\d+", defReadedData) != None:
                    defFont = re.search(r"\\deff(\d+)", defReadedData)
                    self.defFont = defFont.group(1)
                    defReadedData = re.sub(r"\\deff(\d+)(\s{1})?", "", defReadedData, 1)
                #default BiDi font
                if re.search(r"\\adeff\d+", defReadedData) != None:
                    defAFont = re.search(r"\\deff(\d+)", defReadedData)
                    self.defAFont = defAFont.group(1)
                    defReadedData = re.sub(r"\\adeff(\d+)(\s{1})?", "", defReadedData, 1)
                #style sheets
                if re.search(r"(\\stshfdbch\d+(\s{1})?|\\stshfloch\d+(\s{1})?|\\stshfhich\d+(\s{1})?|\\stshfbi\d+(\s{1})?){4}", defReadedData) != None:
                    stsh = re.search(r"\\stshfdbch(\d+)(\s{1})?", defReadedData)
                    self.stshfdbch = stsh.group(1)
                    defReadedData = re.sub(r"\\stshfdbch(\d+)(\s{1})?", "", defReadedData, 1)
                    stsh = re.search(r"\\stshfloch(\d+)(\s{1})?", defReadedData)
                    self.stshfloch = stsh.group(1)
                    defReadedData = re.sub(r"\\stshfloch(\d+)(\s{1})?", "", defReadedData, 1)
                    stsh = re.search(r"\\stshfhich(\d+)(\s{1})?", defReadedData)
                    self.stshfhich = stsh.group(1)
                    defReadedData = re.sub(r"\\stshfhich(\d+)(\s{1})?", "", defReadedData, 1)
                    stsh = re.search(r"\\stshfbi(\d+)(\s{1})?", defReadedData)
                    self.stshfbi = stsh.group(1)
                    defReadedData = re.sub(r"\\stshfbi(\d+)(\s{1})?", "", defReadedData, 1)
            #<deflang>
            if re.search(r"\\deflang\d+", defReadedData) != None:
                defLangFound = True
                defLang = re.search(r"\\deflang(\d+)", defReadedData)
                self.defLang = defLang.group(1)
                defReadedData = re.sub(r"\\deflang\d+(\s{1})?", "", defReadedData, 1)
            if re.search(r"\\adeflang\d+", defReadedData) != None:
                defLangFound = True
                adefLang = re.search(r"\\adeflang(\d+)", defReadedData)
                self.adefLang = adefLang.group(1)
                defReadedData = re.sub(r"\\adeflang\d+(\s{1})?", "", defReadedData, 1)
            if re.search(r"\\deflangfe\d+", defReadedData) != None:
                defLangFound = True
                defLangFe = re.search(r"\\deflangfe(\d+)", defReadedData) 
                self.defLangFe = defLangFe.group(1)
                defReadedData = re.sub(r"\\deflangfe\d+(\s{1})?", "", defReadedData, 1)
            #kontrola, zda byla zadana aspon jedna polozka z <deffont> a <deflang>
            if not (defFontFound and defLangFound):
                sys.stderr.write("Chyba: Spatny format RTF\n")
                sys.exit(1)
            #kontrola, zda bylo pred prvni skupinou vse precteno
            if defReadedData:
                sys.stderr.write("Chyba: v bufferu zustalo: " + defReadedData + "\n")
                sys.exit(1)
        else:
            sys.stderr.write("Chyba: Spatny format RTF\n")
            sys.exit(1)
        
    def LoadRTF(self, currentObject, readedData):
        xml = ""
        retArray = []
        tmpArray = []
        global imp_mode
        
        readedData = re.sub(r"\x0D\x0A", "", readedData)
        readedData = re.sub(r"\\line", "\\line ", readedData)
        
        if not imp_mode:
            sys.stderr.write("RTFParser: Ostry mod zapnut!\n")
            
        while readedData != "}":
            #<themedata>
            #momentalne neni implementovano
            #<colorschememapping>
            #momentalne neni implementovano
            #sys.stderr.write(readedData[:10]+"\n")
            #print readedData
            #sys.exit(0)
            
            if not readedData or re.search(r"^\s*$", readedData) != None:
                #print currentObject.plainText
                sys.stderr.write("RTFParser: Konec\n")
                break
                #sys.exit(0)
            readedData = re.sub(r"^\s+", "", readedData, 1)
            if re.search(r"^\{\{\\shp", readedData) != None:
                tmpArray = self.Shape(self, readedData)
                readedData = tmpArray[0]
                #print readedData
                #sys.stderr.write("JO!!!\n")
                #sys.exit(1)
            elif re.search(r"^\{(\\\*)?\\\w+", readedData) != None:
                readedData = re.sub(r"^\{", "", readedData, 1)
                if re.search(r"^\\\w+", readedData) != None:
                    #<fonttbl>
                    if re.search(r"^\\fonttbl", readedData) != None:
                        sys.stderr.write("FontTable\n")
                        readedData = re.sub(r"\\fonttbl(\x0D\x0A)?", "", readedData, 1)
                        #xml += "<FontTable>"
                        #<fontinfo>
                        tmpArray = self.FontInfo(self, readedData)
                        readedData = tmpArray[0]
                        #xml += tmpArray[1]
                        #xml += "</FontTable>"
                    #<filetbl>
                    #zatim neimplementovano
                    #<colortbl>
                    elif re.search(r"\\colortbl", readedData) != None:
                        sys.stderr.write("ColorTable\n")
                        readedData = re.sub(r"\\colortbl(\x0D\x0A)?;(\x0D\x0A)?", "", readedData, 1)
                        #xml += "<ColorTable>"
                        #<colordef>
                        tmpArray = self.ColorTable(self, readedData)
                        readedData = tmpArray[0]
                        #xml += tmpArray[1]
                        #xml += "</ColorTable>"
                    #<stylesheet>
                    elif re.search(r"^\\stylesheet", readedData) != None:
                        sys.stderr.write("StyleSheet\n")
                        readedData = re.sub(r"\\stylesheet(\x0D\x0A)?", "", readedData, 1)
                        xml += "<StyleSheet>"
                        tmpArray = self.StyleSheet(self, readedData)
                        readedData = tmpArray[0]
                        xml += tmpArray[1]
                        xml += "</StyleSheet>\n"
                    #<info>
                    elif re.search(r"\\info", readedData) != None:
                        sys.stderr.write("Info\n")
                        readedData = re.sub(r"\\info(\x0D\x0A)?", "", readedData, 1)
                        #xml += "<Info>"
                        tmpArray = self.Info(self, readedData)
                        readedData = tmpArray[0]
                        #xml += tmpArray[1]
                        #xml += "</Info>\n"
                        #xml += "<body>\n"
                    elif re.search(r"^\\field", readedData) != None:
                        sys.stderr.write("Field\n")
                        #xml += "<Text>"
                        tmpArray = self.Field(self, readedData)
                        readedData = tmpArray[0]
                        xml += tmpArray[1]
                        #print readedData
                        #xml += "</Text>"
                    elif re.search(r"^\\trowd", readedData) != None:
                        sys.stderr.write("Table\n")
                        tmpArray = self.MakeTable(self, readedData)
                        readedData = tmpArray[0]
                        xml += tmpArray[1]
                        #sys.stderr.write("Tabulka\n")
                        #sys.exit(0)
                    #elif re.search(r"^\\shp", readedData) != None:
                    #    sys.stderr.write("SHP nalezen!\n")
                    #    sys.exit(1)
                    else:
                        sys.stderr.write("{keyword\n")
                        #self.SaveOnStack(self)
                        tmpArray = self.Keywords(self, readedData)
                        #print readedData
                        #sys.exit(0)
                        readedData = tmpArray[0]
                        xml += tmpArray[1]
                        #print readedData
                        #sys.exit(0)
                else:
                    #default properties
                    #\*\defchp
                    if re.search(r"^\\\*\\defchp", readedData) != None:
                        sys.stderr.write("defchp\n")
                        readedData = re.sub(r"\\\*\\defchp", "", readedData)
                        tmpStr = re.search(r"^[^\}]*\}", readedData).group(0)
                        readedData = re.sub(r"^[^\}]*\}(\x0D\x0A)?", "", readedData, 1)
                        self.SetDefPropChar(self, tmpStr)
                    #\*\defpap
                    if re.search(r"^\\\*\\defpap", readedData) != None:
                        sys.stderr.write("defpap\n")
                        readedData = re.sub(r"\\\*\\defpap", "", readedData)
                        tmpStr = re.search(r"^[^\}]*\}", readedData).group(0)
                        readedData = re.sub(r"^[^\}]*\}(\x0D\x0A)?", "", readedData, 1)
                        self.SetDefPropPap(self, tmpStr)
                    #\*listtable
                    if re.search(r"^\\\*\\listtable", readedData) != None:
                        sys.stderr.write("listTable\n")
                        readedData = re.sub(r"^\\\*\\listtable(\x0D\x0A)?", "", readedData, 1)
                        #xml += "<ListTable>"
                        tmpArray = self.ListTable(self, readedData)
                        readedData = tmpArray[0]
                        #xml += tmpArray[1]
                        #xml += "</ListTable>"
                    #\*\listoverridetable
                    if re.search(r"^\\\*\\listoverridetable", readedData) != None:
                        sys.stderr.write("listOverrideTable\n")
                        readedData = re.sub(r"\\\*\\listoverridetable(\x0D\x0A)?", "", readedData, 1)
                        #xml += "<ListOverrideTable>"
                        tmpArray = self.ListOverrideTable(self, readedData)
                        readedData = tmpArray[0]
                        #xml += tmpArray[1]
                        #xml += "</ListOverrideTable>"
                    #\*\ftnsep
                    if re.search(r"^\\\*\\ftnsep", readedData) != None:
                        sys.stderr.write("ftnsep\n")
                        readedData = re.sub(r"\\\*\\ftnsep(\x0D\x0A)?", "", readedData, 1)
                        #xml += "<FootnoteSep>"
                        tmpArray = self.FootnoteSep(self, readedData)
                        readedData = tmpArray[0]
                        #xml += tmpArray[1]
                        #xml += "</FootnoteSep>"
                    #\*\aftnsep
                    if re.search(r"^\\\*\\aftnsep", readedData) != None:
                        sys.stderr.write("aftnsep\n")
                        readedData = re.sub(r"\\\*\\aftnsep(\x0D\x0A)?", "", readedData, 1)
                        #xml += "<EndnoteSep>"
                        tmpArray = self.EndnoteSep(self, readedData)
                        readedData = tmpArray[0]
                        #xml += tmpArray[1]
                        #xml += "</EndnoteSep>"
                    #\*\bkmstart
                    if re.search(r"^\\\*\\bkmkstart", readedData) != None:
                        sys.stderr.write("Bookmark\n")
                        #print readedData
                        #sys.exit(0)
                        #xml += "<Bookmark>"
                        tmpArray = self.Bookmark(self, readedData)
                        readedData = tmpArray[0]
                        xml += tmpArray[1]
                        #xml += "</Bookmark>"
                        #print "ReadedData"
                        #print readedData
                        #sys.exit(0)
            elif re.search(r"^\\\w+", readedData) != None:
                sys.stderr.write("Keywords\n")
                #self.SaveOnStack(self)
                tmpArray = self.Keywords(self, readedData)
                readedData = tmpArray[0]
                xml += tmpArray[1]
            else:
                #re.search(r"\w+", readedData) != None:
                sys.stderr.write("Parse text\n")
                tmpArray = self.ParseText(self, readedData)
                #currentObject.LoadFromStack(currentObject)
                readedData = tmpArray[0]
                xml += tmpArray[1]
                #print "PARSETEXT!!!!!!!!!!!!!!!!1"
                #print xml
        if currentObject.xmlParaList:
            #print currentObject.xmlParaList
            #sys.exit(0)
            currentObject.MakeDocument(currentObject)
    
    def Shape(self, currentObject, readedData):
        retArray = []
        
        #<shape>
        readedData = re.sub(r"^\{\{\\shp", "", readedData, 1)
        #print readedData
        #sys.exit(0)
        
        #<shpinfo>
        while readedData[0] != '{':
            sys.stderr.write(readedData[:32])
            if re.search(r"^\\shpleft\d+", readedData) != None:
                readedData = re.sub(r"^\\shpleft\d+", "", readedData, 1)
            if re.search(r"^\\shptop(\-)?\d+", readedData) != None:
                readedData = re.sub(r"^\\shptop(\-)?\d+", "", readedData, 1)
            if re.search(r"^\\shpbottom(\-)?\d+", readedData) != None:
                readedData = re.sub(r"^\\shpbottom(\-)?\d+", "", readedData, 1)
            if re.search(r"^\\shpright(\-)?\d+", readedData) != None:
                readedData = re.sub(r"^\\shpright(\-)?\d+", "", readedData, 1)
            if re.search(r"^\\shplid(\-)?\d+", readedData) != None:
                readedData = re.sub(r"^\\shplid(\-)?\d+", "", readedData, 1)
            if re.search(r"^\\shpz(\-)?\d+", readedData) != None:
                readedData = re.sub(r"^\\shpz(\-)?\d+", "", readedData, 1)
            if re.search(r"^\\shpfhdr(\-)?\d+", readedData) != None:
                readedData = re.sub(r"^\\shpfhdr(\-)?\d+", "", readedData, 1)
            if re.search(r"^\\shpbxpage", readedData) != None:
                readedData = re.sub(r"^\\shpbxpage", "", readedData, 1)
            if re.search(r"^\\shpbxmargin", readedData) != None:
                readedData = re.sub(r"^\\shpbxmargin", "", readedData, 1)
            if re.search(r"^\\shpbxcolumn", readedData) != None:
                readedData = re.sub(r"^\\shpbxcolumn", "", readedData, 1)
            if re.search(r"^\\shpbxignore", readedData) != None:
                readedData = re.sub(r"^\\shpbxignore", "", readedData, 1)
            if re.search(r"^\\shpbypage", readedData) != None:
                readedData = re.sub(r"^\\shpbypage", "", readedData, 1)
            if re.search(r"^\\shpbymargin", readedData) != None:
                readedData = re.sub(r"^\\shpbymargin", "", readedData, 1)
            if re.search(r"^\\shpbypara", readedData) != None:
                readedData = re.sub(r"^\\shpbypara", "", readedData, 1)
            if re.search(r"^\\shpbyignore", readedData) != None:
                readedData = re.sub(r"^\\shpbyignore", "", readedData, 1)
            if re.search(r"^\\shpwr(\-)?\d+", readedData) != None:
                readedData = re.sub(r"^\\shpwr(\-)?\d+", "", readedData, 1)
            if re.search(r"^\\shpwrk(\-)?\d+", readedData) != None:
                readedData = re.sub(r"^\\shpwrk(\-)?\d+", "", readedData, 1)
            if re.search(r"^\\shpfblwtxt(\-)?\d+", readedData) != None:
                readedData = re.sub(r"^\\shpfblwtxt(\-)?\d+", "", readedData, 1)
            if re.search(r"^\\shplockanchor", readedData) != None:
                readedData = re.sub(r"^\\shplockanchor", "", readedData, 1)
            if re.search(r"^\\shptxt", readedData) != None:
                readedData = re.sub(r"^\\shptxt", "", readedData, 1)
        
        #<shpinst>
        readedData = re.sub(r"^\{\\\*\\shpinst", "", readedData, 1)
        
        #<shpinfo>
        while readedData[0] != '{':
            sys.stderr.write(readedData[:32] + "\n")
            if re.search(r"^\\shpleft\d+", readedData) != None:
                readedData = re.sub(r"^\\shpleft\d+", "", readedData, 1)
            if re.search(r"^\\shptop(\-)?\d+", readedData) != None:
                readedData = re.sub(r"^\\shptop(\-)?\d+", "", readedData, 1)
            if re.search(r"^\\shpbottom(\-)?\d+", readedData) != None:
                readedData = re.sub(r"^\\shpbottom(\-)?\d+", "", readedData, 1)
            if re.search(r"^\\shpright(\-)?\d+", readedData) != None:
                readedData = re.sub(r"^\\shpright(\-)?\d+", "", readedData, 1)
            if re.search(r"^\\shplid(\-)?\d+", readedData) != None:
                readedData = re.sub(r"^\\shplid(\-)?\d+", "", readedData, 1)
            if re.search(r"^\\shpz(\-)?\d+", readedData) != None:
                readedData = re.sub(r"^\\shpz(\-)?\d+", "", readedData, 1)
            if re.search(r"^\\shpfhdr(\-)?\d+", readedData) != None:
                readedData = re.sub(r"^\\shpfhdr(\-)?\d+", "", readedData, 1)
            if re.search(r"^\\shpbxpage", readedData) != None:
                readedData = re.sub(r"^\\shpbxpage", "", readedData, 1)
            if re.search(r"^\\shpbxmargin", readedData) != None:
                readedData = re.sub(r"^\\shpbxmargin", "", readedData, 1)
            if re.search(r"^\\shpbxcolumn", readedData) != None:
                readedData = re.sub(r"^\\shpbxcolumn", "", readedData, 1)
            if re.search(r"^\\shpbxignore", readedData) != None:
                readedData = re.sub(r"^\\shpbxignore", "", readedData, 1)
            if re.search(r"^\\shpbypage", readedData) != None:
                readedData = re.sub(r"^\\shpbypage", "", readedData, 1)
            if re.search(r"^\\shpbymargin", readedData) != None:
                readedData = re.sub(r"^\\shpbymargin", "", readedData, 1)
            if re.search(r"^\\shpbypara", readedData) != None:
                readedData = re.sub(r"^\\shpbypara", "", readedData, 1)
            if re.search(r"^\\shpbyignore", readedData) != None:
                readedData = re.sub(r"^\\shpbyignore", "", readedData, 1)
            if re.search(r"^\\shpwr(\-)?\d+", readedData) != None:
                readedData = re.sub(r"^\\shpwr(\-)?\d+", "", readedData, 1)
            if re.search(r"^\\shpwrk(\-)?\d+", readedData) != None:
                readedData = re.sub(r"^\\shpwrk(\-)?\d+", "", readedData, 1)
            if re.search(r"^\\shpfblwtxt(\-)?\d+", readedData) != None:
                readedData = re.sub(r"^\\shpfblwtxt(\-)?\d+", "", readedData, 1)
            if re.search(r"^\\shplockanchor", readedData) != None:
                readedData = re.sub(r"^\\shplockanchor", "", readedData, 1)
            if re.search(r"^\\shptxt", readedData) != None:
                readedData = re.sub(r"^\\shptxt", "", readedData, 1)
        
        #print readedData
        #sys.exit(0)
        #<sp>+
        while readedData[0] != '}':
            #<sp>
            readedData = re.sub(r"^\{\\sp", "", readedData, 1)
            
            #<sn>
            readedData = re.sub(r"^\{\\sn[^\}]*\}", "", readedData, 1)
            
            #<sv>
            readedData = re.sub(r"^\{\\sv[^\}]*\}", "", readedData, 1)
            
            #<hsv>?
            readedData = re.sub(r"^\{\\sn[^\}]*\}", "", readedData, 1)
            
            readedData = re.sub(r"^\}", "", readedData, 1)
        
        readedData = re.sub(r"^\}*", "", readedData, 1)
        
        #<shprslt>
        readedData = re.sub(r"^\{\\*\\shprslt[^\}]*\}", "", readedData, 1)
        
        readedData = re.sub(r"^\}*", "", readedData, 1)
        
        retArray.append(readedData)
        return retArray
        #sys.exit(0)
            
    
    #Metoda zabyvajici se zpracovanim tabulky v RTF dokumentu
    #@param1 objekt RTFUnit
    #@param2 zbyvajici text RTF souboru
    #@return vraci zbytek z RTF souboru
    def MakeTable(self, currentObject, readedData):
        retArray = []
        table = {}
        table["rows"] = []
        gridRows = []
        currentObject.tableSettings["rowsdef"] = []
        
        readedData = re.sub(r"\x0D\x0A", "", readedData)
        while True:
            #<tbldef>
            readedData = re.sub(r"^\\trowd", "", readedData, 1)
            
            #Zpracovani uvodnich informaci tabulky
            while re.search(r"^\\pard", readedData) == None:
                #print "readedData"
                sys.stderr.write(readedData[:32]+"\n")
                readedData = re.sub(r"^\\irow\d+", "", readedData, 1)
                readedData = re.sub(r"^\\irowband\d+", "", readedData, 1)
                readedData = re.sub(r"^\\ts\d+", "", readedData, 1)
                readedData = re.sub(r"^\\trgaph\d+", "", readedData, 1)
                
                #<rowjust>
                if re.search(r"^\\trql", readedData) != None:
                    currentObject.tableSettings["trql"] = 1
                    readedData = re.sub(r"^\\trql", "", readedData)
                elif re.search(r"^\\trqr", readedData) != None:
                    currentObject.tableSettings["trqr"] = 1
                    readedData = re.sub(r"^\\trqr", "", readedData)
                elif re.search(r"^\\trqc", readedData) != None:
                    currentObject.tableSettings["trqc"] = 1
                    readedData = re.sub(r"^\\trqc", "", readedData)
                """    
                #<rowwrite>
                if re.search(r"^\\ltrrow", readedData) != None:
                    currentObject.tableSettings["ltrrow"] = 1
                    readedData = re.sub(r"^\\ltrrow", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<rowwrite>::Neznam vyznam klioveho slova: \\ltrrow\n")
                elif re.search(r"^\\ltlrow", readedData) != None:
                    currentObject.tableSettings["ltlrow"] = 1
                    readedData = re.sub(r"^\\ltlrow", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<rowwrite>::Neznam vyznam klioveho slova: \\ltlrow\n")
                
                rowTBLRHV = False
                #<rowtop>
                if re.search(r"^\\trbrdrt", readedData) != None:
                    currentObject.tableSettings["trbrdrt"] = 1
                    readedData = re.sub(r"^\\trbrdrt", "", readedData)
                    rowTBLRHV = True
                #<rowbot>
                if re.search(r"^\\trbrdrb", readedData) != None:
                    currentObject.tableSettings["trbrdrb"] = 1
                    readedData = re.sub(r"^\\trbrdrb", "", readedData)
                    rowTBLRHV = True
                #<rowleft>
                if re.search(r"^\\trbrdrl", readedData) != None:
                    currentObject.tableSettings["trbrdrl"] = 1
                    readedData = re.sub(r"^\\trbrdrl", "", readedData)
                    rowTBLRHV = True
                #<rowright>
                if re.search(r"^\\trbrdrr", readedData) != None:
                    currentObject.tableSettings["trbrdrr"] = 1
                    readedData = re.sub(r"^\\trbrdrr", "", readedData)
                    rowTBLRHV = True
                #<rowhor>
                if re.search(r"^\\trbrdrr", readedData) != None:
                    currentObject.tableSettings["trbrdrr"] = 1
                    readedData = re.sub(r"^\\trbrdrr", "", readedData)
                    rowTBLRHV = True
                #<rowvert>
                if re.search(r"^\\trbrdrr", readedData) != None:
                    currentObject.tableSettings["trbrdrr"] = 1
                    readedData = re.sub(r"^\\trbrdrr", "", readedData)
                    rowTBLRHV = True
                    
                if rowTBLRHV:
                    #<brdr>
                    #<brdrk>
                    if re.search(r"^\\brdrs", readedData) != None:
                        currentObject.tableSettings["brdrs"] = 1
                        readedData = re.sub(r"^\\brdrs", "", readedData)
                    elif re.search(r"^\\brdrth", readedData) != None:
                        currentObject.tableSettings["brdrth"] = 1
                        readedData = re.sub(r"^\\brdrth", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrth\n")
                    elif re.search(r"^\\brdrsh", readedData) != None:
                        currentObject.tableSettings["brdrsh"] = 1
                        readedData = re.sub(r"^\\brdrsh", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrsh\n")
                    elif re.search(r"^\\brdrdb", readedData) != None:
                        currentObject.tableSettings["brdrdb"] = 1
                        readedData = re.sub(r"^\\brdrdb", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrdb\n")
                    elif re.search(r"^\\brdrdot", readedData) != None:
                        currentObject.tableSettings["brdrdot"] = 1
                        readedData = re.sub(r"^\\brdrdot", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrdot\n")
                    elif re.search(r"^\\brdrdash", readedData) != None:
                        currentObject.tableSettings["brdrdash"] = 1
                        readedData = re.sub(r"^\\brdrdash", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrdash\n")
                    elif re.search(r"^\\brdrhair", readedData) != None:
                        currentObject.tableSettings["brdrhair"] = 1
                        readedData = re.sub(r"^\\brdrhair", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrhair\n")
                    elif re.search(r"^\\brdrinset", readedData) != None:
                        currentObject.tableSettings["brdrinset"] = 1
                        readedData = re.sub(r"^\\brdrinset", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrinset\n")
                    elif re.search(r"^\\brdrdashsm", readedData) != None:
                        currentObject.tableSettings["brdrdashsm"] = 1
                        readedData = re.sub(r"^\\brdrdashsm", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrdashsm\n")
                    elif re.search(r"^\\brdrdashd", readedData) != None:
                        currentObject.tableSettings["brdrdashd"] = 1
                        readedData = re.sub(r"^\\brdrdashd", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrdashd\n")
                    elif re.search(r"^\\brdrdashdd", readedData) != None:
                        currentObject.tableSettings["brdrdashdd"] = 1
                        readedData = re.sub(r"^\\brdrdashdd", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrdashdd\n")
                    elif re.search(r"^\\brdrdashdot", readedData) != None:
                        currentObject.tableSettings["brdrdashdot"] = 1
                        readedData = re.sub(r"^\\brdrdashdot", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrdashdot\n")
                    elif re.search(r"^\\brdrdashdotdot", readedData) != None:
                        currentObject.tableSettings["brdrdashdotdot"] = 1
                        readedData = re.sub(r"^\\brdrdashdotdot", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrdashdotdot\n")
                    elif re.search(r"^\\brdrtriple", readedData) != None:
                        currentObject.tableSettings["brdrtriple"] = 1
                        readedData = re.sub(r"^\\brdrtriple", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrtriple\n")
                    elif re.search(r"^\\brdrtnthsg", readedData) != None:
                        currentObject.tableSettings["brdrtnthsg"] = 1
                        readedData = re.sub(r"^\\brdrtnthsg", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrtnthsg\n")
                    elif re.search(r"^\\brdrthtnsg", readedData) != None:
                        currentObject.tableSettings["brdrthtnsg"] = 1
                        readedData = re.sub(r"^\\brdrthtnsg", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrthtnsg\n")
                    elif re.search(r"^\\brdrtnthtnsg", readedData) != None:
                        currentObject.tableSettings["brdrtnthtnsg"] = 1
                        readedData = re.sub(r"^\\brdrtnthtnsg", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrtnthtnsg\n")
                    elif re.search(r"^\\brdrtnthmg", readedData) != None:
                        currentObject.tableSettings["brdrtnthmg"] = 1
                        readedData = re.sub(r"^\\brdrtnthmg", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrtnthmg\n")
                    elif re.search(r"^\\brdrthtnmg", readedData) != None:
                        currentObject.tableSettings["brdrthtnmg"] = 1
                        readedData = re.sub(r"^\\brdrthtnmg", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrthtnmg\n")
                    elif re.search(r"^\\brdrtnthtnmg", readedData) != None:
                        currentObject.tableSettings["brdrtnthtnmg"] = 1
                        readedData = re.sub(r"^\\brdrtnthtnmg", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrtnthtnmg\n")
                    elif re.search(r"^\\brdrtnthlg", readedData) != None:
                        currentObject.tableSettings["brdrtnthlg"] = 1
                        readedData = re.sub(r"^\\brdrtnthlg", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrtnthlg\n")
                    elif re.search(r"^\\brdrthtnlg", readedData) != None:
                        currentObject.tableSettings["brdrthtnlg"] = 1
                        readedData = re.sub(r"^\\brdrthtnlg", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrthtnlg\n")
                    elif re.search(r"^\\brdrtnthtnlg", readedData) != None:
                        currentObject.tableSettings["brdrtnthtnlg"] = 1
                        readedData = re.sub(r"^\\brdrtnthtnlg", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrtnthtnlg\n")
                    elif re.search(r"^\\brdrwavy", readedData) != None:
                        currentObject.tableSettings["brdrwavy"] = 1
                        readedData = re.sub(r"^\\brdrwavy", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrwavy\n")
                    elif re.search(r"^\\brdrwavydb", readedData) != None:
                        currentObject.tableSettings["brdrwavydb"] = 1
                        readedData = re.sub(r"^\\brdrwavydb", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrwavydb\n")
                    elif re.search(r"^\\brdrdashdotstr", readedData) != None:
                        currentObject.tableSettings["brdrdashdotstr"] = 1
                        readedData = re.sub(r"^\\brdrdashdotstr", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrdashdotstr\n")
                    elif re.search(r"^\\brdremboss", readedData) != None:
                        currentObject.tableSettings["brdremboss"] = 1
                        readedData = re.sub(r"^\\brdremboss", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdremboss\n")
                    elif re.search(r"^\\brdrengrave", readedData) != None:
                        currentObject.tableSettings["brdrengrave"] = 1
                        readedData = re.sub(r"^\\brdrengrave", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrengrave\n")
                    elif re.search(r"^\\brdroutset", readedData) != None:
                        currentObject.tableSettings["brdroutset"] = 1
                        readedData = re.sub(r"^\\brdroutset", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdroutset\n")
                    elif re.search(r"^\\brdrnone", readedData) != None:
                        currentObject.tableSettings["brdrnone"] = 1
                        readedData = re.sub(r"^\\brdrnone", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrnone\n")
                    elif re.search(r"^\\brdrtbl", readedData) != None:
                        currentObject.tableSettings["brdrtbl"] = 1
                        readedData = re.sub(r"^\\brdrtbl", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrtbl\n")
                    elif re.search(r"^\\brdrnil", readedData) != None:
                        currentObject.tableSettings["brdrnil"] = 1
                        readedData = re.sub(r"^\\brdrnil", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrnil\n")
                    
                    #<brdr>
                    if re.search(r"^\\brdrw\d+", readedData) != None:
                        currentObject.tableSettings["brdrw"] = re.search(r"^\\brdrw(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\brdrw\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\brdrw\n")
                    if re.search(r"^\\brsp\d+", readedData) != None:
                        currentObject.tableSettings["brsp"] = re.search(r"^\\brsp(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\brsp\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\brsp\n")
                    if re.search(r"^\\brdrcf\d+", readedData) != None:
                        currentObject.tableSettings["brdrcf"] = re.search(r"^\\brdrcf(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\brdrcf\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\brdrcf\n")
                
                #<rowpos>
                #<rowhorzpos>
                #<rowhframe>
                if re.search(r"^\\phmrg", readedData) != None:
                    currentObject.tableSettings["phmrg"] = 1
                    readedData = re.sub(r"^\\phmrg", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\phmrg\n")
                elif re.search(r"^\\phpg", readedData) != None:
                    currentObject.tableSettings["phpg"] = 1
                    readedData = re.sub(r"^\\phpg", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\phpg\n")
                elif re.search(r"^\\phcol", readedData) != None:
                    currentObject.tableSettings["phcol"] = 1
                    readedData = re.sub(r"^\\phcol", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\phcol\n")
                #<rowhdist>
                if re.search(r"^\\tposx\d+", readedData) != None:
                    currentObject.tableSettings["tposx"] = re.search(r"^\\tposx(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\tposx\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tposx\n")
                elif re.search(r"^\\tposnegx\d+", readedData) != None:
                    currentObject.tableSettings["tposnegx"] = re.search(r"^\\tposnegx(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\tposnegx\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tposnegx\n")
                elif re.search(r"^\\tposxc", readedData) != None:
                    currentObject.tableSettings["tposxc"] = 1
                    readedData = re.sub(r"^\\tposxc", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tposxc\n")
                elif re.search(r"^\\tposxi", readedData) != None:
                    currentObject.tableSettings["tposxi"] = 1
                    readedData = re.sub(r"^\\tposxi", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tposxi\n")
                elif re.search(r"^\\tposxo", readedData) != None:
                    currentObject.tableSettings["tposxo"] = 1
                    readedData = re.sub(r"^\\tposxo", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tposxo\n")
                elif re.search(r"^\\tposxl", readedData) != None:
                    currentObject.tableSettings["tposxl"] = 1
                    readedData = re.sub(r"^\\tposxl", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tposxl\n")
                elif re.search(r"^\\tposxr", readedData) != None:
                    currentObject.tableSettings["tposxr"] = 1
                    readedData = re.sub(r"^\\tposxr", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tposxr\n")
                
                #<rowvertpost>
                #<rowvframe>
                if re.search(r"^\\tpvmrg", readedData) != None:
                    currentObject.tableSettings["tpvmrg"] = 1
                    readedData = re.sub(r"^\\tpvmrg", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tpvmrg\n")
                elif re.search(r"^\\tpvpg", readedData) != None:
                    currentObject.tableSettings["tpvpg"] = 1
                    readedData = re.sub(r"^\\tpvpg", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tpvpg\n")
                elif re.search(r"^\\tpvpara", readedData) != None:
                    currentObject.tableSettings["tpvpara"] = 1
                    readedData = re.sub(r"^\\tpvpara", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tpvpara\n")
                #<rowvdist>
                if re.search(r"^\\tposy\d+", readedData) != None:
                    currentObject.tableSettings["tposy"] = re.search(r"^\\tposy(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\tposy\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tposy\n")
                elif re.search(r"^\\tposnegy\d+", readedData) != None:
                    currentObject.tableSettings["tposnegy"] = re.search(r"^\\tposnegy(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\tposnegy\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tposnegy\n")
                elif re.search(r"^\\tposyt", readedData) != None:
                    currentObject.tableSettings["tposyt"] = 1
                    readedData = re.sub(r"^\\tposyt", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tposyt\n")
                elif re.search(r"^\\tposyil", readedData) != None:
                    currentObject.tableSettings["tposyil"] = 1
                    readedData = re.sub(r"^\\tposyil", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tposyil\n")
                elif re.search(r"^\\tposyb", readedData) != None:
                    currentObject.tableSettings["tposyb"] = 1
                    readedData = re.sub(r"^\\tposyb", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tposyb\n")
                elif re.search(r"^\\tposyc", readedData) != None:
                    currentObject.tableSettings["tposyc"] = 1
                    readedData = re.sub(r"^\\tposyc", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tposyc\n")
                elif re.search(r"^\\tposyin", readedData) != None:
                    currentObject.tableSettings["tposyin"] = 1
                    readedData = re.sub(r"^\\tposyin", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tposyin\n")
                elif re.search(r"^\\tposyout", readedData) != None:
                    currentObject.tableSettings["tposyout"] = 1
                    readedData = re.sub(r"^\\tposyout", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tposyout\n")
                
                #<rowwrap>
                if re.search(r"^\\tdfrmtxtLeft\d+", readedData) != None:
                    currentObject.tableSettings["tdfrmtxtLeft"] = re.search(r"^\\tdfrmtxtLeft(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\tdfrmtxtLeft\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tdfrmtxtLeft\n")
                if re.search(r"^\\tdfrmtxtRight\d+", readedData) != None:
                    currentObject.tableSettings["tdfrmtxtRight"] = re.search(r"^\\tdfrmtxtRight(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\tdfrmtxtRight\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tdfrmtxtRight\n")
                if re.search(r"^\\tdfrmtxtTop\d+", readedData) != None:
                    currentObject.tableSettings["tdfrmtxtTop"] = re.search(r"^\\tdfrmtxtTop(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\tdfrmtxtTop\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tdfrmtxtTop\n")
                if re.search(r"^\\tdfrmtxtBottom\d+", readedData) != None:
                    currentObject.tableSettings["tdfrmtxtBottom"] = re.search(r"^\\tdfrmtxtBottom(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\tdfrmtxtBottom\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tdfrmtxtBottom\n")
                
                if re.search(r"^\\tabsnoovrlp", readedData) != None:
                    currentObject.tableSettings["tabsnoovrlp"] = re.search(r"^\\tabsnoovrlp", readedData).group(1)
                    readedData = re.sub(r"^\\tabsnoovrlp", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tabsnoovrlp\n")
                
                #\trleft
                if re.search(r"^\\trleft", readedData) != None:
                    currentObject.tableSettings["trleft"] = 1
                    readedData = re.sub(r"^\\trleft", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trleft\n")
                """
                if re.search(r"^\\trrh(\-)?\d+", readedData) != None:
                    currentObject.tableSettings["trrh"] = re.search(r"^\\trrh((\-)?\d+)", readedData).group(1)
                    gridRows.append(abs(int(currentObject.tableSettings["trrh"])))
                    readedData = re.sub(r"^\\trrh(\-)?\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trrh\n")
                """
                if re.search(r"^\\trhdr", readedData) != None:
                    currentObject.tableSettings["trhdr"] = 1
                    readedData = re.sub(r"^\\trhdr", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trhdr\n")
                
                if re.search(r"^\\trkeep", readedData) != None:
                    currentObject.tableSettings["trkeep"] = 1
                    readedData = re.sub(r"^\\trkeep", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trkeep\n")
                
                #<rowwidth>
                if re.search(r"^\\trftsWidth\d+", readedData) != None:
                    currentObject.tableSettings["trftsWidth"] = re.search(r"^\\trftsWidth(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trftsWidth\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trkeep\n")
                if re.search(r"^\\trwWidth\d+", readedData) != None:
                    currentObject.tableSettings["trwWidth"] = re.search(r"^\\trwWidth(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trwWidth\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trwWidth\n")
                
                #<rowinv>
                if re.search(r"^\\trftsWidthB\d+", readedData) != None:
                    currentObject.tableSettings["trftsWidthB"] = re.search(r"^\\trftsWidthB(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trftsWidthB\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trftsWidthB\n")
                if re.search(r"^\\trwWidthB\d+", readedData) != None:
                    currentObject.tableSettings["trwWidthB"] = re.search(r"^\\trwWidthB(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trwWidthB\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trwWidthB\n")
                if re.search(r"^\\trftsWidthA\d+", readedData) != None:
                    currentObject.tableSettings["trftsWidthA"] = re.search(r"^\\trftsWidthA(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trftsWidthA\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trftsWidthA\n")
                if re.search(r"^\\trwWidthA\d+", readedData) != None:
                    currentObject.tableSettings["trwWidthA"] = re.search(r"^\\trwWidthA(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trwWidthA\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trwWidthA\n")
                
                if re.search(r"^\\trautofit", readedData) != None:
                    currentObject.tableSettings["trautofit"] = 1
                    readedData = re.sub(r"^\\trautofit", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trautofit\n")
                
                #<rowspc>
                if re.search(r"^\\trspdl\d+", readedData) != None:
                    currentObject.tableSettings["trspdl"] = re.search(r"^\\trspdl(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trspdl\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trspdl\n")
                if re.search(r"^\\trspdfl\d+", readedData) != None:
                    currentObject.tableSettings["trspdfl"] = re.search(r"^\\trspdfl(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trspdfl\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trspdfl\n")
                if re.search(r"^\\trspdt\d+", readedData) != None:
                    currentObject.tableSettings["trspdt"] = re.search(r"^\\trspdt(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trspdt\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trspdt\n")
                if re.search(r"^\\trspdft\d+", readedData) != None:
                    currentObject.tableSettings["trspdft"] = re.search(r"^\\trspdft(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trspdft\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trspdft\n")
                if re.search(r"^\\trspdb\d+", readedData) != None:
                    currentObject.tableSettings["trspdb"] = re.search(r"^\\trspdb(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trspdb\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trspdb\n")
                if re.search(r"^\\trspdfb\d+", readedData) != None:
                    currentObject.tableSettings["trspdfb"] = re.search(r"^\\trspdfb(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trspdfb\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trspdfb\n")
                if re.search(r"^\\trspdr\d+", readedData) != None:
                    currentObject.tableSettings["trspdr"] = re.search(r"^\\trspdr(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trspdr\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trspdr\n")
                if re.search(r"^\\trspdfr\d+", readedData) != None:
                    currentObject.tableSettings["trspdfr"] = re.search(r"^\\trspdfr(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trspdfr\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trspdfr\n")
                
                #<rowpad>
                if re.search(r"^\\trpaddl\d+", readedData) != None:
                    currentObject.tableSettings["trpaddl"] = re.search(r"^\\trpaddl(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trpaddl\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trpaddl\n")
                if re.search(r"^\\trpaddfl\d+", readedData) != None:
                    currentObject.tableSettings["trpaddfl"] = re.search(r"^\\trpaddfl(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trpaddfl\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trpaddfl\n")
                if re.search(r"^\\trpaddt\d+", readedData) != None:
                    currentObject.tableSettings["trpaddt"] = re.search(r"^\\trpaddt(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trpaddt\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trpaddt\n")
                if re.search(r"^\\trpaddft\d+", readedData) != None:
                    currentObject.tableSettings["trpaddft"] = re.search(r"^\\trpaddft(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trpaddft\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trpaddft\n")
                if re.search(r"^\\trpaddb\d+", readedData) != None:
                    currentObject.tableSettings["trpaddb"] = re.search(r"^\\trpaddb(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trpaddb\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trpaddb\n")
                if re.search(r"^\\trpaddfb\d+", readedData) != None:
                    currentObject.tableSettings["trpaddfb"] = re.search(r"^\\trpaddfb(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trpaddfb\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trpaddfb\n")
                if re.search(r"^\\trpaddr\d+", readedData) != None:
                    currentObject.tableSettings["trpaddr"] = re.search(r"^\\trpaddr(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trpaddr\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trpaddr\n")
                if re.search(r"^\\trpaddfr\d+", readedData) != None:
                    currentObject.tableSettings["trpaddfr"] = re.search(r"^\\trpaddfr(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trpaddfr\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trpaddfr\n")
                
                #<rowspcout>
                if re.search(r"^\\trspol\d+", readedData) != None:
                    currentObject.tableSettings["trspol"] = re.search(r"^\\trspol(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trspol\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trspol\n")
                if re.search(r"^\\trspofl\d+", readedData) != None:
                    currentObject.tableSettings["trspofl"] = re.search(r"^\\trspofl(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trspofl\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trspofl\n")
                if re.search(r"^\\trspot\d+", readedData) != None:
                    currentObject.tableSettings["trspot"] = re.search(r"^\\trspot(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trspot\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trspot\n")
                if re.search(r"^\\trspoft\d+", readedData) != None:
                    currentObject.tableSettings["trspoft"] = re.search(r"^\\trspoft(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trspoft\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trspoft\n")
                if re.search(r"^\\trspob\d+", readedData) != None:
                    currentObject.tableSettings["trspob"] = re.search(r"^\\trspob(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trspob\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trspob\n")
                if re.search(r"^\\trspofb\d+", readedData) != None:
                    currentObject.tableSettings["trspofb"] = re.search(r"^\\trspofb(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trspofb\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trspofb\n")
                if re.search(r"^\\trspor\d+", readedData) != None:
                    currentObject.tableSettings["trspor"] = re.search(r"^\\trspor(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trspor\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trspor\n")
                if re.search(r"^\\trspofr\d+", readedData) != None:
                    currentObject.tableSettings["trspofr"] = re.search(r"^\\trspofr(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trspofr\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trspofr\n")
                
                #<rowpadout>
                if re.search(r"^\\trpadol\d+", readedData) != None:
                    currentObject.tableSettings["trpadol"] = re.search(r"^\\trpadol(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trpadol\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trpadol\n")
                if re.search(r"^\\trpadofl\d+", readedData) != None:
                    currentObject.tableSettings["trpadofl"] = re.search(r"^\\trpadofl(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trpadofl\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trpadofl\n")
                if re.search(r"^\\trpadot\d+", readedData) != None:
                    currentObject.tableSettings["trpadot"] = re.search(r"^\\trpadot(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trpadot\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trpadot\n")
                if re.search(r"^\\trpadoft\d+", readedData) != None:
                    currentObject.tableSettings["trpadoft"] = re.search(r"^\\trpadoft(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trpadoft\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trpadoft\n")
                if re.search(r"^\\trpadob\d+", readedData) != None:
                    currentObject.tableSettings["trpadob"] = re.search(r"^\\trpadob(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trpadob\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trpadob\n")
                if re.search(r"^\\trpadofb\d+", readedData) != None:
                    currentObject.tableSettings["trpadofb"] = re.search(r"^\\trpadofb(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trpadofb\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trpadofb\n")
                if re.search(r"^\\trpador\d+", readedData) != None:
                    currentObject.tableSettings["trpador"] = re.search(r"^\\trpador(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trpador\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trpador\n")
                if re.search(r"^\\trpadofr\d+", readedData) != None:
                    currentObject.tableSettings["trpadofr"] = re.search(r"^\\trpadofr(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trpadofr\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trpadofr\n")
                
                if re.search(r"^\\taprtl", readedData) != None:
                    currentObject.tableSettings["taprtl"] = 1
                    readedData = re.sub(r"^\\taprtl", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\taprtl\n")
                
                #<trrevision>
                if re.search(r"^\\trauth\d+", readedData) != None:
                    currentObject.tableSettings["trauth"] = re.search(r"^\\trauth(\d+)", readedData).group(1)
                    readedData = re.sub(r"^\\trauth\d+", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trauth\n")
                    
                    if re.search(r"^\\trdate\d+", readedData) != None:
                        currentObject.tableSettings["trdate"] = re.search(r"^\\trdate(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\trdate\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\trdate\n")
                
                #<tflags>
                if re.search(r"^\\tbllkborder", readedData) != None:
                    currentObject.tableSettings["tbllkborder"] = 1
                    readedData = re.sub(r"^\\tbllkborder", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tbllkborder\n")
                if re.search(r"^\\tbllkshading", readedData) != None:
                    currentObject.tableSettings["tbllkshading"] = 1
                    readedData = re.sub(r"^\\tbllkshading", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tbllkshading\n")
                if re.search(r"^\\tbllkfont", readedData) != None:
                    currentObject.tableSettings["tbllkfont"] = 1
                    readedData = re.sub(r"^\\tbllkfont", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tbllkfont\n")
                if re.search(r"^\\tbllkcolor", readedData) != None:
                    currentObject.tableSettings["tbllkcolor"] = 1
                    readedData = re.sub(r"^\\tbllkcolor", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tbllkcolor\n")
                if re.search(r"^\\tbllkbestfit", readedData) != None:
                    currentObject.tableSettings["tbllkbestfit"] = 1
                    readedData = re.sub(r"^\\tbllkbestfit", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tbllkbestfit\n")
                if re.search(r"^\\tbllkhdrrows", readedData) != None:
                    currentObject.tableSettings["tbllkhdrrows"] = 1
                    readedData = re.sub(r"^\\tbllkhdrrows", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tbllkhdrrows\n")
                if re.search(r"^\\tbllklastrow", readedData) != None:
                    currentObject.tableSettings["tbllklastrow"] = 1
                    readedData = re.sub(r"^\\tbllklastrow", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tbllklastrow\n")
                if re.search(r"^\\tbllkhdrcols", readedData) != None:
                    currentObject.tableSettings["tbllkhdrcols"] = 1
                    readedData = re.sub(r"^\\tbllkhdrcols", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tbllkhdrcols\n")
                if re.search(r"^\\tbllklastcol", readedData) != None:
                    currentObject.tableSettings["tbllklastcol"] = 1
                    readedData = re.sub(r"^\\tbllklastcol", "", readedData)
                   # sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tbllklastcol\n")
                if re.search(r"^\\tbllknorowband", readedData) != None:
                    currentObject.tableSettings["tbllknorowband"] = 1
                    readedData = re.sub(r"^\\tbllknorowband", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tbllknorowband\n")
                if re.search(r"^\\tbllknocolband", readedData) != None:
                    currentObject.tableSettings["tbllknocolband"] = 1
                    readedData = re.sub(r"^\\tbllknocolband", "", readedData)
                    #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\tbllknocolband\n")
                """
                #<celldef>+
                celldef = []
                celldefItem = {}
                cellKey = False
                
                while re.search(r"^\\pard", readedData) == None:
                    #print "readedData"
                    #print readedData
                    sys.stderr.write(readedData[:32]+"\n")
                    
                    if re.search(r"^\\clmgf", readedData) != None:
                        celldefItem["clmgf"] = 1
                        readedData = re.sub(r"^\\clmgf", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<celldef>::Neznam vyznam klioveho slova: \\clmgf\n")
                    if re.search(r"^\\clmrg", readedData) != None:
                        celldefItem["clmrg"] = 1
                        readedData = re.sub(r"^\\clmrg", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<celldef>::Neznam vyznam klioveho slova: \\clmrg\n")
                    if re.search(r"^\\clvmgf", readedData) != None:
                        celldefItem["clvmgf"] = 1
                        readedData = re.sub(r"^\\clvmgf", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<celldef>::Neznam vyznam klioveho slova: \\clvmgf\n")
                    if re.search(r"^\\clvmrg", readedData) != None:
                        celldefItem["clvmrg"] = 1
                        readedData = re.sub(r"^\\clvmrg", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<celldef>::Neznam vyznam klioveho slova: \\clvmrg\n")
                    
                    #brdrFlag = False
                    brdrFlag = True
                    #<celldgu>
                    if re.search(r"^\\cldglu", readedData) != None:
                        brdrFlag = True
                        cellKey = True
                        celldefItem["cldglu"] = 1
                        readedData = re.sub(r"^\\cldglu", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<celldgu>::Neznam vyznam klioveho slova: \\cldglu\n")
                    #<celldgl>
                    if re.search(r"^\\cldgll", readedData) != None:
                        brdrFlag = True
                        cellKey = True
                        celldefItem["cldgll"] = 1
                        readedData = re.sub(r"^\\cldgll", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<celldgl>::Neznam vyznam klioveho slova: \\cldgll\n")
                    #<celltop>
                    if re.search(r"^\\clbrdrt", readedData) != None:
                        brdrFlag = True
                        cellKey = True
                        celldefItem["clbrdrt"] = 1
                        readedData = re.sub(r"^\\clbrdrt", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<celltop>::Neznam vyznam klioveho slova: \\clbrdrt\n")
                    #<cellleft>
                    if re.search(r"^\\clbrdrl", readedData) != None:
                        brdrFlag = True
                        cellKey = True
                        celldefItem["clbrdrl"] = 1
                        readedData = re.sub(r"^\\clbrdrl", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellleft>::Neznam vyznam klioveho slova: \\clbrdrl\n")
                    #<cellbot>
                    if re.search(r"^\\clbrdrb", readedData) != None:
                        brdrFlag = True
                        cellKey = True
                        celldefItem["clbrdrb"] = 1
                        readedData = re.sub(r"^\\clbrdrb", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellbot>::Neznam vyznam klioveho slova: \\clbrdrb\n")
                    #<cellright>
                    if re.search(r"^\\clbrdrr", readedData) != None:
                        brdrFlag = True
                        cellKey = True
                        celldefItem["clbrdrr"] = 1
                        readedData = re.sub(r"^\\clbrdrr", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellright>::Neznam vyznam klioveho slova: \\clbrdrr\n")
                    #<brdr>
                    if brdrFlag:
                        #<brdr>
                        #<brdrk>
                        if re.search(r"^\\brdrs", readedData) != None:
                            celldefItem["brdrs"] = 1
                            readedData = re.sub(r"^\\brdrs", "", readedData)
                        elif re.search(r"^\\brdrth", readedData) != None:
                            celldefItem["brdrth"] = 1
                            readedData = re.sub(r"^\\brdrth", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrth\n")
                        elif re.search(r"^\\brdrsh", readedData) != None:
                            celldefItem["brdrsh"] = 1
                            readedData = re.sub(r"^\\brdrsh", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrsh\n")
                        elif re.search(r"^\\brdrdb", readedData) != None:
                            celldefItem["brdrdb"] = 1
                            readedData = re.sub(r"^\\brdrdb", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrdb\n")
                        elif re.search(r"^\\brdrdot", readedData) != None:
                            celldefItem["brdrdot"] = 1
                            readedData = re.sub(r"^\\brdrdot", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrdot\n")
                        elif re.search(r"^\\brdrdash", readedData) != None:
                            celldefItem["brdrdash"] = 1
                            readedData = re.sub(r"^\\brdrdash", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrdash\n")
                        elif re.search(r"^\\brdrhair", readedData) != None:
                            celldefItem["brdrhair"] = 1
                            readedData = re.sub(r"^\\brdrhair", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrhair\n")
                        elif re.search(r"^\\brdrinset", readedData) != None:
                            celldefItem["brdrinset"] = 1
                            readedData = re.sub(r"^\\brdrinset", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrinset\n")
                        elif re.search(r"^\\brdrdashsm", readedData) != None:
                            celldefItem["brdrdashsm"] = 1
                            readedData = re.sub(r"^\\brdrdashsm", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrdashsm\n")
                        elif re.search(r"^\\brdrdashd", readedData) != None:
                            celldefItem["brdrdashd"] = 1
                            readedData = re.sub(r"^\\brdrdashd", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrdashd\n")
                        elif re.search(r"^\\brdrdashdd", readedData) != None:
                            celldefItem["brdrdashdd"] = 1
                            readedData = re.sub(r"^\\brdrdashdd", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrdashdd\n")
                        elif re.search(r"^\\brdrdashdot", readedData) != None:
                            celldefItem["brdrdashdot"] = 1
                            readedData = re.sub(r"^\\brdrdashdot", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrdashdot\n")
                        elif re.search(r"^\\brdrdashdotdot", readedData) != None:
                            celldefItem["brdrdashdotdot"] = 1
                            readedData = re.sub(r"^\\brdrdashdotdot", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrdashdotdot\n")
                        elif re.search(r"^\\brdrtriple", readedData) != None:
                            celldefItem["brdrtriple"] = 1
                            readedData = re.sub(r"^\\brdrtriple", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrtriple\n")
                        elif re.search(r"^\\brdrtnthsg", readedData) != None:
                            celldefItem["brdrtnthsg"] = 1
                            readedData = re.sub(r"^\\brdrtnthsg", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrtnthsg\n")
                        elif re.search(r"^\\brdrthtnsg", readedData) != None:
                            celldefItem["brdrthtnsg"] = 1
                            readedData = re.sub(r"^\\brdrthtnsg", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrthtnsg\n")
                        elif re.search(r"^\\brdrtnthtnsg", readedData) != None:
                            celldefItem["brdrtnthtnsg"] = 1
                            readedData = re.sub(r"^\\brdrtnthtnsg", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrtnthtnsg\n")
                        elif re.search(r"^\\brdrtnthmg", readedData) != None:
                            celldefItem["brdrtnthmg"] = 1
                            readedData = re.sub(r"^\\brdrtnthmg", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrtnthmg\n")
                        elif re.search(r"^\\brdrthtnmg", readedData) != None:
                            celldefItem["brdrthtnmg"] = 1
                            readedData = re.sub(r"^\\brdrthtnmg", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrthtnmg\n")
                        elif re.search(r"^\\brdrtnthtnmg", readedData) != None:
                            celldefItem["brdrtnthtnmg"] = 1
                            readedData = re.sub(r"^\\brdrtnthtnmg", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrtnthtnmg\n")
                        elif re.search(r"^\\brdrtnthlg", readedData) != None:
                            celldefItem["brdrtnthlg"] = 1
                            readedData = re.sub(r"^\\brdrtnthlg", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrtnthlg\n")
                        elif re.search(r"^\\brdrthtnlg", readedData) != None:
                            celldefItem["brdrthtnlg"] = 1
                            readedData = re.sub(r"^\\brdrthtnlg", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrthtnlg\n")
                        elif re.search(r"^\\brdrtnthtnlg", readedData) != None:
                            celldefItem["brdrtnthtnlg"] = 1
                            readedData = re.sub(r"^\\brdrtnthtnlg", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrtnthtnlg\n")
                        elif re.search(r"^\\brdrwavy", readedData) != None:
                            celldefItem["brdrwavy"] = 1
                            readedData = re.sub(r"^\\brdrwavy", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrwavy\n")
                        elif re.search(r"^\\brdrwavydb", readedData) != None:
                            celldefItem["brdrwavydb"] = 1
                            readedData = re.sub(r"^\\brdrwavydb", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrwavydb\n")
                        elif re.search(r"^\\brdrdashdotstr", readedData) != None:
                            celldefItem["brdrdashdotstr"] = 1
                            readedData = re.sub(r"^\\brdrdashdotstr", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrdashdotstr\n")
                        elif re.search(r"^\\brdremboss", readedData) != None:
                            celldefItem["brdremboss"] = 1
                            readedData = re.sub(r"^\\brdremboss", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdremboss\n")
                        elif re.search(r"^\\brdrengrave", readedData) != None:
                            celldefItem["brdrengrave"] = 1
                            readedData = re.sub(r"^\\brdrengrave", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrengrave\n")
                        elif re.search(r"^\\brdroutset", readedData) != None:
                            celldefItem["brdroutset"] = 1
                            readedData = re.sub(r"^\\brdroutset", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdroutset\n")
                        elif re.search(r"^\\brdrnone", readedData) != None:
                            celldefItem["brdrnone"] = 1
                            readedData = re.sub(r"^\\brdrnone", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrnone\n")
                        elif re.search(r"^\\brdrtbl", readedData) != None:
                            celldefItem["brdrtbl"] = 1
                            readedData = re.sub(r"^\\brdrtbl", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrtbl\n")
                        elif re.search(r"^\\brdrnil", readedData) != None:
                            celldefItem["brdrnil"] = 1
                            readedData = re.sub(r"^\\brdrnil", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdrk>::Neznam vyznam klioveho slova: \\brdrnil\n")
                        
                        #<brdr>
                        if re.search(r"^\\brdrw\d+", readedData) != None:
                            celldefItem["brdrw"] = re.search(r"^\\brdrw(\d+)", readedData).group(1)
                            readedData = re.sub(r"^\\brdrw\d+", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\brdrw\n")
                        if re.search(r"^\\brsp\d+", readedData) != None:
                            celldefItem["brsp"] = re.search(r"^\\brsp(\d+)", readedData).group(1)
                            readedData = re.sub(r"^\\brsp\d+", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\brsp\n")
                        if re.search(r"^\\brdrcf\d+", readedData) != None:
                            celldefItem["brdrcf"] = re.search(r"^\\brdrcf(\d+)", readedData).group(1)
                            readedData = re.sub(r"^\\brdrcf\d+", "", readedData)
                            #sys.stderr.write("RTFParser::MakeTable()::<brdr>::Neznam vyznam klioveho slova: \\brdrcf\n")
                    
                    #<cellalign>
                    if re.search(r"^\\clvertalt", readedData) != None:
                        cellKey = True
                        celldefItem["clvertalt"] = 1
                        readedData = re.sub(r"^\\clvertalt", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellalign>::Neznam vyznam klioveho slova: \\clvertalt\n")
                    elif re.search(r"^\\clvertalc", readedData) != None:
                        cellKey = True
                        celldefItem["clvertalc"] = 1
                        readedData = re.sub(r"^\\clvertalc", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellalign>::Neznam vyznam klioveho slova: \\clvertalc\n")
                    elif re.search(r"^\\clvertalb", readedData) != None:
                        cellKey = True
                        celldefItem["clvertalb"] = 1
                        readedData = re.sub(r"^\\clvertalb", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellalign>::Neznam vyznam klioveho slova: \\clvertalb\n")
                    
                    #<cellshad>
                    """
                    #<cellpat>
                    if re.search(r"^\\clbghoriz", readedData) != None:
                        celldefItem["clbghoriz"] = 1
                        readedData = re.sub(r"^\\clbghoriz", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpat>::Neznam vyznam klioveho slova: \\clbghoriz\n")
                    elif re.search(r"^\\clbgvert", readedData) != None:
                        celldefItem["clbgvert"] = 1
                        readedData = re.sub(r"^\\clbgvert", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpat>::Neznam vyznam klioveho slova: \\clbgvert\n")
                    elif re.search(r"^\\clbgfdiag", readedData) != None:
                        celldefItem["clbgfdiag"] = 1
                        readedData = re.sub(r"^\\clbgfdiag", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpat>::Neznam vyznam klioveho slova: \\clbgfdiag\n")
                    elif re.search(r"^\\clbgbdiag", readedData) != None:
                        celldefItem["clbgbdiag"] = 1
                        readedData = re.sub(r"^\\clbgbdiag", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpat>::Neznam vyznam klioveho slova: \\clbgbdiag\n")
                    elif re.search(r"^\\clbgcross", readedData) != None:
                        celldefItem["clbgcross"] = 1
                        readedData = re.sub(r"^\\clbgcross", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpat>::Neznam vyznam klioveho slova: \\clbgcross\n")
                    elif re.search(r"^\\clbgdcross", readedData) != None:
                        celldefItem["clbgdcross"] = 1
                        readedData = re.sub(r"^\\clbgdcross", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpat>::Neznam vyznam klioveho slova: \\clbgdcross\n")
                    elif re.search(r"^\\clbgdkhor", readedData) != None:
                        celldefItem["clbgdkhor"] = 1
                        readedData = re.sub(r"^\\clbgdkhor", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpat>::Neznam vyznam klioveho slova: \\clbgdkhor\n")
                    elif re.search(r"^\\clbgdkvert", readedData) != None:
                        celldefItem["clbgdkvert"] = 1
                        readedData = re.sub(r"^\\clbgdkvert", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpat>::Neznam vyznam klioveho slova: \\clbgdkvert\n")
                    elif re.search(r"^\\clbgdkfdiag", readedData) != None:
                        celldefItem["clbgdkfdiag"] = 1
                        readedData = re.sub(r"^\\clbgdkfdiag", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpat>::Neznam vyznam klioveho slova: \\clbgdkfdiag\n")
                    elif re.search(r"^\\clbgdkbdiag", readedData) != None:
                        celldefItem["clbgdkbdiag"] = 1
                        readedData = re.sub(r"^\\clbgdkbdiag", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpat>::Neznam vyznam klioveho slova: \\clbgdkbdiag\n")
                    elif re.search(r"^\\clbgdkcross", readedData) != None:
                        celldefItem["clbgdkcross"] = 1
                        readedData = re.sub(r"^\\clbgdkcross", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpat>::Neznam vyznam klioveho slova: \\clbgdkcross\n")
                    elif re.search(r"^\\clbgdkdcross", readedData) != None:
                        celldefItem["clbgdkdcross"] = 1
                        readedData = re.sub(r"^\\clbgdkdcross", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpat>::Neznam vyznam klioveho slova: \\clbgdkdcross\n")
                    """
                    #<cellshad>
                    if re.search(r"^\\clcfpat\d+", readedData) != None:
                        cellKey = True
                        celldefItem["clcfpat"] = re.search(r"^\\clcfpat(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clcfpat\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellshad>::Neznam vyznam klioveho slova: \\clcfpat\n")
                    if re.search(r"^\\clcbpat\d+", readedData) != None:
                        cellKey = True
                        celldefItem["clcbpat"] = re.search(r"^\\clcbpat(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clcbpat\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellshad>::Neznam vyznam klioveho slova: \\clcbpat\n")
                    if re.search(r"^\\clcbpatraw\d+", readedData) != None:
                        cellKey = True
                        celldefItem["clcbpatraw"] = re.search(r"^\\clcbpatraw(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clcbpatraw\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellshad>::Neznam vyznam klioveho slova: \\clcbpatraw\n")
                    if re.search(r"^\\clshdng\d+", readedData) != None:
                        cellKey = True
                        celldefItem["clshdng"] = re.search(r"^\\clshdng(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clshdng\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellshad>::Neznam vyznam klioveho slova: \\clshdng\n")
                    
                    #<cellflow>
                    if re.search(r"^\\cltxlrtb", readedData) != None:
                        cellKey = True
                        celldefItem["cltxlrtb"] = 1
                        readedData = re.sub(r"^\\cltxlrtb", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellflow>::Neznam vyznam klioveho slova: \\cltxlrtb\n")
                    elif re.search(r"^\\cltxtbrl", readedData) != None:
                        cellKey = True
                        celldefItem["cltxtbrl"] = 1
                        readedData = re.sub(r"^\\cltxtbrl", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellflow>::Neznam vyznam klioveho slova: \\cltxtbrl\n")
                    elif re.search(r"^\\cltxbtlr", readedData) != None:
                        cellKey = True
                        celldefItem["cltxbtlr"] = 1
                        readedData = re.sub(r"^\\cltxbtlr", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellflow>::Neznam vyznam klioveho slova: \\cltxbtlr\n")
                    elif re.search(r"^\\cltxlrtbv", readedData) != None:
                        cellKey = True
                        celldefItem["cltxlrtbv"] = 1
                        readedData = re.sub(r"^\\cltxlrtbv", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellflow>::Neznam vyznam klioveho slova: \\cltxlrtbv\n")
                    elif re.search(r"^\\cltxtbrlv", readedData) != None:
                        cellKey = True
                        celldefItem["cltxtbrlv"] = 1
                        readedData = re.sub(r"^\\cltxtbrlv", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellflow>::Neznam vyznam klioveho slova: \\cltxtbrlv\n")
                    """
                    if re.search(r"^\\clFitText", readedData) != None:
                        celldefItem["clFitText"] = 1
                        readedData = re.sub(r"^\\clFitText", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<celldef>::Neznam vyznam klioveho slova: \\clFitText\n")
                    
                    if re.search(r"^\\clNoWrap", readedData) != None:
                        celldefItem["clNoWrap"] = 1
                        readedData = re.sub(r"^\\clNoWrap", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<celldef>::Neznam vyznam klioveho slova: \\clNoWrap\n")
                    
                    #<cellwidth>
                    if re.search(r"^\\clftsWidth\d+", readedData) != None:
                        celldefItem["clftsWidth"] = re.search(r"^\\clftsWidth(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clftsWidth\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellwidth>::Neznam vyznam klioveho slova: \\clftsWidth\n")
                    if re.search(r"^\\clwWidth\d+", readedData) != None:
                        celldefItem["clwWidth"] = re.search(r"^\\clwWidth(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clwWidth\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellwidth>::Neznam vyznam klioveho slova: \\clwWidth\n")
                    if re.search(r"^\\clhidemark", readedData) != None:
                        celldefItem["clhidemark"] = 1
                        readedData = re.sub(r"^\\clhidemark", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellwidth>::Neznam vyznam klioveho slova: \\clhidemark\n")
                    
                    #<cellrev>
                    if re.search(r"^\\clmrgd", readedData) != None:
                        celldefItem["clmrgd"] = 1
                        readedData = re.sub(r"^\\clmrgd", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellrev>::Neznam vyznam klioveho slova: \\clmrgd\n")
                    if re.search(r"^\\clmrgdr", readedData) != None:
                        celldefItem["clmrgdr"] = 1
                        readedData = re.sub(r"^\\clmrgdr", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellrev>::Neznam vyznam klioveho slova: \\clmrgdr\n")
                    if re.search(r"^\\clsplit", readedData) != None:
                        celldefItem["clsplit"] = 1
                        readedData = re.sub(r"^\\clsplit", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellrev>::Neznam vyznam klioveho slova: \\clsplit\n")
                    if re.search(r"^\\clsplitr", readedData) != None:
                        celldefItem["clsplitr"] = 1
                        readedData = re.sub(r"^\\clsplitr", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellrev>::Neznam vyznam klioveho slova: \\clsplitr\n")
                    #<cellrevauth>
                    if re.search(r"^\\clmrgdauth\d+", readedData) != None:
                        celldefItem["clmrgdauth"] = re.search(r"^\\clmrgdauth(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clmrgdauth\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellrevauth>::Neznam vyznam klioveho slova: \\clmrgdauth\n")
                    #<cellrevdate>
                    if re.search(r"^\\clmrgddttm\d+", readedData) != None:
                        celldefItem["clmrgddttm"] = re.search(r"^\\clmrgddttm(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clmrgddttm\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellrevdate>::Neznam vyznam klioveho slova: \\clmrgddttm\n")
                    
                    #<cellins>
                    if re.search(r"^\\clins", readedData) != None:
                        celldefItem["clins"] = 1
                        readedData = re.sub(r"^\\clins", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellins>::Neznam vyznam klioveho slova: \\clins\n")
                    #<cellinsauth>
                    if re.search(r"^\\clinsauth\d+", readedData) != None:
                        celldefItem["clinsauth"] = re.search(r"^\\clinsauth(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clinsauth\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellinsauth>::Neznam vyznam klioveho slova: \\clinsauth\n")
                    #<cellinsdttm>
                    if re.search(r"^\\clinsdttm\d+", readedData) != None:
                        celldefItem["clinsdttm"] = re.search(r"^\\clinsdttm(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clinsdttm\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellinsdttm>::Neznam vyznam klioveho slova: \\clinsdttm\n")
                    
                    #<celldel>
                    if re.search(r"^\\cldel", readedData) != None:
                        celldefItem["cldel"] = 1
                        readedData = re.sub(r"^\\cldel", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<celldel>::Neznam vyznam klioveho slova: \\cldel\n")
                    #<celldelauth>
                    if re.search(r"^\\cldelauth\d+", readedData) != None:
                        celldefItem["cldelauth"] = re.search(r"^\\cldelauth(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\cldelauth\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<celldelauth>::Neznam vyznam klioveho slova: \\cldelauth\n")
                    #<celldeldttm>
                    if re.search(r"^\\cldeldttm\d+", readedData) != None:
                        celldefItem["cldeldttm"] = re.search(r"^\\cldeldttm(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\cldeldttm\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<celldeldttm>::Neznam vyznam klioveho slova: \\cldeldttm\n")
                    
                    #<cellpad>
                    if re.search(r"^\\clpadl\d+", readedData) != None:
                        celldefItem["clpadl"] = re.search(r"^\\clpadl(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clpadl\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpad>::Neznam vyznam klioveho slova: \\clpadl\n")
                    if re.search(r"^\\clpadfl\d+", readedData) != None:
                        celldefItem["clpadfl"] = re.search(r"^\\clpadfl(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clpadfl\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpad>::Neznam vyznam klioveho slova: \\clpadfl\n")
                    if re.search(r"^\\clpadt\d+", readedData) != None:
                        celldefItem["clpadt"] = re.search(r"^\\clpadt(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clpadt\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpad>::Neznam vyznam klioveho slova: \\clpadt\n")
                    if re.search(r"^\\clpadft\d+", readedData) != None:
                        celldefItem["clpadft"] = re.search(r"^\\clpadft(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clpadft\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpad>::Neznam vyznam klioveho slova: \\clpadft\n")
                    if re.search(r"^\\clpadb\d+", readedData) != None:
                        celldefItem["clpadb"] = re.search(r"^\\clpadb(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clpadb\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpad>::Neznam vyznam klioveho slova: \\clpadb\n")
                    if re.search(r"^\\clpadfb\d+", readedData) != None:
                        celldefItem["clpadfb"] = re.search(r"^\\clpadfb(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clpadfb\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpad>::Neznam vyznam klioveho slova: \\clpadfb\n")
                    if re.search(r"^\\clpadr\d+", readedData) != None:
                        celldefItem["clpadr"] = re.search(r"^\\clpadr(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clpadr\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpad>::Neznam vyznam klioveho slova: \\clpadr\n")
                    if re.search(r"^\\clpadfr\d+", readedData) != None:
                        celldefItem["clpadfr"] = re.search(r"^\\clpadfr(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clpadfr\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellpad>::Neznam vyznam klioveho slova: \\clpadfr\n")
                    
                    #<cellsp>
                    if re.search(r"^\\clspl\d+", readedData) != None:
                        celldefItem["clspl"] = re.search(r"^\\clspl(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clspl\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellsp>::Neznam vyznam klioveho slova: \\clspl\n")
                    if re.search(r"^\\clspfl\d+", readedData) != None:
                        celldefItem["clspfl"] = re.search(r"^\\clspfl(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clspfl\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellsp>::Neznam vyznam klioveho slova: \\clspfl\n")
                    if re.search(r"^\\clspt\d+", readedData) != None:
                        celldefItem["clspt"] = re.search(r"^\\clspt(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clspt\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellsp>::Neznam vyznam klioveho slova: \\clspt\n")
                    if re.search(r"^\\clspft\d+", readedData) != None:
                        celldefItem["clspft"] = re.search(r"^\\clspft(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clspft\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellsp>::Neznam vyznam klioveho slova: \\clspft\n")
                    if re.search(r"^\\clspb\d+", readedData) != None:
                        celldefItem["clspb"] = re.search(r"^\\clspb(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clspb\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellsp>::Neznam vyznam klioveho slova: \\clspb\n")
                    if re.search(r"^\\clspfb\d+", readedData) != None:
                        celldefItem["clspfb"] = re.search(r"^\\clspfb(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clspfb\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellsp>::Neznam vyznam klioveho slova: \\clspfb\n")
                    if re.search(r"^\\clspr\d+", readedData) != None:
                        celldefItem["clspr"] = re.search(r"^\\clspr(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clspr\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellsp>::Neznam vyznam klioveho slova: \\clspr\n")
                    if re.search(r"^\\clspfr\d+", readedData) != None:
                        celldefItem["clspfr"] = re.search(r"^\\clspfr(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\clspfr\d+", "", readedData)
                        #sys.stderr.write("RTFParser::MakeTable()::<cellsp>::Neznam vyznam klioveho slova: \\clspfr\n")
                    """
                    if re.search(r"^\\cellx\d+", readedData) != None:
                        cellKey = True
                        celldefItem["cellx"] = re.search(r"^\\cellx(\d+)", readedData).group(1)
                        readedData = re.sub(r"^\\cellx\d+", "", readedData)
                        if re.search(r"^\\intbl", readedData) != None:
                            readedData = re.sub(r"^\\intbl", "", readedData, 1)
                            if re.search(r"^\\cell", readedData) != None:
                                readedData = re.sub(r"^\\cell", "", readedData, 1)
                                #chyba vystupu OCR systemu, kterou je treba osetrit
                                while re.search(r"^\\intbl\\cell", readedData) != None:
                                    #sys.stderr.write("JJ\n")
                                    #sys.stderr.write(readedData[:32]+"\n")
                                    #a=raw_input()
                                    readedData = re.sub(r"^\\intbl\\cell", "", readedData, 1)
                            
                        #sys.stderr.write("RTFParser::MakeTable()::<cellx>::Neznam vyznam klioveho slova: \\cellx\n")
                        currentObject.tableSettings["rowsdef"].append(celldefItem)
                        celldefItem = {}
                    
                    if cellKey:
                        cellKey = False
                    else:
                        sys.stderr.write("RTFParser::MakeTable() - klicove slovo nenalezeno!\n")
                        print readedData
                        sys.exit(1)
                    
            currentObject.tableSettings["celldef"] = celldefItem
            
            #if re.search(r"^\}", readedData) != None:
            #    readedData = re.sub(r"^\}", "", readedData, 1)
            
            tmpArray = []
            #<row>
            row = []
            cell = {}
            #sys.stderr.write("ROW\n")
            while True:
                sys.stderr.write("CELL\n" + readedData[:10] + "\n")
                cellText = ""
                #currentObject.SaveOnStack(currentObject)
                tmpArray = currentObject.Keywords(currentObject, readedData)
                readedData = tmpArray[0]
                #TODO: prijit na to, proc se nekdy vraci }
                #readedData = re.sub(r"^\}", "", readedData, 1)
                
                if re.search(r"^\{", readedData) == None and re.search(r"^\\cell", readedData) == None:
                    break
                
                #sloupec tabulky je vyplnen textem
                if re.search(r"^\{", readedData) != None:
                    readedData = re.sub(r"^\{", "", readedData, 1)
                    #TODO: muze se vyskytnout bookmark
                    #muze se jednat o vice odstavcu
                    while re.search(r"^\\cell", readedData) == None:
                        sys.stderr.write("CELL1\n" + readedData[:10] + "\n")
                        
                        isBookmark = False
                        if re.search(r"^\\\*\\bkmkstart", readedData) != None:
                            isBookmark = True
                            #print readedData
                            tmpArray = currentObject.Bookmark(currentObject, readedData)
                            readedData = tmpArray[0]
                            #print readedData
                            #sys.exit(0)
                        
                        if re.search(r"^\}", readedData) != None:
                            readedData = re.sub(r"^\}", "", readedData, 1)
                        
                        if re.search(r"^\{", readedData) != None:
                            readedData = re.sub(r"^\{", "", readedData, 1)
                        
                        #nastaveni vsech keywords
                        #currentObject.SaveOnStack(currentObject)
                        tmpArray = currentObject.Keywords(currentObject, readedData)
                        readedData = tmpArray[0]
                        #a=raw_input()
                        #if isBookmark:
                        #    print readedData
                        #    sys.exit(0)
                        #pokud se za keywords nachazi text
                        if re.search(r"^\s", readedData) != None:
                            readedData = re.sub(r"^\s", "", readedData, 1)
                            cellText += re.search(r"^[^\}]*", readedData).group(0)
                            #TODO: udelat tuhle kontrolu pro vice jak jedno opakovani
                            #if re.search(r"\\$", cellText) != None:
                            while re.search(r"\\$", cellText) != None:
                                sys.stderr.write("CELL Prodluzuji\n")
                                sys.stderr.write(readedData[:64] + "\n")
                                if re.search(r"\\\\$", cellText) == None:
                                    cellText += "}"
                                    readedData = re.sub(r"^[^\}]*\}", "", readedData, 1)
                                    cellText += re.search(r"^[^\}]*", readedData).group(0)
                                else:
                                    break
                                    #readedData = re.sub(r"^[^\}]*\}", "", readedData, 1)
                                    #print cellText
                                    #sys.stderr.write("JJJ!!!\n")
                                    #sys.exit(0)
                                #elif re.search(r"\\\}$", cellText) == None:
                                #    cellText += "}"
                                #    readedData = re.sub(r"^[^\}]*\}", "", readedData, 1)
                                #    cellText += re.search(r"^[^\}]*", readedData).group(0)
                            readedData = re.sub(r"^[^\}]*\}", "", readedData, 1)
                        
                        #pokud je na zacatku \par, urizneme jej, protoze by to jinak zpusobovalo problemy 
                        if re.search(r"^\\par", readedData) != None:
                            #sys.stderr.write("PAR\n")
                            re.sub(r"^\\par", "", readedData, 1)
                
                cell["ul"] = currentObject.chrfmt["ul"]
                cell["i"] = currentObject.chrfmt["i"]
                cell["b"] = currentObject.chrfmt["b"]
                cell["f"] = currentObject.parfmt["f"]
                cell["fs"] = currentObject.parfmt["fs"]
                cell["cs"] = currentObject.chrfmt["cs"]
                cell["trrh"] = abs(int(currentObject.tableSettings["trrh"]))
                cell["text"] = cellText
                readedData = re.sub(r"^\\cell", "", readedData, 1)
                row.append(cell)
                cell = {}
            
            #print row
            readedData = re.sub(r"^\\row", "", readedData, 1)
            table["rows"].append(row)
            
            #konec tabulky
            if re.search(r"^\}", readedData) != None:
                readedData = re.sub(r"^\}", "", readedData)
                break
                
        #print "TABLE"
        #print readedData
        table["posx"] = currentObject.apoctl["posx"]
        table["posy"] = currentObject.apoctl["posy"]
        table["absh"] = currentObject.apoctl["absh"]
        
        if not currentObject.parfmt["li"]:
            table["li"] = currentObject.defLi
        else:
            table["li"] = currentObject.parfmt["li"]
        
        if not currentObject.parfmt["ri"]:
            table["ri"] = currentObject.defLi
        else:
            table["ri"] = currentObject.parfmt["ri"]
        
        if currentObject.parfmt["qc"] == 1:
            table["alignment"] = "centered"
        elif currentObject.parfmt["qj"] == 1:
            table["alignment"] = "justified"
        elif currentObject.parfmt["qr"] == 1:
            table["alignment"] = "right"
        else:
            table["alignment"] = "left"
        
        if not currentObject.parfmt["sb"]:
            table["spaceBefore"] = currentObject.defSb
        else:
            table["spaceBefore"] = currentObject.parfmt["sb"]
        
        if not currentObject.parfmt["sa"]:
            table["spaceAfter"] = currentObject.defSa
        else:
            table["spaceAfter"] = currentObject.parfmt["sa"]
        
        #print table
        #print currentObject.tableSettings["rowsdef"]
        
        gridCols = []
        #prava pozice na ose x
        colX = int(currentObject.tableSettings["rowsdef"][0]["cellx"])
        for item in currentObject.tableSettings["rowsdef"]:
            if int(item["cellx"]) < int(colX):
                break
            colX = int(item["cellx"])
            gridCols.append(colX)
        
        fsH = []
        #vyska radku
        colH = table["rows"][0][0]["fs"]
        for item in table["rows"]:
            colH = item[0]["fs"]
            for itemRows in item:
                if int(itemRows["fs"]) > int(colH):
                    colH = int(itemRows["fs"])
            fsH.append(colH)
        
        #print gridCols
        #print fsH
        #sys.exit(0)
        xml = ""
        xml += "<table l=\"" + table["posx"] + "\" t=\"" + table["posy"] + "\" "
        currentObject.xmlList.append("<table l=\"" + table["posx"] + "\" t=\"" + table["posy"] + "\" ")
        xml += "r=\"" + str(int(table["posx"])+gridCols[-1]) + "\" "
        currentObject.xmlList.append("r=\"" + str(int(table["posx"])+gridCols[-1]) + "\" ")
        xml += "b=\"" + str(int(table["posy"]) + int(table["absh"])) + "\" "
        currentObject.xmlList.append("b=\"" + str(int(table["posy"]) + int(table["absh"])) + "\" ")
        xml += "alignment=\"" + table["alignment"] + "\" "
        currentObject.xmlList.append("alignment=\"" + table["alignment"] + "\" ")
        xml += "li=\"" + table["li"] + "\" "
        currentObject.xmlList.append("li=\"" + table["li"] + "\" ")
        xml += "ri=\"" + table["ri"] + "\" "
        currentObject.xmlList.append("ri=\"" + table["ri"] + "\" ")
        xml += "spaceBefore=\"" + table["spaceBefore"] + "\" "
        currentObject.xmlList.append("spaceBefore=\"" + table["spaceBefore"] + "\" ")
        xml += "spaceAfter=\"" + table["spaceAfter"] + "\">\n"
        currentObject.xmlList.append("spaceAfter=\"" + table["spaceAfter"] + "\">\n")
        #print currentObject.tableSettings
        if currentObject.tableSettings["rowsdef"][1].has_key("brdrs") and currentObject.tableSettings["rowsdef"][1]["brdrs"]:
            xml += "<leftBorder type=\"single\" width=\"" + currentObject.tableSettings["rowsdef"][1]["brdrw"] + "\"/>\n"
            currentObject.xmlList.append("<leftBorder type=\"single\" width=\"" + currentObject.tableSettings["rowsdef"][1]["brdrw"] + "\"/>\n")
            xml += "<topBorder type=\"single\" width=\"" + currentObject.tableSettings["rowsdef"][1]["brdrw"] + "\"/>\n"
            currentObject.xmlList.append("<topBorder type=\"single\" width=\"" + currentObject.tableSettings["rowsdef"][1]["brdrw"] + "\"/>\n")
            xml += "<rightBorder type=\"single\" width=\"" + currentObject.tableSettings["rowsdef"][1]["brdrw"] + "\"/>\n"
            currentObject.xmlList.append("<rightBorder type=\"single\" width=\"" + currentObject.tableSettings["rowsdef"][1]["brdrw"] + "\"/>\n")
            xml += "<bottomBorder type=\"single\" width=\"" + currentObject.tableSettings["rowsdef"][1]["brdrw"] + "\"/>\n"
            currentObject.xmlList.append("<bottomBorder type=\"single\" width=\"" + currentObject.tableSettings["rowsdef"][1]["brdrw"] + "\"/>\n")
        else:
            #try:
            #    xml += "<leftBorder type=\"single\" width=\"" + currentObject.tableSettings["rowsdef"][1]["brdrw"] + "\"/>\n"
            #except KeyError:
            #    print currentObject.tableSettings["rowsdef"][1]
            #    sys.exit(1)
            xml += "<leftBorder type=\"single\" width=\"" + str(300) + "\"/>\n"
            currentObject.xmlList.append("<leftBorder type=\"single\" width=\"" + str(300) + "\"/>\n")
            xml += "<topBorder type=\"single\" width=\"" + str(300) + "\"/>\n"
            currentObject.xmlList.append("<topBorder type=\"single\" width=\"" + str(300) + "\"/>\n")
            xml += "<rightBorder type=\"single\" width=\"" + str(300) + "\"/>\n"
            currentObject.xmlList.append("<rightBorder type=\"single\" width=\"" + str(300) + "\"/>\n")
            xml += "<bottomBorder type=\"single\" width=\"" + str(300) + "\"/>\n "
            currentObject.xmlList.append("<bottomBorder type=\"single\" width=\"" + str(300) + "\"/>\n ")
        xml += "<gridTable>\n"
        currentObject.xmlList.append("<gridTable>\n")
        for item in gridCols:
            xml += "<gridCol>"
            currentObject.xmlList.append("<gridCol>")
            xml += str(item)
            currentObject.xmlList.append(str(item))
            xml += "</gridCol>\n"
            currentObject.xmlList.append("</gridCol>\n")
        for item in table["rows"]:
            xml += "<gridRow>"
            currentObject.xmlList.append("<gridRow>")
            xml += str(item[0]["trrh"])
            currentObject.xmlList.append(str(item[0]["trrh"]))
            xml += "</gridRow>\n"
            currentObject.xmlList.append("</gridRow>\n")
        xml += "</gridTable>\n"
        currentObject.xmlList.append("</gridTable>\n")
        
        colPos = 0
        rowPos = 0
        gridColPos = 0
        l = table["posx"]
        constL = table["posx"]
        t = table["posy"]
        for item in table["rows"]:
            colPos = 0
            l = table["posx"]
            for itemRow in item:
                xml += "<cell gridColFrom=\"" + str(colPos) + "\" gridColTill=\"" + str(colPos) + "\" "
                currentObject.xmlList.append("<cell gridColFrom=\"" + str(colPos) + "\" gridColTill=\"" + str(colPos) + "\" ")
                xml += "gridRowFrom=\"" + str(rowPos) + "\" gridRowTill=\"" + str(rowPos) + "\" "
                currentObject.xmlList.append("gridRowFrom=\"" + str(rowPos) + "\" gridRowTill=\"" + str(rowPos) + "\" ")
                xml += "alignment=\"" + table["alignment"] + "\" verticalAlignment=\"center\">\n"
                currentObject.xmlList.append("alignment=\"" + table["alignment"] + "\" verticalAlignment=\"center\">\n")
                if not currentObject.tableSettings["rowsdef"][1].has_key("brdrw"):
                    xml += "<leftBorder type=\"single\" width=\"" + str(300) + "\"/>\n"
                    currentObject.xmlList.append("<leftBorder type=\"single\" width=\"" + str(300) + "\"/>\n")
                    xml += "<topBorder type=\"single\" width=\"" + str(300) + "\"/>\n"
                    currentObject.xmlList.append("<topBorder type=\"single\" width=\"" + str(300) + "\"/>\n")
                    xml += "<rightBorder type=\"single\" width=\"" + str(300) + "\"/>\n"
                    currentObject.xmlList.append("<rightBorder type=\"single\" width=\"" + str(300) + "\"/>\n")
                    xml += "<bottomBorder type=\"single\" width=\"" + str(300) + "\"/>\n"
                    currentObject.xmlList.append("<bottomBorder type=\"single\" width=\"" + str(300) + "\"/>\n")
                else:
                    xml += "<leftBorder type=\"single\" width=\"" + currentObject.tableSettings["rowsdef"][1]["brdrw"] + "\"/>\n"
                    currentObject.xmlList.append("<leftBorder type=\"single\" width=\"" + currentObject.tableSettings["rowsdef"][1]["brdrw"] + "\"/>\n")
                    xml += "<topBorder type=\"single\" width=\"" + currentObject.tableSettings["rowsdef"][1]["brdrw"] + "\"/>\n"
                    currentObject.xmlList.append("<topBorder type=\"single\" width=\"" + currentObject.tableSettings["rowsdef"][1]["brdrw"] + "\"/>\n")
                    xml += "<rightBorder type=\"single\" width=\"" + currentObject.tableSettings["rowsdef"][1]["brdrw"] + "\"/>\n"
                    currentObject.xmlList.append("<rightBorder type=\"single\" width=\"" + currentObject.tableSettings["rowsdef"][1]["brdrw"] + "\"/>\n")
                    xml += "<bottomBorder type=\"single\" width=\"" + currentObject.tableSettings["rowsdef"][1]["brdrw"] + "\"/>\n"
                    currentObject.xmlList.append("<bottomBorder type=\"single\" width=\"" + currentObject.tableSettings["rowsdef"][1]["brdrw"] + "\"/>\n")
                
                xml += "<para l=\"" + str(l) + "\" t=\"" + str(t) + "\" r=\"" + str(int(constL) + int(currentObject.tableSettings["rowsdef"][gridColPos]["cellx"])) + "\" b=\"" + str((int(t) + int(itemRow["trrh"])*(rowPos+1))) + "\" "
                currentObject.xmlList.append("<para l=\"" + str(l) + "\" t=\"" + str(t) + "\" r=\"" + str(int(constL) + int(currentObject.tableSettings["rowsdef"][gridColPos]["cellx"])) + "\" b=\"" + str((int(t) + int(itemRow["trrh"])*(rowPos+1))) + "\" ")
                xml += "alignment=\"" + table["alignment"] + "\" li=\"" + table["li"] + "\" "
                currentObject.xmlList.append("alignment=\"" + table["alignment"] + "\" li=\"" + table["li"] + "\" ")
                if currentObject.parfmt["slmult"] == "1":
                    xml += "lsp=\"single\" "
                    currentObject.xmlList.append("lsp=\"single\" ")
                else:
                    xml += "lsp=\"exactly\" "
                    currentObject.xmlList.append("lsp=\"exactly\" ")
                    if not currentObject.parfmt["sl"] or currentObject.parfmt["sl"] == "0":
                        xml += "lspExact=\"" + str(int(itemRow["fs"])*10) + "\" "
                        currentObject.xmlList.append("lspExact=\"" + str(int(itemRow["fs"])*10) + "\" ")
                    else:
                        xml += "lspExact=\"" + str(abs(int(currentObject.parfmt["sl"]))) + "\" "
                        currentObject.xmlList.append("lspExact=\"" + str(abs(int(currentObject.parfmt["sl"]))) + "\" ")
                if currentObject.parfmt["lang"] == "1033":
                    xml += "language=\"en\" "
                    currentObject.xmlList.append("language=\"en\" ")
                else:
                    xml += "language=\"unknown\" "
                    currentObject.xmlList.append("language=\"unknown\" ")
                xml += "styleRef=\"" + itemRow["cs"] + "\">\n"
                currentObject.xmlList.append("styleRef=\"" + itemRow["cs"] + "\">\n")
                xml += "<ln l=\"" + str(l) + "\" t=\"" + str(t) + "\" r=\"" + str(int(constL) + int(currentObject.tableSettings["rowsdef"][gridColPos]["cellx"])) + "\" b=\"" + str((int(t) + int(itemRow["trrh"])*(rowPos+1))) + "\" "
                currentObject.xmlList.append("<ln l=\"" + str(l) + "\" t=\"" + str(t) + "\" r=\"" + str(int(constL) + int(currentObject.tableSettings["rowsdef"][gridColPos]["cellx"])) + "\" b=\"" + str((int(t) + int(itemRow["trrh"])*(rowPos+1))) + "\" ")
                xml += "baseLine=\"" + str((int(t) + int(itemRow["trrh"])*(rowPos+1))) + "\">\n"
                currentObject.xmlList.append("baseLine=\"" + str((int(t) + int(itemRow["trrh"])*(rowPos+1))) + "\">\n")
                xml += "<run "
                currentObject.xmlList.append("<run ")
                if itemRow["ul"] == "0":
                    xml += "underlined=\"none\" "
                    currentObject.xmlList.append("underlined=\"none\" ")
                else:
                    xml += "underlined=\"yes\" "
                    currentObject.xmlList.append("underlined=\"yes\" ")
                xml += "subsuperscript=\"none\" "
                currentObject.xmlList.append("subsuperscript=\"none\" ")
                if itemRow["f"] == "":
                    itemRow["f"] = currentObject.defFont
                
                fontStyle = {}
                if not itemRow.has_key("f"):
                    for itemFont in currentObject.fontInfo:
                        if str(currentObject.styleSheetTable[0]["f"]) == str(itemFont["id"]):
                            fontStyle = itemFont
                            break
                else:
                    for itemFont in currentObject.fontInfo:
                        if str(itemFont["id"]) == str(itemRow["f"]):
                            fontStyle = itemFont
                            break
                
                xml += "fontSize=\"" + str(int(float(int(itemRow["fs"]))*50)) + "\" "
                currentObject.xmlList.append("fontSize=\"" + str(int(float(int(itemRow["fs"]))*50)) + "\" ")
                try:
                    xml += "fontFace=\"" + fontStyle["fontName"] + "\" "
                except KeyError:
                    print itemRow["f"]
                    print fontStyle
                    sys.exit(1)
                currentObject.xmlList.append("fontFace=\"" + fontStyle["fontName"] + "\" ")
                xml += "fontFamily=\"" + fontStyle["fontFamily"] + "\" "
                currentObject.xmlList.append("fontFamily=\"" + fontStyle["fontFamily"] + "\" ")
                xml += "fontPitch=\"variable\" "
                currentObject.xmlList.append("fontPitch=\"variable\" ")
                xml += "spacing=\"10\">\n"
                currentObject.xmlList.append("spacing=\"10\">\n")
                xml += "<wd l=\"" + str(l) + "\" t=\"" + str(t) + "\" r=\"" + str(int(constL) + int(currentObject.tableSettings["rowsdef"][gridColPos]["cellx"])) + "\" b=\"" + str((int(t) + int(itemRow["trrh"])*(rowPos+1))) + "\">"
                currentObject.xmlList.append("<wd l=\"" + str(l) + "\" t=\"" + str(t) + "\" r=\"" + str(int(constL) + int(currentObject.tableSettings["rowsdef"][gridColPos]["cellx"])) + "\" b=\"" + str((int(t) + int(itemRow["trrh"])*(rowPos+1))) + "\">")
                #print "\"" + itemRow["text"] + "\""
                if itemRow["text"] == "":
                    xml += "_"
                    currentObject.xmlList.append("_")
                else:
                    xml += itemRow["text"]
                    currentObject.xmlList.append(itemRow["text"])
                xml += "</wd>\n"
                currentObject.xmlList.append("</wd>\n")
                xml += "</run>\n"
                currentObject.xmlList.append("</run>\n")
                xml += "</ln>\n"
                currentObject.xmlList.append("</ln>\n")
                xml += "</para>\n"
                currentObject.xmlList.append("</para>\n")
                xml += "</cell>\n"
                currentObject.xmlList.append("</cell>\n")
                l = str(int(constL) + int(currentObject.tableSettings["rowsdef"][gridColPos]["cellx"]))
                gridColPos += 1
                colPos += 1
            rowPos +=1
        xml += "</table>\n"
        currentObject.xmlList.append("</table>\n")
        currentObject.xmlParaList.append(currentObject.xmlList)
        currentObject.xmlList = []
        #print gridRows
        #print xml
        #sys.stderr.write("Table done\n")
        #sys.exit(0)
        retArray.append(readedData)
        retArray.append(xml)
        return retArray
    
    #Metoda ukladajici aktualni stav na zasobnik
    #param1 objekt, jehoz stav se ma ulozit na zasobnik
    def SaveOnStack(self, currentObject):
        stackItem = []
        
        #stackItem.append(currentObject.keywords)
        currentObject.stack.append(stackItem)
    
    #Metoda nahravajici stav na zasobnik
    #param1 objekt, jehoz stav se ma nahrat ze zasobniku
    def LoadFromStack(self, currentObject):
        topItem = len(currentObject.stack) - 1
        currentObject.keywords = currentObject.stack[topItem]
    
    #Metoda parsujici vychozi nastaveni znaku
    #@param1 objekt, do ktereho by se pripadne ukladaly informace
    #@param2 nacteny RTF soubor
    def SetDefPropChar(self, currentObject, readedData):
        while True:
            if readedData[0] == '}':
                break
            keyword = re.search(r"^\\[a-zA-Z]+", readedData).group(0)
            if keyword == "\\fs":
                readedData = re.sub(r"\\fs", "", readedData, 1)
                value = re.search(r"^\d+", readedData).group(0)
                currentObject.defFs = value
                readedData = re.sub(r"\d+", "", readedData, 1)
            elif keyword == "\\afs":
                readedData = re.sub(r"\\[a-zA-Z]+", "", readedData, 1)
                value = re.search(r"^\d+", readedData).group(0)
                currentObject.defAFs = value
                readedData = re.sub(r"\d+", "", readedData, 1)
            elif keyword == "\\loch":
                readedData = re.sub(r"\\[a-zA-Z]+", "", readedData, 1)
                currentObject.defLoch = True
            elif keyword =="\\hich":
                readedData = re.sub(r"\\[a-zA-Z]+", "", readedData, 1)
                currentObject.defHich = True
            elif keyword == "\\dbch":
                readedData = re.sub(r"\\[a-zA-Z]+", "", readedData, 1)
                currentObject.defdbch = True
            elif keyword == "\\af":
                readedData = re.sub(r"\\[a-zA-Z]+", "", readedData, 1)
                value = re.search(r"^\d+", readedData).group(0)
                currentObject.defAF = value
                readedData = re.sub(r"\d+", "", readedData, 1)
                
    #Metoda parsujici vychozi nastaveni znaku
    #@param1 objekt, do ktereho by se pripadne ukladaly informace
    #@param2 nacteny RTF soubor
    def SetDefPropPap(self, currentObject, readedData):
        while True:
            if readedData[0] == '}':
                break
            keyword = re.search(r"^\\[a-zA-Z]+", readedData).group(0)
            if keyword == "\\aspalpha":
                readedData = re.sub(r"\\[a-zA-Z]+", "", readedData, 1)
                currentObject.defAspAlpha = True
            elif keyword == "\\aspnum":
                readedData = re.sub(r"\\[a-zA-Z]+", "", readedData, 1)
                currentObject.defAspNum = True
            elif keyword == "\\faauto":
                readedData = re.sub(r"\\[a-zA-Z]+", "", readedData, 1)
                currentObject.defFaAuto = True
            elif keyword == "\\adjustright":
                readedData = re.sub(r"\\[a-zA-Z]+", "", readedData, 1)
                currentObject.defAdjustRight = True
            elif keyword == "\\cgrid":
                readedData = re.sub(r"\\[a-zA-Z]+", "", readedData, 1)
                currentObject.defCGrid = True
            elif keyword == "\\li":
                readedData = re.sub(r"\\[a-zA-Z]+", "", readedData, 1)
                value = re.search(r"^\d+", readedData).group(0)
                currentObject.defLi = value
                readedData = re.sub(r"\d+", "", readedData, 1)
            elif keyword == "\\ri":
                readedData = re.sub(r"\\[a-zA-Z]+", "", readedData, 1)
                value = re.search(r"^\d+", readedData).group(0)
                currentObject.defRi = value
                readedData = re.sub(r"\d+", "", readedData, 1)
            elif keyword == "\\fi":
                readedData = re.sub(r"\\[a-zA-Z]+", "", readedData, 1)
                value = re.search(r"^\d+", readedData).group(0)
                currentObject.defFi = value
                readedData = re.sub(r"\d+", "", readedData, 1)
            elif keyword == "\\sb":
                readedData = re.sub(r"\\[a-zA-Z]+", "", readedData, 1)
                value = re.search(r"^\d+", readedData).group(0)
                currentObject.defSb = value
                readedData = re.sub(r"\d+", "", readedData, 1)
            elif keyword == "\\sa":
                readedData = re.sub(r"\\[a-zA-Z]+", "", readedData, 1)
                value = re.search(r"^\d+", readedData).group(0)
                currentObject.defSa = value
                readedData = re.sub(r"\d+", "", readedData, 1)
            elif keyword == "\\sl":
                readedData = re.sub(r"\\[a-zA-Z]+", "", readedData, 1)
                value = re.search(r"^\d+", readedData).group(0)
                currentObject.defSl = value
                readedData = re.sub(r"\d+", "", readedData, 1)
            elif keyword == "\\slmult":
                readedData = re.sub(r"\\[a-zA-Z]+", "", readedData, 1)
                value = re.search(r"^\d+", readedData).group(0)
                currentObject.defslmult = value
                readedData = re.sub(r"\d+", "", readedData, 1)
            elif keyword == "\\ql":
                readedData = re.sub(r"\\[a-zA-Z]+", "", readedData, 1)
                currentObject.defAligment = "ql"
            elif keyword == "\\ltrpar":
                readedData = re.sub(r"\\[a-zA-Z]+", "", readedData, 1)
                currentObject.defBidirectControls = "ltrpar"
    
    #Metoda tisknouci surovy text
    def InterpretPlainText(self, currentObject):
        plainText = ""
        
        for item in currentObject.plainText:
            text = item["text"]
            
            #odstraneni CRLF
            text = re.sub(r"\r\n", "", text)
            #dosazeni tabulatoru do textu
            text = re.sub(r"\\tab", "\t", text)
            #dosazeni odradkovani do textu
            text = re.sub(r"\\line", "\n", text)
            #znaky zapsany hexadecimalne jsou docasne odstraneny
            text = re.sub(r"\\\'((\d{2})|([A-Z]{2})|([A-Z]\d)|(\d[A-Z]))", "", text)
            #znaky zapsane v unicode jsou docasne odstraneny
            text = re.sub(r"\\u\d+(\?)?", "", text)
            #znaky < a > jsou zmeneny na -, protoze - v xml nema zadny vyznam
            text = re.sub(r"(<|>)", "-", text)
            #while re.search(r"\\\'\d+", text) != None:
                
                #num = re.search(r"\\\'(\d+)", text).group(1)
                #if currentObject.hexTable.has_key(str(num)):
                #    text = re.sub(r"\\\'(\d+)", currentObject.hexTable[str(num)], text, 1)
                #else:
                #    hexStr = "\\x"+str(num)
                #    sys.stderr.write(hexStr+"\n")
                #    text = re.sub(r"\\\'(\d+)", hexStr, text, 1)
            #while re.search(r"\\\\line\\r\\n", text) != None:
            #    tmpStr = re.search(r"^[^(\\\\line\\r\\n)]+\\\\line\\r\\n", text).group(0)
            #    tmpStr = re.sub(r"\\\\line\\r\\n$", "", tmpStr)
            #    plainText += tmpStr + "\n"
            #if text:
            plainText += text
        
        #print plainText.encode("utf-8")
        return plainText
    
    #Metoda parsujici Bookmark v Body
    #@param1 objekt, do ktereho by se pripadne ukladaly informace
    #@param2 nacteny RTF soubor
    #@return1 nenaparsovana cast RTF souboru
    #@return2 cast xml vystupu
    def Bookmark(self, currentObject, readedData):
        retArray = []
        xml = ""
        
        readedData = re.sub(r"\\\*\\bkmkstart", "", readedData, 1)
        #print readedData
        bkmkcolf = ""
        bkmkcoll = ""
        name = ""
        bookmark = {}
        #<bkmkstart>
        while True:
            #sys.stderr.write(readedData[:10]+"\n")
            if readedData[0] != '\\':
                break
            if re.search(r"\\bkmkcolf\d+", readedData) != None:
                bkmkcolf = re.search(r"\\bkmkcolf(\d+)", readedData).group(1)
                readedData = re.sub(r"\\bkmkcolf(\d+)", "", readedData, 1)
            if re.search(r"\\bkmkcoll\d+", readedData) != None:
                bkmkcoll = re.search(r"\\bkmkcoll(\d+)", readedData).group(1)
                readedData = re.sub(r"\\bkmkcoll(\d+)", "", readedData, 1)
        readedData = re.sub(r"^\s+", "", readedData, 1)
        name = re.search(r"[^\}]+", readedData).group(0)
        readedData = re.sub(r"^[^\}]+\}(\x0D\x0A)?", "", readedData, 1)
        bookmark["name"] = name
        #print bookmark["name"]
        bookmark["bkmkcolf"] = bkmkcolf
        bookmark["bkmkcoll"] = bkmkcoll
        #print readedData
        #<bookmark>
        bookmark["text"] = ""
        #print "READEDDATA"
        #print readedData
        while True:
            sys.stderr.write(readedData[:64]+"\n")
            if re.search(r"^\\cell", readedData) != None:
                sys.stderr.write("MAM TO!!!\n")
                break
            #sys.stdout.write(readedData[:20]+"\n")
            #sys.stdout.flush()
            if re.search(r"^\{", readedData) != None:
                if re.search(r"^\{\\\*\\bkmkend", readedData) != None:
                    break
                #print "text"
                readedData = re.sub(r"\{", "", readedData, 1)
                #print "READEDDATA"
                #print readedData
                #currentObject.SaveOnStack(currentObject)
                tmpArray = currentObject.Keywords(currentObject, readedData)
                readedData = tmpArray[0]
                #print "Returned"
                #print readedData[:20]
                xml += tmpArray[1]
                readedData = re.sub(r"^\s", "", readedData, 1)
                if re.search(r"^\{\\\*\\bkmkend", readedData) != None:
                    continue
                if re.search(r"^\\\*\\bkmkstart", readedData) != None:
                    tmpArray = currentObject.Bookmark(currentObject, readedData)
                    readedData = tmpArray[0]
                    #print readedData
                    #sys.exit(0)
                else:
                    try:
                        bookmark["text"] += re.search(r"^[^\}]*", readedData).group(0)
                        #TODO: Udelat to v cyklu
                        while re.search(r"\\$", bookmark["text"]) != None:
                            if re.search(r"\\\\$", bookmark["text"]) == None:
                                bookmark["text"] += "}"
                                readedData = re.sub(r"^[^\}]*\}",  "",  readedData, 1)
                                bookmark["text"] += re.search(r"^[^\}]*", readedData).group(0)
                            else:
                                break
                        readedData = re.sub(r"^[^\}]*\}",  "",  readedData, 1)
                        #TOHLE JE JEN TEST
                        readedData = re.sub(r"^\}+", "", readedData, 1)
                        bookmark["text"] = re.sub(r"^\s", "", bookmark["text"], 1)
                        #print "\"" + bookmark["text"] + "\""
                    except AttributeError:
                        print readedData
                        sys.exit(0)
                    #print bookmark["text"]
                    plainText = {}
                    plainText["text"] = bookmark["text"]
                    plainText["special"] = currentObject.special
                    currentObject.plainText.append(plainText)
                    #print readedData
                    #print readedData
                    #tmpArray = currentObject.ParseText(currentObject, readedData)
                    #readedData = tmpArray[0]
                    #print "NEXT READ"
                    #print readedData
                    #sys.exit(0)
                    #print "Returned ParseText"
                    #print readedData[:64]
                    #xml += tmpArray[1]
                    #print readedData
                    #sys.exit(0)
                    if re.search(r"^\{", readedData) == None:
                        readedData = re.sub(r"^[^\}]*\}(\x0D\x0A)?", "", readedData, 1)
                    currentObject.bookmarks.append(bookmark)
                #print currentObject.bookmarks
                #print readedData
        #print bookmark["text"]
        currentObject.ParseText(currentObject, bookmark["text"] + "}")
        #currentObject.LoadFromStack(currentObject)
        #print readedData
        #sys.exit(0)
        #print currentObject.plainText
        #sys.exit(0)
        #<bookmarkend>
        if re.search(r"^\{", readedData) != None:
            readedData = re.sub(r"\{", "", readedData, 1)
            if re.search(r"\\\*\\bkmkend", readedData) != None:
                readedData = re.sub(r"\\\*\\bkmkend[^\}]+\}(\}{3})?", "", readedData, 1)
        #print readedData
            #zde pokracovat
            #naimplementovat zasobnik nastaveni
        #sys.stderr.write("811:zde pokracovat\n")
        retArray.append(readedData)
        retArray.append(xml)
        return retArray
    
    #TODO: pred parsaci textu odstranit prvni bily znak
    #Metoda parsujici text v Body
    #@param1 objekt, do ktereho by se pripadne ukladaly informace
    #@param2 nacteny RTF soubor
    #@return1 nenaparsovana cast RTF souboru
    #@return2 cast xml vystupu
    def ParseText(self, currentObject, readedData):
        retArray = []
        xml = ""
        richTextDic = {}
        global imp_mode
        
        readedData = re.sub(r"^\s", "", readedData, 1)
        #print readedData
        #sys.exit(0)
        if re.search(r"^[^\}]*", readedData) != None:
            plainText = {}
            
            #print "OLD"
            #print readedData
            #sys.exit(0)
            tmpStr = ""
            while True:
                tmpStr += re.search(r"^[^\}]*", readedData).group(0)
                readedData = re.sub(r"^[^\}]*", "", readedData, 1)
                if len(tmpStr) > 0 and tmpStr[-1] == '\\' and readedData[0] == '}':
                    tmpStr += "}"
                    readedData = re.sub(r"^\}", "", readedData, 1)
                    continue
                break
            """
            tmpStr = re.search(r"^[^\}]*", readedData).group(0)
            #print tmpStr
            if re.search(r"\\$", tmpStr) != None:
                #tohle tu je, protoze se muze stat, ze text bude ve tvaru neco\\, cimz by podminka sice byla
                #splnena, ale pritom se nejedna o vec, proc ta podminka byla napsana
                if re.search(r"(\\){2,}$", tmpStr) == None:
                    #sys.stderr.write("JJ\n")
                    #sys.exit(0)
                    tmpStr += "}"
                    #print tmpStr
                    #print readedData
                    #sys.exit(0)
                    tmpStr = re.sub(r"\\{", "{", tmpStr)
                    tmpStr = re.sub(r"\\}", "}", tmpStr)
                    if re.search(r"^[^\}]*\}(\x0D\x0A)?\\\}", readedData) == None:
                        readedData = re.sub(r"^[^\}]*\}(\x0D\x0A)?", "", readedData, 1)
                        tmpStr += re.search(r"^[^\}]*", readedData).group(0)
            """
            #print "newTmpStr"
            #print tmpStr
            plainText["text"] = tmpStr
            plainText["special"] = currentObject.special
            currentObject.plainText.append(plainText)
            #currentObject.plainText.append(re.search(r"^[^\}]*", readedData).group(0))
            #if imp_mode:
            #    sys.stderr.write("886: doplnit richText\n")
            if currentObject.init:
                xml += "<section l=\"" + str(currentObject.apoctl["posx"]) + "\" t=\"" + str(currentObject.apoctl["posy"])
                
                if currentObject.apoctl["absw"] == "":
                    lineSize = len(tmpStr)
                    
                    if currentObject.parfmt["fs"] == "":
                        lineSize = int(float(currentObject.defFs)*float(lineSize)*10.0*(25.0/48.0))
                        lineHeight = int(float(currentObject.defFs)*10.0*(25.0/48.0))
                    else:
                        lineSize = int(float(currentObject.parfmt["fs"])*float(lineSize)*10.0*(25.0/48.0))
                        lineHeight = int(float(currentObject.parfmt["fs"])*10.0*(25.0/48.0))
                    
                    xml += "\" r=\"" + str(int(currentObject.apoctl["posx"]) + lineSize)
                    xml += "\" b=\"" + str(int(currentObject.apoctl["posy"]) + lineHeight) +"\">\n"
                else:
                    xml += "\" r=\"" + str(int(currentObject.apoctl["posx"]) + abs(int(currentObject.apoctl["absw"])))
                    xml += "\" b=\"" + str(int(currentObject.apoctl["posy"]) + abs(int(currentObject.apoctl["absh"]))) +"\">\n"
                
                xml += "<column l=\"" + str(currentObject.apoctl["posx"]) + "\" t=\"" + str(currentObject.apoctl["posy"])
                if currentObject.apoctl["absw"] == "":
                    lineSize = len(tmpStr)
                    lineSize = int(float(currentObject.parfmt["fs"])*float(lineSize)*10.0*(25.0/48.0))
                    xml += "\" r=\"" + str(int(currentObject.apoctl["posx"]) + lineSize)
                    lineHeight = int(float(currentObject.parfmt["fs"])*10.0*(25.0/48.0))
                    xml += "\" b=\"" + str(int(currentObject.apoctl["posy"]) + lineHeight) +"\">\n"
                else:
                    xml += "\" r=\"" + str(int(currentObject.apoctl["posx"]) + abs(int(currentObject.apoctl["absw"])))
                    xml += "\" b=\"" + str(int(currentObject.apoctl["posy"]) + abs(int(currentObject.apoctl["absh"]))) +"\">\n"
            #par
            if not currentObject.par:
                xml += "<para l=\"" + str(currentObject.apoctl["posx"]) + "\" t=\"" + str(currentObject.apoctl["posy"])
                currentObject.xmlList.append("<para l=\"" + str(currentObject.apoctl["posx"]) + "\" t=\"" + str(currentObject.apoctl["posy"]))
                if currentObject.apoctl["absw"] == "" or abs(int(currentObject.apoctl["absw"])) == 0:
                    if re.search(r"\\line", tmpStr) != None:
                        lineSize = tmpStr.index("\\line")
                        lineSize = int(float(currentObject.parfmt["fs"])*float(lineSize)*10.0*(25.0/48.0))
                        if not currentObject.parfmt["li"]:
                            lineSize = int(currentObject.defLi) + lineSize
                            if not currentObject.parfmt["ri"]:
                                lineSize = int(currentObject.defRi) + lineSize
                            else:
                                lineSize = int(currentObject.parfmt["ri"]) + lineSize
                        else:
                            lineSize = int(currentObject.parfmt["li"]) + lineSize
                            if not currentObject.parfmt["ri"]:
                                lineSize = int(currentObject.defRi) + lineSize
                            else:
                                lineSize = int(currentObject.parfmt["ri"]) + lineSize
                        #print lineSize
                        #sys.exit(0)
                    else:
                        lineSize = len(tmpStr)
                        lineSize = int(float(currentObject.parfmt["fs"])*float(lineSize)*10.0*(25.0/48.0))
                        if not currentObject.parfmt["li"]:
                            lineSize = int(currentObject.defLi) + lineSize
                            if not currentObject.parfmt["ri"]:
                                lineSize = int(currentObject.defRi) + lineSize
                            else:
                                lineSize = int(currentObject.parfmt["ri"]) + lineSize
                        else:
                            lineSize = int(currentObject.parfmt["li"]) + lineSize
                            if not currentObject.parfmt["ri"]:
                                lineSize = int(currentObject.defRi) + lineSize
                            else:
                                lineSize = int(currentObject.parfmt["ri"]) + lineSize
                        #print tmpStr
                        #print str(int(currentObject.apoctl["posx"]) + lineSize)
                        #sys.exit(0)
                    xml += "\" r=\"" + str(int(currentObject.apoctl["posx"]) + lineSize)
                    currentObject.xmlList.append("\" r=\"" + str(int(currentObject.apoctl["posx"]) + lineSize))
                else:
                    xml += "\" r=\"" + str(int(currentObject.apoctl["posx"]) + abs(int(currentObject.apoctl["absw"])))
                    currentObject.xmlList.append("\" r=\"" + str(int(currentObject.apoctl["posx"]) + abs(int(currentObject.apoctl["absw"]))))
                
                if currentObject.apoctl["absh"] == "":
                    lineHeight = int(float(currentObject.parfmt["fs"])*10.0*(25.0/48.0))
                    xml += "\" b=\"" + str(int(currentObject.apoctl["posy"]) + lineHeight)
                    currentObject.xmlList.append("\" b=\"" + str(int(currentObject.apoctl["posy"]) + lineHeight))
                else:
                    xml += "\" b=\"" + str(int(currentObject.apoctl["posy"]) + abs(int(currentObject.apoctl["absh"])))
                    currentObject.xmlList.append("\" b=\"" + str(int(currentObject.apoctl["posy"]) + abs(int(currentObject.apoctl["absh"]))))
                
                if not currentObject.parfmt["li"]:
                    li = currentObject.defLi
                    xml += "\" li=\"" + currentObject.defLi
                    currentObject.xmlList.append("\" li=\"" + currentObject.defLi)
                else:
                    li = currentObject.parfmt["li"]
                    xml += "\" li=\"" + currentObject.parfmt["li"]
                    currentObject.xmlList.append("\" li=\"" + currentObject.parfmt["li"])
                if not currentObject.parfmt["sa"]:
                    xml += "\" sa=\"" + currentObject.defSa
                    currentObject.xmlList.append("\" sa=\"" + currentObject.defSa)
                else:
                    xml += "\" sa=\"" + currentObject.parfmt["sa"]
                    currentObject.xmlList.append("\" sa=\"" + currentObject.parfmt["sa"])
                if currentObject.parfmt["qc"] == "1":
                    xml += "\" alignment=\"" + "centered"
                    currentObject.xmlList.append("\" alignment=\"" + "centered")
                elif currentObject.parfmt["qj"] == "1":
                    xml += "\" alignment=\"" + "justified"
                    currentObject.xmlList.append("\" alignment=\"" + "justified")
                elif currentObject.parfmt["ql"] == "1":
                    xml += "\" alignment=\"" + "left"
                    currentObject.xmlList.append("\" alignment=\"" + "left")
                else:
                    xml += "\" alignment=\"" + "left"
                    currentObject.xmlList.append("\" alignment=\"" + "left")
                if currentObject.parfmt["slmult"] == "1":
                    xml += "\" lsp=\"single"
                    currentObject.xmlList.append("\" lsp=\"single")
                else:
                    xml += "\" lsp=\"exactly"
                    currentObject.xmlList.append("\" lsp=\"exactly")
                    if not currentObject.parfmt["sl"] or currentObject.parfmt["sl"] == "0":
                        xml += "\" lspExact=\"" + str(int(currentObject.parfmt["fs"])*10)
                        currentObject.xmlList.append("\" lspExact=\"" + str(int(currentObject.parfmt["fs"])*10))
                    else:
                        xml += "\" lspExact=\"" + str(abs(int(currentObject.parfmt["sl"])))
                        currentObject.xmlList.append("\" lspExact=\"" + str(abs(int(currentObject.parfmt["sl"]))))
                if currentObject.parfmt["lang"] == "1033":
                    xml += "\" language=\"en"
                    currentObject.xmlList.append("\" language=\"en")
                else:
                    xml += "\" language=\"unknown"
                    currentObject.xmlList.append("\" language=\"unknown")
                xml += "\" styleRef=\"" + currentObject.chrfmt["cs"] + "\">\n"
                currentObject.xmlList.append("\" styleRef=\"" + currentObject.chrfmt["cs"] + "\">\n")
                self.par = True
                #line
                #xml += "<ln l=\"" + str(int(currentObject.apoctl["posx"]) + int(li)) + "\" t=\"" + str(currentObject.apoctl["posy"])
                #xml += "\" r=\"" + str(int(currentObject.apoctl["posx"]) + abs(int(currentObject.apoctl["absw"])))
                #xml += "\" b=\"" + str(int(currentObject.apoctl["posy"]) + abs(int(currentObject.apoctl["absh"])))
                #xml += "\" baseLine=\"" + str(int(currentObject.apoctl["posy"]) + abs(int(currentObject.apoctl["absh"])) - 51)
                #xml += "\" forcedEOF=\"true\">\n"
                currentObject.init = False
                #print xml
                #sys.exit(0)
            #print readedData
            #richTextDic["data"] = currentObject.keywords
            #richTextDic["text"] = re.search(r"[^\\]*", readedData).group(0)
            #currentObject.richText.append(richTextDic)
            #if not currentObject.line:
                
            #zpracovani metadat
            #nacteni plain textu
            #pokud je v plain textu novy radek
            while re.search(r"\\line", tmpStr) != None:
                #ziskani textu pred novym radkem
                #tmpLine = re.search(r"[^(\\line)]*", tmpStr).group(0)
                tmpStr = re.sub(r"\x0D\x0A", "", tmpStr)
                index = tmpStr.index("\\line")
                if index == 0 and len(tmpStr):
                    first = True
                    cs = 0
                    run = False
                    for item in currentObject.line:
                        if first:
                            cs = item["style"]
                            first = False
                        else:
                            if item["style"] != cs:
                                run = True
                                break
                    xml += self.InterpretRichText(currentObject, run)
                    break
                tmpLine = tmpStr[0:index]
                tmpLine = re.sub(r"^\s+", "", tmpLine)
                tmpStr = tmpStr[(index+5):]
                #print tmpStr
                #print tmpLine
                #sys.exit(0)
                #tmpSpaces = re.subn(r"\s+", "", tmpLine)
                #numSpaces = tmpSpaces[1]
                tmpWords = tmpLine
                #vytazeni jedlotlivych slov z radku
                if not currentObject.parfmt["li"]:
                    li = currentObject.defLi
                else:
                    li = currentObject.parfmt["li"]
                if currentObject.line == []:
                    wordPosition = int(currentObject.apoctl["posx"]) + int(li)
                else:
                    wordPosition = currentObject.wordPos
                #nyni je nutne vypocitat prumernou delku jednoho znaku [Twips/znak]
                lineLen = len(tmpWords)
                if abs(int(currentObject.apoctl["absw"])) == 0:
                    lineWidth = int(float(currentObject.parfmt["fs"])*float(spaceLen)*10.0*(25.0/48.0))
                else:
                    lineWidth = int(currentObject.apoctl["posx"]) + abs(int(currentObject.apoctl["absw"]))
                #charLen = int(lineWidth/lineLen)
                #print wordPosition
                #print tmpWords
                #print lineLen
                #print lineWidth
                #print charLen
                #sys.exit(0)
                while tmpWords:
                    lineWord = {}
                    if re.search(r"\s+", tmpWords) != None:
                        tmpWord = re.search(r"^[^\s]*", tmpWords).group(0)
                        tmpWords = re.sub(r"^[^\s]*", "", tmpWords, 1)
                        spaceLen = len(re.search(r"^\s+", tmpWords).group(0))
                        tmpWords = re.sub(r"^\s+", "", tmpWords, 1)
                        spaceSeek = int(float(currentObject.parfmt["fs"])*float(spaceLen)*10.0*(25.0/48.0))
                    else:
                        tmpWord = tmpWords
                        tmpWords = ""
                        spaceSeek = 0
                    wordLen = len(tmpWord)
                    #velikost slova je ziskana takto:
                    #velikost fontu(half-pointy) * delka slova * koeficient na prevedeni na twipsy * korekcni koeficient
                    #print int(currentObject.parfmt["fs"])
                    wordSize = int(float(currentObject.parfmt["fs"])*float(wordLen)*10.0*(25.0/48.0))
                    lineWord["text"] = tmpWord
                    #print tmpWord
                    lineWord["position"] = wordPosition
                    lineWord["l"] = wordPosition
                    lineWord["t"] = str(currentObject.apoctl["posy"])
                    lineWord["r"] = wordPosition + wordSize
                    lineWord["b"] = str(int(currentObject.apoctl["posy"]) + int(float(currentObject.parfmt["fs"])*10.0*(24.0/48.0))*(currentObject.linePos+1))
                    #print tmpWord
                    #print lineWord
                    #print str(int(currentObject.apoctl["posy"]))
                    #print str(int(float(currentObject.parfmt["fs"])*10.0*(24.0/48.0))*(currentObject.linePos+1))
                    #print "LinePos: " + str(currentObject.linePos)
                    #print "---------------------------------------------------------------"
                    lineWord["style"] = currentObject.chrfmt["cs"]
                    currentObject.line.append(lineWord)
                    wordPosition += wordSize + spaceSeek
                    currentObject.wordPos = wordPosition
                    #print tmpWord
                    #print wordLen
                    #print wordSize
                    #print spaceSeek
                    #print wordPosition
                #print currentObject.line
                #interpretace bohateho textu
                first = True
                cs = 0
                run = False
                for item in currentObject.line:
                    if first:
                        cs = item["style"]
                        first = False
                    else:
                        if item["style"] != cs:
                            run = True
                            break
                xml += self.InterpretRichText(currentObject, run)
                currentObject.linePos += 1
            lineWord = {}
            tmpWords = tmpStr
            #vytazeni jedlotlivych slov z radku
            if not currentObject.parfmt["li"]:
                li = currentObject.defLi
            else:
                li = currentObject.parfmt["li"]
            if currentObject.line == []:
                wordPosition = int(currentObject.apoctl["posx"]) + int(li)
            else:
                wordPosition = currentObject.wordPos
            #wordPosition = int(currentObject.apoctl["posx"]) + int(li)
            #nyni je nutne vypocitat prumernou delku jednoho znaku [Twips/znak]
            lineLen = len(tmpWords)
            if currentObject.apoctl["absw"] == "" or abs(int(currentObject.apoctl["absw"])) == 0:
                lineWidth = int(float(currentObject.parfmt["fs"])*1.0*10.0*(25.0/48.0))
            else:
                lineWidth = int(currentObject.apoctl["posx"]) + abs(int(currentObject.apoctl["absw"]))
            #charLen = int(lineWidth/lineLen)
            #print wordPosition
            #print tmpWords
            #print lineLen
            #print lineWidth
            #print charLen
            #sys.exit(0)
            while tmpWords:
                lineWord = {}
                if re.search(r"\s+", tmpWords) != None:
                    tmpWord = re.search(r"^[^\s]*", tmpWords).group(0)
                    tmpWords = re.sub(r"^[^\s]*", "", tmpWords, 1)
                    spaceLen = len(re.search(r"^\s+", tmpWords).group(0))
                    tmpWords = re.sub(r"^\s+", "", tmpWords, 1)
                    spaceSeek = int(float(currentObject.parfmt["fs"])*float(spaceLen)*10.0*(25.0/48.0))
                else:
                    tmpWord = tmpWords
                    tmpWords = ""
                    spaceSeek = 0
                wordLen = len(tmpWord)
                #velikost slova je ziskana takto:
                #velikost fontu(half-pointy) * delka slova * koeficient na prevedeni na twipsy * korekcni koeficient
                #print int(currentObject.parfmt["fs"])
                wordSize = int(float(currentObject.parfmt["fs"])*float(wordLen)*10.0*(25.0/48.0))
                lineWord["text"] = tmpWord
                lineWord["position"] = wordPosition
                lineWord["l"] = wordPosition
                lineWord["t"] = str(currentObject.apoctl["posy"])
                lineWord["r"] = wordPosition + wordSize
                lineWord["b"] = str(int(currentObject.apoctl["posy"]) + int(float(currentObject.parfmt["fs"])*10.0*(24.0/48.0))*(currentObject.linePos+1))
                lineWord["style"] = currentObject.chrfmt["cs"]
                currentObject.line.append(lineWord)
                wordPosition += wordSize + spaceSeek
                currentObject.wordPos = wordPosition
                #print tmpWord
                #print wordLen
                #print wordSize
                #print spaceSeek
                #print wordPosition
            #print tmpWords
            #sys.exit(0)
            readedData = re.sub(r"^[^\}]*\}(\x0D\x0A)?", "", readedData, 1)
        #print currentObject.plainText
        #print readedData
        #sys.exit(0)
        retArray.append(readedData)
        retArray.append(xml)
        return retArray
    
    def InterpretRichText(self, currentObject, run):
        xml = ""
        #print currentObject.line
        #v radku se nachazi vice nez jeden styl textu
        if run:
            xml += "<ln "
            currentObject.xmlList.append("<ln ")
            xml += "l=\"" + str(currentObject.line[0]["l"]) + "\" "
            currentObject.xmlList.append("l=\"" + str(currentObject.line[0]["l"]) + "\" ")
            xml += "t=\"" + str(currentObject.line[0]["t"]) + "\" "
            currentObject.xmlList.append("t=\"" + str(currentObject.line[0]["t"]) + "\" ")
            xml += "r=\"" + str(currentObject.line[-1]["r"]) + "\" "
            currentObject.xmlList.append("r=\"" + str(currentObject.line[-1]["r"]) + "\" ")
            xml += "b=\"" + str(currentObject.line[0]["b"]) + "\" "
            currentObject.xmlList.append("b=\"" + str(currentObject.line[0]["b"]) + "\" ")
            xml += "baseLine=\"" + str(int(currentObject.line[0]["b"]) - 51) + "\">\n"
            currentObject.xmlList.append("baseLine=\"" + str(int(currentObject.line[0]["b"]) - 51) + "\">\n")
            cs = currentObject.line[0]["style"]
            styleDic = currentObject.styleSheetTable[0]
            for item in currentObject.styleSheetTable:
                if item.has_key("cs") and str(item["cs"]) == str(currentObject.line[0]["style"]):
                    styleDic = item
                    break
            xml += "<run "
            currentObject.xmlList.append("<run ")
            if styleDic["ul"] == "0":
                xml += "underlined=\"none\" "
                currentObject.xmlList.append("underlined=\"none\" ")
            else:
                xml += "underlined=\"yes\" "
                currentObject.xmlList.append("underlined=\"yes\" ")
            xml += "subsuperscript=\"none\" "
            currentObject.xmlList.append("subsuperscript=\"none\" ")
            fontStyle = {}
            if not styleDic.has_key("f"):
                for item in currentObject.fontInfo:
                    if str(currentObject.styleSheetTable[0]["f"]) == str(item["id"]):
                        fontStyle = item
                        break
            else:
                for item in currentObject.fontInfo:
                    try:
                        if str(styleDic["f"]) == str(item["id"]):
                            fontStyle = item
                            #print fontStyle
                            #sys.exit(0)
                            break
                    except KeyError:
                        print styleDic
                        sys.exit(1)
            if not styleDic.has_key("fs"):
                xml += "fontSize=\"" + str(int(float(int(currentObject.styleSheetTable[0]["fs"]))*50)) + "\" "
                currentObject.xmlList.append("fontSize=\"" + str(int(float(int(currentObject.styleSheetTable[0]["fs"]))*50)) + "\" ")
            else:
                xml += "fontSize=\"" + str(int(float(int(styleDic["fs"]))*50)) + "\" "
                currentObject.xmlList.append("fontSize=\"" + str(int(float(int(styleDic["fs"]))*50)) + "\" ")
            xml += "fontFace=\"" + fontStyle["fontName"] + "\" "
            currentObject.xmlList.append("fontFace=\"" + fontStyle["fontName"] + "\" ")
            xml += "fontFamily=\"" + fontStyle["fontFamily"] + "\" "
            currentObject.xmlList.append("fontFamily=\"" + fontStyle["fontFamily"] + "\" ")
            xml += "fontPitch=\"variable\" "
            currentObject.xmlList.append("fontPitch=\"variable\" ")
            xml += "spacing=\"10\">\n"
            currentObject.xmlList.append("spacing=\"10\">\n")
            for item in currentObject.line:
                if item["style"] == cs:
                    xml += "<wd "
                    currentObject.xmlList.append("<wd ")
                    xml += "l=\"" + str(item["l"]) + "\" "
                    currentObject.xmlList.append("l=\"" + str(item["l"]) + "\" ")
                    xml += "t=\"" + str(item["t"]) + "\" "
                    currentObject.xmlList.append("t=\"" + str(item["t"]) + "\" ")
                    xml += "r=\"" + str(item["r"]) + "\" "
                    currentObject.xmlList.append("r=\"" + str(item["r"]) + "\" ")
                    xml += "b=\"" + str(item["b"]) + "\">"
                    currentObject.xmlList.append("b=\"" + str(item["b"]) + "\">")
                    #\tab?
                    while re.search(r"\\\'((\d{2})|([A-Z]{2})|([A-Z]\d)|(\d[A-Z]))",  item["text"]) != None:
                        charHexed = re.search(r"\\\'((\d{2})|([A-Z]{2})|([A-Z]\d)|(\d[A-Z]))",  item["text"]).group(1)
                        item["text"] = re.sub(r"\\\'((\d{2})|([A-Z]{2})|([A-Z]\d)|(\d[A-Z]))", currentObject.hexTable[charHexed], item["text"])
                        sys.stderr.write("Nahrazuji za: " + currentObject.hexTable[charHexed] + "\n")
                    #item["text"] = re.sub(r"\\\'((\d{2})|([A-Z]{2})|([A-Z]\d)|(\d[A-Z]))", "", item["text"])
                    tab = False
                    if re.search(r"\\tab", item["text"]) != None:
                        item["text"] = re.sub(r"\\tab", "", item["text"])
                        tab = True
                    xml += item["text"]
                    currentObject.xmlList.append(item["text"])
                    if str(item["r"]) == str(currentObject.line[-1]["r"]):
                        xml += "</wd>\n"
                        currentObject.xmlList.append("</wd>\n")
                        if tab:
                            xml += "<tab/>\n"
                            currentObject.xmlList.append("<tab/>\n")
                    else:
                        if tab:
                            xml += "</wd>\n<tab/>\n"
                            currentObject.xmlList.append("</wd>\n<tab/>\n")
                        else:
                            xml += "</wd>\n<space/>\n"
                            currentObject.xmlList.append("</wd>\n<space/>\n")
                else:
                    cs = item["style"]
                    xml += "</run>\n"
                    currentObject.xmlList.append("</run>\n")
                    styleDic = currentObject.styleSheetTable[0]
                    for itemStyle in currentObject.styleSheetTable:
                        if itemStyle.has_key("cs") and str(itemStyle["cs"]) == str(cs):
                            styleDic = itemStyle
                            break
                    xml += "<run "
                    currentObject.xmlList.append("<run ")
                    if styleDic["ul"] == "0":
                        xml += "underlined=\"none\" "
                        currentObject.xmlList.append("underlined=\"none\" ")
                    else:
                        xml += "underlined=\"yes\" "
                        currentObject.xmlList.append("underlined=\"yes\" ")
                    xml += "subsuperscript=\"none\" "
                    currentObject.xmlList.append("subsuperscript=\"none\" ")
                    fontStyle = {}
                    if not styleDic.has_key("f"):
                        for itemFont in currentObject.fontInfo:
                            if str(currentObject.styleSheetTable[0]["f"]) == str(itemFont["id"]):
                                fontStyle = itemFont
                                break
                    else:
                        for itemFont in currentObject.fontInfo:
                            if str(styleDic["f"]) == str(itemFont["id"]):
                                fontStyle = itemFont
                                #print fontStyle
                                #sys.exit(0)
                                break
                    if not styleDic.has_key("fs"):
                        xml += "fontSize=\"" + str(int(float(int(currentObject.styleSheetTable[0]["fs"]))*50)) + "\" "
                        currentObject.xmlList.append("fontSize=\"" + str(int(float(int(currentObject.styleSheetTable[0]["fs"]))*50)) + "\" ")
                    else:
                        xml += "fontSize=\"" + str(int(float(int(styleDic["fs"]))*50)) + "\" "
                        currentObject.xmlList.append("fontSize=\"" + str(int(float(int(styleDic["fs"]))*50)) + "\" ")
                    xml += "fontFace=\"" + fontStyle["fontName"] + "\" "
                    currentObject.xmlList.append("fontFace=\"" + fontStyle["fontName"] + "\" ")
                    xml += "fontFamily=\"" + fontStyle["fontFamily"] + "\" "
                    currentObject.xmlList.append("fontFamily=\"" + fontStyle["fontFamily"] + "\" ")
                    xml += "fontPitch=\"variable\" "
                    currentObject.xmlList.append("fontPitch=\"variable\" ")
                    xml += "spacing=\"10\">\n"
                    currentObject.xmlList.append("spacing=\"10\">\n")
                    xml += "<wd "
                    currentObject.xmlList.append("<wd ")
                    xml += "l=\"" + str(item["l"]) + "\" "
                    currentObject.xmlList.append("l=\"" + str(item["l"]) + "\" ")
                    xml += "t=\"" + str(item["t"]) + "\" "
                    currentObject.xmlList.append("t=\"" + str(item["t"]) + "\" ")
                    xml += "r=\"" + str(item["r"]) + "\" "
                    currentObject.xmlList.append("r=\"" + str(item["r"]) + "\" ")
                    xml += "b=\"" + str(item["b"]) + "\">"
                    currentObject.xmlList.append("b=\"" + str(item["b"]) + "\">")
                    #\tab?
#item["text"] = re.sub(r"\\\'((\d{2})|([A-Z]{2})|([A-Z]\d)|(\d[A-Z]))", "", item["text"])
                    while re.search(r"\\\'((\d{2})|([A-Z]{2})|([A-Z]\d)|(\d[A-Z]))",  item["text"]) != None:
                        charHexed = re.search(r"\\\'((\d{2})|([A-Z]{2})|([A-Z]\d)|(\d[A-Z]))",  item["text"]).group(1)
                        item["text"] = re.sub(r"\\\'((\d{2})|([A-Z]{2})|([A-Z]\d)|(\d[A-Z]))", currentObject.hexTable[charHexed], item["text"])
                        sys.stderr.write("Nahrazuji za: " + currentObject.hexTable[charHexed] + "\n")
                    tab = False
                    if re.search(r"\\tab", item["text"]) != None:
                        item["text"] = re.sub(r"\\tab", "", item["text"])
                        tab = True
                    xml += item["text"]
                    currentObject.xmlList.append(item["text"])
                    if str(item["r"]) == str(currentObject.line[-1]["r"]):
                        xml += "</wd>\n"
                        currentObject.xmlList.append("</wd>\n")
                        if tab:
                            xml += "<tab/>\n"
                            currentObject.xmlList.append("<tab/>\n")
                    else:
                        if tab:
                            xml += "</wd>\n<tab/>\n"
                            currentObject.xmlList.append("</wd>\n<tab/>\n")
                        else:
                            xml += "</wd>\n<space/>\n"
                            currentObject.xmlList.append("</wd>\n<space/>\n")
            xml += "</run>\n</ln>\n"
            currentObject.xmlList.append("</run>\n</ln>\n")
            #ZDE OBNOVIT!!!!
            #print xml
        #v radku se nachazi jen jeden styl textu
        else:
            styleDic = {}
            for item in currentObject.styleSheetTable:
                if item.has_key("cs") and str(item["cs"]) == str(currentObject.line[0]["style"]):
                    styleDic = item
                    break
                    #print styleDic
                    #sys.exit(0)
            xml += "<ln "
            currentObject.xmlList.append("<ln ")
            xml += "l=\"" + str(currentObject.line[0]["l"]) + "\" "
            currentObject.xmlList.append("l=\"" + str(currentObject.line[0]["l"]) + "\" ")
            xml += "t=\"" + str(currentObject.line[0]["t"]) + "\" "
            currentObject.xmlList.append("t=\"" + str(currentObject.line[0]["t"]) + "\" ")
            xml += "r=\"" + str(currentObject.line[-1]["r"]) + "\" "
            currentObject.xmlList.append("r=\"" + str(currentObject.line[-1]["r"]) + "\" ")
            xml += "b=\"" + str(currentObject.line[0]["b"]) + "\" "
            currentObject.xmlList.append("b=\"" + str(currentObject.line[0]["b"]) + "\" ")
            xml += "baseLine=\"" + str(int(currentObject.line[0]["b"]) - 51) + "\" "
            currentObject.xmlList.append("baseLine=\"" + str(int(currentObject.line[0]["b"]) - 51) + "\" ")
            if styleDic["ul"] == "0":
                xml += "underlined=\"none\" "
                currentObject.xmlList.append("underlined=\"none\" ")
            else:
                xml += "underlined=\"yes\" "
                currentObject.xmlList.append("underlined=\"yes\" ")
            xml += "subsuperscript=\"none\" "
            currentObject.xmlList.append("subsuperscript=\"none\" ")
            fontStyle = {}
            if not styleDic.has_key("f"):
                styleDic["f"] = currentObject.defFont
            for item in currentObject.fontInfo:
                try:
                    if str(styleDic["f"]) == str(item["id"]):
                        fontStyle = item
                        #print fontStyle
                        #sys.exit(0)
                        break
                except KeyError:
                    print styleDic
                    sys.exit(1)
            
            if styleDic.has_key("fs"):
                xml += "fontSize=\"" + str(int(float(int(styleDic["fs"]))*50)) + "\" "
                currentObject.xmlList.append("fontSize=\"" + str(int(float(int(styleDic["fs"]))*50)) + "\" ")
            else:
                xml += "fontSize=\"" + str(int(float(int(currentObject.defFs))*50)) + "\" "
                currentObject.xmlList.append("fontSize=\"" + str(int(float(int(currentObject.defFs))*50)) + "\" ")
            
            xml += "fontFace=\"" + fontStyle["fontName"] + "\" "
            currentObject.xmlList.append("fontFace=\"" + fontStyle["fontName"] + "\" ")
            xml += "fontFamily=\"" + fontStyle["fontFamily"] + "\" "
            currentObject.xmlList.append("fontFamily=\"" + fontStyle["fontFamily"] + "\" ")
            xml += "fontPitch=\"variable\" "
            currentObject.xmlList.append("fontPitch=\"variable\" ")
            xml += "spacing=\"10\">\n"
            currentObject.xmlList.append("spacing=\"10\">\n")
            for item in currentObject.line:
                xml += "<wd "
                currentObject.xmlList.append("<wd ")
                xml += "l=\"" + str(item["l"]) + "\" "
                currentObject.xmlList.append("l=\"" + str(item["l"]) + "\" ")
                xml += "t=\"" + str(item["t"]) + "\" "
                currentObject.xmlList.append("t=\"" + str(item["t"]) + "\" ")
                xml += "r=\"" + str(item["r"]) + "\" "
                currentObject.xmlList.append("r=\"" + str(item["r"]) + "\" ")
                xml += "b=\"" + str(item["b"]) + "\">"
                currentObject.xmlList.append("b=\"" + str(item["b"]) + "\">")
                #\tab?
                #item["text"] = re.sub(r"\\\'((\d{2})|([A-Z]{2})|([A-Z]\d)|(\d[A-Z]))", "", item["text"])
                while re.search(r"\\\'((\d{2})|([A-Z]{2})|([A-Z]\d)|(\d[A-Z]))",  item["text"]) != None:
                        charHexed = re.search(r"\\\'((\d{2})|([A-Z]{2})|([A-Z]\d)|(\d[A-Z]))",  item["text"]).group(1)
                        item["text"] = re.sub(r"\\\'((\d{2})|([A-Z]{2})|([A-Z]\d)|(\d[A-Z]))", currentObject.hexTable[charHexed], item["text"])
                        sys.stderr.write(("Nahrazuji za: " + currentObject.hexTable[charHexed] + "\n").encode("utf-8"))
                tab = False
                if re.search(r"\\tab", item["text"]) != None:
                    item["text"] = re.sub(r"\\tab", "", item["text"])
                    tab = True
                xml += item["text"]
                currentObject.xmlList.append(item["text"])
                if str(item["r"]) == str(currentObject.line[-1]["r"]):
                    xml += "</wd>\n"
                    currentObject.xmlList.append("</wd>\n")
                    if tab:
                        xml += "<tab/>\n"
                        currentObject.xmlList.append("<tab/>\n")
                else:
                    if tab:
                        xml += "</wd>\n<tab/>\n"
                        currentObject.xmlList.append("</wd>\n<tab/>\n")
                    else:
                        xml += "</wd>\n<space/>\n"
                        currentObject.xmlList.append("</wd>\n<space/>\n")
            xml += "</ln>\n"
            currentObject.xmlList.append("</ln>\n")
            #ZDE OBNOVIT!!!!!
            #print xml
        currentObject.line = []
        return xml
    
    #Metoda parsujici FootnoteSep v Body
    #@param1 objekt, do ktereho by se pripadne ukladaly informace
    #@param2 nacteny RTF soubor
    #@return1 nenaparsovana cast RTF souboru
    #@return2 cast xml vystupu
    def FootnoteSep(self, currentObject, readedData):
        retArray = []
        xml = ""
        #print readedData
        #sys.exit(0)
        readedData = re.sub(r"\{", "", readedData, 1)
        while True:
            if readedData[0] == "}":
                break
            if re.search(r"^\\aspalpha", readedData) != None:
                currentObject.ftnsepDic["aspalpha"] = 1
                readedData = re.sub(r"\\aspalpha", "", readedData, 1)
            if re.search(r"^\\aspnum", readedData) != None:
                currentObject.ftnsepDic["aspnum"] = 1
                readedData = re.sub(r"\\aspnum", "", readedData, 1)
            if re.search(r"^\\faauto", readedData) != None:
                currentObject.ftnsepDic["faauto"] = 1
                readedData = re.sub(r"\\faauto", "", readedData, 1)
            if re.search(r"^\\adjustright", readedData) != None:
                currentObject.ftnsepDic["adjustright"] = 1
                readedData = re.sub(r"\\adjustright", "", readedData, 1)
            if re.search(r"^\\cgrid", readedData) != None:
                currentObject.ftnsepDic["cgrid"] = 1
                readedData = re.sub(r"\\cgrid", "", readedData, 1)
            if re.search(r"^\\chftnsep", readedData) != None:
                currentObject.ftnsepDic["chftnsep"] = 1
                readedData = re.sub(r"\\chftnsep", "", readedData, 1)
            if re.search(r"^\\par", readedData) != None:
                currentObject.ftnsepDic["par"] = 1
                readedData = re.sub(r"\\par", "", readedData, 1)
        #readedData = re.sub(r"\}\s{1}?", "", readedData, 1)
        readedData = re.sub(r"^(\x0D\x0A)?\}(\x0D\x0A)?", "", readedData, 1)
        readedData = re.sub(r"^(\x0D\x0A)?\}(\x0D\x0A)?", "", readedData, 1)
        retArray.append(readedData)
        retArray.append(xml)
        return retArray
    
    #Metoda parsujici EndnoteSep v Body
    #@param1 objekt, do ktereho by se pripadne ukladaly informace
    #@param2 nacteny RTF soubor
    #@return1 nenaparsovana cast RTF souboru
    #@return2 cast xml vystupu
    def EndnoteSep(self, currentObject, readedData):
        retArray = []
        xml = ""
        
        readedData = re.sub(r"\{", "", readedData, 1)
        while True:
            if readedData[0] == "}":
                break
            if re.search(r"^\\aspalpha", readedData) != None:
                currentObject.ftnsepDic["aspalpha"] = 1
                readedData = re.sub(r"\\aspalpha", "", readedData, 1)
            if re.search(r"^\\aspnum", readedData) != None:
                currentObject.ftnsepDic["aspnum"] = 1
                readedData = re.sub(r"\\aspnum", "", readedData, 1)
            if re.search(r"^\\faauto", readedData) != None:
                currentObject.ftnsepDic["faauto"] = 1
                readedData = re.sub(r"\\faauto", "", readedData, 1)
            if re.search(r"^\\adjustright", readedData) != None:
                currentObject.ftnsepDic["adjustright"] = 1
                readedData = re.sub(r"\\adjustright", "", readedData, 1)
            if re.search(r"^\\cgrid", readedData) != None:
                currentObject.ftnsepDic["cgrid"] = 1
                readedData = re.sub(r"\\cgrid", "", readedData, 1)
            if re.search(r"^\\chftnsep", readedData) != None:
                currentObject.ftnsepDic["chftnsep"] = 1
                readedData = re.sub(r"\\chftnsep", "", readedData, 1)
            if re.search(r"^\\par", readedData) != None:
                currentObject.ftnsepDic["par"] = 1
                readedData = re.sub(r"\\par", "", readedData, 1)
        readedData = re.sub(r"^(\x0D\x0A)?\}(\x0D\x0A)?", "", readedData, 1)
        readedData = re.sub(r"^(\x0D\x0A)?\}(\x0D\x0A)?", "", readedData, 1)
        retArray.append(readedData)
        retArray.append(xml)
        return retArray
    
    #Metoda parsujici Keywords v Body
    #@param1 objekt, do ktereho by se pripadne ukladaly informace
    #@param2 nacteny RTF soubor
    #@return1 nenaparsovana cast RTF souboru
    #@return2 cast xml vystupu
    def Keywords(self, currentObject, readedData):
        retArray = []
        xml = ""
        global imp_mode
        global inputLSR
        
        #print readedData
        #sys.exit(0)
        #print "Keywords"
        if re.search(r"^\\field", readedData) != None:
            #sys.stderr.write("JJ\n")
            tmpArray = currentObject.Field(currentObject, readedData)
            readedData = tmpArray[0]
            xml += tmpArray[1]
            if re.search(r"^\{\\\*\\bkmkend", readedData) != None:
                retArray.append(readedData)
                retArray.append(xml)
                return retArray
            #print readedData
            #sys.exit(0)
            readedData = re.sub(r"^\{", "", readedData, 1)
        
        while True:
            #print readedData[0]+readedData[1]+readedData[2]
            #if re.search(r"^\\\*\\bkmkstart", readedData) != None:
            #    print readedData
            #    sys.exit(0)
            if readedData[0] != '\\' or readedData[1] == "*":
                #print "end keywords"
                #print readedData
                break
            try:
                keyword = re.search(r"^\\([a-zA-Z]+)", readedData).group(1)
            except AttributeError:
                print readedData
                sys.exit(0)
            if currentObject.apoctl.has_key(keyword):
                #print "apoctl"
                currentObject.SetApoCtl(currentObject, keyword, readedData)
                readedData = re.sub(r"^\\[a-zA-Z]+(\-)?(\d+)?(\x0D\x0A)?", "", readedData, 1)
            elif currentObject.brdrdef.has_key(keyword):
                #print "brdrdef"
                readedData = re.sub(r"^\\[a-zA-Z]+(\-)?(\d+)?(\x0D\x0A)?", "", readedData, 1)
            elif currentObject.chrfmt.has_key(keyword):
                #print "chrfmt"
                currentObject.SetChrFmt(currentObject, keyword, readedData)
                readedData = re.sub(r"^\\[a-zA-Z]+(\-)?(\d+)?(\x0D\x0A)?", "", readedData, 1) 
            elif currentObject.docfmt.has_key(keyword):
                #print "docfmt"
                currentObject.SetDocFmt(currentObject, keyword, readedData)
                readedData = re.sub(r"^\\[a-zA-Z]+(\-)?(\d+)?(\x0D\x0A)?", "", readedData, 1) 
            elif currentObject.parfmt.has_key(keyword):
                #print "parfmt"
                if keyword == "par":
                    plainText = {}
                    plainText["text"] = "\\line"
                    plainText["special"] = currentObject.special
                    currentObject.plainText.append(plainText)
                    currentObject.apoctl["absh"] = 0
                    currentObject.apoctl["absw"] = 0
                    #print currentObject.line
                    if currentObject.line:
                        first = True
                        cs = 0
                        run = False
                        for item in currentObject.line:
                            if first:
                                cs = item["style"]
                                first = False
                            else:
                                if item["style"] != cs:
                                    run = True
                                    break
                        xml += self.InterpretRichText(currentObject, run)
                    currentObject.line = []
                    currentObject.linePos = 0
                    xml += "</para>\n"
                    currentObject.xmlList.append("</para>\n")
                    currentObject.xmlParaList.append(currentObject.xmlList)
                    #ZDE OBNOVIT
                    #print currentObject.xmlParaList
                    currentObject.xmlList = []
                    currentObject.par = False
                currentObject.SetParFmt(currentObject, keyword, readedData)
                readedData = re.sub(r"^\\[a-zA-Z]+(\-)?(\d+)?(\x0D\x0A)?", "", readedData, 1) 
            elif currentObject.tabdef.has_key(keyword):
                #print "tabdef"
                readedData = re.sub(r"^\\[a-zA-Z]+(\-)?(\d+)?(\x0D\x0A)?", "", readedData, 1) 
            elif currentObject.shading.has_key(keyword):
                #print "shading"
                readedData = re.sub(r"^\\[a-zA-Z]+(\-)?(\d+)?(\x0D\x0A)?", "", readedData, 1)
            elif currentObject.secfmt.has_key(keyword):
                #print "secfmt"
                if keyword == "sect":
                    currentObject.MakeDocument(currentObject)
                    currentObject.xmlParaList = []
                    currentObject.xmlList = []
                readedData = re.sub(r"^\\[a-zA-Z]+(\-)?(\d+)?(\x0D\x0A)?", "", readedData, 1)
            elif currentObject.spec.has_key(keyword):
                #print "spec"
                if keyword == "tab":
                    plainText = {}
                    plainText["text"] = "\\tab"
                    plainText["special"] = currentObject.special
                readedData = re.sub(r"^\\[a-zA-Z]+(\-)?(\d+)?(\x0D\x0A)?", "", readedData, 1)
            #elif currentObject.tbldef.has_key(keyword):
            #    #print "tbldef"
            #    if keyword == "row":
            #        if re.search(r"^\\row\}", readedData) != None:
            #            plainText = {}
            #            plainText["text"] = "\\line"
            #            plainText["special"] = currentObject.special
            #            currentObject.plainText.append(plainText)
            #    readedData = re.sub(r"^\\[a-zA-Z]+(\-)?(\d+)?(\x0D\x0A)?", "", readedData, 1)
            elif re.search(r"^\\u\d+", readedData) != None:
                plainText = {}
                plainText["text"] = re.search(r"^[^\}]+", readedData).group(0)
                plainText["special"] = currentObject.special
                currentObject.plainText.append(plainText)
                readedData = re.sub(r"^[^\}]+\}(\x0D\x0A)?", "", readedData, 1)
                if imp_mode:
                    sys.stderr.write("1028: Pozor na unicode znak\n")
            else:
                if keyword == "cell" or keyword == "row":
                    retArray.append(readedData)
                    retArray.append(xml)
                    return retArray
                    
                sys.stderr.write("Soubor: " + inputLSR + "\n")
                sys.stderr.write(keyword + "\n")
                sys.stderr.write(readedData[:32]+"\n")
                print "nerozpoznan klic " + keyword
                print readedData
                sys.exit(0)
                
        retArray.append(readedData)
        retArray.append(xml)
        return retArray
    
    def MakeDocument(self, currentObject):
        l = 0
        t = 0
        r = 0
        b = 0
        sa = 0
        first = True
        paraDic = {}
        positionDicY = {}
        columnTable = []
        column = []
        
        #print currentObject.xmlParaList
        #sys.exit(0)
        #Nyni se v kazdem odstavci, ktery se prekryva s jinym
        #prepocitaji hodnoty
        indexDel = 0
        toDelArr = []
        for item in currentObject.xmlParaList:
            if len(item) <= 1:
                #toDel = int(indexDel)
                #sys.stderr.write(str(indexDel)+"\n")
                toDelArr.append(str(indexDel))
            indexDel += 1
        
        indexDel = 0
        for item in toDelArr:
            #sys.stderr.write(currentObject.xmlParaList[int(item) - indexDel][0] +"\n")
            del currentObject.xmlParaList[int(item) - indexDel]
            #sys.stderr.write("Mazu na indexu: "+str(int(item) - indexDel)+"\n")
            indexDel += 1
        
        #for item in currentObject.xmlParaList:
        #    print item
        
        #TODO: firstPara muze byt i tabulka
        firstPara = currentObject.xmlParaList[0]
        #print firstPara
        tmpLT = firstPara[0]
        try:
            l = re.search(r"\d+", tmpLT).group(0)
        except AttributeError:
            sys.stderr.write("RTFParser::MakeDocument() - L hodnota nenalezena!\n")
            print firstPara
            sys.exit(1)
        
        if re.search(r"^<table", firstPara[0]) != None:
            t = re.search(r"(\d+)\" $", tmpLT).group(1)
        else:
            t = re.search(r"\d+$", tmpLT).group(0)
        r = re.search(r"\d+", firstPara[1]).group(0)
        b = re.search(r"\d+", firstPara[2]).group(0)
        sa = re.search(r"\d+", firstPara[4]).group(0)
        
        #problem v RTF je, ze si neuklada pozici pro kazdy odstavec
        #a je tedy nutne si tyto udaje spocitat samostatne
        #zde se tedy vypocte opravdova spodni pozice odstavce
        #najde se posledni slovo, vezme se jeho b hodnota a pricte
        #se k ni hodnota \sa
        index = 0
        bPos = 0
        for item in firstPara:
            if re.search(r"^b=", item) != None:
                bPos = index
            index += 1
        tmpB = re.search(r"\d+", firstPara[bPos]).group(0)
        b = int(tmpB) + int(sa)
        #print b
        firstPara[2] = re.sub(r"\d+", str(b), firstPara[2])
        #sys.exit(0)
        #Jelikoz text v RTF muze byt uplne na jinych pozich, nez je
        #ve skutecnosti, je nutne jej srovnat na spravne misto, jinak
        #klasifikace nebude dobre fungovat.
        #Vytvoril jsem tedy slovnik, do ktereho budu nejdrive ukladat
        #pozici na ose Y. Pokud tedy nejaky odstavec bude mit stejnou
        #pozici, je nutne prepocitat jeho pozici. Nicmene se muze stat
        #ze dokument bude obsahovat vice sloupcu textu. Proto se pro
        #kazdou polozku slovniku osy Y uklada slovnik s osami X. Tim
        #se zamezi spatnemu oznaceni odstavcu, ktere sice lezi na stejne
        #poloze osy Y, ale uz ne na stejne poloze osy X.
        paraDic[str(t)] = {}
        paraDic[str(t)][str(l)] = {}
        paraDic[str(t)][str(l)]["l"] = l
        paraDic[str(t)][str(l)]["t"] = t
        paraDic[str(t)][str(l)]["r"] = r
        paraDic[str(t)][str(l)]["b"] = b
        paraDic[str(t)][str(l)]["sa"] = sa
        paraDic[str(t)][str(l)]["nl"] = ""
        paraDic[str(t)][str(l)]["nt"] = ""
        paraDic[str(t)][str(l)]["nr"] = ""
        paraDic[str(t)][str(l)]["nb"] = ""
        paraDic[str(t)][str(l)]["nsa"] = ""
        #print paraDic
        
        """
        #Nyni se v kazdem odstavci, ktery se prekryva s jinym
        #prepocitaji hodnoty
        indexDel = 0
        toDelArr = []
        for item in currentObject.xmlParaList:
            if len(item) <= 1:
                #toDel = int(indexDel)
                sys.stderr.write(str(indexDel)+"\n")
                toDelArr.append(str(indexDel))
            indexDel += 1
        
        indexDel = 0
        for item in toDelArr:
            sys.stderr.write(currentObject.xmlParaList[int(item) - indexDel][0] +"\n")
            del currentObject.xmlParaList[int(item) - indexDel]
            sys.stderr.write("Mazu na indexu: "+str(int(item) - indexDel)+"\n")
            indexDel += 1
        #if toDel >= 0:
            #sys.stderr.write("Mazu na indexu: "+str(toDel)+"\n")
        #    del currentObject.xmlParaList[toDel]
        """
        
        for item in currentObject.xmlParaList:
            if len(item) <= 1:
                continue
            if first:
                first = False
                continue
            #print item
            try:
                parl = re.search(r"\d+", item[0]).group(0)
                if re.search(r"^<table", item[0]) != None:
                    part = re.search(r"(\d+)\" ", item[0]).group(1)
                else:
                    part = re.search(r"\d+$", item[0]).group(0)
                parr = re.search(r"\d+", item[1]).group(0)
                parb = re.search(r"\d+", item[2]).group(0)
                if re.search(r"^<table", item[0]) != None:
                    parsa = re.search(r"\d+", item[7]).group(0)
                else:
                    parsa = re.search(r"\d+", item[4]).group(0)
            except AttributeError:
                sys.stderr.write("rtfParser :: MakeDocument() - AttributeError\n")
                sys.stderr.write("Vyjimka!!\n")
                print item
                sys.exit(0)
            index = 0
            bPos = 0
            #hodnota b je skoro v kazdem pripade spatna
            #proto je nutne ji nejdrive spocitat spravne
            for itemB in item:
                if re.search(r"^b=", itemB) != None:
                    bPos = index
                index += 1
            tmpB = re.search(r"\d+", item[bPos]).group(0)
            parb = int(tmpB) + int(parsa)
            #print l
            #print t
            #print r
            #if re.search(r"^<table", item[0]) != None:
            #    print parb
            #    sys.exit(0)
            if paraDic.has_key(part):
                if paraDic[part].has_key(parl):
                    if paraDic[part][parl]["nb"]:
                        newT = paraDic[part][parl]["nb"]
                        #print "TOHLE!!!!!"
                        #print newT
                        #sys.exit(0)
                    else:
                        #nalezli jsme odstavec, ktery prekryva jiny
                        #nutne prepocitat hodnoty
                        newT = paraDic[part][parl]["b"]
                    subNum = int(newT) - int(part)
                    newB = parb+subNum
                    #print newT
                    #print subNum
                    #nahrazeni pozice pocatku odstavce v ose Y za prepocitanou
                    if re.search(r"^<table", item[0]) != None:
                        item[0] = re.sub(r"(\d+)\" $", str(newT) + "\" ", item[0], 1)
                    else:
                        item[0] = re.sub(r"\d+$", str(newT), item[0], 1)
                    #nahrazeni pozice konce odstavce v ose Y za prepocitanou
                    item[2] = re.sub(r"\d+", str(newB), item[2], 1)
                    tmpItem = item
                    index = 0
                    #TODO: opravit tak, at nemuze nastat situace, ze by se spletl text s atributy
                    for itemPar in item:
                        if re.search(r"^t=\"\d+", itemPar) != None:
                            try:
                                tmpNum = re.search(r"\d+", itemPar).group(0)
                            except AttributeError:
                                sys.stderr.write("Vyjimka! rtfParser::MakeDocument - regexp error\n")
                                sys.stderr.write("         Vypis ve zvolenem souboru\n")
                                print itemPar
                                print item
                                sys.exit(0)
                                
                            tmpNum = int(tmpNum) + subNum
                            itemPar = re.sub(r"\d+", str(tmpNum), itemPar, 1)
                            tmpItem[index] = itemPar
                        elif re.search(r"^b=", itemPar) != None:
                            tmpNum = re.search(r"\d+", itemPar).group(0)
                            tmpNum = int(tmpNum) + subNum
                            itemPar = re.sub(r"\d+", str(tmpNum), itemPar, 1)
                            tmpItem[index] = itemPar
                        index += 1
                    #print tmpItem
                    item = tmpItem
                    #print item
                    #print "\n\n"
                    paraDic[str(newT)] = {}
                    paraDic[str(newT)][str(parl)] = {}
                    paraDic[str(newT)][str(parl)]["l"] = parl
                    paraDic[str(newT)][str(parl)]["t"] = newT
                    paraDic[str(newT)][str(parl)]["r"] = parr
                    paraDic[str(newT)][str(parl)]["b"] = newB
                    paraDic[str(part)][str(parl)]["nb"] = newB
                #else:
                #    print paraDic
                #    sys.exit(0)
            else:
                #if re.search(r"^<table", item[0]) != None:
                #    print "Tabulka chycena"
                #    sys.exit(0)
                item[2] = re.sub(r"\d+", str(parb), item[2], 1)
                paraDic[str(part)] = {}
                paraDic[str(part)][str(parl)] = {}
                paraDic[str(part)][str(parl)]["l"] = parl
                paraDic[str(part)][str(parl)]["t"] = part
                paraDic[str(part)][str(parl)]["r"] = parr
                paraDic[str(part)][str(parl)]["b"] = parb
                paraDic[str(part)][str(parl)]["sa"] = sa
                paraDic[str(part)][str(parl)]["nl"] = ""
                paraDic[str(part)][str(parl)]["nt"] = ""
                paraDic[str(part)][str(parl)]["nr"] = ""
                paraDic[str(part)][str(parl)]["nb"] = ""
                paraDic[str(part)][str(parl)]["nsa"] = ""
                #print item
        onePar = []
        twoPar = []
        othersPar = []
        for item in currentObject.xmlParaList:
            try:
                parL = re.search(r"\d+", item[0]).group(0)
            except AttributeError:
                sys.stderr.write("Vyjimka!!!\n")
                print "VYJIMKA"
                print item[0]
                sys.exit(0)
            parB = re.search(r"\d+", item[1]).group(0)
            try:
                if int(float(currentObject.docfmt["paperw"])/float(int(parB)-int(parL))) == 1:
                    onePar.append(item)
                elif int(float(currentObject.docfmt["paperw"])/float(int(parB)-int(parL))) == 2:
                    twoPar.append(item)
                else:
                    #TODO: tohle je jen docasne reseni a neni zarucene, ze bude fungovat
                    #            az bude chvile, tak opravit
                    #othersPar.append(item)
                    twoPar.append(item)
            except ZeroDivisionError:
                print item
                sys.exit(0)
        
        #for item in twoPar:
        #    print item
        
        #muze nastat situace, kdy se vytvori odstavec, ale
        #neni v nem nic
        #noWd = True
        #for item in othersPar:
        #    if re.search(r"^<wd", itemWord) != None:
        #        noWd = False 
        #        break
        
        #pokud se neco ocitlo v Others, tak se provadi
        #kontrola, zda se nejedno o rozdeleny odstavec
        #toto nastava v pripadech, kdy se na radku nachazi
        #vzorec ci stranka s copyrightem
        #pokud je zde takovy pripad nalezel, pak se provede
        #spojeni techto rozdelenych odstavcu
        indexOthers = 0
        indexOthers2 = 0
        othersParSecondChance = []
        found = False
        while True:
            found = False
            indexOthers = 0
            indexOthers2 = 0
            for itemOthers in othersPar:
                indexOthers2 = 0
                for itemOthers2 in othersPar:
                    if indexOthers == indexOthers2:
                        indexOthers2 += 1
                        continue
                    elif re.search(r"^<table", itemOthers[0]) != None or re.search(r"^<table", itemOthers2[0]) != None:
                        indexOthers2 += 1
                        continue
                    
                    #TODO: tohle optimalizovat, zbytecne se pocita pro kazdy cyklus
                    noWd = True
                    for itemWord in itemOthers:
                        if re.search(r"^<wd", itemWord) != None:
                            noWd = False
                            break
                    if noWd:
                        continue
                    
                    noWd = True
                    for itemWord in itemOthers2:
                        if re.search(r"^<wd", itemWord) != None:
                            noWd = False
                            break
                    if noWd:
                        continue
                    
                    #if re.search(r"^<table", item[0]) != None:
                    try:
                        if re.search(r"^<table", itemOthers[0]) != None:
                            top1 = int(re.search(r"(\d+)\" $", itemOthers[0]).group(1))
                        else:
                            top1 = int(re.search(r"\d+$", itemOthers[0]).group(0))
                            
                        if re.search(r"^<table", itemOthers2[0]) != None:
                            top2 = int(re.search(r"(\d+)\" $", itemOthers2[0]).group(1))
                        else:
                            top2 = int(re.search(r"\d+$", itemOthers2[0]).group(0))
                    except AttributeError:
                        print "itemOthers"
                        print itemOthers
                        print "itemOthers2"
                        print itemOthers2
                        sys.exit(0)
                    indexWord = 0
                    for itemWord in itemOthers:
                        if re.search(r"^<wd", itemWord) != None:
                            break
                        indexWord += 1
                    try:
                        wordT = int(re.search(r"\d+", itemOthers[indexWord+2]).group(0))
                    except IndexError:
                        sys.stderr.write("Vyjimka! rtfParser::MakeDocument() - IndexError\n")
                        sys.stderr.write("         Vypis ve zvolenem souboru\n")
                        print indexWord
                        print itemOthers
                        sys.exit(1)
                    wordB = int(re.search(r"\d+", itemOthers[indexWord+4]).group(0))
                    tol = wordB - wordT - 5
                    #print itemOthers
                    #print wordT
                    #print wordB
                    #print tol
                    #print top1
                    #print top2
                    if abs(top1-top2) < tol:
                        found = True
                        #print itemOthers
                        #print itemOthers2
                        if top1 < top2:
                            bottom2 = int(re.search(r"\d+", itemOthers2[2]).group(0))
                            left1 = int(re.search(r"\d+", itemOthers[0]).group(0))
                            left2 = int(re.search(r"\d+", itemOthers2[0]).group(0))
                            right1 = int(re.search(r"\d+", itemOthers[1]).group(0))
                            right2 = int(re.search(r"\d+", itemOthers2[1]).group(0))
                            
                            if left1 < left2:
                                #print currentObject.docfmt["paperw"]
                                #print itemOthers
                                #sys.exit(0)
                                if int(right2) < int(currentObject.docfmt["paperw"]):
                                    #print re.search(r"\d+", itemOthers[1]).group(0)
                                    itemOthers[1] = re.sub(r"\d+", str(right2), itemOthers[1], 1)
                                    #print right2
                                    #print "--------"
                                else:
                                    itemOthers[1] = re.sub(r"\d+", str(right1 + (right2-left2)), itemOthers[1], 1)
                            else:
                                itemOthers[0] = re.sub(r"\d+", str(left2), itemOthers[0], 1)
                                
                            itemOthers[2] = re.sub(r"\d+", str(bottom2), itemOthers[2], 1)
                            #print itemOthers
                            #print itemOthers2
                            tmpWords = []
                            indexWord = 0
                            beginStart = 0
                            for itemWords in itemOthers2:
                                if re.search(r"^<ln", itemWords) != None:
                                    beginStart = indexWord
                                    break
                                indexWord += 1
                            tmpWords = itemOthers2[beginStart:]
                            arrSize = len(itemOthers)
                            del itemOthers[arrSize-1]
                            for itemtmpWords in tmpWords:
                                itemOthers.append(itemtmpWords)
                            othersParSecondChance.append(itemOthers)
                            #print itemOthers
                        else:
                            bottom1 = int(re.search(r"\d+", itemOthers[2]).group(0))
                            left1 = int(re.search(r"\d+", itemOthers[0]).group(0))
                            left2 = int(re.search(r"\d+", itemOthers2[0]).group(0))
                            right1 = int(re.search(r"\d+", itemOthers[1]).group(0))
                            right2 = int(re.search(r"\d+", itemOthers2[1]).group(0))
                            
                            if left1 < left2:
                                itemOthers2[0] = re.sub(r"\d+", str(left1), itemOthers2[0], 1)
                            else:
                                if int(right1) < int(currentObject.docfmt["paperw"]):
                                    itemOthers2[1] = re.sub(r"\d+", str(right1), itemOthers2[1], 1)
                                else:
                                    itemOthers2[1] = re.sub(r"\d+", str(right2 + (right1-left1)), itemOthers2[1], 1)
                                
                            itemOthers2[2] = re.sub(r"\d+", str(bottom1), itemOthers2[2], 1)
                            tmpWords = []
                            indexWord = 0
                            beginStart = 0
                            for itemWords in itemOthers:
                                if re.search(r"^<ln", itemWords) != None:
                                    beginStart = indexWord
                                    break
                                indexWord += 1
                            tmpWords = itemOthers[beginStart:]
                            arrSize = len(itemOthers2)
                            del itemOthers2[arrSize-1]
                            for itemtmpWords in tmpWords:
                                itemOthers2.append(itemtmpWords)
                            othersParSecondChance.append(itemOthers2)
                            #print itemOthers2
                    if found:
                        break
                    indexOthers2 += 1
                if found:
                    break
                indexOthers += 1
            if found:
                #for itemFor in othersPar:
                #    print itemFor
                del othersPar[indexOthers]
                #print indexOthers
                #print indexOthers2
                del othersPar[(indexOthers2-1)]
                #print othersPar
                found = False
            else:
                break
                
        #zde se provede zarazeni opravenych odstavcu
        for item in othersParSecondChance:
            parL = re.search(r"\d+", item[0]).group(0)
            parB = re.search(r"\d+", item[1]).group(0)
            try:
                if int(float(currentObject.docfmt["paperw"])/float(int(parB)-int(parL))) == 1:
                    onePar.append(item)
                elif int(float(currentObject.docfmt["paperw"])/float(int(parB)-int(parL))) == 2:
                    twoPar.append(item)
                else:
                    othersPar.append(item)
            except ZeroDivisionError:
                print item
                sys.exit(0)
        
        #for item in twoPar:
        #    print item
        #sys.exit(0)
        
        #muze nastat situace, ze se sice provede
        #oprava, ale oprava jeste neni dokoncena,
        #protoze odstavec byl OCR systemem rozdelen
        #na vice jak jeden odstavec.
        #zde se tedy provede oprava, kdyz k odstavci
        #v dvou sloupcove casti dokumentu patri jeste
        #nejaka cast z othersPar
        indexOthers = 0
        indexOthers2 = 0
        othersParSecondChance = []
        found = False
        while True:
            found = False
            indexOthers = 0
            indexOthers2 = 0
            for itemOthers in twoPar:
                indexOthers2 = 0
                for itemOthers2 in othersPar:
                    if indexOthers == indexOthers2:
                        indexOthers2 += 1
                        continue
                    elif re.search(r"^<table", itemOthers[0]) != None or re.search(r"^<table", itemOthers2[0]) != None:
                        indexOthers2 += 1
                        continue
                    
                    #TODO: tohle optimalizovat, zbytecne se pocita pro kazdy cyklus
                    noWd = True
                    for itemWord in itemOthers:
                        if re.search(r"^<wd", itemWord) != None:
                            noWd = False
                            break
                    if noWd:
                        continue
                    
                    noWd = True
                    for itemWord in itemOthers2:
                        if re.search(r"^<wd", itemWord) != None:
                            noWd = False
                            break
                    if noWd:
                        continue
                    
                    top1 = int(re.search(r"\d+$", itemOthers[0]).group(0))
                    top2 = int(re.search(r"\d+$", itemOthers2[0]).group(0))
                    indexWord = 0
                    for itemWord in itemOthers:
                        if re.search(r"^<wd", itemWord) != None:
                            break
                        indexWord += 1
                    wordT = int(re.search(r"\d+", itemOthers[indexWord+2]).group(0))
                    wordB = int(re.search(r"\d+", itemOthers[indexWord+4]).group(0))
                    tol = wordB - wordT - 5
                    #print itemOthers
                    #print wordT
                    #print wordB
                    #print tol
                    #print top1
                    #print top2
                    if abs(top1-top2) < tol:
                        tmpItemOthers = itemOthers
                        found = True
                        #print itemOthers
                        #print itemOthers2
                        if top1 < top2:
                            bottom2 = int(re.search(r"\d+", itemOthers2[2]).group(0))
                            left1 = int(re.search(r"\d+", itemOthers[0]).group(0))
                            left2 = int(re.search(r"\d+", itemOthers2[0]).group(0))
                            right1 = int(re.search(r"\d+", itemOthers[1]).group(0))
                            right2 = int(re.search(r"\d+", itemOthers2[1]).group(0))
                            
                            if left1 < left2:
                                if int(right2) < int(currentObject.docfmt["paperw"]):
                                    itemOthers[1] = re.sub(r"\d+", str(right2), itemOthers[1], 1)
                                else:
                                    itemOthers[1] = re.sub(r"\d+", str(right1 + (right2-left2)), itemOthers[1], 1)
                            else:
                                tmpItemOthers[0] = re.sub(r"\d+", str(left2), tmpItemOthers[0], 1)
                                
                            tmpItemOthers[2] = re.sub(r"\d+", str(bottom2), tmpItemOthers[2], 1)
                            #print tmpItemOthers
                            #print itemOthers2
                            #sys.exit(0)
                            tmpWords = []
                            indexWord = 0
                            beginStart = 0
                            for itemWords in itemOthers2:
                                if re.search(r"^<ln", itemWords) != None:
                                    beginStart = indexWord
                                    break
                                indexWord += 1
                            tmpWords = itemOthers2[beginStart:]
                            arrSize = len(tmpItemOthers)
                            del tmpItemOthers[arrSize-1]
                            for itemtmpWords in tmpWords:
                                tmpItemOthers.append(itemtmpWords)
                            othersParSecondChance.append(tmpItemOthers)
                            #print itemOthers
                        else:
                            bottom1 = int(re.search(r"\d+", itemOthers[2]).group(0))
                            left1 = int(re.search(r"\d+", itemOthers[0]).group(0))
                            left2 = int(re.search(r"\d+", itemOthers2[0]).group(0))
                            right1 = int(re.search(r"\d+", itemOthers[1]).group(0))
                            right2 = int(re.search(r"\d+", itemOthers2[1]).group(0))
                            
                            if left1 < left2:
                                itemOthers2[0] = re.sub(r"\d+", str(left1), itemOthers2[0], 1)
                            else:
                                if int(right1) < int(currentObject.docfmt["paperw"]):
                                    itemOthers2[1] = re.sub(r"\d+", str(right1), itemOthers2[1], 1)
                                else:
                                    itemOthers2[1] = re.sub(r"\d+", str(right2 + (right1-left1)), itemOthers2[1], 1)
                                
                            itemOthers2[2] = re.sub(r"\d+", str(bottom1), itemOthers2[2], 1)
                            tmpWords = []
                            indexWord = 0
                            beginStart = 0
                            for itemWords in tmpItemOthers:
                                if re.search(r"^<ln", itemWords) != None:
                                    beginStart = indexWord
                                    break
                                indexWord += 1
                            tmpWords = tmpItemOthers[beginStart:]
                            arrSize = len(itemOthers2)
                            del itemOthers2[arrSize-1]
                            for itemtmpWords in tmpWords:
                                itemOthers2.append(itemtmpWords)
                            othersParSecondChance.append(itemOthers2)
                            #print itemOthers2
                    if found:
                        break
                    indexOthers2 += 1
                if found:
                    break
                indexOthers += 1
            if found:
                #for itemFor in othersPar:
                #    print itemFor
                del twoPar[indexOthers]
                #print indexOthers
                #print indexOthers2
                del othersPar[indexOthers2]
                #print othersPar
                found = False
            else:
                break
        
        #zde se provede zarazeni opravenych odstavcu
        for item in othersParSecondChance:
            parL = re.search(r"\d+", item[0]).group(0)
            parB = re.search(r"\d+", item[1]).group(0)
            try:
                if int(float(currentObject.docfmt["paperw"])/float(int(parB)-int(parL))) == 1:
                    onePar.append(item)
                elif int(float(currentObject.docfmt["paperw"])/float(int(parB)-int(parL))) == 2:
                    twoPar.append(item)
                else:
                    othersPar.append(item)
            except ZeroDivisionError:
                print item
                sys.exit(0)
        
        #muze nastat situace, ze se sice provede
        #oprava, ale oprava jeste neni dokoncena,
        #protoze odstavec byl OCR systemem rozdelen
        #na vice jak jeden odstavec.
        #zde se tedy provede oprava, kdyz k odstavci
        #v jednove sloupcove casti dokumentu patri jeste
        #nejaka cast z othersPar
        indexOthers = 0
        indexOthers2 = 0
        othersParSecondChance = []
        found = False
        while True:
            found = False
            indexOthers = 0
            indexOthers2 = 0
            for itemOthers in onePar:
                indexOthers2 = 0
                for itemOthers2 in othersPar:
                    if indexOthers == indexOthers2:
                        indexOthers2 += 1
                        continue
                    elif re.search(r"^<table", itemOthers[0]) != None or re.search(r"^<table", itemOthers2[0]) != None:
                        indexOthers2 += 1
                        continue
                    top1 = int(re.search(r"\d+$", itemOthers[0]).group(0))
                    top2 = int(re.search(r"\d+$", itemOthers2[0]).group(0))
                    indexWord = 0
                    for itemWord in itemOthers:
                        if re.search(r"^<wd", itemWord) != None:
                            break
                        indexWord += 1
                    wordT = int(re.search(r"\d+", itemOthers[indexWord+2]).group(0))
                    wordB = int(re.search(r"\d+", itemOthers[indexWord+4]).group(0))
                    tol = wordB - wordT - 5
                    #print itemOthers
                    #print wordT
                    #print wordB
                    #print tol
                    #print top1
                    #print top2
                    if abs(top1-top2) < tol:
                        tmpItemOthers = itemOthers
                        found = True
                        #print itemOthers
                        #print itemOthers2
                        if top1 < top2:
                            bottom2 = int(re.search(r"\d+", itemOthers2[2]).group(0))
                            left1 = int(re.search(r"\d+", itemOthers[0]).group(0))
                            left2 = int(re.search(r"\d+", itemOthers2[0]).group(0))
                            right1 = int(re.search(r"\d+", itemOthers[1]).group(0))
                            right2 = int(re.search(r"\d+", itemOthers2[1]).group(0))
                            
                            if left1 < left2:
                                #print currentObject.docfmt["paperw"]
                                #sys.exit(0)
                                if int(right2) < int(currentObject.docfmt["paperw"]):
                                    itemOthers[1] = re.sub(r"\d+", str(right2), itemOthers[1], 1)
                                else:
                                    itemOthers[1] = re.sub(r"\d+", str(right1 + (right2-left2)), itemOthers[1], 1)
                            else:
                                tmpItemOthers[0] = re.sub(r"\d+", str(left2), tmpItemOthers[0], 1)
                                
                            tmpItemOthers[2] = re.sub(r"\d+", str(bottom2), tmpItemOthers[2], 1)
                            #print tmpItemOthers
                            #print itemOthers2
                            #sys.exit(0)
                            tmpWords = []
                            indexWord = 0
                            beginStart = 0
                            for itemWords in itemOthers2:
                                if re.search(r"^<ln", itemWords) != None:
                                    beginStart = indexWord
                                    break
                                indexWord += 1
                            tmpWords = itemOthers2[beginStart:]
                            arrSize = len(tmpItemOthers)
                            del tmpItemOthers[arrSize-1]
                            for itemtmpWords in tmpWords:
                                tmpItemOthers.append(itemtmpWords)
                            othersParSecondChance.append(tmpItemOthers)
                            #print itemOthers
                        else:
                            bottom1 = int(re.search(r"\d+", itemOthers[2]).group(0))
                            left1 = int(re.search(r"\d+", itemOthers[0]).group(0))
                            left2 = int(re.search(r"\d+", itemOthers2[0]).group(0))
                            right1 = int(re.search(r"\d+", itemOthers[1]).group(0))
                            right2 = int(re.search(r"\d+", itemOthers2[1]).group(0))
                            
                            if left1 < left2:
                                itemOthers2[0] = re.sub(r"\d+", str(left1), itemOthers2[0], 1)
                            else:
                                if int(right1) < int(currentObject.docfmt["paperw"]):
                                    itemOthers2[1] = re.sub(r"\d+", str(right1), itemOthers2[1], 1)
                                else:
                                    itemOthers2[1] = re.sub(r"\d+", str(right2 + (right1-left1)), itemOthers2[1], 1)
                                
                            itemOthers2[2] = re.sub(r"\d+", str(bottom1), itemOthers2[2], 1)
                            tmpWords = []
                            indexWord = 0
                            beginStart = 0
                            for itemWords in tmpItemOthers:
                                if re.search(r"^<ln", itemWords) != None:
                                    beginStart = indexWord
                                    break
                                indexWord += 1
                            tmpWords = tmpItemOthers[beginStart:]
                            arrSize = len(itemOthers2)
                            del itemOthers2[arrSize-1]
                            for itemtmpWords in tmpWords:
                                itemOthers2.append(itemtmpWords)
                            othersParSecondChance.append(itemOthers2)
                            #print itemOthers2
                    if found:
                        break
                    indexOthers2 += 1
                if found:
                    break
                indexOthers += 1
            if found:
                #for itemFor in othersPar:
                #    print itemFor
                del onePar[indexOthers]
                #print indexOthers
                #print indexOthers2
                del othersPar[indexOthers2]
                #print othersPar
                found = False
            else:
                break
        
        #zde se provede zarazeni opravenych odstavcu
        for item in othersParSecondChance:
            parL = re.search(r"\d+", item[0]).group(0)
            parB = re.search(r"\d+", item[1]).group(0)
            try:
                if int(float(currentObject.docfmt["paperw"])/float(int(parB)-int(parL))) == 1:
                    onePar.append(item)
                elif int(float(currentObject.docfmt["paperw"])/float(int(parB)-int(parL))) == 2:
                    twoPar.append(item)
                else:
                    othersPar.append(item)
                    #TODO: tohle je jen docasne reseni a neni zarucene, ze bude fungovat
                    #            az bude chvile, tak opravit
                    #twoPar.append(item)
            except ZeroDivisionError:
                print item
                sys.exit(0)
        
        #for item in onePar:
        #    print item
        #for itemOthers in othersParSecondChance:
        #    print itemOthers
        #sys.exit(0)
        #for itemOthers in othersPar:
        #    print itemOthers
        #sys.exit(0)
        
        #odhad hranice, kde konci levy a zacina pravy sloupec
        sum = 0
        cnt = 0
        for item in twoPar:
            sum += int(re.search(r"\d+", item[0]).group(0))
            cnt += 1
        if cnt > 0:
            avg = sum/cnt
        else:
            #avg = int(currentObject.docfmt["paperw"])
            avg = 15000
        
        #print "onePar"
        #for item in onePar:
        #    print item
        
        #print "twoPar"
        #for item in twoPar:
        #    print item
        
        #print "othersPar"
        #for item in othersPar:
        #    print item
        
        #zde se projedou vsechny odstavce a usporadaji se podle polohy
        nextPar = 0
        sortedPars = []
        oneParWin = []
        twoParWin = []
        buff = []
        twoColumns = False
        while True:
            #nastaveni vychozi hodnoty pro oneParPos
            oneParPos = nextPar
            
            #nastaveni priznaku, ze se jedna o prvni odstavec
            firstPar = True
            
            #pozice odstavce
            oneParIndex = 0
            
            #vitezny odstavec
            oneParWinIndex = 0
            
            #hledani odstavce  s nejmensim umistenim od pocatku
            for item in onePar:
                #print item
                if firstPar:
                    if re.search(r"^<table", item[0]) != None:
                        oneParPos = int(re.search(r"(\d+)\" $", item[0]).group(1))
                    else:
                        oneParPos = int(re.search(r"\d+$", item[0]).group(0))
                    oneParWin = list(item)
                    firstPar = False
                else:
                    if re.search(r"^<table", item[0]) != None:
                        tmpPos = int(re.search(r"(\d+)\" $", item[0]).group(1))
                    else:
                        tmpPos = int(re.search(r"\d+$", item[0]).group(0))
                    if tmpPos < oneParPos:
                        oneParPos = tmpPos
                        oneParWin = list(item)
                        oneParWinIndex = oneParIndex
                oneParIndex += 1
            
            #analogicky pro odstavce v dvou sloupcove casti dokumentu
            twoParPos = nextPar
            firstPar = True
            twoParIndex = 0
            twoParWinIndex = 0
            #hledani odstavce  s nejmensim umistenim od pocatku
            for item in twoPar:
                #print "RomisekOnePar"
                #print item
                if firstPar:
                    if re.search(r"^<table", item[0]) != None:
                        twoParPos = int(re.search(r"(\d+)\" $", item[0]).group(1))
                    else:
                        twoParPos = int(re.search(r"\d+$", item[0]).group(0))
                    
                    twoParWin = list(item)
                    firstPar = False
                else:
                    if re.search(r"^<table", item[0]) != None:
                        tmpPos = int(re.search(r"(\d+)\" $", item[0]).group(1))
                    else:
                        tmpPos = int(re.search(r"\d+$", item[0]).group(0))
                    
                    if tmpPos < twoParPos:
                        twoParPos = tmpPos
                        twoParWin = list(item)
                        twoParWinIndex = twoParIndex
                twoParIndex += 1
                
            if onePar and twoPar and oneParPos == twoParPos:
                #print "JE TO TAK!!!"
                sys.stderr.write("rtfParser :: MakeDocument() - Nepripustna situace\n")
                #print "oneParPos == twoParPos"
                #muze se stat, ze predtim jsme nacitali odstavce z dvousloupcove casti
                #a ty prave jeste nebyly ulozeny, protoze se nejprve musi ulozit ty leve
                if twoColumns:
                    for itemBuff in buff:
                        sortedPars.append("TWOPAR")
                        sortedPars.append(itemBuff)
                    twoColumns = False
                    buff = []
                    
                #vsechny odstavce z bufferu byly zapsany, takze nyni ten vitezny
                sortedPars.append("ONEPAR")
                sortedPars.append(oneParWin)
                nextPar = oneParPos
                del onePar[oneParWinIndex]
                #sys.exit(1)
            #pokud je nejaky odstavec v onePar a jeho pozice je mensi nez odstavce z twoPar
            if onePar and oneParPos < twoParPos:
                #print "onePar and oneParPos < twoParPos"
                #muze se stat, ze predtim jsme nacitali odstavce z dvousloupcove casti
                #a ty prave jeste nebyly ulozeny, protoze se nejprve musi ulozit ty leve
                if twoColumns:
                    for itemBuff in buff:
                        sortedPars.append("TWOPAR")
                        sortedPars.append(itemBuff)
                    twoColumns = False
                    buff = []
                    
                #vsechny odstavce z bufferu byly zapsany, takze nyni ten vitezny
                sortedPars.append("ONEPAR")
                sortedPars.append(oneParWin)
                nextPar = oneParPos
                del onePar[oneParWinIndex]
                
            #analogicky pro twoPar
            elif twoPar and twoParPos < oneParPos:
                #print "twoPar and twoParPos < oneParPos"
                twoColumns = True
                
                #Pokud je viteznym odstavec z praveho sloupce, pak je ulozen do bufferu
                #print "Left: " + re.search(r"\d+", twoPar[twoParWinIndex][0]).group(0)
                if int(re.search(r"\d+", twoPar[twoParWinIndex][0]).group(0)) > avg:
                    #print "->BUFF"
                    #print "--------------"
                    buff.append(twoParWin)
                    del twoPar[twoParWinIndex]
                #Jinak jej normalne zaradime do pole
                else:
                    #print "->Sorted"
                    #for itemSort in sortedPars:
                    #    print itemSort
                    #print "--------------"
                    sortedPars.append("TWOPAR")
                    sortedPars.append(twoParWin)
                    nextPar = twoParPos
                    del twoPar[twoParWinIndex]
            
            #Pokud nam uz zbyvaji pouze jednosloupcove odstavce
            elif onePar and not twoPar:
                #print "onePar and not twoPar"
                #Vycisteni bufferu
                if twoColumns:
                    for itemBuff in buff:
                        sortedPars.append("TWOPAR")
                        sortedPars.append(itemBuff)
                    twoColumns = False
                    buff = []
                
                #Zarazeni viteze
                sortedPars.append("ONEPAR")
                sortedPars.append(oneParWin)
                nextPar = oneParPos
                del onePar[oneParWinIndex]
            
            #Pokud uz zbyvaji jen dvousloupcove odstavce
            elif twoPar and not onePar:
                #print "twoPar and not onePar"
                if int(re.search(r"\d+", twoPar[twoParWinIndex][0]).group(0)) > avg:
                    #print "->BUFF"
                    #print "--------------"
                    buff.append(twoParWin)
                    del twoPar[twoParWinIndex]
                else:
                    #print "->Sorted"
                    sortedPars.append("TWOPAR")
                    sortedPars.append(twoParWin)
                    #for itemSort in sortedPars:
                    #    print itemSort
                    #print "--------------"
                    nextPar = twoParPos
                    del twoPar[twoParWinIndex]
            else:
                #print "break"
                #print avg
                #for itemSort in sortedPars:
                #    print itemSort
                #print "-----------------"
                break
        
        #print "\n"
        #Vycisteni bufferu
        if buff:
            for item in buff:
                sortedPars.append("TWOPAR")
                sortedPars.append(item)
            buff = []
        
        #TODO: opravit pro pripad, ze na strance neni zadny odstavec,
        #ktery by se vesel do onePar nebo twoPar
        #for item in onePar:
        #    print item
        #sys.exit(0)
        #for item in sortedPars:
        #    print item
        #sys.exit(0)
        #vytvoreni xml
        currentObject.xmlSortedPars = sortedPars
        try:
            typeSec = sortedPars[0]
        except IndexError:
            sys.stderr.write("Vyjimka! Dodelat!\n")
            for item in onePar:
                print item
            for item in twoPar:
                print item
            sys.exit(1)
        section = []
        section.append(typeSec)
        xml = "<document>\n"
        currentObject.xmlOutput += "<document>\n"
        xml += "<page>\n"
        currentObject.xmlOutput += "<page>\n"
        xml += "<body>\n"
        currentObject.xmlOutput += "<body>\n"
        breakWhile = False
        while True:
            if not sortedPars:
                breakWhile = True
            if sortedPars and sortedPars[0] == typeSec:
                del sortedPars[0]
                section.append(sortedPars[0])
                del sortedPars[0]
            else:
                try:
                    tmpTry = section[0]
                except IndexError:
                    print "SORTED"
                    print sortedPars
                    print "SECTION"
                    print section
                    sys.exit(0)
                if section[0] == "ONEPAR":
                    del section[0]
                    #print section
                    secColL = int(re.search(r"\d+", section[0][0]).group(0))
                    
                    if re.search(r"^<table", section[0][0]) != None:
                        secColT = int(re.search(r"(\d+)\" $", section[0][0]).group(1))
                    else:
                        secColT = int(re.search(r"\d+$", section[0][0]).group(0))
                    
                    secColR = int(re.search(r"\d+", section[0][1]).group(0))
                    secColB = int(re.search(r"\d+", section[-1][2]).group(0))
                    #print secColL
                    #print secColT
                    #print secColR
                    #print secColB
                    xml += "<section l=\"" + str(secColL) + "\" "
                    currentObject.xmlOutput += "<section l=\"" + str(secColL) + "\" "
                    xml += "t=\"" + str(secColT) + "\" "
                    currentObject.xmlOutput += "t=\"" + str(secColT) + "\" "
                    xml += "r=\"" + str(secColR) + "\" "
                    currentObject.xmlOutput += "r=\"" + str(secColR) + "\" "
                    xml += "b=\"" + str(secColB) + "\">\n"
                    currentObject.xmlOutput += "b=\"" + str(secColB) + "\">\n"
                    xml += "<column l=\"" + str(secColL) + "\" "
                    currentObject.xmlOutput += "<column l=\"" + str(secColL) + "\" "
                    xml += "t=\"" + str(secColT) + "\" "
                    currentObject.xmlOutput += "t=\"" + str(secColT) + "\" "
                    xml += "r=\"" + str(secColR) + "\" "
                    currentObject.xmlOutput += "r=\"" + str(secColR) + "\" "
                    xml += "b=\"" + str(secColB) + "\">\n"
                    currentObject.xmlOutput += "b=\"" + str(secColB) + "\">\n"
                    for item in section:
                        for itemPar in item:
                            xml += itemPar
                            currentObject.xmlOutput += itemPar
                    xml += "</column>\n"
                    currentObject.xmlOutput += "</column>\n"
                    xml += "</section>\n"
                    currentObject.xmlOutput += "</section>\n"
                    #print xml
                    #print sortedPars
                    section = []
                    if breakWhile:
                        break
                    typeSec = sortedPars[0]
                    section.append(typeSec)
                else:
                    del section[0]
                    #print section
                    secColL = int(re.search(r"\d+", section[0][0]).group(0))
                    
                    if re.search(r"^<table", section[0][0]) != None:
                        secColT = int(re.search(r"(\d+)\" $", section[0][0]).group(1))
                    else:
                        secColT = int(re.search(r"\d+$", section[0][0]).group(0))
                    
                    secColR = int(re.search(r"\d+", section[0][1]).group(0))
                    secColB = int(re.search(r"\d+", section[-1][2]).group(0))
                    #print secColL
                    #print secColT
                    #print secColR
                    #print secColB
                    xml += "<section l=\"" + str(secColL) + "\" "
                    currentObject.xmlOutput += "<section l=\"" + str(secColL) + "\" "
                    xml += "t=\"" + str(secColT) + "\" "
                    currentObject.xmlOutput += "t=\"" + str(secColT) + "\" "
                    xml += "r=\"" + str(secColR) + "\" "
                    currentObject.xmlOutput += "r=\"" + str(secColR) + "\" "
                    xml += "b=\"" + str(secColB) + "\">\n"
                    currentObject.xmlOutput += "b=\"" + str(secColB) + "\">\n"
                    column = []
                    try:
                        while section and int(re.search(r"\d+", section[0][0]).group(0)) <= avg:
                            column.append(section[0])
                            del section[0]
                        if not column:
                            while section:
                                column.append(section[0])
                                del section[0]
                    except IndexError:
                        print xml
                        sys.exit(0)
                    try:
                        colL = int(re.search(r"\d+", column[0][0]).group(0))
                    except IndexError:
                        sys.stderr.write("RTFParser::MakeDocument() - L hodnota sloupce nenalezena!\n")
                        #print sortedPars
                        print section
                        print "Column"
                        print column
                        print avg
                        print xml
                        sys.exit(0)
                    if re.search(r"^<table", column[0][0]) != None:
                        colT = int(re.search(r"(\d+)\" $", column[0][0]).group(1))
                    else:
                        colT = int(re.search(r"\d+$", column[0][0]).group(0))
                    colR = int(re.search(r"\d+", column[0][1]).group(0))
                    colB = int(re.search(r"\d+", column[-1][2]).group(0))
                    xml += "<column l=\"" + str(secColL) + "\" "
                    currentObject.xmlOutput += "<column l=\"" + str(secColL) + "\" "
                    xml += "t=\"" + str(colT) + "\" "
                    currentObject.xmlOutput += "t=\"" + str(colT) + "\" "
                    xml += "r=\"" + str(colR) + "\" "
                    currentObject.xmlOutput += "r=\"" + str(colR) + "\" "
                    xml += "b=\"" + str(colB) + "\">\n"
                    currentObject.xmlOutput += "b=\"" + str(colB) + "\">\n"
                    for item in column:
                        for itemPar in item:
                            xml += itemPar
                            currentObject.xmlOutput += itemPar
                    xml += "</column>\n"
                    currentObject.xmlOutput += "</column>\n"
                    if section:
                        secL = int(re.search(r"\d+", section[0][0]).group(0))
                        if re.search(r"^<table", section[0][0]) != None:
                            secT = int(re.search(r"(\d+)\" $", section[0][0]).group(1))
                        else:
                            secT = int(re.search(r"\d+$", section[0][0]).group(0))
                        secR = int(re.search(r"\d+", section[0][1]).group(0))
                        secB = int(re.search(r"\d+", section[-1][2]).group(0))
                        xml += "<column l=\"" + str(secL) + "\" "
                        currentObject.xmlOutput += "<column l=\"" + str(secL) + "\" "
                        xml += "t=\"" + str(secT) + "\" "
                        currentObject.xmlOutput += "t=\"" + str(secT) + "\" "
                        xml += "r=\"" + str(secR) + "\" "
                        currentObject.xmlOutput += "r=\"" + str(secR) + "\" "
                        xml += "b=\"" + str(secB) + "\">\n"
                        currentObject.xmlOutput += "b=\"" + str(secB) + "\">\n"
                        for item in section:
                            for itemPar in item:
                                xml += itemPar
                                currentObject.xmlOutput += itemPar
                        xml += "</column>\n</section>\n"
                        currentObject.xmlOutput += "</column>\n</section>\n"
                    else:
                        xml += "</section>\n"
                        currentObject.xmlOutput += "</section>\n"
                    
                    section = []
                    if breakWhile:
                        break
                    typeSec = sortedPars[0]
                    section.append(typeSec)
        xml += "</body>\n"
        currentObject.xmlOutput += "</body>\n"
        xml += "</page>\n"
        currentObject.xmlOutput += "</page>\n"
        xml += "</document>\n"
        currentObject.xmlOutput += "</document>\n"
        #print currentObject.xmlOutput
        #print xml
        #sys.exit(0)
    
    #Metoda nastavujici jednotlive parametry dokumentu
    #param1 promenna, ktera se ma nastavit
    def SetDocFmt(self, currentObject, keyword, readedData):
        if keyword == "paperw":
            value = re.search(r"^\\paperw((\-)?\d+)", readedData).group(1)
            currentObject.docfmt[keyword] = value
        elif keyword == "paperh":
            value = re.search(r"^\\paperh((\-)?\d+)", readedData).group(1)
            currentObject.docfmt[keyword] = value
        elif keyword == "margl":
            value = re.search(r"^\\margl((\-)?\d+)", readedData).group(1)
            currentObject.docfmt[keyword] = value
        elif keyword == "margr":
            value = re.search(r"^\\margr((\-)?\d+)", readedData).group(1)
            currentObject.docfmt[keyword] = value
        elif keyword == "margb":
            value = re.search(r"^\\margb((\-)?\d+)", readedData).group(1)
            currentObject.docfmt[keyword] = value
        elif keyword == "margt":
            value = re.search(r"^\\margt((\-)?\d+)", readedData).group(1)
            currentObject.docfmt[keyword] = value
        elif keyword == "gutter":
            value = re.search(r"^\\gutter((\-)?\d+)", readedData).group(1)
            currentObject.docfmt[keyword] = value
        elif keyword == "viewkind":
            value = re.search(r"^\\viewkind((\-)?\d+)", readedData).group(1)
            currentObject.docfmt[keyword] = value
        elif keyword == "viewzk":
            value = re.search(r"^\\viewzk((\-)?\d+)", readedData).group(1)
            currentObject.docfmt[keyword] = value
        elif keyword == "fet":
            value = re.search(r"^\\fet((\-)?\d+)", readedData).group(1)
            currentObject.docfmt[keyword] = value
        #else:
            #if imp_mode:
            #    sys.stderr.write("Pozor: SetDocFmt() - Klicove slovo " + keyword + " nezpracovano\n")
    
    #Metoda nastavujici jednotlive parametry dokumentu
    #param1 promenna, ktera se ma nastavit
    def SetApoCtl(self, currentObject, keyword, readedData):
        if keyword == "absw":
            value = re.search(r"^\\absw((\-)?\d+)", readedData).group(1)
            #print value
            currentObject.apoctl[keyword] = value
        elif keyword == "absh":
            value = re.search(r"^\\absh((\-)?\d+)", readedData).group(1)
            currentObject.apoctl[keyword] = value
        elif keyword == "phpg":
            currentObject.apoctl[keyword] = True
        elif keyword == "pvpg":
            currentObject.apoctl[keyword] = True
        elif keyword == "posx":
            value = re.search(r"^\\posx((\-)?\d+)", readedData).group(1)
            currentObject.apoctl[keyword] = value
        elif keyword == "posy":
            value = re.search(r"^\\posy((\-)?\d+)", readedData).group(1)
            currentObject.apoctl[keyword] = value
        #else:
            #if imp_mode:
            #    sys.stderr.write("Pozor: SetApoCtl() - Klicove slovo " + keyword + " nezpracovano\n")
    
    #Metoda nastavujici jednotlive parametry dokumentu
    #param1 promenna, ktera se ma nastavit
    def SetParFmt(self, currentObject, keyword, readedData):
        if keyword == "fs":
            value = re.search(r"^\\fs((\-)?\d+)", readedData).group(1)
            currentObject.parfmt[keyword] = value
            #print "Zadano fs:" + value
        elif keyword == "sa":
            value = re.search(r"^\\sa((\-)?\d+)", readedData).group(1)
            currentObject.parfmt[keyword] = value
        elif keyword == "sl":
            value = re.search(r"^\\sl((\-)?\d+)", readedData).group(1)
            currentObject.parfmt[keyword] = value
        elif keyword == "slmult":
            value = re.search(r"^\\slmult((\-)?\d+)", readedData).group(1)
            currentObject.parfmt[keyword] = value
        elif keyword == "lang":
            value = re.search(r"^\\lang((\-)?\d+)", readedData).group(1)
            currentObject.parfmt[keyword] = value
        elif keyword == "li":
            value = re.search(r"^\\li((\-)?\d+)", readedData).group(1)
            currentObject.parfmt[keyword] = value
        elif keyword == "ri":
            value = re.search(r"^\\ri((\-)?\d+)", readedData).group(1)
            currentObject.parfmt[keyword] = value
        elif keyword == "qc":
            currentObject.parfmt[keyword] = "1"
        elif keyword == "qj":
            currentObject.parfmt[keyword] = "1"
        #else:
            #if imp_mode:
            #   sys.stderr.write("Pozor: SetParFmt() - Klicove slovo " + keyword + " nezpracovano\n")
    
    #Metoda nastavujici jednotlive parametry dokumentu
    #param1 promenna, ktera se ma nastavit
    def SetChrFmt(self, currentObject, keyword, readedData):
        if keyword == "cs":
            value = re.search(r"^\\cs((\-)?\d+)", readedData).group(1)
            currentObject.chrfmt[keyword] = value
        #else:
            #if imp_mode:
            #    sys.stderr.write("Pozor: SetChrFmt() - Klicove slovo " + keyword + " nezpracovano\n")
    
    #Metoda parsujici Field v Body
    #@param1 objekt, do ktereho by se pripadne ukladaly informace
    #@param2 nacteny RTF soubor
    #@return1 nenaparsovana cast RTF souboru
    #@return2 cast xml vystupu
    def Field(self, currentObject, readedData):
        xml = ""
        retArray = []
        global imp_mode
        
        #print "Field"
        #print readedData
        #sys.exit(0)
        readedData = re.sub(r"\\field(\x0D\x0A)?", "", readedData, 1)
        #print readedData
        #<fieldmod>
        while True:
            if re.search(r"^\{\\[a-zA-Z]+", readedData) != None:
                keyword = re.search(r"\{(\\[a-zA-Z]+)", readedData).group(1)
                if keyword == "flddirty" or keyword == "fldedit" or keyword == "fldlock" or keyword == "fldpriv":
                    readedData = re.sub(r"^\{\\[a-zA-Z]+", "", readedData, 1)
            else:
                break
        #<fieldinst>
        #tohle neni podle specifikace 1.9.1
        readedData = re.sub(r"^\{\\\*\\fldinst[^\}]+(\}(\x0D\x0A)?){2}", "", readedData, 1)
        #<fieldrslt>
        readedData = re.sub(r"^\{\\fldrslt(\x0D\x0A)?\{(\x0D\x0A)?\{", "", readedData, 1)
        #currentObject.SaveOnStack(currentObject)
        tmpArray = currentObject.Keywords(currentObject, readedData)
        readedData = tmpArray[0]
        xml += tmpArray[1]
        #print readedData
        #sys.exit(0)
        readedData = re.sub(r"^\s", "", readedData, 1)
        plainText = {}
        if re.search(r"^\\\*\\bkmkstart", readedData) != None:
            tmpArray = currentObject.Bookmark(currentObject, readedData)
            readedData = tmpArray[0]
            readedData = re.sub(r"^(\}(\x0D\x0A)?){3}", "", readedData, 1)
            #print readedData
            #sys.exit(0)
        #print readedData
        #sys.exit(0)
        else:
            plainText["text"] = re.search(r"^[^\}]+", readedData).group(0)
            plainText["special"] = currentObject.special
            currentObject.plainText.append(plainText)
            tmpArray = currentObject.ParseText(currentObject, readedData)
            #currentObject.LoadFromStack(currentObject)
            readedData = tmpArray[0]
            xml += tmpArray[1]
            #print readedData
            #sys.exit(0)
            #if imp_mode:
            #    sys.stderr.write("1403:doplnit richText\n")
            if re.search(r"^\{\\\*\\bkmkend", readedData) == None:
                readedData = re.sub(r"^[^\}]*(\}(\x0D\x0A)?){3}", "", readedData, 1)

        readedData = re.sub(r"^\}+", "", readedData, 1)
        #print readedData
        #print "Konec field"
        #print readedData
        #sys.exit(0)
        retArray.append(readedData)
        retArray.append(xml)
        return retArray
    
    #Metoda parsujici Info v Body
    #@param1 objekt, do ktereho by se pripadne ukladaly informace
    #@param2 nacteny RTF soubor
    #@return1 nenaparsovana cast RTF souboru
    #@return2 cast xml vystupu
    def Info(self, currentObject, readedData):
        xml = ""
        retArray = []
        
        readedData = re.sub(r"^\\info(\x0D\x0A)?", "", readedData, 1)
        #print readedData
        #sys.exit(0)
        while True:
            #print "Info"
            #print readedData
            if readedData[0] == '}':
                break
            if re.search(r"^\{", readedData) != None:
                readedData = re.sub(r"^\{", "", readedData, 1)
                if re.search(r"^\\title", readedData) != None:
                    #print "Keyword"
                    #print readedData
                    readedData = re.sub(r"\\title", "", readedData, 1)
                    currentObject.infoDic["title"] = re.search(r"^[^\}]*", readedData).group(0)
                    readedData = re.sub(r"^[^\}]*(\x0D\x0A)?", "", readedData, 1)
                    #print "Keyword"
                    #print readedData
                if re.search(r"^\\subject", readedData) != None:
                    #print "Keyword"
                    #print readedData
                    readedData = re.sub(r"^\\subject", "", readedData, 1)
                    currentObject.infoDic["subject"] = re.search(r"[^\}]*", readedData).group(0)
                    readedData = re.sub(r"[^\}]*(\x0D\x0A)?", "", readedData, 1)
                if re.search(r"^\\author", readedData) != None:
                    #print "Keyword"
                    #print readedData
                    readedData = re.sub(r"\\author", "", readedData, 1)
                    currentObject.infoDic["author"] = re.search(r"[^\}]*", readedData).group(0)
                    readedData = re.sub(r"[^\}]*(\x0D\x0A)?", "", readedData, 1)
                if re.search(r"^\\manager", readedData) != None:
                    readedData = re.sub(r"\\manager", "", readedData, 1)
                    currentObject.infoDic["manager"] = re.search(r"[^\}]*", readedData).group(0)
                    readedData = re.sub(r"[^\}]*(\x0D\x0A)?", "", readedData, 1)
                if re.search(r"^\\company", readedData) != None:
                    readedData = re.sub(r"\\company", "", readedData, 1)
                    currentObject.infoDic["company"] = re.search(r"[^\}]*", readedData).group(0)
                    readedData = re.sub(r"[^\}]*(\x0D\x0A)?", "", readedData, 1)
                if re.search(r"^\\operator", readedData) != None:
                    readedData = re.sub(r"\\operator", "", readedData, 1)
                    currentObject.infoDic["operator"] = re.search(r"[^\}]*", readedData).group(0)
                    readedData = re.sub(r"[^\}]*(\x0D\x0A)?", "", readedData, 1)
                if re.search(r"^\\category", readedData) != None:
                    readedData = re.sub(r"\\category", "", readedData, 1)
                    currentObject.infoDic["category"] = re.search(r"[^\}]*", readedData).group(0)
                    readedData = re.sub(r"[^\}]*(\x0D\x0A)?", "", readedData, 1)
                if re.search(r"^\\keywords", readedData) != None:
                    #print "Keyword"
                    #print readedData
                    readedData = re.sub(r"\\keywords", "", readedData, 1)
                    currentObject.infoDic["keywords"] = re.search(r"[^\}]*", readedData).group(0)
                    readedData = re.sub(r"[^\}]*(\x0D\x0A)?", "", readedData, 1)
                if re.search(r"^\\comment", readedData) != None:
                    readedData = re.sub(r"\\comment", "", readedData, 1)
                    currentObject.infoDic["comment"] = re.search(r"[^\}]*", readedData).group(0)
                    readedData = re.sub(r"[^\}]*(\x0D\x0A)?", "", readedData, 1)
                if re.search(r"^\\doccomm", readedData) != None:
                    readedData = re.sub(r"\\doccomm", "", readedData, 1)
                    currentObject.infoDic["doccomm"] = re.search(r"[^\}]*", readedData).group(0)
                    readedData = re.sub(r"[^\}]*(\x0D\x0A)?", "", readedData, 1)
                if re.search(r"^\\hlinkbase", readedData) != None:
                    readedData = re.sub(r"\\hlinkbase", "", readedData, 1)
                    currentObject.infoDic["hlinkbase"] = re.search(r"[^\}]*", readedData).group(0)
                    readedData = re.sub(r"[^\}]*(\x0D\x0A)?", "", readedData, 1)
                if re.search(r"^\\creatim", readedData) != None:
                    readedData = re.sub(r"\\creatim", "", readedData, 1)
                    timeDic = {}
                    if re.search(r"^\\yr\d+", readedData) != None:
                        timeDic["yr"] = re.search(r"\\yr(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\yr\d+", "", readedData, 1)
                    if re.search(r"^\\mo\d+", readedData) != None:
                        timeDic["mo"] = re.search(r"\\mo(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\mo\d+", "", readedData, 1)
                    if re.search(r"^\\dy\d+", readedData) != None:
                        timeDic["dy"] = re.search(r"\\dy(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\dy\d+", "", readedData, 1)
                    if re.search(r"^\\hr\d+", readedData) != None:
                        timeDic["hr"] = re.search(r"\\hr(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\hr\d+", "", readedData, 1)
                    if re.search(r"^\\min\d+", readedData) != None:
                        timeDic["min"] = re.search(r"\\min(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\min\d+", "", readedData, 1)
                    if re.search(r"^\\sec\d+", readedData) != None:
                        timeDic["sec"] = re.search(r"\\sec(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\sec\d+", "", readedData, 1)
                    currentObject.infoDic["creatim"] = timeDic
                if re.search(r"^\\revtim", readedData) != None:
                    readedData = re.sub(r"\\revtim", "", readedData, 1)
                    timeDic = {}
                    if re.search(r"^\\yr\d+", readedData) != None:
                        timeDic["yr"] = re.search(r"\\yr(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\yr\d+", "", readedData, 1)
                    if re.search(r"^\\mo\d+", readedData) != None:
                        timeDic["mo"] = re.search(r"\\mo(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\mo\d+", "", readedData, 1)
                    if re.search(r"^\\dy\d+", readedData) != None:
                        timeDic["dy"] = re.search(r"\\dy(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\dy\d+", "", readedData, 1)
                    if re.search(r"^\\hr\d+", readedData) != None:
                        timeDic["hr"] = re.search(r"\\hr(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\hr\d+", "", readedData, 1)
                    if re.search(r"^\\min\d+", readedData) != None:
                        timeDic["min"] = re.search(r"\\min(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\min\d+", "", readedData, 1)
                    if re.search(r"^\\sec\d+", readedData) != None:
                        timeDic["sec"] = re.search(r"\\sec(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\sec\d+", "", readedData, 1)
                    currentObject.infoDic["revtim"] = timeDic
                if re.search(r"^\\printim", readedData) != None:
                    readedData = re.sub(r"\\printim", "", readedData, 1)
                    timeDic = {}
                    if re.search(r"^\\yr\d+", readedData) != None:
                        timeDic["yr"] = re.search(r"\\yr(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\yr\d+", "", readedData, 1)
                    if re.search(r"^\\mo\d+", readedData) != None:
                        timeDic["mo"] = re.search(r"\\mo(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\mo\d+", "", readedData, 1)
                    if re.search(r"^\\dy\d+", readedData) != None:
                        timeDic["dy"] = re.search(r"\\dy(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\dy\d+", "", readedData, 1)
                    if re.search(r"^\\hr\d+", readedData) != None:
                        timeDic["hr"] = re.search(r"\\hr(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\hr\d+", "", readedData, 1)
                    if re.search(r"^\\min\d+", readedData) != None:
                        timeDic["min"] = re.search(r"\\min(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\min\d+", "", readedData, 1)
                    if re.search(r"^\\sec\d+", readedData) != None:
                        timeDic["sec"] = re.search(r"\\sec(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\sec\d+", "", readedData, 1)
                    currentObject.infoDic["printim"] = timeDic
                if re.search(r"^\\buptim", readedData) != None:
                    readedData = re.sub(r"\\buptim", "", readedData, 1)
                    timeDic = {}
                    if re.search(r"^\\yr\d+", readedData) != None:
                        timeDic["yr"] = re.search(r"\\yr(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\yr\d+", "", readedData, 1)
                    if re.search(r"^\\mo\d+", readedData) != None:
                        timeDic["mo"] = re.search(r"\\mo(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\mo\d+", "", readedData, 1)
                    if re.search(r"^\\dy\d+", readedData) != None:
                        timeDic["dy"] = re.search(r"\\dy(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\dy\d+", "", readedData, 1)
                    if re.search(r"^\\hr\d+", readedData) != None:
                        timeDic["hr"] = re.search(r"\\hr(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\hr\d+", "", readedData, 1)
                    if re.search(r"^\\min\d+", readedData) != None:
                        timeDic["min"] = re.search(r"\\min(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\min\d+", "", readedData, 1)
                    if re.search(r"^\\sec\d+", readedData) != None:
                        timeDic["sec"] = re.search(r"\\sec(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\sec\d+", "", readedData, 1)
                    currentObject.infoDic["buptim"] = timeDic
                readedData = re.sub(r"\}(\x0D\x0A)?", "", readedData, 1)
            else:
                if re.search(r"^\\version\d+", readedData) != None:
                    currentObject.infoDic["version"] = re.search(r"\\version(\d+)", readedData).group(1)
                    readedData = re.sub(r"\\version(\d+)", "", readedData, 1)
                if re.search(r"^\\vern\d+", readedData) != None:
                    currentObject.infoDic["vern"] = re.search(r"\\vern(\d+)", readedData).group(1)
                    readedData = re.sub(r"\\vern(\d+)", "", readedData, 1)
                if re.search(r"^\\edmins\d+", readedData) != None:
                    currentObject.infoDic["edmins"] = re.search(r"\\edmins(\d+)", readedData).group(1)
                    readedData = re.sub(r"\\edmins(\d+)", "", readedData, 1)
                if re.search(r"^\\nofpages\d+", readedData) != None:
                    currentObject.infoDic["nofpages"] = re.search(r"\\nofpages(\d+)", readedData).group(1)
                    readedData = re.sub(r"\\nofpages(\d+)", "", readedData, 1)
                if re.search(r"^\\nofwords\d+", readedData) != None:
                    currentObject.infoDic["nofwords"] = re.search(r"\\nofwords(\d+)", readedData).group(1)
                    readedData = re.sub(r"\\nofwords(\d+)", "", readedData, 1)
                if re.search(r"^\\nofchars\d+", readedData) != None:
                    currentObject.infoDic["nofchars"] = re.search(r"\\nofchars(\d+)", readedData).group(1)
                    readedData = re.sub(r"\\nofchars(\d+)", "", readedData, 1)
                if re.search(r"^\\id\d+", readedData) != None:
                    currentObject.infoDic["id"] = re.search(r"\\id(\d+)", readedData).group(1)
                    readedData = re.sub(r"\\id(\d+)", "", readedData, 1)
            #print "protacim cyklus"
        readedData = re.sub(r"^\}(\x0D\x0A)?", "", readedData, 1)
        #print currentObject.infoDic
        retArray.append(readedData)
        retArray.append(xml)
        return retArray
    
    #Metoda parsujici List Override Table v Header
    #@param1 objekt, do ktereho by se pripadne ukladaly informace
    #@param2 nacteny RTF soubor
    #@return1 nenaparsovana cast RTF souboru
    #@return2 cast xml vystupu
    def ListOverrideTable(self, currentObject, readedData):
        xml = ""
        retArray = []
        
        #print readedData
        #sys.exit(0)
        while True:
            if readedData[0] == '}':
                break
            readedData = re.sub(r"^\{", "", readedData, 1)
            listOverrideTableDic = {}
            while True:
                #print "listOverrideTable"
                #print readedData
                if readedData[0] == "}":
                    break
                if re.search(r"^\\listoverride", readedData) != None:
                    readedData = re.sub(r"\\listoverride", "", readedData, 1)
                    listOverrideTableDic["listoverride"] = 1
                if re.search(r"^\\listid\d+", readedData) != None:
                    value = re.search(r"^\\listid(\d+)", readedData).group(1)
                    readedData = re.sub(r"\\listid\d+", "", readedData, 1)
                    listOverrideTableDic["listid"] = value
                if re.search(r"^\\listoverridecount\d+", readedData) != None:
                    value = re.search(r"^\\listoverridecount(\d+)", readedData).group(1)
                    readedData = re.sub(r"\\listoverridecount\d+", "", readedData, 1)
                    listOverrideTableDic["listoverridecount"] = value
                if re.search(r"^\\ls\d+", readedData) != None:
                    value = re.search(r"^\\ls(\d+)", readedData).group(1)
                    readedData = re.sub(r"\\ls\d+", "", readedData, 1)
                    listOverrideTableDic["ls"] = value
                if re.search(r"^\{", readedData, 1) != None:
                    readedData = re.sub(r"\{", "", readedData, 1)
                    if re.search(r"\\lfolevel", readedData) != None:
                        readedData = re.sub(r"\\lfolevel", "", readedData, 1)
                        listOverrideTableDic["lfolevel"] = 1
                    if re.search(r"^\\listoverrideformat\d+", readedData) != None:
                        value = re.search(r"^\\listoverrideformat(\d+)", readedData).group(1)
                        readedData = re.sub(r"\\listoverrideformat\d+", "", readedData, 1)
                        listOverrideTableDic["listoverrideformat"] = value
                    if re.search(r"\\listoverridestartat", readedData) != None:
                        readedData = re.sub(r"\\listoverridestartat", "", readedData, 1)
                        listOverrideTableDic["listoverridestartat"] = 1
                    if re.search("^\{", readedData) != None:
                        listlevel = {}
                        while True:
                            if readedData[0] != '{':
                                break
                            listReadedData = re.search(r"[^\}]+\}", readedData).group(0)
                            readedData = re.sub(r"[^\}]+\}", "", readedData, 1)
                            while re.search(r";\}$", listReadedData) != None:
                                listReadedData += re.search(r"[^\}]+\}", readedData).group(0)
                                readedData = re.sub(r"[^\}]+\}", "", readedData, 1)
                                
                            listReadedData = re.sub(r"\{\\listlevel", "", listReadedData, 1)
                            #<number>
                            if re.search(r"^\\levelnfc\d+", listReadedData) != None:
                                value = re.search(r"^\\levelnfc(\d+)", listReadedData).group(1)
                                listlevel["levelnfc"] = value
                                listReadedData = re.sub(r"^\\levelnfc\d+", "", listReadedData, 1)
                            elif re.search(r"^\\levelnfcn\d+", listReadedData) != None:
                                value = re.search(r"^\\levelnfcn(\d+)", listReadedData).group(1)
                                listlevel["levelnfcn"] = value
                                listReadedData = re.sub(r"^\\levelnfcn\d+", "", listReadedData, 1)
                            while True:
                                if listReadedData[0] == '}':
                                    break
                                #<justification>
                                if re.search("\\leveljc\d+", listReadedData) != None:
                                    value = re.search(r"^\\leveljc(\d+)", listReadedData).group(1)
                                    listlevel["leveljc"] = value
                                    listReadedData = re.sub(r"^\\leveljc\d+", "", listReadedData, 1)
                                elif re.search("\\leveljcn\d+", listReadedData) != None:
                                    value = re.search(r"^\\leveljcn(\d+)", listReadedData).group(1)
                                    listlevel["leveljcn"] = value
                                    listReadedData = re.sub(r"^\\leveljcn\d+", "", listReadedData, 1)
                                #\levelfollowN
                                if re.search(r"\\levelfollow\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levelfollow(\d+)", listReadedData).group(1)
                                    listlevel["levelfollow"] = value
                                    listReadedData = re.sub(r"^\\levelfollow\d+", "", listReadedData, 1)
                                if re.search(r"\\levelstartat\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levelstartat(\d+)", listReadedData).group(1)
                                    listlevel["levelstartat"] = value
                                    listReadedData = re.sub(r"^\\levelstartat\d+", "", listReadedData, 1)
                                if re.search(r"\\lvltentative", listReadedData) !=None:
                                    listlevel["lvltentative"] = 1
                                    listReadedData = re.sub(r"^\\lvltentative", "", listReadedData, 1)
                                if re.search(r"\\levelold\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levelold(\d+)", listReadedData).group(1)
                                    listlevel["levelold"] = value
                                    listReadedData = re.sub(r"^\\levelold\d+", "", listReadedData, 1)
                                if re.search(r"\\levelprev\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levelprev(\d+)", listReadedData).group(1)
                                    listlevel["levelprev"] = value
                                    listReadedData = re.sub(r"^\\levelprev\d+", "", listReadedData, 1)
                                if re.search(r"\\levelprevspace\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levelprevspace(\d+)", listReadedData).group(1)
                                    listlevel["levelprevspace"] = value
                                    listReadedData = re.sub(r"^\\levelprevspace\d+", "", listReadedData, 1)
                                if re.search(r"\\levelspace\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levelspace(\d+)", listReadedData).group(1)
                                    listlevel["levelspace"] = value
                                    listReadedData = re.sub(r"^\\levelspace\d+", "", listReadedData, 1)
                                if re.search(r"\\levelindent\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levelindent(\d+)", listReadedData).group(1)
                                    listlevel["levelindent"] = value
                                    listReadedData = re.sub(r"^\\levelindent\d+", "", listReadedData, 1)
                                    #<leveltext>
                                if re.search(r"^\{\\leveltext", listReadedData) != None:
                                    listReadedData = re.sub(r"^\{\\leveltext", "", listReadedData, 1)
                                    if re.search(r"^\\leveltemplateid", listReadedData) != None:
                                        listReadedData = re.sub(r"^\\leveltemplateid", "", listReadedData, 1)
                                        listlevel["leveltemplateid"] = 1
                                    listlevel["leveltext"] = re.search(r"^(\w+\s*)+", listReadedData).group(0)
                                    listReadedData = re.sub(r"^(\w+\s*)+", "", listReadedData, 1)
                                    listReadedData = re.sub(r"^;\}", "", listReadedData, 1)
                                #<levelnumbers>
                                if re.search(r"^\{\\levelnumbers", listReadedData) != None:
                                    listReadedData = re.sub(r"^\{\\levelnumbers", "", listReadedData, 1)
                                    listlevel["levelnumbers"] = re.search(r"^(\w+\s*)+", listReadedData).group(0)
                                    listReadedData = re.sub(r"^(\w+\s*)+", "", listReadedData, 1)
                                    listReadedData = re.sub(r"^;\}", "", listReadedData, 1)
                                if re.search(r"\\levellegal\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levellegal(\d+)", listReadedData).group(1)
                                    listlevel["levellegal"] = value
                                    listReadedData = re.sub(r"^\\levellegal\d+", "", listReadedData, 1)
                                if re.search(r"\\levelnorestart\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levelnorestart(\d+)", listReadedData).group(1)
                                    listlevel["levelnorestart"] = value
                                    listReadedData = re.sub(r"^\\levelnorestart\d+", "", listReadedData, 1)
                                #<chrfmt>
                                #zatim neimplementovano
                                if re.search(r"\\levelpicture\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levelpicture(\d+)", listReadedData).group(1)
                                    listlevel["levelpicture"] = value
                                    listReadedData = re.sub(r"^\\levelpicture\d+", "", listReadedData, 1)
                                if re.search(r"\\li\d+", listReadedData) !=None:
                                    value = re.search(r"^\\li(\d+)", listReadedData).group(1)
                                    listlevel["li"] = value
                                    listReadedData = re.sub(r"^\\li\d+", "", listReadedData, 1)
                                if re.search(r"\\fi\d+", listReadedData) !=None:
                                    value = re.search(r"^\\fi(\d+)", listReadedData).group(1)
                                    listlevel["fi"] = value
                                    listReadedData = re.sub(r"^\\fi\d+", "", listReadedData, 1)
                                if re.search(r"\\lin\d+", listReadedData) !=None:
                                    value = re.search(r"^\\lin(\d+)", listReadedData).group(1)
                                    listlevel["lin"] = value
                                    listReadedData = re.sub(r"^\\lin\d+", "", listReadedData, 1)
                                if re.search(r"\\jclisttab\\tx\d+", listReadedData) !=None:
                                    value = re.search(r"^\\jclisttab\\tx(\d+)", listReadedData).group(1)
                                    listlevel["tx"] = value
                                    listlevel["jclisttab"] = 1
                                    listReadedData = re.sub(r"^\\jclisttab\\tx\d+", "", listReadedData, 1)
                            listOverrideTableDic["listlevel"] = listlevel
                            listReadedData = re.sub(r"^(\x0D\x0A)?\}(\x0D\x0A)?", "", listReadedData, 1)
            readedData = re.sub(r"^(\x0D\x0A)?\}(\x0D\x0A)?", "", readedData, 1)
            currentObject.listOverrideTable.append(listOverrideTableDic)
        readedData = re.sub(r"^(\x0D\x0A)?\}(\x0D\x0A)?", "", readedData, 1)
        #currentObject.listOverrideTableDic = listOverrideTableDic
        #print currentObject.listOverrideTable
        retArray.append(readedData)
        retArray.append(xml)
        return retArray
    
    #Metoda parsujici List Table v Header
    #@param1 objekt, do ktereho by se pripadne ukladaly informace
    #@param2 nacteny RTF soubor
    #@return1 nenaparsovana cast RTF souboru
    #@return2 cast xml vystupu
    def ListTable(self, currentObject, readedData):
        xml = ""
        retArray = []
        
        #re.purge()
        #<listpicture>?
        if re.search(r"^\{\\\*\\listpicture", readedData) != None:
            readedData = re.sub(r"\{\\\*\\listpicture", "", readedData, 1)
            #<shppictlist>
            #nenalezeno ve specifikaci 1.9.1
        #<list>+
        list = {}

        while True:
            #\list
            #print "list"
            #print readedData[10]
            if re.search(r"^\{\\list", readedData) != None:
                readedData = re.sub(r"\{\\list", "", readedData, 1)
                #readedData = re.sub(r"^\\listtemplateid", "", readedData, 1)
                #print readedData
                while True:
                    sys.stderr.write(readedData[:32]+"\n")
                    #print "Telo list"
                    #sys.stderr.write(readedData[:10]+"\n")
                    if re.search(r"^\{\\list\\", readedData) != None:
                        break
                    if re.search(r"^\}", readedData) != None:
                        #print "Break ktery potrebujes"
                        break
                    if re.search(r"^\\}", readedData) != None:
                        readedData = re.sub(r"^\\}", "", readedData, 1)
                    #print "readedData"
                    #print "\""+readedData+"\""
                    if re.search(r"^\\listtemplateid(\d+)", readedData) != None:
                        #print "J"
                        list["listtemplateid"] = re.search(r"^\\listtemplateid(\d+)", readedData).group(1)
                        #print list["listtemplateid"]
                        readedData = re.sub(r"\\listtemplateid\d+", "", readedData, 1)
                        #print "readedData"
                        #print readedData
                    elif re.search(r"^(\\listsimple|\\listhybrid)", readedData) != None:
                        if re.search(r"^\\listsimple", readedData) != None:
                            readedData = re.sub(r"^\\listsimple", "", readedData, 1)
                            list["listsimple"] = 1
                        else:
                            readedData = re.sub(r"^\\listhybrid", "", readedData, 1)
                            list["listhybrid"] = 1
                    #<listlevel>
                    elif re.search(r"^\{", readedData) != None:
                        listlevel = {}
                        #print "tady"
                        #print readedData
                        while True:
                            #sys.stderr.write(readedData[:10]+"\n")
                            if readedData[0] != '{':
                                break
                            listReadedData = re.search(r"[^\}]*\}", readedData).group(0)
                            if re.search(r"^\{\\listname", listReadedData) != None:
                                break
                            readedData = re.sub(r"[^\}]*\}", "", readedData, 1)
                            while re.search(r";\}$", listReadedData) != None:
                                listReadedData += re.search(r"[^\}]*\}", readedData).group(0)
                                readedData = re.sub(r"[^\}]*\}", "", readedData, 1)
                            #readedData = re.sub(r"^(\x0D\x0A)", "", readedData, 1)
                            #print readedData
                            #print readedData
                            listReadedData = re.sub(r"\{\\listlevel", "", listReadedData, 1)
                            #<number>
                            while True:
                                #sys.stderr.write(listReadedData[:10]+"\n")
                                if re.search(r"^\\(levelnfc|levelnfcn)", listReadedData) == None:
                                    break
                                if re.search(r"^\\levelnfc\d+", listReadedData) != None:
                                    value = re.search(r"^\\levelnfc(\d+)", listReadedData).group(1)
                                    listlevel["levelnfc"] = value
                                    listReadedData = re.sub(r"^\\levelnfc\d+", "", listReadedData, 1)
                                elif re.search(r"^\\levelnfcn\d+", listReadedData) != None:
                                    value = re.search(r"^\\levelnfcn(\d+)", listReadedData).group(1)
                                    listlevel["levelnfcn"] = value
                                    listReadedData = re.sub(r"^\\levelnfcn\d+", "", listReadedData, 1)
                            #print "listReadedData"
                            #print listReadedData
                            while True:
                                #sys.stderr.write(listReadedData[:10]+"\n")
                                if listReadedData[0] == '}':
                                    #print "break"
                                    break
                                #print "listReadedData"
                                #print listReadedData
                                #<justification>
                                if re.search(r"^\\leveljc\d+", listReadedData) != None:
                                    value = re.search(r"^\\leveljc(\d+)", listReadedData).group(1)
                                    listlevel["leveljc"] = value
                                    listReadedData = re.sub(r"^\\leveljc\d+", "", listReadedData, 1)
                                elif re.search(r"^\\leveljcn\d+", listReadedData) != None:
                                    value = re.search(r"^\\leveljcn(\d+)", listReadedData).group(1)
                                    listlevel["leveljcn"] = value
                                    listReadedData = re.sub(r"^\\leveljcn\d+", "", listReadedData, 1)
                                #\levelfollowN
                                if re.search(r"^\\levelfollow\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levelfollow(\d+)", listReadedData).group(1)
                                    listlevel["levelfollow"] = value
                                    listReadedData = re.sub(r"^\\levelfollow\d+", "", listReadedData, 1)
                                if re.search(r"^\\levelstartat\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levelstartat(\d+)", listReadedData).group(1)
                                    listlevel["levelstartat"] = value
                                    listReadedData = re.sub(r"^\\levelstartat\d+", "", listReadedData, 1)
                                if re.search(r"^\\lvltentative", listReadedData) !=None:
                                    listlevel["lvltentative"] = 1
                                    listReadedData = re.sub(r"^\\lvltentative", "", listReadedData, 1)
                                if re.search(r"^\\levelold\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levelold(\d+)", listReadedData).group(1)
                                    listlevel["levelold"] = value
                                    listReadedData = re.sub(r"^\\levelold\d+", "", listReadedData, 1)
                                if re.search(r"^\\levelprev\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levelprev(\d+)", listReadedData).group(1)
                                    listlevel["levelprev"] = value
                                    listReadedData = re.sub(r"^\\levelprev\d+", "", listReadedData, 1)
                                if re.search(r"^\\levelprevspace\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levelprevspace(\d+)", listReadedData).group(1)
                                    listlevel["levelprevspace"] = value
                                    listReadedData = re.sub(r"^\\levelprevspace\d+", "", listReadedData, 1)
                                if re.search(r"^\\levelspace\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levelspace(\d+)", listReadedData).group(1)
                                    listlevel["levelspace"] = value
                                    listReadedData = re.sub(r"^\\levelspace\d+", "", listReadedData, 1)
                                if re.search(r"^\\levelindent\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levelindent(\d+)", listReadedData).group(1)
                                    listlevel["levelindent"] = value
                                    listReadedData = re.sub(r"^\\levelindent\d+", "", listReadedData, 1)
                                #<leveltext>
                                if re.search(r"^\{\\leveltext", listReadedData) != None:
                                    listReadedData = re.sub(r"^\{\\leveltext", "", listReadedData, 1)
                                    if re.search(r"^\\leveltemplateid", listReadedData) != None:
                                        listlevel["leveltemplateid"] = re.search(r"\\leveltemplateid(\d+)", listReadedData).group(1)
                                        listReadedData = re.sub(r"^\\leveltemplateid\d+", "", listReadedData, 1)
                                    listlevel["leveltext"] = re.search(r"^\s([^;]+)", listReadedData).group(1)
                                    #print listlevel["leveltext"]
                                    listReadedData = re.sub(r"^[^;]+", "", listReadedData, 1)
                                    listReadedData = re.sub(r"^;\}", "", listReadedData, 1)
                                #<levelnumbers>
                                if re.search(r"^\{\\levelnumbers", listReadedData) != None:
                                    listReadedData = re.sub(r"^\{\\levelnumbers", "", listReadedData, 1)
                                    try:
                                        listlevel["levelnumbers"] = re.search(r"^\s([^;]*)", listReadedData).group(1)
                                    except AttributeError:
                                        print readedData
                                        sys.exit(0)
                                    #print listlevel["levelnumbers"]
                                    listReadedData = re.sub(r"^[^;]*", "", listReadedData, 1)
                                    listReadedData = re.sub(r"^;\}", "", listReadedData, 1)
                                if re.search(r"^\\levellegal\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levellegal(\d+)", listReadedData).group(1)
                                    listlevel["levellegal"] = value
                                    listReadedData = re.sub(r"^\\levellegal\d+", "", listReadedData, 1)
                                if re.search(r"^\\levelnorestart\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levelnorestart(\d+)", listReadedData).group(1)
                                    listlevel["levelnorestart"] = value
                                    listReadedData = re.sub(r"^\\levelnorestart\d+", "", listReadedData, 1)
                                #<chrfmt>
                                if re.search(r"^\\lang\d+", listReadedData) !=None:
                                    value = re.search(r"^\\lang(\d+)", listReadedData).group(1)
                                    listlevel["lang"] = value
                                    listReadedData = re.sub(r"^\\lang\d+", "", listReadedData, 1)
                                if re.search(r"^\\langfe\d+", listReadedData) !=None:
                                    value = re.search(r"^\\langfe(\d+)", listReadedData).group(1)
                                    listlevel["langfe"] = value
                                    listReadedData = re.sub(r"^\\langfe\d+", "", listReadedData, 1)
                                if re.search(r"^\\f\d+", listReadedData) !=None:
                                    value = re.search(r"^\\f(\d+)", listReadedData).group(1)
                                    listlevel["f"] = value
                                    listReadedData = re.sub(r"^\\f\d+", "", listReadedData, 1)
                                if re.search(r"^\\fs\d+", listReadedData) !=None:
                                    value = re.search(r"^\\fs(\d+)", listReadedData).group(1)
                                    listlevel["fs"] = value
                                    listReadedData = re.sub(r"^\\fs\d+", "", listReadedData, 1)
                                if re.search(r"^\\afs\d+", listReadedData) !=None:
                                    value = re.search(r"^\\afs(\d+)", listReadedData).group(1)
                                    listlevel["afs"] = value
                                    listReadedData = re.sub(r"^\\afs\d+", "", listReadedData, 1)
                                if re.search(r"^\\charscalex\d+", listReadedData) !=None:
                                    value = re.search(r"^\\charscalex(\d+)", listReadedData).group(1)
                                    listlevel["charscalex"] = value
                                    listReadedData = re.sub(r"^\\charscalex\d+", "", listReadedData, 1)
                                if re.search(r"^\\expndtw(\-)?\d+", listReadedData) !=None:
                                    value = re.search(r"^\\expndtw((\-)?\d+)", listReadedData).group(1)
                                    listlevel["expndtw"] = value
                                    listReadedData = re.sub(r"^\\expndtw(\-)?\d+", "", listReadedData, 1)
                                if re.search(r"^\\cf\d+", listReadedData) !=None:
                                    value = re.search(r"^\\cf(\d+)", listReadedData).group(1)
                                    listlevel["cf"] = value
                                    listReadedData = re.sub(r"^\\cf\d+", "", listReadedData, 1)
                                if re.search(r"^\\super", listReadedData) !=None:
                                    listlevel["super"] = 1
                                    listReadedData = re.sub(r"^\\super", "", listReadedData, 1)
                                if re.search(r"^\\dn\d+", listReadedData) !=None:
                                    value = re.search(r"^\\dn(\d+)", listReadedData).group(1)
                                    listlevel["dn"] = value
                                    listReadedData = re.sub(r"^\\dn\d+", "", listReadedData, 1)
                                if re.search(r"^\\b(\d+)?", listReadedData) !=None:
                                    if re.search(r"^\\b\d+", listReadedData) != None:
                                        value = re.search(r"^\\b(\d+)", listReadedData).group(1)
                                        listlevel["b"] = value
                                    else:
                                        listlevel["b"] = 1
                                    listReadedData = re.sub(r"^\\b(\d+)?", "", listReadedData, 1)
                                if re.search(r"^\\i(\d+)?", listReadedData) !=None:
                                    if re.search(r"^\\i\d+", listReadedData) != None:
                                        value = re.search(r"^\\i(\d+)", listReadedData).group(1)
                                        listlevel["i"] = value
                                    else:
                                        listlevel["i"] = 1
                                    listReadedData = re.sub(r"^\\i(\d+)?", "", listReadedData, 1)
                                if re.search(r"^\\ul(\d+)?", listReadedData) !=None:
                                    if re.search(r"^\\ul\d+", listReadedData) != None:
                                        value = re.search(r"^\\ul(\d+)", listReadedData).group(1)
                                        listlevel["ul"] = value
                                    else:
                                        listlevel["ul"] = 1
                                    listReadedData = re.sub(r"^\\ul(\d+)?", "", listReadedData, 1)
                                if re.search(r"^\\strike(\d+)?", listReadedData) !=None:
                                    if re.search(r"^\\strike\d+", listReadedData) != None:
                                        value = re.search(r"^\\strike(\d+)", listReadedData).group(1)
                                        listlevel["strike"] = value
                                    else:
                                        listlevel["strike"] = 1
                                    listReadedData = re.sub(r"^\\strike(\d+)?", "", listReadedData, 1)
                                if re.search(r"^\\scaps(\d+)?", listReadedData) !=None:
                                    if re.search(r"^\\scaps\d+", listReadedData) != None:
                                        value = re.search(r"^\\scaps(\d+)", listReadedData).group(1)
                                        listlevel["scaps"] = value
                                    else:
                                        listlevel["scaps"] = 1
                                    listReadedData = re.sub(r"^\\scaps(\d+)?", "", listReadedData, 1)
                                #</chrfmt>
                                if re.search(r"^\\levelpicture\d+", listReadedData) !=None:
                                    value = re.search(r"^\\levelpicture(\d+)", listReadedData).group(1)
                                    listlevel["levelpicture"] = value
                                    listReadedData = re.sub(r"^\\levelpicture\d+", "", listReadedData, 1)
                                if re.search(r"^\\li\d+", listReadedData) !=None:
                                    value = re.search(r"^\\li(\d+)", listReadedData).group(1)
                                    listlevel["li"] = value
                                    listReadedData = re.sub(r"^\\li\d+", "", listReadedData, 1)
                                if re.search(r"^\\fi\d+", listReadedData) !=None:
                                    value = re.search(r"^\\fi(\d+)", listReadedData).group(1)
                                    listlevel["fi"] = value
                                    listReadedData = re.sub(r"^\\fi\d+", "", listReadedData, 1)
                                if re.search(r"^\\lin\d+", listReadedData) !=None:
                                    value = re.search(r"^\\lin(\d+)", listReadedData).group(1)
                                    listlevel["lin"] = value
                                    listReadedData = re.sub(r"^\\lin\d+", "", listReadedData, 1)
                                if re.search(r"^\\jclisttab\\tx\d+", listReadedData) !=None:
                                    value = re.search(r"^\\jclisttab\\tx(\d+)", listReadedData).group(1)
                                    listlevel["tx"] = value
                                    listlevel["jclisttab"] = 1
                                    listReadedData = re.sub(r"^\\jclisttab\\tx\d+", "", listReadedData, 1)
                            list["listlevel"] = listlevel
                            listReadedData = re.sub(r"^\}", "", listReadedData, 1)
                        #print "readedData"
                        #print readedData
                    if re.search(r"^\\listrestarthnd", readedData) !=None:
                        list["listrestarthnd"] = 1
                        readedData = re.sub(r"^\\listrestarthnd", "", readedData, 1)
                    if re.search(r"^\\listid\d+", readedData) !=None:
                        value = re.search(r"^\\listid(\d+)", readedData).group(1)
                        listlevel["listid"] = value
                        readedData = re.sub(r"^\\listid\d+\}", "", readedData, 1)
                    #print "test"
                    #print readedData
                    if re.search(r"^\\listname", readedData) !=None:
                        value = re.search(r"^\\listname\s+((\w+\s*)+)", readedData).group(1)
                        listlevel["listname"] = value
                        readedData = re.sub(r"^\\listname\s+((\w+\s*)+)", "", readedData, 1)
                    elif re.search(r"^\{\\listname\s", readedData) != None:
                        #print "J"
                        readedData = re.sub(r"^\{\\listname\s", "", readedData, 1)
                        if re.search(r"^[^;]+", readedData) == None:
                            listlevel["listname"] = ""
                        else:
                            listlevel["listname"] = re.search(r"^[^;]+", readedData).group(0)
                        readedData = re.sub(r"^[^;]*;\}", "", readedData, 1)
                    if re.search(r"^\\liststyleid\d+", readedData) !=None:
                        value = re.search(r"^\\liststyleid(\d+)", readedData).group(1)
                        listlevel["liststyleid"] = value
                        readedData = re.sub(r"^\\liststyleid\d+", "", readedData, 1)
                    if re.search(r"^\\liststylename", readedData) !=None:
                        listlevel["liststylename"] = 1
                        readedData = re.sub(r"^\\liststylename", "", readedData, 1)
                    #print "protacim cyklus"
                    #print readedData
                    #sys.exit(0)
                currentObject.listTable.append(list)
                if re.search(r"^\\}", readedData) != None:
                    readedData = re.sub(r"^\\}", "", readedData, 1)
            else:
                break
        readedData = re.sub(r"^\}", "", readedData, 1)
        retArray.append(readedData)
        retArray.append(xml)
        return retArray
    
    #Metoda parsujici Style Sheet v Header
    #@param1 objekt, do ktereho by se pripadne ukladaly informace
    #@param2 nacteny RTF soubor
    #@return1 nenaparsovana cast RTF souboru
    #@return2 cast xml vystupu
    def StyleSheet(self, currentObject, readedData):
        xml = ""
        retArray = []
        
        while True:
            sys.stderr.write(readedData[:32]+"\n")
            if readedData[0] == '}':
                break
            styleSheetTableDic = {}
            readedData = re.sub(r"^\{", "", readedData, 1)
            stShReadedData = re.search(r"^[^;]+;\}", readedData).group(0)
            #print "stShReadedData"
            #print stShReadedData
            readedData = re.sub(r"^[^;]+;\}(\x0D\x0A)?", "", readedData, 1)
            #print "readedData"
            #print readedData
            #<styledef>?
            if re.search(r"^(\\s\d+|\\\*\\cs\d+|\\\*\\ds\d+|\\\*\\ts\d+\\tsrowd)", stShReadedData) != None:
                if re.search(r"^\\s", stShReadedData) != None:
                    stShReadedData = re.sub(r"\\s", "", stShReadedData, 1)
                    value = re.search(r"^\d+", stShReadedData).group(0)
                    styleSheetTableDic["s"] = value
                    stShReadedData = re.sub(r"\d+", "", stShReadedData, 1)
                elif re.search(r"^\\\*\\cs", stShReadedData) != None:
                    stShReadedData = re.sub(r"\\\*\\cs", "", stShReadedData, 1)
                    #print "cs"
                    #print stShReadedData
                    value = re.search(r"^\d+", stShReadedData).group(0)
                    styleSheetTableDic["cs"] = value
                    stShReadedData = re.sub(r"\d+", "", stShReadedData, 1)
                elif re.search(r"^\\\*\\ds", stShReadedData) != None:
                    stShReadedData = re.sub(r"\\\*\\ds", "", stShReadedData, 1)
                    value = re.search(r"^\d+", stShReadedData).group(0)
                    styleSheetTableDic["ds"] = value
                    stShReadedData = re.sub(r"\d+", "", stShReadedData, 1)
                elif re.search(r"^\\\*\\ts", stShReadedData) != None:
                    stShReadedData = re.sub(r"\\\*\\ts", "", stShReadedData, 1)
                    value = re.search(r"^\d+", stShReadedData).group(0)
                    styleSheetTableDic["ts"] = value
                    stShReadedData = re.sub(r"\d+", "", stShReadedData, 1)
                    stShReadedData = re.sub(r"\\tsrowd", "", stShReadedData, 1)
                    styleSheetTableDic["tsrowd"] = 1
            #<keycode>
            if re.search(r"^\{\\keycode", stShReadedData) != None:
                stShReadedData = re.sub(r"\{\\keycode(\x0D\x0A)?", "", stShReadedData, 1)
                #<keys>
                if re.search(r"\\shift", stShReadedData) != None:
                    stShReadedData = re.sub(r"\\shift", "", stShReadedData, 1)
                    styleSheetTableDic["shift"] = 1
                if re.search(r"\\ctrl", stShReadedData) != None:
                    stShReadedData = re.sub(r"\\ctrl", "", stShReadedData, 1)
                    styleSheetTableDic["ctrl"] = 1
                if re.search(r"\\alt", stShReadedData) != None:
                    stShReadedData = re.sub(r"\\alt", "", stShReadedData, 1)
                    styleSheetTableDic["alt"] = 1
                #<key>
                if re.search(r"^\\fn\d+", stShReadedData) != None:
                    stShReadedData = re.sub(r"\\fn", "", stShReadedData, 1)
                    value = re.search(r"\d+", stShReadedData).group(0)
                    styleSheetTableDic["fn"] = value
                else:
                    value = re.search(r"(\w+\s*)+", stShReadedData).group(0)
                    styleSheetTableDic["key"] = value
                    stShReadedData = re.sub(r"(\w+\s*)+", "", readedData, 1)
            #<formatting>
            while True:
                #print "stShReadedData"
                #print stShReadedData
                if re.search(r"^\\[a-zA-Z]+", stShReadedData) != None:
                    keyword = re.search(r"\\([a-zA-Z]+)", stShReadedData).group(1)
                    #print "stShReadedData"
                    #print stShReadedData
                    #print "keyword"
                    #print keyword
                    if currentObject.parfmt.has_key(keyword):
                        #print "vstupuji do parfmt"
                        stShReadedData = re.sub(r"\\[a-zA-Z]+(\x0D\x0A)?", "", stShReadedData, 1)
                        if keyword == "itap" or keyword == "level" or keyword == "outlinelevel" or keyword == "s":
                            styleSheetTableDic[keyword] = re.search(r"(\-)?\d+", stShReadedData).group(0)
                            stShReadedData = re.sub(r"(\-)?\d+(\x0D\x0A)?", "", stShReadedData, 1)
                        elif keyword == "li" or keyword == "ri" or keyword == "fi" or keyword == "sb" or keyword == "sa":
                            styleSheetTableDic[keyword] = re.search(r"(\-)?\d+", stShReadedData).group(0)
                            stShReadedData = re.sub(r"(\-)?\d+(\x0D\x0A)?", "", stShReadedData, 1)
                        elif keyword == "sl" or keyword == "slmult" or keyword == "lang" or keyword == "langfe" or keyword == "f":
                            styleSheetTableDic[keyword] = re.search(r"(\-)?\d+", stShReadedData).group(0)
                            stShReadedData = re.sub(r"(\-)?\d+(\x0D\x0A)?", "", stShReadedData, 1)
                        elif keyword == "fs" or keyword == "afs" or keyword == "charscalex" or keyword == "expndtw":
                            #print "stShReadedData"
                            #print stShReadedData
                            styleSheetTableDic[keyword] = re.search(r"(\-)?\d+", stShReadedData).group(0)
                            stShReadedData = re.sub(r"(\-)?\d+(\x0D\x0A)?", "", stShReadedData, 1)
                            #print "stShReadedData"
                            #print stShReadedData
                        else:
                            styleSheetTableDic[keyword] = 1
                    elif currentObject.apoctl.has_key(keyword):
                        stShReadedData = re.sub(r"\\[a-zA-Z]+(\x0D\x0A)?", "", stShReadedData, 1)
                        if keyword == "absw" or keyword == "absh" or keyword == "posx" or keyword == "posnegx" or keyword == "posy" or keyword == "posnegy" or keyword == "abslock" or keyword == "dxfrtext" or keyword == "dfrmtxtx" or keyword == "dfrmtxty" or keyword == "absnoovrlp":
                            styleSheetTableDic[keyword] = re.search(r"(\-)?\d+", stShReadedData).group(0)
                            stShReadedData = re.sub(r"(\-)?\d+(\x0D\x0A)?", "", stShReadedData, 1)
                        else:
                            styleSheetTableDic[keyword] = 1
                    elif currentObject.tabdef.has_key(keyword):
                        stShReadedData = re.sub(r"\\[a-zA-Z]+(\x0D\x0A)?", "", stShReadedData, 1)
                        if keyword == "tx" or keyword == "tb":
                            styleSheetTableDic[keyword] = re.search(r"(\-)?\d+", stShReadedData).group(0)
                            stShReadedData = re.sub(r"(\-)?\d+(\x0D\x0A)?", "", stShReadedData, 1)
                        else:
                            styleSheetTableDic[keyword] = 1
                    elif currentObject.shading.has_key(keyword):
                        stShReadedData = re.sub(r"\\[a-zA-Z]+(\x0D\x0A)?", "", stShReadedData, 1)
                        if keyword == "shading" or keyword == "cfpat" or keyword == "cbpat":
                            styleSheetTableDic[keyword] = re.search(r"(\-)?\d+", stShReadedData).group(0)
                            stShReadedData = re.sub(r"(\-)?\d+(\x0D\x0A)?", "", stShReadedData, 1)
                        else:
                            styleSheetTableDic[keyword] = 1
                    elif currentObject.chrfmt.has_key(keyword):
                        #print keyword
                        stShReadedData = re.sub(r"\\[a-zA-Z]+", "", stShReadedData, 1)
                        if keyword == "cf" or keyword == "dn" or keyword == "b" or keyword == "i" or keyword == "ul" or keyword == "strike" or keyword == "scaps":
                            if keyword == "b":
                                if re.search(r"^(\-)?\d+", stShReadedData) != None:
                                    styleSheetTableDic[keyword] = re.search(r"(\-)?\d+", stShReadedData).group(0)
                                    stShReadedData = re.sub(r"^(\-)?\d+", "", stShReadedData, 1)
                                else:
                                    styleSheetTableDic[keyword] = 1
                            elif keyword == "i":
                                if re.search(r"^(\-)?\d+", stShReadedData) != None:
                                    styleSheetTableDic[keyword] = re.search(r"(\-)?\d+", stShReadedData).group(0)
                                    stShReadedData = re.sub(r"^(\-)?\d+", "", stShReadedData, 1)
                                else:
                                    styleSheetTableDic[keyword] = 1
                            elif keyword == "ul":
                                if re.search(r"^(\-)?\d+", stShReadedData) != None:
                                    styleSheetTableDic[keyword] = re.search(r"(\-)?\d+", stShReadedData).group(0)
                                    stShReadedData = re.sub(r"^(\-)?\d+", "", stShReadedData, 1)
                                else:
                                    styleSheetTableDic[keyword] = 1
                            elif keyword == "strike":
                                if re.search(r"^(\-)?\d+", stShReadedData) != None:
                                    styleSheetTableDic[keyword] = re.search(r"(\-)?\d+", stShReadedData).group(0)
                                    stShReadedData = re.sub(r"^(\-)?\d+", "", stShReadedData, 1)
                                else:
                                    styleSheetTableDic[keyword] = 1
                            elif keyword == "scaps":
                                if re.search(r"^(\-)?\d+", stShReadedData) != None:
                                    styleSheetTableDic[keyword] = re.search(r"(\-)?\d+", stShReadedData).group(0)
                                    stShReadedData = re.sub(r"^(\-)?\d+", "", stShReadedData, 1)
                                else:
                                    styleSheetTableDic[keyword] = 1
                            else:
                                styleSheetTableDic[keyword] = re.search(r"(\-)?\d+", stShReadedData).group(0)
                                stShReadedData = re.sub(r"(\-)?\d+(\x0D\x0A)?", "", stShReadedData, 1)
                            #print "stShReadedData"
                            #print stShReadedData
                        else:
                            styleSheetTableDic[keyword] = 1
                    elif currentObject.brdrdef.has_key(keyword):
                        stShReadedData = re.sub(r"\\[a-zA-Z]+(\x0D\x0A)?", "", stShReadedData, 1)
                        if keyword == "brdrw" or keyword == "brsp" or keyword == "brdrcf":
                            styleSheetTableDic[keyword] = re.search(r"(\-)?\d+", stShReadedData).group(0)
                            stShReadedData = re.sub(r"(\-)?\d+(\x0D\x0A)?", "", stShReadedData, 1)
                        else:
                            styleSheetTableDic[keyword] = 1
                    #\additive?
                    elif re.search(r"\\additive", stShReadedData) != None:
                        styleSheetTableDic["additive"] = 1
                        stShReadedData = re.sub(r"\\additive", "", stShReadedData, 1)
                    #\sbasedon?
                    elif re.search(r"\\sbasedon\d+", stShReadedData) != None:
                        styleSheetTableDic["sbasedon"] = re.search(r"\\sbasedon(\d+)", stShReadedData).group(1)
                        stShReadedData = re.sub(r"\\sbasedon\d+", "", stShReadedData, 1)
                    #\snext?
                    elif re.search(r"\\snext\d+", stShReadedData) != None:
                        styleSheetTableDic["snext"] = re.search(r"\\snext(\d+)", stShReadedData).group(1)
                        stShReadedData = re.sub(r"\\snext\d+", "", stShReadedData, 1)
                    #\sautoudp?
                    elif re.search(r"\\sautoudp", stShReadedData) != None:
                        styleSheetTableDic["sautoudp"] = 1
                        stShReadedData = re.sub(r"\\sautoudp", "", stShReadedData, 1)
                    #slink?
                    elif re.search(r"\\slink\d+", stShReadedData) != None:
                        styleSheetTableDic["slink"] = re.search(r"\\slink(\d+)", stShReadedData).group(1)
                        stShReadedData = re.sub(r"\\slink\d+", "", stShReadedData, 1)
                    #\sqformat?
                    elif re.search(r"\\sqformat", stShReadedData) != None:
                        styleSheetTableDic["sqformat"] = 1
                        stShReadedData = re.sub(r"\\sqformat", "", stShReadedData, 1)
                    #spriority?
                    elif re.search(r"\\spriority\d+", stShReadedData) != None:
                        styleSheetTableDic["spriority"] = re.search(r"\\spriority(\d+)", stShReadedData).group(1)
                        stShReadedData = re.sub(r"\\spriority\d+", "", stShReadedData, 1)
                    #sunhideused?
                    elif re.search(r"\\sunhideused\d+", stShReadedData) != None:
                        styleSheetTableDic["sunhideused"] = re.search(r"\\sunhideused(\d+)", stShReadedData).group(1)
                        stShReadedData = re.sub(r"\\sunhideused\d+", "", stShReadedData, 1)
                    #\slocked?
                    elif re.search(r"\\slocked", stShReadedData) != None:
                        styleSheetTableDic["slocked"] = 1
                        stShReadedData = re.sub(r"\\slocked", "", stShReadedData, 1)
                    #\shidden?
                    elif re.search(r"\\shidden", stShReadedData) != None:
                        styleSheetTableDic["shidden"] = 1
                        stShReadedData = re.sub(r"\\shidden", "", stShReadedData, 1)
                    #ssemihidden?
                    elif re.search(r"\\ssemihidden\d+", stShReadedData) != None:
                        styleSheetTableDic["ssemihidden"] = re.search(r"\\ssemihidden(\d+)", stShReadedData).group(1)
                        stShReadedData = re.sub(r"\\ssemihidden\d+", "", stShReadedData, 1)
                    #\spersonal?
                    elif re.search(r"\\spersonal", stShReadedData) != None:
                        styleSheetTableDic["spersonal"] = 1
                        stShReadedData = re.sub(r"\\spersonal", "", stShReadedData, 1)
                    #\scompose?
                    elif re.search(r"\\scompose", stShReadedData) != None:
                        styleSheetTableDic["scompose"] = 1
                        stShReadedData = re.sub(r"\\scompose", "", stShReadedData, 1)
                    #\sreply?
                    elif re.search(r"\\sreply", stShReadedData) != None:
                        styleSheetTableDic["sreply"] = 1
                        stShReadedData = re.sub(r"\\sreply", "", stShReadedData, 1)
                    #styrsid?
                    elif re.search(r"\\styrsid\d+", stShReadedData) != None:
                        styleSheetTableDic["styrsid"] = re.search(r"\\styrsid(\d+)", stShReadedData).group(1)
                        stShReadedData = re.sub(r"\\styrsid\d+", "", stShReadedData, 1)
                    else:
                        break
                else:
                    break
            #<stylename>?
            if re.search(r"^ ?[^;]+", stShReadedData) != None:
                stShReadedData = re.sub(r" ", "", stShReadedData, 1)
                styleSheetTableDic["stylename"] = re.search(r"^[^;]+", stShReadedData).group(0)
                stShReadedData = re.sub(r"^[^;]+", "", stShReadedData, 1)
            stShReadedData = re.sub(r";\}(\x0D\x0A)?", "", stShReadedData, 1)
            currentObject.styleSheetTable.append(styleSheetTableDic)
            #print styleSheetTableDic
            #print " "
        #print readedData
        #print currentObject.styleSheetTable
        #sys.exit(0)
        readedData = re.sub(r"\}(\x0D\x0A)?", "", readedData, 1)
        retArray.append(readedData)
        retArray.append(xml)
        return retArray
    
    #Metoda parsujici Color Table v Header
    #@param1 objekt, do ktereho by se pripadne ukladaly informace
    #@param2 nacteny RTF soubor
    #@return1 nenaparsovana cast RTF souboru
    #@return2 cast xml vystupu
    def ColorTable(self, currentObject, readedData):
        xml = ""
        retArray = []
        
        id = 1
        #<colordef>+
        colorReadedData = re.search(r"[^\}]+\}", readedData).group(0)
        readedData = re.sub(r"^[^\}]+\}(\x0D\x0A)?", "", readedData, 1)
        colorReadedData = re.sub(r"\\colortbl;(\x0D\x0A)?", "", colorReadedData, 1)
        while True:
            if colorReadedData[0] == '}':
                break
            colorTableDic = {}
            strPart = re.search("^[^;]*;", colorReadedData).group(0)
            colorReadedData = re.sub(r"^[^;]*;(\x0D\x0A)?", "", colorReadedData, 1)
            #print strPart
            #print colorReadedData
            if re.search(r"\\red\d+", strPart) != None:
                red = re.search(r"\\red(\d+)", strPart).group(1)
            if re.search(r"\\green\d+", strPart) != None:
                green = re.search(r"\\green(\d+)", strPart).group(1)
            if re.search(r"\\blue\d+", strPart) != None:
                blue = re.search(r"\\blue(\d+)", strPart).group(1)
            redHex = re.sub(r"^0x", "", str(hex(int(red))))
            if len(redHex) < 2:
                redHex = "0"+redHex
            #print redHex
            greenHex = re.sub(r"^0x", "", str(hex(int(green))))
            if len(greenHex) < 2:
                greenHex = "0"+greenHex
            #print greenHex
            blueHex = re.sub(r"^0x", "", str(hex(int(blue))))
            if len(blueHex) < 2:
                blueHex = "0"+blueHex
            #print blueHex
            colorHex = "#" + redHex.upper() + greenHex.upper() + blueHex.upper()
            #print "colorHex"
            #print colorHex
            xml += "<item id=\"" + str(id) + "\" value=\"" + colorHex + "\"/>"
            colorTableDic["id"] = id
            colorTableDic["colorHex"] = colorHex
            currentObject.colorTable.append(colorTableDic)
            id += 1
            #print "colorReadedData"
            #print colorReadedData
        
        #print currentObject.colorTable
        retArray.append(readedData)
        retArray.append(xml)
        return retArray
        
    #Metoda parsujici Font Table v Header
    #@param1 objekt, do ktereho by se pripadne ukladaly informace
    #@param2 nacteny RTF soubor
    #@return1 nenaparsovana cast RTF souboru
    #@return2 cast xml vystupu
    def FontInfo(self, currentObject, readedData):
        xml = ""
        retArray = []
        
        #print readedData
        #sys.exit(0)
        #vychozi nastaveni je, ze kazda polozka tabulky bude podskupina
        #{<fontinfo>}
        subGroup = True
        #<fontinfo>
        #print readedData
        #sys.exit(0)
        if re.search(r"^[^\{]", readedData) != None:
            subGroup = False
        while True:
            fontInfoDic = {}
            if readedData[0] == '}':
                break
            if subGroup:
                readedData = re.sub(r"\{", "", readedData, 1)
            #<themefont>?
            if re.search(r"(\\flomajor|\\fhimajor|\\fdbmajor|\\fbimajor|\\flominor|\\fhiminor|\\fdbminor|\\fbiminor)", readedData) != None:
                readedData = re.sub(r"\\\w+(\x0D\x0A)?", "", readedData, 1)
            #\fN
            id = re.search(r"\\f(\d+)", readedData)
            fontInfoDic["id"] = id.group(1)
            xml += "<item id=\"" + id.group(1) + "\" "
            readedData = re.sub(r"\\f\d+(\x0D\x0A)?", "", readedData, 1)
            #<fontfamily>
            if re.search(r"(\\fnil|\\froman|\\fswiss|\\fmodern|\\fscript|\\fdecor|\\ftech|\\fbidi)", readedData) != None:
                fontInfoDic["fontFamily"] = re.search(r"(\\fnil|\\froman|\\fswiss|\\fmodern|\\fscript|\\fdecor|\\ftech|\\fbidi)", readedData).group(0)
                fontInfoDic["fontFamily"] = re.sub(r"^\\", "", fontInfoDic["fontFamily"] , 1)
                readedData = re.sub(r"\\\w+(\x0D\x0A)?", "", readedData, 1)
            else:
                sys.stderr.write("Chyba: Spatny format RTF\n")
                sys.exit(1)
            #\fcharsetN?
            if re.search(r"\\fcharset\d+", readedData) != None:
                readedData = re.sub(r"\\fcharset\d+(\x0D\x0A)?", "", readedData, 1)
            #\fprq?
            if re.search(r"\\fprq", readedData) != None:
                readedData = re.sub(r"\\fprq(\x0D\x0A)?", "", readedData, 1)
            #<panose>?
            if re.search(r"\{\\\*\\panose", readedData) != None:
                readedData = re.sub(r"\{\\\*\\panose[^\}]+\}(\x0D\x0A)?", "", readedData, 1)
            #<nontaggedname>?
            if re.search(r"\{\\\*\\fname", readedData) != None:
                readedData = re.sub(r"\{\\\*\\panose[^\}]+;\}(\x0D\x0A)?", "", readedData, 1)
            #<fontemb>?
            if re.search(r"\{\\\*\\fontemb", readedData) != None:
                readedData = re.sub(r"\{\\\*\\fontemb([^\}]+\}){2}(\x0D\x0A)?", "", readedData, 1)
            #\cpgN?
            if re.search(r"\\cpg\d+", readedData) != None:
                readedData = re.sub(r"\\cpg\d+(\x0D\x0A)?", "", readedData, 1)
            #<fontname>
            fontName = re.search(r"(\w+(\s+)?)+", readedData).group(0)
            fontName = re.sub(r"\s+$", "", fontName, 1)
            fontInfoDic["fontName"] = fontName
            xml += "font=\"" + fontName + "\"/>"
            readedData = re.sub(r"(\w+(\s+)?)+", "", readedData, 1)
            #<fontaltname>?
            if re.search(r"\{\\\*\\falt", readedData) != None:
                readedData = re.sub(r"\{\\\*\\falt[^\}]+\}(\x0D\x0A)?", "", readedData, 1)
            #konec polozky
            if subGroup:
                if re.search(r"^\s;(\x0D\x0A)?\}", readedData) == None:
                    print readedData
                    sys.stderr.write("Chyba parsovani FontTable\n")
                    sys.exit(1)
                readedData = re.sub(r"^\s;(\s{1})?\}(\x0D\x0A)?", "", readedData, 1)
            else:
                if not readedData[0] == ";":
                    print readedData
                    sys.stderr.write("Chyba parsovani FontTable\n")
                    sys.exit(1)
                readedData = re.sub(r"\s;(\x0D\x0A)?", "", readedData, 1)
             
            currentObject.fontInfo.append(fontInfoDic)
        readedData = re.sub(r"\}(\x0D\x0A)?", "", readedData, 1)
        #print currentObject.fontInfo
        #sys.exit(0)
        retArray.append(readedData)
        retArray.append(xml)
        return retArray
    
""" PARSOVANI RTF """
#def parseRTF():
#    parrent = RTFUnit()
#    parrent.text = "ROOT"
#    #print input
    #sys.exit(0)
#    parrent.LoadFile(input)
#    parrent.InterpretPlainText(parrent)
#    return parrent

""" MAIN """
#def main():
#    parsedRTF = parseRTF()
    
""" ZACATEK """
#main()
