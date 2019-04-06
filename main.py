from src.src import extract_data, re_list
from utils import get_json_data, json_to_fpdf
import json
import os
import pypdftk2

SRC_DIR = os.path.join(os.getcwd(), "src")
DATA_DIR = os.path.join(os.getcwd(), os.pardir, "data")


def get_ticket():

    ticket_path = os.path.join(DATA_DIR, "ticket3_ocr.json")

    with open(ticket_path, 'r') as f:
        ticket_json = json.load(f)
    # ticket_json = json.load(open(ticket_path, "r"))

    return ticket_json


def create_user_dir(user_id):

    dir_path = os.path.join(DATA_DIR, "users", user_id)
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)

    assert os.path.isdir(dir_path)


def db_fill_form():

    # Read ticket info
    ticket_json = get_ticket()
    recognition_result = ticket_json["recognitionResult"]
    lines = recognition_result["lines"]
    BB_KEY = "boundingBox"
    all_texts = [line["text"] for line in lines]
    extracted_data = extract_data(all_texts, re_list)

    # Define PDF files
    form_de = os.path.join(DATA_DIR, "form_de.pdf")
    temp_file = os.path.join(DATA_DIR, "temp_fpdf")
    output_pdf = os.path.join(DATA_DIR, "output.pdf")

    # Get key mappings
    mapping = get_json_data("mapping.json")

    # Map ticket values to form keys
    data = json_to_fpdf(mapping, extracted_data)

    # Fill form and generate PDF
    generated_pdf = pypdftk2.fill_form_v2(form_de, data, temp_file, output_pdf)
    out_pdf = pypdftk2.concat([output_pdf, generated_pdf])


# if __name__ == '__main__':
#     db_fill_form()
