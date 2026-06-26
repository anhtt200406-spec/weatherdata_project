# Quy tắc dbt + Airflow cho ELT Pipeline

## 1. Kiến trúc tổng thể (ELT)

```
Source API / DB
  → Extract + Load (Python script)     # Lấy dữ liệu thô, đưa vào DB nguyên xi
  → Transform (dbt)                    # Làm sạch và tạo báo cáo
  → Orchestrate (Airflow)              # Lên lịch, đảm bảo đúng thứ tự chạy
```

**Nguyên tắc phân vai:**
- **Python/Airflow**: chỉ điều phối và vận chuyển dữ liệu, không chứa business logic
- **dbt**: toàn bộ logic transform và làm sạch dữ liệu nằm ở đây
- Không viết SQL transform bên trong PythonOperator — khó test, khó maintain

---

## 2. Quy tắc dbt

### 2.1 Cấu trúc thư mục chuẩn

```
models/
├── staging/
│   └── stg_[source]__[entity].sql     # stg_weatherstack__weather.sql
├── intermediate/                       # (tuỳ chọn, dùng khi logic phức tạp)
│   └── int_[domain]__[purpose].sql
└── mart/
    └── [entity_name].sql              # daily_average.sql, weather_report.sql
```

### 2.2 Quy tắc đặt tên model

| Layer | Prefix | Ví dụ |
|---|---|---|
| Staging | `stg_` | `stg_weather__current.sql` |
| Intermediate | `int_` | `int_weather__daily_grouped.sql` |
| Mart | *(không có prefix)* | `daily_average.sql`, `weather_report.sql` |

### 2.3 Materialization (cách dbt lưu kết quả)

| Layer | Materialization | Lý do |
|---|---|---|
| Staging | `view` | Không tốn storage, luôn lấy data mới nhất |
| Intermediate | `ephemeral` hoặc `view` | Chỉ là bước trung gian |
| Mart | `table` | Query nhanh, dùng cho dashboard/báo cáo |

```sql
-- staging: dùng view
{{ config(materialized='view') }}

-- mart: dùng table
{{ config(materialized='table') }}
```

### 2.4 Quy tắc staging model

- Mỗi staging model **1-1 với 1 source table** — không join ở đây
- Chỉ được dùng macro `{{ source(...) }}` tại staging, các layer sau dùng `{{ ref(...) }}`
- Chỉ làm: đổi tên cột, cast kiểu dữ liệu, lọc dữ liệu xấu
- Không chứa business logic (tính toán, aggregation)

```sql
-- ĐÚNG: staging chỉ rename + cast
select
    id,
    temperature::float        as temperature,
    observation_time::timestamp as observed_at
from {{ source('weather', 'weather_data') }}

-- SAI: đừng aggregation ở staging
select avg(temperature) from {{ source('weather', 'weather_data') }}
```

### 2.5 Hàm SQL PostgreSQL hay bị nhầm

| SAI | ĐÚNG | Ghi chú |
|---|---|---|
| `average(col)` | `avg(col)` | PostgreSQL không có `average()` |
| `round(avg(col::numeric, 2))` | `round(avg(col)::numeric, 2)` | Cast phải nằm ngoài `avg()` |
| `ILIKE` trên số | chỉ dùng cho text | |

### 2.6 profiles.yml và DBT_PROFILES_DIR

- Mặc định dbt tìm `profiles.yml` tại `~/.dbt/profiles.yml`
- Nếu đặt `profiles.yml` trong project folder (khuyến nghị cho Docker), phải set env var:
  ```
  DBT_PROFILES_DIR=/path/to/project
  ```
- `working_dir` của container dbt phải trỏ đúng vào folder chứa `dbt_project.yml`

```yaml
# profiles.yml — kết nối PostgreSQL
my_project:
  target: dev
  outputs:
    dev:
      type: postgres
      host: db          # hostname của container, KHÔNG phải localhost
      port: 5432
      dbname: mydb
      schema: my_schema
      user: user
      password: password
      threads: 1
```

### 2.7 Testing dbt model

Thêm file `schema.yml` vào mỗi layer để test tự động:

```yaml
# models/staging/schema.yml
version: 2
models:
  - name: stg_weather__current
    columns:
      - name: id
        tests:
          - unique
          - not_null
      - name: temperature
        tests:
          - not_null
```

Chạy test: `dbt test`

