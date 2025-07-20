-- count of UN member countries
select count(*) from countries
where un_member = 'true';

-- count of non-UN member countries
select count(*) from countries
where un_member = 'false';

-- count of countries from West Europe
select count(*)  from countries
where upper(subregion) like '%WESTERN EUROPE%';

-- countries that use the Euro
select count(*) from countries
where upper(currency_names) like '%EURO%';

-- count of countries without independence
select count(*)  from countries
where independent = 'false';

-- count of distinct continents and count of countries from each
select distinct(continents), count(*) from countries
group by continents;

-- count of countries with startofweek not Monday
select count(*) from countries
where start_of_week <> 'monday';




























































