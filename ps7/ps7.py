# Copyright 2026 Bhavana Kondu

import re
import sys
from datetime import datetime
from pathlib import Path

TIME = r"(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(?:\.\d+)?\s*:\s*"
START = re.compile(TIME + r"\(log\.c\.166\)\s*server started\b")
END = re.compile(TIME + r"INFO:oejs\.AbstractConnector:Started SelectChannelConnector")


def main():
    if len(sys.argv) != 2:
        print("Usage: python ps7.py <log_file>", file=sys.stderr)
        return 1

    log = Path(sys.argv[1])
    boots, active, line_count = [], None, 0

    try:
        with log.open("r", encoding="utf-8", errors="replace") as log_file:
            for line_count, line in enumerate(log_file, 1):
                match = START.search(line)
                if match:
                    active = [line_count, datetime.fromisoformat(match["time"]), None]
                    boots.append(active)
                    continue
                match = END.search(line)
                if match and active is not None:
                    active[2] = (line_count, datetime.fromisoformat(match["time"]))
                    active = None
        completed = sum(boot[2] is not None for boot in boots)
        report = [
            "Device Boot Report", "",
            f"InTouch log file: {log.name}",
            f"Lines Scanned: {line_count}", "",
            f"Device boot count: initiated = {len(boots)}, completed: {completed}", "",
        ]
        for start_line, start_time, end in boots:
            report.extend(["=== Device boot ===",
                           f'{start_line}({log.name}): {start_time:%Y-%m-%d %H:%M:%S} Boot Start'])
            if end:
                end_line, end_time = end
                report.extend([f'{end_line}({log.name}): {end_time:%Y-%m-%d %H:%M:%S} Boot Completed',
                               f"\tBoot Time: {int((end_time - start_time).total_seconds() * 1000)}ms"])
            else:
                report.append("**** Incomplete boot ****")
            report.append("")

        output = Path(str(log) + ".rpt")
        output.write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")
    except (OSError, ValueError) as error:
        print(f"ps7: {error}", file=sys.stderr)
        return 1

    print(f"Report written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
