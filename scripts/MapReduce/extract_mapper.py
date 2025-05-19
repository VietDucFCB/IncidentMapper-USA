#!/usr/bin/env python3
import sys
import json
from datetime import datetime

# Process each line of input
for line in sys.stdin:
    try:
        # Parse JSON data
        data = json.loads(line.strip())

        if "incidents" in data and len(data["incidents"]) > 0:
            for incident in data["incidents"]: # Iterate over all incidents

                if "geometry" in incident and "coordinates" in incident["geometry"]:
                    coordinates = incident["geometry"]["coordinates"]

                    if not coordinates or len(coordinates) == 0:
                        continue

                    # Extract properties
                    props = incident["properties"]
                    incident_id = props.get("id", "unknown")
                    icon_category = props.get("iconCategory", 0)
                    magnitude_of_delay = props.get("magnitudeOfDelay", 0)
                    start_time_str = props.get("startTime", "")
                    end_time_str = props.get("endTime", "")
                    from_location = props.get("from", "unknown")
                    to_location = props.get("to", "unknown")
                    length = props.get("length", 0.0)
                    delay = props.get("delay", None)
                    road_numbers = ",".join(props.get("roadNumbers", [])) # Join list into a string
                    time_validity = props.get("timeValidity", "unknown")
                    state = props.get("state", "unknown")

                    event_code = "Unknown"
                    event_description = "Unknown"
                    event_icon_category = 0

                    if "events" in props and len(props["events"]) > 0:
                        first_event = props["events"][0]
                        event_code = first_event.get("code", "Unknown")
                        event_description = first_event.get("description", "Unknown")
                        event_icon_category = first_event.get("iconCategory", 0)
                    
                    # If iconCategory was 0 at the top level, use the event's iconCategory
                    if icon_category == 0:
                        icon_category = event_icon_category


                    # Format time fields
                    year = "unknown"
                    month = "unknown"
                    day = "unknown"
                    formatted_date = "unknown"
                    formatted_time = "unknown"

                    if start_time_str:
                        try:
                            dt = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%SZ")
                            year = dt.strftime("%Y")
                            month = dt.strftime("%m")
                            day = dt.strftime("%d")
                            formatted_date = dt.strftime("%Y-%m-%d")
                            formatted_time = dt.strftime("%H:%M:%S")
                        except ValueError: # Handle cases where parsing might fail
                            pass
                    
                    end_year = "unknown"
                    end_month = "unknown"
                    end_day = "unknown"
                    end_formatted_date = "unknown"
                    end_formatted_time = "unknown"

                    if end_time_str:
                        try:
                            dt_end = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M:%SZ")
                            end_year = dt_end.strftime("%Y")
                            end_month = dt_end.strftime("%m")
                            end_day = dt_end.strftime("%d")
                            end_formatted_date = dt_end.strftime("%Y-%m-%d")
                            end_formatted_time = dt_end.strftime("%H:%M:%S")
                        except ValueError:
                            pass


                    # Process each coordinate point
                    for i, point in enumerate(coordinates):
                        longitude = point[0]
                        latitude = point[1]

                        # Determine position
                        position = "middle"
                        if i == 0:
                            position = "start"
                        elif i == len(coordinates) - 1:
                            position = "end"

                        # Output with all extracted features
                        output_fields = [
                            str(position), str(latitude), str(longitude), str(state),
                            str(event_description), str(event_code), str(magnitude_of_delay),
                            str(year), str(month), str(day), str(formatted_date), str(formatted_time),
                            str(incident_id), str(i), str(len(coordinates)), str(icon_category),
                            str(end_year), str(end_month), str(end_day), str(end_formatted_date), str(end_formatted_time),
                            str(from_location), str(to_location), str(length),
                            str(delay if delay is not None else "null"), # handle None for delay
                            str(road_numbers), str(time_validity)
                        ]
                        print("\\t".join(output_fields))
    except Exception as e:
        sys.stderr.write(f"Error processing input: {str(e)}\\n")
