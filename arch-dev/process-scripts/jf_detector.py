import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"   # to Force CPU usage

from tensorflow.keras.layers import Input, Reshape, Dense, concatenate, Conv2D, MaxPooling2D
from keras.layers import Lambda, Layer
from tensorflow.keras.metrics import BinaryAccuracy, Precision, Recall
from keras.callbacks import ModelCheckpoint, Callback, EarlyStopping
from keras.models import Model
from tensorflow.keras.layers import  Flatten, BatchNormalization, LeakyReLU, Dropout
from tensorflow.keras.optimizers import Adam
import tensorflow as tf
from training.mvsa import MyMultiHeadAttention
from tensorflow.keras.models import load_model
import numpy as np

import keras

keras.config.enable_unsafe_deserialization()

def expand_dims_with_shape(x):
    return Lambda(
        lambda x: tf.expand_dims(x, axis=-1),
        output_shape=lambda input_shape: (*input_shape, 1)  # Add a dimension at the end
    )(x)

def create_model():
    input_css = Input(shape=(1, 768), name="css_input")
    input_ddg = Input(shape=(200, 200), name="ddg_input")
    input_cfg = Input(shape=(200, 200), name="cfg_input")
    input_ast = Input(shape=(600, 600), name="ast_input")

    att_ast = MyMultiHeadAttention(600, 4)(input_ast)  # Output dimension, number of heads
    att_ddg = MyMultiHeadAttention(200, 4)(input_ddg)  
    att_cfg = MyMultiHeadAttention(200, 4)(input_cfg)  
    att_css = MyMultiHeadAttention(400, 4)(input_css)
#print(att_cfg.shape) # it returns (None, 200, 200) 
#print(att_css.shape) # result in (None, 1, 400)
#print(att_ast.shape) # result in (None, 400, 400)
    reshape_css = Reshape((200, 2))(att_css)
    reshape_ast = Reshape((200, 1800))(att_ast)
    combine1 = concatenate([att_ddg, att_cfg]) # (200, 400)
    combine2 = concatenate([reshape_css, reshape_ast]) # (200, 1802)
    combine3 = concatenate([combine1, combine2]) # (200, 2202)
#expending = Lambda(lambda x: tf.expand_dims(x, axis=-1))(combine3)
    expending = expand_dims_with_shape(combine3) # Quad Self Attention Layer
# Now Applying CNN
    conv_1 = Conv2D(filters=32, kernel_size=(5, 5), strides=(3, 3), padding="valid")(expending)
    bn_1 = BatchNormalization(axis=-1, trainable=True, momentum=0.9)(conv_1)
    active_1 = LeakyReLU(0.01)(bn_1)
    conv_2 = Conv2D(filters=16, kernel_size=(3, 3), strides=(2, 2), padding="valid")(active_1)
    active_2 = LeakyReLU(0.01)(conv_2)
    maxpool_1 = MaxPooling2D(pool_size=(3, 3), strides=(1, 1), padding="valid")(active_2)
    drop_1 = Dropout(0.05)(maxpool_1)
    conv_3 = Conv2D(filters=8, kernel_size=(3, 3), strides=(2, 2), padding="valid")(drop_1)
    active_3 = LeakyReLU(0.01)(conv_3)
    maxpool_2 = MaxPooling2D(pool_size=(3, 3), strides=(1, 1), padding="valid")(active_3)
    drop_2 = Dropout(0.1)(maxpool_2)
    flatten_1 = Flatten()(drop_2)

# Final classification layers
    dense_1 = Dense(1024, activation="relu")(flatten_1)
    z = Dense(1, activation='sigmoid')(dense_1)

# Create and compile model
    model = Model(inputs=[input_css, input_ddg, input_cfg, input_ast], outputs=z)
    model.compile(optimizer=Adam(learning_rate=1e-5), loss=["binary_crossentropy"], metrics=[BinaryAccuracy(), Precision(), Recall()])
    return model


if __name__ == "__main__":
    

    """ new_model = load_model( this wont work unitl defining a Custom Layer class
    "../models/java-vuln-detection.keras",
    custom_objects={ 
        "MyMultiHeadAttention": MyMultiHeadAttention,    
    }
) """

    new_model = create_model()

    new_model.load_weights("../models/java-vuln-detection.keras") # this works well
    print("Loading Testing Data...")
    y_test = np.load("../dataset/ready/test_y.npy")
    x_test_css = np.load("../dataset/ready/css_test.npy")
    x_test_css = np.expand_dims(x_test_css, axis=1)
    data = np.load("../dataset/training-sets/600_ast_test.npz")
    x_test_ast = data["matrices"]
    data = np.load("../dataset/ready/cfg_test.npz")
    x_test_cfg = data["matrices"]
    data = np.load("../dataset/ready/ddg_test.npz")
    x_test_ddg = data["matrices"]

    css_input = x_test_css[0:1]# Shape (1, 1, 768)
    ddg_input = x_test_ddg[0:1]  # Shape (1, 200, 200)
    cfg_input = x_test_cfg[0:1]  # Shape (1, 200, 200)
    ast_input = x_test_ast[0:1] 
    y_pred_prob = new_model.predict([css_input, ddg_input, cfg_input, ast_input])
    y_pred = (y_pred_prob > 0.5).astype(int)
    print(y_pred[0][0])
    print("real target is")
    print(y_test[0])