import tensorflow as tf
import numpy as np

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from sklearn.utils.class_weight import compute_class_weight

# ----------------------------
# PATHS
# ----------------------------

TRAIN_DIR = "../../dataset/train"
VAL_DIR = "../../dataset/val"

IMG_SIZE = (256, 256)
BATCH_SIZE = 32

EPOCHS_FROZEN = 6
EPOCHS_FINE = 15

# ----------------------------
# DATA GENERATORS
# ----------------------------

train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    rotation_range=20,
    zoom_range=0.2,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.1,
    horizontal_flip=True,
    fill_mode="nearest"
)

val_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input
)

train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    shuffle=True
)

val_generator = val_datagen.flow_from_directory(
    VAL_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    shuffle=False
)

NUM_CLASSES = train_generator.num_classes
print("Classes:", train_generator.class_indices)

# ----------------------------
# CLASS WEIGHTS
# ----------------------------

labels = train_generator.classes

class_weights = compute_class_weight(
    class_weight="balanced",
    classes=np.unique(labels),
    y=labels
)

class_weights = dict(enumerate(class_weights))

print("Class Weights:", class_weights)

# ----------------------------
# BASE MODEL
# ----------------------------

base_model = MobileNetV2(
    input_shape=(256,256,3),
    include_top=False,
    weights="imagenet"
)

base_model.trainable = False

# ----------------------------
# MODEL HEAD
# ----------------------------

x = base_model.output

x = GlobalAveragePooling2D()(x)

x = Dropout(0.5)(x)

x = Dense(256, activation="relu")(x)

x = Dropout(0.4)(x)

output = Dense(NUM_CLASSES, activation="softmax")(x)

model = Model(inputs=base_model.input, outputs=output)

# ----------------------------
# CALLBACKS
# ----------------------------

best_checkpoint = ModelCheckpoint(
    "best_model.h5",
    monitor="val_accuracy",
    save_best_only=True,
    mode="max",
    verbose=1
)

latest_checkpoint = ModelCheckpoint(
    "latest_model.h5",
    save_freq="epoch",
    verbose=1
)

callbacks = [

    EarlyStopping(
        monitor="val_loss",
        patience=6,
        restore_best_weights=True
    ),

    ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.2,
        patience=3,
        min_lr=1e-7
    ),

    best_checkpoint,
    latest_checkpoint
]

# ----------------------------
# TRAINING PARAMETERS
# ----------------------------

steps_per_epoch = train_generator.samples // BATCH_SIZE
validation_steps = val_generator.samples // BATCH_SIZE

# ----------------------------
# PHASE 1 TRAINING
# ----------------------------

model.compile(

    optimizer=Adam(learning_rate=1e-4),

    loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.1),

    metrics=[
        "accuracy",
        tf.keras.metrics.TopKCategoricalAccuracy(k=2)
    ]

)

print("\nPhase 1: Training Frozen Base\n")

model.fit(

    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS_FROZEN,
    steps_per_epoch=steps_per_epoch,
    validation_steps=validation_steps,
    class_weight=class_weights,
    callbacks=callbacks

)

# ----------------------------
# PHASE 2 FINE TUNING
# ----------------------------

print("\nPhase 2: Fine Tuning\n")

base_model.trainable = True

for layer in base_model.layers[:-120]:
    layer.trainable = False

model.compile(

    optimizer=Adam(learning_rate=1e-5),

    loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.1),

    metrics=[
        "accuracy",
        tf.keras.metrics.TopKCategoricalAccuracy(k=2)
    ]

)

model.fit(

    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS_FINE,
    steps_per_epoch=steps_per_epoch,
    validation_steps=validation_steps,
    class_weight=class_weights,
    callbacks=callbacks

)

# ----------------------------
# SAVE MODEL
# ----------------------------

model.save("trained_model.h5")

print("Final model saved as trained_model.h5")
print("Best model saved as best_model.h5")