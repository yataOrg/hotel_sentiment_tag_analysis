-- create table
use tmp_htlbidb;
drop table tmp_yxdhtlcomms_city_total1;
create table if not exists tmp_yxdhtlcomms_city_total1 as
select b.city, b.hotel, c.cityname, b.hotelname, b.star
from dim_htldb.dimhtlhotel b
join dim_pubdb.dimcity c
on b.city = c.cityid
where b.masterhotelid<=0

-- use created table
select b.city, b.cityname, b.hotel, b.hotelname, a.writingid, a.writingcontent, b.star
from tmp_htlbidb.tmp_yxdhtlcomms_city_total b
join Olap_HtlbiModelDB.FactCommHotelValidComment a
on b.hotel = a.masterhotelid
where a.d = '2015-10-22';