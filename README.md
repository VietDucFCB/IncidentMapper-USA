# IncidentMapper-USA

## Traffic Incident Analysis System Across All US States

![Project Architecture](https://github.com/VietDucFCB/PythonForDS/blob/master/diagram.png)

## Project Overview

IncidentMapper-USA is a comprehensive data engineering and analysis project that processes traffic incident data across all US states. The system collects real-time incident data from APIs, processes it through a distributed computing infrastructure, and presents analytical insights through interactive dashboards.

## Technical Architecture

- **Data Collection:** API integration for real-time traffic incident data
- **Data Storage:** Hadoop Distributed File System (HDFS) with 2 DataNodes
- **Data Processing:** MapReduce for large-scale data cleaning and transformation
- **Database:** PostgreSQL for structured data storage
- **Visualization:** Apache Superset for dashboards and heatmap visualizations
- **Deployment:** Containerized with Docker for scalability and portability

![Data Pipeline](https://github.com/VietDucFCB/PythonForDS/blob/master/pipeline.png)

## Project Structure

```
IncidentMapper-USA/
├── hadoop-docker-cluster/
│   ├── config/
│   │   ├── core-site.xml
│   │   └── hdfs-site.xml
│   ├── create-configs.sh
│   ├── docker-compose.xml
│   ├── create-configs.sh
│   └── Dockerfile
├── scripts/
│   ├── data_stored/
│   │   ├── load_traffic_data_to_hdfs.py
│   │   ├── hdfs_upload.log
│   ├── get_data/
│   ├── GeoMapUSA/
│   └── MapReduce/
│       ├── preprocess_json.py
│       ├── map_reduce.py
├── supersetdocker/
│   ├── superset-home/
│   ├── docker/
│   └── docker-compose-superset.xml
└── README.md
```

## Dataset Description

The project works with traffic incident data from a specialized API that provides comprehensive incident information across the United States. The API returns data in GeoJSON format with the following structure:

### Data Structure

#### Root Object
| Field | Description |
|-------|-------------|
| incidents | Object containing incidents that belong to or intersect with the given bounding box |

#### Incident Object
| Field | Description |
|-------|-------------|
| type | GeoJSON feature object (value is set as "Feature") |
| geometry | A GeoJSON feature of type Point or Linestring containing type and coordinates |
| properties | Detailed properties of a particular incident |

#### Incident Properties
| Field | Description |
|-------|-------------|
| id | Unique identifier of the traffic incident |
| iconCategory | Integer representing the main incident category (0: Unknown, 1: Accident, 2: Fog, 3: Dangerous Conditions, 4: Rain, 5: Ice, 6: Jam, 7: Lane Closed, 8: Road Closed, 9: Road Works, 10: Wind, 11: Flooding, 14: Broken Down Vehicle) |
| magnitudeOfDelay | Severity level (0: Unknown, 1: Minor, 2: Moderate, 3: Major, 4: Undefined) |
| events | List of event objects describing the details of the incident |
| startTime | Start time of the incident in ISO8601 format |
| endTime | End time of the incident in ISO8601 format |
| from | Name of the location where the traffic due to the incident starts |
| to | Name of the location where the traffic due to the incident ends |
| length | Length of the incident in meters |
| delay | Delay in seconds caused by the incident (compared to free-flow traffic) |
| roadNumbers | Array of strings representing affected road numbers |
| timeValidity | String describing if the incident occurrence is now or in the future |
| tmc | Traffic Message Channel data needed to determine incident location |
| probabilityOfOccurrence | Likelihood of occurrence (certain, probable, risk_of, improbable) |
| numberOfReports | Number of reports submitted by end-users |
| lastReportTime | Timestamp of the most recent incident report in ISO8601 format |
| aci | Community attributes object |

#### Event Object
| Field | Description |
|-------|-------------|
| description | Description of the event in the requested language |
| code | Predefined alert code describing the event |
| iconCategory | Icon category associated with the event |

#### ACI (Community Attributes) Object
| Field | Description |
|-------|-------------|
| probabilityOfOccurrence | Likelihood of occurrence (certain, probable, risk_of, improbable) |
| numberOfReports | Number of reports submitted by end-users |
| lastReportTime | Timestamp of the most recent incident report in ISO8601 format |

### Data Processing Workflow

1. **Data Extraction:** The raw JSON data is extracted from the API with geographic bounding boxes covering all US states.
2. **Data Storage:** Raw data is stored in its original JSON format on HDFS.
3. **Data Transformation:** MapReduce jobs parse the JSON structure and transform it into a normalized format.
4. **Data Enrichment:** Additional geographic and time-based information is added during processing.
5. **Data Loading:** Processed data is loaded into PostgreSQL with optimized schema design.

### Data Volume

The system processes hundreds of thousands of traffic incidents daily across all US states, with peak volumes during rush hours and adverse weather conditions.
## Project Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- PostgreSQL client
- Apache Hadoop ecosystem knowledge

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/VietDucFCB/IncidentMapper-USA.git
   cd IncidentMapper-USA
   ```

2. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

3. Initialize the HDFS cluster:
   ```bash
   ./scripts/init-hdfs.sh
   ```

4. Run the data collection job:
   ```bash
   python src/data_collection.py
   ```

5. Process data with MapReduce:
   ```bash
   ./scripts/run-mapreduce.sh
   ```

6. Load data into PostgreSQL:
   ```bash
   python src/load_to_postgres.py
   ```

7. Access the Superset dashboard:
   ```
   http://localhost:8088
   ```

