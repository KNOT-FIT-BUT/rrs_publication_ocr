# rrs_publication_ocr #

## crfpp/ ##

Slozka s instalacnimi soubory CRF++ klasifikatoru + trenovaci data.

## LSR/ ##

### Skripty ###

#### Klasifikator: ####

**./lsr.py** --input vstup --output výstup -m [extract_all | extract_hed | extract_section| extract_nocit] -i [rtf | ...]

	* --input - vstupní soubor <br />
	* --output - výstupní soubor v XML. Pokud není zadán, tiskne se výsledek na standardní výstup. <br />
	* -m - mód zpracování souboru:

	"extract_all" - provede základní klasifikaci dokumentu + dodateènou klasifikaci nadpisù <br />
	+ klasifikaci hlavièky dokumentu <br />

	"extract_hed" - provede klasifikaci hlavièky dokumentu <br />

	"extract_section" - provede základní klasifikaci dokumentu <br />

	* -i - urèuje formát vstupu. Zatím "rtf" bere jako vstupní soubor formátu RTF, ostatní èi nezadané považuje za txt soubor. <br />

**./processOCRRTF.py** <br />

Jedna se o modul, ktery pouziva klasifikator k extrahovani suroveho textu z vysledku klasifikace, ktera je ve forme XML <br />
souboru. <br />

#### XML parser: ####

**./xmlParser.py**

XML parser je možné použít i samostatnì bez následné klasifikace.

#### RTF parser: ####

Starý parser <br />
**./rtfParser.py**

Nový parser <br />
**./rtfParserNew.py**

RTF parser je možné použít i samostatnì bez následné klasifikace. Staèí odkomentovat funkci main().

#### Klasifikace dokumentu z vystupu OCR systemu: ####

**./runClassification.py**

Skript urceny pouze pro zklasifikovani vsech dokumentu nachazejicich se ve vystupni slozce OCR systemu. <br />
K tomuto skriptu se vaze soubor classPassed.dat, ktery rika, ktere slozky jiz byly klasifikovany a take <br />
soubor outClass.log, ktery uchovava informace o vysledku klasifikace kazdeho klasifikovaneho souboru. <br />

#### Automatizované vyhodnocení klasifikace: ####

**./ClassificationCheck.py**

Automatizované vyhodnocení provádí kontrolu klasifikace Titulu, Autorù, E-Mailù, Pøièlenìní, Abstraktu, Nadpisu 1 a Nadpisu 2. <br />
Výstupem je tabulka pro každý soubor, která ukazuje výsledek klasifikace pro danou èást dokumentu. Po dokonèení kontroly všech <br />
dokumentù je vytvoøena tabulka ukazující F-Measure Score, Recall, Precision, skuteèný poèet dané èasti dokumentu ve všech <br />
dokumentech, poèet oznaèení klasifikátorem a poèet správných oznaèení klasifikátorem. <br />

#### Uložení klasifikovaných dokumentù do databáze: ####

**./SaveOutClassToDatabase.py**

Skript prochází složku OutClass a všechny doposud neuložené dokumenty ukládá do databáze. Seznam již uložených dokumentù <br />
je obsažen v souboru OutSavedToDB.dat. Skript tento seznam s každým svým bìhem aktualizuje. <br />

Skript vyuziva pro pristup k databazi soubor databaseAccess.dat, ktery je naplnen pristupovymi udaji ve tvaru: <br />
host:dbname:user:password <br />

Jelikoz tento soubor obsahuje citliva data, neni verzovan a je nutne si jej lokalne vytvorit!

### Slozky ###

#### crfpp/ ####

obsahuje nainstalovany CRF++ klasifikator

#### in/ ####

Sada dokumentu z OCR systemu, ktera slouzi pro kontrolu chovani klasifikatoru a jeho schopnost klasifikace po upravach. <br />
Spravna klasifikace je ulozena v manualClassification.txt ve formatu JSON. <br />

#### in2/ ####

Druha sada dokumentu z OCR systemu, ktera slouzi pro kontrolu chovani klasifikatoru a jeho schopnost klasifikace po upravach. <br />
Spravna klasifikace je ulozena v manualClassificationWithReferences.txt ve formatu JSON. Tato sada narozdil od prvni obsahuje <br />
i klasifikaci referenci. <br />

#### LSRCIT/ ####

Skripty vyuzivane ke klasifikaci citaci.

#### LSRHED/ ####

Skripty vyuzivane ke klasifikaci hlavicky dokumentu.

#### LSRLabel/ ####

Skripty vyuzivane k obecne klasifikaci dokumentu.

#### LSRRTF/ ####

Pomocne skripty klasifikatoru.

#### out/ ####

Klasifikovane dokumenty prvni testovaci sady.

#### out2/ ####

Klasifikovane dokumenty druhe testovaci sady.

#### outClass/ ####

Klasifikovane dokumenty z vystupni slozky OCR systemu.

#### tmp/ ####

Slozka pro ukladani pomocnych souboru pri klasifikovani.
