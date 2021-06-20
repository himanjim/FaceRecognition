import time, shutil
import face_recognition
from multiprocessing import Pool, Value
import csv
from FaceRecognition.Utils import *
import  pickle
from itertools import repeat
from scipy.spatial import distance

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


def mobilenos_names_builder(csv_file_name):

    m_names = dict()
    with open(csv_file_name) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if len(row) == 4:
                m_names[remove_nonnum(row[2])] = {NAME: remove_nonalpha(remove_name_salutation(row[3]), CAF_STRIP_STR).lower(), TSP: remove_nonalpha(row[1], None).lower()}

    return m_names


def read_csv_executor ():
    p = Pool (pool_size)
    mnb = p.map (mobilenos_names_builder, csvs)
    p.close()
    return mnb


def is_valid_face_encoding(f_encoding):
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


def cmp_faces(face_under_comparision, lists):
    encoded_images_list, image_full_paths_list = lists
    if is_valid_face_encoding(face_under_comparision) is False:
        return

    index = face_under_comparision[3]

    if index == -1:
        return

    c_distances = distance.cdist([face_under_comparision[1]], encoded_images_list[index + 1:], "cosine")[0]
    # print(distances)

    paths = []

    i = 0
    for c_distance in c_distances:
        if c_distance <= .04 :
            paths.append(image_full_paths_list[i + index + 1])
        i += 1

    # check if it was a match
    if len(paths) > 0:
        paths.append(image_full_paths_list[index])
        return face_under_comparision, paths

    return


def copy_similiar_faces(face_matching_faces_paths, mobilenos_names):
    if face_matching_faces_paths is None:
        return

    face_under_comparision, matching_faces_paths = face_matching_faces_paths

    if matching_faces_paths is None or len(matching_faces_paths) == 0:
        return

    matching_faces_paths = [x for x in matching_faces_paths if x is not None]

    new_dir = copy_dir + face_under_comparision[0]
    if os.path.isdir(new_dir) is False:
        os.mkdir(new_dir)

    copy_image_to_new_dir(new_dir, face_under_comparision[2], mobilenos_names)

    for matching_face_path in matching_faces_paths:
        copy_image_to_new_dir(new_dir, matching_face_path, mobilenos_names)


def copy_image_to_new_dir(new_dir, file_to_copy, mobilenos_names):
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


def compare_faces(f_encodings, encoded_images_list, image_full_paths_list, mobilenos_names):
    p = Pool(pool_size)

    face_all_matching_faces_paths = p.starmap(cmp_faces, zip(f_encodings, repeat([encoded_images_list, image_full_paths_list])))

    p.close()

    face_all_matching_faces_paths = [x for x in face_all_matching_faces_paths if x is not None]

    face_all_matching_faces_paths = sorted(face_all_matching_faces_paths, key=lambda x: len(x[1]))

    i = 0
    while i >= len(face_all_matching_faces_paths):

        for j in range(i + 1, len(face_all_matching_faces_paths)):

            if (all(x in face_all_matching_faces_paths[j][1] for x in face_all_matching_faces_paths[i][1])):
               del face_all_matching_faces_paths[i]
               break
            else:
                i += 1


    p = Pool(pool_size)

    p.starmap(copy_similiar_faces, zip(face_all_matching_faces_paths, repeat(mobilenos_names)))

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

    mob_nums_list = list()
    encoded_images_list = list()
    image_full_paths_list = list()

    index = 0
    for f_encoding in face_encodings:
        if f_encoding[1] is not None:
            mob_nums_list.append(f_encoding[0])
            image_full_paths_list.append(f_encoding[2])
            encoded_images_list.append(f_encoding[1])

            if index == max_images_to_encode -1:
                index = -1
            f_encoding.append(index)
            index += 1

    compare_faces (face_encodings, encoded_images_list, image_full_paths_list, mobilenos_names)
    print ("---%d images compared in %s seconds ---" % (max_images_to_encode, time.time () - start_time))


