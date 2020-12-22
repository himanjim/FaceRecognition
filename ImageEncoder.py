import os, time, shutil
import face_recognition
from multiprocessing import Pool
import csv, re
import  pickle
from FaceRecognition.Utils import *


image_dirs = [PARENT_DIR + 'BAL_Crop_images/', PARENT_DIR + 'BSNL_Crop_images/', PARENT_DIR + 'RJIL_Crop_images/', PARENT_DIR + 'VIL_Crop_images/']
pool_size = 8

max_images_to_encode = 3


def read_dirs(dirs):
    files = []
    for dir in dirs:
        for file in os.listdir(dir):
            files.append(dir + file)
    return files


def encode_image(img):
    mobile_no = remove_nonnum(img.split('/')[-1])
    try:
        face_encoding = face_recognition.face_encodings (face_recognition.load_image_file (img))
    except Exception as err:
        print('Error while encoding:' + img)
        print('Error:' + str(err))
        return [mobile_no, None]

    if face_encoding is None or len (face_encoding) == 0:
        print ('Cannot encode:' + img)
        return [mobile_no, None]
    return [mobile_no, face_encoding[0]]


def encode_images_task_executor ():
    p = Pool (pool_size)
    encs = p.map (encode_image, images[0:max_images_to_encode])
    p.close()
    return encs

if __name__ == '__main__':
    images = read_dirs(image_dirs)

    start_time = time.time ()

    face_encodings = encode_images_task_executor()

    # face_encodings = dict(encodings)
    # del encodings
    print("---%d images encoded in %s seconds ---" % (len(face_encodings), time.time() - start_time))

    with open(PARENT_DIR + ENCODINGS_PICK_FILE, 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(face_encodings, f, pickle.HIGHEST_PROTOCOL)



