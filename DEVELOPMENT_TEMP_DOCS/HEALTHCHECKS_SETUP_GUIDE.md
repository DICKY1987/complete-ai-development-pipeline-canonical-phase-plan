# Healthchecks.io Monitoring Setup Guide

## Quick Setup (5 minutes)

### 1. Create Free Account
Visit: https://healthchecks.io/accounts/signup/

Benefits:
- Free tier: 20 checks, 100 pings/day
- Email and Slack notifications
- Dead man's switch monitoring
- Downtime alerts

### 2. Create Check for MASTER_SPLINTER

1. Log in to healthchecks.io
2. Click "Add Check"
3. Configure:
   - **Name**: MASTER_SPLINTER Orchestrator
   - **Schedule**: Daily (cron: 0 2 * * *)
   - **Grace Period**: 1 hour
   - **Timeout**: 12 hours
   - **Tags**: automation, orchestrator, master-splinter

4. Copy the check URL (looks like: https://hc-ping.com/YOUR-UUID)

### 3. Add to GitHub Secrets

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `HEALTHCHECK_URL`
5. Value: `https://hc-ping.com/YOUR-UUID`
6. Click "Add secret"

### 4. Test Integration

Run this in PowerShell:
```powershell
# Set environment variable (temporary)
$env:HEALTHCHECK_URL = "https://hc-ping.com/YOUR-UUID"

# Test ping
python -c "
from scripts.setup_monitoring import HealthcheckMonitor
monitor = HealthcheckMonitor()
monitor.ping_start()
monitor.ping_success()
print('✅ Healthcheck integration working!')
"
```

### 5. Verify in Dashboard

1. Go back to healthchecks.io
2. You should see:
   - ✅ Last ping: just now
   - ✅ Status: Up
   - 📊 Ping log with "start" and success events

## How It Works

### Scheduled Orchestrator Integration

The scheduled workflow (.github/workflows/scheduled-orchestrator.yml) will:

1. **On start**: Ping `/start` endpoint
2. **On success**: Ping main URL
3. **On failure**: Ping `/fail` endpoint with error details

### Expected Behavior

**Normal operation**:
- Daily at 2 AM UTC: Orchestrator runs
- Healthcheck receives success ping
- Status shows "Up"
- No alerts sent

**Failure scenario**:
- Orchestrator doesn't run or fails
- No success ping received within grace period (1 hour)
- Healthchecks.io marks as "Down"
- **Alert sent** to configured channels (email, Slack, etc.)

## Notification Channels

Configure in healthchecks.io → Integrations:

### Email (included in free tier)
- ✅ Already configured with signup email
- Add more: Settings → Email Addresses

### Slack (recommended)
1. Integrations → Add Integration → Slack
2. Click "Add to Slack"
3. Select channel (e.g., #alerts, #automation)
4. Test with "Send Test Notification"

### Other Channels
- PagerDuty
- OpsGenie  
- Discord
- Webhook (custom)
- Telegram
- Microsoft Teams

## Monitoring Best Practices

### 1. Set Appropriate Timeouts
- **Grace Period**: Time before alert (1 hour recommended)
- **Timeout**: Max execution time (12 hours for orchestrator)

### 2. Use Meaningful Names
- Good: "MASTER_SPLINTER Daily Orchestrator"
- Bad: "Check 1"

### 3. Add Tags
- `automation`
- `critical`
- `master-splinter`
- `daily`

### 4. Test Regularly
```powershell
# Manually trigger scheduled workflow
gh workflow run scheduled-orchestrator.yml
```

### 5. Review Ping History
- Check dashboard weekly
- Look for patterns (consistent timing?)
- Investigate missed pings

## Troubleshooting

### Issue: Ping not received
**Symptoms**: No activity in healthchecks.io dashboard

**Solutions**:
1. Verify HEALTHCHECK_URL is set in GitHub Secrets
2. Check workflow logs: GitHub → Actions → Scheduled Orchestrator
3. Ensure curl command in workflow has correct URL
4. Test locally with above PowerShell command

### Issue: False alarms (Down when actually running)
**Symptoms**: Alert emails but orchestrator completed successfully

**Solutions**:
1. Increase grace period (e.g., 2 hours instead of 1)
2. Check if workflow is actually completing (GitHub Actions logs)
3. Verify success ping is being sent (check workflow logs for curl output)

### Issue: Environment variable not available
**Symptoms**: HealthcheckMonitor.enabled is False

**Solutions**:
```powershell
# Check if set
$env:HEALTHCHECK_URL

# Set for current session
$env:HEALTHCHECK_URL = "https://hc-ping.com/YOUR-UUID"

# Set permanently (Windows)
[System.Environment]::SetEnvironmentVariable('HEALTHCHECK_URL', 'https://hc-ping.com/YOUR-UUID', 'User')
```

## Integration with Other Scripts

Any script can use the monitor:

```python
from scripts.setup_monitoring import HealthcheckMonitor

monitor = HealthcheckMonitor()

monitor.ping_start()

try:
    # Your script logic here
    run_orchestrator()
    monitor.ping_success()
except Exception as e:
    monitor.ping_failure(str(e))
    raise
```

## Cost & Limits

**Free Tier**:
- 20 checks
- 100 pings/day
- Email notifications
- 7-day ping history

**Current Usage**:
- MASTER_SPLINTER Orchestrator: 1 check
- Daily pings: ~3/day (start, success, and health check)
- Well within limits ✅

**Upgrade** (optional):
- $7/month: 100 checks, unlimited pings, SMS
- $20/month: Unlimited checks, phone calls, longer history

## Security Notes

✅ **Ping URLs are secret**: Treat like passwords  
✅ **Use GitHub Secrets**: Never commit HEALTHCHECK_URL to code  
✅ **Read-only**: Ping URLs can only send data, not read or modify  
✅ **Revocable**: Can regenerate URL if compromised  

## Status

- [x] Account created
- [ ] MASTER_SPLINTER check configured
- [ ] GitHub Secret added
- [ ] Test ping successful
- [ ] Notifications configured
- [ ] First automated run verified

---

**Setup Time**: ~5 minutes  
**Maintenance**: Zero (fully automated)  
**Value**: Instant notification of automation failures  
**Cost**: Free

For issues: https://healthchecks.io/docs/
