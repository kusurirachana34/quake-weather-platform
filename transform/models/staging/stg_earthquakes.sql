select
    event_id,
    event_time,
    magnitude,
    place,
    trim(split_part(place, ',', -1)) as region,
    longitude,
    latitude,
    depth_km,
    case
        when magnitude >= 7 then 'major'
        when magnitude >= 5 then 'moderate'
        when magnitude >= 4 then 'light'
        else 'minor'
    end as severity,
    loaded_at
from {{ source('raw', 'earthquakes') }}
where event_type = 'earthquake'
  and magnitude is not null
