# gunicorn.conf.py

# Worker 設定
workers = 1  # 減少 worker 數量
threads = 2  # 使用執行緒來處理請求
worker_class = 'gthread'  # 使用執行緒模式
worker_connections = 1000

# 超時設定
timeout = 120  # 增加超時時間
graceful_timeout = 30

# 記憶體相關
max_requests = 1000        # 處理這麼多請求後重啟 worker
max_requests_jitter = 200  # 添加隨機性以避免同時重啟
worker_tmp_dir = '/tmp'

# 日誌設定
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# 限制記憶體使用
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190