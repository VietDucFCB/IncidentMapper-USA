import json
import os
import subprocess
import glob

print("JSON Preprocessing for MapReduce - Starting")

# Create preprocessing script for container
preprocessing_script = """#!/usr/bin/env python3
import json
import os
import glob
import sys

def preprocess_file(input_file, output_file):
    \"\"\"Convert a pretty-printed JSON file to one incident per line\"\"\"
    try:
        print(f"Processing {input_file}...")

        # Read the entire file as a single JSON object
        with open(input_file, 'r') as f:
            data = json.load(f)

        # Check if it contains incidents
        if "incidents" not in data:
            print(f"No incidents found in {input_file}")
            return 0

        # Write one incident per line to the output file
        count = 0
        with open(output_file, 'w') as out:
            for incident in data["incidents"]:
                # Create a new JSON object with just this incident
                incident_json = {"incidents": [incident]}
                # Write as a single line
                out.write(json.dumps(incident_json) + "\\n")
                count += 1

        print(f"Wrote {count} incidents from {input_file}")
        return count
    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")
        return 0

def main():
    # Create directories
    os.makedirs("/tmp/json_processed", exist_ok=True)

    # Get all JSON files
    input_dir = "/tmp/traffic_data"
    output_dir = "/tmp/json_processed"

    # First, copy files from HDFS to local temp dir
    os.system("mkdir -p /tmp/traffic_data")
    os.system("hdfs dfs -copyToLocal /data_lake/raw/traffic_data/us/* /tmp/traffic_data/")

    # Process each file
    total_incidents = 0
    total_files = 0
    processed_files = 0

    for json_file in glob.glob(f"{input_dir}/*.json"):
        filename = os.path.basename(json_file)
        output_file = os.path.join(output_dir, filename)

        incident_count = preprocess_file(json_file, output_file)
        total_incidents += incident_count
        total_files += 1

        if incident_count > 0:
            processed_files += 1

    print(f"Processed {processed_files} of {total_files} files, extracted {total_incidents} incidents")

    # Create directory in HDFS and upload processed files
    os.system("hdfs dfs -mkdir -p /data_lake/processed/traffic_data_lines")
    os.system("hdfs dfs -put /tmp/json_processed/* /data_lake/processed/traffic_data_lines/")

    print("Preprocessing complete! Files uploaded to HDFS at /data_lake/processed/traffic_data_lines/")

if __name__ == "__main__":
    main()
"""

# Write script to container
print("Creating preprocessing script...")
subprocess.run('docker exec -i namenode bash -c "cat > /tmp/preprocess_json.py"',
               input=preprocessing_script.encode(),
               shell=True)

# Make executable and run
print("Running preprocessing script...")
subprocess.run('docker exec namenode chmod +x /tmp/preprocess_json.py', shell=True)
subprocess.run('docker exec namenode python3 /tmp/preprocess_json.py', shell=True)

print("Preprocessing complete! Your data is now ready for MapReduce.")