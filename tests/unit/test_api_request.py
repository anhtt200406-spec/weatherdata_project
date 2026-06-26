import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../api_request"))

from api_request import get_weather_data


# ============================================================
# DỮ LIỆU MẪU (dùng chung cho các test)
# ============================================================

SAMPLE_RESPONSE = {
    "request": {"type": "City", "query": "Hanoi, Vietnam"},
    "location": {
        "name": "Hanoi",
        "country": "Vietnam",
        "utc_offset": "7.0",
    },
    "current": {
        "temperature": 30,
        "humidity": 80,
        "wind_speed": 15,
        "weather_descriptions": ["Partly cloudy"],
    },
}


# ============================================================
# BÀI TẬP 1 — Kiểm tra trường hợp API trả về thành công
# TODO: dùng @patch để mock requests.get, cho nó trả về
#       SAMPLE_RESPONSE, rồi assert kết quả của get_weather_data()
# ============================================================
def test_get_weather_data_success():
    pass  # TODO: viết test ở đây


# ============================================================
# BÀI TẬP 2 — Kiểm tra khi API trả về lỗi (status 500)
# TODO: mock requests.get để raise requests.exceptions.HTTPError
#       rồi assert get_weather_data() raise exception hoặc
#       trả về giá trị phù hợp
# ============================================================
def test_get_weather_data_http_error():
    pass  # TODO: viết test ở đây


# ============================================================
# BÀI TẬP 3 — Kiểm tra cấu trúc JSON trả về
# TODO: assert response có đủ các key: "location", "current"
#       và current có các key: "temperature", "humidity", "wind_speed"
# ============================================================
def test_get_weather_data_response_structure():
    pass  # TODO: viết test ở đây


# ============================================================
# BÀI TẬP 4 — Kiểm tra khi mất kết nối mạng
# TODO: mock requests.get để raise requests.exceptions.ConnectionError
# ============================================================
def test_get_weather_data_connection_error():
    pass  # TODO: viết test ở đây
