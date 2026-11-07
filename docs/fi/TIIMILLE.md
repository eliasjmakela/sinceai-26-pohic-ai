> **Vanhentunut 7.11. illalla (tiimin työpaperi, säilytetty historiaksi).** Voimassa olevat päätökset ja luvut:
> `MASTER.md` §B–§C ja `PRODUCT.md`. Tärkeimmät muutokset: itsenostin (H7) jokaiseen uuteen COMBI-puristimeen
> 1 000 €:lla (ei kiskoja 10 %:iin eikä virtuaalivaakaa pääviestinä); jäteyhtiö maksaa 30 €/laite/kk (NPV +0,18 M€,
> takaisinmaksu v9); tiedon epäsymmetria ±37 % vs ±10 % (ei 21/9 %); ei "varmennettua painoa"; ei laskujen
> lataamista; OpenWeight ei välitä tarjouksia (jäteyhtiö suunnittelee hinnan, asiakas vertaa saamiaan tarjouksia).

# OpenWeight – mitä rakennetaan ja miksi

*Tiimin taustapaperi. Lue tämä ennen kuin aloitat, niin kaikki rakentavat samaa asiaa.*

---

## 1. Haaste yhdellä kappaleella

Europress valmistaa jätepuristimia, joita on kauppojen, kauppakeskusten, varastojen ja tehtaiden pihoilla.
Puristin tiivistää kartongin, muovin tai sekajätteen konttiin, ja jäteyhtiö käy tyhjentämässä sen. Jäteyhtiö
punnitsee kuorman omalla jäteasemallaan ja laskuttaa asiakasta. **Paino ratkaisee, paljonko asiakas maksaa,
mutta painon tietää vain jäteyhtiö.** Europress haluaa siirtyä laitevalmistajasta palveluyhtiöksi, ja sen
mielestä tie sinne kulkee painotiedon kautta. Haasteessa on kaksi osaa: (1) miten paino saadaan mitattua
halvalla puristimessa ja (2) miten painotiedosta tehdään liiketoimintaa. Tämä paperi koskee osaa 2, eli
ohjelmistoa. Punnituksen mekaniikka suunnitellaan erikseen.

## 2. Miksi ala ei liiku: kolme havaintoa

**Havainto 1: Jäteyhtiö hyötyy turhista tyhjennyksistä.**
Tyhjennyksestä maksetaan yleensä kiinteä hinta, joten mitä useammin jäteyhtiö käy, sitä enemmän se tienaa.
Datassa kolmannes tyhjennyksistä tehdään alle 60 %:n täytöllä. Jos jokainen kuorma olisi täysi,
tyhjennyksiä tarvittaisiin 18 % vähemmän. HSY:n logistiikkapäällikkö sanoi saman suoraan:
"Kuljetusyritys ei suoraan säästä, jopa menettää."

**Havainto 2: Painotieto on vakiintuneen jäteyhtiön suoja kilpailutuksissa.**
Sopimukset kilpailutetaan noin kolmen vuoden välein. Kohdetta pitkään palvellut yhtiö tietää vuosien ajalta,
montako kiloa kohteesta lähtee ja mitä sen hoitaminen maksaa. Haastaja tarjoaa sokkona. Datassa uuden
tarjoajan arvio menee keskimäärin 21 % pieleen, kun kohteen painohistorialla se menee 9 % pieleen. Siksi
haastaja ei uskalla tarjota kilohintaa, ja vakiintunut voittaa. Haasteen vetäjä vahvisti, että juuri näin käy.

**Havainto 3: Europressin nykyiset palvelut eivät osu rahaan.**
Europressin SMART näyttää täyttöasteen, tilaa tyhjennykset ja hoitaa huollon. Se lupaa 37 % vähemmän
tyhjennyksiä, mutta:
- se toimii jäteyhtiöiden kannustimia vastaan, joten vakiintuneet yhtiöt puhuvat sitä vastaan
- se myydään loppuasiakkaalle, joka käyttää jätehuoltoon noin 3 % työajastaan ja on hintaherkkä
  (lisäpalvelu vain noin 15 %:lla asiakkaista)
