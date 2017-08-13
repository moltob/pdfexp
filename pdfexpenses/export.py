import attr
import xlsxwriter
import yaml

from pdfexpenses.expenses import Expense, Category


def export_expenses(dependencies, targets):
    ExpenseReport(dependencies).export_xlsx(targets[0])


@attr.s
class ExpenseReport:
    yml_paths = attr.ib()
    expenses = None

    def export_xlsx(self, path):
        self.expenses = [Expense.from_yaml(p) for p in self.yml_paths]
        workbook = xlsxwriter.Workbook(path)
        self.report_expenses(workbook)
        workbook.close()

    def report_expenses(self, workbook):
        worksheet = workbook.add_worksheet("Expenses")
        currency_format = workbook.add_format({
            'num_format': 0x08,  # built-in currency with red negatives
        })

        worksheet.set_column(0, 0, 25)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 3, 12)
        worksheet.set_column(4, 4, 100)

        data = [[
            e.category,
            e.recognizer_name,
            e.date,
            e.amount,
            e.source_document,
        ] for e in self.expenses]

        worksheet.add_table(0, 0, len(data), 4, {
            'style': 'Table Style Light 18',
            'data': data,
            'total_row': True,
            'columns': [{
                'header': "Category",
            }, {
                'header': "Document Type",
            }, {
                'header': "Date",
            }, {
                'header': "Amount",
                'format': currency_format,
                'total_function': 'sum',
            }, {
                'header': "Source Document",
            }]
        })
