"""
Used tuned model to predict on new images.
"""
import os
from ultralytics import YOLO


def model(model_name):
    return YOLO(model_name)


def predict(model_object, image_path):
    """
    Predict on new images.
    """
    results = model_object(image_path)
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
            return [image_path, bodybox]
    return None


def predict_on_vector(model_name, image_list):
    """
    Predict on new images.
    """
    model_object = model(model_name)
    results = model_object(image_list)
    results.print()
    results.save()

    return results

