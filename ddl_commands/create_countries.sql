-- create_countries.sql
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
    )