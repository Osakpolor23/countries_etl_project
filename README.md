# World Countries ETL Pipeline

This project builds a complete **ETL (Extract, Transform, Load)** pipeline using Python and PostgreSQL to ingest structured data from the [REST Countries API](https://restcountries.com). The pipeline parses, transforms, and stores each country’s metadata — enabling meaningful analysis using custom SQL queries.


## ETL Architecture Workflow

+----------------------+       +-----------------------+       +------------------------+
|   REST Countries API |  -->  | Python ETL Script     |  -->  | PostgreSQL (pgAdmin)   |
|   (JSON Responses)   |       | (Requests + psycopg2) |       |   Table: countries     |
+----------------------+       +-----------------------+       +------------------------+

    Extraction (E)                Transformation (T)                  Loading (L)    
────────────────────            ────────────────────                ─────────────────
• REST Countries API            • Merge chunked responses     • Connect using psycopg2 
• Two-part data requests        • Extract nested fields       • Create table with UNIQUE
• JSON responses retrieved      • Format values (strings)     • Insert with conflict check
                                • Structure into row tuples


## ETL Process Breakdown
### 1. Extraction
API endpoint: https://restcountries.com/v3.1/all
To avoid query limits, fields are split across two chunks:
    Basic info (name, region, languages, etc.)
    Area-related info (population, area, continents)  
Both responses are merged using zip() and dictionary unpacking.

### 2. Transformation
Each country record is flattened into a tuple using the transform_country() custom function:
    (
  country_name,
  official_name,
  native_names,
  currency_codes,
  currency_names,
  currency_symbols,
  idd_codes,
  capitals,
  region,
  subregion,
  languages,
  area,
  population,
  continents,
  independent,
  un_member,
  start_of_week
    )
Nested dictionaries and lists are joined using commas.
Defaults like "Unknown" or 0 are used where data is missing.

### 3. Loading
Connection handled via ***psycopg2***. Postgres database adapter for python.
Table creation if not already present.
Composite uniqueness constraint prevents duplicate ingestion.
Bulk insertion is handled using executemany() and conflict checking.

### Database Schema
    CREATE TABLE IF NOT EXISTS public.countries (
    id SERIAL PRIMARY KEY,
    country_name TEXT,
    official_name TEXT,
    native_names TEXT,
    currency_codes TEXT,
    currency_names TEXT,
    currency_symbols TEXT,
    idd_codes TEXT,
    capitals TEXT,
    region TEXT,
    subregion TEXT,
    languages TEXT,
    area REAL,
    population BIGINT,
    continents TEXT,
    independent BOOLEAN,
    un_member BOOLEAN,
    start_of_week TEXT,
    CONSTRAINT unique_country_profile UNIQUE (
        country_name,
        official_name,
        region,
        area,
        continents
    )
    );

### Conflict Resolution
On insertion, duplicate records are ignored using:

    ON CONFLICT ON CONSTRAINT unique_country_profile DO NOTHING;

This ensures the script is idempotent and safely re-runnable without issues of duplicate insertions.

### SQL Analysis Queries on the postgres db
Included are various insights-driven .sql files to query the ingested data.

**Examples:**
count_of_countries_with_more_than_one_official_languages.sql

least_two_populous_countries_from_each_continent.sql

top_5_largest_countries_by_area.sql

count_of_french_speaking_countries.sql

count_of_non_unmember_countries.sql

Each file contains a clean SELECT query ready for use in pgAdmin or programmatic execution.

### 🤝 Community & Collaboration

This project was built with open data, open code, and an open mind.

Feel free to **clone**, **fork**, or contribute to this repository — whether you're fixing a bug, enhancing the pipeline, adding new insights, or just experimenting with global data. Pull requests and ideas are always welcome!

Your improvements might shape how we understand the world — one country at a time.
A bientot!
