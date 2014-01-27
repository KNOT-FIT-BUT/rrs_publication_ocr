rrs_publication_ocr
===================

+-----------------+
|crfpp/           |
+-----------------+

Slozka s instalacnimi soubory CRF++ klasifikatoru + trenovaci data.


+-----------------+
|LSR/             |
+-----------------+

===================
Skripty
===================

Klasifikator:
-------------

./lsr.py --input vstup --output v�stup -m [extract_all | extract_hed | extract_section| extract_nocit] -i [rtf | ...]

--input - vstupn� soubor
--output - v�stupn� soubor v XML. Pokud nen� zad�n, tiskne se v�sledek na standardn� v�stup.
-m - m�d zpracov�n� souboru: - "extract_all" - provede z�kladn� klasifikaci dokumentu + dodate�nou klasifikaci nadpis�
                                + klasifikaci hlavi�ky dokumentu
                             - "extract_hed" - provede klasifikaci hlavi�ky dokumentu
                             - "extract_section" - provede z�kladn� klasifikaci dokumentu
-i - ur�uje form�t vstupu. Zat�m "rtf" bere jako vstupn� soubor form�tu RTF, ostatn� �i nezadan� pova�uje za txt soubor.

./processOCRRTF.py

Jedna se o modul, ktery pouziva klasifikator k extrahovani suroveho textu z vysledku klasifikace, ktera je ve forme XML
souboru.

XML parser:
-----------

./xmlParser.py

XML parser je mo�n� pou��t i samostatn� bez n�sledn� klasifikace.


RTF parser:
-----------

Star� parser
./rtfParser.py

Nov� parser
./rtfParserNew.py

RTF parser je mo�n� pou��t i samostatn� bez n�sledn� klasifikace. Sta�� odkomentovat funkci main().


Klasifikace dokumentu z vystupu OCR systemu:
--------------------------------------------

./runClassification.py

Skript urceny pouze pro zklasifikovani vsech dokumentu nachazejicich se ve vystupni slozce OCR systemu.
K tomuto skriptu se vaze soubor classPassed.dat, ktery rika, ktere slozky jiz byly klasifikovany a take
soubor outClass.log, ktery uchovava informace o vysledku klasifikace kazdeho klasifikovaneho souboru.

Automatizovan� vyhodnocen� klasifikace:
---------------------------------------

./ClassificationCheck.py

Automatizovan� vyhodnocen� prov�d� kontrolu klasifikace Titulu, Autor�, E-Mail�, P�i�len�n�, Abstraktu, Nadpisu 1 a Nadpisu 2.
V�stupem je tabulka pro ka�d� soubor, kter� ukazuje v�sledek klasifikace pro danou ��st dokumentu. Po dokon�en� kontroly v�ech
dokument� je vytvo�ena tabulka ukazuj�c� F-Measure Score, Recall, Precision, skute�n� po�et dan� �asti dokumentu ve v�ech
dokumentech, po�et ozna�en� klasifik�torem a po�et spr�vn�ch ozna�en� klasifik�torem.


Ulo�en� klasifikovan�ch dokument� do datab�ze:
----------------------------------------------

./SaveOutClassToDatabase.py

Skript proch�z� slo�ku OutClass a v�echny doposud neulo�en� dokumenty ukl�d� do datab�ze. Seznam ji� ulo�en�ch dokument� je
obsa�en v souboru OutSavedToDB.dat. Skript tento seznam s ka�d�m sv�m b�hem aktualizuje.

Skript vyuziva pro pristup k databazi soubor databaseAccess.dat, ktery je naplnen pristupovymi udaji ve tvaru:
host:dbname:user:password

Jelikoz tento soubor obsahuje citliva data, neni verzovan a je nutne si jej lokalne vytvorit!


===================
Slozky
===================

crfpp/
------
obsahuje nainstalovany CRF++ klasifikator

in/
---
Sada dokumentu z OCR systemu, ktera slouzi pro kontrolu chovani klasifikatoru a jeho schopnost klasifikace po upravach.
Spravna klasifikace je ulozena v manualClassification.txt ve formatu JSON.

in2/
---
Druha sada dokumentu z OCR systemu, ktera slouzi pro kontrolu chovani klasifikatoru a jeho schopnost klasifikace po upravach.
Spravna klasifikace je ulozena v manualClassificationWithReferences.txt ve formatu JSON. Tato sada narozdil od prvni obsahuje
i klasifikaci referenci.

LSRCIT/
-------
Skripty vyuzivane ke klasifikaci citaci.

LSRHED/
-------
Skripty vyuzivane ke klasifikaci hlavicky dokumentu.

LSRLabel/
---------
Skripty vyuzivane k obecne klasifikaci dokumentu.

LSRRTF/
-------
Pomocne skripty klasifikatoru.

out/
----
Klasifikovane dokumenty prvni testovaci sady.

out2/
-----
Klasifikovane dokumenty druhe testovaci sady.

outClass/
---------
Klasifikovane dokumenty z vystupni slozky OCR systemu.

tmp/
----
Slozka pro ukladani pomocnych souboru pri klasifikovani.
