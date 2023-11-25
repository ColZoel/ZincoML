"""
 Use dataset from Roboflow to train own model with YOLOv8. Most of this should be done in Colab instead of locally
  in order to use the GPU.

"""
import ultralytics
import os
from PIL import Image
from ultralytics import YOLO
# ultralytics.settings.update({'datasets_dir': '/content/drive/MyDrive/'})
from get_model import get_dataset, get_roboflow_model
import yaml
ultralytics.checks()


def check_data_version(data_version, datayaml):
    """
    Check if data version is valid.
    """
    with open(datayaml) as f:
        config = yaml.safe_load(f)
        version = config['version']
        if version != data_version:
            return False
        return True


def train_model(data_version, epochs=10):
    """
    Train model with YOLOv8.
    """
    if not os.path.isfile("image_segmentation/data.yaml"):
        dataset = get_dataset(data_version)
    elif not check_data_version(data_version, "image_segmentation/data.yaml"):
        dataset = get_dataset(data_version)
    else:
        dataset = "image_segmentation/data.yaml"
    model = YOLO('yolov8n.pt')
    model.train(dataset, epochs=epochs, device='mps', imgsz=640)
    return model


def validate(model):
    """
    Validate model.
    """
    results = model.val()
    results.print()
    results.save()


def save_model(model, model_name):
    """
    Save model.
    """
    print(f'Model saved as {model_name}.')
    model.export(format='onnx', dynamic=False, simplify=False, out=model_name)


