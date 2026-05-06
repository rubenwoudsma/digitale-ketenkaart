# Woo-vragenpakket: digitale keten gemeente Huizen

## Doel van het verzoek

Dit verzoek is bedoeld om de publieke digitale keten rond gemeente Huizen te verduidelijken. De publieke scan toont technische indicatoren, maar kan niet vaststellen waar data, logs en back-ups staan, welke subverwerkers betrokken zijn, welke contractuele waarborgen gelden en welke interne systemen gekoppeld zijn.

## Algemene vragen

- Graag een overzicht van alle domeinen en subdomeinen die gemeente Huizen beheert of laat beheren.
- Graag een overzicht van websites, SaaS-platformen en externe digitale diensten die worden gebruikt voor publieke dienstverlening.
- Graag per domein of dienst: verantwoordelijke organisatie, verwerker, leverancier, subverwerkers en doel van verwerking.
- Graag per domein of dienst: of persoonsgegevens worden verwerkt, welke categorieën persoonsgegevens, en of bijzondere of gevoelige gegevens kunnen voorkomen.
- Graag per domein of dienst: hostinglocatie, cloudregio, logginglocatie, back-uplocatie en bewaartermijnen.
- Graag per domein of dienst: of leveranciers of subverwerkers onder niet-EU jurisdictie vallen, en welke aanvullende waarborgen daarvoor zijn getroffen.
- Graag het beleid van de gemeente rond cloudgebruik, digitale soevereiniteit en inzet van niet-Europese leveranciers.
- Graag beschikbare DPIA's, risicoanalyses of BIO-classificaties voor de onderzochte digitale diensten, voor zover openbaar te maken.

## Leveranciersgerichte vragen

### Microsoft 365 / Exchange Online

- Type: mail/cloud
- Jurisdictie-indicatie: US supplier, EU region possible
- Aantal domeinen met indicator: 16
- Mogelijke datacategorieën: email content, email metadata, account identifiers
- Welke Microsoft 365 tenantregio, workloads, logginglocaties, supporttoegang en subverwerkers zijn van toepassing?

### Google Tag Manager

- Type: tag management / analytics enabler
- Jurisdictie-indicatie: US supplier
- Aantal domeinen met indicator: 10
- Mogelijke datacategorieën: browser metadata, event data, tags loaded by configuration
- Welke tags zijn actief binnen Google Tag Manager en welke persoonsgegevens of identifiers worden verwerkt?

### YouTube

- Type: embedded media
- Jurisdictie-indicatie: US supplier
- Aantal domeinen met indicator: 8
- Mogelijke datacategorieën: browser metadata, viewing data, cookies possible
- Worden YouTube embeds privacyvriendelijk geladen en is toestemming of een alternatief ingericht?

### Cloudflare

- Type: CDN/WAF/DNS
- Jurisdictie-indicatie: US supplier, global edge
- Aantal domeinen met indicator: 7
- Mogelijke datacategorieën: IP address, headers, request metadata, security logs
- Welke Cloudflare-diensten worden gebruikt, waar worden logs verwerkt en welke dataverwerkingsafspraken gelden?

### Google Analytics

- Type: analytics
- Jurisdictie-indicatie: US supplier
- Aantal domeinen met indicator: 2
- Mogelijke datacategorieën: analytics identifiers, browser metadata, usage data
- Wordt Google Analytics gebruikt, hoe is IP-anonimisering ingericht, en welke doorgiftewaarborgen bestaan?

### Mailgun

- Type: transactional email
- Jurisdictie-indicatie: US supplier
- Aantal domeinen met indicator: 2
- Mogelijke datacategorieën: email content, recipient metadata, delivery logs
- Welke mailstromen lopen via Mailgun en welke bewaartermijnen en subverwerkers gelden?

### Google APIs

- Type: frontend / API / SaaS
- Jurisdictie-indicatie: US supplier
- Aantal domeinen met indicator: 9
- Mogelijke datacategorieën: browser metadata, IP address, request metadata, usage data possible
- Welke Google-diensten worden geladen, met welk doel, en is lokaal hosten of Europese alternatieven mogelijk?

### Zivver

- Type: secure email
- Jurisdictie-indicatie: NL/EU supplier
- Aantal domeinen met indicator: 6
- Mogelijke datacategorieën: secure email content, recipient metadata, access logs
- Welke berichtenstromen lopen via Zivver en welke subverwerkers en hostinglocaties worden gebruikt?

### ReadSpeaker

