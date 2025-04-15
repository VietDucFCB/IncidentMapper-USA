import subprocess

print("Creating MapReduce job...")

mapreduce_script = """#!/bin/bash
# Create directories
mkdir -p /tmp/mapreduce_scripts

cat > /tmp/mapreduce_scripts/extract_mapper.py << 'EOF'
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
                    output = f"{position}\\t{latitude}\\t{longitude}\\t{state}\\t{event_type}\\t{magnitude}\\t{year}\\t{month}\\t{day}\\t{formatted_date}\\t{formatted_time}\\t{incident_id}\\t{i}\\t{len(coordinates)}\\t{icon_category}"
                    print(output)
    except Exception as e:
        sys.stderr.write(f"Error processing input: {str(e)}\\n")
EOF

# Create reducer script
cat > /tmp/mapreduce_scripts/extract_reducer.py << 'EOF'
#!/usr/bin/env python3
import sys

# Print CSV header with icon_category
print("position,latitude,longitude,state,event_type,magnitude,year,month,day,date,time,incident_id,point_index,total_points,icon_category")

# Process each line
for line in sys.stdin:
    values = line.strip().split('\\t')
    cleaned_values = [v.replace(',', ' ') if v else '' for v in values]
    print(",".join(cleaned_values))
EOF

# Make scripts executable
chmod +x /tmp/mapreduce_scripts/extract_mapper.py
chmod +x /tmp/mapreduce_scripts/extract_reducer.py

# Run MapReduce job
echo "Running MapReduce job to extract existing icon categories..."
hadoop jar /opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar \\
  -files /tmp/mapreduce_scripts/extract_mapper.py,/tmp/mapreduce_scripts/extract_reducer.py \\
  -mapper "python3 /tmp/mapreduce_scripts/extract_mapper.py" \\
  -reducer "python3 /tmp/mapreduce_scripts/extract_reducer.py" \\
  -input /data_lake/processed/traffic_data_lines \\
  -output /data_lake/processed/traffic_extracteds

# Copy results to a local file
hdfs dfs -copyToLocal /data_lake/processed/traffic_extracteds/part-* /tmp/powerbi/traffic_extracteds.csv
echo "Results saved to /tmp/powerbi/traffic_extracteds.csv"
"""

# Write script to container
print("Creating icon extraction MapReduce job script...")
subprocess.run('docker exec -i namenode bash -c "cat > /tmp/run_extract_mapreduce.sh"',
               input=mapreduce_script.encode(),
               shell=True)

# Make executable and run
print("Running MapReduce job...")
subprocess.run('docker exec namenode chmod +x /tmp/run_extract_mapreduce.sh', shell=True)
subprocess.run('docker exec namenode /tmp/run_extract_mapreduce.sh', shell=True)

# Copy results
print("Copying results to local machine...")
subprocess.run('docker cp namenode:/tmp/powerbi/traffic_extracteds.csv ./traffic_extracteds.csv', shell=True)

print(f"Process complete!")
print(f"Current Date and Time: 2025-04-14 07:32:15")
print(f"User: VietDucFCB")