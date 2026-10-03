# Prompt: Build an Offline Hindu Panchang and Festival Calculator in Python

Copy everything below the line into your AI coding assistant. Work phase by phase and do not move to the next phase until the current one passes its tests.

---

## 1. Role and goal

You are a senior Python engineer with working knowledge of positional astronomy and the Hindu (Vedic) calendar. Build a Python library and command line tool called `panchang` that computes a complete Drik Panchang and the dates of Hindu festivals for any year between 1900 and 2100, for any latitude, longitude and timezone, in North Indian and South Indian traditions.

The program must run with no internet access, no database, no downloaded ephemeris files, and no third-party packages. Every astronomical value must be computed from formulas written in the code itself. Festival rules must be stored as Python data structures inside the package, not in SQL, SQLite, JSON fetched from anywhere, or any external service. Machine learning is not to be used. Festival dates are deterministic results of astronomy plus rules.

## 2. Hard constraints

Use only the Python standard library (`math`, `datetime`, `dataclasses`, `enum`, `argparse`, `json`, `functools`, `zoneinfo` for timezones). Target Python 3.10 or newer. No network calls of any kind, and no reading of data files at runtime other than optional user configuration. All time handling must be explicit about timezone, and internal calculations must use Julian Day in UT with a documented Delta T approximation (use the Espenak and Meeus polynomial expressions). Every public function needs type hints and a docstring stating units (degrees, days, hours). Code must be pure and deterministic: the same inputs always give the same outputs, and the calculation core performs no I/O.

## 3. Package layout

```
panchang/
  __init__.py
  julian.py          # JD conversion, Delta T, sidereal time
  sun.py             # solar longitude, declination, right ascension, equation of time
  moon.py            # lunar longitude, latitude, distance (Meeus ch. 47 series)
  planets.py         # Mercury..Saturn, Rahu/Ketu (mean and true node)
  ayanamsa.py        # Lahiri (default), Raman, KP, selectable
  solver.py          # root finding: bisection plus secant on angle crossings
  sunrise.py         # sunrise, sunset, moonrise, moonset, with refraction and disc-limb correction
  limbs.py           # tithi, vara, nakshatra, yoga, karana with start and end times
  calendar_month.py  # masa, paksha, adhika and kshaya masa, amanta/purnimanta, ritu, ayana
  eras.py            # Vikram, Shaka, Samvatsara (60-year), Kollam, Bengali, Gujarati
  muhurta.py         # Rahu Kalam, Gulika, Yamaganda, Abhijit, Brahma Muhurta, Choghadiya, Hora
  yogas.py           # Sarvartha Siddhi, Amrit Siddhi, Ravi Pushya, Panchaka, Bhadra, Gand Mool
  eclipses.py        # solar and lunar eclipses, Sutak
  transits.py        # sign ingress, retrograde, combustion, nakshatra pada changes
  festivals/
    rules.py         # festival rule table as Python dataclass instances
    engine.py        # rule interpreter
    regions.py       # regional variants and tie-break policies
  cli.py
tests/
  reference_dates.py # hardcoded known dates used as ground truth
  test_*.py
README.md
```

## 4. Phase 1: Astronomy foundation

Implement Julian Day conversion for Gregorian and Julian dates, Delta T, and Greenwich sidereal time. Implement the Sun's apparent geocentric longitude using Meeus chapter 25 (low accuracy is not enough; include the nutation and aberration corrections so the result is within about 0.01 degree). Implement the Moon's longitude, latitude and distance using the full periodic term tables from Meeus chapter 47, hardcoded as tuples. Implement Lahiri ayanamsa as the value at J2000 (about 23.85306 degrees, state your exact constant and source in a comment) plus the precession rate, using the proper precession formula rather than a flat 50.29 arcseconds per year, and allow the ayanamsa to be switched by configuration. The sidereal longitude is tropical longitude minus ayanamsa.

Write the generic root finder in `solver.py`. Given a function of time that returns an angle, it must find the instant when that angle crosses a target value, handling the 360 to 0 wraparound, to a tolerance of one second of time. Every later phase reuses this function.

Acceptance test: Sun and Moon longitudes for ten known dates match published values within 0.01 degree, and new moon and full moon instants for 2000 to 2030 match published tables within one minute.

## 5. Phase 2: Panchang limbs

Compute tithi as the floor of (Moon minus Sun longitude) divided by 12 degrees, giving 30 tithis, with exact start and end times found by the root finder. Compute nakshatra as the floor of sidereal Moon longitude divided by 13 degrees 20 minutes, including pada. Compute yoga from the sum of sidereal Sun and Moon longitudes divided by 13 degrees 20 minutes. Compute karana as half a tithi, with the 7 repeating movable karanas and the 4 fixed ones (Shakuni, Chatushpada, Naga, Kimstughna) placed correctly. Compute vara from the weekday at local sunrise, since the Hindu day begins at sunrise and not at midnight.

