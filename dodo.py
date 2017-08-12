import glob

import os

PDFTOTEXT = r'D:\Work\dms\parsepdf\xpdf-tools-win-4.00\bin64\pdftotext.exe'

INPUT_DIR = r'q:\Privat\Rechnungen\00_Sonstige'
OUTPUT_DIR = r'd:\Temp\dodoout'

PDF_PATHS = glob.glob(os.path.join(INPUT_DIR, '**', '*.pdf'), recursive=True)


def task_extract():
    """Extract invoice data from PDF."""

    yml_paths = []

    for pdf_path in PDF_PATHS:
        rel_path = os.path.relpath(pdf_path, INPUT_DIR)
        rel_base_path, _ = os.path.splitext(rel_path)
        out_base_path = os.path.join(OUTPUT_DIR, rel_base_path)

        txt_path = out_base_path + '.txt'
        dirname = os.path.dirname(txt_path)

        yield dict(
            basename=txt_path,
            file_dep=[pdf_path],
            targets=[txt_path],
            clean=True,
            actions=[
                'if not exist "%s" mkdir "%s"' % (dirname, dirname),
                [PDFTOTEXT, '-table', pdf_path, txt_path]
            ],
        )

        yml_path = out_base_path + '.yml'
        yield dict(
            basename=yml_path,
            file_dep=[txt_path],
            targets=[yml_path],
            clean=True,
            actions=['copy "%(dependencies)s" "%(targets)s"'],
        )
        yml_paths.append(yml_path)

    xlsx_path = os.path.join(OUTPUT_DIR, 'expenses.xlsx')
    yield dict(
        basename=xlsx_path,
        file_dep=yml_paths,
        targets=[xlsx_path],
        clean=True,
        actions=['echo REPORT > %(targets)s']
    )


if __name__ == '__main__':
    import doit

    doit.run(globals())
