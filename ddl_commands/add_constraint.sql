/*modify the table schema to add contraints for data quality check before insertion of records.
This is done if it was not done at the table creation stage and it prevents the insertion
of duplicate records.
*/
ALTER TABLE public.countries
ADD CONSTRAINT unique_country_profile UNIQUE (
    country_name,
    official_name,
    region,
    area,
    continents
);
