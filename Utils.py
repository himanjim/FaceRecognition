import re, os

NAME = 'name'
TSP = 'tsp'
CAF_STRIP_STR = 'CAF no.'
NON_ALPHA = re.compile('[^a-zA-Z]')
NON_NUM = re.compile('[^0-9]')

PARENT_DIR = 'E:/TestFaceRecognition/'
# PARENT_DIR = 'C:/Users/himan/Downloads/mewat special audit/'
ENCODINGS_PICK_FILE = 'encoding_dump'

def read_dirs(dirs):
    files = []
    for dir in dirs:
        for file in os.listdir(dir):
            files.append(dir + file)
    return files

def remove_nonalpha(text, strip_str):
    if strip_str is not None:
        return re.sub(NON_ALPHA, '', text.split(CAF_STRIP_STR)[0])
    else:
        return re.sub(NON_ALPHA, '', text)


def remove_nonnum(text):
    return re.sub(NON_NUM,'',text)


def remove_name_salutation(name):
    return re.sub(r'(^\w{2,3}\. ?)', r'', name)

