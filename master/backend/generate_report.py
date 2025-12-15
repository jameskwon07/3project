#!/usr/bin/env python3
"""
Monitoring report generator
Generates periodic reports from logs and metrics
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import re
from typing import Dict, List

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent))

try:
    from monitoring import get_metrics_summary, get_pending_deployment_metrics
    from database import engine
except ImportError:
    # If running standalone without full app context
    print("Warning: Could not import monitoring modules. Some metrics may be unavailable.")
    def get_metrics_summary():
        return {}
    def get_pending_deployment_metrics():
        return {}
    engine = None


def parse_log_file(log_file: Path, start_time: datetime = None, end_time: datetime = None) -> List[Dict]:
    """Parse log file and extract relevant entries"""
    if not log_file.exists():
        return []
    
    entries = []
    with open(log_file, 'r') as f:
        for line in f:
            try:
                # Parse timestamp from log entry
                # Format: YYYY-MM-DD HH:MM:SS
                match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                if match:
                    log_time = datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
                    
                    if start_time and log_time < start_time:
                        continue
                    if end_time and log_time > end_time:
                        continue
                    
                    entries.append({
                        'timestamp': log_time,
                        'line': line.strip()
                    })
            except Exception:
                continue
    
    return entries


def analyze_logs(log_dir: Path, hours: int = 24) -> Dict:
    """Analyze logs for the last N hours"""
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    
    log_file = log_dir / "master-backend.log"
    db_log_file = log_dir / "database-queries.log"
    
    analysis = {
        'period': {
            'start': start_time.isoformat(),
            'end': end_time.isoformat(),
            'hours': hours
        },
        'request_logs': parse_log_file(log_file, start_time, end_time),
        'database_queries': parse_log_file(db_log_file, start_time, end_time)
    }
    
    # Count errors by status code
    error_counts = defaultdict(int)
    endpoint_counts = defaultdict(int)
    
    for entry in analysis['request_logs']:
        line = entry['line']
        # Extract status code
        status_match = re.search(r'Status: (\d+)', line)
        if status_match:
            status = status_match.group(1)
            if int(status) >= 400:
                error_counts[status] += 1
        
        # Extract endpoint
        method_path_match = re.search(r'(GET|POST|PUT|DELETE|PATCH) (/[^\s]+)', line)
        if method_path_match:
            endpoint = f"{method_path_match.group(1)} {method_path_match.group(2)}"
            endpoint_counts[endpoint] += 1
    
    analysis['error_summary'] = dict(error_counts)
    analysis['endpoint_counts'] = dict(endpoint_counts)
    analysis['total_requests'] = len(analysis['request_logs'])
    analysis['total_errors'] = sum(error_counts.values())
    analysis['error_rate'] = analysis['total_errors'] / analysis['total_requests'] if analysis['total_requests'] > 0 else 0
    
    # Count database queries
    analysis['database_query_count'] = len(analysis['database_queries'])
    
    return analysis


def get_database_stats():
    """Get database connection pool statistics"""
    if engine is None:
        return {"error": "Database engine not available"}
    
    try:
        pool = engine.pool
        stats = {
            "pool_size": pool.size() if hasattr(pool, 'size') else "N/A",
            "checked_in": pool.checkedin() if hasattr(pool, 'checkedin') else "N/A",
            "checked_out": pool.checkedout() if hasattr(pool, 'checkedout') else "N/A",
            "overflow": pool.overflow() if hasattr(pool, 'overflow') else "N/A",
            "total_connections": None
        }
        
        # Calculate total connections if possible
        if stats["pool_size"] != "N/A" and stats["checked_out"] != "N/A":
            stats["total_connections"] = stats["pool_size"] + (stats["overflow"] if stats["overflow"] != "N/A" else 0)
        
        return stats
    except Exception as e:
        return {"error": str(e)}


def generate_report(hours: int = 24, output_file: Path = None):
    """Generate monitoring report"""
    log_dir = Path(__file__).parent / "logs"
    
    print(f"Generating monitoring report for the last {hours} hours...")
    print("=" * 80)
    
    # Get current metrics
    try:
        metrics = get_metrics_summary()
        pending_metrics = get_pending_deployment_metrics()
    except Exception as e:
        print(f"Warning: Could not get metrics: {e}")
        metrics = {}
        pending_metrics = {}
    
    # Analyze logs
    log_analysis = analyze_logs(log_dir, hours=hours)
    
    # Get database stats
    db_stats = get_database_stats()
    
    # Build report
    report = {
        'generated_at': datetime.now().isoformat(),
        'period_hours': hours,
        'metrics': metrics,
        'pending_deployment_metrics': pending_metrics,
        'log_analysis': log_analysis,
        'database_pool_stats': db_stats
    }
    
    # Print summary
    print("\n📊 METRICS SUMMARY")
    print("-" * 80)
    if metrics:
        print(f"Total Requests: {metrics.get('total_requests', 0)}")
        print(f"Requests per Second: {metrics.get('requests_per_second', 0):.2f}")
        print(f"Uptime: {metrics.get('uptime_seconds', 0):.0f} seconds")
    
    print("\n📦 PENDING DEPLOYMENT ENDPOINT METRICS")
    print("-" * 80)
    if pending_metrics:
        print(f"Total Requests: {pending_metrics.get('total_requests', 0)}")
        print(f"RPS: {pending_metrics.get('rps', 0):.2f}")
        rt = pending_metrics.get('response_time_ms', {})
        print(f"Response Time - Mean: {rt.get('mean', 0):.2f}ms, P50: {rt.get('p50', 0):.2f}ms, "
              f"P95: {rt.get('p95', 0):.2f}ms, P99: {rt.get('p99', 0):.2f}ms")
        print(f"Error Rate: {pending_metrics.get('error_rate', 0):.2%}")
        if pending_metrics.get('errors'):
            print(f"Errors: {pending_metrics.get('errors')}")
    
    print("\n📋 LOG ANALYSIS")
    print("-" * 80)
    print(f"Total Requests (from logs): {log_analysis['total_requests']}")
    print(f"Total Errors: {log_analysis['total_errors']}")
    print(f"Error Rate: {log_analysis['error_rate']:.2%}")
    if log_analysis['error_summary']:
        print("Errors by Status Code:")
        for status, count in sorted(log_analysis['error_summary'].items()):
            print(f"  {status}: {count}")
    print(f"Database Queries: {log_analysis['database_query_count']}")
    
    print("\n🗄️  DATABASE POOL STATS")
    print("-" * 80)
    for key, value in db_stats.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 80)
    
    # Save to file if specified
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n✅ Report saved to: {output_file}")
    
    return report


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate monitoring report')
    parser.add_argument('--hours', type=int, default=24, help='Number of hours to analyze (default: 24)')
    parser.add_argument('--output', type=str, help='Output file path (JSON format)')
    
    args = parser.parse_args()
    
    output_path = Path(args.output) if args.output else None
    generate_report(hours=args.hours, output_file=output_path)

