from flask import Flask,request, jsonify, render_template
import pickle
import numpy as np
from watchdog.events import EVENT_TYPE_OPENED
import cv2 as cv
import joblib
import json
import torch
from PIL import Image, ImageChops, ImageOps
from torchvision import transforms
from Models.Mnist.model import Model
import io
from Models.Cifar.Net import Net
from Models.Mnist.PredictModel import Predict
# from Models.Chatbot.PretrainedChatbot.Model import ChatBot
from Models.Chatbot.CustomChatbot.model import response
import base64
from datetime import datetime
# from Models.Translate.Transformer import Seq2SeqTransformer, translate


# TODO: Activity Recognition
# TODO: Languange Technology
# TODO: Real-Time Face Detection

app = Flask(__name__, static_url_path='/static', static_folder='static')

def load_paths(tag):
    with open('C:/Users/chris/Desktop/Dimitris/Tutorials/AI/Computational-Intelligence-and-Statistical-Learning/WebApp/Paths.json', 'r') as file:
        config  = json.load(file)

    if tag in config["Paths"]:
        paths = config["Paths"][tag]
        return paths
    else:
        raise ValueError(f"Tag '{tag}' not found in the configuration file.")
    
selected_tag = "Office"  # Change this tag based on your environment
selected_paths = load_paths(selected_tag)

SAVE_MODEL_PATH = selected_paths["SAVE_MODEL_PATH"]

### IRIS Classification Models ### Model based on Text classification
SVM_Iris_model = joblib.load(selected_paths["SVM_Iris_model"])
KNN_Iris_model = joblib.load(selected_paths["KNN_Iris_model"])
KNearestCentroid_Iris_model = joblib.load(selected_paths["KNearestCentroid_Iris_model"])

### IRIS Clustering Model ### 
KMeans_Iris_model = joblib.load(selected_paths["KMeans_Iris_model"])

### BreastCancer Clustering Model ### 
KMeans_breast_cancer_model = joblib.load(selected_paths["KMeans_breast_cancer_model"])

# Load the saved KMeans model and StandardScaler
scaler = joblib.load(selected_paths["KNearestCentroid_Iris_model"])

Regression_Iris_model = joblib.load(selected_paths["Regression_Iris_model"])
Regression_House_model = joblib.load(selected_paths["Regression_House_model"])


# Load Cifar-10 CNN model
cifar10_model = Net()
cifar10_model.load_state_dict(torch.load(selected_paths["Cifar_model_filename"]))
cifar10_model.eval()  # Set the model to evaluation mode
class_names = [
    'airplane', 'automobile', 'bird', 'cat', 'deer',
    'dog', 'frog', 'horse', 'ship', 'truck'
]

from keras.models import load_model
activity_model = load_model(selected_paths["Activity_Recognize"])



# Englist_To_German_model = joblib.load(selected_paths["Englist_To_German_model"])

# EMB_SIZE = 512
# NHEAD = 8
# FFN_HID_DIM = 512
# BATCH_SIZE = 128
# NUM_ENCODER_LAYERS = 3
# NUM_DECODER_LAYERS = 3

# checkpoint = torch.load(Englist_To_German_model, map_location=torch.device('cpu'))

# Translator = Seq2SeqTransformer(NUM_ENCODER_LAYERS, NUM_DECODER_LAYERS, EMB_SIZE,
#                            NHEAD, checkpoint['SRC_VOCAB_SIZE'], checkpoint['TGT_VOCAB_SIZE'], FFN_HID_DIM)

# Translator.load_state_dict(checkpoint['model_state_dict'])
# Translator.eval()




@app.route('/')
def home():
    return render_template('Home.html')


### Classification
@app.route('/Classification')
def Classification():
    return render_template('Classification.html')

@app.route('/Classification_Iris', methods=['GET'])
def Classification_Iris():
    return render_template('Classification_Iris.html')

