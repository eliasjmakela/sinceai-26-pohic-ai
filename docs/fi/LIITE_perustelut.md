# OpenWeight – liite: lähteet, laskelmat ja perustelut

Tämä liite käy läpi jokaisen projektikuvauksessa (`OpenWeight.pdf`) esitetyn väitteen ja luvun:
mistä se tulee, miten se on laskettu, mihin päättely nojaa ja kuinka varma se on.
Tavoite on, että lukija voi tarkistaa kaiken itse ja näkee suoraan, mikä on mitattua ja mikä arvausta.

Kirjoitettu 7.11.2026. Laskentaskriptit ovat kansiossa `analysis/` (ajetaan projektin juuresta, data
`materials/engine/Europress_SMART_Material_Value_Engine_v1.0.1/data/competition/public`).

---

## 0. Miten tätä liitettä luetaan

### 0.1 Varmuusluokat

Jokainen väite on merkitty yhdellä näistä:

| Merkintä | Tarkoittaa | Kuinka paljon siihen voi luottaa |
|---|---|---|
| **HAVAITTU** | julkinen lähde (tilinpäätös, yrityksen sivu) tai haasteen vetäjän suora sanominen | luku on lähteen mukainen; lähde voi silti olla epätarkka |
| **SIMULOITU** | laskettu haasteen synteettisestä datasta | kuvaa haasteen keksittyä maailmaa, ei todellisuutta. Suuruusluokka on järkevä, tarkka luku ei ole todiste mistään |
| **ARVIO** | tiimin laskelma, joka nojaa fysiikkaan, julkisiin hintoihin tai muihin lukuihin | perusteltu, mutta ei mitattu |
| **OLETUS** | tiimin valinta, jolle ei ole suoraa näyttöä | voi olla väärin; vaikutus näytetään herkkyysanalyysissä |
| **ARVAUS** | numero, jolle ei ole juuri perustetta | käytetty vain esimerkkinä tai täytteenä; merkitty erikseen |

### 0.2 Lähdeluettelo

| Tunnus | Lähde | Tyyppi | Huomio |
|---|---|---|---|
| L1 | Haasteen datapaketti `Europress_SMART_Material_Value_Engine_v1.0.1` (Since AI / Europress), competition-profiili, `public/` | synteettinen data | 447 laitetta taloustaulukoissa, 304 päivän jakso (`labels_dev/reference_economics`). Dokumentaation mukaan noin 500 laitetta, 365 päivää; ero johtuu siitä, että dev-labelit kattavat vain osan jaksosta |
| L2 | Datapaketin dokumentaatio: `START_HERE.md`, `docs/ECONOMIC_MODEL.md`, `docs/BENCHMARK.md`, `README_FIRST.txt` | dokumentaatio | |
| L3 | Haasteen virallinen briiffi (PDF) | dokumentti | arviointikriteerit ja palautusmuoto |
| L4 | Avausinfo 6.11.2026, vetäjän puhe (litterointi, osin sotkuinen) | keskustelu | |
| L5 | Toinen keskustelu vetäjän kanssa 7.11.2026 (litterointi, hyvin sotkuinen) | keskustelu | osa repliikeistä voi olla väärin litteroitu tai väärälle puhujalle merkitty |
| L6 | Kolmas keskustelu vetäjän kanssa 7.11.2026 (`Downloads/tall_fin.json`) | keskustelu | selkein litterointi |
| L7 | epsmart.fi: etusivu, Toiminnot, SMART FAQ | yrityksen sivu | |
| L8 | europressgroup.com/fi/scaletipper-x1 | yrityksen sivu | |
| L9 | Lassila & Tikanoja Oyj, osavuosikatsaus Q1/2026 (lt.fi) | julkinen raportti | |
| L10 | Asiakastieto, Stena Recycling Oy (1956402-5) yleiskuva | julkinen yritystieto | |
| L11 | Finder, Remeo Oy | julkinen yritystieto | aggregoitu, ei alkuperäinen tilinpäätös |
| L12 | Europress Group Oy konsernin tunnusluvut 2021–2025 (Orbis-vienti 7.11.2026) | tietokanta | **Orbiksen lisenssi on akateeminen; lukua ei saa käyttää palautuksessa sellaisenaan.** Sama tieto on julkisessa tilinpäätöksessä (PRH), jota ei vielä ole hankittu |
| L13 | Vainu, Europress Group Oy (emoyhtiö) | julkinen yritystieto | emoyhtiö 2025: liikevaihto ~40 M€, liikevoitto 6 % |
| L14 | HSY:n logistiikkapäällikön sähköposti 26.6.2026 (Smartbins-validointi) | henkilökohtainen viesti | |
| L15 | Mike: "Plus-malli: kestävä versio – yhteenveto" 7.11.2026 | tiimin dokumentti | hinnat ja tarkkuudet ovat Miken arvioita |
| L16 | Tamtron/Lahti Precision BC5 -punnitusanturin datalehti | valmistajan dokumentti | ei hintaa |

---

## 1. Kansilehti

### 1.1 "Asiakkaan hyöty ~1 900 € / laite / vuosi, ilmaiseksi" — SIMULOITU + OLETUS

Summa viidestä osasta (L1, `analysis/economics_full.py`, `analysis/value_pools.py`):

| Osa | € / laite / v | Laskenta | Varmuus |
|---|---|---|---|
| Täysien kuormien säästö, asiakkaan puolikas | 634 | 1 269 € × 50 % (ks. 2.2) | SIMULOITU × OLETUS (50/50-jako) |
| Kilpailutus ja uudelleenneuvottelu | ~806 | 7,9 % × 10 200 € (ks. alla) | SIMULOITU |
| Kiistettävät lisämaksut | ~248 | (559 + 209 + 59) € × 30 % | SIMULOITU × OLETUS (30 %) |
| Väärä jäte | ~122 | 407 € × 30 % | SIMULOITU × OLETUS (30 %) |
| Laskuvirheet | ~94 | 49 + 36 + 7 + 2 € | SIMULOITU |
| **Yhteensä** | **~1 904** | | |

