from math_model.feature import Feature as FV

class Content:
    # set id of content
    def __init__(self, id, data):
        self.__id = id
        self.__data = data

    # get id of content
    def id(self):
        return self.__id

    # set data
    def data(self, d):
        self.__data = d

    # number of features
    def fnum(self):
        return len(self.__data)

    # value of the feature with the id
    def fval(self, id):
        return self.__data[id]

    def data(self):
        return self.__data



    def to_string(self):
        out = str(self.__id) + ": "
        out += "[ "
        for key in self.__data:
            out += "(" + key + " | " + str(self.__data[key]) + "), "
        out = out[:-2]
        out += "]"
        return out

