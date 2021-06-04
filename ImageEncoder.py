import time, shutil
import face_recognition
from multiprocessing import Pool, Manager
import csv, re
import  pickle
from FaceRecognition.Utils import *
from itertools import repeat
import imghdr

# image_dirs = [PARENT_DIR + 'img_dir1/', PARENT_DIR + 'img_dir2/', PARENT_DIR + 'img_dir3/']
image_dirs = [PARENT_DIR + 'img_dir3/']
# image_dirs = [PARENT_DIR + 'airtel/', PARENT_DIR + 'bsnl/', PARENT_DIR + 'Idea/', PARENT_DIR + 'rjil/', PARENT_DIR + 'Vodafone/']
error_csv = PARENT_DIR + 'errors.csv'
max_images_to_encode = None
max_images_to_encode_per_batch = 2

def read_dirs(dirs):
    files = []
    for dir in dirs:
        for file in os.listdir(dir):
            files.append(dir + file)
    return files


def encode_image(img, Uencodable_faces):
    # mobile_no = remove_nonnum(img.split('/')[-1])
    m = re.match(r'^.*(\d{10}).*$', img)
    if m:
        mobile_no = m.group(1)
    else:
        print('Invalid mobile no' + img)

    if imghdr.what(img) is None:
        Uencodable_faces.append('Cannot encode(not image):' + img)
        return [mobile_no, None, img]

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
        Uencodable_faces.append('Cannot encode(poor photo):' + img)
        return [mobile_no, None, img]
    return [mobile_no, face_encoding[0], img]


def encode_images_task_executor (images):
    Uencodable_faces = Manager().list()

    p = Pool (pool_size)
    encs = p.starmap (encode_image, zip(images[0:max_images_to_encode], repeat(Uencodable_faces)))
    p.close()
    return encs, Uencodable_faces

if __name__ == '__main__':
    images = read_dirs(image_dirs)

    images_sub_arrays = x = [images[i:i + max_images_to_encode_per_batch] for i in range(0, len(images), max_images_to_encode_per_batch)]
    del images

    pickle_file_index = 0
    for images_sub_array in images_sub_arrays:

        start_time = time.time ()

        face_encodings, Uencodable_faces = encode_images_task_executor(images_sub_array)

        # face_encodings = dict(encodings)
        # del encodings
        print("---%d images encoded in %s seconds ---" % (len(face_encodings) - len(Uencodable_faces), time.time() - start_time))

        with open(PARENT_DIR + ENCODINGS_PICK_FILE + str(pickle_file_index), 'wb') as f:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(face_encodings, f, pickle.HIGHEST_PROTOCOL)

        pickle_file_index += 1

        print("---%d images can't be encoded---" % ( len(Uencodable_faces)))

        with open(error_csv, mode='a') as err_file:
            error_file_writer = csv.writer(err_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            for face in Uencodable_faces:
                m = re.match(r'(^.*)(\d{10}).*$', face)
                if m:
                    error_file_writer.writerow([m.group(1), m.group(2)])
                else:
                    error_file_writer.writerow([face])

exit(0)


