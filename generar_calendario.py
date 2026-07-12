#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

LOCAL_TARGETS = ("bilbao", "bilbo", "basauri")
COMMON_SCOPES = (
    "euskadi",
    "país vasco",
    "pais vasco",
    "comunidad autónoma del país vasco",
    "comunidad autonoma del pais vasco",
    "bizkaia",
    "vizcaya",
    "biscay",
)
URL_TEMPLATE = (
    "https://opendata.euskadi