**Osien perustelut:**
- **10 200 €** on asiakkaan keskimääräinen kokonaiskulu per laite per vuosi: `reference_economics.total_customer_cost_eur` summattuna laitteittain, jaettuna 304/365 vuodella, keskiarvo laitteiden yli (mediaani 6 578 €). Keskiarvoa nostaa muutama kallis laite.
- **7,9 %**: `labels_dev/operator_action_values`. Jokaiselle 207 sopimukselle on laskettu paras toimenpideyhdistelmä (kiistä lasku, pyydä punnitusdata, neuvottele, kilpailuta). Parhaiden yhdistelmien arvo on keskimäärin 1 064 € sopimusta kohden, kun sopimuksen vuosikulu on keskimäärin 13 459 €. 1 064 / 13 459 = 7,9 %. Keskiarvossa ovat mukana myös ne 52 % sopimuksista, joissa paras toimenpide on "ei mitään" (arvo 0). Sovelsin 7,9 %:a 10 200 €:n keskikuluun, koska nämä 207 sopimusta ovat osajoukko eikä niiden kulutaso vastaa kaikkia laitteita.
- **559, 209, 59 €**: lisämaksurivit `reference_charge_lines`: ylitäyttömaksu (SIDE_WASTE_FEE), hätätilauksen lisä (EMERGENCY_SURCHARGE), turhan käynnin maksu (WASTED_TRIP_FEE), per laite per vuosi.
- **407 €**: `anomaly_labels`, perhe CONTAMINATION_VALUE_LOSS, `value_at_stake_eur` per laite per vuosi.
- **49 + 36 + 7 + 2 €**: `anomaly_labels`, perheet DUPLICATE_LINE, UNMATCHED_LINE, WRONG_SURCHARGE, WEIGHT_BASIS_MISMATCH.

**Epävarmuudet ja rehellinen arvio:**
- **30 %:n toteutumisaste** lisämaksuille ja väärälle jätteelle on **ARVAUS**. En löytänyt mitään, mihin sen voisi perustaa. Datapaketin `commercial_assumptions.yaml` jättää nämä tarkoituksella tiimin valittaviksi.
- **50/50-jako** täysien kuormien säästöstä asiakkaan ja jäteyhtiön kesken on **OLETUS**. Todellisuudessa jako riippuu kilpailun kireydestä.
- **Mahdollinen päällekkäisyys:** kilpailutuksen arvo (806 €) lasketaan sopimusehtojen muutoksesta, ja osa siitä voi syntyä samoista turhista tyhjennyksistä kuin täysien kuormien säästö. En ole poistanut päällekkäisyyttä. Pahimmassa tapauksessa asiakkaan hyöty on noin 1 100–1 300 € eikä 1 900 €.
- Jätin pois perheen PREMATURE_UNJUSTIFIED (738 €), koska se on lähes sama asia kuin täysien kuormien säästö. Jätin pois myös COST_PER_T_HIGH (1 245 €), koska se kuvaa kallista hintaa eikä suoraan saavutettavaa säästöä.
- Kaikki on synteettistä dataa. Datapaketin ohje sanoo suoraan: "Never present a number from it as a real saving."

### 1.2 "Jäteyhtiön hyöty ~1 400 € / laite / vuosi; nyt se tienaa laitteesta 0–800 €" — SIMULOITU + ARVIO + HAVAITTU

| Osa | € / laite / v | Laskenta | Varmuus |
|---|---|---|---|
| Täysien kuormien säästö, jäteyhtiön puolikas | 634 | 1 269 € × 50 % | SIMULOITU × OLETUS |
| Vähemmän turhia käyntejä | 130 | 0,89 turhaa käyntiä/v × ~131 €/käynti ≈ 116 €, pyöristetty ylöspäin | SIMULOITU, **pyöristys liian suuri** |
| Hinnoitteluriskin pieneneminen | 643 | 1 930 € / 3 vuotta (ks. 2.3) | SIMULOITU × OLETUS |
| **Yhteensä** | **~1 407** | | |

- **0,89 turhaa käyntiä per laite per vuosi**: `collection_events.status = WASTED_TRIP`, 332 kpl / 447 laitetta / (304/365).
- **~131 € per käynti**: (tyhjennysmaksu 4 700 + kuljetus 1 716) € / 49,15 tyhjennystä per laite per vuosi. Tämä on asiakkaan maksama hinta, ei jäteyhtiön kustannus. Jäteyhtiön todellinen kustannus turhasta käynnistä (auto + kuljettaja) on luultavasti pienempi. **Rehellisesti: 130 € on yläraja, ja oikea arvo on luultavasti 60–116 €.**
- **"Nyt se tienaa laitteesta 0–800 €"**: 10 200 € × liikevoitto-% (L&T 8,0 %, Stena 2,7 %, L&T Q1/2026 −0,9 %, Remeo −3,7 %). Ks. luku 6.2. **Heikkous:** oletan, että jäteyhtiön liikevaihto laitetta kohden on sama kuin asiakkaan kokonaiskulu. Siihen sisältyy käsittelymaksuja, jotka jäteyhtiö maksaa eteenpäin jäteasemalle (joskus itselleen). Lisäksi koko yhtiön liikevoitto-% ei ole sama kuin yritysasiakkaiden puristinliiketoiminnan liikevoitto-%.

### 1.3 "Europressin NPV +2,5 M€ (10 v); täydessä vauhdissa +2,4 M€ kassavirtaa vuodessa" — OLETUS

Laskettu mallilla `analysis/final_v2.py` (N = 20 000, NEW = 1 200, punnitus 825 €). Kaikki oletukset ja vuositaulukko luvussa 6.3. NPV on 2,49 M€. Vuoden 10 kassavirta on 2,38 M€. Luvut ovat **mallin tuloksia, eivät ennusteita**. Ne ovat herkkiä erityisesti punnituksen hinnalle ja jäteyhtiöiden omaksumiselle (luku 7).

### 1.4 Tunnisteet "Punnitus jokaiseen uuteen puristimeen", "Asiakkaalle ilmainen", "Jäteyhtiö maksaa datasta", "Tekoäly raportoi ja ennustaa"

Nämä ovat konseptin valintoja, eivät väitteitä. Perustelut luvuissa 3 ja 4.

---

## 2. Sivu 2: Ongelma

### 2.1 "33 % tyhjennyksistä tehdään alle 60 %:n täytöllä" — SIMULOITU

`collection_events`, status COMPLETED (18 297 tyhjennystä), kenttä `device_fill_pct_before < 60`: osuus 33,0 %. Täyttöasteen kvantiilit tyhjennyshetkellä: 10 %: 25,6; 25 %: 49,1; mediaani 72,2; 75 %: 87,8.

**Rajoitus:** osa vajaista tyhjennyksistä on perusteltuja: hygieniasäännöt, biojätteen enimmäisvälit, aukiolot ja varmuustilaukset ennen pyhiä. Datan labeleissa on erikseen perhe EARLY_JUSTIFIED (2,3 per laite per vuosi). 33 % ei siis tarkoita, että kolmannes olisi turhia.