@app.route('/ClassificationIris', methods=['POST'])
def ClassificationIris():
    try:
        # Extract the input data from the HTML form
        SepalLength = request.form.get('SepalLength')
        SepalWidth = request.form.get('SepalWidth')
        PetalLength = request.form.get('PetalLength')
        PetalWidth = request.form.get('PetalWidth')

        # Check if any of the features are null or empty strings
        if not all([SepalLength, SepalWidth, PetalLength, PetalWidth]):
            message = "Please set all the features"
            return render_template('Classification_Iris.html', message=message)
        
        # Convert features to floats if they are not null or empty strings
        SepalLength = float(SepalLength)
        SepalWidth = float(SepalWidth)
        PetalLength = float(PetalLength)
        PetalWidth = float(PetalWidth)
        
        input_data = np.array([SepalLength, SepalWidth, PetalLength, PetalWidth]).reshape(1, -1)

        if 'SVM' in request.form:
            prediction = SVM_Iris_model.predict(input_data)
        elif 'KNN' in request.form:
            prediction = KNN_Iris_model.predict(input_data)
        elif 'KNearestCentroid' in request.form:
            prediction = KNearestCentroid_Iris_model.predict(input_data)

        if(prediction is None):
            return render_template('Classification_Iris.html')
        else:
            result = int(prediction[0])
            if(result == 0):
                result = "Setosa"
            elif result == 1:
                result = "Versicolor"
            else:
                result = "Virginica"
            return render_template('Classification_Iris.html', result=result)
        
        
    except (ValueError, TypeError) as e:
        message = "Invalid input format. Please provide valid numeric values for all features."
        return render_template('Classification_Iris.html', message=message)



### Clustering 
@app.route('/Clustering')
def Clustering():
    return render_template('Clustering.html')


@app.route('/Clustering_Iris')
def Clustering_Iris():
    return render_template('Clustering_Iris.html')


@app.route('/Clustering_Iris', methods=['GET', 'POST'])
def Clustering_Iris_Predict():
    if request.method == 'POST':
        try:
            sepal_length = float(request.form.get('sepal_length'))
            sepal_width = float(request.form.get('sepal_width'))

            # Create a new data point from user input
            new_data_point = np.array([[sepal_length, sepal_width]])

            # Predict the cluster for the user's input
            predicted_cluster = KMeans_Iris_model.predict(new_data_point)

            if(predicted_cluster is None):
                return render_template('Clustering_Iris.html')
            else:
                result = int(predicted_cluster[0])
                if(result == 0):
                    result = "Setosa"
                elif result == 1:
                    result = "Versicolor"
                else:
                    result = "Virginica"
            return render_template('Clustering_Iris.html', result=result)


        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid input. Please enter valid numbers.'})

    return render_template('Clustering_Iris.html')



@app.route('/Clustering_BreastCancer')
def Clustering_BreastCancer():
    return render_template('Clustering_BreastCancer.html')

### TODO: Display plots to the html code
@app.route('/Clustering_BreastCancer', methods=['GET', 'POST'])
def Clustering_BreastCancer_Predict():
    if request.method == 'POST':
        try:
            # Get user input features (mean radius and mean texture)
            mean_radius = float(request.form.get('mean_radius'))
            mean_texture = float(request.form.get('mean_texture'))

            # Standardize the input features (same as during training)
            user_input = np.array([[mean_radius, mean_texture]])
            user_input = scaler.transform(user_input)

            # Predict the cluster for the user's input
            predicted_cluster = KMeans_Iris_model.predict(user_input)
            if(predicted_cluster is None):
                return render_template('Clustering_BreastCancer.html')
            else:
                result = int(predicted_cluster[0])
                if(result == 0):
                    result = "Setosa"
                elif result == 1:
                    result = "Versicolor"
                else:
                    result = "Virginica"
            return render_template('Clustering_BreastCancer.html', result=result)


        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid input. Please enter valid numbers.'})

    return render_template('Clustering_BreastCancer.html')



### Regression 
@app.route('/Regression')
def Regression():
    return render_template('Regression.html')


