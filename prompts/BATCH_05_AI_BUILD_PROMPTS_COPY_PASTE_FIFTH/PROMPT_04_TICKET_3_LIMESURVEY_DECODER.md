Ticket 3: Build the LimeSurvey response decoder.

Input:
- CSV and XLSX batch response files from test_data/

The decoder must:
- detect each organisation row
- read LimeSurvey question-code style columns
- support single-choice answers
- support matrix/subquestion columns
- support multi-select Y/blank columns
- count decoded scored signals
- list unknown fields
- list missing required fields

Hard fail:
If decoded scored signals = 0, stop and return a clear error. Do not generate a report.

Add tests using the 5 dummy test responses.
Run tests.