### 2.2 "Täysillä kuormilla tyhjennyksiä tarvittaisiin 18 % vähemmän" — SIMULOITU + OLETUS

`analysis/economics_full.py`:
1. Jokaiselle laitteelle lasketaan "täyden kuorman paino": niiden tyhjennysten mediaanipaino (`billing_mass_kg`), joissa täyttöaste oli ≥ 80 %.
2. Tarvittavat tyhjennykset = laitteen vuoden tonnit / täyden kuorman paino, enintään toteutuneet tyhjennykset.
3. Tyhjennykset vähenevät yhteensä 17,9 %. Keräyskulut (tyhjennysmaksu, kuljetus, lisät) laskevat 16,9 % = 1 269 € per laite per vuosi.

Sopimustyypeittäin säästö on: kiinteä hinta per tyhjennys 2 195 €, hybridi + minimi 1 553 €, hybridi 1 230 €, hinta per tonni 855 €.

**Rajoitukset:**
- Malli olettaa, että jokainen tyhjennys voidaan tehdä täytenä. Todellisuudessa hygienian enimmäisvälit ja sesonkivaihtelu estävät osan tästä.
- Keräämön logistiikkapäällikkö (Smartbins-validointi) kertoi, että lähellä oleva 60 %:n astia tyhjennetään samalla ajolla, jotta alueelle ei tarvitse palata. Tätä logiikkaa malli ei huomioi.
- Säästö on siis **yläraja**. Datapaketin oma päätöstehtävä (task C, `decision_outcomes`) näyttää, että aggressiivinen tyhjennysten vähentäminen voi tuottaa piilokuluja (`hidden_cost_trap`).

### 2.3 "Uuden tarjoajan arvio kiloista per tyhjennys menee sokkona 21 % pieleen, kohteen painohistorialla 9 %" — SIMULOITU, tämän projektin ydinluku

`analysis/value_pools.py`, 440 laitetta:
- **Sokko:** tarjoaja tietää kohteesta vain sen, minkä voi nähdä: jae, kontin koko ja laitetyyppi. Arvio on samanlaisten laitteiden (`material_stream`, `container_volume_m3`, `equipment_class`) kilojen mediaani per tyhjennys. Virhe = |arvio − laitteen todellinen keskiarvo| / todellinen.
- **Profiili:** vuoden ensimmäisen puoliskon keskiarvo kiloista per tyhjennys ennustaa toisen puoliskon keskiarvoa.
- Tulokset: sokkona mediaanivirhe 20,6 %, 80. persentiili 43,2 %, yli 20 % pielessä 50,9 % laitteista. Profiililla mediaani 9,1 %, 80. persentiili 19,2 %, yli 20 % pielessä 19,1 %.

**Rehellisesti:**
- Sokkoarvio sisältää laitteen itsensä vertailuryhmään. Todellinen sokkovirhe on siksi hieman **suurempi** kuin 21 %, eli tämä on varovainen arvio.
- Profiilissa käytin jäteaseman punnitusta (laskutuspainoa), en laitteen punnitusta. Laitteen punnituksen virhe (luku 5) tulee tämän päälle, joten todellinen profiilivirhe on noin 10–12 %.
- Synteettisessä datassa painon vaihtelu on generoitu; todellisessa maailmassa ero voi olla suurempi tai pienempi.
- Siitä, että vakiintuneella yhtiöllä on painohistoria ja haastajalla ei, on vain vetäjän vahvistus (2.4). Määrällistä tutkimusta siitä, kuinka paljon tämä vaikuttaa kilpailutuksiin, ei ole.

### 2.4 "Vakiintunut voittaa joka kolmas vuosi" — HAVAITTU (osin)

L5: tiimin jäsen kuvasi tilanteen: "konservatiivinen jäteyhtiö … yhdeksän vuotta sitä dataa … ne voi aina heittää paremman tarjouksen". Vetäjä vastasi "Kyllä. Hyvä lähtökohta." ja kertoi, että sopimukset ovat tyypillisesti kolmivuotisia ja kilpailutetaan pääosin hinnalla.

**Rehellisesti:** vetäjä vahvisti asetelman, mutta ei antanut lukuja siitä, kuinka usein vakiintunut voittaa. Sana "voittaa" on tulkinta. Kolmen vuoden sykli on vetäjän ilmoittama tyypillinen arvo.

### 2.5 "Kuljetusyritys ei suoraan säästä, jopa menettää." — HAVAITTU

L14: HSY:n logistiikkapäällikön sähköposti 26.6.2026. Alkuperäinen lause: "Kuka säästää? Kuljetusyritys, joka tekee työn, ei suoraan säästä, jopa menettää." Lyhensin lainausta PDF:ään. Yhteys oli kunnallinen jätehuolto eikä yritysten puristimet, mutta kannustinlogiikka on sama: tyhjennyksistä maksetaan.

### 2.6 "~3 % kiinteistöpäällikön työajasta menee jätehuoltoon" — HAVAITTU (epävarma litterointi)

L5: vetäjän repliikki litteroitui muotoon "ne käyttää keskimäärin 3% työajastajia". Litterointi on sotkuinen, mutta lukuna 3 % on selvä. Lähdettä vetäjä ei maininnut, joten luku on todennäköisesti hänen arvionsa.

### 2.7 "SMART: −37 % tyhjennyksiä" — HAVAITTU

L7, epsmart.fi etusivu: "keskimäärin" 37 % vähemmän tyhjennyksiä, 58 % parempi täyttöaste, 40 % pienemmät kokonaiskustannukset. Nämä ovat Europressin omia markkinointilukuja. Menetelmää tai vertailukohtaa ei kerrota.

### 2.8 "Insights ~15 %:lla" — HAVAITTU

L4: vetäjä: "at the moment we have smart insights subscription-based service maybe in 15 percent of our complete". Tarkoittaa noin 15 %:a laitekannasta tai asiakkaista; litteroinnista ei selviä kumpi.

### 2.9 "Europress ei pääse viemään tapausta loppuun" — HAVAITTU (epävarma puhuja)

L5: "koska meidän tästä painoa, me ei pystyy viemään keissiä loppuun asti". Litterointi on niin sotkuinen, että en ole varma, onko puhuja vetäjä vai tiimin jäsen. Asiasisältö (ilman painoa säästöä ei voi todentaa) on kuitenkin linjassa vetäjän avausinfon kanssa (L4: "we don't know how much it weighs").

### 2.10 "Hinta lyödään lukkoon kolmeksi vuodeksi ilman Europressia" — HAVAITTU + päättely

