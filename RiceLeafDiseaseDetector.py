from tensorflow import keras
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np


class RiceLeafDiseaseDetector:
    __MODEL_PATH = "./Model"

    def __init__(self):
        self.__model = keras.models.load_model(RiceLeafDiseaseDetector.__MODEL_PATH)

    def detect(self, image):
        image_array = RiceLeafDiseaseDetector.__load_image(image)
        prediction = np.round(self.__model.predict(image_array)[0])
        if prediction[3]:
            return "Leaf smut"
        elif prediction[0]:
            return "Bacterial leaf blight"
        elif prediction[1]:
            return "Brown spot"
        else:
            return "None"

    @classmethod
    def __load_image(cls, image_path, image_size=256):
        if not image_path:
            return None
        image = load_img(image_path, target_size=(image_size, image_size, 3))
        x = [img_to_array(image)]
        x = np.array(x)
        return x
