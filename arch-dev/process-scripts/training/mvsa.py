from keras import initializers
from keras.layers import Layer
import tensorflow as tf

class MyMultiHeadAttention(Layer):
    def __init__(self, output_dim, num_head, kernel_initializer='glorot_uniform', **kwargs):
        self.output_dim = output_dim
        self.num_head = num_head
       # self.kernel_initializer = initializers.get(kernel_initializer) # return Serialiazation Error
        self.kernel_initializer = kernel_initializer
        super(MyMultiHeadAttention, self).__init__(**kwargs)

    def build(self, input_shape):
        initializer_object = initializers.get(self.kernel_initializer)
        self.W = self.add_weight(name='W',
                                 shape=(self.num_head, 3, input_shape[2], self.output_dim),
                                 initializer=initializer_object,
                                 trainable=True)
        self.Wo = self.add_weight(name='Wo',
                                  shape=(self.num_head * self.output_dim, self.output_dim),
                                  initializer=initializer_object,
                                  trainable=True)
        self.built = True

    def call(self, x):
        q = tf.linalg.matmul(x, self.W[0, 0])
        k = tf.linalg.matmul(x, self.W[0, 1])
        v = tf.linalg.matmul(x, self.W[0, 2])

        e = tf.linalg.matmul(q, k, transpose_b=True)
        e = e / (self.output_dim ** 0.5)
        e = tf.nn.softmax(e)
        outputs = tf.linalg.matmul(e, v)

        for i in range(1, self.W.shape[0]):
            q = tf.linalg.matmul(x, self.W[i, 0])
            k = tf.linalg.matmul(x, self.W[i, 1])
            v = tf.linalg.matmul(x, self.W[i, 2])

            e = tf.linalg.matmul(q, k, transpose_b=True)
            e = e / (self.output_dim ** 0.5)
            e = tf.nn.softmax(e)
            o = tf.linalg.matmul(e, v)
            outputs = tf.concat([outputs, o], axis=-1)

        z = tf.linalg.matmul(outputs, self.Wo)
        return z
    def compute_output_shape(self, input_shape):
        return input_shape[0], input_shape[1], self.output_dim

    def get_config(self):
        config = super().get_config().copy()
        config.update({
            "output_dim": self.output_dim,
            'num_head': self.num_head,
            'kernel_initializer': self.kernel_initializer
        })
        return config