Kolmen vuoden sopimukset: L5. Europress ei ole sopimusosapuoli: L2 (`START_HERE.md`: "Europress is currently not a party to transport or treatment") ja L4.

### 2.11 Scaletipper X1: "Jätettä heitetään ohi ja virheet kertautuvat; sopii vuokralaisten kulujen jakoon" — HAVAITTU

L6, vetäjä: "mikään ei estä, että joku heittää ohi sen kippauslaitteen … ne avaa kannen ja heittää sinne" ja "jos sulla on satoja kippaustapahtumia, joissa jokaisessa on mittausvirhe … se kertautuu … ei sitä voi käyttää arvioimaan luotettavasti, paljonko siinä lopulta kertyy". Käyttö kauppakeskuksissa vuokralaisten jakoon RFID-tunnisteilla: sama lähde. Tuotetiedot (1 kg:n tarkkuusväli, 440 kg maksimi, 150 toimijaa Tukkutorilla): L8.

### 2.12 "Tasovaaka yhtä kallis kuin koko puristin" — HAVAITTU

L6, vetäjä kennoista kiskojen alla: "sitten se on lähellä sitä meidän tasovaakaa … ne on tosi kalliita … vaatii semmoisen rakenteen … ne on sitten yhtä kallis kuin koko puristin". L5:ssä vetäjä arvioi nykyisen punnituksen lisäävän laitteen hintaan noin 20 %.

### 2.13 Johtopäätöslaatikko — päättely

"Painotieto on alan tärkein tieto": vetäjän "who owns the weight is the holy grail" (L4). "Kun paino on riippumaton ja ostettavissa, tietoetu katoaa": tämä on tiimin päättely, joka nojaa lukuun 2.3. Sitä ei ole testattu todellisessa kilpailutuksessa.

---

## 3. Sivu 3: Ratkaisu

### 3.1 Kierteen viisi vaihetta — päättely, osin HAVAITTU

| Vaihe | Perustelu | Varmuus |
|---|---|---|
| 1. Europress punnitsee jokaisen uuden puristimen, asiakas ei maksa | tiimin valinta, perustelu 3.2 | OLETUS / valinta |
| 2. Asiakkaan vaatimus saa jäteyhtiön mukaan | L6, vetäjä: Insights myydään asiakkaalle, "operaattori vaan sit hyödyntää niitä meidän palveluita, koska asiakas … vaatii" | HAVAITTU mekanismi; ei näyttöä, että sama toimii painodatalle |
| 3. Kilpaileva jäteyhtiö ostaa painodatan ja tarjoaa kilohinnan | päättely luvusta 2.3: tarkempi arvio → pienempi riskilisä → kilpailukykyisempi tarjous | **hypoteesi, ei testattu** |
| 4. Vakiintuneen on pakko seurata | markkinalogiikka | hypoteesi |
| 5. Jäteyhtiöt alkavat suositella Europressin laitteita | päättely: kilohinnoittelussa jäteyhtiön kate riippuu kuormien täyteydestä, ja tehokas puristin tuottaa täydempiä kuormia | hypoteesi; vastakkainen havainto L4: vakiintuneet "talk against" automaattista tilausta nykytilanteessa |

**Rehellisesti:** vaiheet 3–5 ovat projektin keskeinen hypoteesi. Mikään lähde ei todista niitä. Siksi luvussa 7 ehdotetaan pilottia.

### 3.2 "Jo 10–25 % pois jättäneitä asiakkaita syö maksullisuuden hyödyn" — ARVIO

`analysis/optout.py`. Verrattiin kahta mallia: punnitus ilmainen (kattavuus 100 %) ja punnitus maksaa asiakkaalle 10 €/kk, jolloin osa jättää sen pois. Verkostovaikutus mallinnettiin niin, että jäteyhtiöiden omaksuminen ja tarjouspakettien hyödyllisyys skaalautuvat kattavuuden potenssiin k (k = 1; 1,5; 2).

Tulos (sen hetken mallilla, punnitus 600 €, 6 vuotta):
- Maksullinen ilman poisjättäjiä: NPV +1,17 M€.
- 10 % poisjättäjiä: +0,23 / −0,07 / −0,36 M€ (k = 1 / 1,5 / 2). Eli 10 % syö 80–130 % maksullisuuden lisäarvosta.
- Raja, jonka jälkeen ilmainen on parempi: 39 % / 30 % / 24 % poisjättäjiä.

**Rehellisesti:**
- PDF:n muotoilu "10–25 %" on tiivistys. Tarkka tulos on: jo 10 % vie suurimman osan hyödystä, ja 24–39 %:n kohdalla ilmainen on suoraan parempi.
- Tämä laskelma tehtiin aiemmalla malliversiolla (6 vuotta, eri laitemäärä). Johtopäätös ei muutu, mutta luvut eivät ole samoja kuin luvun 6 mallissa.
- Verkostovaikutuksen muoto (kattavuus potenssiin k) on **OLETUS**. Perustelu: jäteyhtiö ei uskalla siirtyä kilohinnoitteluun koko asiakaskunnalleen, jos osa kohteista on punnitsematta.
- Poisjättäjien osuudesta ei ole dataa. Vetäjän mukaan asiakkaat ovat hintaherkkiä eivätkä maksa punnituksesta (L5), mikä tukee oletusta, että poisjättäjiä olisi paljon.

---

## 4. Sivu 4: Mitä rakennetaan

### 4.1 Toiminnot

Näkymien toiminnot ovat suunnitelma, eivät väitteitä. Niiden kytkentä haasteen tehtäviin (A, B, B2, C2, E) perustuu L2:n tiedostoon `docs/BENCHMARK.md`, jossa tehtävät on määritelty.

### 4.2 "Painon ja jäteaseman vaa'an ero ±3,3 %" — HAVAITTU (datapaketin oletus)

L2, `ECONOMIC_MODEL.md` §2b: "a difference beyond an agreed tolerance (e.g. the accuracy target of about ±3.3 %) triggers a review". Tämä on datapaketin esimerkkitoleranssi, ei Europressin vahvistama tavoite.

### 4.3 Tekoälyn tehtävät ja säännöt

Säännöt (ihmisen hyväksyntä, jäljitettävyys rivitasolle, neutraali sävy) tulevat suoraan haasteen arviointirubriikista (L2 `BENCHMARK.md`, "Rubric for D and E") ja `START_HERE.md`:n kohdasta "Ground rules". "Luvut tulevat aina laskennasta, eivät kielimallilta" on tiimin suunnitteluperiaate.

---

## 5. Sivu 5: Punnituskonsepti

### 5.1 Toimintaperiaate — ARVIO (fysiikka) + L15

