> **Vanhentunut 7.11. illalla (tiimin työpaperi, säilytetty historiaksi).** Voimassa olevat päätökset ja luvut:
> `MASTER.md` §B–§C ja `PRODUCT.md`. Tärkeimmät muutokset: itsenostin (H7) jokaiseen uuteen COMBI-puristimeen
> 1 000 €:lla (ei kiskoja 10 %:iin eikä virtuaalivaakaa pääviestinä); jäteyhtiö maksaa 30 €/laite/kk (NPV +0,18 M€,
> takaisinmaksu v9); tiedon epäsymmetria ±37 % vs ±10 % (ei 21/9 %); ei "varmennettua painoa"; ei laskujen
> lataamista; OpenWeight ei välitä tarjouksia (jäteyhtiö suunnittelee hinnan, asiakas vertaa saamiaan tarjouksia).

# OpenWeight – rakennussuunnitelma

Mitä rakennetaan hackathonissa ja miten se nojaa haasteen dataan ja tehtäviin (A–E).
Konsepti ja talous: `PROJECT.md`. Tiimin taustapaperi: `TIIMILLE.md`.

## Palautus (haasteen kohta 07)
1. **Punnituskonsepti** (lyhyt kuvitettu dokumentti): punnitsevat ohjauskiskot CombiMaxiin, 4 kennoa,
   BOM 530–1 300 €, asennus, kalibrointi (tyhjä kontti = tara, koekuormat), virhelähteet (puristus, lumi,
   jää, kosteus, sivuvoimat vedossa), validointikoe (kiskot vs. jäteaseman vaaka 30 tyhjennyksellä).
2. **Toimiva ohjelmistodemo** synteettisellä datalla + koodi ja ajo-ohjeet + jäljitettävä talous + SMART-integraatio.
3. **Asiakasarvo ja liiketoimintamalli** (PROJECT.md luvut 4–7) + lisenssiluettelo + oletukset ja testaamattomat asiat.

## Demosovellus: kolme näkymää, yksi kohde läpi

### Näkymä 1 – Kiinteistöpäällikkö (ilmainen)
| Osa | Mitä näkyy | Data | Haasteen tehtävä |
|---|---|---|---|
| Kustannus per tonni | mitä kukin tyhjennys maksoi ja €/t, rivi riviltä sopimusta vasten | `contract_versions`, `collection_events`, `weighbridge_tickets`, `invoice_lines` | **A** (pohjana B1, 96 % sentilleen) |
| Asiat, jotka eivät käy järkeen | vajaat ja ennenaikaiset tyhjennykset, kalliit tonnit, painoerot, päällekkäiset ja väärät laskurivit, väärä jäte | `anomaly_labels` (validointi) | **B** (pohjana B2-säännöt, macro-F1 0,73) |
| Palvelutaso | jäteyhtiön täsmällisyys, väliin jääneet käynnit, punnitusdatan jakaminen, ylilaskutus, tilauksesta tyhjennykseen | `task_b2_scorecard_rows` | **B2** (pohjana B5, 68/100) |
| Kilpailutusapuri | suositus: kiistä lasku / pyydä punnitusdata / neuvottele / kilpailuta, euroarvo ja perustelu, Hyväksy / Ei nyt | `operator_action_cases`, `operator_action_values` | **C2** (pohjana B6, regret 240 €) |
| Tekoälyraportti | kielimalli kirjoittaa kolme tärkeintä asiaa; luvut tulevat laskennasta, jokainen avautuu lähderiveihin | kaikki yllä | **E** |

### Näkymä 2 – Haastava jäteyhtiö (maksullinen)
| Osa | Mitä näkyy | Data |
|---|---|---|
| Tarjouspaketti | kohteen kg/tyhjennys P10/P50/P90, täyttymisnopeus, kausivaihtelu, 12 kk ennuste | `telemetry_daily_summary` (mass_kg), `collection_events` |
| Sokko vs. profiili | arviovirhe vertailulaitteilla 21 % vs. kohteen omalla datalla 9 % | `analysis/value_pools.py` |
| Hintalaskuri | yhtiön omat kustannukset → kannattava €/t ja kate 50/90 %:n varmuudella | profiili + syötteet |
| Live-ennuste | mitkä puristimet täynnä 3 päivän sisällä ja montako kiloa | `telemetry_hourly` |

