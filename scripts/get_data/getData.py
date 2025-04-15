import requests
import json
import time
import os
import math
from datetime import datetime


def calculate_area(bbox_str):
    """
    Tính diện tích xấp xỉ của bounding box theo km²
    """
    parts = list(map(float, bbox_str.split(',')))
    min_lon, min_lat, max_lon, max_lat = parts

    # Xấp xỉ 111km trên mỗi độ vĩ độ và 111*cos(lat) km trên mỗi độ kinh độ
    width_km = abs(max_lon - min_lon) * 111 * math.cos(math.radians((min_lat + max_lat) / 2))
    height_km = abs(max_lat - min_lat) * 111

    return width_km * height_km


def get_incidents_by_bbox(api_key, bbox, fields=None, language="en-US", traffic_model_id="1111",
                          category_filter=None, time_validity_filter="present"):
    """
    Lấy thông tin giao thông dựa trên bounding box
    """
    base_url = "https://api.tomtom.com/traffic/services/5/incidentDetails"

    # Kiểm tra diện tích của bounding box
    area = calculate_area(bbox)
    if area > 10000:
        print(f"Warning: Bounding box area is {area:.2f} km², which exceeds the 10,000 km² limit")
        return None

    # Chuẩn bị tham số
    params = {
        "key": api_key,
        "bbox": bbox,
        "language": language,
        "t": traffic_model_id,
        "timeValidityFilter": time_validity_filter
    }

    if fields:
        params["fields"] = fields

    if category_filter:
        params["categoryFilter"] = category_filter

    # Thực hiện request
    try:
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None


# Hàm mới để chia bounding box theo phương pháp đệ quy
def adaptive_split_bbox(bbox_str, max_area=9000):
    """
    Chia bounding box thành các phần nhỏ hơn một cách đệ quy cho đến khi đạt được diện tích mong muốn
    """
    parts = list(map(float, bbox_str.split(',')))
    min_lon, min_lat, max_lon, max_lat = parts

    area = calculate_area(bbox_str)

    if area <= max_area:
        return [bbox_str]

    # Tính số cần chia dựa trên diện tích
    split_factor = math.ceil(math.sqrt(area / max_area))

    # Giới hạn tối đa split_factor để tránh quá nhiều phân chia
    split_factor = min(split_factor, 10)  # Tối đa 10x10 = 100 ô ở mỗi cấp

    results = []

    # Chia theo chiều dọc (latitude)
    lat_step = (max_lat - min_lat) / split_factor
    for i in range(split_factor):
        cell_min_lat = min_lat + i * lat_step
        cell_max_lat = min_lat + (i + 1) * lat_step

        # Chia theo chiều ngang (longitude)
        lon_step = (max_lon - min_lon) / split_factor
        for j in range(split_factor):
            cell_min_lon = min_lon + j * lon_step
            cell_max_lon = min_lon + (j + 1) * lon_step

            sub_bbox = f"{cell_min_lon:.6f},{cell_min_lat:.6f},{cell_max_lon:.6f},{cell_max_lat:.6f}"
            sub_area = calculate_area(sub_bbox)

            # Nếu sub-bbox vẫn còn quá lớn, tiếp tục phân chia đệ quy
            if sub_area > max_area:
                results.extend(adaptive_split_bbox(sub_bbox, max_area))
            else:
                results.append(sub_bbox)

    return results