Yksi hydraulisylinteri nostaa kontin takapäätä noin 10 mm. Etupää jää kiskoille ja toimii nivelenä. Momenttitasapaino nivelen ympäri:

R · L = W_kone · x_kone + W_jäte · x_jäte

missä R on sylinterin voima, L nivelen ja sylinterin välinen etäisyys ja x kunkin massan painopisteen etäisyys nivelestä. Kun tyhjällä kontilla mitattu voima R₀ vähennetään (R₀ · L = W_kone · x_kone):

**W_jäte = (R − R₀) · L / x_jäte**

Kaava on oikein, kun nosto on pieni (kulma noin 0,1°, jolloin vaakaetäisyydet eivät muutu käytännössä) ja runko on jäykkä.

**Painopiste x_jäte on menetelmän heikoin kohta.** Sitä ei mitata, vaan se päätellään. PDF:ssä se päätellään täyttöasteesta ja puristuskerroista eli siitä, kuinka pitkälle jäte ulottuu. Tämä on **OLETUS**: ei ole tiedossa, miten jäte kertyy CombiMaxissa (etupäähän puristimen viereen vai takapäähän). Vetäjältä ei ole kysytty tätä. Synteettisessä datassa ei ole painopistetietoa (L15 toteaa saman).

### 5.2 Mittaussekvenssi ja kitkan kumoaminen — ARVIO

Noston ja laskun aikana sylinterin tiivisteiden kitka vaikuttaa vastakkaisiin suuntiin: nostossa paine on todellista suurempi, laskussa pienempi. Keskiarvo kumoaa kitkan, jos se on symmetrinen. Tämä on tavallinen keino hydraulisissa punnitusjärjestelmissä. Täsmällistä kitkan suuruutta ei ole arvioitu.

### 5.3 "Kaikki puristimet": COMBI, DUO, nykyinen kanta — ARVIO, osin validoimaton

- **COMBI-perhe:** sylinteri koneessa, asennus tehtaalla. Perustelu: kone ja kontti ovat yhtä, ja hydrauliikka on valmiina (L15). CombiMax on COMBI-laite (tiimin toteamus).
- **DUO:** sylinteri kiskorakenteessa kontin takapäässä, puristimen hydrauliikasta. **Tämä on minun ehdotukseni, eikä sitä ole tarkistettu.** Avoimia kysymyksiä: DUO-kontti lukitaan puristimeen, joten osa painosta voi kulkea puristimen rungon kautta, ja lukitus voi estää nivelliikkeen. Mike'n dokumentti (L15) arvioi kiinteiden puristimien sopivuuden heikoksi ja ehdottaa niihin kiskokennoja tai tasovaakaa.
- **Nykyinen kanta:** jälkiasennus huollon yhteydessä. **ARVAUS** sen toteutettavuudesta. L15 arvioi jälkiasennuksen vaikeaksi, koska se vaatii runkomuutoksia. Talousmalli ei sisällä jälkiasennuksia.

### 5.4 Mitoitus

| PDF:n luku | Laskenta | Varmuus |
|---|---|---|
| Nostovoima ≈ 4–6 t (≈ 60 kN) | Vetäjä: kone noin 3 t, jätettä enintään noin 5 t (L5). Kokonaispaino 8–10 t. Takapään osuus oletettu 50–60 % → 4–6 t. 6 t × 9,81 ≈ 59 kN | ARVIO; painojakaumaa ei tunneta |
| Sylinteri Ø 80 mm → ≈ 120 bar < 200 bar | Pinta-ala π × 40² = 5 027 mm². 60 000 N / 5 027 mm² = 11,9 MPa = 119 bar. Järjestelmän maksimi 200 bar vetäjän mukaan (L4) | ARVIO, laskenta tarkka |
| Anturi 0–250 bar, ±0,25 % FS → ±30 kg | ±0,25 % × 250 bar = ±0,625 bar = 62 500 Pa. × 5 027 mm² = ±314 N ≈ ±32 kg | ARVIO; tavallinen teollisuusanturin luokka |
| | **Tarkennus:** ±32 kg on virhe sylinterin voimassa R. Jätteen painossa se kerrotaan suhteella L / x_jäte, joka on yli 1, koska jätteen painopiste on lähempänä niveltä kuin sylinteri. Jos L / x = 1,5–2, anturin osuus jätteen painon virheestä on ±50–65 kg. PDF:n "±30 kg" on siis voiman virhe, ei painon virhe. | **Korjattava PDF:ään** |
| Tarkkuus ±3 % täynnä, ±8–10 % puolitäynnä | Mike'n arvio (L15). Peruste: painopisteen epävarmuus pienenee, kun kontti on täynnä | ARVIO, **validoimaton** |
| Maahan: jalka kiskolla; levy 400 mm ≈ 0,4 MPa | 60 kN / (0,4 m × 0,4 m) = 0,375 MPa | Laskenta tarkka. **Asfaltin kantokykyä en ole tarkistanut lähteestä.** Lämmin asfaltti voi painua jo tällä paineella, vaikka kuormitus kestää vain noin 30 s. Siksi ehdotus on, että jalka painaa kiskoa eikä asfalttia, mutta kiskon ja sen kiinnityksen kestävyyttä ei ole tarkistettu |
| Hinta ≈ 550–1 100 € | L15: perusjärjestelmä 400–800 € + kestävyyslisät 150–300 €. Perustuu vähittäishintoihin ja oletettuun noin 50 %:n volyymialennukseen | ARVIO; OEM-tarjouksia ei ole |

### 5.5 Turvallisuus — ARVIO

Nosto vain 10 mm, kuristin, varoventtiili, mekaaninen pysäytin ja SMART-lukitus noudolle: nämä ovat tavallisia hydrauliikan turvaratkaisuja. Konedirektiivin mukaista riskiarviointia ei ole tehty.

### 5.6 "Biojäte punnitaan normaalisti, toisin kuin painesensorilla" — ARVIO (fysiikka) + HAVAITTU

Vetäjä (L4): biojäte on puristuspainesensorille vaikea, koska se antaa vähän vastapainetta. Sylinterin nostovoima riippuu vain massasta, ei jätteen koostumuksesta, joten biojäte ei ole erikoistapaus.

### 5.7 Vaihtoehtotaulukko