- siinä ei ole painoa, joten säästöä ei voi todentaa eikä laskua tarkistaa
- se ei ole mukana kilpailutuksessa, jossa jätehuollon hinta lyödään lukkoon kolmeksi vuodeksi
- Europressilla on jo punnitus (Scaletipper X1), mutta se on kallis, sopii vain astioilla syötettäviin
  kohteisiin, ja sen data jää vuokralaisraportteihin.

**Johtopäätös:** ongelma ei ole jäteyhtiöissä vaan kannustimissa. Kaikki toimivat järkevästi omista
lähtökohdistaan. Painotieto muuttaa kannustimet.

## 3. Ratkaisu: OpenWeight

Europress tuo painotiedon jokaiseen puristimeen ja tekee siitä palvelun, josta kolme osapuolta hyötyy:

**Loppuasiakas saa ilmaiseksi**
- tekoälyapurin, joka kertoo, kannattaako kilpailuttaa, auttaa siinä ja vertaa tarjoukset
- jatkuvan seurannan siitä, pitääkö jäteyhtiö sopimuksen: väliin jääneet käynnit, myöhästymiset,
  turhat tyhjennykset, ylilaskutus ja asiat, jotka eivät käy järkeen.

**Jäteyhtiö ostaa Europressilta**
- live-painot ja ennusteet omille asiakkailleen, jolloin se voi suunnitella kuormat ja ajaa tehokkaammin
- tarjouspaketin jokaisesta kilpailutettavasta kohteesta, jolloin se voi tarjota kilohinnan ilman riskiä.

**Europress saa**
- palvelutulon jäteyhtiöiltä
- lisämyyntiä, koska kilohinnoittelussa täydet kuormat ovat jäteyhtiön etu, ja se alkaa suositella Europressin laitteita.

**Miksi tämä toimii, vaikka SMART ei ole toiminut:** maksaja vaihtuu. Haastavat jäteyhtiöt maksavat, koska
data auttaa niitä voittamaan kilpailutuksia. Kun haastajat alkavat voittaa, vakiintuneiden on pakko seurata.
Asiakasta ei tarvitse saada maksamaan, vain kilpailuttamaan.

## 4. Mitä rakennetaan

Yksi web-sovellus, kolme näkymää ja yhteinen taustajärjestelmä.

### Näkymä 1: Loppuasiakas (kiinteistöpäällikkö)
Kaiken pitää olla valmiiksi pureskeltua, koska käyttäjällä ei ole aikaa.
- **Kuukausiraportti:** tekoäly kirjoittaa kolme tärkeintä asiaa euroina. Esimerkki: "Kartonkipuristin
  tyhjennettiin viisi kertaa alle puolillaan. Kilohinnalla olisit maksanut 410 € vähemmän." Jokainen luku
  avautuu laskelmaksi, ja jokaisessa suosituksessa on Hyväksy / Ei nyt.
- **Sopimuksen seuranta:** palvelutaso ja lisämaksut, poikkeamat korostettuina.
- **Laskujen täsmäytys:** lasku ladataan, rivit verrataan puristimen painoon ja tyhjennyksiin.
- **Kilpailutusapuri:** muistutus ennen sopimuksen päättymistä, säästöarvio, lupa jakaa painoprofiili,
  tarjousten vertailu ja tekoälyn selitys eroista.

### Näkymä 2: Jäteyhtiö
- **Tarjouspaketti:** kohteen painoprofiili (kilot per tyhjennys vaihteluväleineen, täyttymisnopeus,
  kausivaihtelu, 12 kk ennuste) ja hintalaskuri, joka laskee yhtiön omilla kustannuksilla kannattavan
  hinnan per tonni ja sen riskin.
- **Omat asiakkaat:** mitkä puristimet ovat täynnä lähipäivinä ja montako kiloa niissä on.
- **Varmennettu paino** jokaisesta tyhjennyksestä.

### Näkymä 3: Europress
- Verkosto, punnituksen kattavuus ja virtuaalivaa'an tarkkuus.
- Palvelutulo, kilpailutukset, jäteyhtiöiden laitesuositukset eli myyntiliidit.

### Taustajärjestelmä
- **Paino jokaiseen laitteeseen:** osaan laitteista punnitsevat ohjauskiskot (noin 10 %), ja niiden datalla
  opetetaan tekoälymalli eli virtuaalivaaka, joka arvioi painon kaikissa muissa laitteissa puristimen nykyisistä
  signaaleista (täyttöaste, puristuskerrat, puristuskuorma).
