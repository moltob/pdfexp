import datetime
import enum
import logging

import attr
import yaml

_logger = logging.getLogger(__name__)


def convert_amount(value):
    if isinstance(value, str):
        # this is a mean locale handling shortcut, but let's see whether we hit the bad cases:
        value = float(value.replace(',', '.'))
    return value


def convert_date(value):
    if isinstance(value, str):
        for fmt in {'%d.%m.%y', '%d.%m.%Y'}:
            try:
                value = datetime.datetime.strptime(value, fmt).date()
                break
            except ValueError:
                # try next format:
                pass
        else:
            raise ValueError(f'Cannot parse date format {value!r}.')

    return value


@attr.s
class Expense:
    source_document = attr.ib()
    recognizer_name = attr.ib()
    category = attr.ib()
    date = attr.ib(convert=convert_date)
    amount = attr.ib(convert=convert_amount)

    def to_yaml(self, yml_path):
        _logger.debug(f'Writing expense to {yml_path!r}.')
        with open(yml_path, 'wt') as yml_file:
            yaml.dump(attr.asdict(self), yml_file, default_flow_style=False)

    @classmethod
    def from_yaml(cls, yml_path):
        _logger.debug(f'Reading expense from {yml_path!r}.')
        with open(yml_path, 'rt') as yml_file:
            data = yaml.load(yml_file)
            expense = cls(**data)
        return expense


class Category(enum.Enum):
    UNDEFINED = 0
    EXTERNAL_SERVICE = 1  # German: Fremdleistung
    POSTAGE_COSTS = 2  # German: Portokosten
    DEPRECIATION = 3  # German: Abschreibung
    OFFICE_SUPPLIES = 4  # German: Büroartikel
