# Kernbevindingen: digitale keten gemeente Huizen

## Samenvatting

- Onderzochte domeinen: **24**
- Datastroomindicatoren: **301**
- Unieke leveranciers of diensten: **15**
- Domeinen met US-leveranciersindicatie: **24**
- P1-verificatievragen: **45**
- P2-verificatievragen: **24**

## Belangrijkste leveranciersindicatoren

| supplier                        | supplier_type                                  | jurisdiction_groups                     |   domains_count | highest_data_risk   |   p1_questions_count | example_domains                                                                                                                             |
|:--------------------------------|:-----------------------------------------------|:----------------------------------------|----------------:|:--------------------|---------------------:|:--------------------------------------------------------------------------------------------------------------------------------------------|
| Microsoft 365 / Exchange Online | mail/cloud                                     | US supplier, EU region possible         |              16 | high                |                   16 | huizen.nl, maatschappelijkezaken.nl, belastingenhbl.nl, sro.nl, regiogv.nl, gad.nl, vrgooienvechtstreek.nl, tomingroep.nl, +8 meer          |
| Google Tag Manager              | tag management / analytics enabler             | US supplier                             |              10 | high                |                   10 | sro.nl, regiogv.nl, gad.nl, tomingroep.nl, dekringloper.nl, randmeren.com, gnr.nl, visitgooivecht.nl, +2 meer                               |
| YouTube                         | embedded media                                 | US supplier                             |               8 | medium/high         |                    8 | huizen.nl, www.huizen.nl, ris.gemeenteraadhuizen.nl, sro.nl, gad.nl, bngbank.nl, visitgooivecht.nl, readspeaker.com                         |
| Cloudflare                      | CDN/WAF/DNS                                    | US supplier, global edge                |               7 | medium/high         |                    7 | tomingroep.nl, archiefgooienvechtstreek.nl, huizenduurzaam.nl, energieloketten.nl, regionaalenergieloket.nl, archiefweb.eu, readspeaker.com |
| Google Analytics                | analytics                                      | US supplier                             |               2 | high                |                    2 | sro.nl, randmeren.com                                                                                                                       |
| Mailgun                         | transactional email                            | US supplier                             |               2 | medium/high         |                    2 | huizenduurzaam.nl, energieloketten.nl                                                                                                       |
| Google APIs                     | frontend / API / SaaS                          | US supplier                             |               9 | medium              |                    0 | formulieren.huizen.nl, sro.nl, regiogv.nl, gad.nl, randmeren.com, gnr.nl, huizenduurzaam.nl, archiefweb.eu, +1 meer                         |
| Zivver                          | secure email                                   | NL/EU supplier                          |               6 | medium/high         |                    0 | huizen.nl, regiogv.nl, gad.nl, tomingroep.nl, dekringloper.nl, visitgooivecht.nl                                                            |
| ReadSpeaker                     | accessibility / text-to-speech                 | EU supplier with international presence |               6 | low/medium          |                    0 | huizen.nl, www.huizen.nl, maatschappelijkezaken.nl, belastingenhbl.nl, ris.gemeenteraadhuizen.nl, readspeaker.com                           |
| Siteimprove                     | analytics / accessibility / quality monitoring | EU supplier with international presence |               5 | medium              |                    0 | huizen.nl, www.huizen.nl, maatschappelijkezaken.nl, belastingenhbl.nl, archiefgooienvechtstreek.nl                                          |
| SIMgroep                        | municipal website / CMS / CDN                  | NL/EU supplier                          |               4 | medium/high         |                    0 | huizen.nl, www.huizen.nl, maatschappelijkezaken.nl, belastingenhbl.nl                                                                       |
| TOPdesk                         | service management / SaaS                      | NL/EU supplier                          |               3 | medium/high         |                    0 | huizen.nl, tomingroep.nl, ofgv.nl                                                                                                           |

## Domeinen met hoogste prioriteit

