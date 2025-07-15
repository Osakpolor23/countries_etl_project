ALTER TABLE public.countries
ADD CONSTRAINT unique_country_profile UNIQUE (
    country_name,
    official_name,
    region,
    area,
    continents
);
