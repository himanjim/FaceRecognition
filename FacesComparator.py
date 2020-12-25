import time, shutil
import face_recognition
from multiprocessing import Pool, Value
import csv
from FaceRecognition.Utils import *
import  pickle
from itertools import repeat

NAME = 'name'
TSP = 'tsp'
CAF_STRIP_STR = 'CAF no.'
NON_ALPHA = re.compile('[^a-zA-Z]')
NON_NUM = re.compile('[^0-9]')
mobilenos_names = None
# copy_dir = 'E:/TestFaceRecognition/'
# csv_dirs = ['E:/TestFaceRecognition/csv_dir/']
copy_dir = PARENT_DIR + 'copy_dir/'
csv_dirs = [PARENT_DIR + 'csv_dir/']
pool_size = 8

def mobilenos_names_builder(csv_file_name):

    m_names = dict()
    with open(csv_file_name) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            m_names[remove_nonnum(row[2])] = {NAME: remove_nonalpha(remove_name_salutation(row[4]), CAF_STRIP_STR).lower(), TSP: remove_nonalpha(row[1], None).lower()}

    return m_names


def read_csv_executor ():
    p = Pool (pool_size)
    mnb = p.map (mobilenos_names_builder, csvs)
    p.close()
    return mnb


def is_valid_face_encoding(f_encoding):
    global mobilenos_names
    if f_encoding[1] is None:
        return False

    return True


def are_all_names_same(n_to_cmp):
    chk = True
    for item in n_to_cmp:
        if n_to_cmp[0] != item:
            chk = False
            break;

    return chk


def cmp_faces(f_encoding, face_under_comparision):
    if is_valid_face_encoding(f_encoding) is False:
        return None

    # match your image with the image and check if it matches
    result = face_recognition.compare_faces([f_encoding[1]], face_under_comparision[1])

    # check if it was a match
    if result[0]:
        return f_encoding[0]

    return None



def compare_faces(f_encodings, mobilenos_names):
    p = Pool(pool_size)

    while len(f_encodings) > 0:
        face_under_comparision = f_encodings.pop()
        if is_valid_face_encoding(face_under_comparision) is False:
            continue

        matching_nos = p.starmap(cmp_faces, zip(f_encodings, repeat(face_under_comparision)))

        for matching_no in matching_nos:
            if matching_no is not None:
                print(face_under_comparision[0] + ':' + mobilenos_names[face_under_comparision[0]][NAME] + ' matches with ' + matching_no + ':' + mobilenos_names[matching_no][NAME])

    p.close()


if __name__ == '__main__':

    start_time = time.time()

    csvs = read_dirs(csv_dirs)

    mobilenos_names_d = read_csv_executor()

    mobilenos_names = dict()

    for m_names_d in mobilenos_names_d:
        for key, value in m_names_d.items():
            mobilenos_names[key] = value

    del mobilenos_names_d

    print("---%d mobilenames map build up in %s seconds ---" % (len(mobilenos_names), time.time() - start_time))

    with open(PARENT_DIR + ENCODINGS_PICK_FILE, 'rb') as f:
        # The protocol version used is detected automatically, so we do not
        # have to specify it.
        face_encodings = pickle.load(f)

    max_images_to_encode = len(face_encodings)
    compare_faces (face_encodings, mobilenos_names)
    print ("---%d images compared in %s seconds ---" % (max_images_to_encode, time.time () - start_time))


