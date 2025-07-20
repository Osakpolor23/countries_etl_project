-- top 5 largest countries by area
select country_name, area from countries
order by area desc
limit 5;

-- Top 5 smallest countries by area
select country_name, area from countries
order by area asc
limit 5;

-- The two most largest countries by area from each continent
select country_name,
        area,
        continents
from
(SELECT 
        country_name,
        area,
        continents,
        ROW_NUMBER() OVER (
            PARTITION BY continents
            ORDER BY area DESC) as area_rank
	from countries
			)
where area_rank <= 2
order by continents;

-- The two least populous countries from each continent
select country_name,
        population,
        continents
from
(SELECT 
        country_name,
        population,
        continents,
        ROW_NUMBER() OVER (
            PARTITION BY continents
            ORDER BY population ASC) as pop_rank
	from countries
			)
where pop_rank <= 2
order by continents;



