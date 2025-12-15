"""
Metrics collection middleware
Collects API metrics for monitoring
"""

import time
from datetime import datetime
from typing import Dict
from collections import defaultdict, deque
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Metrics storage (in-memory)
request_counts: Dict[str, int] = defaultdict(int)
response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
error_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
total_requests: int = 0
start_time: datetime = datetime.now()


class MetricsCollectorMiddleware(BaseHTTPMiddleware):
    """Middleware to collect API metrics"""
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method
        endpoint = f"{method} {path}"
        
        start = time.time()
        status_code = 200
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception:
            status_code = 500
            raise
        finally:
            # Record metrics
            elapsed_time = (time.time() - start) * 1000  # Convert to milliseconds
            
            # Update request count
            request_counts[endpoint] += 1
            global total_requests
            total_requests += 1
            
            # Record response time
            response_times[endpoint].append(elapsed_time)
            
            # Record error counts
            if status_code >= 400:
                error_counts[endpoint][str(status_code)] += 1


def get_metrics() -> Dict:
    """Get current metrics (exported for monitoring module)"""
    return {
        'request_counts': dict(request_counts),
        'response_times': {k: list(v) for k, v in response_times.items()},
        'error_counts': {k: dict(v) for k, v in error_counts.items()},
        'total_requests': total_requests,
        'start_time': start_time
    }

