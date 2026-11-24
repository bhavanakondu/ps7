#!/usr/bin/env python3
"""Generate a Kronos InTouch device boot report from a log file."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


TIMESTAMP = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
BOOT_START_RE = re.compile(
    rf"(?P<timestamp>{TIMESTAMP})(?:\.\d+)?\s*:\s*"
    r"\(log\.c\.166\)\s*server started\b"
)
BOOT_COMPLETE_RE = re.compile(
    rf"(?P<timestamp>{TIMESTAMP})(?:\.\d+)?\s*:\s*"
    r"INFO:oejs\.AbstractConnector:Started SelectChannelConnector"
)
SERVICE_START_RE = re.compile(
    r"Starting Service\.\s+(?P<name>.+?)\s+\d+(?:\.\d+)*\s*$",
    re.IGNORECASE,
)
SERVICE_COMPLETE_RE = re.compile(
    r"Service started successfully\.\s+(?P<name>.+?)\s+\d+(?:\.\d+)*"
    r"(?:\s+\((?P<duration>\d+)\s+ms\))?\s*$",
    re.IGNORECASE,
)


@dataclass
class ServiceRun:
    start_line: int | None = None
    completion_line: int | None = None
    elapsed_ms: int | None = None


@dataclass
class Boot:
    start_line: int
    start_time: datetime
    completion_line: int | None = None
    completion_time: datetime | None = None
    services: dict[str, ServiceRun] = field(default_factory=dict)


@dataclass
class LogReport:
    line_count: int
    boots: list[Boot]
    services: list[str]


def parse_timestamp(value: str, line_number: int) -> datetime:
    try:
        # The supplied sample reports use whole-second boot timestamps.
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError as error:
        raise ValueError(
            f"invalid boot timestamp on line {line_number}: {value}"
        ) from error


def analyze_log(input_path: Path) -> LogReport:
    boots: list[Boot] = []
    service_names: list[str] = []
    known_services: set[str] = set()
    active_boot: Boot | None = None
    line_count = 0

    with input_path.open("r", encoding="utf-8", errors="replace") as log_file:
        for line_number, line in enumerate(log_file, start=1):
            line_count = line_number
            start_match = BOOT_START_RE.search(line)
            if start_match:
                # The next start closes the previous boot's service-tracking window.
                active_boot = Boot(
                    start_line=line_number,
                    start_time=parse_timestamp(
                        start_match.group("timestamp"), line_number
                    ),
                )
                boots.append(active_boot)
                continue

            completion_match = BOOT_COMPLETE_RE.search(line)
            if (
                completion_match
                and active_boot is not None
                and active_boot.completion_line is None
            ):
                active_boot.completion_line = line_number
                active_boot.completion_time = parse_timestamp(
                    completion_match.group("timestamp"), line_number
                )
                continue

            if active_boot is None:
                continue

            service_start = SERVICE_START_RE.search(line)
            if service_start:
                service_name = service_start.group("name").strip()
                if service_name not in known_services:
                    known_services.add(service_name)
                    service_names.append(service_name)
                run = active_boot.services.setdefault(service_name, ServiceRun())
                if run.start_line is None:
                    run.start_line = line_number
                continue

            service_completion = SERVICE_COMPLETE_RE.search(line)
            if service_completion:
                service_name = service_completion.group("name").strip()
                if service_name not in known_services:
                    known_services.add(service_name)
                    service_names.append(service_name)
                run = active_boot.services.setdefault(service_name, ServiceRun())
                if run.completion_line is None:
                    run.completion_line = line_number
                    duration = service_completion.group("duration")
                    if duration is not None:
                        run.elapsed_ms = int(duration)

    return LogReport(
        line_count=line_count,
        boots=boots,
        services=service_names,
    )


def line_reference(line_number: int | None, filename: str, missing: str) -> str:
    if line_number is None:
        return f"{missing}({filename})"
    return f"{line_number}({filename})"


def format_report(report: LogReport, filename: str) -> str:
    completed_count = sum(boot.completion_line is not None for boot in report.boots)
    lines = [
        "Device Boot Report",
        "",
        f"InTouch log file: {filename}",
        f"Lines Scanned: {report.line_count}",
        "",
        (
            "Device boot count: initiated = "
            f"{len(report.boots)}, completed: {completed_count}"
        ),
        "",
    ]

    for boot in report.boots:
        lines.extend(
            [
                "=== Device boot ===",
                (
                    f"{boot.start_line}({filename}): "
                    f"{boot.start_time:%Y-%m-%d %H:%M:%S} Boot Start"
                ),
            ]
        )
        if boot.completion_line is not None and boot.completion_time is not None:
            elapsed_ms = int(
                (boot.completion_time - boot.start_time).total_seconds() * 1000
            )
            lines.extend(
                [
                    (
                        f"{boot.completion_line}({filename}): "
                        f"{boot.completion_time:%Y-%m-%d %H:%M:%S} Boot Completed"
                    ),
                    f"\tBoot Time: {elapsed_ms}ms",
                ]
            )
        else:
            lines.append("**** Incomplete boot ****")

        lines.extend(["", "Services"])
        for service_name in report.services:
            service = boot.services.get(service_name, ServiceRun())
            start = line_reference(service.start_line, filename, "Not started")
            completion = line_reference(
                service.completion_line, filename, "Not completed"
            )
            elapsed = (
                f"{service.elapsed_ms} ms" if service.elapsed_ms is not None else ""
            )
            elapsed_line = f"\t\t Elapsed Time: {elapsed}".rstrip()
            lines.extend(
                [
                    f"\t{service_name}",
                    f"\t\t Start: {start}",
                    f"\t\t Completed: {completion}",
                    elapsed_line,
                ]
            )
        lines.append("")

    return "\n".join(lines).rstrip("\n")


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Analyze Kronos InTouch logs and write a boot report."
    )
    parser.add_argument("log_file", type=Path, help="path to the InTouch log file")
    args = parser.parse_args(argv)

    input_path = args.log_file
    if not input_path.is_file():
        parser.error(f"input file does not exist or is not a file: {input_path}")

    project_root = Path(__file__).resolve().parent
    references_dirs = [
        ancestor / "references" for ancestor in (project_root, *project_root.parents)
    ]
    output_path = Path(f"{input_path}.rpt")
    if any(
        is_within(output_path, references_dir) for references_dir in references_dirs
    ):
        parser.error("refusing to write a report inside the untouched references folder")

    try:
        report = analyze_log(input_path)
        output_path.write_text(
            format_report(report, input_path.name) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    except (OSError, ValueError) as error:
        print(f"ps7: {error}", file=sys.stderr)
        return 1

    print(f"Report written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
