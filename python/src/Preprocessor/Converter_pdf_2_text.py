####################################################################################################################
# This script converts pdf files to raw text files                                                            ######
####################################################################################################################

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.psparser import PSEOF
from io import StringIO
from os import listdir
from os.path import isfile, join

# Custom imports from other folders of this project
# All paths to directories within project are held in one play, to be able to change them easily.
from shared_info import file_pdf_directory, file_txt_directory, preprocessor_blacklist_id_file


# This function will take path to pdf file on input and return its content as string
# It's going to be used below
def convert_pdf_to_txt(path, pages=None):
    # Sometimes we might want to specify which pages from the document we want. Let's handle that.
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    # Set up the converter. Based on documentation.
    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    # Let's read the file
    infile = open(path, 'rb')

    # Let's loop over pages of document and process them.
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)

    # Let's clean up the converter stuff and retrieve the text of the file.
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close()

    # Return the textual content of pdf file
    return text


# Let's retrieve list of ids of all documents in pdf form on the disk.
all_pdf_id_list = [f.replace('.pdf', '') for f in listdir(file_pdf_directory) if isfile(join(file_pdf_directory, f))]
# Let's retrieve list of ids of all documents in raw text form on the disk -
# - that have already been processed by this script
all_txt_id_list = [f.replace('.txt', '') for f in listdir(file_txt_directory) if isfile(join(file_txt_directory, f))]
# Let's determine which documents need to be processed (were not previously processed).
only_pdf_id_list = list(set(all_pdf_id_list) - set(all_txt_id_list))

# Let's ignore files from blacklist - that were either erroneous or the pdf converter was unable to process them.
blacklist_ids = []
with open(preprocessor_blacklist_id_file, "r") as file:
    for line in file:
        blacklist_ids.append(line.replace("\n", ""))
only_pdf_id_list = list(set(only_pdf_id_list) - set(blacklist_ids))

# Let's initialize the counters
counter = 1
bad_ids = 0
# Let's loop over all file ids that are supposed to be processed.
# Each file will be loaded and processed.
for file_id in only_pdf_id_list:
    # Let's output progress to console.
    print("Converting file " + str(counter) + "/" + str(len(only_pdf_id_list) - bad_ids))

    # Let's try to convert pdf to file to text form and save it on disk
    try:
        # Let's convert the pdf file to string using util function from above
        pdf_text = convert_pdf_to_txt(file_pdf_directory + '/' + file_id + '.pdf')
        # Let's write the file content to disk in text form.
        with open(file_txt_directory + '/' + file_id + '.txt', 'w') as text_file:
            text_file.write(pdf_text)
        # Let's output progress to console.
        print("Converted file " + str(counter) + "/" + str(len(only_pdf_id_list) - bad_ids))
        # Increase processed file counter
        counter = counter + 1
    # If something went wrong, let's save the file's id to blacklist
    except PSEOF:
        # Let's write the file id to blacklist on disk.
        with open(preprocessor_blacklist_id_file, 'a+') as text_file:
            text_file.write(file_id + "\n")
        # Increase faulty file counter
        bad_ids = bad_ids + 1
        # Let's output progress to console.
        print("Bad id " + str(file_id))
    # Nothing needs to be done in the end so far, but we might need to add something later.
    finally:
        pass
