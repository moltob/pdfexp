import re

import attr
import yaml

from pdfexpenses.expenses import Category, Expense


class RecognitionFailedError(Exception):
    """Recognition of the file typ failed."""


@attr.s
class Recognizer:
    """Recognition of and data extraction from (PDF) text content.

    Attributes:
        name: Unique name identifying this content type.
        selector: Regular expression used to recognize the type from dcoument text.
        extractor: Regaular expression with captures to extract data.

    If the selector matches the document text, this type is used. Next the extractor will be
    matched. Failure to match is an error. The matched captures then form the extracted data set.
    """
    name = attr.ib()
    category = attr.ib()
    selector = attr.ib()
    extractor = attr.ib()

    def match(self, txt):
        return re.search(self.selector, txt, re.MULTILINE | re.DOTALL) is not None

    def extract(self, txt, *, source_document=None):
        match = re.search(self.extractor, txt, re.MULTILINE | re.DOTALL)
        if not match:
            raise RecognitionFailedError(self.name)

        expense = Expense(
            recognizer_name=self.name,
            category=self.category.name,
            source_document=source_document,
            **match.groupdict()
        )

        return expense


CONTENT_TYPES = [
    Recognizer(
        'Saal',
        Category.EXTERNAL_SERVICE,
        r'www\.saal-digital\.de',
        r'Rechnungsdatum\:\s*(?P<date>\d{2}\.\d{2}\.\d{4}).*Gesamtbetrag\:\s*(?P<amount>\d+,\d{2})'
    ),
    Recognizer(
        'Post',
        Category.POSTAGE_COSTS,
        r'Deutsche\s+Post\s+AG.*Postwertzeichen\s+ohne\s+Zuschlag',
        r'(?P<date>\d{2}\.\d{2}\.\d{2}).*Bruttoumsatz\s+\*(?P<amount>\d+,\d{2})\s+EUR'
    ),
    Recognizer(
        'Tintenalarm',
        Category.OFFICE_SUPPLIES,
        r'tintenalarm',
        r'(?P<date>\d{2}\.\d{2}\.\d{4}).*Summe\:\s+(?P<amount>\d+,\d{2})\s+'
    ),
    Recognizer(
        'Pixum',
        Category.EXTERNAL_SERVICE,
        r'Pixum',
        r'(?P<date>\d{2}\.\d{2}\.\d{4}).*Gesamt EUR\:\s+(?P<amount>\d+,\d{2})\s+'
    ),
]

CONTENT_TYPE_BY_NAME = {t.name: t for t in CONTENT_TYPES}


def recognize_pdf_text(txt_path, yml_path, pdf_path):
    with open(txt_path, 'rt') as txt_file:
        txt = txt_file.read()

    for content_type in CONTENT_TYPES:
        if content_type.match(txt):
            expense = content_type.extract(txt, source_document=pdf_path)
            expense.to_yaml(yml_path)
            return

    raise RecognitionFailedError(txt_path)
