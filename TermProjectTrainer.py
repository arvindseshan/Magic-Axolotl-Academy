from  tensorflow.keras  import  models
from  tensorflow.keras  import  layers
from sklearn.model_selection  import train_test_split
from sklearn.preprocessing  import LabelEncoder, StandardScaler
from pickle import dump

# Source: CMU 15-112 Homework 11
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

gestures = ["horizontalLine", "verticalLine"]

fullData = ''

for gesture in gestures:
    fullData += readFile(f"{gesture}.txt")
fullData = fullData.strip()
x = []
y = []
for line in fullData.splitlines():
    line = line.split(',')
    x.append(line[:-1])
    y.append(line[-1])
scaler = StandardScaler()
scaler.fit(x)
x = scaler.transform(x)

# Source for saving scaler: https://machinelearningmastery.com/how-to-save-and-load-models-and-data-preparation-in-scikit-learn-for-later-use/
dump(scaler, open('scaler.pkl', 'wb'))
encoder = LabelEncoder()
y = encoder.fit_transform(y)
xTrain = x
yTrain = y
#xTrain, xTest, yTrain, yTest = train_test_split(x, y, test_size =0.1,  random_state =1)

model = models.Sequential()
model.add(layers.Dense(100,  activation='relu', input_shape = (xTrain.shape[1],)))
model.add(layers.Dense(50,  activation='relu'))
model.add(layers.Dense(len(gestures),  activation='softmax'))
model.compile(optimizer='adam',loss='sparse_categorical_crossentropy', metrics =['accuracy'])
history = model.fit(xTrain ,yTrain ,epochs =500)#,validation_data =(xTest , yTest))

# Source for saving model: https://keras.io/api/models/model_saving_apis/#save_model-function
model.save("gestureRecognizer.h5")