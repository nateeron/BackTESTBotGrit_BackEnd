import tensorflow as tf
# pip install tensorflow-gpu

# Check if GPU is available
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
