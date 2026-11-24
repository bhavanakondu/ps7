# Copyright 2026 Bhavana Kondu

import re
import sys
from datetime import datetime
from pathlib import Path

BOOT_START = re.compile(
    r"(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(?:\.\d+)?\s*:\s*"
    r"\(log\.c\.166\)\s*server started\b"
)
BOOT_COMPLETE = re.compile(
    r"(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(?:\.\d+)?\s*:\s*"
    r"INFO:oejs\.AbstractConnector:Started SelectChannelConnector"
)


def main():
    if len(sys.argv) != 2:
        print("Usage: python ps7.py <log_file>", file=sys.stderr)
        return 1

    input_file = Path(sys.argv[1])
    if not input_file.is_file():
        print(f"Input file not found: {input_file}", file=sys.stderr)
        return 1

    boots = []
    current_boot = None

    try:
        with input_file.open("r", encoding="utf-8", errors="replace") as log_file:
            for line_number, line in enumerate(log_file, start=1):
                start = BOOT_START.search(line)
                if start:
                    current_boot = {
                        "line": line_number,
                        "time": datetime.strptime(
                            start.group("time"), "%Y-%m-%d %H:%M:%S"
                        ),
                    }
                    boots.append(current_boot)
                    continue

                complete = BOOT_COMPLETE.search(line)
                if complete and current_boot is not None:
                    current_boot["complete_line"] = line_number
                    current_boot["complete_time"] = datetime.strptime(
                        complete.group("time"), "%Y-%m-%d %H:%M:%S"
                    )
                    current_boot = None

        report = []
        for boot in boots:
            report.append("=== Device boot ===")
            report.append(
                f'{boot["line"]}({input_file.name}): '
                f'{boot["time"]:%Y-%m-%d %H:%M:%S} Boot Start'
            )
            if "complete_line" in boot:
                report.append(
                    f'{boot["complete_line"]}({input_file.name}): '
                    f'{boot["complete_time"]:%Y-%m-%d %H:%M:%S} Boot Completed'
                )
                elapsed = int(
                    (boot["complete_time"] - boot["time"]).total_seconds() * 1000
                )
                report.append(f"\tBoot Time: {elapsed}ms")
            else:
                report.append("**** Incomplete boot ****")
            report.append("")

        output_file = Path(str(input_file) + ".rpt")
        output_file.write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")
    except (OSError, ValueError) as error:
        print(f"ps7: {error}", file=sys.stderr)
        return 1

    print(f"Report written to {output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