For a given date and place, return each limb that is active during that civil day with its start and end datetimes in local time, including the case where two tithis or two nakshatras occur in one day, and the case where a tithi is skipped (kshaya) or spans two sunrises (vriddhi).

Implement sunrise, sunset, moonrise and moonset for any latitude and longitude, using the standard altitude of the Sun's upper limb at minus 0.833 degrees and an option for the center of the disc. Handle polar cases by returning `None` rather than raising errors.

Acceptance test: for at least 20 location and date combinations (include Delhi, Mumbai, Chennai, Kolkata, Ujjain, Varanasi, Bikaner, Kota and one overseas city), sunrise and sunset are within one minute and tithi, nakshatra, yoga and karana end times are within two minutes of published Drik Panchang values placed in `tests/reference_dates.py`.

## 6. Phase 3: Calendar structure

Determine the lunar month (masa) in both systems. In the amanta system the month runs from one new moon to the next and takes its name from the sidereal sign the Sun enters during the month, with the month named after the sign preceding the Sun's ingress. In the purnimanta system the dark fortnight is assigned to the following month, which is the North Indian convention. Detect adhika masa as a lunar month with no sankranti inside it, and kshaya masa as one with two. Implement the sankranti finder and the solar months (Mesha to Meena) with the civil-day assignment rules for each regional solar calendar: Tamil (sunset-based rule), Malayalam (an aparahna cutoff), Bengali (midnight rule with the sunrise adjustment), and Odia. Compute ritu, ayana, Vikram Samvat, Shaka year, the 60-year Samvatsara name, Kollam year, and the Gujarati new year.

Acceptance test: adhika masa years match published records for 2000 to 2040 (for example 2012, 2015, 2018, 2020, 2023, 2026), and the Hindu new year dates for Chaitra Shukla Pratipada, Ugadi, Gudi Padwa, Tamil Puthandu, Vishu, Pohela Boishakh and Baisakhi match for 2000 to 2030.

## 7. Phase 4: Daily timings and yogas

Implement the day divided into eight parts for Rahu Kalam, Gulika Kalam and Yamaganda by weekday, Abhijit Muhurta around local noon, Brahma Muhurta before sunrise, day and night Choghadiya, planetary Hora, Durmuhurta, Varjyam and Amrit Kalam, and the lagna table with sign rising times at the given latitude. Implement Sarvartha Siddhi, Amrit Siddhi, Ravi Pushya, Guru Pushya, Panchaka, Bhadra (Vishti karana, noting whether it falls in Swarga, Patala or Prithvi), Gand Mool nakshatras, Chandrabalam, Tarabalam, and Dagdha and Vish yogas. Keep each rule in its own small function with a docstring citing the rule in plain words.

## 8. Phase 5: Eclipses and transits

For lunar eclipses, compute the Moon's passage through the Earth's umbra and penumbra using the Danjon method or Besselian elements from Meeus chapter 54, giving type (penumbral, partial, total), magnitude, contact times (P1, U1, U2, greatest, U3, U4, P4), and visibility at a given location. For solar eclipses, compute Besselian elements, magnitude, obscuration, type (partial, annular, total, hybrid), and local contact times with visibility check. Compute Sutak as 12 hours before a solar eclipse and 9 hours before a lunar eclipse in the traditional rule (4 prahar and 3 prahar), applying it only when the eclipse is visible at the location, and make the Sutak hours configurable.

For transits, compute the sign and nakshatra ingress of all planets, retrograde and direct stations, combustion using standard orb values per planet, and Rahu and Ketu movement. Include Guru Pushkaram and Shani transits as festival-adjacent events.

Acceptance test: all lunar and solar eclipses from 2020 to 2035 match NASA eclipse catalog dates, types and greatest-eclipse times to within five minutes, stored in the tests as constants.

## 9. Phase 6: Festival rule engine

Festival rules must be data. Define a frozen dataclass `FestivalRule` with these fields: `name`, `names_regional` (a dict of language to name), `system` (lunar or solar), `masa`, `paksha`, `tithi` or `sankranti`, `time_window` (one of sunrise, madhyahna, aparahna, pradosh, nishita, moonrise, arunodaya, or a custom function), `tithi_rule` (which day to choose when the tithi spans two days or is skipped), `nakshatra_condition` (optional), `weekday_condition` (optional), `regions` (a set from North, South, East, West, or specific states), `adhika_masa_policy` (observe in nija only, in adhika, or both), and `source_note` (a short plain-language note on the textual basis, such as Dharmasindhu or Nirnaya Sindhu). The engine reads the rules, finds the month and tithi for the requested year, and applies the time-window and tie-break logic to select the civil date.

Implement the common tie-break policies as separate, testable functions. These include: the day on which the tithi is present at sunrise, the day on which the tithi covers the madhyahna (for Rama Navami and similar), the day on which it covers the pradosh period after sunset (Diwali Lakshmi Puja, Holika Dahan with Bhadra avoidance), the day on which it covers nishita kaal (Maha Shivaratri, Janmashtami), the day with moonrise during the tithi (Karwa Chauth, Sankashti Chaturthi), the day on which the Ekadashi tithi is present at arunodaya (Smartha versus Vaishnava Ekadashi), and the Dashami-viddha avoidance logic. When two civil days are valid, return both and mark which tradition picks which.

