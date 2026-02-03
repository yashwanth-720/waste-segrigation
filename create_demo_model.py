import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

print("Creating demo model for deployment...")

# Create a simple lightweight model
model = keras.Sequential([
    layers.Input(shape=(224, 224, 3)),
    layers.Conv2D(32, 3, activation='relu'),
    layers.MaxPooling2D(),
    layers.Conv2D(64, 3, activation='relu'),
    layers.MaxPooling2D(),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dense(2, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Save the model
model.save('waste_segregation_model.h5')
print("✅ Demo model created: waste_segregation_model.h5")
print("⚠️  This is a demo model. Train a real model later for 97% accuracy.")