### 2.8 sources.yml

```yaml
# models/staging/sources.yml
version: 2
sources:
  - name: weather                    # tên dùng trong {{ source('weather', ...) }}
    schema: weather_schema           # schema thật trong DB
    tables:
      - name: weather_data
```

---

## 3. Quy tắc Airflow

### 3.1 Cấu trúc DAG tối thiểu

```python
import pendulum                      # LUÔN dùng pendulum, không dùng datetime.now()
from airflow import DAG
from datetime import timedelta

default_args = {
    'start_date': pendulum.datetime(2025, 1, 1, tz="Asia/Ho_Chi_Minh"),
    'catchup': False,                # Tắt backfill nếu không cần
}

dag = DAG(
    dag_id='my_pipeline',
    default_args=default_args,
    schedule=timedelta(hours=1)
)
```

**Lý do dùng `pendulum` thay `datetime`:** `datetime.now()` trả về giờ máy local, kết quả khác nhau mỗi lần chạy — vi phạm tính idempotency. `pendulum` xử lý timezone tường minh.

### 3.2 Idempotency — Nguyên tắc quan trọng nhất

Task phải cho **cùng kết quả** dù chạy 1 lần hay 10 lần:

```python
# SAI: mỗi lần chạy insert 1 bản ghi mới → bị duplicate
cursor.execute("INSERT INTO table VALUES (%s)", (value,))

# ĐÚNG: upsert — nếu đã có thì update
cursor.execute("""
    INSERT INTO table (id, value)
    VALUES (%s, %s)
    ON CONFLICT (id) DO UPDATE SET value = EXCLUDED.value
""", (id, value))
```

### 3.3 DockerOperator — cấu hình đúng

```python
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

task = DockerOperator(
    task_id='run_dbt',
    image='ghcr.io/dbt-labs/dbt-postgres:1.9.latest',
    command='run',
    working_dir='/usr/app/my_project',  # phải trỏ đúng folder có dbt_project.yml

    mounts=[
        Mount(
            source='/absolute/path/on/host/dbt/my_project',  # đường dẫn TUYỆT ĐỐI trên máy host
            target='/usr/app/my_project',                     # nơi container sẽ thấy
            type='bind'
        ),
        Mount(
            source='/absolute/path/on/host/dbt/my_project',  # profiles.yml nằm đây
            target='/root/.dbt/',                              # dbt tìm profiles ở đây mặc định
            type='bind'
        ),
    ],

    environment={
        'DBT_PROFILES_DIR': '/usr/app/my_project'  # chỉ rõ nơi có profiles.yml
    },

    network_mode='my_network',              # phải cùng network với PostgreSQL container
    docker_url='unix:///var/run/docker.sock',
    auto_remove='success'                   # xóa container sau khi chạy xong thành công
)
```

**Checklist DockerOperator:**
- [ ] `source` trong Mount phải là **đường dẫn tuyệt đối** trên máy host
- [ ] `working_dir` phải chứa `dbt_project.yml`
- [ ] `network_mode` phải cùng với network của database container
- [ ] Set `DBT_PROFILES_DIR` nếu `profiles.yml` không ở `~/.dbt/`
- [ ] Không hardcode credentials — dùng Airflow Connections hoặc biến môi trường

### 3.4 Thứ tự task và dependency

```python
# Cú pháp khai báo thứ tự
task1 >> task2           # task2 chạy sau task1 thành công
task1 >> [task2, task3]  # task2 và task3 chạy song song sau task1
[task1, task2] >> task3  # task3 chờ cả task1 và task2 xong
```

### 3.5 Truyền dữ liệu giữa task

```python
# Dùng XCom cho dữ liệu nhỏ (< 48KB)
def task1(**context):
    context['ti'].xcom_push(key='result', value={'count': 100})

def task2(**context):
    data = context['ti'].xcom_pull(task_ids='task1', key='result')
```

Dữ liệu lớn: ghi ra file/S3/DB, task sau đọc lại — không truyền qua XCom.

### 3.6 sys.path khi import module trong DAG

```python
import sys
import os

# ĐÚNG: thêm đường dẫn trong container, không phải máy local
sys.path.insert(0, '/opt/airflow/dags')

# SAI: đường dẫn máy local không tồn tại trong container
sys.path.insert(0, '/home/user/repos/my_project/airflow/dags')
```

---

