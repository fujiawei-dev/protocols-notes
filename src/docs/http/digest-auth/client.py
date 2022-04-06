"""
Date: 2022.04.06 16:24
Description: Omit
LastEditors: Rustle Karl
LastEditTime: 2022.04.06 16:24
"""
import requests
from requests.auth import HTTPDigestAuth

requests.put(
    "http://localhost:8787/immigration/debug",
    auth=HTTPDigestAuth("admin", "admin"),
    json={"x": "y"},
)
