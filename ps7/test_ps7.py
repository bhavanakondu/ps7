import tempfile
import unittest
from pathlib import Path

from ps7 import analyze_log, format_report


class AnalyzeLogTests(unittest.TestCase):
    def test_pairs_boots_and_marks_interrupted_boot_incomplete(self):
        contents = "\n".join(
            [
                "2014-01-26 09:55:07: (log.c.166) server started",
                "Starting Service. Logging 1.0",
                "Service started successfully. Logging 1.0 (268 ms)",
                "2014-01-26 09:58:04.362:INFO:oejs.AbstractConnector:Started "
                "SelectChannelConnector@0.0.0.0:9080",
                "Starting Service. LateService 1.0",
                "Service started successfully. LateService 1.0 (12 ms)",
                "2014-01-26 12:15:18: (log.c.166) server started",
                "2014-01-26 12:16:00: (log.c.166) server started",
                "2014-01-26 12:18:03:INFO:oejs.AbstractConnector:Started "
                "SelectChannelConnector@0.0.0.0:9080",
            ]
        )

        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "device.log"
            log_path.write_text(contents, encoding="utf-8")
            report = analyze_log(log_path)

        self.assertEqual(report.line_count, 9)
        self.assertEqual(len(report.boots), 3)
        self.assertEqual(report.boots[0].completion_line, 4)
        self.assertEqual(report.boots[0].services["LateService"].start_line, 5)
        self.assertIsNone(report.boots[1].completion_line)
        self.assertEqual(report.boots[2].completion_line, 9)
        self.assertEqual(report.services, ["Logging", "LateService"])
        self.assertEqual(report.boots[0].services["Logging"].elapsed_ms, 268)

        text = format_report(report, log_path.name)
        self.assertIn("Device boot count: initiated = 3, completed: 2", text)
        self.assertIn("**** Incomplete boot ****", text)
        self.assertIn("Boot Time: 177000ms", text)

    def test_ignores_different_server_started_message(self):
        contents = "\n".join(
            [
                "2014-01-26 09:55:07: (log.c.172) server started",
                "2014-01-26 09:56:07: (log.c.166) server started",
                "2014-01-26 09:58:04:INFO:oejs.AbstractConnector:Started "
                "SelectChannelConnector@0.0.0.0:9080",
            ]
        )

        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "device.log"
            log_path.write_text(contents, encoding="utf-8")
            report = analyze_log(log_path)

        self.assertEqual(len(report.boots), 1)
        self.assertEqual(report.boots[0].start_line, 2)

    def test_end_of_file_leaves_boot_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "unfinished.log"
            log_path.write_text(
                "2014-01-26 12:15:18: (log.c.166) server started\n",
                encoding="utf-8",
            )
            report = analyze_log(log_path)

        self.assertEqual(len(report.boots), 1)
        self.assertIsNone(report.boots[0].completion_line)
        self.assertIn("**** Incomplete boot ****", format_report(report, log_path.name))


if __name__ == "__main__":
    unittest.main()
