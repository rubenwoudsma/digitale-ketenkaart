# Blog-outline

## Werktitel

**De gemeentelijke website is geen eiland: de digitale keten achter gemeente Huizen**

Alternatieven:

- **De website staat misschien in Nederland, maar waar loopt de digitale keten naartoe?**
- **Van huizen.nl naar cloud, mail en scripts: waarom digitale gemeentelijke dienstverlening meer is dan hosting**
- **Wie helpt mee achter het digitale loket van de gemeente? Een publieke analyse van Huizen**

## Centrale boodschap

Voor inwoners lijkt digitale dienstverlening vaak eenvoudig: je bezoekt een website, vult een formulier in of stuurt een bericht. Achter die handeling zit meestal een keten van organisaties en technische diensten.

In deze analyse zijn 24 domeinen en gelieerde digitale diensten rond gemeente Huizen onderzocht. De scan laat zien dat hostinglocatie maar één deel van het verhaal is. Via mail, formulieren, scripts, CDN’s, analytics, toegankelijkheidsdiensten en SaaS ontstaat een bredere digitale keten.

De analyse toont geen overtreding aan en bewijst niet dat gegevens buiten Europa worden opgeslagen. De analyse laat wel zien dat publiek vaak zichtbaar is dát leveranciers betrokken zijn, maar niet welke gegevens precies worden verwerkt, waar logs en back-ups staan, welke subverwerkers worden gebruikt en welke contractuele waarborgen gelden.

## Mogelijke inleiding

Wie online contact heeft met een gemeente, verwacht waarschijnlijk dat hij of zij zich binnen de digitale overheid bevindt. Je bezoekt een gemeentelijke website, opent een pagina, vult een formulier in, bekijkt een video of stuurt een e-mail.

Maar een moderne gemeentelijke website is zelden één website. Achter de voorkant zit vaak een netwerk van domeinen, maildiensten, formulieren, toegankelijkheidsdiensten, cloudplatformen, analytics, beveiligingsdiensten, uitvoeringsorganisaties en leveranciers.

De casus Huizen laat zien waarom een overzicht van alleen gemeentelijke domeinen niet genoeg is. De echte vraag is niet alleen: “Waar staat de website?” De betere vraag is: “Welke digitale keten ontstaat zodra een inwoner een gemeentelijke dienst gebruikt?”

## 1. Aanleiding: transparantie begint bij weten welke websites erbij horen

Gemeente Huizen lijkt geen volledig publiek domeinoverzicht te gebruiken via het Register Internetdomeinen Overheid. Dat is jammer, want zo’n register kan inwoners helpen controleren of een website of e-mailadres echt bij een overheid hoort.

Maar zelfs als zo’n domeinenregister volledig zou zijn, blijft er een groter probleem bestaan. Gemeenten werken via samenwerkingen, uitvoeringsorganisaties, leveranciers, gemeenschappelijke regelingen en verbonden partijen. Daardoor ligt een deel van de digitale dienstverlening buiten het hoofddomein van de gemeente.

Een inwoner ervaart zo’n dienst vaak nog steeds als “de gemeente”, maar de techniek, verantwoordelijkheid en gegevensverwerking kunnen verspreid zijn over meerdere partijen.

## 2. Methode: publieke, niet-invasieve analyse

Voor deze analyse is gekeken naar publiek zichtbare informatie, waaronder:

- domeinen en subdomeinen
- DNS-records
- MX- en SPF-records voor e-mail
- HTTPS en beveiligingsheaders
- externe scripts en embeds
- hosting- en netwerkindicatoren
- leveranciersindicatoren
- publieke verwijzingen tussen websites

De analyse is geen pentest, geen kwetsbaarheidsscan en geen poging om systemen binnen te dringen. Het gaat om informatie die publiek zichtbaar is en die iets zegt over de digitale keten.

## 3. Van website naar keten

Een websitebezoek lijkt eenvoudig, maar achter de schermen kunnen verschillende lagen betrokken zijn:

- de webserver of hostingprovider
- een CDN of beveiligingsdienst
- scripts in de browser
- analytics of tag management
- video-embeds
- toegankelijkheidsdiensten
- formulierenleveranciers
- mailplatformen
- SaaS-applicaties
- logging en monitoring

Daarom is hostinglocatie alleen onvoldoende om digitale soevereiniteit te beoordelen. Een website kan in Nederland gehost zijn, terwijl mail, scripts, logging, support of SaaS via internationale leveranciers lopen.

## 4. Wat zichtbaar wordt in de casus Huizen

De publieke analyse laat meerdere leveranciersindicatoren zien. Voorbeelden zijn:

- Microsoft 365 / Exchange Online in de mailketen
- Google Tag Manager, Google APIs, Google Analytics en YouTube als frontend- of analyticsindicatoren
- Cloudflare als CDN/WAF/DNS-indicator
- Zivver, TOPdesk, Formulierenserver en Flowmailer als mail-, formulier- of SaaS-indicatoren
- SIMgroep, ReadSpeaker, Siteimprove en Cookiebot / Usercentrics als website-, toegankelijkheids-, analytics- of consentdiensten

