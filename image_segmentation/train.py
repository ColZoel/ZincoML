"""

"""

from ultralytics import YOLO
from get_roboflow import get_dataset, yolov8
import yaml
import os
import torch


def check_data_version(data_version, datayaml):
    """
    Check if data version is valid.
    """
    with open(datayaml) as f:
        config = yaml.safe_load(f)
        version = config['roboflow']['version']
        if version != data_version:
            return False
        return True


def train(data_version, epochs=100, resume=False, dataset_location=yolov8()):

    """
    Train model with YOLOv8.
    :param data_version: version of training data to run
    :param epochs: number of epochs to train
    :param resume: whether to resume training from last checkpoint
    :param dataset_location: location to save dataset (if not already downloaded)
    """
    dataset = os.path.join(dataset_location, "data.yaml")
    if not os.path.isfile(dataset):
        dataset = get_dataset(data_version, dataset_location)
    elif not check_data_version(data_version, dataset):
        dataset = get_dataset(data_version, dataset_location)
    model = YOLO('yolov8n.pt').to(torch.device("mps"))
    model.train(data=dataset, epochs=epochs,
                device='mps', imgsz=640,
                save=True, save_period=50,
                resume=resume, batch=16)
    return model


def validate(model):
    """
    Validate model.
    """
    results = model.val()
    results.print()
    results.save()
    return results


def save_model(model, model_name):
    """
    Save model.
    """
    print(f'Model saved as {model_name}.')
    model.export(format='onnx', dynamic=False, simplify=False, out=model_name)


def train_pipeline(data_version, epochs=1, resume=False, dataset_location=None, debug=False):
    """
    Train model with YOLOv8, validate and save.
    :param data_version: version of training data to run
    :param epochs: number of epochs to train
    :param resume: whether to resume training from last checkpoint
    :param dataset_location: location to save dataset (if not already downloaded)
    :param debug: whether to run in debug mode (1 epoch)
    """

    if debug:
        epochs = 1
        model_name = f'yolov8n_dirs_v{data_version}_debug.onnx'
    else:
        model_name = f'yolov8n_dirs_v{data_version}.onnx'
    if dataset_location is None:
        dataset_location = yolov8()
    model = train(data_version, epochs=epochs, resume=resume, dataset_location=dataset_location)
    validate(model)
    save_model(model, model_name)
    return model


train_pipeline(2, epochs=1, debug=True)


