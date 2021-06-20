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
forged_mobile_nos = list()
# copy_dir = 'E:/TestFaceRecognition/'
# csv_dirs = ['E:/TestFaceRecognition/csv_dir/']
copy_dir = PARENT_DIR + 'copy_dir/'
csv_dirs = [PARENT_DIR + 'csv_dir/']




def is_valid_face_encoding(f_encoding):
    if f_encoding[1] is None:
        return False

    return True




def cmp_faces(f_encodings, face_under_comparision):
    fc_encods = []

    for f_encoding in f_encodings:
        if is_valid_face_encoding(f_encoding) is False:
            continue

        fc_encods.append(f_encoding[1])

    if len(fc_encods) == 0:
        return

    # match your image with the image and check if it matches
    result = face_recognition.compare_faces(fc_encods, face_under_comparision[1], .4)

    # check if it was a match
    # if result[0]:
    #     return f_encoding[0], f_encoding[2]

    return


def copy_image_to_new_dir(new_dir, file_to_copy):
    global mobilenos_names
    f_name = file_to_copy.split('/')[-1]

    m_no = remove_nonnum(f_name)

    ext = remove_nonalpha(f_name, None)

    if m_no not in mobilenos_names:
        print(str(m_no) + ' not in mobilenos_names map.')
        return

    tsp = ['', mobilenos_names[m_no][TSP]][m_no in mobilenos_names]
    name = ['', mobilenos_names[m_no][NAME]][m_no in mobilenos_names]

    file_new_path = new_dir + '/' + m_no + '_' + name + '_' + tsp + '.' + ext
    if os.path.isdir(file_new_path) is False:
        shutil.copyfile(file_to_copy, file_new_path)


def compare_faces(f_encodings, start_time):
    p = Pool(pool_size)

    images_count = 0

    while len(f_encodings) > 0:
        face_under_comparision = f_encodings.pop()

        if is_valid_face_encoding(face_under_comparision) is False:
            continue

        f_encodings_sub_arrays = [f_encodings[i:i + 200] for i in range(0, len(f_encodings), 200)]

        matching_nos_paths = p.starmap(cmp_faces, zip(f_encodings_sub_arrays, repeat(face_under_comparision)))

        # matching_nos_paths = [x for x in matching_nos_paths if x is not None]

        if images_count % 50 == 0:
            print ("---%d images compared in %s seconds ---" % (len(f_encodings), time.time () - start_time))

        images_count += 1

        if len(matching_nos_paths) == 0:
            continue

        # new_dir = copy_dir + face_under_comparision[0]
        # if os.path.isdir(new_dir) is False:
        #     os.mkdir(new_dir)
        #
        # copy_image_to_new_dir(new_dir, face_under_comparision[2])
        #
        # for matching_nos_path in matching_nos_paths:
        #
        #     if matching_nos_path[0] is not None:
        #         forged_mobile_nos.append(matching_nos_path[0])
        #         copy_image_to_new_dir(new_dir, matching_nos_path[1])

                # print(face_under_comparision[0] + ':' + mobilenos_names[face_under_comparision[0]][NAME] + ' matches with ' + matching_no + ':' + mobilenos_names[matching_no][NAME])

    p.close()


if __name__ == '__main__':

    start_time = time.time()

    with open('C:/Users/himan/Downloads/encoding_dump_naveen', 'rb') as f:
        # The protocol version used is detected automatically, so we do not
        # have to specify it.
        face_encodings = pickle.load(f)

    max_images_to_encode = len(face_encodings)
    compare_faces (face_encodings, start_time)
    print ("---%d images compared in %s seconds ---" % (max_images_to_encode, time.time () - start_time))


