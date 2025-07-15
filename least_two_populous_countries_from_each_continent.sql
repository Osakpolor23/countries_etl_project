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
order by continents