### Näkymä 3 – Europress
| Osa | Mitä näkyy |
|---|---|
| Verkosto | punnitut laitteet, painon ja jäteaseman vaa'an ero (toleranssi ±3,3 %) |
| Business case | liukusäätimet: punnituksen hinta, jäteyhtiön maksu, omaksuminen, laitemäärä → NPV, takaisinmaksu, syvin kertymä (`analysis/final_v2.py`) |
| Liidit | jäteyhtiöiden laitesuositukset |

## Haasteen vetäjän kahdesta keskustelusta nousseet vaatimukset
| Vetäjä sanoi | Mitä rakennetaan |
|---|---|
| "Who owns the weight is the holy grail"; operaattori panttaa painon | punnitus jokaiseen laitteeseen, paino Europressin ja asiakkaan |
| Ei kuljetusbisnekseen; suora integraatio jäteyhtiöön epäonnistui | ei reititystä, ei syvää integraatiota: portaali + avoin rajapinta |
| Insightsia myyty jäteyhtiön kautta; kumppanuudet strategiaa | maksaja on jäteyhtiö |
| Loppuasiakkaalle vaikea myydä, Insights ~15 %:lla, kiinteistöpäällikkö käyttää ~3 % ajastaan | asiakkaalle ilmainen, valmiiksi pureskeltu tekoälyraportti |
| Sopimukset ~3 v, SLA, kilpailutus pelkällä hinnalla | palvelutason seuranta ja kilpailutusapuri, joka vertaa myös palvelutasoa |
| Europress haluaa olla läsnä myös kilpailutusten välissä | jatkuva sopimuksen seuranta ja kuukausiraportti |
| Kuljetus kiinteä per tyhjennys, käsittely ~3× kuljetus | €/t-laskelma erottelee kuljetuksen ja käsittelyn (tehtävä A) |
| Asiakas epäilee, että häntä huijataan | laskujen täsmäytys ja painoerot rivitasolla, neutraali sävy |
| Kosteus: paino nousee viikonloppuna ilman käyttöä → palvelumahdollisuus | kosteushälytys: "maksat vedestä" (datan skenaario S28) |
| Väärä jäte väärässä puristimessa (kärryllinen elektroniikkaa biopuristimeen) | väärän jätteen tunnistus tiheydestä (CONTAMINATION, S07) |
| Biojäte vaikea painesensorille | kiskot punnitsevat suoraan, biojäte ei ole ongelma (~1/3 laitteista) |
| Punnitus +20 % hintaan, asiakas ei maksa; Europress maksaa, jos elinkaari plussalla | Europress maksaa punnituksen, business case näyttää plussan |
| Punnitus suppilossa, ei koko 5 t + 3 t järjestelmää; ei tarvitse olla tarkka, pitää olla halpa | punnituskonseptissa vaihtoehtojen vertailu: suppilo/Scaletipper, kiskot, auton koukku |
| Tekoälyn käyttö kiinnostaa, myös asiakaskokemuksessa | ennusteet, poikkeamat, kielimalliraportti |
| Pitchaa kuin myisit sen Europressille | demo ja pitch Europressin näkökulmasta: tulos, liidit, laitemyynti |
| Isot ketjut (~100 laitetta), kauppakeskukset (~20), Suomessa ~10 000 laitetta | demokohde kauppaketju; portfolion näkymä usealle laitteelle |
| Puola ja Keski-Eurooppa tärkeitä, aikataulupohjaisia | laajentumisdia |
| Europress haluaa oman IP:n | IP on ohjelmistossa ja verkoston datassa, kennot ovat vakio-osia |
| SMARTin tasot Intro / Insights / Inventory | tuotteistus uutena tasona SMARTin päälle |

## Datapaketista (download) käytettävät osat
| Datapaketti | Käyttö |
|---|---|
| `reference/` (devices, contracts, contract_versions, operators, sites, regions, price_index_monthly) | sopimushinnat, laitteet, jäteyhtiöt, alueet |
| `operations/` (collection_events, weighbridge_tickets, quality_assessments, maintenance_work_orders) | tyhjennykset, punnitukset, laatu |
| `telemetry/` (telemetry_hourly, telemetry_daily_summary; mass_kg = simuloitu integroitu punnitus) | kiskopunnituksen paino, profiilit, ennusteet |
| `finance/` (invoices, invoice_lines) | laskujen täsmäytys |
| `labels_dev/` (anomaly_labels, reference_economics, operator_action_values, operator_scorecard, decision_outcomes) | evaluointi validointijaksolla |
| `benchmark/` (task_ab_test_collections, task_b2_scorecard_rows, operator_action_cases, decision_cases) | tehtävien A, B, B2, C2 syötteet |
| `baselines/` (b1, b2, b5, b6, business_case.py) | lähtötaso, jota parannetaan |
| `docs/ECONOMIC_MODEL.md` (§2b verification basis ±3,3 %, §6 säästöjen rakenne, §7 C2) | laskentasäännöt ja toleranssi |
| Datan oletus: "most devices have integrated weighing" | sama maailma kuin konseptimme: paino jokaisesta laitteesta |

