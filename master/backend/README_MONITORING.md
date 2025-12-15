# Monitoring System

Simple monitoring system for small-scale deployments (Agent < 50).

## Features

- ✅ FastAPI request/response logging to files
- ✅ Database query logging
- ✅ API metrics collection (RPS, response times, error rates)
- ✅ Database connection pool monitoring
- ✅ Periodic report generation

## Log Files

Logs are stored in `master/backend/logs/`:

- `master-backend.log` - Application logs (requests, responses, errors)
- `database-queries.log` - Database query logs
- `master-backend.log.1`, `master-backend.log.2`, etc. - Rotated log files (max 10MB, 5 backups)

## API Endpoints

### `/api/health`
Health check endpoint with basic stats and database pool information.

### `/api/metrics`
Get comprehensive metrics summary for all endpoints.

### `/api/metrics/pending-deployments`
Get specific metrics for `/api/deployments/pending/{agent_id}` endpoint:
- Total requests
- Requests per second (RPS)
- Response times (mean, p50, p95, p99)
- Error rate and error breakdown

## Generating Reports

Generate monitoring reports using the `generate_report.py` script:

```bash
# Generate report for last 24 hours (default)
cd master/backend
python generate_report.py

# Generate report for last 12 hours
python generate_report.py --hours 12

# Generate report and save to JSON file
python generate_report.py --output reports/report_$(date +%Y%m%d_%H%M%S).json
```

Report includes:
- Metrics summary (RPS, response times, error rates)
- Pending deployment endpoint specific metrics
- Log analysis (request counts, errors by status code)
- Database connection pool statistics

## Scheduled Reports

Set up a cron job to generate reports periodically:

```bash
# Add to crontab (crontab -e)
# Generate daily report at 00:00
0 0 * * * cd /path/to/master/backend && python generate_report.py --output reports/daily_$(date +\%Y\%m\%d).json

# Generate hourly reports
0 * * * * cd /path/to/master/backend && python generate_report.py --hours 1 --output reports/hourly_$(date +\%Y\%m\%d_\%H).json
```

## Database Indexes

The following indexes are created for optimal query performance:

### Deployments Table
- `idx_deployment_agent_status_created` - Composite index on (agent_id, status, created_at)
  - Optimizes: `WHERE agent_id = ? AND status = ? ORDER BY created_at`
- `idx_deployment_status` - Index on status column
  - Optimizes: Filtering by deployment status
- `idx_deployment_created_at` - Index on created_at column
  - Optimizes: Ordering by creation date

### Agents Table
- Index on `id` (primary key)
- Index on `name` column

### Other Tables
- Primary key indexes on all tables

## Monitoring Checklist

### Daily Checks
- [ ] Review `/api/metrics/pending-deployments` endpoint metrics
- [ ] Check error rates (should be < 1%)
- [ ] Monitor database connection pool usage
- [ ] Review log files for errors

### Weekly Checks
- [ ] Review weekly report summary
- [ ] Analyze response time trends (p95, p99)
- [ ] Check database query performance
- [ ] Verify indexes are being used (check query plans if needed)

### Performance Metrics to Track
- [ ] `/api/deployments/pending/{agent_id}` RPS (should be ~0.1 req/sec per agent)
- [ ] Response time p50 < 50ms, p95 < 200ms, p99 < 500ms
- [ ] Database connection pool usage < 80%
- [ ] Error rate < 1%
- [ ] Database query time < 100ms

## Troubleshooting

### High RPS on pending deployment endpoint
- Check number of agents
- Verify polling interval (should be 10 seconds per agent)
- Consider increasing polling interval if needed

### High response times
- Check database query performance
- Verify indexes are created and being used
- Monitor database connection pool
- Check for slow queries in `database-queries.log`

### High error rate
- Review error logs in `master-backend.log`
- Check database connection issues
- Verify agent IDs are valid
- Check for database constraint violations

### Database pool exhaustion
- Increase `pool_size` in `database.py` if needed
- Check for connection leaks (connections not being closed)
- Monitor with `/api/health` endpoint

