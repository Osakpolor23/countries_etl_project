-- countries that use the Euro
select count(*) from countries
where upper(currency_names) like '%EURO%';




