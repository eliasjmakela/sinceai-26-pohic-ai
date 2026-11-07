> **Vanhentunut 7.11. illalla (tiimin työpaperi, säilytetty historiaksi).** Voimassa olevat päätökset ja luvut:
> `MASTER.md` §B–§C ja `PRODUCT.md`. Tärkeimmät muutokset: itsenostin (H7) jokaiseen uuteen COMBI-puristimeen
> 1 000 €:lla (ei kiskoja 10 %:iin eikä virtuaalivaakaa pääviestinä); jäteyhtiö maksaa 30 €/laite/kk (NPV +0,18 M€,
> takaisinmaksu v9); tiedon epäsymmetria ±37 % vs ±10 % (ei 21/9 %); ei "varmennettua painoa"; ei laskujen
> lataamista; OpenWeight ei välitä tarjouksia (jäteyhtiö suunnittelee hinnan, asiakas vertaa saamiaan tarjouksia).

# OpenWeight
**Paino jokaisesta puristimesta. Kilpailuetu jäteyhtiöille. Läpinäkyvyys asiakkaalle. Kasvu Europressille.**

Europress × Since AI Hackathon 2026 · tiimi PöhiC.AI

---

## 1. Tiivistelmä

Jätehuollon hinnan ratkaisee paino, mutta painon tietää vain jäteyhtiö, ja vasta jälkikäteen. Vakiintunut
jäteyhtiö käyttää vuosien painohistoriaansa kilpailutuksissa, ja ajoperusteinen laskutus palkitsee sitä vajaista
tyhjennyksistä. Europressin SMART vähentää tyhjennyksiä, mutta toimii jäteyhtiöiden kannustimia vastaan eikä ole
mukana siellä, missä rahasta päätetään.

**OpenWeight** tuo punnituksen jokaiseen Europressin puristimeen Europressin omalla kustannuksella ja tekee
painotiedosta palvelun:

- **Loppuasiakas** saa ilmaiseksi tekoälyapurin kilpailutukseen ja jatkuvan sopimuksen seurannan.
- **Jäteyhtiö** ostaa live-painot, ennusteet ja tarjouspaketit, joilla se voittaa kilpailutuksia ja ajaa täysiä kuormia.
- **Europress** saa palvelutulon ja lisämyynnin, kun kilohinnoittelussa täydet kuormat ovat jäteyhtiön etu ja
  jäteyhtiöt alkavat suositella Europressin laitteita.

Laskelman mukaan palvelu kasvattaa Europressin nykyistä tulosta noin 45 % täydessä vauhdissa (1,8 M€/v),
NPV 10 v noin 2,4 M€.

---

## 2. Ongelma

### 2.1 Jäteyhtiö hyötyy turhista tyhjennyksistä
Tyhjennyksestä maksetaan kiinteä hinta. Haasteen datassa kolmannes tyhjennyksistä tehdään alle 60 %:n
täytöllä, ja täysillä kuormilla tyhjennyksiä tarvittaisiin 18 % vähemmän. HSY:n logistiikkapäällikkö:
*"Kuljetusyritys ei suoraan säästä, jopa menettää."*

### 2.2 Painotieto suojaa vakiintunutta jäteyhtiötä
Sopimukset kilpailutetaan noin kolmen vuoden välein. Kohdetta pitkään palvellut yhtiö tietää, montako kiloa
kohteesta lähtee. Haastaja tarjoaa sokkona: datassa uuden tarjoajan arvio kiloista per tyhjennys menee
keskimäärin **21 %** pieleen, kohteen painohistorialla **9 %**. Siksi haastaja ei uskalla tarjota kilohintaa.
Haasteen vetäjä vahvisti asetelman.

