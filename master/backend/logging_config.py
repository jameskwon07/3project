"""
Logging configuration for Master backend
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
logs_dir = Path(__file__).parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Remove existing handlers
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Console handler (stdout)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(console_formatter)

# File handler (rotating)
log_file = logs_dir / "master-backend.log"
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_formatter)

# Database query log file
db_log_file = logs_dir / "database-queries.log"
db_handler = RotatingFileHandler(
    db_log_file,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5
)
db_handler.setLevel(logging.INFO)
db_formatter = logging.Formatter(
    '%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
db_handler.setFormatter(db_formatter)

# SQLAlchemy query logger
sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
sqlalchemy_logger.setLevel(logging.INFO)
sqlalchemy_logger.addHandler(db_handler)
sqlalchemy_logger.propagate = False  # Don't propagate to root logger

# Add handlers to root logger
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

# Application logger
app_logger = logging.getLogger('master_backend')
app_logger.setLevel(logging.INFO)

# Request/response logger
request_logger = logging.getLogger('master_backend.requests')
request_logger.setLevel(logging.INFO)

def log_database_query(query: str, params: dict = None):
    """Log database query"""
    query_log = f"QUERY: {query}"
    if params:
        query_log += f" | PARAMS: {params}"
    db_handler.emit(logging.LogRecord(
        name='database',
        level=logging.INFO,
        pathname='',
        lineno=0,
        msg=query_log,
        args=(),
        exc_info=None
    ))

