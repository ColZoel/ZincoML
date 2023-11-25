"""
Utilize the Roboflow API to download the dataset and model. Images are annotated on Roboflow.
"""


from roboflow import Roboflow
from os import getenv
from dotenv import load_dotenv

load_dotenv()
ROBOFLOW_API_KEY = getenv("ROBOFLOW_API_KEY")


def get_dataset(version=2):
    rf = Roboflow(api_key=ROBOFLOW_API_KEY)
    project = rf.workspace("directory-conversion").project("text-fields")
    dataset = project.version(version).download("yolov8")

    return dataset
# It might be necessary to change the config file to point to the correct paths for the dataset.


def get_roboflow_model(version):
    rf = Roboflow(api_key=ROBOFLOW_API_KEY)
    project = rf.workspace("directory-conversion").project("text-fields")
    model = project.version(version).model()
    return model
