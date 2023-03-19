import sqlite3
import hashlib
import datetime
import MySQLdb
from flask import session
from datetime import datetime
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import VGG16
from tensorflow.keras.layers import AveragePooling2D
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Input
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from imutils import paths
import matplotlib.pyplot as plt
import numpy as np
import argparse
import cv2
import os
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from tensorflow.keras.preprocessing.image import load_img, img_to_array





def image_info(image_path):
    classes = {0:"Infected eye",1:"Normal eye"}
     # load the model we saved
    model = load_model('blackfungus.h5')
        # predicting images
        #img = image.load_img('lungcancer/Train/lungcancer/3.png', target_size=(img_width, img_height))
    image = load_img(image_path,target_size=(224,224))
    print(image)
    image = img_to_array(image)
    image = image/255
    image = np.expand_dims(image,axis=0)
    result = np.argmax(model.predict(image))


    prediction = classes[result]
    print(prediction)
    return prediction

if __name__ == "__main__":
    print(db_connect())
