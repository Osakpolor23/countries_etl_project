-- count of French-speaking countries
select count(*) from countries
where upper(languages) like '%FRENCH%';
