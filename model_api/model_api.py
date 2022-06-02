import uvicorn
import numpy as np
import pandas as pd
from fastapi import FastAPI, File, UploadFile
import yolov5.detect as detect
from pathlib import Path
import os
import base64
import gc

description = """
Send here your photos to obtain a recognized ingredients list in return.

Where you can:
* `/predict` to recognize a single ingredient on an uploaded photo file (jpg or png format)
* `/detect` to detect and recognize ingredients on an uploaded photo file (jpg or png format)
"""

tags_metadata = [
    {
        "name": "Predictions",
        "description": "Endpoints that uses our Machine Learning model for recognizing ingredients"
    }
]

app = FastAPI(
    title="Model API",
    description=description,
    version="0.1",
    openapi_tags=tags_metadata
)

LABELS = ['Apple', 'Banana', 'Bell pepper', 'Broccoli', 'Carrot', 'Cheese', 'Cucumber', 'Grape', 'Grapefruit', 'Lemon', 'Mushroom', 'Orange', 'Peach', 'Pear', 'Pomegranate', 'Potato', 'Pumpkin', 'Radish', 'Tomato', 'Zucchini']

# Detection vith YOLO_V5
@app.post("/detect", tags=["Predictions"])
#,response_model = YOLO_Prediction)
async def infer(img_file : UploadFile = File(...)):
    # Cleaning memory
    gc.collect(generation=2)
    contents = await img_file.read()
    with open(f"temp/{img_file.filename}", "wb") as f:
        f.write(contents)
    detect.run(
            weights= 'model/best.pt',  # model.pt path(s)
            source=f"temp/{img_file.filename}",  # file/dir/URL/glob, 0 for webcam
            data='model/data.yaml',  # dataset.yaml path
            imgsz=(640, 640),  # inference size (height, width)
            conf_thres=0.20,  # confidence threshold
            iou_thres=0.45,  # NMS IOU threshold
            max_det=1000,  # maximum detections per image
            device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
            view_img=False,  # show results
            save_txt=True,  # save results to *.txt
            save_conf=True,  # save confidences in --save-txt labels
            project='temp',  # save results to project/name
            name='results',  # save results to project/name
            exist_ok=True,  # existing project/name ok, do not increment
    )
    results_file_path = Path(f"temp/results/labels/{img_file.filename.split('.')[0]}.txt")
    results_file_data = []
    list_labels = [] 
    # open file and write the content in a list
    if os.path.exists(results_file_path):
        with open(results_file_path, 'r') as myfile:
            for line in myfile:
                # remove linebreak which is the last character of the string
                currentLine = line[:-1]
                data = currentLine.split(" ")
                # add item to the list
                results_file_data.append(data)
        # Get the first number in any line (corresponding to the predicted label)
        for i in results_file_data:
            list_labels.append(LABELS[int(i[0])])
        # Getting the image with the prediction boxes
        with open(f"temp/results/{img_file.filename}", 'rb') as f:
            predictions_image_bytes = f.read() # Getting image as binary file
        predictions_image = base64.b64encode(predictions_image_bytes) # Encoding binary file as b64 to avoid compatibility problems through the response
        # Removing the files stored during process
        os.remove(f"temp/results/labels/{img_file.filename.split('.')[0]}.txt")
        os.remove(f"temp/results/{img_file.filename}")
        os.remove(f"temp/{img_file.filename}")
    else:
        list_labels = []
        predictions_image = "No ingredients detected"
    # Format response
    response = {
        "predictions": list_labels,
        "predictions_image": predictions_image
    }
    #return model_output
    return response


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000, debug=True, reload=True)