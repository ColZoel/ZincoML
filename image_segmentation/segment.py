"""
Used tuned model to predict on new images.
"""
import os
from ultralytics import YOLO


def predict(model_name, image_path):
    """
    Predict on new images.
    """
    model = YOLO(model_name)
    results = model(image_path)
    results.print()
    results.save()

    return results


def predict_text_fields(model_name, image_path):
    """
    Predict on new images.
    """
    results = predict(model_name, image_path)
    for result in results:
        if result['class'] == 'body':
            bodybox = result.boxes.xywh
            print(bodybox)
            return bodybox


    return None