## 4. Quy tắc Docker + Network

### 4.1 Hostname trong container

```
# Bên ngoài container (máy host)   →   Bên trong container
localhost:5432                      →   db:5432  (tên service trong docker-compose)
```

**Lỗi phổ biến:** code Python dùng `host="localhost"` — hoạt động khi test local nhưng fail trong container vì `localhost` trong container là chính container đó, không phải máy host.

```python
# insert_record.py chạy trong container → dùng tên service
conn = psycopg2.connect(host="db", ...)     # ĐÚNG khi chạy trong Docker
conn = psycopg2.connect(host="localhost", ...) # CHỈ đúng khi chạy local
```

### 4.2 Bind mount — quy tắc

- Mount source phải là **đường dẫn tuyệt đối**, không dùng `./` hay `~`
- Mỗi thứ mount vào container có thể bị ghi đè nếu target trùng — cẩn thận thứ tự mount
- File tạo bởi Docker (chạy root) có thể bị lỗi permission khi sửa trên host:
  ```bash
  sudo chown -R $USER:$USER ./dbt/
  ```

---

## 5. Checklist khi tạo pipeline mới

### Bước 1 — Thiết kế schema DB

- [ ] Xác định tất cả cột cần lấy từ API (bao gồm city, timezone, v.v.)
- [ ] Định nghĩa đúng kiểu dữ liệu (FLOAT, TEXT, TIMESTAMP)
- [ ] Thêm cột `id SERIAL PRIMARY KEY` và `timestamp DEFAULT CURRENT_TIMESTAMP`

### Bước 2 — Script Extract + Load

- [ ] Parse đủ các field cần thiết từ API response
- [ ] Dùng UPSERT thay INSERT để tránh duplicate
- [ ] Kết nối DB dùng hostname của container (không phải `localhost`)

### Bước 3 — dbt models

- [ ] Tạo `sources.yml` khai báo source table
- [ ] Staging model: `stg_` prefix, materialized view, chỉ dùng `{{ source() }}`
- [ ] Mart model: tên entity, materialized table, dùng `{{ ref() }}` tham chiếu staging
- [ ] Thêm `schema.yml` với test `unique` và `not_null` cho cột quan trọng

### Bước 4 — Airflow DAG

- [ ] Import `pendulum`, không dùng `datetime`
- [ ] `catchup=False` nếu không cần backfill
- [ ] DockerOperator: kiểm tra path, network, DBT_PROFILES_DIR
- [ ] Khai báo `task1 >> task2` đúng thứ tự
- [ ] Không hardcode password trong DAG file

### Bước 5 — Kiểm tra

```bash
# Kiểm tra dbt compile trước khi run
dbt compile

# Chạy test dbt
dbt test

# Validate DAG không có lỗi syntax
python my_dag.py

# Xem kết quả trong DB
psql -U user -d db -c "SELECT * FROM schema.mart_model LIMIT 10;"
```

---

## 6. Lỗi thường gặp và cách fix

| Lỗi | Nguyên nhân | Fix |
|---|---|---|
| `function average() does not exist` | PostgreSQL không có `average()` | Đổi thành `avg()` |
| `syntax error at or near "select"` | Thiếu `;` giữa các câu SQL trong psql | Thêm `;` sau mỗi câu |
| `could not connect to server` trong container | Dùng `localhost` thay vì tên service | Đổi host thành tên service (`db`) |
| `dbt_project.yml not found` | `working_dir` sai | Set `working_dir` trỏ đúng folder project |
| `profiles.yml not found` | dbt tìm sai vị trí | Set `DBT_PROFILES_DIR` |
| Permission denied trên file dbt | Docker tạo file với quyền root | `sudo chown -R $USER:$USER ./dbt/` |
| DAG không load được | Thiếu `import pendulum` | Thêm import |

---

## Sources

- [How we structure our dbt projects — dbt Developer Hub](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview)
- [Staging: Preparing our atomic building blocks — dbt Developer Hub](https://docs.getdbt.com/best-practices/how-we-structure/2-staging)
- [Marts: Business-defined entities — dbt Developer Hub](https://docs.getdbt.com/best-practices/how-we-structure/4-marts)
- [Best Practices — Airflow 3.2.2 Documentation](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [DockerOperator in Apache Airflow: A Comprehensive Guide](https://www.sparkcodehub.com/airflow/operators/docker-operator)
