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

## Features

- Real-time traffic incident data capture across all US states
- Distributed storage system with redundancy
- Parallel data processing capabilities
- Interactive dashboards showing incident trends
- Geographic heatmaps visualizing incident concentration
- High availability through containerized architecture

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

## Project Structure

```
IncidentMapper-USA/
├── docker/
│   ├── hadoop/
│   │   ├── datanode/
│   │   └── namenode/
│   ├── postgres/
│   └── superset/
├── scripts/
│   ├── init-hdfs.sh
│   └── run-mapreduce.sh
├── src/
│   ├── data_collection.py
│   ├── mapreduce/
│   │   ├── mapper.py
│   │   └── reducer.py
│   ├── data_processing.py
│   └── load_to_postgres.py
├── notebooks/
│   └── analysis.ipynb
├── docker-compose.yml
└── README.md
```

## Future Enhancements

- Integration with machine learning models for incident prediction
- Real-time alerting system for severe incidents
- Extension to support international traffic data
- Mobile application for on-the-go insights

## License

This project is licensed under the MIT License - see the LICENSE file for details.
