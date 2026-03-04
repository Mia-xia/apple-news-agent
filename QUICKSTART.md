# Quick Start Guide - 5 Minutes

## Step 1: Install and Configure (2 min)

```bash
cd ~/apple-news-agent
python3 agent.py --test
```

This will:
- ✅ Verify Python is installed
- ✅ Fetch Apple news from RSS feeds (no API key needed!)
- ✅ Generate a sample briefing (Chinese格式) in `test_briefing.md`

**Result:** You should see "Successfully fetched X items" in your terminal.

By default the agent generates a Chinese “Apple热点速览” bulletin. To switch languages, set `LANGUAGE=en` in `.env`.

## Step 2: Set Up Email (1 min) - Optional

If you want daily email delivery:

1. Open `.env` in your editor:
   ```bash
   nano .env
   ```

2. For Gmail:
   - Enable 2-Factor Authentication
   - Generate App Password (16 characters)
   - Add to `.env`:
     ```
     EMAIL_SENDER=your-email@gmail.com
     EMAIL_PASSWORD=your_16_char_password
     EMAIL_RECIPIENTS=boss@company.com,colleague@company.com
     ```

3. Save and exit

## Step 3: Test Email (1 min)

```bash
python3 agent.py --once
```

Check your inbox! (and spam folder)

## Step 4: Schedule (1 min)

### macOS - Using LaunchAgent

```bash
# Create folder
mkdir -p ~/Library/LaunchAgents

# Create the plist file
cat > ~/Library/LaunchAgents/com.apple.news.agent.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.apple.news.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/$(whoami)/apple-news-agent/agent.py</string>
        <string>--once</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Hour</key>
            <integer>9</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
    </array>
    <key>StandardErrorPath</key>
    <string>/Users/$(whoami)/apple-news-agent/logs/error.log</string>
    <key>StandardOutPath</key>
    <string>/Users/$(whoami)/apple-news-agent/logs/output.log</string>
</dict>
</plist>
EOF

# Load the agent
launchctl load ~/Library/LaunchAgents/com.apple.news.agent.plist

# Verify it's running
launchctl list | grep apple.news.agent
```

**Runs daily at 9:00 AM UTC**

### Linux - Using Cron

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 9:00 AM):
0 9 * * * cd /path/to/apple-news-agent && python3 agent.py --once
```

### Windows - Using Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 9:00 AM
4. Set action: `python3 agent.py --once`
5. Set working directory: `C:\path\to\apple-news-agent`

## Done! 🎉

Your Apple News Agent is now:
- ✅ Monitoring RSS feeds automatically
- ✅ Fetching latest Apple news daily
- ✅ Sending formatted briefings to your inbox
- ✅ Running on schedule

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No emails sent | Check `.env` credentials, verify Gmail app password is 16 chars |
| "No module" error | Run: `pip3 install -r requirements.txt` |
| No news items | Check internet connection, verify RSS feed URLs |
| Wrong time | Check TIMEZONE in `.env` and system timezone |

## Next: Customize

Want more? Add to your `.env`:
1. **NewsAPI key** - Expands sources to 40,000+ outlets
2. **Twitter API** - Monitor trending Apple discussions
3. **Slack webhook** - Deliver to team Slack channel

See [README.md](README.md) for full setup instructions.

## Logs

Monitor what the agent is doing:

```bash
# Real-time logs
tail -f apple_news_agent.log

# Last 50 lines
tail -50 apple_news_agent.log

# Search for errors
grep ERROR apple_news_agent.log
```

---

**Questions?** Check README.md or review the agent logs for detailed error messages.
