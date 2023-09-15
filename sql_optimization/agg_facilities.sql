ALTER TABLE facilities ADD column fac_sum integer;

UPDATE facilities 
set fac_sum = ferry_t + ferry_i + bus_t + bus_i + bus_code_s + bus_supp + 
rail_i + rail_c + rail_h +rail_light + air_serve + bike_share + i_service;