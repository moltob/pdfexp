import logging
import re

import attr
import os

import datetime

from pdfexpenses.expenses import Category, Expense

_logger = logging.getLogger(__name__)


class RecognitionFailedError(Exception):
    """Recognition of the file typ failed."""


PATTERN_DATE_PAID = re.compile(r'_BEZ(?P<date>\d{4}-\d{2}-\d{2})')


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
        self.process_filename_tags(source_document, expense)

        return expense

    @staticmethod
    def process_filename_tags(path, expense):
        if not path:
            return

        _, filename = os.path.split(path)

        m = PATTERN_DATE_PAID.search(path)
        if m:
            date = datetime.datetime.strptime(m.group('date'), '%Y-%m-%d').date()
            _logger.debug(f'Payment date overriden for {path!r}: {date}.')
            expense.date = date


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
    _logger.info(f'Extracting expense data from {pdf_path!r}.')
    with open(txt_path, 'rt') as txt_file:
        txt = txt_file.read()

    for content_type in CONTENT_TYPES:
        if content_type.match(txt):
            _logger.debug(f'Content type {content_type.name!r} marching.')
            expense = content_type.extract(txt, source_document=pdf_path)
            expense.to_yaml(yml_path)
            return

        _logger.debug(f'Content type {content_type.name!r} not marching.')

    _logger.error(f'Content type recognition failed for {pdf_path!r}.')
    raise RecognitionFailedError(txt_path)
