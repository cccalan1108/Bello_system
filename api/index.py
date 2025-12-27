# Vercel Serverless Function entry point
# This file is used by Vercel to handle API requests

import sys
import os

# 添加 backend 目錄到 Python 路徑
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, os.path.abspath(backend_path))

# 導入 Flask 應用
# Vercel @vercel/python 會自動識別名為 'app' 的 Flask 應用
from app import app
