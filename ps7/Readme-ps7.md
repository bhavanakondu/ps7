# PS7 Kronos Time Clock

## Contact

- Name: [enter your name]
- Section: [enter your section]
- Time to Complete: [enter your estimate]

## Description

`ps7.py` scans a Kronos InTouch log and writes a report named after the input
with `.rpt` appended. It lists each boot attempt, its start and completion
lines and timestamps, elapsed boot time, and incomplete boots. It also reports
service start/completion lines and service durations.

## Features

- Reads the log sequentially and pairs each `server started` event with the
  next connector-start event.
- Marks a boot incomplete if another boot starts first or the log ends before
  the connector-start event.
- Prints a summary with the number of initiated and completed boots.
- Tracks service starts and successful completions from a boot start until the
  next boot start, including services logged after connector startup and
  services that did not start or complete.
- Uses only the Python standard library.

## Approach

The program keeps at most one boot attempt active while scanning the log. A
second start closes the previous attempt as incomplete if it has no connector
completion; a connector-start event completes the active attempt. Service
events remain associated with that boot until the next boot start. It then
formats the captured line numbers, timestamps, and service events using the
supplied sample report as a guide.

The provided files are copied under `project-materials` so the originals in
`references` remain untouched. Reports are written next to the copied input
log. The program refuses to write a report inside the original `references`
folder.

## Regex

- The boot-start expression finds an ISO date/time followed by
  `(log.c.166) server started`.
- The completion expression finds an ISO date/time followed by
  `oejs.AbstractConnector:Started SelectChannelConnector`.
- The service expressions capture the service name and version from
  `Starting Service.` and `Service started successfully.` lines. The latter
  also captures the duration in milliseconds when present.

## Time

Boot timestamps are parsed to whole-second precision to match the supplied
sample reports, which omit fractional seconds. Boot duration is the difference
between the parsed start and completion timestamps. Service durations are read
from the elapsed-millisecond value logged by the service itself.

## Issues

The supplied logs contain ordinary syslog lines as well as timestamped boot
events and service messages. The parser only treats lines matching the
documented boot markers as boot boundaries; other log lines are ignored for
boot pairing.

## Extra Credit

The report includes a boot-count summary and service-level start/completion
line numbers and elapsed times, with explicit placeholders for missing service
events.

## Acknowledgements

The PS7 assignment brief and the supplied Kronos InTouch logs and sample
reports.

## Running

From the submission directory (the `ps7` subfolder):

```powershell
Set-Location ps7
python ps7.py "project-materials\ps7 sir instrctions\logs\logs\device5_intouch.log"
```

The report is written next to the input file as
`device5_intouch.log.rpt`. The Python assignment option does not require a
Makefile; Gradescope supplies one.