@app.route('/Regression_iris', methods=['GET', 'POST'])
def Regression_iris():
    if request.method == 'POST':
        try:
            # Get user input features (sepal length, sepal width, petal length, petal width)
            sepal_length = float(request.form.get('sepal_length'))
            sepal_width = float(request.form.get('sepal_width'))
            petal_length = float(request.form.get('petal_length'))
            petal_width = float(request.form.get('petal_width'))

            # Create a new data point from user input
            user_input = np.array([[sepal_length, sepal_width, petal_length, petal_width]])

            # Predict the regression value for the user's input
            predicted_value = Regression_Iris_model.predict(user_input)

            return render_template('Regression_Iris.html', predicted_value=predicted_value[0])

        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid input. Please enter valid numbers.'})

    return render_template('Regression_Iris.html', predicted_value=None)


@app.route('/Regression_house', methods=['GET', 'POST'])
def Regression_house():
    try:
        # Get input data from the form
        inputs = [float(x) for x in request.form.values()]
        
        # Make a prediction using the model
        prediction = Regression_House_model.predict([inputs])[0]
        
        # Format the prediction as a string
        predicted_value = f"${prediction:.4f}"
        
        return render_template('Regression_House.html', prediction=predicted_value)
    
    except Exception as e:
        return render_template('Regression_House.html', error="Error: " + str(e))





#ComputerVision
@app.route('/ComputerVision', methods=['GET'])
def ComputerVision():
    return render_template('ComputerVision.html')

@app.route('/ComputerVision_MNIST', methods=['GET'])
def ComputerVision_MNIST():
    return render_template('ComputerVision_MNIST.html')

@app.route('/ComputerVision_MNIST_Up_image', methods=['GET'])
def ComputerVision_MNIST_Up_image():
    return render_template('ComputerVision_MNIST_Up_image.html')


@app.route('/ComputerVision_MNIST_RealTime', methods=['GET'])
def ComputerVision_MNIST_RealTime():
    return render_template('ComputerVision_MNIST_RealTime.html')

 
@app.route("/predict_uploaded_image", methods=["POST"])
def predict_uploaded_image():

    img = Image.open(request.files["img"]).convert("L")

    # predict
    res_json = {"pred": "Err", "probs": []}
    if predict is not None:
        res = predict(img)
        res_json["pred"] = str(np.argmax(res))
        res_json["probs"] = [p * 100 for p in res]

    return render_template('ComputerVision_MNIST_Up_image.html', predicted_value=res_json["pred"])


@app.route("/DigitRecognition", methods=["POST"])
def predict_digit():
    img = Image.open(request.files["img"]).convert("L")

    # predict
    res_json = {"pred": "Err", "probs": []}
    if predict is not None:
        res = predict(img)
        res_json["pred"] = str(np.argmax(res))
        res_json["probs"] = [p * 100 for p in res]

    return json.dumps(res_json)


@app.route('/ComputerVision_CIFAR', methods=['GET'])
def ComputerVision_CIFAR():
    return render_template('ComputerVision_CIFAR10.html')

