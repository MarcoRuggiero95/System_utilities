# detect_client_ip file must read containing records in key-value format and identify clients
# generating a high number of HTTP client errors, from 400 to 499
import argparse
import ipaddress
from pathlib import Path
from typing import Iterable
from log_parser import Record, read_log_file

# Outputs the top n client IP addresses that at least meet the error threshold
def detect_client_ip(
    records: Iterable[Record], threshold: int = 1, top_n: int = 1
) -> dict[str, int]:
    if threshold < 1:
        raise ValueError("threshold must be at least 1")
    if top_n < 1:
        raise ValueError("top_n must be at least 1")

    error_counts: dict[str, int] = {}
    for record in records:
        status = int(record["http_status"])
        is_client_error = 400 <= status <= 499
        if is_client_error:
            ip_address = ipaddress.ip_address(str(record["ip"])).compressed
            error_counts[ip_address] = error_counts.get(ip_address, 0) + 1

    selected_ips = []
    for ip_address, error_count in error_counts.items():
        meets_threshold = error_count >= threshold
        if meets_threshold:
            selected_ips.append((ip_address, error_count))

    selected_ips.sort(key=_ip_error_sort_key)

    top_ips = selected_ips[:top_n]
    return dict(top_ips)

def _ip_error_sort_key(ip_result: tuple[str, int]) -> tuple[int, str]:
    ip_address, error_count = ip_result
    return -error_count, ip_address

def _existing_file(value: str) -> str:
    path = Path(value)
    if not path.is_file():
        raise argparse.ArgumentTypeError("must be an existing file")
    return value

def _non_negative_integer(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error
    if number < 0:
        raise argparse.ArgumentTypeError("must be non-negative")
    return number


def _positive_integer(value: str) -> int:
    number = _non_negative_integer(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find client IP addresses generating frequent HTTP 4xx errors."
    )
    parser.add_argument(
        "-f",
        "--file_path",
        "--file-path",
        required=True,
        type=_existing_file,
        help="Path to the log file",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        type=_positive_integer,
        default=1,
        help="Minimum number of 4xx errors required (default: 1)",
    )
    parser.add_argument(
        "-n",
        "--top_n",
        "--top-n",
        type=_positive_integer,
        default=1,
        help="Maximum number of IP addresses to print (default: 1)",
    )
    args = parser.parse_args()

    records, stats = read_log_file(args.file_path)
    results = detect_client_ip(records, args.threshold, args.top_n)
    print(f"Total entries: {stats['total_entries']}")
    print(f"Entries with missing fields: {stats['missing_field_entries']}")
    print(f"Malformed entries: {stats['malformed_entries']}")
    print("Top client IPs:")
    if results:
        for ip_address, error_count in results.items():
            print(f"{ip_address}: {error_count}")
    else:
        print("No IP addresses met the threshold.")