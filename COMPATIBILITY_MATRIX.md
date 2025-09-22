# COMPATIBILITY_MATRIX.md

This document explains the structure, meanings, and provenance of the repository's land-use compatibility matrix.

Source file: [`Compatibility Matrix.csv`](data/input/Compatibility Matrix.csv:1)

## Data dictionary

| Category | Definition |
|---|---|
| Administrative and Law Enforcement | Municipal offices, government buildings, police and emergency services, and associated support facilities. |
| Buffer Zone / Right-of-Way | Public corridors such as road verges, utility easements, and landscaped setbacks where development is restricted. |
| Commercial | General retail and service businesses (shops, small retail units, local offices). |
| Commercial - Residential | Mixed parcels with ground-floor commercial and upper-level residential units. |
| Commercial Residential | A mixed-use classification emphasizing equal presence of commercial and residential uses. |
| Commercial Services | Service-oriented commercial uses (banking, repair shops, salons, small clinics) that support local activity. |
| Commercial-Residential | Variant mixed-use classification (synonymous with "Commercial - Residential") used in source data; treated as mixed commercial and residential. |
| Centralized Commercial | Large-scale commercial centers, malls, or hub retail districts with higher intensity and footfall. |
| Cultural | Museums, galleries, libraries, community cultural centers and similar civic cultural facilities. |
| Cultural and Sports | Facilities combining cultural and sporting uses (stadiums with community spaces, cultural centers with sports halls). |
| Educational | General education facilities (schools, training centers) not otherwise specified by level. |
| Educational - High School | Secondary education institutions serving older adolescents. |
| Educational - Middle School | Education institutions serving middle-grade students. |
| Educational - Primary School | Elementary schools serving young children. |
| Existing Garden/Orchard | Small-scale cultivated gardens, orchards, and productive green plots (not public parks). |
| Green Space | Public parks, landscaped open spaces, and recreational greenery (non-agricultural). |
| Health and Medical Services | Clinics, small hospitals, medical offices, and outpatient care facilities. |
| Higher Education | Universities, colleges, and other tertiary education campuses. |
| Industrial | Heavy and light industry where manufacturing, processing or assembly occurs; may include emissions/noise. |
| Mixed-Use | Zones intended for a mix of residential, commercial, and other compatible urban functions. |
| Permanent Fairground/Exhibition | Dedicated land uses for fairs, exhibitions, trade shows and other periodic large events. |
| Religious | Mosques, churches, temples, and other places of worship and associated facilities. |
| Residential | Housing of varying densities (single-family, multi-family) unless otherwise specified. |
| River | River channels and associated floodplain or riparian functional area. |
| Sports | Sporting facilities (stadiums, tracks, courts) and outdoor athletic spaces. |
| Tourism and Hospitality | Hotels, hostels, guesthouses, and tourism-oriented businesses and amenities. |
| Transportation and Parking | Transport infrastructure (parking lots, bus terminals, transit depots) and associated land uses. |
| Urban Reserve (Land) | Land reserved for future urban expansion, held in a vacant or low-intensity state. |
| Urban Utilities and Infrastructure | Utility yards, substations, wastewater facilities, and infrastructure that may impose operational constraints. |
| Workshop and Warehouse | Small workshops, storage, and warehousing with light industrial operations and goods handling. |

## Scoring Rubric (1–5)

- 1: Fully Incompatible — Adjacency creates a direct, adverse impact (health, safety, noise, emissions, or severe land-value mismatch). Uses scored 1 should be avoided in direct adjacency without mitigation or separation.
- 2: Generally Incompatible — Adjacency is problematic and requires mitigation (setbacks, buffers, operational controls) to be acceptable.
- 3: Neutral / Conditional — Adjacency is acceptable under typical conditions; compatibility depends on operational details, scale, or time-of-day (requires case-by-case assessment).
- 4: Generally Compatible — Uses are broadly compatible with limited or no mitigation required in most contexts.
- 5: Fully Compatible — Uses are mutually supportive or synergistic; adjacency enhances functionality or amenity.

Guidance: When applying the rubric, document the rationale for any non-obvious interpretation (e.g., why a given workshop type received a 2 rather than a 3) and version-control changes to the CSV.

## Provenance (Qazvin case study)

The values in [`Compatibility Matrix.csv`](data/input/Compatibility Matrix.csv:1) were developed through structured consultations with three senior planners from the Qazvin Municipal Planning Office in May 2023 and subsequently reviewed by the research team. The process combined local professional judgment with literature-based heuristics for land-use compatibility. The final CSV represents a consensus judgment intended specifically for the Qazvin case study and the local planning context at the time of study.

Limitations: These values reflect local policy intent and local operational conditions in Qazvin. They are not universally transferable; researchers and practitioners should recalibrate the matrix when applying the framework to other jurisdictions.

## How to adapt

To adapt the compatibility matrix for another city or policy scenario:
1. Export the current CSV as a new version and record a clear changelog entry.
2. Run a structured expert elicitation with local planners, stakeholders, or domain experts.
3. Document provenance for each change (who, when, rationale).
4. Re-run the engine and publish both the new CSV and an updated `COMPATIBILITY_MATRIX.md` describing changes.

## Notes

- This markdown file and the CSV together form the auditable "policy-as-code" for the engine. Treat edits as governance decisions and keep them under version control.
- For automated reproducibility, include the matrix version (commit hash or tag) used for any published analysis and add a short provenance note in project metadata.
- For ultimate traceability, any published analysis should cite the specific Git commit hash of the Compatibility Matrix.csv version used in the experiment.
