-- count of French-speaking countries
select count(*) from countries
where upper(languages) like '%FRENCH%';

-- count of English-speaking countries
select count(*) from countries
where upper(languages) like '%ENGLISH%';

-- count of countries with more than one official language
SELECT count(*)
FROM public.countries
WHERE LENGTH(languages) - LENGTH(REPLACE(languages, ',', '')) >= 1; 
/*
The comma-separated languages are replaced by an empty string, making the count of each character,
one less than the length(i.e the count of each character including the spaces and commas).
A difference of 1 and above means one or more commas separated them initially.
*/