### 2.3 Europressin nykyiset palvelut eivät osu rahaan
| SMART nyt | Miksi se ei riitä |
|---|---|
| Täyttöaste ja automaattiset tyhjennyskutsut (−37 % tyhjennyksiä) | Toimii jäteyhtiöiden kannustimia vastaan, vakiintuneet puhuvat sitä vastaan |
| Myydään loppuasiakkaalle | Asiakas käyttää jätehuoltoon ~3 % työajastaan ja on hintaherkkä; Insights ~15 %:lla |
| Portaali ja raportit | Näyttävät dataa, eivät kerro mitä tehdä |
| Ei painoa | Säästöä ei voi todentaa eikä laskua tarkistaa |
| Ei roolia kilpailutuksessa | Hinta lyödään lukkoon kolmeksi vuodeksi ilman Europressia |
| Data jäteyhtiöille ilmaiseksi (tyhjennyskutsut, rajapinta) | Europressilla ei tuotetta, josta jäteyhtiö maksaisi |
| Scaletipper X1 punnitsee | Kallis, vain astioilla syötettäviin kohteisiin, data jää vuokralaisraportteihin |

**Johtopäätös:** ongelma ei ole jäteyhtiöissä vaan kannustimissa. Painotieto muuttaa kannustimet.

---

## 3. Ratkaisu

### 3.1 Kierre
1. Europress punnitsee jokaisen uuden puristimen (punnitsevat ohjauskiskot), asiakas ei maksa mitään.
2. Asiakas saa ilmaiseksi näkyvyyden ja kilpailutusapurin → vaatii parempia tarjouksia.
3. Haastava jäteyhtiö ostaa painodatan → tarjoaa kilohinnan ilman riskiä → voittaa.
4. Vakiintuneen on pakko seurata.
5. Kilohinnoittelussa täydet kuormat ovat jäteyhtiön etu → se suosittelee Europressin laitteita → lisämyynti.

**Miksi asiakas ei maksa mitään:** jokainen punnitsematon laite heikentää kilpailuetua, jota Europress myy
jäteyhtiöille. Laskelmassa jo 10–25 % pois jättäneitä asiakkaita syö maksullisuuden hyödyn.

### 3.2 Loppuasiakas (kiinteistöpäällikkö, ketjun ympäristöpäällikkö) – ilmainen
- **Kuukausiraportti (tekoäly):** kolme tärkeintä havaintoa euroina. Jokainen luku avautuu laskelmaksi,
  jokaisessa suosituksessa Hyväksy / Ei nyt.
- **Sopimuksen seuranta:** vasteajat, väliin jääneet käynnit, turhat ja vajaat tyhjennykset, lisämaksut.
- **Laskujen täsmäytys:** tekoäly lukee laskun, jokainen rivi verrataan punnittuun painoon ja tyhjennyksiin.
- **Asiat, jotka eivät käy järkeen:** €/t yli vertailutason, sama kuljetus kahdesti, paino nousee ilman puristuksia.
- **Kilpailutusapuri:** muistutus ennen sopimuksen päättymistä, säästöarvio, lupa jakaa painoprofiili,
  tarjousten vertailu kokonaishintana per tonni ja palvelutasona, tekoäly selittää erot.
- **Kysy datastasi.**

### 3.3 Jäteyhtiö – maksullinen
- **Tarjouspaketti** kilpailutettavasta kohteesta: kg/tyhjennys (P10/P50/P90), täyttymisnopeus, kausivaihtelu,
  12 kk ennuste. Hintalaskuri yhtiön omilla kustannuksilla: kannattava €/t ja kate eri varmuustasoilla.
- **Live-paino ja ennuste** omille asiakkaille: mitkä ovat täynnä lähipäivinä ja montako kiloa.
- **Varmennettu paino** jokaisesta tyhjennyksestä.
- **Kilohintasopimusten riskiseuranta.**
- **Oma vertailukortti** myyntivälineeksi.
- **Laitesuositukset** asiakkaille → liidit Europressille.

