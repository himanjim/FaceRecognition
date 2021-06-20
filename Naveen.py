# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 23:25:24 2021

@author: Himanshu Sharma ITS, ADG (Administration) and Naveen Jakhar ITS, ADG (Security), DoT Haryana LSA
"""
#######################################################################################
############ code for finding image comparison using cosine difference ################
#######################################################################################

import pickle
import time
import pandas as pd
import numpy as np
import shutil
from datetime import datetime
import os
from scipy.spatial import distance

import threading
import time

tolerance = 0.4
cosine_diff = 0.04
NUM_PROCESSORS = 1

PARENT_DIR = 'D:/TestFaceRecognition_Naveen/'
ENCODINGS_PICK_FILE = 'encoding_dump'
FILTERED_SET_OF_IMAGES = "FILTERED_SET_OF_IMAGES/"
TEST_DIR = 'D:/TestFaceRecognition_Naveen/temp_results/unknown_image/'
encoded_image_df = pd.DataFrame()

print("Started reading the pickle dump file at -- ", datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + "hrs")
with open(PARENT_DIR + ENCODINGS_PICK_FILE, 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    data = pickle.load(f)
    # data = np.array(data)

print("Number of Images in ecoded pickle dump :: ", len(data))
start_time = time.time()
print("Started Comaprison of Images at Time stamp:: ", datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + "hrs")

i = 0


def finding_similar_images_using_cosine(mob_num_list, full_path_list, encoded_data_numpy_array, start_val, end_val):
    ##### using cosine distance separation ##########
    for x in range(start_val, end_val, 1):
        ## print("value of x is:",x)
        target = encoded_data_numpy_array[x]
        # print(target)
        vectors = encoded_data_numpy_array
        # print(vectors)
        ## start_time = time.time()
        distances = distance.cdist([target], vectors, "cosine")[0]
        # print(distances)
        similar_images = []
        index_list = []
        for i in distances:
            if i <= cosine_diff:
                # print(i)
                similar_images.append(i)
                index = np.where(distances == i)
                index_0 = index[0]
                if index_0 != x:
                    index_list.append(index)

        ## print(index_list)
        if len(index_list) > 0:
            complete_filename = full_path_list[x]
            file_name = complete_filename.split("/")[-1]
            directory_name = file_name.split(".")[0]
            # Providing Full Path
            path = os.path.join(PARENT_DIR + FILTERED_SET_OF_IMAGES, directory_name)
            if os.path.exists(path):
                print("Directory Name already exists")
            else:
                os.mkdir(path)

            shutil.copy(str(complete_filename),
                        PARENT_DIR + FILTERED_SET_OF_IMAGES + directory_name + "/" + str(file_name))

            for pp in range(len(index_list)):
                ## print(index_list[pp])
                index_val = int(index_list[pp][0])
                fname = full_path_list[index_val]
                shutil.copy(str(fname),
                            PARENT_DIR + FILTERED_SET_OF_IMAGES + directory_name + "/" + str(fname).split("/")[-1])


mob_num_list = list()
encoded_image_list = list()
full_path_list = list()
encoded_array_numpy_list = list()

for x in data:
    ### checking if we have encoded image data or not
    if x[1] is not None:
        mob_num_list.append(x[0])
        full_path_list.append(x[2])
        encoded_array_val = x[1]
        encoded_image_list.append(encoded_array_val)

encoded_data_numpy_array = np.array(encoded_image_list)
# print(encoded_data_numpy_array.shape)

start_val = 0

q = 0
val = list()
for q in range(NUM_PROCESSORS + 1):
    print(q)
    print(len(encoded_data_numpy_array))
    value = int((len(encoded_data_numpy_array) * int(q)) / int(NUM_PROCESSORS))
    print(value)
    val.append(value)

print(val)

## define the threads ###

q = 0
thread = list()
for q in range(NUM_PROCESSORS):
    print(q)
    start_val = val[q]
    print(start_val)
    end_val = val[q + 1]
    print(end_val)

q = 0
thread = [None] * NUM_PROCESSORS
for q in range(NUM_PROCESSORS):
    print(q)
    start_val = val[q]
    end_val = val[q + 1]
    thread[q] = threading.Thread(target=finding_similar_images_using_cosine,
                                args=([mob_num_list, full_path_list, encoded_data_numpy_array, start_val, end_val]))

q = 0
for q in range(NUM_PROCESSORS):
    print(thread[q])

# Start the threads
q = 0
for q in range(NUM_PROCESSORS):
    (thread[q]).start

# Join the threads before moving further
q = 0
for q in range(NUM_PROCESSORS):
    (thread[q]).join

print("Completed finding similar images at --", datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + "hrs")
end_time = time.time()
print("---The code completed its execution in %s seconds ---" % (time.time() - start_time))

del data
del encoded_image_df
# del index_list
del mob_num_list
del encoded_image_list
del full_path_list
del encoded_array_numpy_list
# del target
# del vectors
# del similar_images

#######################################################################################
######## code ends: for finding image comparison using cosine difference ##############
###########################################################################