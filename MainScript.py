import os, time, shutil
import face_recognition
from multiprocessing import Pool, Queue
import csv, re

NAME = 'name'
TSP = 'tsp'
CAF_STRIP_STR = 'CAF no.'
NON_ALPHA = re.compile('[^a-zA-Z]')
NON_NUM = re.compile('[^0-9]')

# copy_dir = 'E:/TestFaceRecognition/'
# image_dirs = ['E:/TestFaceRecognition/img_dir1/', 'E:/TestFaceRecognition/img_dir2/', 'E:/TestFaceRecognition/img_dir3/']
# csv_dirs = ['E:/TestFaceRecognition/csv_dir/']
PARENT_DIR = 'C:/Users/himan/Downloads/mewat special audit/'
copy_dir = PARENT_DIR + 'copy_dir/'
image_dirs = [PARENT_DIR + 'BAL_Crop_images/', PARENT_DIR + 'BSNL_Crop_images/', PARENT_DIR + 'RJIL_Crop_images/', PARENT_DIR + 'VIL_Crop_images/']
csv_dirs = [PARENT_DIR + 'csv_dir/']
pool_size = 8
mobilenos_names = dict()

max_images_to_encode = 1


def read_dirs(dirs):
    files = []
    for dir in dirs:
        for file in os.listdir(dir):
            files.append(dir + file)
    return files


def mobilenos_names_builder(csv_file_name):
    m_names = dict()
    with open(csv_file_name) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            m_names[remove_nonnum(row[2])] = {NAME: remove_nonalpha(row[4], CAF_STRIP_STR).lower(), TSP: remove_nonalpha(row[1], None).lower()}

    return m_names


def remove_nonalpha(text, strip_str):
    if strip_str is not None:
        return re.sub(NON_ALPHA, '', text.split(CAF_STRIP_STR)[0])
    else:
        return re.sub(NON_ALPHA, '', text)


def remove_nonnum(text):
    return re.sub(NON_NUM,'',text)


def encode_image(img):
    try:
        face_encoding = face_recognition.face_encodings (face_recognition.load_image_file (img))
    except Exception as err:
        print('Error while encoding:' + img)
        print('Error:' + str(err))
        return [img, None]

    if face_encoding is None or len (face_encoding) == 0:
        print ('Cannot encode:' + img)
        return [img, None]
    return [img, face_encoding[0]]


def read_csv_executor ():
    p = Pool (pool_size)
    return p.map (mobilenos_names_builder, csvs)


def encode_images_task_executor ():
    p = Pool (pool_size)
    return p.map (encode_image, images[0:max_images_to_encode])


def are_all_names_same(n_to_cmp):
    chk = True
    for item in n_to_cmp:
        if n_to_cmp[0] != item:
            chk = False
            break;

    return chk


def compare_faces(f_encodings):
    i = 0
    no_of_encodings = len(f_encodings)

    mobile_nos_forged = []

    for i in range (no_of_encodings):
        if f_encodings[images[i]] is None:
            continue
        mobile_no1 = remove_nonnum(images[i].split('/')[-1])
        if mobile_no1 not in mobilenos_names:
            print(str(mobile_no1) + " not found in map.")
            continue

        if mobile_no1 in mobile_nos_forged:
            continue

        files_to_copy = [images[i]]
        names_to_cmp = [mobilenos_names[mobile_no1][NAME]]

        for j in range (i + 1, no_of_encodings):
            if f_encodings[images[j]] is None:
                continue
            mobile_no2 = remove_nonnum(images[j].split('/')[-1])

            if mobile_no2 not in mobilenos_names:
                print(str(mobile_no2) + " not found in map.")
                continue

            if mobile_no2 in mobile_nos_forged:
                continue
            # match your image with the image and check if it matches
            result = face_recognition.compare_faces ([f_encodings[images[j]]], f_encodings[images[i]], .4)

            # check if it was a match
            if result[0]:
                names_to_cmp.append(mobilenos_names[mobile_no2][NAME])
                files_to_copy.append(images[j])

        if len(files_to_copy) > 1 and are_all_names_same(names_to_cmp) is False:
            new_dir = copy_dir + mobile_no1
            os.mkdir(new_dir)
            for file_to_copy in files_to_copy:
                f_name = file_to_copy.split('/')[-1]

                m_no =  remove_nonnum(f_name)
                mobile_nos_forged.append(m_no)

                ext = remove_nonalpha(f_name, None)
                shutil.copyfile(file_to_copy, new_dir+ '/' + m_no + '_' + mobilenos_names[m_no][TSP] + '_' + mobilenos_names[m_no][NAME] + '.' + ext)



if __name__ == '__main__':
    images = read_dirs(image_dirs)
    csvs = read_dirs(csv_dirs)

    start_time = time.time ()
    mobilenos_names_d = read_csv_executor()

    for m_names_d in mobilenos_names_d:
        for key, value in m_names_d.items():
            mobilenos_names[key] = value

    del mobilenos_names_d

    print(len(mobilenos_names))

    encodings = encode_images_task_executor()
    face_encodings = dict(encodings)
    del encodings

    print(len(face_encodings))
    print ("---%d images encoded in %s seconds ---" % (max_images_to_encode, time.time () - start_time))
    compare_faces (face_encodings)
    print ("---%d images compared in %s seconds ---" % (max_images_to_encode, time.time () - start_time))


