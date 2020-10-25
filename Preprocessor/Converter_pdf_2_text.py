from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.psparser import PSEOF
from io import StringIO
from os import listdir
from os.path import isfile, join

from shared_info import file_pdf_directory, file_txt_directory, index_directory, blacklist_id_file


def convert_pdf_to_txt(path, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)
    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(path, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close()
    return text


all_pdf_id_list = [f.replace('.pdf', '') for f in listdir(file_pdf_directory) if isfile(join(file_pdf_directory, f))]
all_txt_id_list = [f.replace('.txt', '') for f in listdir(file_txt_directory) if isfile(join(file_txt_directory, f))]
only_pdf_id_list = list(set(all_pdf_id_list) - set(all_txt_id_list))

counter = 1
bad_ids = 0
for file_id in only_pdf_id_list:
    print("Converting file " + str(counter) + "/" + str(len(only_pdf_id_list) - bad_ids))

    try:
        pdf_text = convert_pdf_to_txt(file_pdf_directory + '/' + file_id + '.pdf')
        with open(file_txt_directory + '/' + file_id + '.txt', 'w') as text_file:
            text_file.write(pdf_text)

        print("Converted file " + str(counter) + "/" + str(len(only_pdf_id_list) - bad_ids))
        counter = counter + 1
    except PSEOF:
        with open(blacklist_id_file, 'a+') as text_file:
            text_file.write(file_id + "\n")

        bad_ids = bad_ids + 1
        print("Bad id " + str(file_id))
        pass
    finally:
        pass
