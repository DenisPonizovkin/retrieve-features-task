# The weight value of the feature
class FeatureValue:
    def __init__(self, v):
        self.__v = v

    def v(self):
        return self.__v

    def v(self, v):
        self.__v = v
