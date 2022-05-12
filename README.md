# Deep chef app

Deep chef is an online app that helps you find the recipe you need. Take a picture of you fruits and vegetables, the app will recognize it and suggest different recipes. 

## Objective
We used different tools to create the systems interacting with each other in this app:

- Collect data from OpenImageV6 Database with NanoCode012's [OIDv6_ToolKit_Download_Open_Images_Support_Yolo_Format](https://github.com/NanoCode012/OIDv6_ToolKit_Download_Open_Images_Support_Yolo_Format)
- Train a YoloV5 model to recognise ingredients with ultralytics' [yolov5](https://github.com/ultralytics/yolov5)
- Load the model on FastAPI deployed with Heroku
- Get recipes with Spoonacular API 
- The online app created with streamlit deployed with Heroku

## Dataset
A special dataset containing 10 000 images was fetched from OpenImageV6 Database. It is available on RoboFlow at https://app.roboflow.com/ds/asCOwPsjUr?key=1nVXvQ7xsQ . To download and extract use command <br/> `curl -L "https://app.roboflow.com/ds/asCOwPsjUr?key=1nVXvQ7xsQ" > roboflow.zip; unzip roboflow.zip; rm roboflow.zip`

## Prerequisites

### Dependencies
- The source code is written in Python 3.
- To localy run app and API you need Docker and Heroku

## Usage
### Fetch data from OpenImageV6
Follow instruction in NanoCode012's repository. Command `python main.py downloader --classes classes.txt --type_csv all --yoloLabelStyle --multiclasses 1 --limit 600` where classes.txt is the list of ingredients you want.

### Train YoloV5 model
Follow instruction in ultralytics' repository. Command `python train.py --img 640 --batch-size 16 --epochs 50 --save-period 10 --data yolov5s.yaml --weights yolov5s.pt --freeze 10` for example.

### ...


## Team contributors
Quentin Gottafray
Antoine Costes1
Christopher Gbezo
Baptiste Eluard
Léa Boussekeyt

## References
App link: https://deepchef-app.herokuapp.com/
Project presentation: https://docs.google.com/presentation/d/1eNNhturBgnbf9MO3AZ3NRq6GgE9U0vso55SP4R5BbA8/edit?usp=sharing
Project presentation video: 
