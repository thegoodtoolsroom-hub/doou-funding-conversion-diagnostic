Ticket 1: Create the repo scaffold only.

Create this structure:
app/
engine/
templates/
product_lock/
test_data/
tests/
outputs/
docs/

Create setup files:
README.md
requirements.txt or pyproject.toml
Makefile

Add these commands:
make test
make run
make generate-sample
make clean

Do not build the UI yet.
Do not generate reports yet.
After creating the scaffold, run the tests. If there are no tests yet, create one smoke test that proves the repo imports cleanly.