Belangrijk: een leverancier in deze lijst betekent niet automatisch dat persoonsgegevens daar worden opgeslagen. Het betekent dat de leverancier publiek zichtbaar is in de technische keten en daarom relevant is voor verificatie.

## 5. Hosting is niet hetzelfde als digitale soevereiniteit

In discussies over digitale soevereiniteit wordt vaak gevraagd waar een website wordt gehost. Dat is belangrijk, maar het is niet genoeg.

Digitale soevereiniteit gaat ook over:

- wie de leverancier is
- onder welke jurisdictie de leverancier valt
- waar data, logging en back-ups worden opgeslagen
- wie supporttoegang heeft
- welke subverwerkers worden gebruikt
- welke metadata wordt verwerkt
- welke contractuele waarborgen bestaan
- welke alternatieven beschikbaar zijn

Een Nederlandse hostinglocatie kan dus samengaan met internationale afhankelijkheden in mail, scripts, cloud, analytics of CDN’s.

## 6. De privacyverklaring is niet de ketenkaart

Een privacyverklaring kan juridisch nuttig zijn, maar geeft voor inwoners vaak onvoldoende zicht op de feitelijke digitale keten.

Een inwoner kan meestal niet zien:

- welke leveranciers op welke domeinen actief zijn
- welke scripts of tags worden geladen
- waar logging en back-ups staan
- welke subverwerkers zijn betrokken
- welke supporttoegang mogelijk is
- of gegevens of metadata buiten de EU kunnen worden verwerkt
- hoe samenwerkingen en verbonden partijen digitaal zijn ingericht

Daarom is een privacyverklaring niet hetzelfde als een digitale ketenkaart.

## 7. Wat deze analyse niet bewijst

Deze analyse bewijst niet dat gemeente Huizen regels overtreedt. De analyse bewijst ook niet dat persoonsgegevens buiten Europa worden opgeslagen.

Wat de analyse wel laat zien:

- er zijn publieke indicatoren van meerdere leveranciers en technische diensten
- hosting is slechts één onderdeel van de digitale keten
- mail, scripts, formulieren, CDN’s en SaaS kunnen extra afhankelijkheden creëren
- inwoners kunnen deze keten niet eenvoudig controleren
- aanvullende informatie van de gemeente of leveranciers is nodig om de situatie goed te beoordelen

Juist dat laatste is de kern: het probleem is niet alleen technisch, maar ook bestuurlijk en transparantiegericht.

## 8. Wat nog geverifieerd moet worden

De analyse leidt tot concrete verificatievragen, onder andere over:

- Microsoft 365 en Azure
- OGD als beheer- en cloudpartner
- Google Tag Manager en actieve tags
- Google Analytics, YouTube en Google APIs
- Cloudflare of vergelijkbare CDN/WAF-diensten
- Zivver, TOPdesk, Formulierenserver, Flowmailer en Mailgun
- logging, back-ups, supporttoegang en subverwerkers
- cloudregio’s, tenantinstellingen en datalocaties
- DPIA’s, risicoanalyses en BIO-classificaties

Deze vragen kunnen worden gebruikt voor vervolgonderzoek of een Woo-verzoek.

## 9. Oplossing: publiceer een digitale ketenkaart

Gemeenten zouden niet alleen een lijst met domeinen moeten publiceren, maar een digitale ketenkaart.

Zo’n kaart bevat per digitale dienst:

- domein of URL
- verantwoordelijke organisatie
- leverancier
- doel van de dienst
- categorieën gegevens
- hostinglocatie
- cloudregio
- subverwerkers
- betrokken derde partijen
- contactpunt
- laatste controle
- relevante standaarden en beveiligingsmaatregelen

Dat hoeft geen kwetsbaarheden of beveiligingsgeheimen prijs te geven. Het gaat om bestuurlijke en juridische transparantie: wie doet wat, namens wie, met welke gegevens en onder welke afspraken?

## 10. Conclusie

De casus Huizen laat zien dat digitale gemeentelijke dienstverlening niet stopt bij het hoofddomein van de gemeente. Achter websites en formulieren zit een bredere keten van leveranciers, platforms, samenwerkingen en technische diensten.

De centrale vraag is daarom niet alleen waar de website staat. De vraag is welke digitale keten ontstaat zodra een inwoner een pagina opent, mailt, een formulier invult of een gemeentelijke dienst gebruikt.

Zolang die keten niet publiek inzichtelijk is, blijft digitale transparantie onvolledig.

## Mogelijke slotzin

> Een domeinenregister laat zien waar de voordeur zit. Een digitale ketenkaart laat zien wie er achter die voordeur allemaal meedoen.
