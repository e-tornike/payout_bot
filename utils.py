import json
import yaml
import os


def load_telegram_token():
    with open("config.yaml", 'r') as stream:
        try:
            token = yaml.safe_load(stream)
            return token['TOKEN']
        except yaml.YAMLError as exc:
            raise


def get_json_data(json_path):
    with open(json_path) as f:
        data = json.load(f)
    return data


def json_to_fpdf(mapping, extracted_data):

    form_data = {}

    for k, v in extracted_data.items():
        form_data[mapping[k]] = v

    return form_data


