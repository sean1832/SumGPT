import json
from io import StringIO


def read_json_file(file):
    with open(file, "r") as f:
        return json.load(f)


def write_json_file(file, data: dict):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


def read_to_string(file):
    stringio = StringIO(file.getvalue().decode("utf-8"))
    return stringio.read()
