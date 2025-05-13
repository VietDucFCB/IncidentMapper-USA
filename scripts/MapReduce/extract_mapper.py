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
            incident = data["incidents"][0]

            if "geometry" in incident and "coordinates" in incident["geometry"]:
                coordinates = incident["geometry"]["coordinates"]

                if not coordinates or len(coordinates) == 0:
                    continue

                # Extract properties
                props = incident["properties"]
                incident_id = props.get("id", "unknown")
                state = props.get("state", "unknown")

                # Get icon category directly from properties
                icon_category = props.get("iconCategory", 0)

                # If not found in main properties, try to get from first event
                if icon_category == 0 and "events" in props and len(props["events"]) > 0:
                    icon_category = props["events"][0].get("iconCategory", 0)

                event_type = "Unknown"
                if "events" in props and len(props["events"]) > 0:
                    if "description" in props["events"][0]:
                        event_type = props["events"][0]["description"]

                magnitude = props.get("magnitudeOfDelay", 0)

                # Format time fields
                start_time = props.get("startTime", "")
                year = "unknown"
                month = "unknown"
                day = "unknown"
                formatted_date = "unknown"
                formatted_time = "unknown"

                if start_time:
                    try:
                        dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
                        year = dt.strftime("%Y")
                        month = dt.strftime("%m")
                        day = dt.strftime("%d")
                        formatted_date = dt.strftime("%Y-%m-%d")
                        formatted_time = dt.strftime("%H:%M:%S")
                    except:
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

                    # Output with existing icon category
                    output = f"{position}\t{latitude}\t{longitude}\t{state}\t{event_type}\t{magnitude}\t{year}\t{month}\t{day}\t{formatted_date}\t{formatted_time}\t{incident_id}\t{i}\t{len(coordinates)}\t{icon_category}"
                    print(output)
    except Exception as e:
        sys.stderr.write(f"Error processing input: {str(e)}\n")
