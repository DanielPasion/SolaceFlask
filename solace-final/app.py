import os

#open ai imports
import openai
from flask import Flask, redirect, render_template, request, url_for

#hemu imports
from hume import HumeBatchClient
from hume.models.config import FaceConfig
from pprint import pprint
from hume import HumeStreamClient
import asyncio
import cv2

def capture_image():
    # Create a VideoCapture object
    cap = cv2.VideoCapture(0)

    # Check if the webcam is opened successfully
    if not cap.isOpened():
        print("Unable to access the camera.")
        return

    # Capture frame-by-frame
    ret, frame = cap.read()

    # Check if the frame was captured successfully
    if not ret:
        print("Failed to capture frame.")
        return

    # Save the image
    cv2.imwrite('captured_image.jpg', frame)
    print('Image captured!')

    # Release the VideoCapture object
    cap.release()

def findEmotion (result):
    max = 0
    emotion = ""
    for i in range(47):
        if result[i]['score'] > max:
            max = result[i]['score']
            emotion = result[i]['name']
    return [emotion,max]
            
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        emotion = request.form["emotion"]
        prompt = request.form["prompt"]
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(prompt),
            temperature=.6,
            max_tokens=100
        )
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    return render_template("index.html", result=result)


def generate_prompt(prompt):
    while True:
        capture_image()

        async def main():
            client = HumeStreamClient("mPASmY2oLMgBm4X1UkE278lU6W8ILuOOvg7m8QFd5ADfucat")
            config = FaceConfig(identify_faces=True)
            async with client.connect([config]) as socket:
                result = await socket.send_file("captured_image.jpg")
                print(result['face'])
                try:
                    result['face']['predictions']
                    print(findEmotion(result['face']['predictions'][0]['emotions']))
                except:
                    print("Faceless")


            asyncio.run(main())
    
    return "Write a response to this following prompt: " + prompt + "if the person was feeling very " + emotion
