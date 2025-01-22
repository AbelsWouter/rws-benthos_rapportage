<!-- title: Benthos script-->

# Python script voor RWS rapportage protocol Deel-C <!-- omit in toc --> 
## Gebruikers- en beheerdershandleiding <!-- omit in toc -->
*Release 1.0.0*
<br> <br> <br> <br> 

<p align="center">
  <img alt="Light" src="https://waardenburg.eco/images/logo.svg" width="30%">
&nbsp; &nbsp; &nbsp; &nbsp;
  <img alt="Dark" src="https://www.rijkswaterstaat.nl/static/img/logo-nl.svg" width="45%">
</p>
<div class="page"/>

## Versie informatie <!-- omit in toc -->

| Versie | Datum | Auteur         | Wijziging                   |
| ------ | ----------- | -------------- | ----------------------------|
| 1      | 04-12-2023  | Joyce Haringa / Maarten Japink |Concept versie|
| 2      | 20-02-2024  | Joyce Haringa / Maarten Japink |Definitieve versie oplevering script|

<div class="page"/>

## Inhoud <!-- omit in toc -->

- [1. Algemene informatie](#1-algemene-informatie)
- [2. Installatie](#2-installatie)
  - [2.1 Installatie programma's](#21-installatie-programmas)
  - [2.3 Gebruik van de prompt/terminal](#23-gebruik-van-de-promptterminal)
  - [2.4 Ophalen van het script](#24-ophalen-van-het-script)
  - [2.5 Installatie packages](#25-installatie-packages)
  - [2.6 Starten virtuele omgeving](#26-starten-virtuele-omgeving)
  - [2.7 Stoppen virtuele omgeving](#27-stoppen-virtuele-omgeving)
  - [2.8 Configureren Code-editor](#28-configureren-code-editor)
  - [2.9 Aquadesk-api-key](#29-aquadesk-api-key)
- [3 Gebruik](#3-gebruik)
  - [3.1 Input](#31-input)
  - [3.2 Aquadesk of eigen data](#32-aquadesk-of-eigen-data)
  - [3.3 Uitvoeren](#33-uitvoeren)
- [4 Inhoudelijke afspraken](#4-inhoudelijke-afspraken)
  - [4.1 Analyse protocollen](#41-analyse-protocollen)
    - [4.1.1 Determinatie niveau](#411-determinatie-niveau)
    - [4.1.2 Abundantie/Presentie](#412-abundantiepresentie)
    - [4.1.3 Biomassa](#413-biomassa)
  - [4.2 Diversiteitsindeling](#42-diversiteitsindeling)
  - [4.3 Diversiteitsberekening](#43-diversiteitsberekening)
  - [4.4 Dichtheid](#44-dichtheid)
  - [4.5 Groepen](#45-groepen)
  - [4.6 Trend](#46-trend)
  - [4.7 Fouten](#47-fouten)
  - [4.8 TWN](#48-twn)
  - [4.9 Bewaren van uitkomsten](#49-bewaren-van-uitkomsten)
- [5 Output](#5-output)
  - [5.1 Data](#51-data)
  - [5.2 Tabellen](#52-tabellen)
  - [5.3 Figuren](#53-figuren)
- [6 Logging](#6-logging)
- [7. Beheer](#7-beheer)
  - [7.1 Data-model](#71-data-model)
  - [7.2 Waterlichamen](#72-waterlichamen)
  - [7.3 Locaties](#73-locaties)
  - [7.4 BISI](#74-bisi)
    - [7.4.1 Nieuwe BISI](#741-nieuwe-bisi)
  - [7.5 BISI config](#75-bisi-config)
  - [7.6 Exotics](#76-exotics)
  - [7.7 Taxongroep classificatie](#77-taxongroep-classificatie)
  - [7.8 Taxonomische rangen](#78-taxonomische-rangen)
  - [7.9 Typische soorten habitatgebieden](#79-typische-soorten-habitatgebieden)
  - [7.10 Yaml bestanden](#710-yaml-bestanden)
  - [7.11 Technische documentatie](#711-technische-documentatie)
- [8. Credits](#8-credits)
  - [Auteurs](#auteurs)
  - [Inhoudelijke begeleiding](#inhoudelijke-begeleiding)
- [9. Licentie](#9-licentie)
- [10. Disclaimer](#10-disclaimer)

<div class="page"/>

---

## 1. Algemene informatie

Het Python script is door Waardenburg Ecology ontwikkeld in opdracht van Rijkswaterstaat (RWS). Het doel is om automatisch een deel van de tabellen en figuren te genereren, zoals gesteld in het Protocol Deel-C voor het KRW en KRM-monitoringprogramma macrozoöbenthos. 

De volgende onderdelen uit Protocol Deel-C (versie 5 april 2022) zijn in dit script verwerkt:
- H9.3 KRM en Ospar  
  
  Noordzee: Boxcorer, Bodemschaaf, Video
  - BISI
  - Margalef index
- H9.6 Overige Beheervragen  
  
  Alle methodieken m.u.v. video
  - Aantallen, biodiversiteit, dichtheden en biomassa
  - Scatterplot gemiddelde dichtheid, biomassa en diversiteit
  - Gestapelde staafdiagram dichtheden en biomassa
  - Tabel nieuwe en verdwenen soorten  
  
  Video
  - Aantallen, dichtheden per eunis
  - Figuur met dichtheden per soortgroep
  - Figuur met bedekkingspercentage per soortgroep per eunis 
habitat

Het script is met grootte zorg ontwikkeld. De te verwachten data-fouten worden afgevangen. Slechts een deel van de data-fouten kan worden opgelost met een default.
Alle herkende fouten worden aan de gebruiker gerapporteerd in de logfile. Default verbeteringen worden eveneens in de logfile aan de gebruiker kenbaar gemaakt.
Doordat een eigen databestand kan worden aangeboden (conform het gestelde format) heeft de gebruiker de mogelijkheid om data-issues naar eigen inzicht op te lossen en daarmee de script-defaults te overrulen.

De locatie- en waterlichamen configuratiebestanden zijn de ruggengraat van het script. Het beheer van deze bestanden ligt bij Rijkswaterstaat.

<div class="page"/>

## 2. Installatie

### 2.1 Installatie programma's

Het script is getest op Windows 11 en op WSL2-Ubuntu. 
Voor een correcte werking moeten minimaal Python en Poetry geïnstalleerd zijn.
De volgende installaties moeten éénmalig op het systeem worden uitgevoerd.

**Pyenv - Optioneel**  
Installeer pyenv indien er meerdere python versies nodig zijn op je systeem. Pyenv helpt je hierbij: https://github.com/pyenv-win/pyenv-win. 
Let op de installatie van een aantal systeemvariabelen.

**Python**  
Het script is ontwikkeld en getest in python 3.12.
Installeer Python via één van de volgende manieren
- Python3.12: https://www.python.org/downloads
of 
- met pyenv via de command line: 
```cmd
pyenv install 3.12.1
pyenv global 3.12.1
```

**Poetry**  
Het script is afhankelijk van een aantal packages. Op het moment van schrijven is Poetry de beste packagemanager, zie: https://python-poetry.org/docs/.
Let op de installatie van een aantal systeemvariabelen.
Test de poetry installatie vanaf de command line:
```cmd
poetry --version
```

**Git - Optioneel**  
Het script wordt gehost/beheerd op Gitlab. Met Git kan direct met de repository worden gesynchroniseerd.
De installatie in configuratie-instellingen staan beschreven in Installing Git en First time git setup op: https://git-scm.com/book/en/v2 of de Nederlandse versie: https://git-scm.com/book/nl/v2

**Code editor / IDE**  
Het script kan vanaf de command line worden gestart, maar het is handiger om hiervoor een IDE of code editor te gebruiken. Er zijn heel veel code editors beschikbaar, het maakt niet uit welke je gebruikt, zolang Python maar ondersteund wordt. Standaard wordt Python geleverd met IDLE. Dit is een prima optie, maar wij raden Thonny aan als simpel alternatief, zie: https://realpython.com/python-thonny/. 

### 2.3 Gebruik van de prompt/terminal
Poetry en evt. ook Git worden bediend vanaf de commando-regel. Op windows is dat de prompt en op Linux of Mac de Terminal.
In Windows open je de prompt door in het zoekvenster in de taakbalk te zoeken naar 'cmd' of 'Command Prompt'.

In de prompt kun je door de bestandsstructuur navigeren met het commando `cd`.
Met `cd ..` ga je één niveau omhoog. 
Met `cd [foldernaam]` ga je één niveau dieper naar de betreffende folder.
Met `cd \` ga je direct terug naar de root, dus bijvoorbeeld 'C:'
Met `dir` op Windows en `ls` op Mac en Linux krijg je een overzicht van de folders en bestanden in je huidige locatie.

Voor een uitgebreidere uitleg over de prompt zie: https://nl.wikibooks.org/wiki/Gebruik_van_de_opdrachtprompt

### 2.4 Ophalen van het script
RWS levert het script aan als zipfile of je kunt het zelf downloaden / klonen vanaf de Gitlab repository.
Het makkelijkst is het om het script in een makkelijk te bereiken folder te plaatsten, dat scheelt veel typen in de prompt. Bijvoorbeeld: C:\scripts\benthos. 
Maar per bedrijf zal hier vanuit ict anders mee omgegaan worden. Bij twijfel overleg met ict.

### 2.5 Installatie packages
Navigeer in de terminal/prompt naar de script-folder.

Type het volgende commando op de command line:
```cmd
poetry install --no-root
```

Poetry maakt een virtuele omgeving aan met daarin alle door het script benodigde packages. Ieder keer als het script gebruikt moet worden, moet eerst de virtuele omgeving gestart.  

### 2.6 Starten virtuele omgeving
Navigeer in de terminal/prompt naar de script-folder.

Type het volgende commando op de command line:
```cmd
poetry shell
```
Als alles goed gaat reageert Poetry met het volledige pad naar de virtuele omgeving. Bijvoorbeeld: 
```
Spawning shell within C:\Users\*Gebruikersnaam*\AppData\Local\pypoetry\Cache\virtualenvs\rws-project-py3.12
```
Dit pad heb je later nodig voor het configureren van de code editor / IDE.  
Laat de prompt open staan.

### 2.7 Stoppen virtuele omgeving
Ga naar de terminal/prompt waarin de Poetry shell draait (het venster waarin je het commando `poetry shell` hebt gegeven).

Type het volgende commando op de command line:
```cmd
deactivate
```

De terminal/prompt kun je afsluiten met het commando:
```cmd
exit
```

### 2.8 Configureren Code-editor
In de code editor moet je de juiste interpreter configureren. Als de code editor alleen voor dit project gebruikt is de instelling eenmalig. Gebruik je de code-editor voor verschillende Python doeleinden dan zul je de interpreter steeds opnieuw moeten instellen.
In iedere code editor zal de interpreter anders ingesteld moeten worden, maar in Thonny kan dit als volgt:
- Ga naar menu: Run, Select interpreter. 
- Kies voor 'Alternative Python 3 interpreter or Virtual environment'
- Geef de locatie op van de virtuele omgeving. Deze staat in de poetry shell.
- Klik op Ok

### 2.9 Aquadesk-api-key
Om het script te gebruiken heb je een geldige Aquadesk-api-key nodig. Deze kun je opvragen bij RWS: Functioneel beheer Aquadesk aquadesk@rws.nl. Deze code moet in de aquadesk.yaml in de config folder van het script worden gezet.
Op de tweede regel moet de api key achter het woord 'api_key:' ingevuld worden.

<div class="page"/>

## 3 Gebruik

### 3.1 Input
In de input-folder staan altijd 2 tekstbestanden. Hierin kan de gebruiker aangeven welke wateren en Aquadesk-projecten er verwerkt moeten worden.
Alle regels die beginnen met een hekje '#' worden genegeerd door het script.

LET OP:
Er mogen geen regels worden verwijderd.
Er mogen geen tekstuele wijzigingen worden doorgevoerd. (verwijderen en plaatsen van '#' uitgezonderd)
Deze 2 bestanden mogen niet verwijderd worden.

De gebieden in de Noordzee zijn als waterlichamen opgenomen in de configuratie. De Noordzee als geheel waterlichaam bestaat niet. Locaties kunnen niet aan meerdere waterlichamen worden toegekend. Indien de Noordzee als geheel moet worden gerapporteerd dan moet een alternatieve configuratie worden aangeboden.

De resultaten van bemonsteringen die over meerdere jaren lopen kunnen voor die jaren worden geclusterd. Dit is per project en waterlichaam in te stellen in de het configuratiebestand clustered_sample_year.yaml. De consequentie is dat projecten met verschillende temporele bemonsteringsstrategieën niet correct in één figuur kunnen worden weergegeven. Voor correcte resultaten moeten de figuren en tabellen voor waterlichamen/projecten met afwijkende temporele bemonsteringsstrategieën dus in aparte runs worden gegenereerd.

Het al dan niet tonen van missende meetjaren in de grafieken is een configureerbare instelling. Voor de lijn en staaf diagrammen is dit afzonderlijk in te stellen in config/global_variables.yaml.

### 3.2 Aquadesk of eigen data
Het script gaat uit van het Aquadesk formaat, zoals dat via de website https://live.aquadesk.nl/home kan worden gedownload.

De gebruiker heeft twee opties om data aan te bieden aan het script:
1. Eigen dataset aanleveren door deze in de input-folder te zetten. 
2. Automatisch downloaden vanaf de DD-ECO-API V2;

Een [eigen dataset] moet voldoen aan het Aquadesk formaat. 
Er wordt gecontroleerd op de vereiste kolommen en verplichte velden.

Het script leest 1 bestand met gegevens in. Dit bestand kan een .csv of .xlsx bestand zijn. 
Indien er geen .csv of .xlsx bestand in de map input staat dan wordt automatisch data van de DD-ECO-API V2 gedownload. 
Indien er meerdere .csv en/of .xlsx bestanden in de input folder staan. Dan stopt het script met een waarschuwing.

De door de gebruiker opgegeven selectie van projecten en waterlichamen wordt ook op de eigen dataset toegepast. De selectie van projecten en waterlichamen moeten dus altijd worden ingesteld.

### 3.3 Uitvoeren
In de hoofdfolder van het project staat het bestand main.py.
Dit is het enige python-script dat de gebruiker nodig heeft. In main.py staan een aantal python commando's die achter elkaar uitgevoerd worden. 
De volgorde van deze commando's is van cruciaal belang.

In Thonny kan het script op meerdere manieren worden uitgevoerd:
- Via Menu Run, Run current script
- Via het groene start knopje
- Door de F5 toets in te drukken.
In alle gevallen is het resultaat hetzelfde.

LET OP: voor de **BISI** is 2015 een standaard input waarde voor het jaar gegeven. Deze kan de gebruiker handmatig veranderen in het script door 2015 te vervangen door het gewenste jaartal. Zie onderstaande voorbeeld (2016 i.p.v. 2015):
```cmd
BISI.main_bisi(data, year=2016)
```

<div class="page"/>

## 4 Inhoudelijke afspraken

### 4.1 Analyse protocollen
In de analyseprotocollen staat beschreven tot op welk niveau de verschillende organismen gedetermineerd dienen te worden, welke taxa geteld of op presentie gescoord worden en van weke taxa de biomassa bepaald moet worden. Soms worden in de opdracht aanvullende voorwaarden opgegeven. De analyseprotocollen kunnen worden beschouwd als de algemeen geldende eis. Voor de vergelijkbaarheid over monsters en jaren moet alles minimaal aan het laatst geldende analyseprotocol voldoen.
Vigerend determinatie niveau, aanwezigheid/presentie en biomassa bepaling zijn hiërarchisch op basis van de TWN-taxonomie configureerbaar.

#### 4.1.1 Determinatie niveau
Soms wordt/werd er verder gedetermineerd en komt dit te hoge detail-niveau toch in Aquadesk. Deze taxa worden automatisch op het geconfigureerde niveau gezet.

#### 4.1.2 Abundantie/Presentie
Soms wordt/werden taxa waarvan de presentie dient te worden bepaald toch geteld. Taxa die onterecht wel geteld zijn worden automatisch op aantal = 0 gesteld.

Taxa uit de screening worden daarentegen (volgens protocol) op presentie gescoord. Deze soorten komen dus sporadisch in het monster voor. Om ze toch mee te laten wegen in de indexen en dichtheid worden deze taxa op aantal = 1 gesteld. Deze gecorrigeerde aantallen worden eveneens omgerekend naar dichtheden.

#### 4.1.3 Biomassa 
Soms wordt/werd bij taxa onterecht de biomassa bepaald. Deze biomassa's worden automatisch verwijderd.

### 4.2 Diversiteitsindeling
Voor de berekening van de diversiteitsindexen wordt gekeken naar het aantal soorten in een monster. In de praktijk blijkt dit echter een lastig begrip. Veel taxa worden op een hoger taxonomisch genoteerd. Doen deze hogere taxa wel of niet mee in de index? In overleg met Eurofins en RWS is tot de volgende oplossing gekomen:

> Het soortniveau is het laagste taxonomische niveau dat wordt onderkend. Ondersoorten worden op soortniveau gebracht. De hogere taxonomische niveaus doen alleen mee als er op een lager niveau geen soorten zijn onderscheiden. De abundanties van taxa die niet meedoen worden naar rato verdeeld over de lagere taxa. 

Nadeel van deze aanpak is een kleine onderschatting van de diversiteit. Het grote voordeel dat deze indeling reproduceerbaar is en dus over de jaren in de rapportages constant is.

### 4.3 Diversiteitsberekening
**Shannon-index en soortenrijkdom**  
De Shannon-index en de soortenrijkdom worden op 2 manieren berekent: over het gebied/deelgebied en als het gemiddelde van de index per monster. Monsters zonder taxa worden op 0 gesteld. Deze monsters drukken dus het gemiddelde. De index is gebaseerd op de dichtheid per oppervlakte of volume.

Er wordt geen onderscheid gemaakt in de monsters met een bemonsterde oppervlakte of -volume. De aanname is dat er representatief wordt bemonsterd en dat het gebruik van diverse bemonsteringstechnieken daaraan bijdraagt. Belangrijke aanname daarbij is dat de gebruikte bemonsteringstechnieken over de jaren heen gelijk zijn. Helaas is dit voor Macrofauna-zoet zelden het geval. Het gemiddelde per monster lijkt hier dan ook een betrouwbaarder berekening te zijn dan het gemiddelde over het gebied/deelgebied. 

Diversiteitsindexen worden niet gewogen naar substraat. Ook hier is de aanname dat er representatief wordt bemonsterd.

**Margalef**
De Margalef-index word gebaseerd op aantallen individuen. (https://search.r-project.org/CRAN/refmans/abdiv/html/margalef.html, https://www.sciencedirect.com/science/article/abs/pii/S1470160X09001253). Vanwege de grootte diversiteit aan bemonsteringstechnieken en monstergroottes is Margalef geen goede index voor de zoete wateren. 
Conform Deel-C, H9.3 KRM en OSPAR kan per Noordzee-meetpunt of voor de bemonsterde data een Margalef index moet worden berekend of niet. Deze configuratie kan worden ingesteld in config/locaties.csv. 
De Margalef wordt alleen als gemiddelde per monster berekend.

### 4.4 Dichtheid
De dichtheid wordt zowel voor de abundantie als de Biomassa bepaald. Monsters met een bemonsterd volume worden buiten beschouwing gelaten. 
Bij de kleine massa's wordt het limietsymbool '>' genegeerd.

### 4.5 Groepen
De dichtheden worden in staafdiagrammen over functionele groepen gepresenteerd.
Er zijn hiervoor drie groepsindelingen geconfigureerd, voor zoet, overgang en zout.
Deze groepsindelingen zijn gebaseerd op de TWN-groepen en kunnen worden verfijnd op basis van de taxonomische hiërarchie in de TWN.
De groepsindeling kan in de configuratie per waterlichaam worden gespecificeerd.

### 4.6 Trend
Vooral in de zoete Waterlichamen is de monsterinspanning over de jaren weinig constant. Om trends te kunnen laten zien wil je zoveel mogelijk gebruik maken van gelijke aantallen monsters en bemonsteringstechnieken over de jaren. Om hier grip op te krijgen kan per combinatie van locatie en bemonsteringstechniek de geschiktheid voor de trend worden geconfigureerd.
Per waterlichaam kan geconfigureerd worden hoeveel trend-monsters er minimaal per jaar aanwezig moeten zijn.

### 4.7 Fouten
Indien een data-issue middels een default kan worden opgelost zonder het eindresultaat geweld aan te doen dan wordt de default toegepast en krijgt de gebruiker hierover een melding in de logfile. Het script genereert in dezelfde run, zonder tussenkomst van de gebruiker de beoogde output.
Indien een issue niet middels een default kan worden opgelost, dan stopt het script met een foutmelding. De gebruiker moet handmatig de data aanpassen en het script vanaf de juiste stap opnieuw starten.

### 4.8 TWN
De TWN wordt iedere run automatisch gedownload. Fouten kunnen het beste worden doorgegeven aan: Functioneel beheer Aquadesk, zodat de TWN bij de bron verbeterd wordt.
Om toch verder te kunnen met de verwerking kunnen in config/twn_corrections.yaml fouten worden opgelost.

### 4.9 Bewaren van uitkomsten
De gebruiker moet de output eerst leegmaken voordat het script opnieuw gerund kan worden.

<div class="page"/>

## 5 Output
Alle door het script gegenereerde output komt in de map output met een uitsplitsing naar waterlichaam en eventueel seizoen en deelgebied/stratum/ecotoop.

### 5.1 Data
De door het script gedownloade en voorbewerkte data komt direct in de output folder
- *twn_download*: de TWN zoals gedownload
- *twn_gecorrigeerd*: de TWN na doorvoeren van correcties. Correcties worden geconfigureerd.
- *opgewerkte_data*: de Aquadesk data wordt verbeterd en verrijkt. De verrijking komt grotendeels uit de configuratie d.m.v. het toevoegen van Waterlichaam- en locatie-gegevens. Verbeteringen zijn deels hardcoded in het script en deels geconfigureerd. 
- *analyse_data*: dit is het geaggregeerd databestand waarin o.a. naast taxonwijzigingen de diversiteitsindeling is doorgerekend. 

### 5.2 Tabellen
Tabellarische analyse resultaten worden op verschillende niveaus weggeschreven.  
In de output folder: 
- *Monsters per jaar*: een overzicht van de trend en overige monsters per jaar per waterlichaam, gebied, seizoen, etc. Advies is om dit bestand te gebruiken om de kwaliteit van de output te duiden. Op waterlichaam niveau:
- *Nieuw_terug_verdwenen_per_WL*
- *BISI*
  
Op waterlichaam/seizoen gebied en/of stratum en/of ecotoop niveau:
- *Dichtheid_Aantal*
- *Dichtheid_Aantal - groep*
- *Dichtheid_Massa*
- *Dichtheid_Massa - groep*
- *Shannon*: Shannon van het areaal als geheel
- *Shannon_Monster*: Gemiddelde van de Shannon per monster
- *Soortenrijkdom*: Soortenrijkdom van het areaal als geheel
- *Soortenrijkdom_monster*: Gemiddelde van het aantal soorten per monster
- *Margalef_Monster*: Gemiddelde van de Margalef per monster. Wordt alleen berekend indien op locatieniveau geconfigureerd.
  
Alleen op het niveau van gebied en/of stratum en/of ecotoop:
- *Dichtheid_Aantal - pivot*: als draaitabel
- *Dichtheid_Massa - pivot*: als draaitabel
- *Shannon_Monster* - pivot: als draaitabel
- *Soortenrijkdom_Monster* - pivot: als draaitabel
- *Margalef_Monster* - pivot: als draaitabel
 
### 5.3 Figuren
De figuren zijn direct afgeleid van de hierboven beschreven tabellarische output.
Op alle niveaus
- *Dichtheid_Aantal*
- *Dichtheid_Aantal - groep*
- *Dichtheid_Massa*
- *Dichtheid_Massa - groep*
- *Shannon*
- *Shannon_Monster*
- *Soortenrijkdom*
- *Soortenrijkdom_monster*
Alleen per waterlichaam
- *Margalef_Monster*

<div class="page"/> 

## 6 Logging
Bij iedere run van het script wordt de logfile.log in de outputfolder opnieuw aangemaakt en gevuld. Er worden op verschillende niveaus meldingen gegenereerd. Het word aangeraden om na iedere run de meldingen in de logfile te controleren. Na een error- of critical-melding wordt het script gestopt. Via de prompt wordt de gebruiker er nogmaals op geattendeerd dat de log moet worden bekeken.

**debug**  
Debug-meldingen worden standaard niet weggeschreven. Deze kunnen tijdens werkzaamheden aan de code worden aangezet.

**info**  
Info-meldingen bevatten informatie over de keuzes die in het script zijn gemaakt. Ben je het als gebruiker niet eens met deze keuzes, dan kun je:
- handmatig het databestand in de input folder aanpassen en/of
- de configuratie aanpassen.

**warning**  
Warning-meldingen gaan over data-issues. Bij data-issues die niet standaard zijn op te lossen worden hele monsters of meetregels verwijderd. De gebruiker wordt hiervan met een melding in de logfile op de hoogte gebracht. Ook kwaliteitsaspecten, zoals te weinig monsters voor de BISI worden gemeld. Bij waarschuwingen gaat het script gewoon verder. Het is aan de gebruiker om te bepalen in hoeverre de uitkomsten bruikbaar zijn.

**error**  
Error-meldingen worden gegenereerd als er sprake is van een data of configuratie-fout. Het script stopt. Pas na een gebruikersactie kan het script opnieuw worden gerund.

**critical**  
Op meerdere plekken in het script wordt gecontroleerd op onlogische uitkomsten.
Naar alle verwachting gaat het hier om bugs in de code. Kritische meldingen moeten gerapporteerd aan RWS. 

<div class="page"/>

## 7. Beheer
In de map config staan de configuratiebestanden die het script op de achtergrond gebruikt. Bij normaal gebruik hoeft de gebruiker niet veel met deze bestanden te doen. 
Voor een correcte werking van het script moet een deel van de bestanden wel actief beheerd worden.
Alle configuratie bestanden zijn opgeslagen als tekstbestanden, .csv, of .yaml, zodat ze meedoen in het GIT versiebeheer. Alleen de BISI-rekensheet is een excel bestand.

### 7.1 Data-model
Het bestand data-model.csv beschrijft de benthosdata in de verschillende stadia van het script.
Dit bestand mag en hoeft niet aangepast te worden.
Veranderingen in dit bestand zullen meestal gepaard gaan met veranderingen in het script.

In tabel 1 worden de opbouw van het datamodel toegelicht. 

|kolomnaam|beschrijving|
|---|---|
|api_name|kolom in dd-eco-api v2 download|
|web_name|kolomnaam in download website Aquadesk|
|benthos_import|kolommen die geïmporteerd worden in het script|
|script_name|kolomnaam zoals in script gebruikt|
|not_null|kolommen die verplicht gevuld zijn|
|remark|opmerkingen, worden verder niet gebruikt|
|analysis_name|volledige lijst van kolommen, na uitvoering van alle voorbereidende scriptstappen|
|config|de data komt uit één van de configuratiebestanden|
|sample_property|de kolommen die uniek moeten zijn per monstercode

---
*tabel 1: beschrijving van het datamodel*

Het data bestand dat de gebruiker zelf aanbied moet voldoen aan de Aquadesk-specificaties.  De kolom 'web_name' bevat deze namen. De schrijfwijze van de kolomnamen moet exact overeenkomen. De regels met een waarde in de kolom 'script-name' zijn de minimaal benodigde. Een custom aangemaakt bestand kan dus minder kolommen bevatten dan voor een Aquadesk-upload noodzakelijk.

### 7.2 Waterlichamen
Het bestand waterbodies.csv bevat informatie over het waterlichamen, krw-type, of er seizoenen zijn, trendgroepen, determinatie- en biomassaprotocol, startjaar van de data, minimaal aantal monsters om voor trend te gelden. Het startjaar is 1999, behalve voor de Waddenzee (1987). Eventueel kan oudere data ook gebruikt worden, maar de kwaliteit is dan niet gegarandeerd want hier is niet op getest.
Deze configuratie-tabel moet actief worden beheerd door RWS. Niet of slecht gedefinieerde Waterlichamen zorgen voor verwerkingsproblemen.

### 7.3 Locaties
Het bestand locations.csv bevat de meetobjectcodes, locatiecodes, projectcodes, de indeling in waterlichamen, gebieden, strata en de indeling in de BISI elementen. Ook bevat deze tabel informatie over het bemonsteringsapparaat/methode, gebruik voor de trend en of de Margalef moet worden berekend. Deze configuratie-tabel moet actief worden beheerd door RWS. Niet of slecht gedefinieerde Waterlichamen zorgen voor verwerkingsproblemen.

### 7.4 BISI
Het beheer van de BISI-excel ligt bij Sander Wijnhoven. Het script gebruikt gebruikt de door Sander gedefinieerde rekenfunctionaliteit. Het script kopieert de BISI-excel van config naar de output folder. In de output folder word de BISI-excel gevuld. Om de juiste gegevens in de juiste werkbladen in te vullen zijn een minimaal aantal benodigde variabele verwijzingen in de BISI-config vastgelegd.

De BISI-excel bestaat uit een aantal werkbladen, per N2000-gebied, eunis of habitat 1. Op deze werkbladen kunnen meerdere rekenbereiken onder elkaar staan staan. 

> Bijvoorbeeld  
Voor de Doggerbank is er het werkblad 'DB v3'. Op het werkblad staan de rekenbereiken voor: Doggerbank (HR-area), Doggerbank (open area 'DB-Noord') en Doggerbank (open area 'DB-Zuid') onder elkaar.

In de locations.csv config staat per locatie aangegeven voor welk BISI-rekenbereik de locatie/monsterapparaat combinatie relevant is.
In de BISI_config.csv worden de BISI aanduiding in location.csv gelinkt aan het juiste werkblad en rekenbereik.

Het script gaat uit van een vaste opbouw die voor alle rekenbereiken identiek is.
Het script gebruikt de gegevens van kolom A voor de navigatie. Het script gaat hier van boven naar onder door heen. In de kolommen M, N, O worden vervolgens de juiste waarden gezet.

Het script controleert de gebruikte taxonnamen op TWN geldigheid. Eventuele taxon-naamsveranderingen moeten in de BISI-excel worden aangepast. Aangezien de BISI uitgaat van redelijk algemene taxa, moet met Sander worden afgestemd wat en of er consequenties zijn aan de naamsverandering(en).
De bemonsteringsapparaten zijn een combinatie van het bemonsteringsapparaat en bemonsterde oppervlakte. Deze codering wordt via de BISI-config vertaald naar de monsterapparaten in de Aquadesk-data.


#### 7.4.1 Nieuwe BISI
Voordat een nieuwe versie van de BISI-excel gebruikt kan worden moet de layout gecontroleerd worden en evt. testwaarden moeten verwijderd worden.

**Controle**  
Controleer voor ieder werkblad of:  
-  de naam exact zo gespeld is in de BISI-config.

Zo niet dan moet dit aangepast worden in de configuratie.

Controleer voor ieder werkblad voor ieder rekenbereik of:
- kolom H de bemonsteringstechniek bevat
- kolom K het verwacht aantal monsters bevat
- in kolom M het bemonsterd aantal monsters moet worden ingevuld, 
- in kolom N de dichtheid moet worden ingevuld,
- in kolom O de standaarddeviatie moeten worden ingevuld.

Zo niet dan moet het script hierop aangepast worden.

Controleer voor ieder werkblad, in kolom A, voor ieder rekenbereik of:
- de naam van het bereik (bijvoorbeeld: Doggerbank (HR-area)) exact zo wordt gespeld in de BISI-config.  
  Zo niet dan moet de BISI-config aangepast worden. 
- of de volgende cel NIET leeg is. Idealiter staat daar iets als 'Indicator soorten', maar dat is niet verplicht.
- in de cellen direct daaronder staan alleen maar taxonnamen. Er staan geen lege cellen tussen de taxa.
- na het laatste taxonnaam van het rekenbereik staat minimaal één lege regel (minimaal de cellen A t/m Q zijn leeg).

Indien er nieuwe werkbladen of rekenbereiken aan de BISI-excel zijn toegevoegd dan moet de configuratie uitgebreid worden:
- de BISI-config moet uitgebreid worden met extra regels, afhankelijk van het aantal nieuwe rekenbereiken
- de location.csv moet aangevuld met de extra BISI indeling(en) in één van de BISI-kolommen. Indien noodzakelijk kan een nieuwe BISI-kolom worden toegevoegd.
- global_variables.yaml moet worden aangepast indien een nieuwe BISI-kolom wordt toegevoegd aan location.csv. De nieuwe BISI-kolom moet toegevoegd aan de lijst 'bisi_area_columns'.


**Verwijderen** 
Het kan zijn dat de BISI door Sander wordt aangeleverd met testdata. Deze data moet worden verwijderd.

Verwijder op alle werkbladen uit kolom A de jaartallen. Voor de gebieden die gevuld worden, wordt door het script het juiste jaartal gevuld. 

Verwijder op alle werkbladen uit kolom M, N, O de aanwezige getallen. Het script vult deze waar nodig.

Een nieuwe BISI-excel moet ook getest met de pytest test_bisi_main. Deze test leest voor alle rekenbereiken, voor alle taxa en bemonsteringsapparaten data in en vult de excel. De excel moet handmatig nagekeken worden. Alle taxa moeten een dichtheid hebben van 1 of hoger.

### 7.5 BISI config
Het bestand bisi_config.csv bevat de benodigde koppelingen tussen de data en het vullen van de BISI tabel:
- Koppeling tussen de BISI indeling (uit locations.csv) en de indeling in een van de rijen in de BISI Excel tabel. Ook de sheet naam uit de BISI tabel wordt hieraan gekoppeld.
- Koppeling tussen het bemonsteringsapparaat/methode (uit locations.csv) en de methodes (sampling techniques) uit de BISI tabel. 

### 7.6 Exotics
De tabel exotics.csv is een tabel met TWN taxa namen die moeten worden gemarkeerd als exoot. Dit wordt gebruikt voor de nieuw, verdwenen en teruggevonden soorten tabel.

### 7.7 Taxongroep classificatie
De tabel taxon_groups.csv bevat de trendgroepen, taxongroepen(codes), de groepen, hiërarchie en de kleuren voor de grafieken met soortgroepen. Bij het kiezen van deze kleuren is zoveel mogelijk rekening gehouden met kleurenblindheid. De groepsindeling kan hier aangepast worden, evenals de gebruikte kleuren. Eventueel kunnen er ook groepsindelingen worden toegevoegd. Zorg ervoor dat alle TWN-taxongroepen vertalen naar een groep. De nieuwe groepsindeling moet een nieuwe naam krijgen in de kolom trendgroep. Deze nieuwe naam kan in waterbody.csv in de kolom Trendgroep worden opgenomen.

### 7.8 Taxonomische rangen
De tabel taxonomic_order.csv wordt gebruikt om de rangorde toe te kennen aan de TWN-taxa. 

### 7.9 Typische soorten habitatgebieden
De tabel typical_species_habitat_protected_areas.csv bevat de typische soorten voor verschillende habitattypen. Deze soorten komen uit de profielen van de habitattypen (https://www.natura2000.nl/beschermde-natuur/habitattypen). De typische soorten worden gemarkeerd in de soortenlijst die wordt gegenereerd als output.

### 7.10 Yaml bestanden
Er zijn een aantal .yaml bestanden als configuratie:
- Aquadesk: de configuraties voor de dataparser voor de ddecoapi voor het downloaden van de Aquadesk- en de TWN-data.
- Aquadesk_corrections: de correcties die worden gedaan aan de (Aquadesk) data zodat deze conform de TWN is.
- global_variables: alle paden naar bestanden (input, output, configs) en variabelen voor gebiedsindelingen en figuren.
- hierarchy: bevat de analyseprotocol-afspraken voor determinatie-niveau presentie en biomassa naar zoet en zout.
- twn_corrections: de correcties die worden gedaan aan de TWN.
- clustered_sample_year: per waterlichaam en bemonsteringsapparaat welke jaren geclusterd moeten worden.


### 7.11 Technische documentatie
In de map sphinx_docs staat alles wat nodig is om de PDF met de technische documentatie te maken o.b.v. de docstring in de modules. Voor het genereren van de technische documentatie moeten wrs extra programma's als MikTeX en Perl worden geïnstalleerd.

Generen van technische documentatie kan met de volgende commando's:
1. Ga naar de sphinx_docs folder: `cd sphinx_docs`
2. Maak de _build en _autosummary folder leeg: `make clean`
3. Maak de latex pdf: `make latexpdf`

Zoals de terminal laat zien, is het bestand opgeslagen in de folder `._build/latex`

<div class="page"/>

## 8. Credits
### Auteurs
* Joyce Haringa, Waardenburg Ecology
* Maarten Japink, Waardenburg Ecology

### Inhoudelijke begeleiding
* Wouter Abels, Rijkswaterstaat
* Laura Hesp, Rijkswaterstaat
* Harm de Coninck, Rijkswaterstaat
* Anke Engelberts, Rijkswaterstaat
* Iris van Santbrink, Rijkswaterstaat
<br>

## 9. Licentie
Dit script is eigendom van Rijkswaterstaat CIV. De code wordt beschikbaar gesteld volgens het open-source principe en is vrij van copyright. 

## 10. Disclaimer
Dit script is ontworpen voor het genereren van tabellen en figuren op basis van de verstrekte configuratie en data. Hoewel de grootst mogelijke zorg is besteed aan de ontwikkeling van dit script, wordt het geleverd zoals het is, zonder enige garantie, expliciet of impliciet.

De gebruiker en opdrachtgever zijn zelf verantwoordelijk voor het begrijpen van de configuratie en het valideren van de aangeleverde data. Het gebruik van dit script impliceert dat de gebruiker akkoord gaat met het aanvaarden van alle risico's die verbonden zijn aan het gebruik van deze configuratie en data.

De auteurs en distributeurs van dit script aanvaarden geen aansprakelijkheid voor verlies, schade of kosten die voortvloeien uit het gebruik van, of vertrouwen op, gegenereerde tabellen en figuren. Het wordt sterk aanbevolen om de resultaten grondig te controleren en te valideren voordat ze worden toegepast in een officiële context.

Dit script is bedoeld als een hulpmiddel voor datavisualisatie en mag niet worden beschouwd als een vervanging voor professioneel advies. Gebruikers worden aangemoedigd om het script te testen en te evalueren in overeenstemming met hun specifieke vereisten voordat het in een productieomgeving wordt ingezet. 