- **Tyhjennysten tunnistus, profiilit ja ennusteet** jokaiselle laitteelle.
- **Hinnoittelumoottori** jäteyhtiön tarjouksiin.
- **Täsmäytys ja palvelutason seuranta** sopimusta vasten.
- **Suosittelija:** säännöt laskevat toimenpiteet ja niiden euroarvon, kielimalli kirjoittaa selityksen.
  Luvut tulevat aina laskennasta, ei kielimallilta. Ihminen hyväksyy kaiken.
- **Luvat:** data kuuluu asiakkaalle, ja hän päättää, kenelle sitä jaetaan.

### Missä tekoäly on
1. **Virtuaalivaaka:** paino ilman punnitusanturia. Tämä on teknisesti vaikuttavin osa ja talouden ehto.
2. **Ennusteet vaihteluväleineen:** hinnoitteluriski on epävarmuutta, ja sen pienentäminen on se, mistä jäteyhtiö maksaa.
3. **Kielimalli asiakkaalle:** raportit, kilpailutuksen selitykset ja vastaukset kysymyksiin.

## 5. Demo-tarina (3 min)
1. Kauppaketjun kohde, jolla sama jäteyhtiö on ollut yhdeksän vuotta. Kukaan muu ei tiedä painoja.
2. Kiinteistöpäällikön raportti: "Sopimus päättyy 7 kk päästä, arvioitu säästö kilpailutuksella 2 100–3 400 €/v."
3. Hän antaa luvan jakaa painoprofiilin.
4. Haastaja avaa tarjouspaketin: sokkona virhe 21 %, profiililla 9 %. Se tarjoaa kilohinnan, joka on
   sille kannattava ja asiakkaalle halvempi.
5. Asiakas valitsee. Europress saa palvelutulon ja myyntiliidin.

## 6. Miksi tämä kannattaa: luvut

Laskettu haasteen synteettisestä datasta ja omista oletuksistamme. Suuruusluokkia, ei todellisia säästöjä.

| | |
|---|---|
| Asiakkaan jätehuoltokulut nyt | ~10 200 €/laite/v |
| Asiakkaan hyöty | ~1 900 €/laite/v (~19 %), ilmaiseksi |
| Jäteyhtiön hyöty | ~1 400 €/laite/v, maksaa 240 €/v → noin 6-kertainen tuotto |
| Europress, 10 000 laitetta Suomessa, 6 v | investointi ~1 M€, NPV ~1,9 M€, kassavirta plussalla vuodesta 3 |
| Kannattavuusraja | 12–35 €/laite/kk (vertailu: Enevo 10–14 €/kk) |

**Tärkein havainto:** kiskot kaikkiin laitteisiin kaataisivat talouden (NPV −4,8 M€). Kiskot noin 10 %:iin
kalibrointiverkostoksi ja virtuaalivaaka loppuihin tekee mallista kannattavan. Siksi virtuaalivaa'an tarkkuus
on projektin tärkein yksittäinen luku.

Tarkemmat laskelmat: `PROJECT.md` ja `analysis/`.

## 7. Mitä emme tee
- **Reittioptimointia.** Europress ei halua kuljetusbisnekseen, ja jäteyhtiöt kertoivat, että dynaaminen
  reititys ei sovi niiden ajojärjestelmiin ja työvuoroihin.
- **Laskutusta laitteen painolla.** Jäteaseman vaaka pysyy laskutusperusteena. Meidän paino on ennuste ja tarkistus.
- **Kunnallista jätehuoltoa.** Siellä asiakas ei voi valita jäteyhtiötä.
- **Ketään ei syyllistetä.** Palvelu on neutraali, ja kaikki jäteyhtiöt saavat sen samoin ehdoin.

## 8. Avoimet kysymykset
- Kuinka tarkka virtuaalivaaka on? Tämä mitataan ensimmäisenä.
- Antavatko asiakkaat luvan jakaa painoprofiilin? Oletus: kyllä, koska he hyötyvät kilpailutuksesta.
- Miten vakiintunut jäteyhtiö reagoi? Oletus: vastustaa ensin, seuraa kun alkaa hävitä.
- Biojäte on vaikein jae punnitukselle, joten se rajataan aluksi pois.
