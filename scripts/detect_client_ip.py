# detect_client_ip file must read containing records in key-value format and identify clients
# generating a high number of HTTP client errors, from 400 to 499
import argparse
import ipaddress
import shlex
from datetime import datetime
from pathlib import Path
from typing import Iterable

# Fields required in each log entry
REQUIRED_FIELDS = (
    "ip",
    "timestamp",
    "method",
    "path",
    "http_status",
    "request_id",
)
MONTHS = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
)
HTTP_TOKEN_PUNCTUATION = "!#$%&'*+-.^_`|~"


def _read_logfmt(line: str) -> tuple[dict[str, str], bool]:
    fields: dict[str, str] = {}
    malformed = False
    try:
        tokens = shlex.split(line, comments=False, posix=True)
    except ValueError:
        return fields, True

     
    for token in tokens:
        field_name, separator, field_value = token.partition("=")
        has_equals_sign = bool(separator)
        has_field_name = bool(field_name)
        is_duplicate_field = field_name in fields

        if not has_equals_sign or not has_field_name or is_duplicate_field:
            malformed = True
            continue
        fields[field_name] = field_value
    return fields, malformed


def _is_valid_field(name: str, value: str) -> bool:
    if name == "ip":
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False
    if name == "timestamp":
        has_expected_length = len(value) == 20
        if not has_expected_length:
            return False

        has_expected_separators = (
            value[2] == "/"
            and value[6] == "/"
            and value[11] == ":"
            and value[14] == ":"
            and value[17] == ":"
        )
        if not has_expected_separators:
            return False

        day_text = value[:2]
        month_text = value[3:6]
        year_text = value[7:11]
        hour_text = value[12:14]
        minute_text = value[15:17]
        second_text = value[18:20]
        numeric_parts = (day_text, year_text, hour_text, minute_text, second_text)

        all_parts_are_ascii_digits = all(
            part.isascii() and part.isdigit() for part in numeric_parts
        )
        if not all_parts_are_ascii_digits:
            return False

        try:
            month_number = MONTHS.index(month_text) + 1
            datetime(
                int(year_text),
                month_number,
                int(day_text),
                int(hour_text),
                int(minute_text),
                int(second_text),
            )
            return True
        except ValueError:
            return False
    if name == "method":
        has_method_name = bool(value)
        is_ascii = value.isascii()
        if not has_method_name or not is_ascii:
            return False

        is_valid_method = True
        for character in value:
            is_alphanumeric = character.isalnum()
            is_allowed_punctuation = character in HTTP_TOKEN_PUNCTUATION
            if not is_alphanumeric and not is_allowed_punctuation:
                is_valid_method = False
                break
        return is_valid_method
    if name == "path":
        starts_with_slash = value.startswith("/")
        return starts_with_slash
    if name == "http_status":
        has_three_digits = len(value) == 3
        contains_ascii_digits = value.isascii() and value.isdigit()
        if not has_three_digits or not contains_ascii_digits:
            return False

        status_number = int(value)
        is_valid_status = 100 <= status_number <= 599
        return is_valid_status
    if name == "request_id":
        has_request_id = bool(value)
        is_ascii = value.isascii()
        if not has_request_id or not is_ascii:
            return False

        is_valid_request_id = True
        for character in value:
            if not character.isalnum():
                is_valid_request_id = False
                break
        return is_valid_request_id
    return True


def _validate_line(line: str) -> tuple[dict[str, str], set[str], set[str]]:
    """Return parsed fields and the missing and malformed field names."""
    fields, malformed_logfmt = _read_logfmt(line)
    missing_fields = set(REQUIRED_FIELDS) - fields.keys()
    malformed_fields = set()

    for field_name in REQUIRED_FIELDS:
        if field_name not in fields:
            continue

        field_value = fields[field_name]
        is_valid = _is_valid_field(field_name, field_value)
        if not is_valid:
            malformed_fields.add(field_name)

    if malformed_logfmt:
        malformed_fields.add("logfmt")

    return fields, missing_fields, malformed_fields


def _parse(fields: dict[str, str]) -> dict[str, str | int]:
    """Build a record from fields already accepted by _validate_line()."""
    status_number = int(fields["http_status"])
    return {
        "ip": fields["ip"],
        "timestamp": fields["timestamp"],
        "method": fields["method"],
        "path": fields["path"],
        "http_status": status_number,
        "request_id": fields["request_id"],
    }


def _read_log_file(file_path: str | Path) -> tuple[list[dict[str, str | int]], dict[str, int]]:
    records: list[dict[str, str | int]] = []
    stats = {
        "total_entries": 0,
        "missing_field_entries": 0,
        "malformed_entries": 0,
    }

    with Path(file_path).open("r", encoding="utf-8") as log_file:
        for line in log_file:
            stats["total_entries"] += 1
            fields, missing, malformed = _validate_line(line)
            if missing:
                stats["missing_field_entries"] += 1
            if malformed:
                stats["malformed_entries"] += 1
            if missing or malformed:
                continue
            records.append(_parse(fields))
    return records, stats


def _ip_error_sort_key(ip_result: tuple[str, int]) -> tuple[int, str]:
    ip_address, error_count = ip_result
    return -error_count, ip_address


def detect_client_ip(
    records: Iterable[dict[str, str | int]], threshold: int = 1, top_n: int = 1
) -> dict[str, int]:
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    if top_n < 1:
        raise ValueError("top_n must be at least 1")

    error_counts: dict[str, int] = {}
    for record in records:
        ip_address = ipaddress.ip_address(str(record["ip"])).compressed
        if ip_address not in error_counts:
            error_counts[ip_address] = 0

        status = int(record["http_status"])
        is_client_error = 400 <= status <= 499
        if is_client_error:
            error_counts[ip_address] += 1

    selected_ips = []
    for ip_address, error_count in error_counts.items():
        meets_threshold = error_count >= threshold
        if meets_threshold:
            selected_ips.append((ip_address, error_count))

    selected_ips.sort(key=_ip_error_sort_key)

    top_ips = selected_ips[:top_n]
    return dict(top_ips)


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
        type=_non_negative_integer,
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

    records, stats = _read_log_file(args.file_path)
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