- Type: accessibility / text-to-speech
- Jurisdictie-indicatie: EU supplier with international presence
- Aantal domeinen met indicator: 6
- Mogelijke datacategorieën: requested page text, IP address, browser metadata possible
- Welke gegevens worden door ReadSpeaker verwerkt en waar worden logs opgeslagen?

### Siteimprove

- Type: analytics / accessibility / quality monitoring
- Jurisdictie-indicatie: EU supplier with international presence
- Aantal domeinen met indicator: 5
- Mogelijke datacategorieën: website usage, quality metrics, browser metadata possible
- Welke Siteimprove-modules zijn actief en worden persoonsgegevens of identifiers verwerkt?

### SIMgroep

- Type: municipal website / CMS / CDN
- Jurisdictie-indicatie: NL/EU supplier
- Aantal domeinen met indicator: 4
- Mogelijke datacategorieën: website content, forms, usage logs, citizen interactions possible
- Welke SIMgroep-diensten worden gebruikt en welke hosting, CDN, logging en subverwerkers zijn van toepassing?

### TOPdesk

- Type: service management / SaaS
- Jurisdictie-indicatie: NL/EU supplier
- Aantal domeinen met indicator: 3
- Mogelijke datacategorieën: tickets, contact details, internal service data
- Welke TOPdesk-omgeving wordt gebruikt, waar staat deze gehost en welke subverwerkers gelden?

### Formulierenserver

- Type: forms / e-government SaaS
- Jurisdictie-indicatie: NL/EU supplier
- Aantal domeinen met indicator: 1
- Mogelijke datacategorieën: form submissions, contact details, potentially sensitive citizen data
- Welke formulieren lopen via Formulierenserver, waar worden inzendingen, bijlagen en logs opgeslagen?

### Flowmailer

- Type: transactional email
- Jurisdictie-indicatie: NL/EU supplier
- Aantal domeinen met indicator: 1
- Mogelijke datacategorieën: email content, recipient metadata, delivery logs
- Welke mailstromen lopen via Flowmailer en waar worden inhoud, metadata en logs verwerkt?

### Cookiebot / Usercentrics

- Type: cookie consent management
- Jurisdictie-indicatie: EU supplier
- Aantal domeinen met indicator: 1
- Mogelijke datacategorieën: consent preferences, browser metadata possible
- Welke consentgegevens worden opgeslagen, waar en met welke subverwerkers?

## Domeinen met hoogste prioriteit

- **huizenduurzaam.nl** (P1): 4 P1-verificatievragen; 5 leverancier(s) met US-indicatie; 4 leverancier(s) met hoog datarisico
- **sro.nl** (P1): 4 P1-verificatievragen; 5 leverancier(s) met US-indicatie; 4 leverancier(s) met hoog datarisico
- **gad.nl** (P1): 3 P1-verificatievragen; 4 leverancier(s) met US-indicatie; 4 leverancier(s) met hoog datarisico
- **readspeaker.com** (P1): 3 P1-verificatievragen; 4 leverancier(s) met US-indicatie; 3 leverancier(s) met hoog datarisico
- **tomingroep.nl** (P1): 3 P1-verificatievragen; 3 leverancier(s) met US-indicatie; 5 leverancier(s) met hoog datarisico
- **visitgooivecht.nl** (P1): 3 P1-verificatievragen; 3 leverancier(s) met US-indicatie; 4 leverancier(s) met hoog datarisico
- **energieloketten.nl** (P1): 3 P1-verificatievragen; 3 leverancier(s) met US-indicatie; 3 leverancier(s) met hoog datarisico
- **regiogv.nl** (P1): 2 P1-verificatievragen; 3 leverancier(s) met US-indicatie; 3 leverancier(s) met hoog datarisico
- **gnr.nl** (P1): 2 P1-verificatievragen; 3 leverancier(s) met US-indicatie; 2 leverancier(s) met hoog datarisico
- **randmeren.com** (P1): 2 P1-verificatievragen; 3 leverancier(s) met US-indicatie; 2 leverancier(s) met hoog datarisico
- **huizen.nl** (P1): 2 P1-verificatievragen; 2 leverancier(s) met US-indicatie; 7 leverancier(s) met hoog datarisico
- **archiefgooienvechtstreek.nl** (P1): 2 P1-verificatievragen; 2 leverancier(s) met US-indicatie; 2 leverancier(s) met hoog datarisico

## Toelichting bij de publieke scan

De bijlage met publieke indicatoren is geen kwetsbaarheidsscan en bevat geen bewijs dat gegevens buiten de EU worden opgeslagen. De indicatoren tonen wel welke leveranciers en technische ketens publiek zichtbaar zijn. Het verzoek richt zich daarom op verificatie van de ontbrekende context.
