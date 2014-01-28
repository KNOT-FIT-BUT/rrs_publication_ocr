# rrs_publication_ocr #

## crfpp/ ##

Složka s instalaèními soubory CRF++ klasifikátoru + trénovací data.

## LSR/ ##

### Skripty ###

#### Klasifikátor: ####

**./lsr.py** --input vstup --output vystup -m [extract_all | extract_hed | extract_section| extract_nocit] -i [rtf | ...]

* --input - vstupní soubor <br />
* --output - výstupní soubor v XML. Pokud není zadán, tiskne se výsledek na standardní výstup. <br />
* -m - mód zpracování souboru:

	"extract_all" - provede základní klasifikaci dokumentu, dodateènou klasifikaci nadpisù <br />
	a klasifikaci hlavièky dokumentu <br />

	"extract_hed" - provede klasifikaci hlavièky dokumentu <br />

	"extract_section" - provede základní klasifikaci dokumentu <br />

* -i - urèuje formát vstupu. Zatím "rtf" bere jako vstupní soubor formátu RTF, ostatní èi nezadané považuje za txt soubor. <br />

**./processOCRRTF.py** <br />

Jedná se o modul, který používá klasifikátor k extrahování surového textu z výsledku klasifikace, která je ve formì XML souboru. <br />

#### XML parser: ####

**./xmlParser.py**

XML parser je možné použít i samostatnì bez následné klasifikace.

#### RTF parser: ####

Starý parser <br />
**./rtfParser.py**

Nový parser <br />
**./rtfParserNew.py**

RTF parser je možné použít i samostatnì bez následné klasifikace. Staèí odkomentovat funkci main().

#### Klasifikace dokumentu z výstupu OCR systému: ####

**./runClassification.py**

Skript urèený pouze pro zklasifikování všech dokumentù nacházejících se ve výstupní složce OCR systému. 
K tomuto skriptu se váže soubor classPassed.dat, který øíká, které složky již byly klasifikovány a také 
soubor outClass.log, který uchovává informace o výsledku klasifikace každého klasifikovaného souboru. <br />

#### Automatizované vyhodnocení klasifikace: ####

**./ClassificationCheck.py**

Automatizované vyhodnocení provádí kontrolu klasifikace Titulu, Autorù, E-Mailù, Pøièlenìní, Abstraktu, Nadpisu 1 a Nadpisu 2. 
Výstupem je tabulka pro každý soubor, která ukazuje výsledek klasifikace pro danou èást dokumentu. Po dokonèení kontroly všech 
dokumentù je vytvoøena tabulka ukazující F-Measure Score, Recall, Precision, skuteèný poèet dané èasti dokumentu ve všech 
dokumentech, poèet oznaèení klasifikátorem a poèet správných oznaèení klasifikátorem. <br />

#### Uložení klasifikovaných dokumentù do databáze: ####

**./SaveOutClassToDatabase.py**

Skript prochází složku OutClass a všechny doposud neuložené dokumenty ukládá do databáze. Seznam již uložených dokumentù 
je obsažen v souboru OutSavedToDB.dat. Skript tento seznam s každým svým bìhem aktualizuje. 

Skript využívá pro pøístup k databázi soubor databaseAccess.dat, který je naplnìn pøístupovými údaji ve tvaru: <br />
host:dbname:user:password <br />

Jelikož tento soubor obsahuje citlivá data, není verzován a je nutné si jej lokálnì vytvoøit!

### Složky ###

#### crfpp/ ####

obsahuje nainstalovaný CRF++ klasifikátor

#### in/ ####

Sada dokumentù z OCR systému, která slouží pro kontrolu chování klasifikátoru a jeho schopnost klasifikace po úpravách. 
Správná klasifikace je uložena v manualClassification.txt ve formátu JSON. <br />

#### in2/ ####

Druhá sada dokumentù z OCR systému, která slouží pro kontrolu chování klasifikátoru a jeho schopnost klasifikace po úpravách. 
Správná klasifikace je uložena v manualClassificationWithReferences.txt ve formátu JSON. Tato sada narozdíl od první obsahuje 
i klasifikaci referencí. <br />

#### LSRCIT/ ####

Skripty využívané ke klasifikaci citací.

#### LSRHED/ ####

Skripty využívané ke klasifikaci hlavièky dokumentu.

#### LSRLabel/ ####

Skripty využívané k obecné klasifikaci dokumentu.

#### LSRRTF/ ####

Pomocné skripty klasifikátoru.

#### out/ ####

Klasifikované dokumenty první testovací sady.

#### out2/ ####

Klasifikované dokumenty druhé testovací sady.

#### outClass/ ####

Klasifikované dokumenty z výstupní složky OCR systému.

#### tmp/ ####

Složka pro ukládání pomocných souborù pøi klasifikování.
