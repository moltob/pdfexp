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
        return match.groupdict()


CONTENT_TYPES = [
    ContentType(
        'Saal',
        r'www\.saal-digital\.de',
        r'Rechnungsdatum\:\s*(?P<date>\d{2}\.\d{2}\.\d{4}).*Gesamtbetrag\:\s*(?P<total>\d+,\d{2})'
    )
]

CONTENT_TYPE_BY_NAME = {t.name: t for t in CONTENT_TYPES}


def recognize_pdf_text(dependencies, targets, pdf_path):
    assert len(dependencies) == 1
    assert len(targets) == 1
    txt_path = next(iter(dependencies))
    yml_path = targets[0]

    with open(txt_path, 'rt') as txt_file:
        txt = txt_file.read()

    data = {
        'original': pdf_path
    }

    for content_type in CONTENT_TYPES:
        if content_type.match(txt):
            data.update(content_type.extract(txt))
            with open(yml_path, 'wt') as yml_file:
                yaml.dump(data, yml_file)
            return

    raise RecognitionFailedError(txt_path)
