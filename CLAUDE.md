# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ELT pipeline thu thập dữ liệu thời tiết Hà Nội từ Weatherstack API, lưu vào PostgreSQL, điều phối bằng Airflow, transform bằng dbt.

**Stack:** Python · PostgreSQL · Apache Airflow · dbt-postgres · Docker Compose

## Docker Commands

```bash
# Khởi động toàn bộ stack
docker-compose up

# Chạy riêng dbt (debug kết nối)
docker-compose run dbt

# Xem log container cụ thể
docker logs dbt_container
docker logs airflow_container
docker logs postgres_container

# Dừng và xóa container
docker-compose down
```

## Data Flow

```
Weatherstack API (Hanoi weather)
  → api_request/api_request.py        # GET request, trả về JSON
  → api_request/insert_record.py      # parse JSON, INSERT vào PostgreSQL
  → PostgreSQL: db.weather_schema.weather_data
  → dbt (transform): dbt/my_project/models/
```

Airflow DAG (`airflow/dags/orchestrator.py`) trigger pipeline trên theo `schedule=timedelta(minutes=1)`.

## Architecture Notes

### Containers & Networks
Tất cả container dùng chung network `my_network`. Trong container, hostname của PostgreSQL là `db` (tên service), không phải `localhost`.

| Container | Image | Port |
|---|---|---|
| `postgres_container` | postgres:14.23 | 5432 |
| `airflow_container` | apache/airflow:latest | 8080 |
| `dbt_container` | dbt-postgres:1.9.latest | — |

### PostgreSQL
- **2 database tách biệt:** `airflow_db` (metadata của Airflow, tạo qua `postgres/airflow_init.sql`) và `db` (weather data)
- Weather data lưu ở schema `weather_schema`, table `weather_data`
- `insert_record.py` tự tạo schema/table nếu chưa có

### Airflow
- DAG file: `airflow/dags/orchestrator.py`
- Được mount vào container tại `/opt/airflow/dags/`
- Chạy `airflow db migrate && airflow standalone` khi khởi động
- **Lưu ý:** `orchestrator.py` thiếu `import pendulum` và `sys.path` trỏ sai (trỏ local path thay vì `/opt/airflow/dags/`)

### dbt
- Project: `dbt/my_project/`
- `profiles.yml` nằm trong `dbt/my_project/profiles.yml` (không phải `~/.dbt/`)
- `working_dir` trong docker-compose phải là `/usr/app/my_project` (không phải `/usr/app`)
- `DBT_PROFILES_DIR=/usr/app/my_project` được set qua environment trong docker-compose
- Models đặt tại `dbt/my_project/models/`, kết nối vào `db.weather_schema`

### Quyền file
Thư mục `dbt/` được tạo bởi Docker (chạy root), có thể bị lỗi permission khi chỉnh sửa file. Fix:
```bash
sudo chown -R $USER:$USER ./dbt/
```

## Key Files

| File | Vai trò |
|---|---|
| `api_request/api_request.py` | Gọi Weatherstack API, trả về JSON |
| `api_request/insert_record.py` | Kết nối DB, tạo bảng, insert data |
| `airflow/dags/orchestrator.py` | Airflow DAG định nghĩa schedule và task |
| `postgres/airflow_init.sql` | Khởi tạo user/database cho Airflow |
| `dbt/my_project/profiles.yml` | Config kết nối DB cho dbt |
| `docker-compose.yaml` | Định nghĩa toàn bộ infrastructure |