### 3.4 Europress – sisäinen
- Verkosto, punnituksen tila ja kalibrointi.
- Palvelutulo, kilpailutukset, liidit.
- **Markkinahintaindeksi:** anonymisoitu €/t alueittain ja jakeittain toteutuneista kilpailutuksista.

### 3.5 Taustajärjestelmä
1. **Tiedonkeruu:** punnitus (neljän kennon summa), SMART-telemetria, tilaukset, asiakkaan laskut.
2. **Punnituksen käsittely:** mitataan vain koneen ollessa levossa, kontin poisto nollaa vaa'an, tyhjä kontti
   antaa taran. Painon nousu ilman puristuksia = kosteus tai lumi.
3. **Tyhjennysten tunnistus:** paino ennen ja jälkeen, liitos tilaukseen ja laskuriviin.
4. **Profiilit ja ennusteet** vaihteluväleineen.
5. **Hinnoittelumoottori:** profiili + yhtiön kustannukset → €/t ja riski.
6. **Täsmäytys ja palvelutaso** sopimusta vasten.
7. **Suosittelija:** säännöt laskevat toimenpiteet euroineen ja todisteineen, kielimalli kirjoittaa
   selityksen, luvut tulevat aina laskennasta, ihminen hyväksyy.
8. **Luvat:** data kuuluu asiakkaalle, jakolupa kilpailutuskohtainen ja määräaikainen.
9. **Kilpailutus:** paketin jako, tarjousten normalisointi, hintaindeksin päivitys.
10. **Rajapinnat:** SMART-portaali, jäteyhtiöiden rajapinta, sähköposti.

### 3.6 Tekoäly
1. **Ennusteet vaihteluväleineen:** hinnoitteluriski on epävarmuutta, ja sen pienentäminen on se, mistä jäteyhtiö maksaa.
2. **Poikkeamien tunnistus:** palvelutason rikkomukset, laskuvirheet, kosteus, väärä jäte.
3. **Kielimalli asiakkaalle:** raportit, kilpailutuksen selitykset, laskujen lukeminen, vastaukset kysymyksiin.

---

## 4. Talous

Arvot per laite on laskettu haasteen synteettisestä datasta (447 laitetta, 304 päivää); ne ovat suuruusluokkia.
Laskenta: `analysis/final_v2.py`, `analysis/economics_full.py`, `analysis/value_pools.py`.

### 4.1 Arvo per laite vuodessa
| | €/laite/v | Mistä |
|---|---|---|
| Asiakkaan kulut nyt | 10 200 | tyhjennykset 4 700, käsittely 3 605, kuljetus 1 716, lisämaksut ~1 600, hyvitys −2 209 |
| **Asiakkaan hyöty** | **~1 900 (~19 %)** | täydet kuormat 634, kilpailutus ~800, kiistettävät lisämaksut ~250, väärä jäte ~120, laskuvirheet ~95 |
| **Jäteyhtiön hyöty** | **~1 400** | täydet kuormat 634, turhat käynnit ~130, hinnoitteluriski 1 930 / 3 v = 643 |

### 4.2 Paljonko jäteyhtiö voi maksaa
| Yhtiö | Liikevoitto | Liikevoitto per laite* |
|---|---|---|
| L&T 2025 | 8,0 % | ~816 €/v |
| Stena Recycling Oy 2025 | ~2,7 % | ~275 €/v |
| L&T Q1/2026 | −0,9 % | tappiollinen |
| Remeo 2025 | −3,7 % | tappiollinen |

*Datan keskimääräisellä asiakaskululla 10 200 €/laite/v.

**Jäteyhtiö tienaa nyt laitteesta 0–800 €/v. Palvelu tuo ~1 400 €/v.** Hinnoittelu:
- **30 €/kk per laite** (360 €/v, ~25 % arvosta), jäteyhtiölle jää ~1 050 €/v.
- **Tarjouspaketti 500 € per tarjoaja** (~20 % yhden voitetun kolmen vuoden sopimuksen voitosta).

