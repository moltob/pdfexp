import os

import yaml

from pdfexpenses.expenses import Expense
from pdfexpenses.recognition import CONTENT_TYPE_BY_NAME, recognize_pdf_text


def test__content_type__saal():
    with open('inputs/Saal_OCR.txt', 'rt') as txtfile:
        txt = txtfile.read()

    content_type = CONTENT_TYPE_BY_NAME['Saal']
    assert content_type.match(txt)

    expense = content_type.extract(txt)
    assert expense.recognizer_name == 'Saal'
    assert expense.category == 'EXTERNAL_SERVICE'
    assert expense.amount == '11,10'
    assert expense.date == '10.07.2017'


def test__content_type__post():
    with open('inputs/Post.txt', 'rt') as txtfile:
        txt = txtfile.read()

    content_type = CONTENT_TYPE_BY_NAME['Post']
    assert content_type.match(txt)

    expense = content_type.extract(txt)
    assert expense.amount == '3,00'
    assert expense.date == '02.01.17'


def test__recognize_pdf_text__saal(output_dir):
    yml_path = os.path.join(output_dir, 'Saal.yml')
    recognize_pdf_text('inputs/Saal_OCR.txt', yml_path, r'q:\folder 1\Saal.pdf')
    expense = Expense.from_yaml(yml_path)

    assert expense.amount == '11,10'
    assert expense.date == '10.07.2017'
    assert expense.source_document == r'q:\folder 1\Saal.pdf'
