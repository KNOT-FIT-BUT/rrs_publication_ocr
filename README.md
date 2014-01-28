# rrs_publication_ocr #

## crfpp/ ##

Slo�ka s instala�n�mi soubory CRF++ klasifik�toru + tr�novac� data.

## LSR/ ##

### Skripty ###

#### Klasifik�tor: ####

**./lsr.py** --input vstup --output vystup -m [extract_all | extract_hed | extract_section| extract_nocit] -i [rtf | ...]

* --input - vstupn� soubor <br />
* --output - v�stupn� soubor v XML. Pokud nen� zad�n, tiskne se v�sledek na standardn� v�stup. <br />
* -m - m�d zpracov�n� souboru:

	"extract_all" - provede z�kladn� klasifikaci dokumentu, dodate�nou klasifikaci nadpis� <br />
	a klasifikaci hlavi�ky dokumentu <br />

	"extract_hed" - provede klasifikaci hlavi�ky dokumentu <br />

	"extract_section" - provede z�kladn� klasifikaci dokumentu <br />

* -i - ur�uje form�t vstupu. Zat�m "rtf" bere jako vstupn� soubor form�tu RTF, ostatn� �i nezadan� pova�uje za txt soubor. <br />

**./processOCRRTF.py** <br />

Jedn� se o modul, kter� pou��v� klasifik�tor k extrahov�n� surov�ho textu z v�sledku klasifikace, kter� je ve form� XML souboru. <br />

#### XML parser: ####

**./xmlParser.py**

XML parser je mo�n� pou��t i samostatn� bez n�sledn� klasifikace.

#### RTF parser: ####

Star� parser <br />
**./rtfParser.py**

Nov� parser <br />
**./rtfParserNew.py**

RTF parser je mo�n� pou��t i samostatn� bez n�sledn� klasifikace. Sta�� odkomentovat funkci main().

#### Klasifikace dokumentu z v�stupu OCR syst�mu: ####

**./runClassification.py**

Skript ur�en� pouze pro zklasifikov�n� v�ech dokument� nach�zej�c�ch se ve v�stupn� slo�ce OCR syst�mu. 
K tomuto skriptu se v�e soubor classPassed.dat, kter� ��k�, kter� slo�ky ji� byly klasifikov�ny a tak� 
soubor outClass.log, kter� uchov�v� informace o v�sledku klasifikace ka�d�ho klasifikovan�ho souboru. <br />

#### Automatizovan� vyhodnocen� klasifikace: ####

**./ClassificationCheck.py**

Automatizovan� vyhodnocen� prov�d� kontrolu klasifikace Titulu, Autor�, E-Mail�, P�i�len�n�, Abstraktu, Nadpisu 1 a Nadpisu 2. 
V�stupem je tabulka pro ka�d� soubor, kter� ukazuje v�sledek klasifikace pro danou ��st dokumentu. Po dokon�en� kontroly v�ech 
dokument� je vytvo�ena tabulka ukazuj�c� F-Measure Score, Recall, Precision, skute�n� po�et dan� �asti dokumentu ve v�ech 
dokumentech, po�et ozna�en� klasifik�torem a po�et spr�vn�ch ozna�en� klasifik�torem. <br />

#### Ulo�en� klasifikovan�ch dokument� do datab�ze: ####

**./SaveOutClassToDatabase.py**

Skript proch�z� slo�ku OutClass a v�echny doposud neulo�en� dokumenty ukl�d� do datab�ze. Seznam ji� ulo�en�ch dokument� 
je obsa�en v souboru OutSavedToDB.dat. Skript tento seznam s ka�d�m sv�m b�hem aktualizuje. 

Skript vyu��v� pro p��stup k datab�zi soubor databaseAccess.dat, kter� je napln�n p��stupov�mi �daji ve tvaru: <br />
host:dbname:user:password <br />

Jeliko� tento soubor obsahuje citliv� data, nen� verzov�n a je nutn� si jej lok�ln� vytvo�it!

### Slo�ky ###

#### crfpp/ ####

obsahuje nainstalovan� CRF++ klasifik�tor

#### in/ ####

Sada dokument� z OCR syst�mu, kter� slou�� pro kontrolu chov�n� klasifik�toru a jeho schopnost klasifikace po �prav�ch. 
Spr�vn� klasifikace je ulo�ena v manualClassification.txt ve form�tu JSON. <br />

#### in2/ ####

Druh� sada dokument� z OCR syst�mu, kter� slou�� pro kontrolu chov�n� klasifik�toru a jeho schopnost klasifikace po �prav�ch. 
Spr�vn� klasifikace je ulo�ena v manualClassificationWithReferences.txt ve form�tu JSON. Tato sada narozd�l od prvn� obsahuje 
i klasifikaci referenc�. <br />

#### LSRCIT/ ####

Skripty vyu��van� ke klasifikaci citac�.

#### LSRHED/ ####

Skripty vyu��van� ke klasifikaci hlavi�ky dokumentu.

#### LSRLabel/ ####

Skripty vyu��van� k obecn� klasifikaci dokumentu.

#### LSRRTF/ ####

Pomocn� skripty klasifik�toru.

#### out/ ####

Klasifikovan� dokumenty prvn� testovac� sady.

#### out2/ ####

Klasifikovan� dokumenty druh� testovac� sady.

#### outClass/ ####

Klasifikovan� dokumenty z v�stupn� slo�ky OCR syst�mu.

#### tmp/ ####

Slo�ka pro ukl�d�n� pomocn�ch soubor� p�i klasifikov�n�.
