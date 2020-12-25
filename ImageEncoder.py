import time, shutil
import face_recognition
from multiprocessing import Pool, Manager
import csv, re
import  pickle
from FaceRecognition.Utils import *
from itertools import repeat

image_dirs = [PARENT_DIR + 'img_dir1/', PARENT_DIR + 'img_dir2/', PARENT_DIR + 'img_dir3/']
# image_dirs = [PARENT_DIR + 'BAL_Crop_images/', PARENT_DIR + 'BSNL_Crop_images/', PARENT_DIR + 'RJIL_Crop_images/', PARENT_DIR + 'VIL_Crop_images/']
pool_size = 8
max_images_to_encode = -1


def read_dirs(dirs):
    files = []
    for dir in dirs:
        for file in os.listdir(dir):
            files.append(dir + file)
    return files


def encode_image(img, Uencodable_faces):
    mobile_no = remove_nonnum(img.split('/')[-1])
    try:
        face_encoding = face_recognition.face_encodings (face_recognition.load_image_file (img))
    except Exception as err:
        print('Error while encoding:' + img + str(err))
        return [mobile_no, None]

    if face_encoding is None or len (face_encoding) == 0:
        print('Erro')
        Uencodable_faces.put('Cannot encode:' + img)
        return [mobile_no, None]
    return [mobile_no, face_encoding[0]]


def encode_images_task_executor (Uencodable_faces):
    p = Pool (pool_size)
    encs = p.starmap (encode_image, zip(images[0:max_images_to_encode], repeat(Uencodable_faces)))
    p.close()
    return encs

if __name__ == '__main__':
    images = read_dirs(image_dirs)

    start_time = time.time ()
    Uencodable_faces = Manager().Queue()

    face_encodings = encode_images_task_executor(Uencodable_faces)

    # face_encodings = dict(encodings)
    # del encodings
    print("---%d images encoded in %s seconds ---" % (len(face_encodings), time.time() - start_time))

    with open(PARENT_DIR + ENCODINGS_PICK_FILE, 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(face_encodings, f, pickle.HIGHEST_PROTOCOL)

    i = 0
    errors = []
    while i <= Uencodable_faces.qsize():
        errors.append(Uencodable_faces.get())
        i += 1

    print(errors)

    exit(0)


