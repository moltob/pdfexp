import enum

import attr
import yaml


@attr.s
class Expense:
    source_document = attr.ib()
    recognizer_name = attr.ib()
    category = attr.ib()
    date = attr.ib()
    amount = attr.ib()

    def to_yaml(self, yml_path):
        with open(yml_path, 'wt') as yml_file:
            yaml.dump(attr.asdict(self), yml_file, default_flow_style=False)

    @classmethod
    def from_yaml(cls, yml_path):
        with open(yml_path, 'rt') as yml_file:
            data = yaml.load(yml_file)
            expense = cls(**data)
        return expense


class Category(enum.Enum):
    EXTERNAL_SERVICE = 1  # German: Fremdleistung
    POSTAGE_COSTS = 2  # German: Portokosten
    DEPRECIATION = 3  # German: Abschreibung