import pytest
import psycopg2
import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../api_request"))

# Integration test — cần PostgreSQL đang chạy (docker-compose up)
# Chạy riêng: pytest tests/integration/ -v

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "database": os.getenv("POSTGRES_DB", "db"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}


# ============================================================
# BÀI TẬP 1 — Kết nối thực tới DB và kiểm tra bảng tồn tại
# TODO: kết nối DB thật, truy vấn information_schema để xác nhận
#       bảng weather_schema.weather_data tồn tại
# ============================================================
def test_weather_table_exists():
    pass  # TODO: viết test ở đây


# ============================================================
# BÀI TẬP 2 — Insert một record thật và kiểm tra nó được lưu
# TODO: insert 1 row với dữ liệu giả, rồi SELECT lại và assert
#       các giá trị khớp. Nhớ dọn dẹp (DELETE) sau khi test.
# ============================================================
def test_insert_and_select_record():
    pass  # TODO: viết test ở đây
