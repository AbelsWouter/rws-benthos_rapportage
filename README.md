# Python script voor RWS rapportage protocol deel C 
<br> <br>

<p align="center">
  <img alt="Light" src="https://waardenburg.eco/images/logo.svg" width="35%">
&nbsp; &nbsp; &nbsp; &nbsp;
  <img alt="Dark" src="https://www.rijkswaterstaat.nl/static/img/logo-nl.svg" width="45%">
</p>


## Beschrijving
Dit Python-script is ontworpen om benthosgegevens te verwerken volgens de specificaties van het KRW en KRM-monitoringprogramma van Rijkswaterstaat, zoals verwoord in protocol Bijlage Deel C. Het script automatiseert het genereren van benodigde parameters en uitvoeren van data-analyses voor de meetnetten macrozoöbenthos in zoete en zoute rijkswateren.

## Info
Voor eer inhoudelijke informatie met betrekking tot de rapportage van het monitoringsprogramme zie, https://waterinfo-extra.rws.nl/monitoring/biologie/bodemdieren/.

## Vereisten
Minimaal Python versie 3.12 en Poetry als package manager.

## Installatie

1. Pak de ontvangen zipfile uit of kloon de repository
```cmd/terminal
git clone git@github.com:AbelsWouter/rws-benthos_rapportage.git
```

2. Installeer de vereiste bibliotheken:
```cmd/terminal
poetry install
```

Zie voor uitgebreide installatie instructies de gebruikers-en beheerdershandleiding.

## Gebruik
Allereerst moeten de te verwerken project(en) en waterlichaam(en) worden geselecteerd.
Uncomment de gewenste instellingen in ./input/selectie_waterlichaam.txt en ./input/selectie_project.txt.
Ook dient er in ./configs/aquadesk.yaml een juiste API KEY ingevoerd te worden, deze is op te vragen via aquadesk@rws.nl.

```cmd/terminal
python main.py
```

Zie voor een uitgebreide handleiding de gebruikers-en beheerdershandleiding.

## Invoerbestandsindeling
De gebruiker kan een eigen bestand met Benthos-monitoringsdata aanbieden in de map ./input. Deze moet voldoen aan de eisen gesteld aan het Aquadesk import/export .xlsx-formaat.
Indien er geen eigen bestand wordt aangeboden, wordt de selectie uit de Aquadesk gedownload.

Zie voor een uitgebreide beschrijving de gebruikers-en beheerdershandleiding.

## Uitvoer
Het script genereert een aantal Excel-bestanden en grafieken in .png format. 
De aquadesk download wordt in de map ./input opgeslagen.
De resultaat bestanden worden in de map ./output weggeschreven.

Zie voor een uitgebreide beschrijving de gebruikers-en beheerdershandleiding.

## Licentie
Dit script is eigendom van Rijkswaterstaat CIV. De code wordt beschikbaar gesteld volgens het open-source principe en zijn vrij van copyright. 

## Auteurs
* Joyce Haringa, Waardenburg Ecology
* Maarten Japink, Waardenburg Ecology

## Inhoudelijke begeleiding
* Wouter Abels, Rijkswaterstaat

## Disclaimer
Dit script is ontworpen voor het genereren van tabellen en figuren op basis van de verstrekte configuratie en data. Hoewel de grootst mogelijke zorg is besteed aan de ontwikkeling van dit script, wordt het geleverd zoals het is, zonder enige garantie, expliciet of impliciet.

De gebruiker en opdrachtgever zijn zelf verantwoordelijk voor het begrijpen van de configuratie en het valideren van de aangeleverde data. Het gebruik van dit script impliceert dat de gebruiker akkoord gaat met het aanvaarden van alle risico's die verbonden zijn aan het gebruik van deze configuratie en data.

De auteurs en distributeurs van dit script aanvaarden geen aansprakelijkheid voor verlies, schade of kosten die voortvloeien uit het gebruik van, of vertrouwen op, gegenereerde tabellen en figuren. Het wordt sterk aanbevolen om de resultaten grondig te controleren en te valideren voordat ze worden toegepast in een officiële context.

Dit script is bedoeld als een hulpmiddel voor datavisualisatie en mag niet worden beschouwd als een vervanging voor professioneel advies. Gebruikers worden aangemoedigd om het script te testen en te evalueren in overeenstemming met hun specifieke vereisten voordat het in een productieomgeving wordt ingezet. 