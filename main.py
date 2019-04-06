from src.src import extract_data, re_list
from utils import get_json_data, json_to_fpdf, json_to_fpdf_v2
import json
import os
import pypdftk2

SRC_DIR = os.path.join(os.getcwd(), "src")
DATA_DIR = os.path.join(os.getcwd(), os.pardir, "data")


def get_ticket(user_dir):

    ticket_path = os.path.join(user_dir, "ticket_ocr.json")
    with open(ticket_path, 'r') as f:
        ticket_json = json.load(f)
    # ticket_json = json.load(open(ticket_path, "r"))

    return ticket_json


def create_user_dir(user_id):

    dir_path = os.path.join(DATA_DIR, "users", str(user_id))
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)

    assert os.path.isdir(dir_path)

    return dir_path


def delete_user_dir(path):
    if os.path.isdir(path):
        os.removedirs(path)


def db_fill_form(user_dir, ocr_data):
    data_dir = os.path.join(os.getcwd(), os.pardir, "data")

    # Read ticket info
    # ticket_json = get_ticket(user_dir)
    # recognition_result = ticket_json["recognitionResult"]
    # lines = recognition_result["lines"]
    # BB_KEY = "boundingBox"
    # all_texts = [line["text"] for line in lines]
    # extracted_data = extract_data(all_texts, re_list)

    # Define PDF files
    form_de = os.path.join(data_dir, "form_de.pdf")
    print(form_de)
    temp_file = os.path.join(user_dir, "temp_fpdf")
    output_pdf = os.path.join(user_dir, "form.pdf")

    # Get key mappings
    mapping = get_json_data(os.path.join(data_dir, "mapping.json"))

    # Map ticket values to form keys
    data = json_to_fpdf_v2(mapping, ocr_data)

    try:
        # Fill form and generate PDF
        generated_pdf = pypdftk2.fill_form_v2(form_de, data, temp_file, output_pdf)
        out_pdf = pypdftk2.concat([output_pdf, generated_pdf])

        # TODO
        # return output_pdf
        return True
    except:
        return False


def send_pdf(user_dir):

    # TODO
    # pdf_path = db_fill_form(user_dir)

    pdf_path = os.path.join(user_dir, "form.pdf")

    if os.path.isfile(pdf_path):
        # TODO upload PDF to Telegram
        return True
    else:
        return False


# if __name__ == '__main__':
#     user_dir = os.path.join(os.getcwd(), os.pardir, "data", "users", "542253555")
#     db_fill_form(user_dir)
