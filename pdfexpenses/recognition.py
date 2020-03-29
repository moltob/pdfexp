import logging
import re

import attr
import os

import datetime

import colorama

from pdfexpenses.expenses import Category, Expense

_logger = logging.getLogger(__name__)


class RecognitionFailedError(Exception):
    """Recognition of the file typ failed."""


FILENAME_PATTERN_DATE_PAID = re.compile(r'_BEZ(?P<date>\d{4}-\d{2}-\d{2})')
TEXT_PATTERN_FALLBACK_DATE = re.compile(r'(?P<date>\d{2}\.\d{2}\.\d{2}(\d{2})?)')
TEXT_PATTERN_FALLBACK_AMOUNT = re.compile(r'([Gg]}esamt|[Ee]ndsumme|[Ee]ndbetrag)\s*:\s+'
                                          r'(?P<amount>\d+,\d{2})')


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
            _logger.warning(f'Recognizer {self.name!r} matched selector but not content.')
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

        m = FILENAME_PATTERN_DATE_PAID.search(path)
        if m:
            date = datetime.datetime.strptime(m.group('date'), '%Y-%m-%d').date()
            _logger.debug(f'Payment date overriden for {path!r}: {date}.')
            expense.date = date


CONTENT_TYPES = [
    Recognizer(
        'Saal',
        Category.EXTERNAL_SERVICE,
        r'(www\.saal-digital\.de|Saal-Digital Fotoservice GmbH)',
        r'Rechnungsdatum:\s*(?P<date>\d{2}\.\d{2}\.\d{4}).*(Gesamt|Rechnungs)betrag:?\s*(?P<amount>\d+,\d{2})'
    ),
    Recognizer(
        'Post',
        Category.POSTAGE_COSTS,
        r'Deutsche\s+Post',
        r'(?P<date>\d{2}\.\d{2}\.\d{2}).*Bruttoumsatz\s+\*(?P<amount>\d+,\d{2})\s+EUR'
    ),
    Recognizer(
        'Tintenalarm',
        Category.OFFICE_SUPPLIES,
        r'tintenalarm',
        r'(?P<date>\d{2}\.\d{2}\.\d{4}).*Summe:\s+(?P<amount>\d+,\d{2})\s+'
    ),
    Recognizer(
        'Pixum',
        Category.EXTERNAL_SERVICE,
        r'Pixum',
        r'(?P<date>\d{2}\.\d{2}\.\d{4}).*Gesamt EUR:\s+(?P<amount>\d+,\d{2})\s+'
    ),
    Recognizer(
        'Spamdrain',
        Category.EXTERNAL_SERVICE,
        r'SpamDrain',
        r'Invoice date:\s+(?P<date>\d{2}\.\d{2}\.\d{2}).*Total incl. VAT\s+(?P<amount>\d+,\d{2})\s+'
    ),
]

CONTENT_TYPE_BY_NAME = {t.name: t for t in CONTENT_TYPES}


class ExpenseExtractor:

    def __init__(self):
        self.prepared_expense_templates = []

    def recognize_pdf_text(self, txt_path, yml_path, pdf_path):
        _logger.info(f'Extracting expense data from {pdf_path!r}.')
        with open(txt_path, 'rt') as txt_file:
            txt = txt_file.read()

        for content_type in CONTENT_TYPES:
            if content_type.match(txt):
                try:
                    _logger.debug(f'Content type {content_type.name!r} matching.')
                    expense = content_type.extract(txt, source_document=pdf_path)
                    expense.to_yaml(yml_path)
                except RecognitionFailedError:
                    self.prepare_expense_template(txt, yml_path, pdf_path, content_type)
                break

            _logger.debug(f'Content type {content_type.name!r} not matching.')
        else:
            _logger.warning(f'Content type recognition failed for {pdf_path!r}.')
            self.prepare_expense_template(txt, yml_path, pdf_path)

    def prepare_expense_template(self, txt, yml_path, pdf_path, content_type=None):
        # try to find a fallback values in document:
        m = TEXT_PATTERN_FALLBACK_DATE.search(txt)
        date = m.group('date') if m else datetime.date(1900, 1, 1)

        m = TEXT_PATTERN_FALLBACK_AMOUNT.search(txt)
        amount = m.group('amount') if m else '0,00'

        expense = Expense(
            source_document=pdf_path,
            recognizer_name=content_type.name if content_type else 'Manual',
            category=content_type.category.name if content_type else Category.UNDEFINED.name,
            date=date,
            amount=amount
        )
        expense.to_yaml(yml_path)
        self.prepared_expense_templates.append(yml_path)

        _logger.warning(
            f'Please prepare a manual expense and save it next to the original document. '
            f'You can take the template from {yml_path!r}.'
        )

    def print_prepared_expense_templates(self):
        if not self.prepared_expense_templates:
            return

        _logger.warning(f'{len(self.prepared_expense_templates)} expense templates prepared.')
        for template in self.prepared_expense_templates:
            _logger.info(f'  {template}')
