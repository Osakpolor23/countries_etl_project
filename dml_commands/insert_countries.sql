-- insert countries.sql
INSERT INTO public.countries (
            country_name, official_name, native_names,
            currency_codes, currency_names, currency_symbols,
            idd_codes, capitals, region, subregion, languages,
            area, population, continents,
            independent, un_member, start_of_week
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT ON CONSTRAINT unique_country_profile DO NOTHING