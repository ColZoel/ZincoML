"""
Utilize the Roboflow API to download the dataset and model. Images are annotated on Roboflow.
"""


from roboflow import Roboflow
from os import getenv
from dotenv import load_dotenv
import os
load_dotenv()
ROBOFLOW_API_KEY = getenv("ROBOFLOW_API_KEY")


def yolov8():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'yolov8')


def get_dataset(version=2, location=yolov8()):
    rf = Roboflow(api_key=ROBOFLOW_API_KEY)
    project = rf.workspace("directory-conversion").project("text-fields")
    dataset = project.version(version).download("yolov8", location=location)

    return dataset
# It might be necessary to change the config file to point to the correct paths for the dataset.


def get_model(version):
    rf = Roboflow(api_key=ROBOFLOW_API_KEY)
    project = rf.workspace("directory-conversion").project("text-fields")
    model = project.version(version).model()
    return model
