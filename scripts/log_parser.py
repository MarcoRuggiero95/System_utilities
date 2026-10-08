import ipaddress
import shlex
from datetime import datetime
from pathlib import Path
from typing import TypeAlias

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

Record: TypeAlias = dict[str, str | int | dict[str, str]]


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

        for character in value:
            is_alphanumeric = character.isalnum()
            is_allowed_punctuation = character in HTTP_TOKEN_PUNCTUATION
            if not is_alphanumeric and not is_allowed_punctuation:
                return False
        return True
    if name == "path":
        return value.startswith("/")
    if name == "http_status":
        has_three_digits = len(value) == 3
        contains_ascii_digits = value.isascii() and value.isdigit()
        if not has_three_digits or not contains_ascii_digits:
            return False

        status_number = int(value)
        return 100 <= status_number <= 599
    if name == "request_id":
        has_request_id = bool(value)
        is_ascii = value.isascii()
        if not has_request_id or not is_ascii:
            return False

        for character in value:
            if not character.isalnum():
                return False
        return True
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


def _parse(fields: dict[str, str]) -> Record:
    """Build a record from fields already accepted by _validate_line()."""
    status_number = int(fields["http_status"])
    return {
        "ip": fields["ip"],
        "timestamp": fields["timestamp"],
        "method": fields["method"],
        "path": fields["path"],
        "http_status": status_number,
        "request_id": fields["request_id"],
        "extra": {
            field_name: field_value
            for field_name, field_value in fields.items()
            if field_name not in REQUIRED_FIELDS
        },
    }


def read_log_file(file_path: str | Path) -> tuple[list[Record], dict[str, int]]:
    """Parse valid logfmt records and return counts for invalid entries."""
    records: list[Record] = []
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