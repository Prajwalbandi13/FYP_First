import tensorflow as tf
import numpy as np
import os


class AnalyzingAgent:
    """
    Analyzing Agent:
    - Loads trained CNN model
    - Performs inference on preprocessed images
    """

    def __init__(self):
        model_path = os.path.join(
            os.path.dirname(__file__),
            "../model/trained_model.h5"
        )

        if not os.path.exists(model_path):
            raise FileNotFoundError("trained_model.h5 not found")

        self.model = tf.keras.models.load_model(model_path)

        # MUST match training directory order
        self.class_labels = [
            "Bacterial Pneumonia",
            "Corona Virus Disease",
            "Normal",
            "Tuberculosis",
            "Viral Pneumonia"
        ]

    def analyze(self, image):
        """
        Input  : Preprocessed image tensor (1, 224, 224, 3)
        Output : Dict of class probabilities
        """
        predictions = self.model.predict(image)[0]

        result = {}
        for i, label in enumerate(self.class_labels):
            result[label] = float(predictions[i])

        return result
