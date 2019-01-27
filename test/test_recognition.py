import os

import datetime
import yaml

from pdfexpenses.expenses import Expense
from pdfexpenses.recognition import CONTENT_TYPE_BY_NAME, ExpenseExtractor


def test__content_type__saal():
    with open('inputs/Saal_OCR.txt', 'rt') as txtfile:
        txt = txtfile.read()

    content_type = CONTENT_TYPE_BY_NAME['Saal']
    assert content_type.match(txt)

    expense = content_type.extract(txt)
    assert expense.recognizer_name == 'Saal'
    assert expense.category == 'EXTERNAL_SERVICE'
    assert expense.amount == 11.1
    assert expense.date == datetime.date(2017, 7, 10)


def test__content_type__post():
    with open('inputs/Post.txt', 'rt') as txtfile:
        txt = txtfile.read()

    content_type = CONTENT_TYPE_BY_NAME['Post']
    assert content_type.match(txt)

    expense = content_type.extract(txt)
    assert expense.amount == 3
    assert expense.date == datetime.date(2017, 1, 2)


def test__content_type__tintenalarm():
    with open('inputs/Tintenalarm.txt', 'rt') as txtfile:
        txt = txtfile.read()

    content_type = CONTENT_TYPE_BY_NAME['Tintenalarm']
    assert content_type.match(txt)

    expense = content_type.extract(txt)
    assert expense.amount == 45.69
    assert expense.date == datetime.date(2017, 2, 8)
    assert expense.category == 'OFFICE_SUPPLIES'


def test__content_type__pixum():
    with open('inputs/Pixum.txt', 'rt') as txtfile:
        txt = txtfile.read()

    content_type = CONTENT_TYPE_BY_NAME['Pixum']
    assert content_type.match(txt)

    expense = content_type.extract(txt)
    assert expense.amount == 148.37
    assert expense.date == datetime.date(2016, 12, 18)
    assert expense.category == 'EXTERNAL_SERVICE'


def test__recognize_pdf_text__saal(output_dir):
    yml_path = os.path.join(output_dir, 'Saal.yml')
    ExpenseExtractor().recognize_pdf_text('inputs/Saal_OCR.txt', yml_path, r'q:\folder 1\Saal.pdf')
    expense = Expense.from_yaml(yml_path)

    assert expense.amount == 11.1
    assert expense.date == datetime.date(2017, 7, 10)
    assert expense.source_document == r'q:\folder 1\Saal.pdf'


def test__recognize_pdf_text__overridden_date(output_dir):
    yml_path = os.path.join(output_dir, 'Pixum_BEZ2017-01-03.yml')
    ExpenseExtractor().recognize_pdf_text(
        'inputs/Pixum_BEZ2017-01-03.txt',
        yml_path,
        r'q:\folder 1\Pixum_BEZ2017-01-03.pdf'
    )
    expense = Expense.from_yaml(yml_path)
    assert expense.date == datetime.date(2017, 1, 3)