### 4.3 Punnituksen hinta (punnitsevat ohjauskiskot, asennettuna uuden laitteen mukana)
| Taso | Kennot | Muut osat | Asennus | Yhteensä | Vuosikustannus |
|---|---|---|---|---|---|
| Matala | 4 × 60 € | 210 € | 80 € | 530 € | ~130 €/v |
| **Perus** | 4 × 100 € | 300 € | 100 € | **800 €** | ~170 €/v |
| Korkea | 4 × 200 € | 350 € | 150 € | 1 300 € | ~250 €/v |

Punnitus maksaa ~14 €/kk ja tuottaa asiakkaalle ja jäteyhtiölle yhteensä ~3 300 €/v, eli noin 20-kertaisesti.

### 4.4 Europress, Suomi, 10 vuotta
Oletukset: 10 000 laitetta, käyttöikä 8 v (1 250 uutta/v), punnitus jokaiseen uuteen laitteeseen 800 €,
jäteyhtiöt 30 €/kk, omaksuminen 60 % neljässä vuodessa, tarjouspaketit 500 € × 2,5 tarjoajaa 35 %:ssa
kilpailutuksista, lisämyynti +5 % uusista laitteista (kate 25 % × 22 500 €), kiinteät kulut 400 k€/v,
alusta 26 €/laite/v, kalibrointi 50 €/laite/v, korko 8 %.

| Vuosi | Punnittu | Tulot | Kulut + investointi | Kassavirta | Kertymä |
|---|---|---|---|---|---|
| 1 | 1 250 | 0,1 M€ | 1,5 M€ | −1,4 M€ | −1,4 M€ |
| 3 | 3 750 | 1,2 M€ | 1,7 M€ | −0,5 M€ | −2,9 M€ |
| 4 | 5 000 | 2,1 M€ | 1,8 M€ | +0,3 M€ | −2,6 M€ |
| 7 | 8 750 | 3,5 M€ | 2,1 M€ | +1,5 M€ | +0,7 M€ |
| 10 | 10 000 | 4,0 M€ | 2,2 M€ | +1,8 M€ | +6,1 M€ |

**NPV 10 v 2,4 M€, kassavirta plussalla vuodesta 4, takaisinmaksu vuonna 7.**
Syvin kertymä −2,9 M€ ≈ 0,7 × Europress-konsernin vuoden 2025 tulos ennen veroja (4,0 M€), ~15 % omasta pääomasta.
Täydessä vauhdissa +1,8 M€/v ≈ +45 % nykyiseen tulokseen.

### 4.5 Herkkyys (NPV 10 v)
| Skenaario | NPV | Plussalla |
|---|---|---|
| Maksu 40 €/kk tai omaksuminen 80 % | +5,0 M€ | v6 |
| Punnitus 530 € | +4,7 M€ | v6 |
| Hidas omaksuminen (6 v) | +1,0 M€ | v8 |
| Ei lisämyyntiä | +0,8 M€ | v8 |
| Maksu 20 €/kk tai omaksuminen 40 % | −0,2 M€ | v9 |
| Punnitus 1 300 € | −1,8 M€ | ei |

**Kannattavuusraja** (NPV 10 v = 0): punnitus 530 € → 13–19 €/kk · 800 € → 21–32 €/kk · 1 300 € → 37–56 €/kk
(omaksuminen 60 % / 40 %).

### 4.6 Johtopäätökset
1. Malli kannattaa, kun punnitus maksaa enintään ~800 € asennettuna (tavoite 600 €) ja jäteyhtiöt maksavat 30–40 €/kk.
2. Herkimmät tekijät: punnituksen hinta ja jäteyhtiöiden omaksumisnopeus.
3. **Pilotti ensin:** 1 000 laitetta ja yksi haastava jäteyhtiö kahdeksi vuodeksi. Jos jäteyhtiöt eivät lähde
   mukaan, Europress lopettaa ~1 M€:n tappiolla eikä 5–11 M€:n.
