# 02 — Feature Parity: Drik Panchang → Kalagana

A complete inventory of what drikpanchang.com offers (from its navigation,
sitemap and day-panchang page), mapped to our implementation status.

Legend — **Status:** `have` · `partial` · `missing` · `app-only` (content, not a
calculation). **Owner:** `pkg` (lives in the `kalagana` package) · `app`.
**Priority:** `P0` MVP · `P1` parity · `P2` later.

> Guardrail: every `pkg` item is a **computed** capability, never stored data.
> Content (`app-only`) is authored assets/markdown.

---

## A. Panchang

| Feature | Status | Owner | Priority | Notes |
|---|---|---|---|---|
| Daily panchang (Dainik) | have | pkg | P0 | tithi/nakshatra/yoga/karana/vara + timings |
| Month panchang (day-by-day) | have | pkg | P0 | `/month` + CLI `month` |
| Panchang for any city (world) | partial | pkg | P0 | city table exists; need worldwide city search |
| Location by lat/lon/tz/elevation | partial | pkg | P1 | lat/lon/tz done; elevation not yet |
| Chandrabalam / Tarabalam | missing | pkg | P1 | good/bad moon & star strength per rashi |
| Vinchudo / Vinchhudo | missing | pkg | P1 | south-style inauspicious windows |
| Nakshatra pages (28 incl. Abhijit) | partial | pkg | P1 | 27 nakshatras present; Abhijit page missing |

### A1. Daily panchang detail fields (target columns)
From the Drik day-panchang page — the full field set we aim to render:

- Sunrise, Sunset, Moonrise, Moonset.
- Tithi (+ end time), Nakshatra (+ pada, + end), Yoga (+ end), Karana (each
  half-tithi), Weekday, Paksha.
- Vikram Samvat, **Samvatsara** (Brihaspati), Shaka Samvat, **Gujarati Samvat**,
  Chandramasa (Amanta & Purnimanta), **Pravishte/Gate**.
- **Mantri Mandala** of Vikram Samvat (Raja / Senadhipati / Mantri /
  Dhanyadhipati / Sasyadhipati / Meghadhipati / Dhanadhipati / Nirasadhipati /
  Rasadhipati / Phaladhipati).
- Moonsign, Sunsign, **Surya Nakshatra**, **Surya Pada**, Nakshatra Pada.
- **Drik Ritu / Vedic Ritu**, **Dinamana / Ratrimana**, **Drik Ayana / Vedic
  Ayana**, Madhyahna.
- Auspicious: Brahma Muhurta, Pratah Sandhya, Abhijit, **Vijaya Muhurta**,
  **Godhuli Muhurta**, Sayahna Sandhya, **Amrit Kalam**, **Nishita Muhurta**.
- Inauspicious: Rahu Kalam, Yamaganda, **Aadal Yoga**, **Dur Muhurtam**,
  Gulikai Kalam, **Varjyam**, **Baana (Chora upto…)**.
- **Anandadi Yoga**, **Tamil Yoga**, **Chhatra / Siddha / Jeevanama / Netrama**
  (half-life "Hora" totals).
- **Nivas & Shool:** Homahuti, Disha Shool, Chandra Vasa, Agnivasa, Rahu Vasa,
  Kumbha Chakra, Shivavasa.
- **Other calendars/epoch:** Kaliyuga (years), Lahiri Ayanamsha, Kali Ahargana,
  Rata Die, Julian Date, Julian Day, National Civil Date, Modified Julian Day,
  National Nirayana Date.
- **Panchaka Rahita Muhurta** (day-long Good/Chora/Roga/Mrityu/Agni blocks).
- **Udaya Lagna Muhurta** (rising Lagna windows through the day).
- Day festivals & events; **Lagna Kundali** (planetary chart); Vedic (Ghati)
  clock; Rashifal; upcoming upavas/festivals; upcoming planetary events.

**Status vs us:** we have the core five limbs, sunrise/sunset/moonrise/moonset,
samvat/shaka/samvatsara, ritu, ayana, muhurta (rahu/yamaganda/gulika/abhijit/
brahma/durmuhurta/choghadiya/hora). The **bolded** items above are gaps.

## B. Regional panchang variants

