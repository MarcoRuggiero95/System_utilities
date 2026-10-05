DETECT CLIENT IP
In this section, i want to write specifications related to detect_client_ip script for my agent. <br>

detect_client_ip file must read containing records in key-value format and identify clients generating a high number of HTTP client errors, from 400 to 499 (first and last included).  

SCRIPT INPUT
Each line of the input file represents one record in key-value Logfmt format.
The following an example of valid input line: 

ip=10.0.0.15 timestamp=04/Jun/2026:22:48:13 method=GET path=/v1/login http_status=404 request_id=3245
PARSER OUTPUT
Each item of the parsed collection is a dictionary with the following fields:
- ip 
- timestamp
- method
- path 
- http_status
- request_id

Therefore, each key-value line of the file must be validate in order to verify: a line from the input is counted as valid only if all required fields are present and valid. Required fields must be valid according to their own semantic: eg a valid ip. 
When a line overcomes the previous checks, a parse() function must parse it and add it to the collection: parse() should only operate on an already-validated line.

SCRIPT OUTPUT
The collection is then scanned by detect_client_ip function. This one saves in a collection the ips which have a number of client error bigger or equal than a threshold. These items must be sorted in descending order. Then top N ips with most number of errors are printed. also numeber of errors associated to the selected ip must be printed. 

LINES NOT RESPECTING THE FORMAT
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

CONFIGURATION
The following parameters must be configurable: 
- path to the log file 
- threshold: mimimum number of client errors required for an IP to be selected, default 1
- N: maximum number of IP addresses to print, default 1
Validation rules for the configuration parameters:
- threshold: non negative, it applies to valid lines. 
- path to the log file: it mus t be an existing path
- N: bigger or equal 1