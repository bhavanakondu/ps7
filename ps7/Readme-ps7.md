# PS7: Kronos Log Parsing

## Contact

Name: Bhavana Kondu
Section: 201
Time to Complete: 2 days

## Description

I wrote a Python program that reads a Kronos InTouch log and creates a .rpt file listing each boot, whether it completed, and how long it took. It writes the report beside the input log.

### Features

Each boot entry includes its line number and timestamp. The report also shows the log filename, lines scanned, total boot attempts, and completed boots. An attempt is marked incomplete if another boot starts first or the log ends before it completes.

### Approach

I went through each log one line at a time and used regular expressions to find the boot start and completion messages. Then I used Python's datetime module to calculate how long each completed boot took.

### Regex

One regular expression finds the timestamp and the specific log.c.166 server started message. The other finds the connector-start message that marks a completed boot.

### Issues

Some log lines say server started but do not indicate a device boot. I matched the specific log.c.166 message to avoid counting those lines as boot starts.

### Extra Credit

I added a summary header with the log filename, lines scanned, total boot attempts, and completed boots. I did not implement the optional service tracking.

## Acknowledgements

I used the assignment instructions, log files, and sample reports provided by my instructor.
