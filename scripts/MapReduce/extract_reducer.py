#!/usr/bin/env python3
import sys

# Print CSV header with icon_category
print("position,latitude,longitude,state,event_type,magnitude,year,month,day,date,time,incident_id,point_index,total_points,icon_category")

# Process each line
for line in sys.stdin:
    values = line.strip().split('\t')
    cleaned_values = [v.replace(',', ' ') if v else '' for v in values]
    print(",".join(cleaned_values))
