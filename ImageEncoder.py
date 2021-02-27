import time, shutil
import face_recognition
from multiprocessing import Pool, Manager
import csv, re
import  pickle
from FaceRecognition.Utils import *
from itertools import repeat


# image_dirs = [PARENT_DIR + 'img_dir1/', PARENT_DIR + 'img_dir2/', PARENT_DIR + 'img_dir3/']
image_dirs = [PARENT_DIR + 'BAL_Crop_images/', PARENT_DIR + 'BSNL_Crop_images/', PARENT_DIR + 'RJIL_Crop_images/', PARENT_DIR + 'VIL_Crop_images/']
max_images_to_encode = 2000


def read_dirs(dirs):
    files = []
    for dir in dirs:
        for file in os.listdir(dir):
            files.append(dir + file)
    return files


def encode_image(img, Uencodable_faces):
    mobile_no = remove_nonnum(img.split('/')[-1])
    try:
        # source = open(img, 'rb')
        # face_encoding = None
        # contents = source.read()

        img_nump = face_recognition.load_image_file (img)

        img_loc = face_recognition.face_locations(img_nump, number_of_times_to_upsample=0, model='hog')

        face_encoding = face_recognition.face_encodings (img_nump, known_face_locations=img_loc, num_jitters=1, model="small")
    except Exception as err:
        print('Error while encoding:' + img + str(err))
        return [mobile_no, None, img]

    if face_encoding is None or len (face_encoding) == 0:
        Uencodable_faces.append('Cannot encode:' + img)
        return [mobile_no, None, img]
    return [mobile_no, face_encoding[0], img]


def encode_images_task_executor ():
    Uencodable_faces = Manager().list()

    p = Pool (pool_size)
    encs = p.starmap (encode_image, zip(images[0:max_images_to_encode], repeat(Uencodable_faces)))
    p.close()
    return encs, Uencodable_faces

if __name__ == '__main__':
    images = read_dirs(image_dirs)

    start_time = time.time ()


    face_encodings, Uencodable_faces = encode_images_task_executor()

    # face_encodings = dict(encodings)
    # del encodings
    print("---%d images encoded in %s seconds ---" % (len(face_encodings) - len(Uencodable_faces), time.time() - start_time))

    with open(PARENT_DIR + ENCODINGS_PICK_FILE, 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(face_encodings, f, pickle.HIGHEST_PROTOCOL)

    # print(len(Uencodable_faces))

    exit(0)