| Feature | Status | Owner | Priority |
|---|---|---|---|
| Assamese Panjika | missing | pkg | P2 |
| Bengali Panjika | partial | pkg | P1 |
| Odia Panji | missing | pkg | P2 |
| Tamil Panchangam (+ Gowri Nalla Neram) | partial | pkg | P1 |
| Telugu Panchangam | partial | pkg | P1 |
| Malayalam Panchangam | partial | pkg | P2 |
| Marathi / Gujarati / Kannada Panchang | partial | pkg | P2 |
| Nepali Patro | missing | pkg | P2 |
| ISKCON Panchang / ISKCON Ekadashi | missing | pkg | P2 |

> We already have a `tradition=` axis (north/south/tamil/telugu/kannada/
> malayalam/bengali/odia/gujarati/marathi) that selects regional rules. These
> entries are about **display conventions** (month systems, naming, calendars),
> not just rules.

## C. Calendars

| Feature | Status | Owner | Priority |
|---|---|---|---|
| Hindu Calendar (year, festivals) | have | pkg | P0 |
| Indian Calendar | have | pkg | P0 |
| Monthly calendar grid view | partial | app | P0 | render month grid with tithi |
| Sankranti Calendar | partial | pkg | P1 |
| Diwali Calendar | have | pkg | P1 |
| Durga Puja Calendar | have | pkg | P1 |
| Shardiya / Chaitra Navratri | have | pkg | P1 |
| Regional calendars (Odia/Bengali/Gujarati/Marathi/Telugu/Tamil) | partial | pkg | P2 |
| ISKCON Calendar | missing | pkg | P2 |

## D. Muhurat

| Feature | Status | Owner | Priority |
|---|---|---|---|
| Choghadiya (day + night) | have | pkg | P0 |
| Shubha Hora | have | pkg | P0 |
| Abhijit Muhurat | have | pkg | P0 |
| Rahu Kala | have | pkg | P0 |
| **Vivah (marriage) Muhurat** | missing | pkg | P1 |
| **Griha Pravesh Muhurat** | missing | pkg | P1 |
| **Vehicle Purchase dates** | missing | pkg | P1 |
| **Property Purchase dates** | missing | pkg | P1 |
| **Lagna Table / Lagna Muhurat** | missing | pkg | P1 |
| **Gowri Panchangam** | missing | pkg | P1 |
| **Panchaka Rahita Muhurat** | missing | pkg | P1 |
| **Do Ghati Muhurat** | missing | pkg | P1 |
| **Shubha Dates** (day-of-week goodness) | missing | pkg | P2 |
| **Jain Pachchakkhan** | missing | pkg | P2 |
| **Pancha Pakshi activities** | missing | pkg | P2 |
| Auspicious Yogas (Sarvarthasiddhi, Amritsiddhi, Dwipushkar, Tripushkar, Ravi Pushya, Guru Pushya, Ravi Yoga) | missing | pkg | P1 |

## E. Vrat & Upavas

| Feature | Status | Owner | Priority |
|---|---|---|---|
| Ekadashi dates (+ Vaishnava) | have | pkg | P0 |
| Purnima / Amavasya dates | have | pkg | P0 |
| Sankashti Chaturthi | have | pkg | P0 |
| Ganesha Chaturthi / Vinayaka Chaturthi | have | pkg | P1 |
| Pradosham dates | have | pkg | P1 |
| Sankranti dates | partial | pkg | P1 |
| Masik Shivaratri / Durgashtami / Kalashtami | have | pkg | P1 |
| Chandra Darshan | missing | pkg | P1 |
| Satyanarayana Puja dates | missing | pkg | P1 |
| Dwadashi dates | partial | pkg | P2 |
| Skanda Sashti / Karthigai dates | partial | pkg | P2 |
| Shraddha (Pitru Paksha) dates | missing | pkg | P1 |
| Janmashtami dates | have | pkg | P1 |
| Vrat Katha (story content) | app-only | app | P1 |

## F. Festivals

| Feature | Status | Owner | Priority |
|---|---|---|---|
| Hindu festivals (year) | have | pkg | P0 |
| Festival **detail page** (date, significance, vidhi, tithi) | partial | app | P0 |
| Top 10 / featured festivals | app-only | app | P1 |
| Tamil / Malayalam / Sankranti festival sets | partial | pkg | P2 |
| Fixed-date national holidays & observances | have | pkg | P1 |
| Islamic (Hijri) festivals | have | pkg | P2 |
| Dashavatara / Navdurga / Hindu Deities pages | app-only | app | P2 |
| Regional Deities / Gurus & Saints / Pilgrim Places | app-only | app | P2 |
| 24 Vishnu Avatara | app-only | app | P2 |
| Puja Vidhi (procedure) pages | app-only | app | P1 |

