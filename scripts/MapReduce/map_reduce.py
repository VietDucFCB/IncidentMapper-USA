import subprocess
import os
from datetime import datetime

print("Starting MapReduce job setup...")

# Define paths
script_dir = os.path.dirname(os.path.abspath(__file__))
mapper_script_host_path = os.path.join(script_dir, "extract_mapper.py")
reducer_script_host_path = os.path.join(script_dir, "extract_reducer.py")

container_script_dir = "/tmp/mapreduce_scripts"
container_mapper_path = f"{container_script_dir}/extract_mapper.py"
container_reducer_path = f"{container_script_dir}/extract_reducer.py"

# Ensure local output directory exists
local_output_dir = os.path.join(script_dir, "output")
os.makedirs(local_output_dir, exist_ok=True)
local_output_file = os.path.join(local_output_dir, "traffic_extracteds.csv")

# Bash script to be run inside the namenode container
mapreduce_bash_script_content = f"""#!/bin/bash
# Create directories for scripts and output
mkdir -p {container_script_dir}
mkdir -p /tmp/mapreduce_output


# Mapper and Reducer scripts are copied by the Python script before this bash script runs.

# Make scripts executable
chmod +x {container_mapper_path}
chmod +x {container_reducer_path}

# Remove previous HDFS output directory if it exists
echo "Attempting to remove previous HDFS output directory /data_lake/processed/traffic_extracteds_output..."
hdfs dfs -rm -r /data_lake/processed/traffic_extracteds_output || echo "Previous HDFS output directory not found or could not be removed."

# Run MapReduce job
echo "Running MapReduce job to extract data..."
hadoop jar /opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar \
  -files {container_mapper_path},{container_reducer_path} \
  -mapper "python3 {container_mapper_path}" \
  -reducer "python3 {container_reducer_path}" \
  -input /data_lake/processed/traffic_data_lines \
  -output /data_lake/processed/traffic_extracteds_output

# Copy results to a local file in the container
echo "Copying MapReduce results from HDFS to container path /tmp/mapreduce_output/traffic_extracteds.csv..."
rm -f /tmp/mapreduce_output/traffic_extracteds.csv # Remove if exists
hdfs dfs -copyToLocal /data_lake/processed/traffic_extracteds_output/part-* /tmp/mapreduce_output/traffic_extracteds.csv
if [ $? -eq 0 ]; then
    echo "Results successfully copied to /tmp/mapreduce_output/traffic_extracteds.csv in the container."
else
    echo "Failed to copy results from HDFS to container."
    echo "Listing HDFS output directory /data_lake/processed/traffic_extracteds_output:"
    hdfs dfs -ls /data_lake/processed/traffic_extracteds_output
fi
"""

def run_docker_command(command, input_data=None):
    """Helper function to run a command in Docker and print output."""
    print(f"Executing Docker command: {command}")
    try:
        process = subprocess.run(command, shell=True, input=input_data, capture_output=True, text=True, check=False)
        if process.stdout:
            print(f"STDOUT:\n{process.stdout}")
        if process.stderr:
            print(f"STDERR:\n{process.stderr}")
        if process.returncode != 0:
            print(f"Command failed with exit code {process.returncode}")
        return process.returncode == 0
    except Exception as e:
        print(f"Exception during Docker command execution: {e}")
        return False

# Step 1: Create script directory in container
print(f"Creating script directory {container_script_dir} in namenode container...")
if not run_docker_command(f"docker exec namenode_con mkdir -p {container_script_dir}"):
    print(f"Failed to create directory {container_script_dir} in container. Exiting.")
    exit(1)

# Step 2: Copy mapper and reducer scripts to container
print(f"Copying mapper script from {mapper_script_host_path} to namenode_con:{container_mapper_path}...")
if not os.path.exists(mapper_script_host_path):
    print(f"Mapper script not found at {mapper_script_host_path}. Exiting.")
    exit(1)
if not run_docker_command(f"docker cp \"{mapper_script_host_path}\" namenode_con:{container_mapper_path}"):
    print(f"Failed to copy mapper script. Exiting.")
    exit(1)

print(f"Copying reducer script from {reducer_script_host_path} to namenode_con:{container_reducer_path}...")
if not os.path.exists(reducer_script_host_path):
    print(f"Reducer script not found at {reducer_script_host_path}. Exiting.")
    exit(1)
if not run_docker_command(f"docker cp \"{reducer_script_host_path}\" namenode_con:{container_reducer_path}"):
    print(f"Failed to copy reducer script. Exiting.")
    exit(1)

# Step 3: Write the bash script to the container
bash_script_in_container_path = "/tmp/run_extract_mapreduce.sh"
print(f"Writing MapReduce bash script to namenode_con:{bash_script_in_container_path}...")
if not run_docker_command(f'docker exec -i namenode_con bash -c "cat > {bash_script_in_container_path}"',
                          input_data=mapreduce_bash_script_content):
    print(f"Failed to write bash script to container. Exiting.")
    exit(1)

# Step 4: Make the bash script executable and run it
print(f"Making bash script {bash_script_in_container_path} executable in container...")
if not run_docker_command(f"docker exec namenode_con chmod +x {bash_script_in_container_path}"):
    print(f"Failed to make bash script executable. Exiting.")
    exit(1)

print(f"Running MapReduce job via {bash_script_in_container_path} in container...")
if not run_docker_command(f"docker exec namenode_con {bash_script_in_container_path}"):
    print(f"MapReduce job execution failed. Check logs in container.")
    # No exit here, proceed to attempt copying results if any partial output exists.

# Step 5: Copy results from container to host
container_output_file = "/tmp/mapreduce_output/traffic_extracteds.csv"
print(f"Attempting to copy results from namenode_con:{container_output_file} to {local_output_file}...")
if run_docker_command(f"docker cp namenode_con:{container_output_file} \"{local_output_file}\""):
    print(f"Successfully copied results to {local_output_file}")
else:
    print(f"Failed to copy results from container. Check if {container_output_file} was created.")
    print(f"Listing contents of /tmp/mapreduce_output/ in container:")
    run_docker_command(f"docker exec namenode_con ls -l /tmp/mapreduce_output/")

print(f"\nProcess complete!")
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f"Current Date and Time: {current_time}")
print("MapReduce job finished. Output (if successful) is in:", local_output_file)