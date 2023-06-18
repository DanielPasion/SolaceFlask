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
            
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        prompt = request.form["prompt"]
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(prompt),
            temperature=.6,
            max_tokens=1000
        )
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    return render_template("index.html", result=result)

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

def generate_prompt(prompt):
    
    while (True):
        global emotion
        emotion = ""
        capture_image()

        async def main():
            client = HumeStreamClient("mPASmY2oLMgBm4X1UkE278lU6W8ILuOOvg7m8QFd5ADfucat")
            config = FaceConfig(identify_faces=True)
            async with client.connect([config]) as socket:
                result = await socket.send_file("captured_image.jpg")
                print(result['face'])
                try:
                    result['face']['predictions']
                    global emotion
                    emotion = findEmotion(result['face']['predictions'][0]['emotions'])
                    print(emotion[0])
                except:
                    print("Faceless")
            
        asyncio.run(main())
    
        return """Your name is Solace and you are an Artifical Intelligence therapist. You are given the task to find the best, most comforting ways to respond to people's issues, concerns, or anything they want to talk about.
        You are most known for your superpower of being able to tell how a person is feeling just by the look of their face. Knowing this, a person just
        spoke to you about """ + prompt + ", give a reponse to them knowing they feel " + emotion[0] + "but dont mention their emotion. Also, you will always remember everything somebody says for a session and will bring it up if mentioned before."
        