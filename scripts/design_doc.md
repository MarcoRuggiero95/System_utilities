## DETECT CLIENT IP

In this section, i want to write specifications related to detect_client_ip script for my agent. <br>

The `log_parser.py` module reads records in key-value format, validates them, and yields parsed records. The `detect_client_ip.py` script consumes those records and identifies clients generating a high number of HTTP client errors, from 400 to 499 (first and last included).

### SCRIPT INPUT

Each line of the input file represents one record in key-value Logfmt format. Parsing and validation are owned by `log_parser.py`; IP error detection is owned by `detect_client_ip.py`.
The following an example of valid input line: 

ip=10.0.0.15 timestamp=04/Jun/2026:22:48:13 method=GET path=/v1/login http_status=404 request_id=3245

### PARSER OUTPUT

Each item of the yielded records is a dictionary with the following fields:
- ip 
- timestamp
- method
- path 
- http_status
- request_id
- extra: a dictionary containing any other key-value fields from the input line

Each input line must be validated before it is counted as a valid record. All required fields must be present and valid according to their meaning, such as a valid IP address.

### FLOW
The instruction flow calls `read_log_file` once to create and return an iterator of records plus a statistics dictionary. Creating the iterator does not read the file; file reading begins when `detect_client_ip` starts iterating over it. `detect_client_ip` is called once, and its `for record in records` loop requests one record at a time. The parser reads and validates lines until it finds a valid one, then `yield` returns that record and pauses the parser. The loop body processes that record; when the loop requests another, the parser resumes immediately after `yield` and continues with the next line. This producer-consumer cycle repeats until the file ends. Invalid lines are skipped and counted, not yielded.  Thus, parsed records are processed one at a time rather than accumulated in memory.

### SCRIPT OUTPUT

Streamed records are then consumed by detect_client_ip function.  This one saves in a collection the distinct ips which have a number of client error bigger or equal than a threshold. In this way, memory usage is proportional to the number of distinct IPs. The items must be sorted in descending order. Then top N ips with most number of errors are printed. Also number of errors associated to the selected ip must be printed. 

### LINES NOT RESPECTING THE FORMAT

For lines which miss a required field or one of them is malformed: it must be tracked the total number of possible entries, the total number of entries with a missing field, the total numbner of malformed lines. 
A line which misses a required field is a line where that attribute is not present. 
A line which malformed fields is a line where one of the fields has at least an invalid value.  
Validation rules for the fields: 
- ip: either ipv4 or ipv6
- timestamp: dd/Mon/yyyy:hh:mm:ss, timezone unspecified
- method: valid http methods like GET, POST and others
- path: starting with /
- http_status: from 100 to 599, extremes inclueded
- request_id: alphanumeric
If a line has a missing or malformedd value, then that line is invalid. 
If an invalid line is met, it is not added given to the parser and processing does not stop. 

### CONFIGURATION

The following parameters must be configurable: 
- path to the log file 
- threshold: mimimum number of client errors required for an IP to be selected, default 1
- N: maximum number of IP addresses to print, default 1
Validation rules for the configuration parameters:
- threshold: bigger or equal 1, it applies to valid lines. 
- path to the log file: it mus t be an existing path
- N: bigger or equal 1