# Hàm xử lý đặc biệt các bang cực lớn
def process_large_state(state_name, bbox, api_key, fields, max_area=5000):
    """
    Xử lý đặc biệt các bang rất lớn như Alaska bằng cách phân chia nhỏ hơn
    và thêm thời gian chờ giữa các yêu cầu
    """
    print(f"Special processing for large state: {state_name}...")
    sub_bboxes = adaptive_split_bbox(bbox, max_area)
    print(f"  State divided into {len(sub_bboxes)} adaptive sub-regions")

    state_incidents = []
    region_count = 0

    for region_bbox in sub_bboxes:
        region_count += 1
        print(f"  Processing region {region_count}/{len(sub_bboxes)} in {state_name}...")

        # Thêm thời gian chờ dài hơn cho các bang lớn
        if region_count > 1:
            time.sleep(1.5)

        area = calculate_area(region_bbox)
        if area > 10000:
            print(f"  Warning: Skipping sub-region with area {area:.2f} km² (exceeds API limit)")
            continue

        incidents_data = get_incidents_by_bbox(api_key, region_bbox, fields)

        if incidents_data and 'incidents' in incidents_data:
            num_incidents = len(incidents_data['incidents'])
            print(f"    Found {num_incidents} traffic incidents")

            # Thêm thông tin tiểu bang
            for incident in incidents_data['incidents']:
                if 'properties' not in incident:
                    incident['properties'] = {}
                incident['properties']['state'] = state_name

            state_incidents.extend(incidents_data['incidents'])
        else:
            print(f"    No incidents found or request failed")

    return state_incidents

def split_bbox(bbox_str, max_area=9000):
    """
    Chia bounding box thành các phần nhỏ hơn để không vượt quá giới hạn diện tích
    """
    parts = list(map(float, bbox_str.split(',')))
    min_lon, min_lat, max_lon, max_lat = parts

    area = calculate_area(bbox_str)

    if area <= max_area:
        return [bbox_str]

    # Quyết định số lượng grid cần tạo
    grid_size = math.ceil(math.sqrt(area / max_area))

    # Tăng grid_size cho những vùng cực lớn
    if area > 100000:  # Nếu diện tích lớn hơn 100,000 km²
        grid_size = max(grid_size, 10)  # Ít nhất 10x10 grid

    lat_step = (max_lat - min_lat) / grid_size
    lon_step = (max_lon - min_lon) / grid_size

    grid_cells = []

    for i in range(grid_size):
        for j in range(grid_size):
            cell_min_lat = min_lat + i * lat_step
            cell_max_lat = min_lat + (i + 1) * lat_step
            cell_min_lon = min_lon + j * lon_step
            cell_max_lon = min_lon + (j + 1) * lon_step

            bbox = f"{cell_min_lon:.6f},{cell_min_lat:.6f},{cell_max_lon:.6f},{cell_max_lat:.6f}"
            grid_cells.append(bbox)

    return grid_cells


