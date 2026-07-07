.RECIPEPREFIX := >
.PHONY: test run generate-sample clean-outputs clean

test:
>python -m pytest tests -q

run:
>uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

generate-sample:
>python -m engine.generate_sample

clean-outputs:
>rm -rf outputs/*

clean: clean-outputs
