import os

import yaml

from pdfexpenses.recognizer import CONTENT_TYPE_BY_NAME, recognize_pdf_text


def test__content_type__saal():
    with open('inputs/Saal_OCR.txt', 'rt') as txtfile:
        txt = txtfile.read()

    content_type = CONTENT_TYPE_BY_NAME['Saal']
    assert content_type.match(txt)

    data = content_type.extract(txt)
    assert data['total'] == '11,10'
    assert data['date'] == '10.07.2017'


def test__recognize_pdf_text__saal(output_dir):
    yml = os.path.join(output_dir, 'Saal.yml')
    recognize_pdf_text('inputs/Saal_OCR.txt', yml, r'q:\folder 1\Saal.pdf')

    with open(yml, 'rt') as yml_file:
        data = yaml.load(yml_file)

    assert data['total'] == '11,10'
    assert data['date'] == '10.07.2017'
    assert data['original'] == r'q:\folder 1\Saal.pdf'