| domain                      | priority   | personal_data_likelihood   |   us_supplier_count |   high_risk_supplier_count |   p1_questions_count | priority_reason                                                                                 |
|:----------------------------|:-----------|:---------------------------|--------------------:|---------------------------:|---------------------:|:------------------------------------------------------------------------------------------------|
| huizenduurzaam.nl           | P1         | Mogelijk                   |                   5 |                          4 |                    4 | 4 P1-verificatievragen; 5 leverancier(s) met US-indicatie; 4 leverancier(s) met hoog datarisico |
| sro.nl                      | P1         | Mogelijk                   |                   5 |                          4 |                    4 | 4 P1-verificatievragen; 5 leverancier(s) met US-indicatie; 4 leverancier(s) met hoog datarisico |
| gad.nl                      | P1         | Mogelijk                   |                   4 |                          4 |                    3 | 3 P1-verificatievragen; 4 leverancier(s) met US-indicatie; 4 leverancier(s) met hoog datarisico |
| readspeaker.com             | P1         | Te beoordelen              |                   4 |                          3 |                    3 | 3 P1-verificatievragen; 4 leverancier(s) met US-indicatie; 3 leverancier(s) met hoog datarisico |
| tomingroep.nl               | P1         | Te beoordelen              |                   3 |                          5 |                    3 | 3 P1-verificatievragen; 3 leverancier(s) met US-indicatie; 5 leverancier(s) met hoog datarisico |
| visitgooivecht.nl           | P1         | Te beoordelen              |                   3 |                          4 |                    3 | 3 P1-verificatievragen; 3 leverancier(s) met US-indicatie; 4 leverancier(s) met hoog datarisico |
| energieloketten.nl          | P1         | Te beoordelen              |                   3 |                          3 |                    3 | 3 P1-verificatievragen; 3 leverancier(s) met US-indicatie; 3 leverancier(s) met hoog datarisico |
| regiogv.nl                  | P1         | Te beoordelen              |                   3 |                          3 |                    2 | 2 P1-verificatievragen; 3 leverancier(s) met US-indicatie; 3 leverancier(s) met hoog datarisico |
| gnr.nl                      | P1         | Te beoordelen              |                   3 |                          2 |                    2 | 2 P1-verificatievragen; 3 leverancier(s) met US-indicatie; 2 leverancier(s) met hoog datarisico |
| randmeren.com               | P1         | Te beoordelen              |                   3 |                          2 |                    2 | 2 P1-verificatievragen; 3 leverancier(s) met US-indicatie; 2 leverancier(s) met hoog datarisico |
| huizen.nl                   | P1         | Mogelijk                   |                   2 |                          7 |                    2 | 2 P1-verificatievragen; 2 leverancier(s) met US-indicatie; 7 leverancier(s) met hoog datarisico |
| archiefgooienvechtstreek.nl | P1         | Te beoordelen              |                   2 |                          2 |                    2 | 2 P1-verificatievragen; 2 leverancier(s) met US-indicatie; 2 leverancier(s) met hoog datarisico |
| bngbank.nl                  | P1         | Te beoordelen              |                   2 |                          2 |                    2 | 2 P1-verificatievragen; 2 leverancier(s) met US-indicatie; 2 leverancier(s) met hoog datarisico |
| archiefweb.eu               | P1         | Te beoordelen              |                   2 |                          1 |                    1 | 1 P1-verificatievragen; 2 leverancier(s) met US-indicatie; 1 leverancier(s) met hoog datarisico |
| belastingenhbl.nl           | P1         | Waarschijnlijk             |                   1 |                          2 |                    1 | 1 P1-verificatievragen; 1 leverancier(s) met US-indicatie; 2 leverancier(s) met hoog datarisico |

## Service layers

| service_layer    |   domains_count |   suppliers_count |   indicator_count |   us_supplier_domains_count |   high_data_risk_domains_count | top_suppliers                                                                                                  |
|:-----------------|----------------:|------------------:|------------------:|----------------------------:|-------------------------------:|:---------------------------------------------------------------------------------------------------------------|
| mx_spf           |              17 |                 6 |               154 |                          16 |                             17 | Microsoft 365 / Exchange Online, Zivver, TOPdesk, Flowmailer, Formulierenserver, Mailgun                       |
| frontend_scripts |              19 |                 7 |                97 |                          16 |                             14 | YouTube, Siteimprove, ReadSpeaker, Google APIs, Google Tag Manager, Google Analytics, Cookiebot / Usercentrics |
| network_hosting  |              11 |                 2 |                50 |                           7 |                             11 | SIMgroep, Cloudflare                                                                                           |

## Voorzichtige interpretatie

De analyse toont publieke indicatoren van betrokken leveranciers, diensten en technische ketens. Dit is geen sluitend bewijs van fysieke datalocatie of juridische doorgifte. Het laat wel zien waar aanvullende verificatie nodig is, bijvoorbeeld rond tenantregio, logging, back-ups, supporttoegang, subverwerkers en contractuele waarborgen.
