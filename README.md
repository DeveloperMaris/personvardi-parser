# Personvārdi Parser
A script to parse out information from html page of [Personvārdi DB](https://personvardi.pmlp.gov.lv/index.php)

## Setup

1. Set up virtual environment

```
python -m venv env
```

2. Active environment

```
source env/bin/activate
```

3. Install dependencies

```
python -m pip install -r requirements/base.txt
```

## Run

```
python -m parse.py
```

## Output

The output of the command will produce a `output/results.json` file containing all the information.