The rule table must cover at least the following groups. Major pan-Indian festivals: Makar Sankranti, Vasant Panchami, Maha Shivaratri, Holika Dahan, Holi, Ugadi and Gudi Padwa, Chaitra Navratri, Rama Navami, Hanuman Jayanti, Akshaya Tritiya, Buddha Purnima, Rath Yatra, Guru Purnima, Nag Panchami, Raksha Bandhan, Krishna Janmashtami, Ganesh Chaturthi and Anant Chaturdashi, Pitru Paksha with Mahalaya Amavasya, Sharad Navratri, Durga Ashtami, Dussehra, Karwa Chauth, Dhanteras, Naraka Chaturdashi, Diwali, Govardhan Puja, Bhai Dooj, Chhath Puja, Kartik Purnima and Dev Deepawali. Monthly observances: all Ekadashis (24 named ones plus the adhika pair), Pradosh Vrat, Sankashti Chaturthi, Vinayaka Chaturthi, Amavasya and Purnima, Masik Shivaratri, Sankranti in each of the 12 months. Regional festivals: Pongal and Bhogi, Onam, Vishu, Puthandu, Pohela Boishakh, Durga Puja days (Shashthi to Dashami), Kali Puja, Bihu (Bohag, Magh, Kati), Lohri, Baisakhi, Teej varieties, Gangaur (Rajasthan), Ratha Saptami, Varalakshmi Vratam, Karthigai Deepam, Thaipusam, Vaikuntha Ekadashi, Maha Navami and Ayudha Puja, Kumbh and Pushkaram dates by planetary position. Allow adding new rules without touching the engine.

Acceptance test: for 2015 to 2030, at least 50 major festivals per year match Drik Panchang for New Delhi, and a separate regional test set matches for Chennai, Kolkata and Mumbai. Every mismatch must be listed in a `KNOWN_DIFFERENCES.md` file with a one-line reason (tradition difference or bug), and the unexplained mismatch count must be zero before declaring the phase done.

## 10. Phase 7: Interfaces

Provide a clean public API:

```python
from panchang import Location, daily_panchang, festivals_for_year, eclipses_for_year

loc = Location(name="Delhi", lat=28.6139, lon=77.2090, tz="Asia/Kolkata")
day = daily_panchang(date(2026, 11, 8), loc, ayanamsa="lahiri", month_system="purnimanta")
fests = festivals_for_year(2027, loc, tradition="north", include_monthly=True)
ecl = eclipses_for_year(2027, loc)
```

Provide a command line tool with subcommands `day`, `month`, `year`, `festivals`, `eclipses`, `muhurta`, and `find` (find the next date of a named festival). Options include `--lat`, `--lon`, `--tz`, `--tradition north|south|bengali|gujarati|tamil|malayalam`, `--ayanamsa`, `--format text|json|csv`, and `--lang en|hi|ta|te|kn|ml|bn|gu` for names. Provide a small built-in city list (major Indian cities with coordinates) as a Python dict so no lookup service is needed. Output must be readable text by default and valid JSON on request.

## 11. Accuracy, testing and quality

Write `pytest` tests, plus a plain `python -m panchang.selftest` runner so the project can be verified without installing pytest. Ground-truth data is a set of known dates you hardcode in `tests/reference_dates.py`; note in comments where each value came from, and ask me to supply or confirm any values you are unsure about instead of guessing. Report your accuracy as a table at the end of each phase: what was tested, how many cases, maximum error. Do not claim accuracy you have not measured. If a rule is disputed between traditions, implement both as options, document the default, and say so clearly rather than silently choosing one.

Performance target: a full year of daily panchang for one location in under 10 seconds on a normal laptop, using caching of computed Sun and Moon positions where useful.

## 12. Working method

Start by restating the plan and listing any assumptions or questions, then implement Phase 1 only. After each phase, show the test results, list what remains uncertain, and wait for my confirmation before continuing. Keep functions small, keep astronomy separate from calendar rules and from festival rules, and never hardcode a festival date for a specific year, since every date must come out of computation. If something cannot be computed offline with acceptable accuracy, say so explicitly instead of approximating quietly.

## 13. Definition of done

The program runs entirely offline using only the standard library. It produces tithi, nakshatra, yoga, karana, vara, sunrise, sunset, moonrise, moonset and daily timings for any date and location from 1900 to 2100. It identifies adhika and kshaya masa, lists the major and regional festivals with correct dates for North and South traditions, reports all solar and lunar eclipses with Sutak, and gives planetary transits. Test results show agreement with published panchangs for a decade of past years, with every remaining difference explained. A README documents the formulas used, their sources, the supported traditions, the known limits, and how to add a new festival rule.
