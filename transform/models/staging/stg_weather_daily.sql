select
    city,
    weather_date,
    temp_max_c,
    temp_min_c,
    round(((temp_max_c + temp_min_c) / 2)::numeric, 1) as temp_avg_c,
    precipitation_mm,
    loaded_at
from {{ source('raw', 'weather_daily') }}
