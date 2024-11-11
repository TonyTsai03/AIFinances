#!/usr/bin/env bash
# exit on error
set -o errexit

# 安裝依賴
pip install -r requirements.txt

# 設定 Python 路徑
export PYTHONPATH="${PYTHONPATH}:/opt/render/project/src/aifinances"

# 收集靜態檔案
python manage.py collectstatic --no-input

# 運行資料庫遷移
python manage.py migrate