# System Utilities
Scripts to automate routine system tasks. See the table for details.

## Included Scripts

| Script | Description | Input | Output |
| :--- | :--- | :--- | :--- |
| `tail_f.py` | Displays the last N lines, then monitors one or more files for appended content, replacement, and truncation | File path(s) (required), `--lines` (default: 0), `--time-to-wait` (required, greater than 0) | Prints initial and appended content with file headers; stop with `Ctrl+C` |
| `disk_usage_alert.py` | Checks disk usage for a path (default: `/`) against a percentage threshold (default: 80) | `--path`, `--threshold` (0-100) | Prints a warning when usage is greater than or equal to the threshold |
| `detect_client_ip.py` | Counts HTTP client errors (status 400-499) per IP and selects the top results meeting the threshold | Log file (required), `--threshold` (default: 1), `--top-n` (default: 1) | Prints entry validation counts and matching IP addresses with their 4xx error counts |
| `process_finder.py` | Finds running processes by exact name | `--process-name` (required) | Prints each matching process PID and memory usage, or a message if there are no matches |

## How to execute
Run scripts from the repository root with `py .\scripts\script_name.py`. For example:

```powershell
# Show the last 10 lines, then poll one or more files every 0.5 seconds
py .\scripts\tail_f.py --file-path .\app.log --lines 10 --time-to-wait 0.5
py .\scripts\tail_f.py --file-path .\app.log .\worker.log --time-to-wait 0.5

# Warn when the disk containing the given path is at least 80% full
py .\scripts\disk_usage_alert.py --path C:\ --threshold 80

# Show up to 5 IPs with at least 3 HTTP 4xx responses
py .\scripts\detect_client_ip.py --file-path .\access.log --threshold 3 --top-n 5

# Find running PowerShell processes and display their PIDs and memory usage
py .\scripts\process_finder.py --process-name powershell.exe
```

`detect_client_ip.py` expects one logfmt record per line with `ip`, `timestamp`, `method`, `path`, `http_status`, and `request_id` fields. Malformed records and records missing required fields are excluded from the results and included in the printed validation counts. 