with cities as (
    select
        city,
        cast(latitude as double precision) as latitude,
        cast(longitude as double precision) as longitude
    from {{ ref('cities') }}
),

quakes as (
    select
        event_id,
        magnitude,
        latitude,
        longitude,
        cast(event_time at time zone 'UTC' as date) as quake_date
    from {{ ref('stg_earthquakes') }}
),

city_quakes as (
    select
        c.city,
        q.quake_date,
        q.magnitude,
        6371 * 2 * asin(least(1.0, sqrt(
            power(sin(radians(q.latitude - c.latitude) / 2), 2)
            + cos(radians(c.latitude)) * cos(radians(q.latitude))
              * power(sin(radians(q.longitude - c.longitude) / 2), 2)
        ))) as distance_km
    from cities c
    cross join quakes q
),

nearby as (
    select
        city,
        quake_date,
        count(*) as nearby_quakes,
        max(magnitude) as max_nearby_magnitude
    from city_quakes
    where distance_km <= 1000
    group by 1, 2
)

select
    w.city,
    w.weather_date,
    w.temp_avg_c,
    w.precipitation_mm,
    coalesce(n.nearby_quakes, 0) as nearby_quakes,
    n.max_nearby_magnitude
from {{ ref('stg_weather_daily') }} w
left join nearby n
    on n.city = w.city
   and n.quake_date = w.weather_date