| PDF:n väite | Perustelu | Varmuus |
|---|---|---|
| Yksi sylinteri: vakaa, Europressin oma IP | vakaus: tiimin arvio (kolme tukipistettä). IP: Europress haluaa oman ratkaisun (L4) | **Patentoitavuutta ei ole tarkistettu.** Koukkulavettien ja trukkien hydraulisia punnitusjärjestelmiä on olemassa, ja haussa löytyi patentti paalainten jälkiasennettavasta punnituksesta (US11148383). IP-väite on toive, ei tosiasia |
| Kaksi sylinteriä: ei vakaa, koko yksikkö keikkuu | tiimin arvio (Nooa) | tiimin arvio; ei laskettu |
| Kennot kiskojen alla / tasovaaka / Scaletipper | kennojen hinta 530–1 300 € on tiimin osaluetteloarvio (luku 6.3). Vetäjän kommentit L6 | ARVIO + HAVAITTU |

---

## 6. Sivu 6: Talous

### 6.1 Arvo per laite vuodessa

Asiakas ~1 900 € ja jäteyhtiö ~1 400 €: ks. luvut 1.1 ja 1.2.

**Punnituksen kustannus ~190 € / v:** 825 € jaettuna 8 vuoden annuiteettikertoimella 8 %:n korolla (5,747) = 143,6 € + kalibrointi ja huolto 50 € (**OLETUS**) ≈ 194 €. 825 € on tiimin keskiarvoinen oletus Mike'n haarukasta 550–1 100 €.

### 6.2 Jäteyhtiöiden liikevoitto — HAVAITTU

| Yhtiö | Luku | Lähde | Huomio |
|---|---|---|---|
| L&T 2025 | liikevaihto 426,6 M€, liikevoitto 34,2 M€ → 8,0 % | L9, avainlukutaulukko 1–12/2025 | Jakautumisen jälkeinen kiertotalousliiketoiminta, carve-out-luvut. Sisältää myös vaaralliset jätteet ja teollisuuspalvelut (jätehuolto ja kierrätys 278,1 M€) |
| L&T Q1/2026 | liikevaihto 94,8 M€, liikevoitto −0,8 M€ → −0,9 % | L9 | Syyt raportin mukaan: jätehuollon volyymilasku, polttoaineiden hinnannousu, poistot ja jätteenkäsittelymaksujen nousu. Yksi neljännes, sesonkivaihtelu mahdollinen |
| Stena Recycling Oy 2025 | liikevaihto 176,1 M€, liikevoitto 4 693 000 € → 2,7 % | L10 | Asiakastieto ilmoittaa 3 %; laskin tarkemmin 2,67 %. Liikevaihto kasvoi 63,8 %, joten vuosi ei välttämättä ole tyypillinen |
| Remeo 2025 | liikevaihto 77,5 M€, liikevoitto-% −3,7 % | L11 | Finderin aggregaatti, ei alkuperäinen tilinpäätös |

"€ / laite / v" = 10 200 € × liikevoitto-%. Rajoitus: ks. luku 1.2.

### 6.3 Europressin 10 vuoden laskelma — OLETUS (tulokset riippuvat oletuksista)

Malli `analysis/final_v2.py`, funktio `pnl()`, parametrit N = 20 000 ja NEW = 1 200.

| Oletus | Arvo | Peruste | Varmuus |
|---|---|---|---|
| Laitekanta | ~20 000 | L6: "älykkäiden laitteiden kannassa … parikyt tuhatta, vähän vajaa" | HAVAITTU. Koskee koko konsernia (ei vain Suomea) ja älylaitteita |
| Uusia puristimia / v | 1 200 | L6: "puristimia tulee semmonen tuhannen kakssataa" (paalaimet pois) | HAVAITTU. Koko konsernin tehtaan tuotanto, ei vain Pohjoismaat |
| Punnitus | 825 € jokaiseen uuteen | Mike'n haarukan 550–1 100 € keskiarvo | ARVIO |
| Jäteyhtiön maksu | 30 € / laite / kk | 25 % jäteyhtiön arvosta (1 400 € × 25 % / 12 ≈ 29 €) | **OLETUS. Vertailukohtaa ei ole.** Vetäjä kertoi (L6), että Insightsin jälleenmyynnissä asiakas maksoi ja jäteyhtiö lisäsi vain ~10 % päälle. Siitä, että jäteyhtiö maksaisi itse, ei ole näyttöä |
| Omaksuminen | 60 % jäteyhtiöiden palvelemista punnituista laitteista, lineaarisesti 4 vuodessa | – | **ARVAUS.** Toiseksi herkin tekijä |
| Tarjouspaketit | 500 € × 2,5 tarjoajaa, 35 % kilpailutuksista, kilpailutus 3 v välein | 500 € ≈ 20 % yhden voitetun sopimuksen voitosta (10 200 € × 8 % × 3 v = 2 448 €). 2,5 tarjoajaa: ARVAUS; vetäjä ei tiennyt (L6). 35 %: ARVAUS | OLETUS |
| Lisämyynti | 0 → +5 % uusista laitteista, kate 25 % × 22 500 € = 5 625 € per laite | Laitteen hinta 20–25 k€ (L5). Kate 25 %: ARVAUS. +5 %: ARVAUS | **Heikko.** Pohjoismaissa noin 70 % laitteista on liisattuja (L6), joten kate kertyy vuokrasopimuksen aikana eikä kertamyynnistä. Mallissa kate kirjataan kertaluonteisesti |
| Kiinteät kulut | 400 k€ / v | noin 3 kehittäjää, pilvi ja kumppanipäällikkö | ARVIO |
| Alusta | 26 € / punnittu laite / v | data ja kielimalli | ARVAUS |
| Kalibrointi ja huolto | 50 € / punnittu laite / v | – | ARVAUS |
| Korko | 8 % | tavallinen yrityksen laskentakorko | OLETUS |

**Vuositaulukko (M€):**

| Vuosi | Punnittu | Jäteyhtiöt | Paketit | Lisämyynti | Kulut | Investointi | Kassavirta | Kertymä |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 200 | 0,06 | 0,04 | 0,00 | 0,49 | 0,99 | −1,37 | −1,37 |
| 2 | 2 400 | 0,26 | 0,17 | 0,08 | 0,58 | 0,99 | −1,05 | −2,43 |
| 3 | 3 600 | 0,58 | 0,39 | 0,17 | 0,67 | 0,99 | −0,52 | −2,94 |
| 4 | 4 800 | 1,04 | 0,70 | 0,25 | 0,76 | 0,99 | +0,24 | −2,71 |
| 5 | 6 000 | 1,30 | 0,88 | 0,34 | 0,86 | 0,99 | +0,66 | −2,05 |
| 6 | 7 200 | 1,56 | 1,05 | 0,34 | 0,95 | 0,99 | +1,01 | −1,04 |
| 7 | 8 400 | 1,81 | 1,22 | 0,34 | 1,04 | 0,99 | +1,35 | +0,31 |
| 8 | 9 600 | 2,07 | 1,40 | 0,34 | 1,13 | 0,99 | +1,69 | +2,00 |
| 9 | 10 800 | 2,33 | 1,57 | 0,34 | 1,22 | 0,99 | +2,03 | +4,03 |
| 10 | 12 000 | 2,59 | 1,75 | 0,34 | 1,31 | 0,99 | +2,38 | +6,41 |

