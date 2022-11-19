# Personvārdi Parser

A Python script to retrieve and parse information from [Personvārdi DB](https://personvardi.pmlp.gov.lv/index.php)

### Attention
If this script is executed too often, your IP address can get blocked by the host!

## Setup

1. Set up virtual environment

```console
python -m venv env
```

2. Active environment

```console
source env/bin/activate
```

3. Install dependencies

```console
python -m pip install -r requirements/base.txt
```

## Run

```console
python -m parse.py
```

## Input

A json file containing all the names is provided as an input. This file contains a specific structure and is generated with [vardadiena-parser](https://github.com/DeveloperMaris/vardadiena-parser) script.

## Output

The output of the command will produce an `output/personvardi.json` file containing all the information.

### JSON structure

```json
{
    "<name>": {
        "name": String,                     # Person name.
        "count": Int,                       # Count of the registered people with that name.
        "explanation": Optional<String>     # Name explanation, if available.
    }
}
```

## Licence

`personvardi-parser` is released under the MIT License. See [LICENSE](LICENSE) for details.
