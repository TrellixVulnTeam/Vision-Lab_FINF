from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input
from tensorflow.keras.applications import VGG19
from tensorflow.keras.applications.vgg19 import preprocess_input

from . import _utils


MODEL_NAME = 'vgg19'
IMAGE_SIZE = 224


def load_model(model_version = 'default'):
  return _utils.load_model(MODEL_NAME, model_version)


def build_model():
  inputs = Input(shape = (IMAGE_SIZE, IMAGE_SIZE, 3))
  x = preprocess_input(inputs)
  x = VGG19(weights=None, classes=2)(x)
  model = Model(inputs=inputs, outputs=x)
  model.compile(loss='categorical_crossentropy', metrics=['accuracy'])
  return model
