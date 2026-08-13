# Goal of this script is to parse a log file in order to detect client ip addesses that 
# are getting a number of authorization error (401, 403, 404) major then a threshold. 
# Supposing log file format is like the following: ipaddress  datetime  requestmethodurl response code useragent.
import argparse

def detect_client_ip(file_path, threshold = 5):
    result = {} # key is the ip address, value is the number of times that ip address triggered that error class
    with open(file_path,"r") as file:
        for line in file:
            parts = line.split(sep = ", ")
            if len(parts) < 5:
                continue #skip lines if they don't have exactly 5 parts as written upper

            http_response_code = parts[3]            
            if http_response_code in ["401", "403", "404"]:  # check that line contains error script is looking for
                ip_address = parts[0]  # assuming the first part is the ip address
                if ip_address in result:
                    result[ip_address] += 1
                else:
                    result[ip_address] = 1
    # Select only those those keys whose value is greater than the threshold
    final_result = {}
    for ip in result.keys():
        if result[ip] > threshold:
            final_result[ip] = result[ip]
    return final_result

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Detect client IP addresses with  a number of authorization errors major than threshold.")
        parser.add_argument("--file_path", required=True, help="Path to the log file")
        parser.add_argument("--threshold", type=int, default=5, help="Threshold for number of errors")
        args = parser.parse_args()

        print(detect_client_ip(args.file_path, args.threshold))
    except FileNotFoundError as e:
        print("File not found:" + str(e))
    except Exception as e:
        print("An error occurred:" + str(e))