4. Keski-Eurooppa ja Puola, missä tyhjennykset ovat aikataulupohjaisia, kasvattavat täysien kuormien arvoa.

---

## 5. Hackathon-demo

Yksi polku läpi kolmen näkymän:
1. Kauppaketjun kohde, sama jäteyhtiö yhdeksän vuotta.
2. Asiakasraportti: *"Sopimus päättyy 7 kk päästä, arvioitu säästö kilpailutuksella 2 100–3 400 €/v."*
3. Asiakas antaa luvan jakaa painoprofiilin.
4. Haastaja avaa tarjouspaketin: sokkona virhe 21 %, profiililla 9 %. Se tarjoaa kilohinnan, joka on sille
   kannattava ja asiakkaalle halvempi.
5. Asiakas valitsee. Europressin näkymä: palvelutulo, liidi, kertymä kohti takaisinmaksua.

## 6. Mitä emme tee
- Reittioptimointia (Europress ei halua kuljetusbisnekseen; jäteyhtiöiden ajojärjestelmät ja työvuorot).
- Laskutusta laitteen painolla (jäteaseman vaaka pysyy laskutusperusteena).
- Kunnallista jätehuoltoa (asiakas ei voi valita jäteyhtiötä).
- Ketään ei syyllistetä: palvelu on neutraali ja sama kaikille jäteyhtiöille.

## 7. Rajoitukset
- Arvot per laite tulevat synteettisestä datasta.
- Punnituskennojen sarjahinta on arvio; budjettitarjous kennovalmistajalta puuttuu.
- Laitekanta (10 000) ja käyttöikä (8 v) ovat vetäjän arvio ja oletus.
- Oletus: asiakas antaa luvan jakaa painoprofiilinsa kilpailutukseen (asiakas hyötyy siitä suoraan).
- Pohjoismaissa valtaosa laitteista on liisattuja, joten lisämyynti näkyy uusina vuokrasopimuksina.
  Laskelma käyttää katetta laitteen hinnasta; tarkennetaan vuokrasopimuksen katteella.
- CombiMax on COMBI-laite: koko yksikkö (kone ja kontti) seisoo kiskoilla ja lähtee tyhjennykseen,
  joten tara on tyhjän koneen paino.
- Vakiintuneen jäteyhtiön vastareaktio.
- Biojäte, lumi ja kosteus vaikeuttavat punnitusta.

## 8. Lähteet
- Haasteen synteettinen data ja dokumentaatio (Since AI / Europress); haasteen vetäjän kommentit 6.–7.11.2026.
- SMART: https://epsmart.fi/, https://epsmart.fi/palvelumme/ominaisuudet/, https://epsmart.fi/palvelumme/smart-faq/
- Scaletipper X1: https://europressgroup.com/fi/scaletipper-x1/
- L&T osavuosikatsaus Q1/2026: https://www.lt.fi/hubfs/Sijoittajat/Osavuosikatsaukset/Lassila%20Tikanoja%20Osavuosikatsaus%20Q1%202026.pdf
- Stena Recycling Oy: https://www.asiakastieto.fi/yritykset/fi/stena-recycling-oy/19564025/yleiskuva
- Remeo: https://www.finder.fi/J%C3%A4tehuolto/Remeo+Oy+Helsinki/Helsinki/yhteystiedot/3517535
- Europress-konsernin tilinpäätös 2025: PRH / Virre (julkinen rekisteri)
- Punnituskennot: Tamtron BC5 -datalehti https://tamtrongroup.com/wp-content/uploads/2024/04/DN16992_1-FI_Datalehti-Punnitusanturi-BC5_240201.pdf
- HSY:n logistiikkapäällikön sähköposti 26.6.2026 (sensorikokeilut, kustannukset)

Käytetyt kirjastot: pandas (BSD-3), pyarrow (Apache 2.0), numpy (BSD-3). Lisätään demon kirjastot.
