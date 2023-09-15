
CREATE INDEX index_reviews_date ON public.reviews USING btree (date);
CREATE INDEX index_cluster_weather_tmax ON public.cluster_weather USING btree (tmax);
CREATE INDEX index_cluster_weather_tmin ON public.cluster_weather USING btree (tmin);
CREATE INDEX index_cluster_weather_perception ON public.cluster_weather USING btree (perception);