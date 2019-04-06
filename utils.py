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


def make_dir(path):
    if not os.path.isdir(path):
        os.mkdir(path)


def get_json_data(json_path):
    with open(json_path) as f:
        data = json.load(f)
    return data


def json_to_fpdf(mapping, extracted_data):

    form_data = {}

    for k, v in extracted_data.items():
        form_data[mapping[k]] = v

    return form_data


def json_to_fpdf_v2(mapping, extracted_data):

    form_data = {}

    for k, v in extracted_data.items():
        form_data[mapping[k]] = v

    template_path = os.path.join(os.getcwd(), os.pardir, "data", "template.json")
    template_data = get_json_data(template_path)

    # Fill the rest the of the input fields with template data
    for k_2, v_2 in template_data.items():
        # print(k_2, v_2)
        if not k_2 in form_data:
            form_data[k_2] = v_2

    return form_data

