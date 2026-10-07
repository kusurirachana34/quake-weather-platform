select
    cast(event_time at time zone 'UTC' as date) as quake_date,
    count(*) as quake_count,
    round(avg(magnitude)::numeric, 2) as avg_magnitude,
    max(magnitude) as max_magnitude,
    count(*) filter (where severity in ('moderate', 'major')) as significant_quakes
from {{ ref('stg_earthquakes') }}
group by 1
