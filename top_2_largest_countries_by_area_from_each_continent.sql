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