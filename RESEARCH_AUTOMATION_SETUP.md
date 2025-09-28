# Research Auto-Update Setup Instructions

## Windows Task Scheduler (Recommended for Windows)

1. **Open Task Scheduler** (search "Task Scheduler" in Start menu)
2. **Create Basic Task** > Name: "Pulse Research Update"
3. **Trigger**: Daily at 6:00 AM
4. **Action**: Start a program
   - **Program**: `C:\path\to\your\python.exe`
   - **Arguments**: `C:\Users\Razam\Documents\GitHub\Pulse\automated_research_update.py`
   - **Start in**: `C:\Users\Razam\Documents\GitHub\Pulse`

## PowerShell Script Alternative

Create a PowerShell script to run the update:

```powershell
# research_update.ps1
Set-Location "C:\Users\Razam\Documents\GitHub\Pulse"
python automated_research_update.py
```

Then schedule this script to run daily.

## Manual Update Commands

```bash
# Generate new research content
python manage.py update_research --verbose

# Or run the standalone script
python automated_research_update.py
```

## Environment Variables (Optional)

For enhanced functionality, you can set these environment variables:

```
RESEARCH_UPDATE_FREQUENCY=daily
RESEARCH_LOG_LEVEL=INFO
RESEARCH_MAX_ARTICLES=50
```

## Monitoring Logs

The system logs all activities to:
- `research_update.log` (file)
- Console output

Check these logs to ensure the system is working properly.

## Database Maintenance

The system automatically:
- Removes research older than 30 days
- Updates existing articles if found
- Creates new articles from multiple sources
- Categorizes articles by medical specialty
- Calculates relevance scores

## Integration with External APIs (Future Enhancement)

To enable real web scraping (requires additional setup):

1. Install required packages:
   ```bash
   pip install beautifulsoup4 requests lxml
   ```

2. Update `core/research_scraper.py` imports
3. Configure API keys if needed

## Troubleshooting

Common issues:
- **Django not found**: Ensure the script runs from the project directory
- **Database locked**: Make sure no other Django processes are running
- **Permission errors**: Run with appropriate user permissions
- **Memory issues**: Limit the number of articles processed at once