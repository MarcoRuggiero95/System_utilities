# A script that reads a log file (like /var/log/syslog format)
# and prints the count of lines per log level (ERROR, WARNING, INFO).

import argparse
import re 

def parse_log_levels(file_path):

    result = {"ERROR":0, "WARNING":0, "INFO":0}

    pattern = re.compile(r"\b(ERROR|WARNING|INFO)\b")
    # so, at first i want to check whether the file exists or not. if it exixts, i'll continue. otherwise scripts prints an error message and exits. 
                   
    # Try to open the file
    with open(file_path, 'r') as file:
        # Since file exists, it is time to read it and check every line.
        # Idea is not to read the whole file, as it would be loaded in memory. 
        # File is then looped line by line.
        for line in file:
            match = pattern.search(line)
            if match:
                log_level = match.group(1)
                result[log_level] += 1
        return result

if __name__=="__main__":

    parser = argparse.ArgumentParser(description="A script that parses a log file and counts lines per log level.")
    
    # Arguments to accept
    parser.add_argument("-f", "--file", required=True, help="The path to the log file.")
    
    # Parse the arguments from the command line
    args = parser.parse_args() 

    try:
        result = parse_log_levels(args.file)
        print("Log level counts: "+ str(result))
    except FileNotFoundError:
        print("File does not exist")
    except PermissionError:
        print("Permission denied to read the file")