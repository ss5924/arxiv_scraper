import os
from dotenv import load_dotenv
import logging

# .env 파일 로드
load_dotenv()

# DB 설정
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_ENGINE_URL = os.getenv("DB_ENGINE_URL")

# 서비스 동작 제어를 위한 기본값 설정
TASK_POLL_INTERVAL = int(os.getenv("TASK_POLL_INTERVAL"))
RATE_LIMIT_DELAY = tuple(map(float, os.getenv("RATE_LIMIT_DELAY", "1.5,2.5").split(",")))
SEMAPHORE_LIMIT = int(os.getenv("SEMAPHORE_LIMIT"))
WORKER_COUNT = int(os.getenv("WORKER_COUNT"))

# arxiv API 설정
MAX_RESULTS_PER_QUERY = 100
SORT_BY = "lastUpdatedDate"
SORT_ORDER = "descending"


# logging 설정
def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='/app/logs/app.log',
    )
