"""
Used tuned model to predict on new images.
"""
import os
from ultralytics import YOLO
import torch
import pandas as pd
from utils.dirs import recent_model
from utils.config import load_config
import numpy as np

def to_gpu(model):
    if not torch.backends.mps.is_available():
        if not torch.backends.mps.is_built():
            print("MPS not available because the current PyTorch install was not "
                  "built with MPS enabled.")
        else:
            print("MPS not available because the current MacOS version is not 12.3+ "
                  "and/or you do not have an MPS-enabled device on this machine.")

    else:
        # Move your model to mps just like any other device
        return model.to(torch.device("mps"))


def predict_text_fields(image_path):
    """
    Predict on new images. can be a single image or a list of images.
    Accepts .jpg, .jpeg, .png, .gif, .bmp, .ico, .tiff, .tif, .webp and .svg
    """
    model_path = get_model_path()
    model = YOLO(model_path,
                 task='detect')
    results = model.predict('/Users/collinzoeller/city_directories/AZ/1994_ROC_AZ/1994_ROC_1__0339.jpg',
                            stream=True, conf=0.5, classes=1, device='mps')

    results_list = [[r.path] + r.boxes.xywh[0].tolist() for r in results]
    return results_list


def get_model_path():
    model_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                              'yolov8', 'weights')
    if os.path.isdir(model_path):
        model_path = recent_model(model_path)
    else:
        raise ValueError(f'Bad file path. The model path {model_path} should exist, but does not.')
    return model_path


# predict_text_fields('/Users/collinzoeller/PycharmProjects/ZincoML/image_segmentation/yolov8/weights/8v1.onnx',
#                     '/Users/collinzoeller/city_directories/AZ/test')
