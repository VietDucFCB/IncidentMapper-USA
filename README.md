# IncidentMapper-USA

## Hệ thống Phân tích Sự cố Giao thông

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![Sơ đồ Kiến trúc Dự án](https://github.com/VietDucFCB/PythonForDS/blob/master/diagram.png)

## Tổng quan Dự án

IncidentMapper-USA là một dự án được thiết kế để thu thập, xử lý, lưu trữ và trực quan hóa data sự cố giao thông thời gian thực từ tất cả 50 tiểu bang của Hoa Kỳ. Hệ thống tận dụng kiến trúc phân tán để xử lý khối lượng lớn data, cung cấp thông tin phân tích thông qua các bảng điều khiển tương tác. 

## **Features**

- **Data Ingestion:** Tìm data sự cố giao thông trực tiếp bằng API chuyên dụng.
- **Distributed Data Storage:** Sử dụng Hệ thống tệp phân tán Hadoop (HDFS) để lưu trữ data thô.
- **Large-Scale Data Processing:** Sử dụng Apache Hadoop MapReduce để xử lý song song và chuyển đổi data sự cố một cách hiệu quả.
- **Structured Data Warehousing:** Sử dụng PostgreSQL làm cơ sở data quan hệ để lưu trữ data đã được làm sạch và tổng hợp, sẵn sàng cho việc phân tích.
- **Interactive Visualization:** Tích hợp Apache Superset để tạo các bảng điều khiển động, bản đồ nhiệt và báo cáo để khám phá data một cách sâu sắc.
- **Containerized Deployment:** Tất cả các thành phần (Hadoop, Superset, PostgreSQL) được đóng gói bằng Docker và Docker Compose để dễ dàng thiết lập, di chuyển và mở rộng.
- **Automated Workflows:** Cung cấp các tập lệnh để tự động hóa việc tải data, xử lý và khởi tạo hệ thống.

## **Technical Architecture**

Hệ thống bao gồm một số thành phần chính hoạt động phối hợp với nhau:

- **Data Collection:** Các tập lệnh Python (`scripts/get_data/getData.py`) tương tác với các API bên ngoài để truy xuất data sự cố giao thông cho mỗi tiểu bang của Hoa Kỳ. data thô ở định dạng JSON.
- **Data Staging (HDFS):**
    - Các tệp JSON thô ban đầu được tải vào HDFS vào một lớp 'thô' được chỉ định (ví dụ: `/data_lake/raw/traffic_data/us`) bằng tập lệnh Python (`scripts/data_stored/load_traffic_data_to_hdfs.py`).
    - Cụm Hadoop (namenode, datanodes) được quản lý thông qua Docker (`hadoop-docker-cluster/docker-compose.yml`).
- **Data Processing (MapReduce):**
    - Các công việc MapReduce, được viết bằng Python (`scripts/MapReduce/`), được thực thi trên cụm Hadoop để:
        - Phân tích cú pháp và xác thực data JSON (`scripts/MapReduce/preprocess_json.py`).
        - Chuyển đổi và tổng hợp data, ví dụ, để chuẩn bị cho việc tạo bản đồ nhiệt (`scripts/MapReduce/map_reduce_heatmap.py` sử dụng `extract_mapper.py` và `extract_reducer.py`).
    - Data đã xử lý được lưu trữ trong một lớp 'đã xử lý' trong HDFS (`/data_lake/processed/traffic_extracteds_output`).
- **Data Serving (PostgreSQL):**
    - data đã chuyển đổi từ HDFS sau đó được tải vào cơ sở data PostgreSQL..
    - PostgreSQL đóng vai trò là cơ sở data phân tích cho Apache Superset.
- **Visualization (Apache Superset):**
    - Apache Superset, chạy trong Docker (`superset-docker/docker-compose-superset.yml`), kết nối với cơ sở data PostgreSQL.
    - Người dùng có thể tạo và xem các bảng điều khiển, biểu đồ và bản đồ nhiệt để phân tích các mẫu sự cố giao thông, mức độ nghiêm trọng và xu hướng.
- **Orchestration & Management:**
    - Docker Compose được sử dụng để quản lý vòng đời của tất cả các dịch vụ.
    - Các tập lệnh shell và Python được sử dụng cho các tác vụ thiết lập và vận hành khác nhau.

![Sơ đồ Quy trình Data](https://github.com/VietDucFCB/PythonForDS/blob/master/pipeline.png)

## **Project Structure**

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

## **Dataset Description**

Dự án sử dụng data sự cố giao thông thu được từ một API cung cấp thông tin thời gian thực trên khắp Hoa Kỳ. data thường ở định dạng GeoJSON.

### **Key Data Fields (Illustrative based on common incident APIs):**

- **`id`**: Mã định danh duy nhất cho sự cố.
- **`geometry`**: Đối tượng GeoJSON (Point hoặc LineString) cho biết vị trí của sự cố.
    - **`coordinates`**: Kinh độ và vĩ độ.
- **`properties`**: Một tập hợp các thuộc tính mô tả sự cố:
    - **`type` / `iconCategory`**: Loại hoặc danh mục của sự cố (ví dụ: tai nạn, tắc nghẽn, công trình đường bộ).
    - **`description`**: Mô tả văn bản của sự cố.
    - **`startTime` / `endTime`**: Dấu thời gian cho thời điểm bắt đầu và kết thúc của sự cố.
    - **`severity` / `magnitudeOfDelay`**: Mức độ ảnh hưởng của sự cố.
    - **`state`**: Tiểu bang của Hoa Kỳ nơi sự cố xảy ra.
    - **`delay`**: Thời gian trễ ước tính tính bằng giây.
    - **`roadNumbers`**: (Các) con đường bị ảnh hưởng.
    - *(Các trường khác theo API cụ thể cung cấp)*

### **Data Processing Workflow**

1.  **Data Ingestion:** `scripts/get_data/getData.py` tìm nạp data cho tất cả các tiểu bang của Hoa Kỳ và lưu chúng dưới dạng các tệp JSON riêng lẻ (ví dụ: `Alabama_traffic.json`).
2.  **HDFS Loading:** `scripts/data_stored/load_traffic_data_to_hdfs.py` tải các tệp JSON này lên thư mục data thô HDFS (`/data_lake/raw/traffic_data/us`).
3.  **Preprocessing:** `scripts/MapReduce/preprocess_json.py` có thể được sử dụng để làm sạch, xác thực hoặc tái cấu trúc nhẹ các tệp JSON trên HDFS để đảm bảo chúng phù hợp cho quá trình xử lý MapReduce. Điều này thường bao gồm việc chuyển đổi JSON nhiều dòng thành định dạng một dòng cho mỗi bản ghi nếu Hadoop Streaming yêu cầu.
4.  **MapReduce Transformation:** `scripts/MapReduce/map_reduce_heatmap.py` điều phối một công việc MapReduce.
    - `extract_mapper.py`: Đọc data từ HDFS, phân tích cú pháp JSON, trích xuất các trường liên quan (như tọa độ, loại sự cố, mức độ nghiêm trọng, thành phần ngày/giờ, tiểu bang).
    - `extract_reducer.py`: Tổng hợp hoặc đơn giản là định dạng đầu ra đã ánh xạ, thường thành định dạng CSV hoặc văn bản có cấu trúc. Đầu ra được lưu vào một thư mục HDFS mới (ví dụ: `/data_lake/processed/traffic_extracteds_output`).
5.  **Data Loading to PostgreSQL:** (Khái niệm - cần có tập lệnh `load_to_postgres.py`) data đã xử lý từ HDFS sau đó được tải vào các bảng có cấu trúc trong cơ sở data PostgreSQL.
6.  **Dashboarding:** Apache Superset kết nối với PostgreSQL để trực quan hóa data. Người dùng có thể xây dựng các bảng điều khiển để hiển thị bản đồ nhiệt sự cố, xu hướng theo thời gian, sự cố theo tiểu bang, phân tích mức độ nghiêm trọng, v.v.

## **Setup and Installation**

### **Installation Steps**

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/VietDucFCB/IncidentMapper-USA.git
    cd IncidentMapper-USA
    ```

2.  **Configure Environment Variables:**
    - Xem xét và cập nhật bất kỳ tệp `.env` nào nếu chúng tồn tại 
    - Cập nhật đường dẫn trong các tập lệnh cấu hình nếu thiết lập cục bộ của bạn khác biệt đáng kể.

3.  **Build and Start Hadoop Cluster:**
    ```bash
    cd hadoop-docker-cluster
    # Ensure create-configs.sh has execute permissions and run it if needed by your setup
    # sh create-configs.sh
    docker-compose up -d
    cd ..
    ```
    *Đợi cụm Hadoop (namenode, datanodes) khởi động và chạy hoàn toàn. Bạn có thể kiểm tra nhật ký bằng cách sử dụng `docker-compose logs -f` trong thư mục `hadoop-docker-cluster`.*

4.  **Build and Start Apache Superset & Dependencies:**
    ```bash
    cd superset-docker
    docker-compose -f docker-compose-superset.yml up -d
    cd ..
    ```
    *Đợi Superset, Redis và PostgreSQL (cho siêu data của Superset) khởi tạo. Dịch vụ `superset-init` sẽ xử lý thiết lập Superset ban đầu như tạo người dùng quản trị và khởi tạo cơ sở data.*

5.  **Prepare HDFS Directories (Run once):**
    Bạn có thể cần tạo thủ công các thư mục HDFS ban đầu nếu tập lệnh tải không thực hiện việc đó, hoặc thêm nó vào một tập lệnh khởi tạo.
    ```bash
    # Example: Connect to namenode and create directories
    docker exec -it namenode bash
    hdfs dfs -mkdir -p /data_lake/raw/traffic_data/us
    hdfs dfs -mkdir -p /data_lake/processed
    exit
    ```

6.  **Run Data Ingestion Script:**
    *(Đảm bảo bạn đã thiết lập bất kỳ khóa API hoặc cấu hình cần thiết nào cho `getData.py`)*
    ```bash
    python scripts/get_data/getData.py
    ```
    Thao tác này sẽ điền vào thư mục **Data** cục bộ (ví dụ: `scripts/get_data/us_traffic_data_.../`).

7.  **Load Raw Data to HDFS:**
    ```bash
    python scripts/data_stored/load_traffic_data_to_hdfs.py
    ```
    Kiểm tra `hdfs_upload.log` để biết trạng thái.

8.  **Run Preprocessing and MapReduce Jobs:**
    Đầu tiên, tiền xử lý **Data** JSON (nếu các công việc MapReduce của bạn mong đợi một định dạng cụ thể như một đối tượng JSON trên mỗi dòng):
    ```bash
    python scripts/MapReduce/preprocess_json.py
    ```
    Sau đó, chạy công việc MapReduce
    ```bash
    python scripts/MapReduce/map_reduce.py
    ```
    Tập lệnh này sẽ sao chép mapper/reducer vào container, thực thi công việc Hadoop Streaming và sao chép kết quả trở lại `scripts/MapReduce/output/`.

9.  **Load Processed Data into PostgreSQL (Conceptual):**
    *(Bước này yêu cầu một tập lệnh `load_to_postgres.py` mà bạn sẽ cần tạo. Tập lệnh này thường sẽ đọc đầu ra CSV từ HDFS (hoặc bản sao cục bộ) và chèn nó vào các bảng PostgreSQL.)*
    ```bash
    # python scripts/load_to_postgres.py
    ```

10. **Access Apache Superset:**
    Mở trình duyệt web của bạn và điều hướng đến:
    ```
    http://localhost:8088
    ```
    Đăng nhập bằng thông tin đăng nhập mặc định (thường là `admin`/`admin` hoặc như được cấu hình trong `superset-init.sh` hoặc các biến môi trường của Superset).
    - **Connect to Data Source:** Trong Superset, thêm cơ sở data PostgreSQL của bạn (cơ sở data mà bạn đã tải data giao thông vào) làm nguồn data.
    - **Create Datasets:** Xác định các tập data trong Superset dựa trên các bảng PostgreSQL của bạn.
    - **Build Charts and Dashboards:** Bắt đầu tạo các trực quan hóa.

## **Usage**

- **Data Refresh:** Lên lịch chạy định kỳ `getData.py`, `load_traffic_data_to_hdfs.py`, các tập lệnh MapReduce và tập lệnh tải PostgreSQL để giữ cho data được cập nhật.
- **Superset Exploration:** Sử dụng Superset để khám phá data sự cố, xác định các điểm nóng, phân tích xu hướng theo thời gian trong ngày hoặc ngày trong tuần và so sánh tỷ lệ sự cố giữa các tiểu bang.

*README này được cập nhật lần cuối vào: 20 tháng 5 năm 2025.*