@app.route('/ComputerVision_CIFAR_predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        uploaded_image = request.files['image']
        temp_image_path = 'temp_image.jpg'
        uploaded_image.save(temp_image_path)
        predicted_class = predict_image(temp_image_path)
        return render_template('ComputerVision_CIFAR10.html', prediction_result=predicted_class)
    

def predict_image(image_path):
    # Preprocess the input image
    input_image = preprocess_image(image_path)
    print(type(input_image))
    print(len(input_image))
    
    # Make predictions
    with torch.no_grad():
        output = cifar10_model(input_image)
    
    # Get the predicted class index
    _, predicted_class_idx = torch.max(output, 1)
    
    predicted_class_name = class_names[predicted_class_idx.item()]
    
    # Return the predicted class name
    return predicted_class_name

def preprocess_image(image_path):
    # Open the image using PIL (Python Imaging Library)
    image = Image.open(image_path)
    print('The size of the input image is ', image.size)
    # Resize the image to 32x32 pixels
    image = image.resize((32, 32))

    # Apply the same transformations used during training (convert to tensor and normalize)
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    # Apply the transformations to the image
    processed_image = transform(image).unsqueeze(0)  # Add a batch dimension

    return processed_image


@app.route('/RealTimeFaceDetection', methods=['GET'])
def RealTimeFaceDetection():
    return render_template('RealTimeFaceDetection.html')


@app.route('/capture_photo', methods=['POST'])
def capture_photo():
    # Capture and save the photo
    image_data = request.json.get('image')

    if image_data:
        img_path = save_photo(image_data)
        return jsonify({'message': 'Photo captured successfully', 'img_path': img_path})
    else:
        return jsonify({'message': 'Failed to capture the photo'}), 400
    
def save_photo(image_data):
    # Ensure the 'faces' directory exists
    if not os.path.exists('faces'):
        os.makedirs('faces')

    try:
        # Decode base64 image data and convert to numpy array
        img_data = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(img_data, np.uint8)
        # Decode image using OpenCV
        img = cv.imdecode(nparr, cv.IMREAD_COLOR)

        if img is not None:
            # Generate a unique file name based on the timestamp
            img_name = f'faces/photo_{datetime.now().strftime("%Y%m%d%H%M%S")}.jpg'
            # Save the image to file
            cv.imwrite(img_name, img)

            return img_name  # Return the path where the image is saved
        else:
            print("Failed to decode image.")
            return None
    except Exception as e:
        print(f"Error saving photo: {e}")
        return None




@app.route('/Activity_Recognition', methods=['GET'])
def Activity_Recognition():
    return render_template('Activity_Recognition.html')



@app.route('/Predict_Activity_Recognition', methods=['Post'])
def PredictActivityRecognition():
    if request.method == "Post":
        uploaded_video = request.files['video']
        if uploaded_video is not None:
            print("Get the video")
        else:
            print("Error")
        # prediction_result = predict_activity(video_data)
    return render_template('Activity_Recognition.html')







# Language Model 
@app.route('/LanguageTechnology', methods=['GET'])
def LanguageTechnology():
    return render_template('LanguageTechnology.html')


# Language Model 
@app.route('/English_To_German', methods=['GET'])
def English_To_German():
    return render_template('English_To_German.html')


# @app.route('/English_To_German_Predict', methods=['Post'])
# def English_To_German_Predict():
#     if request.method == 'POST':
#         # Get the input text from the form
#         english_text = request.form['english_text']

#         # Perform translation using the loaded PyTorch model
#         translated_text = translate(Translator, english_text)  # Implement the translation function using your PyTorch model

#         # Return the translated text as JSON response
#         return jsonify({'translation': translated_text})
#     return "Error"


# Reinforcement Learning Model 
@app.route('/ReinforcementLearning', methods=['GET'])
def ReinforcementLearning():
    return render_template('ReinforcementLearning.html')


### Chat Bot
@app.route('/Chatbot', methods=['GET'])
def Chat_bot():
    return render_template('Chatbot.html')


@app.route('/PretrainedChatbot', methods=['GET'])
def Chat_PretrainedChatbotbot():
    return render_template('PretrainedChatbot.html')


# bot = ChatBot()
# @app.route('/PretrainedChat', methods=['POST'])
# def PretainedChat():
#     user_input = request.form['user_input']
#     if user_input.lower().strip() in ['bye', 'quit', 'exit']:
#         bot.end_chat = True
#         return "ChatBot: See you soon! Bye!"
#     bot.new_user_input_ids = bot.tokenizer.encode(user_input + bot.tokenizer.eos_token, return_tensors='pt')
#     bot_response = bot.bot_response()
#     return "ChatBot: " + bot_response


@app.route('/CustomChatbot', methods=['GET'])
def CustomChatbot():
    return render_template('CustomChatbot.html')


@app.route('/CustomChat', methods=['POST'])
def CustomChat():
    user_input = request.form['user_input']
    if user_input.lower().strip() in ['bye', 'quit', 'exit']:
        
        return "ChatBot: See you soon! Bye!"
    bot_response = response(user_input)
    return "ChatBot: " + bot_response




@app.route('/FakeImage', methods=['GET'])
def FakeImage():
    return render_template('FakeImage.html')



@app.route('/FromTextToImage', methods=['GET'])
def FromTextToImage():
    return render_template('FromTextToImage.html')




if __name__ == '__main__':
    import os
    assert os.path.exists(SAVE_MODEL_PATH), "no saved model"
    predict = Predict()
    app.run(debug=True)


