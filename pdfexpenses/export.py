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
        self.report_expenses(workbook.add_worksheet("Expenses"))
        workbook.close()

    def report_expenses(self, worksheet):
        data = [[
            e.category,
            e.recognizer_name,
            e.date,
            e.amount,
            e.source_document,
        ] for e in self.expenses]

        worksheet.add_table(0, 0, len(data), 4, {
            'data': data
        })
