# IncidentMapper-USA

## Real-time Traffic Incident Analysis System for the Entire USA

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![Project Architecture Diagram](https://github.com/VietDucFCB/PythonForDS/blob/master/diagram.png) 
*Note: You might need to update this link if the diagram is hosted elsewhere or if the path changes.*

## Project Overview

IncidentMapper-USA is a robust data engineering project designed to collect, process, store, and visualize real-time traffic incident data from all 50 U.S. states. The system leverages a distributed architecture to handle large volumes of data, providing analytical insights through interactive dashboards. This project demonstrates a full data pipeline, from raw data ingestion to end-user visualization.

## Features

- **Real-time Data Ingestion:** Fetches live traffic incident data using a dedicated API.
- **Distributed Data Storage:** Utilizes Hadoop Distributed File System (HDFS) for scalable and resilient storage of raw and processed data.
- **Large-Scale Data Processing:** Employs Apache Hadoop MapReduce for efficient parallel processing and transformation of incident data.
- **Structured Data Warehousing:** Uses PostgreSQL as a relational database for storing cleaned and aggregated data ready for analysis.
- **Interactive Visualization:** Integrates Apache Superset to create dynamic dashboards, heatmaps, and reports for insightful data exploration.
- **Containerized Deployment:** All components (Hadoop, Superset, PostgreSQL) are containerized using Docker and Docker Compose for easy setup, portability, and scalability.
- **Automated Workflows:** Scripts are provided for automating data loading, processing, and system initialization.

## Technical Architecture

The system is composed of several key components working in concert:

- **Data Collection:** Python scripts (`scripts/get_data/getData.py`) interact with external APIs to retrieve traffic incident data for each US state. The raw data is typically in JSON format.
- **Data Staging (HDFS):**
    - Raw JSON files are initially loaded into HDFS into a designated 'raw' layer (e.g., `/data_lake/raw/traffic_data/us`) using a Python script (`scripts/data_stored/load_traffic_data_to_hdfs.py`).
    - The Hadoop cluster (namenode, datanodes) is managed via Docker (`hadoop-docker-cluster/docker-compose.yml`).
- **Data Processing (MapReduce):**
    - MapReduce jobs, written in Python (`scripts/MapReduce/`), are executed on the Hadoop cluster to:
        - Parse and validate JSON data (`scripts/MapReduce/preprocess_json.py`).
        - Transform and aggregate data, for example, to prepare it for heatmap generation (`scripts/MapReduce/map_reduce_heatmap.py` using `extract_mapper.py` and `extract_reducer.py`).
    - Processed data is stored in a 'processed' layer in HDFS (e.g., `/data_lake/processed/traffic_extracteds_output`).
- **Data Serving (PostgreSQL):**
    - The transformed data from HDFS is then loaded into a PostgreSQL database. (Note: The script for this step, `load_to_postgres.py`, was mentioned but not present in the provided structure; this would be a typical next step).
    - PostgreSQL serves as the analytical database for Apache Superset.
- **Visualization (Apache Superset):**
    - Apache Superset, running in Docker (`superset-docker/docker-compose-superset.yml`), connects to the PostgreSQL database.
    - Users can create and view dashboards, charts, and heatmaps to analyze traffic incident patterns, severity, and trends.
- **Orchestration & Management:**
    - Docker Compose is used to manage the lifecycle of all services.
    - Shell scripts and Python scripts are used for various setup and operational tasks.

![Data Pipeline Diagram](https://github.com/VietDucFCB/PythonForDS/blob/master/pipeline.png)
*Note: You might need to update this link if the diagram is hosted elsewhere or if the path changes.*

## Project Structure

```
IncidentMapper-USA/
├── README.md
├── hadoop-docker-cluster/    
│   ├── config/
│   │   ├── core-site.xml
│   │   └── hdfs-site.xml
│   ├── create-configs.sh     
│   ├── docker-compose.yml    
│   ├── Dockerfile            
│   └── entrypoint.sh         
├── scripts/                   
│   ├── data_stored/
│   │   ├── load_traffic_data_to_hdfs.py 
│   │   └── hdfs_upload.log              
│   ├── GeoMapUSA/                       
│   │   ├── condenseGeoJSON.py
│   │   └── state_lookup.csv
│   ├── get_data/
│   │   ├── getData.py                   
│   │   └── us_traffic_data_20250401_211449/ 
│   │       └── ... 
│   └── MapReduce/
│       ├── extract_mapper.py           
│       ├── extract_reducer.py           
│       ├── map_reduce.py        
│       └── preprocess_json.py           
├── superset-docker/            
│   ├── docker-compose-superset.yml 
│   ├── docker/
│   │   ├── init/
│   │   │   └── superset-init.sh       
│   │   ├── .env-postgresql          
│   │   └── .env-superset           
│   └── superset_home/               
│       └── superset.db                
└── .gitignore 
```

## Dataset Description

The project utilizes traffic incident data obtained from an API providing real-time information across the United States. The data is typically in GeoJSON format.

### Key Data Fields (Illustrative based on common incident APIs):

- **`id`**: Unique identifier for the incident.
- **`geometry`**: GeoJSON object (Point or LineString) indicating the location of the incident.
    - **`coordinates`**: Latitude and longitude.
- **`properties`**: A collection of attributes describing the incident:
    - **`type` / `iconCategory`**: Type or category of the incident (e.g., accident, congestion, road work).
    - **`description`**: Textual description of the incident.
    - **`startTime` / `endTime`**: Timestamp for the start and end of the incident.
    - **`severity` / `magnitudeOfDelay`**: Impact level of the incident.
    - **`state`**: The US state where the incident occurred.
    - **`delay`**: Estimated delay in seconds.
    - **`roadNumbers`**: Affected road(s).
    - *(Other fields as provided by the specific API)*

### Data Processing Workflow

1.  **Data Ingestion:** `scripts/get_data/getData.py` fetches data for all US states and saves them as individual JSON files (e.g., `Alabama_traffic.json`).
2.  **HDFS Loading:** `scripts/data_stored/load_traffic_data_to_hdfs.py` uploads these JSON files to the HDFS raw data directory (`/data_lake/raw/traffic_data/us`).
3.  **Preprocessing (Optional but Recommended):** `scripts/MapReduce/preprocess_json.py` can be used to clean, validate, or slightly restructure JSON files on HDFS to ensure they are suitable for MapReduce processing. This often involves converting multi-line JSONs to single-line-per-record format if needed by Hadoop Streaming.
4.  **MapReduce Transformation:** `scripts/MapReduce/map_reduce_heatmap.py` orchestrates a MapReduce job.
    - `extract_mapper.py`: Reads data from HDFS, parses JSON, extracts relevant fields (like coordinates, incident type, severity, date/time components, state).
    - `extract_reducer.py`: Aggregates or simply formats the mapped output, typically into a CSV or structured text format. The output is saved to a new HDFS directory (e.g., `/data_lake/processed/traffic_extracteds_output`).
5.  **Data Loading to PostgreSQL:** (Conceptual - script `load_to_postgres.py` would be needed) The processed data from HDFS is then loaded into structured tables in a PostgreSQL database.
6.  **Dashboarding:** Apache Superset connects to PostgreSQL to visualize the data. Users can build dashboards to show incident heatmaps, trends over time, incidents by state, severity analysis, etc.

## Setup and Installation

### Prerequisites

- Docker Engine
- Docker Compose
- Python 3.8+ (for running local scripts)
- Git (for cloning the repository)
- A stable internet connection (for pulling Docker images and fetching data)

### Installation Steps

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/VietDucFCB/IncidentMapper-USA.git
    cd IncidentMapper-USA
    ```

2.  **Configure Environment Variables (if necessary):**
    - Review and update any `.env` files if they exist (e.g., for database passwords or API keys, though not explicitly shown in the structure for Superset, it's good practice).
    - Update paths in configuration scripts if your local setup differs significantly.

3.  **Build and Start Hadoop Cluster:**
    ```bash
    cd hadoop-docker-cluster
    # Ensure create-configs.sh has execute permissions and run it if needed by your setup
    # sh create-configs.sh 
    docker-compose up -d
    cd ..
    ```
    *Wait for the Hadoop cluster (namenode, datanodes) to be fully up and running. You can check logs using `docker-compose logs -f` within the `hadoop-docker-cluster` directory.*

4.  **Build and Start Apache Superset & Dependencies:**
    ```bash
    cd superset-docker
    docker-compose -f docker-compose-superset.yml up -d
    cd ..
    ```
    *Wait for Superset, Redis, and PostgreSQL (for Superset's metadata) to initialize. The `superset-init` service will handle initial Superset setup like creating an admin user and initializing the database.*

5.  **Prepare HDFS Directories (Run once):**
    You might need to manually create the initial HDFS directories if the loading script doesn't do it, or add it to an initialization script.
    ```bash
    # Example: Connect to namenode and create directories
    docker exec -it namenode bash
    hdfs dfs -mkdir -p /data_lake/raw/traffic_data/us
    hdfs dfs -mkdir -p /data_lake/processed
    exit 
    ```
    *(Alternatively, incorporate these into `load_traffic_data_to_hdfs.py` or a dedicated setup script).*

6.  **Run Data Ingestion Script:**
    *(Ensure you have any necessary API keys or configurations set up for `getData.py`)*
    ```bash
    python scripts/get_data/getData.py
    ```
    This will populate the local data directory (e.g., `scripts/get_data/us_traffic_data_.../`).

7.  **Load Raw Data to HDFS:**
    ```bash
    python scripts/data_stored/load_traffic_data_to_hdfs.py
    ```
    Check `hdfs_upload.log` for status.

8.  **Run Preprocessing and MapReduce Jobs:**
    First, preprocess the JSON data (if your MapReduce jobs expect a specific format like one JSON object per line):
    ```bash
    python scripts/MapReduce/preprocess_json.py
    ```
    Then, run the main MapReduce job for heatmap data (or other analyses):
    ```bash
    python scripts/MapReduce/map_reduce_heatmap.py
    ```
    This script will copy the mapper/reducer to the container, execute the Hadoop Streaming job, and copy results back to `scripts/MapReduce/output/`.

9.  **Load Processed Data into PostgreSQL (Conceptual):**
    *(This step requires a `load_to_postgres.py` script that you would need to create. This script would typically read the CSV output from HDFS (or the local copy) and insert it into PostgreSQL tables.)*
    ```bash
    # python scripts/load_to_postgres.py 
    ```

10. **Access Apache Superset:**
    Open your web browser and navigate to:
    ```
    http://localhost:8088
    ```
    Log in with the default credentials (usually `admin`/`admin` or as configured in `superset-init.sh` or Superset's environment variables).
    - **Connect to Data Source:** In Superset, add your PostgreSQL database (the one where you loaded the traffic data) as a data source.
    - **Create Datasets:** Define datasets in Superset based on your PostgreSQL tables.
    - **Build Charts and Dashboards:** Start creating visualizations.

## Usage

- **Data Refresh:** Schedule `getData.py`, `load_traffic_data_to_hdfs.py`, MapReduce scripts, and the PostgreSQL loading script to run periodically to keep the data updated.
- **Superset Exploration:** Use Superset to explore incident data, identify hotspots, analyze trends by time of day or day of week, and compare incident rates across states.

## Future Enhancements / To-Do

- Implement a robust `load_to_postgres.py` script.
- Develop more sophisticated MapReduce jobs for advanced analytics (e.g., incident correlation, predictive analysis).
- Enhance error handling and logging across all scripts.
- Add unit and integration tests.
- Secure API keys and credentials using a secrets management system (e.g., Docker secrets, HashiCorp Vault).
- Create a more detailed `create-configs.sh` or provide clearer instructions for Hadoop configuration.
- Add data quality checks at various stages of the pipeline.
- Implement data archival and retention policies for HDFS data.

## Contributing

Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m \'Add some AmazingFeature\'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the `LICENSE` file for details (you would need to create a LICENSE file, e.g., with MIT license text).

## Acknowledgements

- Apache Hadoop Community
- Apache Superset Community
- PostgreSQL Community
- Docker Community
- Any APIs or data sources used.

---

*This README was last updated on: May 14, 2025.*

