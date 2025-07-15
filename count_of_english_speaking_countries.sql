-- count of English-speaking countries
select count(*) from countries
where upper(languages) like '%ENGLISH%';
