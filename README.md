# System Utilities
Scripts to automate routine system tasks. See the table for details.

## Included Scripts

| Script | Description | Input | Output |
| :--- | :--- | :--- | :--- |
| `tail_f.py` | Monitors a file for appended content, starting at the current end of the file | File path (required), polling interval in seconds (default: 3) | Prints new content as it is appended; stop with `Ctrl+C` |
| `disk_usage_alert.py` | Checks disk usage for a path (default: `/`) against a percentage threshold (default: 80) | `--path`, `--threshold` (0-100) | Prints a warning when usage is greater than or equal to the threshold |
| `detect_client_ip.py` | Counts HTTP client errors (status 400-499) per IP and selects the top results meeting the threshold | Log file (required), `--threshold` (default: 1), `--top-n` (default: 1) | Prints entry validation counts and matching IP addresses with their 4xx error counts |

## How to execute
Run scripts from the repository root with `py .\scripts\script_name.py`. For example:

```powershell
# Monitor appended lines; poll every 3 seconds by default
py .\scripts\tail_f.py --file-path .\app.log --time-to-wait 3

# Warn when the disk containing the given path is at least 80% full
py .\scripts\disk_usage_alert.py --path C:\ --threshold 80

# Show up to 5 IPs with at least 3 HTTP 4xx responses
py .\scripts\detect_client_ip.py --file-path .\access.log --threshold 3 --top-n 5
```

`detect_client_ip.py` expects one logfmt record per line with `ip`, `timestamp`, `method`, `path`, `http_status`, and `request_id` fields. Malformed records and records missing required fields are excluded from the results and included in the printed validation counts. 