NPV 8 %:lla: **+2,49 M€**. Kassavirta plussalla vuodesta 4, kertymä plussalla vuonna 7, syvin kertymä −2,94 M€ vuonna 3.

**Mallin rakenteelliset rajoitukset:**
- Jokaisen punnitun laitteen oletetaan olevan aktiivinen koko jakson. Poistuvia laitteita ei vähennetä, eli laskelma on tältä osin optimistinen.
- Laitteisto ostetaan myös uusiin laitteisiin, jotka korvaavat vanhoja, eli tältä osin varovainen.
- Tarjouspakettien tulo olettaa, että jokainen punnittu kohde kilpailutetaan kolmen vuoden välein.
- Kaikki tulot ovat yhden maan mittakaavassa, mutta laitekanta ja tuotanto ovat koko konsernin lukuja. Keski-Euroopassa (vähän liisausta, enemmän aikataulupohjaisia tyhjennyksiä) arvo voi olla erilainen.

### 6.4 "Syvin kertymä ≈ 0,7 × Europressin tulos ennen veroja 2025 (4,0 M€)" — HAVAITTU + laskenta

Europress-konserni 2025 (L12): liikevaihto 58,6 M€, tulos ennen veroja 3,97 M€, nettotulos 3,05 M€, oma pääoma 19,8 M€, omavaraisuus 67 %. 2,94 / 3,97 = 0,74.

**Lisenssihuomio:** luvut ovat Orbiksesta, jonka lisenssi sallii vain akateemisen käytön. Palautukseen sama tieto pitää hakea julkisesta tilinpäätöksestä (PRH:n Virre). Sitä ei ole vielä tehty. Vainun mukaan emoyhtiön liikevaihto oli noin 40 M€ ja liikevoitto 6 % (L13). Ero johtuu siitä, että Vainu näyttää emoyhtiön ja Orbis konsernin.

### 6.5 "+2,4 M€ / v ≈ +60 % nykyiseen tulokseen" — laskenta

Vuoden 10 kassavirta 2,38 M€ / 3,97 M€ = 0,60. **Vertailu on epätäsmällinen:** kassavirta ja tulos ennen veroja eivät ole sama asia, eikä vuoden 10 lukua voi verrata vuoden 2025 tulokseen ilman, että Europressin oma tulos muuttuu siinä välissä. Luku kuvaa suuruusluokkaa.

---

## 7. Sivu 7: Herkkyys ja riskit

### 7.1 Herkkyystaulukko — mallin tulos

Kaikki `final_v2.py`, N = 20 000, NEW = 1 200, muut parametrit kuten luvussa 6.3:

| Skenaario | NPV 10 v | Kertymä plussalla |
|---|---|---|
| Perus | +2,49 M€ | v7 |
| Punnitus 550 € | +4,71 M€ | v6 |
| Maksu 40 €/kk | +5,13 M€ | v6 |
| Omaksuminen 80 % | +5,13 M€ | v6 |
| Hidas omaksuminen (6 v) | +1,16 M€ | v8 |
| Ei lisämyyntiä | +0,95 M€ | v8 |
| Punnitus 1 100 € | +0,28 M€ | v9 |
| Maksu 20 €/kk | −0,15 M€ | v9 |
| Omaksuminen 40 % | −0,15 M€ | v9 |
| Punnitus 1 400 € | −2,14 M€ | ei |

Maksu 40 €/kk ja omaksuminen 80 % antavat saman tuloksen, koska tulo on maksu × omaksuminen: molemmat kasvattavat tuloa 33 %.

**"Kannattavuusraja 21 €/kk"**: pienin kokonaislukumaksu, jolla NPV ≥ 0, punnitus 825 €.

**"Jokainen +100 € punnituksessa ≈ −0,8 M€"**: (4,71 − 0,28) / 5,5 = 0,81 M€ per 100 €.

### 7.2 "Tavoite alle 800 € tehtaalla asennettuna"

Tiimin asettama tavoite: 800 €:lla NPV on noin +2,7 M€. Raja on noin 1 130 €, jossa NPV on nolla.

### 7.3 Pilotti: "Europress lopettaa ~1 M€:n tappiolla eikä 5–11 M€:n" — **PDF:n luku on liian pieni, korjattava**

Laskin pilotin kustannuksen tarkemmin:
- 1 000 laitetta × 825 € = 0,83 M€
- kiinteät kulut 2 × 400 k€ = 0,80 M€
- laitekohtaiset kulut 2 × 1 000 × 76 € = 0,15 M€
- **kulut yhteensä 1,78 M€**, tulot kahdelta vuodelta noin 0,27 M€ (jos omaksuminen etenee suunnitellusti)
- **nettotappio, jos pilotti lopetetaan: noin 1,5 M€**, ei ~1 M€.

Kiinteitä kuluja voi pilotissa pienentää (pienempi tiimi), jolloin tappio voi olla noin 1 M€, mutta PDF:n luku olettaa sen ilman, että se on laskettu.

"5–11 M€": pessimistisen skenaarion syvin kertymä aiemmissa malliversioissa oli −8,5…−11,2 M€. Nykyisellä mallilla pessimistinen skenaario (20 €/kk, punnitus 1 300 €, omaksuminen 40 %, hidas, ei lisämyyntiä) antaa samaa suuruusluokkaa. 5 M€ on alaraja kohtalaisen epäonnistumisen tapauksessa (punnitus 1 300 €). Luku on haarukka, ei tarkka laskelma.

### 7.4 Muut riskit

Tiimin listaamia, ei laskettu. Asiakkaan lupa datan jakamiseen: tiimi oletti "käytännössä varmaksi kyllä" kysymättä vetäjältä.

### 7.5 "Mitä emme tee"

