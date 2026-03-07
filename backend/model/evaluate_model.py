import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import tensorflow.keras.backend as K

from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
from sklearn.preprocessing import label_binarize

# ----------------------------
# FOCAL LOSS (needed to load model)
# ----------------------------

def focal_loss(gamma=2., alpha=.25):

    def focal_loss_fixed(y_true, y_pred):

        epsilon = 1e-9
        y_pred = K.clip(y_pred, epsilon, 1. - epsilon)

        cross_entropy = -y_true * K.log(y_pred)

        weight = alpha * K.pow(1 - y_pred, gamma)

        loss = weight * cross_entropy

        return K.sum(loss, axis=1)

    return focal_loss_fixed


# ----------------------------
# PATHS
# ----------------------------

MODEL_PATH = "best_model.h5"
VAL_DIR = "../../dataset/val"

IMG_SIZE = (224,224)
BATCH_SIZE = 32


# ----------------------------
# LOAD MODEL
# ----------------------------

model = tf.keras.models.load_model(
    MODEL_PATH,
    custom_objects={"focal_loss_fixed": focal_loss()}
)

print("✅ Model loaded successfully")


# ----------------------------
# DATA GENERATOR
# ----------------------------

val_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input
)

val_generator = val_datagen.flow_from_directory(
    VAL_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    shuffle=False
)

class_labels = list(val_generator.class_indices.keys())

NUM_CLASSES = len(class_labels)

print("Classes:", class_labels)


# ----------------------------
# PREDICTIONS
# ----------------------------

print("\nRunning predictions...")

predictions = model.predict(val_generator)

predicted_classes = np.argmax(predictions,axis=1)

true_classes = val_generator.classes


# ----------------------------
# CONFUSION MATRIX
# ----------------------------

cm = confusion_matrix(true_classes,predicted_classes)

print("\nConfusion Matrix:\n")

print(cm)


# ----------------------------
# CLASSIFICATION REPORT
# ----------------------------

report = classification_report(
    true_classes,
    predicted_classes,
    target_names=class_labels
)

print("\nClassification Report:\n")

print(report)

with open("evaluation_report.txt","w") as f:
    f.write(report)

print("✅ evaluation_report.txt saved")


# ----------------------------
# ROC CURVE + AUC
# ----------------------------

print("\nGenerating ROC Curve...")

y_true = label_binarize(true_classes,classes=range(NUM_CLASSES))

plt.figure(figsize=(8,6))

for i in range(NUM_CLASSES):

    fpr,tpr,_ = roc_curve(y_true[:,i],predictions[:,i])

    roc_auc = auc(fpr,tpr)

    plt.plot(fpr,tpr,label=f"{class_labels[i]} (AUC={roc_auc:.2f})")

plt.plot([0,1],[0,1],'--')

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")

plt.title("ROC Curve")

plt.legend()

plt.savefig("roc_curve.png")

print("✅ roc_curve.png saved")


# ----------------------------
# CONFUSION MATRIX HEATMAP
# ----------------------------

plt.figure(figsize=(8,6))

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=class_labels,
    yticklabels=class_labels
)

plt.title("Confusion Matrix")

plt.ylabel("Actual Class")
plt.xlabel("Predicted Class")

plt.tight_layout()

plt.savefig("confusion_matrix.png")

print("✅ confusion_matrix.png saved")

print("\n🎉 Evaluation Completed Successfully!")