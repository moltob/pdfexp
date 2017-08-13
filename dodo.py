import glob
import os

import doit.tools

from pdfexpenses.export import export_expenses
from pdfexpenses.recognition import recognize_pdf_text

PDFTOTEXT = r'pdftotext.exe'

INPUT_DIRS = [
    r'q:\Britta Pagel Fotografie\Fremdleistungen',
    r'q:\Britta Pagel Fotografie\Portokosten',
]
OUTPUT_DIR = r'd:\Temp\dodoout'


def task_extract():
    """Extract invoice data from PDF."""

    yml_paths = []
    created_dirs = set()

    for index, input_dir in enumerate(INPUT_DIRS):
        pdf_paths = glob.glob(os.path.join(input_dir, '**', '*.pdf'), recursive=True)

        for pdf_path in pdf_paths:
            rel_path = os.path.relpath(pdf_path, input_dir)
            rel_base_path, _ = os.path.splitext(rel_path)
            out_base_path = os.path.join(OUTPUT_DIR, str(index), rel_base_path)

            txt_path = out_base_path + '.txt'
            dirname = os.path.dirname(txt_path)

            if dirname not in created_dirs:
                created_dirs.add(dirname)

                yield dict(
                    name=dirname,
                    clean=True,
                    targets=[dirname],
                    actions=[(doit.tools.create_folder, (dirname,))],
                    uptodate=[doit.tools.run_once]
                )

            yield dict(
                name=txt_path,
                file_dep=[pdf_path],
                task_dep=['extract:' + dirname],
                targets=[txt_path],
                clean=True,
                actions=[[PDFTOTEXT, '-table', pdf_path, txt_path]],
            )

            yml_path = out_base_path + '.yml'
            yield dict(
                name=yml_path,
                file_dep=[txt_path],
                targets=[yml_path],
                clean=True,
                actions=[(recognize_pdf_text, (), {
                    'pdf_path': pdf_path,
                    'txt_path': txt_path,
                    'yml_path': yml_path,
                })],
            )
            yml_paths.append(yml_path)

    xlsx_path = os.path.join(OUTPUT_DIR, 'expenses.xlsx')
    yield dict(
        name=xlsx_path,
        file_dep=yml_paths,
        targets=[xlsx_path],
        clean=True,
        actions=[export_expenses]
    )


if __name__ == '__main__':
    import doit

    doit.run(globals())
