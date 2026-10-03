# Festival coverage vs. Drik Panchang

A gap analysis of Kalagana's rule engine against the **2026 Hindu festival
calendar** published by
[drikpanchang.com](https://www.drikpanchang.com/calendars/hindu/hinducalendar.html).

Nothing here is stored — every date is *computed* from a `FestivalRule`.
This document records what we now cover and what remains.

---

## 1. Coverage at a glance

| Group | Where | Count (rules) |
|---|---|---|
| Major pan-Indian (lunar + solar) | `FESTIVAL_RULES` | ~55 |
| Secondary / regional / named vrats | `SECONDARY_RULES` | 62 |
| Islamic (Hijri) | `ISLAMIC_RULES` | 9 |
| Fixed Gregorian-date | `FIXED_RULES` | 44 |
| Monthly vrats | `_MONTHLY` | 10 |

Adding `SECONDARY_RULES` closed **most** of the gap against the Drik list:
named Ekadashis, the month-specific vrats (Sakat Chauth, Hariyali Teej,
Rishi Panchami, …), the jayantis (Narada, Parashurama, Shani, Balarama,
Radha, Kalabhairav, Dattatreya, …) and the common aliases (Rakhi, Chhoti
Holi, Kali Chaudas, Lakshmi Puja, Ganesh Visarjan, Jagannath Rathyatra,
Navratri Begins).

---

## 2. Now covered (added this round)

**Named Ekadashis (23):** Shattila, Jaya, Vijaya, Amalaki, Kamada, Varuthini,
Mohini, Apara, Nirjala, Yogini, Devshayani, Kamika, Shravana Putrada, Aja,
Parsva, Indira, Papankusha, Rama, Devutthana, Utpanna, Mokshada, Saphala,
Pausha Putrada.

**Vrats & jayantis:** Sakat Chauth, Mauni Amavas, Bhishma Ashtami, Sheetala
Ashtami, Basoda, Gauri Puja, Yamuna Chhath, Swaminarayan Jayanti, Parashurama
Jayanti, Ganga Saptami, Sita Navami, Narasimha Jayanti, Narada Jayanti, Vat
Savitri Vrat, Shani Jayanti, Ganga Dussehra, Hariyali Teej, Gayatri Jayanti,
Kajari Teej, Rishi Panchami, Balarama Jayanti, Radha Ashtami, Ganesh Visarjan,
Kojagara Puja, Sharad Purnima, Ahoi Ashtami, Govatsa Dwadashi, Kansa Vadh,
Devutthana, Tulasi Vivah, Kalabhairav Jayanti, Vivah Panchami, Dattatreya
Jayanti.

**Aliases:** Chhoti Holi, Rakhi, Kali Chaudas, Lakshmi Puja, Ganesh Visarjan,
Jagannath Rathyatra, Navratri Begins, Sharad Purnima, Kojagara Puja.

**Solar:** Vishwakarma Puja (Kanya Sankranti).

---

## 3. What remains

### 3.1 Named repetitions still run on the generic rule

We compute the day but under a generic name, so a *name* lookup won't find it:

| Drik name | Our rule |
|---|---|
| Pausha / Magha / Phalguna / … Purnima | `Purnima` (monthly) — month-specific naming not yet surfaced |
| Kumbha / Meena / Mesha / … Sankranti | `Sankranti` (monthly) — the rashi is known but not used as a name |
| Surya Grahan / Chandra Grahan | `eclipses_for_year` (not festival rules) |

### 3.2 Ambiguous / convention-dependent (deliberately skipped)

- **Saraswati Avahan / Saraswati Puja** — the day is sampradaya-dependent
  (Maha Saptami vs Ashtami vs Navami), so it is not hardcoded.
- **Padmini / Parama Ekadashi** — occur only in an **adhika** (leap) month;
  handled by the generic `Ekadashi` and the adhika-masa policy.

### 3.3 Known engine limitations

- **Kshaya (skipped) tithis.** A tithi that does not touch sunrise produces no
  match at the sunrise window (e.g. Dattatreya Jayanti in 2026, whose Purnima
  is skipped). Drik handles this with explicit *gauna* days; we do not yet.
- **Adhika-masa placement.** In a leap-masa year (e.g. 2026 *Adhika Jyeshtha*)
  a few month-named festivals (Ganga Dussehra, …) may sit in the nija rather
  than the adhika month — a genuine convention split between panchangs.

---

## 4. Verification

Against the Drik 2026 list (which renders for **Beijing**, so tithi-boundary
festivals can differ by ±1 day), **48 of 60** secondary festivals matched
exactly for Delhi; the rest differ by one day or fall on the adhika/kshaya
edge cases in §3.3. The added rules are exercised by `tests/test_secondary.py`.

> Nothing is stored. Every date above is recomputed for any year and place.
