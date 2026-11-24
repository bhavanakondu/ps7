# PS7: Kronos Log Parsing

## Contact

Name: Bhavana Kondu
Section: 201
Time to Complete: 2 days

## Description

I wrote a Python program that reads a Kronos InTouch log and writes a `.rpt`
file listing each device boot, its completion status, and its duration.

### Features

The report includes a boot summary and each boot's start and completion line
numbers and timestamps. An attempt is incomplete if another boot starts first
or the log ends before boot completion.

### Approach

I read the log one line at a time, match each boot start with its completion,
and use `datetime` to calculate the elapsed time.

### Regex

One regular expression matches the timestamp and `(log.c.166) server started`
message. Another matches the connector-start message that marks boot completion.

### Issues

Other `server started` messages appear in the logs, so I matched the specific
`log.c.166` message required by the assignment.

### Extra Credit

I included the summary header and boot counts. I did not implement optional
service tracking.

## Acknowledgements

I used the assignment instructions, provided log files, and sample reports.
