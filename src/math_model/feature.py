# Presentation of the feature object.
# Feature has identifier, name and weght.

from math_model.feature_value import FeatureValue as FV

class Feature:
    def __init__(self):
        self.__name = ""
        self.__weight = FV()

    def __init__(self, id, weigt):
        self.__id = id
        self.__weight = weigt
