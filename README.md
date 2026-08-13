# System Utilities
Scripts to automate routine system tasks. See the table for details.

## Included Scripts

| Script | Description | Input | Output |
| :--- | :--- | :--- | :--- |
| `tail_f.py` | File monitoring | Filepath, Time | Periodically, it prints added content |
| `disk_usage_alert.py` | Checks storage | Path, Threshold | It prints a warning if storage >= threshold |
| `syslog_parsing.py` | Log parsing looking for log level | Filepath | It prints number of occurences per log level (ERROR, WARNING, INFO) |
| `detect_client_ip.py` | Detects client IP addresses with  a number of authorization errors major than threshold. | Filepath, Threshold (default = 5) | Returns ip addresses with authorization errors > threshold|

## How to execute
Download and run `py .\scripts\script_name.py --placeholder_arg1 value --placeholder_arg2 value` replacing placeholders with correct values