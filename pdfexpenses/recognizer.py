import re

import attr
import yaml


class RecognitionFailedError(Exception):
    """Recognition of the file typ failed."""


@attr.s
class ContentType:
    """Recognition of and data extraction from (PDF) text content.

    Attributes:
        name: Unique name identifying this content type.
        selector: Regular expression used to recognize the type from dcoument text.
        extractor: Regaular expression with captures to extract data.

    If the selector matches the document text, this type is used. Next the extractor will be
    matched. Failure to match is an error. The matched captures then form the extracted data set.
    """
    name = attr.ib()
    selector = attr.ib()
    extractor = attr.ib()

    def match(self, txt):
        return re.search(self.selector, txt, re.MULTILINE | re.DOTALL) is not None

    def extract(self, txt):
        match = re.search(self.extractor, txt, re.MULTILINE | re.DOTALL)
        if not match:
            raise RecognitionFailedError(self.name)

        data = dict(recognizer=self.name)
        data.update(match.groupdict())
        return data


CONTENT_TYPES = [
    ContentType(
        'Saal',
        r'www\.saal-digital\.de',
        r'Rechnungsdatum\:\s*(?P<date>\d{2}\.\d{2}\.\d{4}).*Gesamtbetrag\:\s*(?P<total>\d+,\d{2})'
    ),
    ContentType(
        'Post',
        r'Deutsche\s+Post\s+AG.*Postwertzeichen\s+ohne\s+Zuschlag',
        r'(?P<date>\d{2}\.\d{2}\.\d{2}).*Bruttoumsatz\s+\*(?P<total>\d+,\d{2})\s+EUR'
    )
]

CONTENT_TYPE_BY_NAME = {t.name: t for t in CONTENT_TYPES}


def recognize_pdf_text(txt_path, yml_path, pdf_path):
    with open(txt_path, 'rt') as txt_file:
        txt = txt_file.read()

    data = {
        'original': pdf_path
    }

    for content_type in CONTENT_TYPES:
        if content_type.match(txt):
            data.update(content_type.extract(txt))
            with open(yml_path, 'wt') as yml_file:
                yaml.dump(data, yml_file, default_flow_style=False)
            return

    raise RecognitionFailedError(txt_path)
