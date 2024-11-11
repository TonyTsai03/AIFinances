# wsgi.py (在根目錄)
import os
import sys

# 添加專案目錄到 Python 路徑
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_path)

from aifinances.wsgi import application