## Missä voitamme perustason mallit (paino on ratkaisu)
- **B, PREMATURE_UNJUSTIFIED** (recall 0,59): perusmalli ei näe varmuuden vuoksi tehtyjä tilauksia ennen
  viikonloppua (S39) eikä täyttöanturia, joka näyttää täyttä vaikka paino on pieni (S40). **Painoperusteinen
  sääntö: tyhjennys, jossa paino alle X % kohteen täyden kuorman painosta = ennenaikainen.** Tämä on suora todiste
  siitä, mitä punnitus tuo.
- **B, COST_PER_T_HIGH** (90 väärää hälytystä): jätetään hälyttämättä, kun hygienia tai minimiveloitus selittää.
- **B, WEIGHT_DISCREPANCY**: erotellaan auton vanhentunut tara (sama auto monella asiakkaalla) laitteen virheestä.
- **C2** (regret 240 €): kilpailutussuosituksessa käytetään jäteyhtiön laskutuksen laatua (B2-kortti), jota B6 ei käytä.

Mittaus: `python -m europress_data.evaluate --task B|B2|C2` validointijaksolla. Testijaksoon ei kosketa.

## Arviointikriteerit → missä pisteet tulevat
| Kriteeri | Paino | Mitä tuomme |
|---|---|---|
| Punnituskonsepti | 25 % | kiskot, BOM, validointikoe |
| Asiakas- ja liiketoiminta-arvo | 25 % | kierre, jäteyhtiön maksukyky julkisista tilinpäätöksistä, Europressin NPV |
| Analyysi | 20 % | A/B/B2/C2-tulokset perustasoa vasten, jäljitettävät laskelmat |
| Ohjelmisto ja SMART | 15 % | kolme näkymää, SMART-integraatiokaavio |
| Tuotteistus | 10 % | hinnoittelu, pilotti, laajentuminen |
| Selkeys ja rajoitukset | 5 % | jokainen luku merkitty: havaittu / arvioitu / simuloitu / oletus |

## Säännöt, joita noudatetaan (haasteen rubriikki D/E)
- Jokainen luku merkitään: havaittu, arvioitu, simuloitu tai oletus.
- Jäljitettävyys rivitasolle: tilaus → punnituskuitti → sopimusversio → laskurivi.
- Ihminen hyväksyy jokaisen suosituksen, perustelu ja peruutuspolku näkyvät.
- Ei väitteitä todellisista säästöistä.
- Neutraali sävy: erotellaan jäteyhtiön, laitteen ja datan aiheuttamat erot.
- Orbiksen lukuja ei palautukseen (akateeminen lisenssi); julkiset lähteet.

## Työnjako ja aikataulu (palautus sunnuntaina)
| Kuka | Lauantai-ilta | Yö / sunnuntaiaamu | Sunnuntaipäivä |
|---|---|---|---|
| Data 1 | A + B pohjalta, painoperusteiset säännöt (S39/S40) | evaluointi, luvut demoon | tuloksiin perustuvat diat |
| Data 2 | profiilit, sokko vs. profiili, hintalaskuri | B2 + C2 parannus | evaluointi |
| Käyttöliittymä | kolmen näkymän runko | tekoälyraportti, business case -säätimet | demon viimeistely, video |
| Mekaniikka + bisnes | punnituskonsepti, BOM | liiketoimintadokumentti | pitch, lisenssit, rajoitukset |

## Karsintajärjestys, jos aika loppuu
1. Live-ennuste (näkymä 2)
2. Liidit (näkymä 3)
3. C2-parannus (perusmalli B6 riittää näyttämiseen)
Ei karsita: tarjouspaketti, painoperusteinen ennenaikaisuussääntö, tekoälyraportti, business case.
