"""
Used tuned model to predict on new images.
"""
import os
from ultralytics import YOLO
import torch
from utils.dirs import recent_model


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
    results = model.predict(image_path,
                            stream=True, conf=0.5, device='mps')

    results_list = []
    for r in results:
        try:
            bodyidx = r.boxes.cls.tolist().index(1)
        except:
            print(f'{os.path.basename(r.path)}:  No body class in image.')
            continue
        boxes = r.boxes.xyxy.tolist()[bodyidx]
        path = r.path
        results_list += [[path] + boxes]

    return results_list


def get_model_path():
    model_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                              'yolov8', 'weights')
    if os.path.isdir(model_path):
        model_path = recent_model(model_path)
    else:
        raise ValueError(f'Bad file path. The model path {model_path} should exist, but does not.')
    return model_path
