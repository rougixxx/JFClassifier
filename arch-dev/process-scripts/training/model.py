from tensorflow.keras.layers import Input, Reshape, Dense, concatenate, Conv2D, MaxPooling2D
from keras.layers import Lambda, Layer
from tensorflow.keras.metrics import BinaryAccuracy, Precision, Recall
from keras.callbacks import ModelCheckpoint, Callback, EarlyStopping
from keras.models import Model
from tensorflow.keras.layers import  Flatten, BatchNormalization, LeakyReLU, Dropout
from tensorflow.keras.optimizers import Adam
import tensorflow as tf
from mvsa import MyMultiHeadAttention

class ExpandDimsLayer(Layer): # this class can be used to load the model directly
    """Custom layer to expand dimensions instead of using Lambda"""
    
    def __init__(self, axis=-1, **kwargs):
        super(ExpandDimsLayer, self).__init__(**kwargs)
        self.axis = axis
    
    def call(self, inputs):
        return tf.expand_dims(inputs, axis=self.axis)
    
    def compute_output_shape(self, input_shape):
        output_shape = list(input_shape)
        if self.axis == -1:
            output_shape.append(1)
        else:
            output_shape.insert(self.axis, 1)
        return tuple(output_shape)
    
    def get_config(self):
        config = super(ExpandDimsLayer, self).get_config()
        config.update({'axis': self.axis})
        return config


def expand_dims_with_shape(x):
    return Lambda(
        lambda x: tf.expand_dims(x, axis=-1),
        output_shape=lambda input_shape: (*input_shape, 1)  # Add a dimension at the end
    )(x)


input_css = Input(shape=(1, 768), name="css_input")
#input_css = Input(shape=(768))
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
combine1 = concatenate([att_ddg, att_cfg]) # (200, 400) input_ddg, input_cfg
combine2 = concatenate([reshape_css, reshape_ast]) # (200, 1802)
combine3 = concatenate([combine1, combine2]) # (200, 2202)
#expending = Lambda(lambda x: tf.expand_dims(x, axis=-1))(combine3)
expending = expand_dims_with_shape(combine3) # This is the Quad Attetntion Layer
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
model.compile(optimizer=Adam(learning_rate=1e-5), loss=["binary_crossentropy"], 
              metrics=[BinaryAccuracy(), Precision(), Recall()])

# Define checkpoint callback

checkpoints = ModelCheckpoint(
    filepath='models/ck/{epoch:04d}.weights.h5',
    monitor="val_loss",
    verbose=1,
    save_weights_only=True,
    save_freq='epoch',# or set period (older Keras)
)

early_stop = EarlyStopping(
    monitor="val_loss",
    patience=100,
    verbose=1,
    restore_best_weights=True
)

