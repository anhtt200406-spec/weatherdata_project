import pytest
from unittest.mock import patch, MagicMock, call
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../api_request"))

from insert_record import connect_db, create_table, insert_weather_data


# ============================================================
# DỮ LIỆU MẪU
# ============================================================

SAMPLE_WEATHER_DATA = {
    "location": {"utc_offset": "7.0"},
    "current": {
        "temperature": 30,
        "humidity": 80,
        "wind_speed": 15,
    },
}


# ============================================================
# BÀI TẬP 1 — Kiểm tra connect_db() thành công
# TODO: mock psycopg2.connect, assert nó được gọi đúng 1 lần
#       và trả về connection object
# ============================================================
def test_connect_db_success():
    pass  # TODO: viết test ở đây


# ============================================================
# BÀI TẬP 2 — Kiểm tra connect_db() khi DB không khả dụng
# TODO: mock psycopg2.connect để raise psycopg2.OperationalError
#       rồi assert connect_db() raise exception
# ============================================================
def test_connect_db_failure():
    pass  # TODO: viết test ở đây


# ============================================================
# BÀI TẬP 3 — Kiểm tra create_table() gọi đúng câu SQL
# TODO: tạo mock_conn với mock cursor, gọi create_table(mock_conn),
#       rồi assert cursor.execute() được gọi với câu SQL chứa
#       "CREATE TABLE IF NOT EXISTS"
# ============================================================
def test_create_table_executes_correct_sql():
    pass  # TODO: viết test ở đây


# ============================================================
# BÀI TẬP 4 — Kiểm tra insert_weather_data() truyền đúng giá trị
# TODO: gọi insert_weather_data(mock_conn, SAMPLE_WEATHER_DATA)
#       rồi assert cursor.execute() được gọi với tuple
#       (30, 80, 15, "7.0")
# ============================================================
def test_insert_weather_data_correct_values():
    pass  # TODO: viết test ở đây


# ============================================================
# BÀI TẬP 5 — Kiểm tra insert_weather_data() gọi conn.commit()
# TODO: assert conn.commit() được gọi sau khi insert thành công
# ============================================================
def test_insert_weather_data_commits():
    pass  # TODO: viết test ở đây


# ============================================================
# BÀI TẬP 6 — Kiểm tra insert_weather_data() khi cursor.execute raise lỗi
# TODO: cho cursor.execute raise psycopg2.DatabaseError
#       rồi assert insert_weather_data() cũng raise exception
# ============================================================
def test_insert_weather_data_raises_on_db_error():
    pass  # TODO: viết test ở đây
