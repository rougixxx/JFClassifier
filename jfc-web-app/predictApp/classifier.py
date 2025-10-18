import re
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
from tensorflow.keras.models import load_model
from .mvsa import MyMultiHeadAttention, ExpandDimsLayer
import numpy as np 

from tensorflow.keras.layers import Input, Reshape, Dense, concatenate, Conv2D, MaxPooling2D
from keras.layers import Lambda
from tensorflow.keras.metrics import BinaryAccuracy, Precision, Recall
from keras.callbacks import ModelCheckpoint, Callback, EarlyStopping
from keras.models import Model
from tensorflow.keras.layers import  Flatten, BatchNormalization, LeakyReLU, Dropout
from tensorflow.keras.optimizers import Adam


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
    #expending = expand_dims_with_shape(combine3)
    expending = ExpandDimsLayer(axis=-1)(combine3) 
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
    
class JavaFunctionClassifier:
    def __init__(self, model_path ):
        #self.model = create_model()
        self.model_path = model_path
        
         # Check if model file exists
        if not os.path.exists(model_path):
            print(f"Error: Model file not found at {model_path}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Absolute path would be: {os.path.abspath(model_path)}")
            return
        
        try:
            self.model = load_model(
                model_path,
            custom_objects={
                "MyMultiHeadAttention": MyMultiHeadAttention,
                'ExpandDimsLayer': ExpandDimsLayer
    }
)
            """ print(f"Loading weights from: {model_path}")
            self.model.load_weights(model_path)
            print("✓ Model loaded successfully") """
            
        except Exception as e:
            import traceback
            print("❌ Failed to load model!")
        
            print(f"Model path: {model_path}")
            print(f"File exists: {e}")
            self.model = None
    def is_loaded(self):
        """Check if model is loaded"""
        return self.model is not None
    
    def predict(self, ast_matrix_path, cfg_matrix_path, ddg_matrix_path, css_matrix_path):
        """Predict the classification of Java code"""
        if self.model is None:
            raise Exception(f"Model isn't loaded. Check if model file exists at: {self.model_path}")
        
        try:
            # Load matrices
            x_css = np.load(css_matrix_path) # (1, 768)
            x_ast = np.load(ast_matrix_path) # (600, 600)
            x_cfg = np.load(cfg_matrix_path) # (200, 200)
            x_ddg = np.load(ddg_matrix_path) # (200, 200)
            
            print("Matrix shapes:")
            print(f"CSS: {x_css.shape}")
            print(f"AST: {x_ast.shape}")
            print(f"CFG: {x_cfg.shape}")
            print(f"DDG: {x_ddg.shape}")

            x_css = np.expand_dims(x_css, axis=0)
            x_ast = np.expand_dims(x_ast, axis=0)
            x_cfg = np.expand_dims(x_cfg, axis=0)
            x_ddg = np.expand_dims(x_ddg, axis=0)
        except Exception as e:
            print(f"Error during prediction: {e}")
            raise Exception(f"Prediction failed: {e}")
        
        y_pred_prob = self.model.predict([x_css, x_ddg, x_cfg, x_ast])
        y_pred = (y_pred_prob > 0.5).astype(int)[0][0]
        if y_pred == 0:
            return "safe"
        else:
            return "vulnerable"
            
            
        
    
if __name__ == "__main__":
    classifier = JavaFunctionClassifier("prediction-files/java-vuln-detection_v2.keras")
    classifier.predict("prediction-files/npy-files/ast_matrix.npy", "prediction-files/npy-files/cfg_matrix.npy", "prediction-files/npy-files/ddg_matrix.npy", "prediction-files/npy-files/css_matrix.npy")
            
            
# Initialize the classifier