def get_us_traffic_data(api_key,
                        fields="{incidents{type,geometry{type,coordinates},properties{id,iconCategory,magnitudeOfDelay,events{description,code,iconCategory},startTime,endTime,from,to,length,delay,roadNumbers,timeValidity}}}"):
    """
    Lấy dữ liệu giao thông cho tất cả các tiểu bang của Mỹ
    với xử lý đặc biệt cho các bang có diện tích lớn
    """
    # Định nghĩa bounding box cho tất cả các tiểu bang (giữ nguyên các giá trị trong code gốc)
    us_states = {
        "Alabama": "-88.49,30.17,-84.89,35.01",
        "Alaska": "-179.15,51.20,-129.98,71.44",
        "Arizona": "-114.82,31.33,-109.04,37.00",
        "Arkansas": "-94.62,33.00,-89.64,36.50",
        "California": "-124.41,32.53,-114.13,42.01",
        "Colorado": "-109.06,36.99,-102.04,41.00",
        "Connecticut": "-73.73,40.95,-71.78,42.05",
        "Delaware": "-75.79,38.45,-75.04,39.84",
        "Florida": "-87.63,24.52,-80.03,31.00",
        "Georgia": "-85.61,30.36,-80.84,35.00",
        "Hawaii": "-178.33,18.91,-154.81,28.40",
        "Idaho": "-117.24,42.00,-111.04,49.00",
        "Illinois": "-91.51,36.97,-87.49,42.51",
        "Indiana": "-88.10,37.77,-84.78,41.76",
        "Iowa": "-96.64,40.38,-90.14,43.50",
        "Kansas": "-102.05,36.99,-94.59,40.00",
        "Kentucky": "-89.57,36.50,-81.96,39.15",
        "Louisiana": "-94.04,28.93,-88.82,33.02",
        "Maine": "-71.08,43.06,-66.95,47.46",
        "Maryland": "-79.49,37.91,-75.05,39.72",
        "Massachusetts": "-73.51,41.24,-69.93,42.89",
        "Michigan": "-90.42,41.70,-82.41,48.30",
        "Minnesota": "-97.24,43.50,-89.53,49.38",
        "Mississippi": "-91.65,30.17,-88.09,35.00",
        "Missouri": "-95.77,36.00,-89.10,40.61",
        "Montana": "-116.05,44.36,-104.04,49.00",
        "Nebraska": "-104.05,40.00,-95.31,43.00",
        "Nevada": "-120.00,35.00,-114.04,42.00",
        "New Hampshire": "-72.56,42.70,-70.71,45.31",
        "New Jersey": "-75.56,38.93,-73.89,41.36",
        "New Mexico": "-109.05,31.33,-103.00,37.00",
        "New York": "-79.76,40.50,-71.85,45.01",
        "North Carolina": "-84.32,33.84,-75.46,36.59",
        "North Dakota": "-104.05,45.94,-96.55,49.00",
        "Ohio": "-84.82,38.40,-80.52,41.98",
        "Oklahoma": "-103.00,33.62,-94.43,37.00",
        "Oregon": "-124.57,42.00,-116.46,46.29",
        "Pennsylvania": "-80.52,39.72,-74.69,42.27",
        "Rhode Island": "-71.89,41.14,-71.12,42.02",
        "South Carolina": "-83.35,32.05,-78.54,35.22",
        "South Dakota": "-104.06,42.48,-96.44,45.94",
        "Tennessee": "-90.31,34.98,-81.65,36.68",
        "Texas": "-106.65,25.84,-93.51,36.50",
        "Utah": "-114.05,37.00,-109.04,42.00",
        "Vermont": "-73.44,42.73,-71.47,45.02",
        "Virginia": "-83.68,36.54,-75.24,39.46",
        "Washington": "-124.77,45.54,-116.91,49.00",
        "West Virginia": "-82.64,37.20,-77.72,40.64",
        "Wisconsin": "-92.89,42.49,-86.81,47.08",
        "Wyoming": "-111.05,41.00,-104.05,45.01",
        "District of Columbia": "-77.12,38.80,-76.91,38.99"
    }

    # Danh sách các bang đặc biệt lớn cần xử lý riêng với độ phân giải cao hơn
    very_large_states = ["Texas", "California", "Montana", "Wyoming"]

    # Danh sách các bang lớn hơn mức trung bình nhưng không quá lớn
    large_states = ["Arizona", "Colorado", "Idaho", "Kansas", "Minnesota",
                    "Nebraska", "Nevada", "New Mexico", "North Dakota",
                    "Oklahoma", "Oregon", "South Dakota", "Utah", "Washington"]

    # Tạo thư mục output với timestamp để tránh ghi đè
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"us_traffic_data_{timestamp}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    all_incidents = []
    processed_states = 0
    total_states = len(us_states)
    start_time = time.time()

    # Thống kê các trạng thái xử lý
    success_states = []
    failed_states = []
    partial_states = []

    print(f"Starting to collect traffic data from {total_states} US states...")

    for state, bbox in us_states.items():
        print(f"\nProcessing {state} ({processed_states + 1}/{total_states})...")
        state_start_time = time.time()

        try:
            # Xử lý theo 3 nhóm kích thước bang
            if state in very_large_states:
                # Các bang cực lớn: phân chia nhỏ nhất với max_area = 3000 km²
                print(f"Applying very high resolution division for {state} (extremely large state)")
                state_incidents = process_large_state(state, bbox, api_key, fields, max_area=3000)
            elif state in large_states:
                # Các bang lớn: phân chia với max_area = 6000 km²
                print(f"Applying high resolution division for {state} (large state)")
                state_incidents = process_large_state(state, bbox, api_key, fields, max_area=6000)
            else:
                # Các bang nhỏ và vừa: phân chia bình thường với max_area = 9000 km²
                sub_bboxes = split_bbox(bbox, max_area=9000)
                print(f"State divided into {len(sub_bboxes)} sub-regions for processing")

                state_incidents = []
                region_count = 0

                for region_bbox in sub_bboxes:
                    region_count += 1
                    print(f"  Processing region {region_count}/{len(sub_bboxes)} in {state}...")

                    # Thêm một khoảng thời gian nhỏ giữa các request để tránh rate limiting
                    if region_count > 1:
                        time.sleep(0.8)  # Thời gian chờ ngắn hơn cho các bang nhỏ

                    area = calculate_area(region_bbox)
                    if area > 10000:
                        print(f"  Warning: Skipping sub-region with area {area:.2f} km² (exceeds API limit)")
                        continue

                    incidents_data = get_incidents_by_bbox(api_key, region_bbox, fields)

                    if incidents_data and 'incidents' in incidents_data:
                        num_incidents = len(incidents_data['incidents'])
                        print(f"    Found {num_incidents} traffic incidents")

                        # Thêm thông tin tiểu bang
                        for incident in incidents_data['incidents']:
                            if 'properties' not in incident:
                                incident['properties'] = {}
                            incident['properties']['state'] = state

                        state_incidents.extend(incidents_data['incidents'])
                    else:
                        print(f"    No incidents found or request failed")

            # Lưu dữ liệu của tiểu bang
            if state_incidents:
                state_data = {"incidents": state_incidents}

                state_file = f"{output_dir}/{state.replace(' ', '_')}_traffic.json"
                with open(state_file, 'w') as f:
                    json.dump(state_data, f, indent=2)

                num_incidents = len(state_incidents)
                print(f"Saved {num_incidents} incidents for {state}")

                # Thêm thống kê thời gian xử lý cho bang
                state_duration = time.time() - state_start_time
                print(f"Processing time for {state}: {state_duration:.2f} seconds")

                all_incidents.extend(state_incidents)
                success_states.append(state)
            else:
                print(f"No incidents found for {state}")
                failed_states.append(state)

        except Exception as e:
            print(f"Error processing {state}: {e}")
            failed_states.append(state)
            # Tiếp tục xử lý các bang khác
            continue
        finally:
            processed_states += 1
            # Thêm thời gian nghỉ giữa các bang để tránh rate limiting
            if processed_states < total_states:
                time.sleep(2)

    # Lưu toàn bộ dữ liệu
    combined_data = {"incidents": all_incidents}

    with open(f"{output_dir}/all_us_traffic.json", 'w') as f:
        json.dump(combined_data, f, indent=2)

    # Thống kê tổng thể
    end_time = time.time()
    duration = end_time - start_time

    print(f"\nSummary:")
    print(f"Total incidents collected: {len(all_incidents)}")
    print(f"Total states processed: {processed_states}/{total_states}")
    print(f"States with successful data collection: {len(success_states)}/{total_states}")
    if failed_states:
        print(f"States with failed data collection: {len(failed_states)}")
        print(f"  Failed states: {', '.join(failed_states)}")
    print(f"Total processing time: {duration:.2f} seconds")
    print(f"All data saved to directory: {output_dir}")

    return combined_data


# Ví dụ sử dụng:
if __name__ == "__main__":
    api_key = "qO825bMb13Vad8AGE5mpNCngpm63wWND"

    # Tùy chỉnh fields để lọc thông tin bạn cần
    fields = "{incidents{type,geometry{type,coordinates},properties{id,iconCategory,magnitudeOfDelay,events{description,code,iconCategory},startTime,endTime,from,to,length,delay,roadNumbers,timeValidity}}}"

    # Lấy dữ liệu và chỉ lưu dạng JSON
    us_traffic_data = get_us_traffic_data(api_key, fields)