## G. Jyotish (Vedic astrology)

| Feature | Status | Owner | Priority |
|---|---|---|---|
| Kundali / Janma Kundali (birth chart) | have | pkg | P1 | `kalagana.jyotish.kundali` (grahas, houses, Lagna) |
| Horoscope Match (kundali matching / gun milan) | have | pkg | P1 | Ashtakoota; Vashya/Yoni use simplified tiers |
| Divisional charts (Shodasavarga) | have | pkg | P1 | 16 vargas incl. D9 |
| Vimshottari dasha | have | pkg | P1 | maha/antar/pratyantar |
| Rashi / Moonsign calculator | have | pkg | P1 | |
| Sunsign calculator | have | pkg | P1 | tropical sunsign derivable |
| Birthstar (nakshatra) finder | have | pkg | P1 | |
| Lagna calculator | have | pkg | P1 | `kalagana.jyotish.ascendant` |
| Rashifal (daily/weekly/monthly/yearly) | missing | pkg | P2 |
| Gemstone calculator | missing | pkg | P2 |
| Rudraksha calculator | missing | pkg | P2 |
| Mangal Dosha | have | pkg | P2 | from Lagna/Moon/Venus |
| Kalasarpa Yoga | missing | pkg | P2 |
| Shani Sadesati | missing | pkg | P2 |
| Baby Name Finder (+ name initials) | missing | pkg | P2 |
| Shraddha calculator | missing | pkg | P2 |
| Sahasra Chandrodaya | missing | pkg | P2 |
| Prashnavali / Prashna Kundali | missing | pkg | P2 |

## H. Planets & Astronomy

| Feature | Status | Owner | Priority |
|---|---|---|---|
| Planetary positions (sun/moon/planets) | have | pkg | P1 | Sun..Saturn + nodes (Keplerian) |
| Planet Transit (gochara) | missing | pkg | P1 |
| Planet Combustion (Asta) | have | pkg | P2 | elongation limits |
| Planet Retrograde (Vakri/Margi) | have | pkg | P1 | daily-motion sign |
| Eclipse dates (solar + lunar) | have (approx) | pkg | P1 | refine accuracy/type |
| Graha Asta & Uday | missing | pkg | P2 |
| Indian Seasons (Ritu) | have | pkg | P1 |
| Winter/Summer Solstice, Equinoxes | have (partial) | pkg | P2 |

## I. Devotional content (lyrics, galleries)

| Feature | Status | Owner | Priority |
|---|---|---|---|
| Aarti / Chalisa / Stotram / Ashtakam collections | app-only | app | P2 |
| Vedic Mantra / Deities Namavali | app-only | app | P2 |
| Durga Saptashati / Sundarkand / Nama Ramayanam | app-only | app | P2 |
| Vedic Yantra | app-only | app | P2 |
| Gallery: paintings, mehandi, rangoli, greetings, icons | app-only | app | P2 |

> Devotional corpus is large, licensed content. Plan: curate a **small public-
> domain subset first** (aartis/chalisas), expand later with attribution.

## J. Platform & app features

| Feature | Status | Owner | Priority |
|---|---|---|---|
| Location switcher (city search, world) | partial | app+pkg | P0 |
| Date navigation (prev/next/today/picker) | have | app | P0 |
| 12h/24h/24-plus time formats | partial | app | P1 |
| Amanta/Purnimanta toggle | have | pkg | P0 |
| Ayanamsa selector | have | pkg | P1 |
| Settings (persist city, format, theme) | missing | app | P1 |
| PWA install + offline | missing | app | P0 |
| Share / deep links per date+city | missing | app | P1 |
| Multiple languages (i18n) | missing | app | P2 |
| REST API + docs | have | pkg | P1 |
| CLI | have | pkg | P1 |
| Mobile apps (native) | out of scope | — | — |

---

## Coverage summary (P0/P1)

- **P0** items: mostly `have` in the package (core panchang, festivals, vrat,
  choghadiya/hora). App must render them well + PWA.
- **P1** gaps to build (package): muhurat suite (vivah/griha pravesh/vehicle/
  property/lagna/gowri/panchaka rahita/do ghati), panchaka rahita & udaya lagna
  daily blocks, chandrabalam/tarabalam, vinchudo, planetary positions/transit/
  retrograde, auspicious yogas, chandra darshan, shraddha dates, kundali/match.
- **P2**: regional conventions, jyotish extras, devotional corpus, galleries.
