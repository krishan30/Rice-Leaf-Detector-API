from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
#tensorflow is missing

class RiceLeafDiseaseDetector:
    __MODEL_PATH = ""

    def __init__(self):
        self.model = None#keras.models.load_model(RiceLeafDiseaseDetector.__MODEL_PATH)

    def detect(self, image):
        image_array = RiceLeafDiseaseDetector.__load_image(image)
        #prediction = np.round(self.model.predict(image_array)[0])

    @classmethod
    def __load_image(cls, file_storage, image_size=256):
        if not file_storage:
            return None
        image = load_img(file_storage, target_size=(image_size, image_size, 3))
        x = [img_to_array(image)]
        x = np.array(x)
        return x