| Väite | Peruste |
|---|---|
| Ei reittioptimointia | L4: Europress ei halua kuljetusbisnekseen ("definitely not … we are a technology company"); suora integraatio jäteyhtiöön oli "a huge challenge" ja "looks like that direction is not going to work". Lisäksi Smartbins-validoinnissa jäteyhtiöt kertoivat, että dynaaminen reititys ei sovi niiden ajojärjestelmiin ja kolmen viikon työvuorosuunnitteluun |
| Ei laskutusta laitteen painolla | L2 `ECONOMIC_MODEL.md` §2b: laitteen paino laskutusperusteena vaatisi mittauslainsäädännön ja osapuolten hyväksynnän |
| Ei kunnallista jätehuoltoa | L5 (vetäjä mainitsi kunnallisen sääntelyn) ja Smartbins-validointi: asukas ei voi valita jäteyhtiötä |
| Ei virtuaalivaakaa | tiimin päätös (Nooa): painoa ei voi luotettavasti päätellä puristuspaineesta |

### 7.6 Demo-tarina: "arvioitu säästö kilpailutuksella 2 100–3 400 €/v" — **ARVAUS / paikkamerkki**

Tätä lukua ei ole laskettu mistään. Se on havainnollistava esimerkki. Demossa luku pitää laskea todellisesta (synteettisestä) laitteesta tehtävän C2 arvoista. "Sama jäteyhtiö 9 vuotta" on tiimin jäsenen esimerkki keskustelusta L5.

---

## 8. Sivu 8: Data, tehtävät ja lähteet

### 8.1 Perustason tulokset — HAVAITTU (L2 `BENCHMARK.md`, validointijakso)

| PDF:n luku | Tarkka arvo lähteessä |
|---|---|
| A: 96 % sentilleen | net exact to cent 0,964 |
| B: macro-F1 0,73 | B2_rules 0,7309 (hybridi ML + säännöt 0,7818) |
| B: ennenaikaisten recall 0,59 | PREMATURE_UNJUSTIFIED recall 0,5941 |
| B2: 68 / 100 | score 67,75 |
| C2: regret 240 € | B6_rules mean regret 240,07 € |

"Miten parannamme" -sarake on suunnitelma, ei tulos. Parannuskohteet on valittu `BENCHMARK.md`:n osiosta "Known failure cases": B2 ei näe varmuustilauksia ennen viikonloppua (skenaario S39) eikä täyttöanturia, joka näyttää täyttä vaikka paino on pieni (S40). B6 ei huomioi jäteyhtiön laskutuksen laatua kilpailutuksessa.

### 8.2 "Data kuvaa tulevaisuutta, jossa useimmissa laitteissa on integroitu punnitus" — HAVAITTU

L2 `README_FIRST.txt`: "The dataset depicts a future scenario in which most devices have integrated weighing." Datan laitteiden `weight_measurement` on `INTEGRATED_SIMULATED`.

### 8.3 Vetäjältä listatut faktat — HAVAITTU

| Väite | Lähde |
|---|---|
| Laitekanta ~20 000, ~1 200 puristinta / v, ~70 % liisattuja Pohjoismaissa | L6 ("vielä vähemmän, seitkyt prosenttia" on litteroitu epäselvästi; luku 70 % on selvä) |
| Sopimukset ~3 v ja SLA, kilpailutus pääosin hinnalla | L5 |
| Kuljetus kiinteä per tyhjennys, käsittely ~3× kuljetus | L4: "let's say three times as high … it comes a bit out of my sleeve" eli vetäjän oma hatusta vedetty arvio |
| Asiakas ei maksa punnituksesta; Europress hyväksyy, jos elinkaari on plussalla | L5 |
| Kiskot kaikissa laitteissa; hydraulinen nosto "ei poissuljettu" | L6 |

### 8.4 "Yhdellä lauseella" — tiimin tiivistys

"Kun kannustimet kääntyvät, jäteyhtiöistä tulee Europressin myyjiä" on luvun 3.1 hypoteesi, ei todennettu.

---

## 9. Korjattavat kohdat PDF:ssä

Tätä liitettä kirjoittaessa löytyi neljä kohtaa, jotka PDF:ssä ovat epätarkkoja tai virheellisiä:

| Sivu | PDF:ssä | Pitäisi olla | Syy |
|---|---|---|---|
| 5 | Anturi ±30 kg | ±30 kg sylinterin voimassa, noin ±50–65 kg jätteen painossa | anturin virhe kerrotaan suhteella L / x |
| 6 ja kansi | Jäteyhtiön hyöty: turhat käynnit 130 € | ~60–116 € | 130 € on asiakkaan maksama hinta, ei jäteyhtiön kustannus; jäteyhtiön hyöty on silloin ~1 330–1 390 € |
| 7 | Pilotin tappio ~1 M€ | ~1,5 M€ | laskettu luvussa 7.3 |
| 7 | Demon "2 100–3 400 €/v" | lasketaan demossa todellisesta laitteesta | luku on keksitty esimerkki |

Lisäksi PDF:n asiakashyödyssä (~1 900 €) voi olla päällekkäisyyttä kilpailutuksen ja täysien kuormien välillä (luku 1.1). Pahimmillaan hyöty on ~1 100–1 300 €.

---

## 10. Yhteenveto: mihin projekti nojaa ja kuinka vahvasti

| Väite | Varmuus | Mikä sen vahvistaisi |
|---|---|---|
| Painotieto on jäteyhtiöllä ja sitä pantataan | vahva (vetäjä, useita lähteitä) | – |
| Ajoperusteinen laskutus palkitsee vajaista tyhjennyksistä | vahva (vetäjä, HSY, datan sopimusmallit) | – |
| Painohistoria antaa kilpailutuksessa merkittävän edun (21 % vs 9 %) | kohtalainen: logiikka vahva, luku synteettinen | todellinen tarjousdata jäteyhtiöltä |
| Yksi sylinteri riittää punnitukseen ±3 % täydellä kontilla | heikko–kohtalainen: fysiikka toimii, painopistemalli validoimaton | testi koekuormilla eri paikoissa konttia |
| Punnitus maksaa alle 1 100 € | heikko: vain vähittäishintoihin perustuva arvio | OEM-tarjoukset |
| Jäteyhtiö maksaa 30 €/kk | **heikko: ei vertailukohtaa** | pilotti |
| Jäteyhtiöt omaksuvat palvelun 60 %:sti neljässä vuodessa | **heikko: arvaus** | pilotti |
| Jäteyhtiöt alkavat suositella Europressia | heikko: hypoteesi | pilotti, haastattelut |
| Europressin NPV +2,5 M€ | yhtä vahva kuin heikoin oletus yllä | – |

Projektin ydinoivallus (kannustimet ja tiedon epäsymmetria) on hyvin perusteltu. Projektin talous nojaa kahteen testaamattomaan oletukseen: jäteyhtiöiden maksuhalukkuuteen ja omaksumisnopeuteen. Siksi PDF ehdottaa pilottia ennen koko laitekannan investointia.
