import numpy as np
from PIL import Image
import io

class MonitoringAgent:
    """
    Monitoring Agent:
    - Validates input image
    - Performs preprocessing
    - Prepares image for CNN inference
    """

    def __init__(self, img_size=(224, 224)):
        self.img_size = img_size
        self.allowed_types = ["image/jpeg", "image/png"]

    def process(self, file):
        """
        Input  : Uploaded image file
        Output : Preprocessed NumPy array ready for CNN
        """

        # ----------------------------
        # 1. FILE TYPE VALIDATION
        # ----------------------------
        if file.content_type not in self.allowed_types:
            raise ValueError("Invalid file type. Only JPG and PNG are supported.")

        # ----------------------------
        # 2. READ IMAGE BYTES SAFELY
        # ----------------------------
        image_bytes = file.file.read()

        if len(image_bytes) == 0:
            raise ValueError("Empty image file received.")

        # ----------------------------
        # 3. IMAGE DECODING
        # ----------------------------
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image = image.convert("RGB")
        except Exception:
            raise ValueError("Corrupted or unsupported image file.")

        # ----------------------------
        # 4. BASIC IMAGE QUALITY CHECK
        # ----------------------------
        width, height = image.size
        if width < 100 or height < 100:
            raise ValueError("Image resolution too low for medical analysis.")

        # ----------------------------
        # 5. RESIZE (MODEL INPUT SIZE)
        # ----------------------------
        image = image.resize(self.img_size)

        # ----------------------------
        # 6. NORMALIZATION
        # ----------------------------
        image_array = np.array(image, dtype=np.float32)
        image_array /= 255.0

        # ----------------------------
        # 7. BATCH DIMENSION
        # ----------------------------
        image_array = np.expand_dims(image_array, axis=0)

        return image_array
