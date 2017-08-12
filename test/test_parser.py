from pdfexpenses.parser import CONTENT_TYPE_BY_NAME


def test__content_type__saal():
    with open('inputs/Saal_OCR.txt', 'rt') as txtfile:
        txt = txtfile.read()

    content_type = CONTENT_TYPE_BY_NAME['Saal']
    assert content_type.match(txt)

    data = content_type.extract(txt)
    assert data['total'] == '11,10'
