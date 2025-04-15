#!/usr/bin/env python3

import subprocess
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("hdfs_upload.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# Configuration
CONFIG = {
    'source_dir': r'C:\Users\kkagi\Downloads\CarIncidents\scripts\get_data\us_traffic_data_20250401_211449',
    'hdfs_target_path': '/data_lake/raw/traffic_data/us',
    'user': 'VietDucFCB',
    'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}


def run_command(cmd):
    """Run a shell command and log output"""
    logger.info(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Command succeeded")
            return True, result.stdout
        else:
            logger.error(f"Command failed with exit code {result.returncode}")
            logger.error(f"Error: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        return False, str(e)


def check_hdfs_health():
    """Check if HDFS cluster is healthy with active datanodes"""
    success, output = run_command("docker exec namenode hdfs dfsadmin -report")
    if success and "Live datanodes" in output:
        if "Live datanodes (0)" in output:
            logger.error("No live datanodes found! HDFS cluster is not healthy.")
            return False
        else:
            live_count = output.count("Decommission Status : Normal")
            logger.info(f"Found {live_count} live datanodes")
            return True
    else:
        logger.error("Failed to get HDFS cluster report")
        return False


def main():
    logger.info(f"Starting data upload for user {CONFIG['user']} at {CONFIG['current_time']}")

    # Step 1: Check HDFS health
    if not check_hdfs_health():
        return False

    # Step 2: Create target directory in HDFS
    run_command(f"docker exec namenode hdfs dfs -mkdir -p {CONFIG['hdfs_target_path']}")

    # Step 3: Create temporary directory in namenode container
    temp_dir = f"/tmp/traffic_data_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    run_command(f"docker exec namenode mkdir -p {temp_dir}")

    # Step 4: Copy files from Windows to Docker container
    source_path = CONFIG['source_dir'].replace('\\', '/')
    logger.info(f"Copying JSON files from {source_path} to Docker container")
    run_command(f'docker cp "{source_path}/." namenode:{temp_dir}/')

    # Step 5: List files in temporary directory without using grep
    success, file_list = run_command(f"docker exec namenode ls -1 {temp_dir}")

    if not success or not file_list.strip():
        logger.error("No files found in temporary directory")
        run_command(f"docker exec namenode rm -rf {temp_dir}")
        return False

    # Filter JSON files in Python
    files = [f for f in file_list.strip().split('\n') if f.endswith('.json')]

    if not files:
        logger.error("No JSON files found in temporary directory")
        run_command(f"docker exec namenode rm -rf {temp_dir}")
        return False

    logger.info(f"Found {len(files)} JSON files to upload")

    # Step 6: Upload files one by one
    uploaded = 0
    for file_name in files:
        file_name = file_name.strip()
        if not file_name:
            continue

        logger.info(f"Uploading {file_name}...")

        # Upload file to HDFS - make sure to specify the full path
        full_path = f"{temp_dir}/{file_name}"
        target_path = f"{CONFIG['hdfs_target_path']}/{file_name}"

        success, _ = run_command(f'docker exec namenode hdfs dfs -put -f "{full_path}" "{target_path}"')

        if success:
            uploaded += 1
            logger.info(f"Successfully uploaded {file_name} ({uploaded}/{len(files)})")
        else:
            logger.error(f"Failed to upload {file_name}")

    # Step 7: Verify files in HDFS
    logger.info("Verifying files in HDFS...")
    success, hdfs_listing = run_command(f"docker exec namenode hdfs dfs -ls {CONFIG['hdfs_target_path']}")

    if success:
        hdfs_files = hdfs_listing.count(".json")
        logger.info(f"Found {hdfs_files} JSON files in HDFS target path")

    # Step 8: Clean up temporary directory
    logger.info("Cleaning up temporary directory...")
    run_command(f"docker exec namenode rm -rf {temp_dir}")

    logger.info(f"Upload process completed. {uploaded}/{len(files)} files uploaded.")
    return uploaded > 0


if __name__ == "__main__":
    success = main()
    if success:
        print("\nJSON files successfully uploaded to HDFS!")
        print(f"Files are available at: {CONFIG['hdfs_target_path']}")

        # Print a summary of available commands to interact with the files
        print("\nUseful commands to interact with your data:")
        print("----------------------------------------------")
        print(f"• List files: docker exec namenode hdfs dfs -ls {CONFIG['hdfs_target_path']}")
        print(f"• View file content: docker exec namenode hdfs dfs -cat {CONFIG['hdfs_target_path']}/[filename]")
        print(f"• Get file info: docker exec namenode hdfs dfs -stat {CONFIG['hdfs_target_path']}/[filename]")
        print(f"• Check file size: docker exec namenode hdfs dfs -du -h {CONFIG['hdfs_target_path']}")
    else:
        print("\nFailed to upload JSON files to HDFS. Check logs for details.")