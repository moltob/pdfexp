import glob
import logging
import os
import sys

import colorama
import daiquiri
import doit.tools

from pdfexpenses.export import export_expenses
from pdfexpenses.recognition import ExpenseExtractor

PDFTOTEXT = r'pdftotext.exe'

INPUT_DIRS = (
    r'q:\Britta Pagel Fotografie',
)
OUTPUT_DIR = r'x:\BPF Ausgaben'

_logger = logging.getLogger(__name__)


def task_extract():
    """Extract invoice data from PDF."""
    configure_logging()

    extractor = ExpenseExtractor()
    yml_paths = []
    created_dirs = set()

    for index, input_dir in enumerate(INPUT_DIRS):
        _logger.info(f'Collecting PDF documents in {input_dir!r}')
        pdf_paths = glob.iglob(os.path.join(input_dir, '**', '*.pdf'), recursive=True)

        for pdf_path in pdf_paths:
            base_path, _ = os.path.splitext(pdf_path)
            rel_base_path = os.path.relpath(base_path, input_dir)
            out_base_path = os.path.join(OUTPUT_DIR, str(index), rel_base_path)

            # allow usage of manually created annotation yaml:
            manual_yml_path = base_path + '.yml'
            if os.path.exists(manual_yml_path):
                _logger.debug(f'Using manual annotation {manual_yml_path!r}.')
                yml_paths.append(manual_yml_path)
            else:
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
                    actions=[(extractor.recognize_pdf_text, (), {
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


def configure_logging():
    # enable colored output and explicitly pass colorama-wrapped std stream to logger lib:
    level = doit.get_var('log', 'WARNING')
    colorama.init()
    daiquiri.setup(level, outputs=[daiquiri.output.Stream(sys.stderr)])


if __name__ == '__main__':
    doit.run(globals())
