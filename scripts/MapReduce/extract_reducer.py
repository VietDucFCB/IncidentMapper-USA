#!/usr/bin/env python3
import sys

# Print CSV header with all new fields
print("position,latitude,longitude,state,event_type,event_code,magnitude_of_delay,start_year,start_month,start_day,start_date,start_time,incident_id,point_index,total_points,icon_category,end_year,end_month,end_day,end_date,end_time,from_location,to_location,length,delay,road_numbers,time_validity")

# Process each line
for line in sys.stdin:
    values = line.strip().split('\\t')
    # Ensure all values are strings and replace commas to prevent CSV issues
    cleaned_values = [str(v).replace(',', ' ') if v is not None else '' for v in values]
    print(",".join(cleaned_values))
