import logging
import operator

import attr
import xlsxwriter
import yaml

from pdfexpenses.expenses import Expense, Category

_logger = logging.getLogger(__name__)


def export_expenses(dependencies, targets):
    ExpenseReport(dependencies).export_xlsx(targets[0])


@attr.s
class ExpenseReport:
    yml_paths = attr.ib()
    expenses = None

    def export_xlsx(self, path):
        _logger.info(f'Writing expense report to {path!r}.')
        self.expenses = [Expense.from_yaml(p) for p in self.yml_paths]
        workbook = xlsxwriter.Workbook(path)
        self.report_expenses(workbook)
        workbook.close()

    def report_expenses(self, workbook):
        worksheet = workbook.add_worksheet("Expenses")

        # built-in formats:
        currency_format = workbook.add_format({'num_format': 0x08})
        date_format = workbook.add_format({'num_format': 0x0E})

        worksheet.set_column(0, 0, 25)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 3, 12)
        worksheet.set_column(4, 4, 100)

        data = [[
            e.category,
            e.recognizer_name,
            e.date,
            e.amount,
            'external:' + e.source_document,
        ] for e in sorted(self.expenses, key=operator.attrgetter('date'))]

        worksheet.add_table(0, 0, len(data) + 1, 4, {
            'style': 'Table Style Light 18',
            'data': data,
            'total_row': True,
            'columns': [{
                'header': "Category",
            }, {
                'header': "Document Type",
            }, {
                'header': "Date",
                'format': date_format,
            }, {
                'header': "Amount",
                'format': currency_format,
                'total_function': 'sum',
            }, {
                'header': "Source Document",
            }]
        })
