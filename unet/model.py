#!/bin/python

import numpy as np 
from keras.models import Model
from keras.layers import Input, Convolution2D, MaxPooling2D, UpSampling2D, Lambda, ZeroPadding2D
from keras.layers.merge import concatenate
from keras import backend as K

### IOU approximation based on http://www.cs.umanitoba.ca/~ywang/papers/isvc16.pdf
def IOU_calc(y_true, y_pred):
	y_true_f = K.flatten(y_true)
	y_pred_f = K.flatten(y_pred)
	intersection = y_true_f * y_pred_f
	union = y_true_f + y_pred_f - intersection
	return K.sum(intersection)/K.sum(union)

def IOU_calc_loss(y_true, y_pred):
	return 1.0 - IOU_calc(y_true, y_pred)

### Defining a small Unet
def unet_model(img_shape, segments):
	inputs = Input(img_shape)
	inputs_norm = Lambda(lambda x: x/127.5 - 1.)(inputs)
	conv1 = Convolution2D(8, (3, 3), activation='relu', padding='same')(inputs_norm)
	conv1 = Convolution2D(8, (3, 3), activation='relu', padding='same')(conv1)
	pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)

	conv2 = Convolution2D(16, (3, 3), activation='relu', padding='same')(pool1)
	conv2 = Convolution2D(16, (3, 3), activation='relu', padding='same')(conv2)
	pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)

	conv3 = Convolution2D(32, (3, 3), activation='relu', padding='same')(pool2)
	conv3 = Convolution2D(32, (3, 3), activation='relu', padding='same')(conv3)
	pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)

	conv4 = Convolution2D(64, (3, 3), activation='relu', padding='same')(pool3)
	conv4 = Convolution2D(64, (3, 3), activation='relu', padding='same')(conv4)
	pool4 = MaxPooling2D(pool_size=(2, 2))(conv4)

	conv5 = Convolution2D(128, (3, 3), activation='relu', padding='same')(pool4)
	conv5 = Convolution2D(128, (3, 3), activation='relu', padding='same')(conv5)

	up6 = concatenate([UpSampling2D(size=(2,2))(conv5), conv4], axis=3)
	conv6 = Convolution2D(64, (3, 3), activation='relu', padding='same')(up6)
	conv6 = Convolution2D(64, (3, 3), activation='relu', padding='same')(conv6)

	up7 = concatenate([UpSampling2D(size=(2, 2))(conv6), conv3], axis=3)
	conv7 = Convolution2D(32, (3, 3), activation='relu', padding='same')(up7)
	conv7 = Convolution2D(32, (3, 3), activation='relu', padding='same')(conv7)

	up8 = concatenate([UpSampling2D(size=(2, 2))(conv7), conv2], axis=3)
	conv8 = Convolution2D(16, (3, 3), activation='relu', padding='same')(up8)
	conv8 = Convolution2D(16, (3, 3), activation='relu', padding='same')(conv8)

	up9 = concatenate([UpSampling2D(size=(2, 2))(conv8), conv1], axis=3)
	conv9 = Convolution2D(8, (3, 3), activation='relu', padding='same')(up9)
	conv9 = Convolution2D(8, (3, 3), activation='relu', padding='same')(conv9)

	conv10 = Convolution2D(segments, (1, 1), activation='sigmoid')(conv9)

	model = Model(inputs=inputs, outputs=conv10)

	return model

def unet_test_model(img_shape, segments):
	inputs = Input(img_shape)
	inputs_norm = Lambda(lambda x: x/127.5 - 1.)(inputs)
	conv10 = Convolution2D(segments, (1, 1), activation='sigmoid')(inputs_norm)
	conv10.trainable = False
	model = Model(input=inputs, output=conv10)
	return model
