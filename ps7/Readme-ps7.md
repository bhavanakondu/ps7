# PS7: Kronos Log Parsing

## Contact

Name: Bhavana Kondu
Section: 201
Time to Complete: 2 days

## Description

I wrote this program to read a Kronos InTouch log and create a report with
.rpt added to the input filename. It reports when each boot starts, whether it
finishes, and how long it takes. I ran it on all six provided logs.

### Features

I chose Python for this assignment. My program finds boot and service
messages, then includes their line numbers and durations in the report. If
another boot starts before the current one finishes, I mark the earlier boot
as incomplete.

### Approach

I read each log one line at a time and keep track of the current boot. I use
Python's datetime module to calculate boot time to the nearest second, as in
the sample reports. For service times, I use the milliseconds recorded in the
log.

### Regex

I used one regular expression to find the timestamp and log.c.166 server
started message. Another finds the connector-start message that marks a
completed boot. I also used regular expressions to find service start and
completion messages and the service duration when it is included.

### Issues

At first, I matched other server-started messages in the logs and counted too
many boot attempts. I fixed this by matching the required log.c.166 message.
Some boots did not finish, so I reported them as incomplete.

### Extra Credit

I added a summary of the number of boot attempts and completions. The report
also includes service start and completion line numbers and durations.

## Acknowledgements

I used the PS7 assignment instructions and the Kronos log files and sample
reports provided for the assignment.
