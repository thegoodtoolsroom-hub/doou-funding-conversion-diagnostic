BATCH 02 — SURVEY / LIMESURVEY — UPLOAD SECOND

Purpose: This is the survey file that creates respondent data.

Use the .lss file in LimeSurvey:
Surveys > Create new survey > Import > Upload .lss

After import:
1. Open the survey.
2. Check that the questions are readable.
3. Complete 1 manual test response.
4. Export responses as CSV.
5. The app must decode that CSV.

The app must read LimeSurvey exports by question codes, not by guessing long question text.

Tell the AI:
"Build the decoder for this exact LSS/export structure. Fail if zero scored signals are decoded."
