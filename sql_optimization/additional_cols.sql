ALTER TABLE hours ADD COLUMN open_span integer;


UPDATE hours
set open_span = dat.open_span
FROM 
(
SELECT bid, dow, 
REGEXP_REPLACE(
	round(EXTRACT(epoch FROM ((time '24:00:00' - open + close))/3600)::decimal, 0)::text, '^0', '24')::integer as open_span
FROM hours
WHERE open > close
) as dat (bid, dow, open_span)
WHERE hours.bid = dat.bid and hours.dow = dat.dow;


UPDATE hours
set open_span = dat.open_span
FROM 
(
SELECT bid, dow, 
REGEXP_REPLACE(
	round(EXTRACT(epoch FROM (close-open)/3600)::decimal, 0)::text,'^0','24')::integer  as open_span
FROM hours
WHERE open < close
) as dat (bid, dow, open_span)
WHERE hours.bid = dat.bid and hours.dow = dat.dow;


update hours set open_span = 24 where open = close;