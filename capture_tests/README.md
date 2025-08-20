
# CBRAIN Client Capture Test Folder

This folder contains the support scripts for running
a special 'capture' test of the "cbrain" client command.

The script "cbrain_cli_commands" contains a bunch of such
commands. They are run one by one by the script "capture_wrapper".
That script carefully logs the return codes, and the standard out
and standard err messages, and provides a report.

That report is compared to an 'expected' report, in file
"expected_captures.txt". The comparison is performed
by the main script, "run_and_diff_captures".

All of this is performed by GitHub actions, as described in
the file .github/workflows/capture_tests.yaml

### Credits

Pierre Rioux <pierre.rioux@mcgill.ca>, July 2025
