import math

class DistanceCalculator:
    def __init__(self):
        pass

    def hamming(self, data1, data2):
        res = 0
        keys = data1.data().keys()
        max = 0
        c1 = ""
        c2 = ""
        for key in keys:
            if not (key in data1.data()):
                print(data1.data())
            if not (key in data2.data()):
                print(data2.data())
            if data1.data()[key] > max:
                max = data1.data()[key]
            if data2.data()[key] > max:
                max = data2.data()[key]
            res += abs(data1.data()[key] - data2.data()[key])
            c1 += "(" + key + ", " + str(data1.data()[key]) + ") "
            c2 += "(" + key + ", " + str(data2.data()[key]) + ") "
        print(c1)
        print(c2)
        return res / (max * len(data1.data()))

    def pearson(self, data1, data2):
        keys = data1.data().keys()
        mv1 = 0
        for key in keys:
            mv1 += data1.data()[key]
        mv1 /= len(data1.data())
        mv2 = 0
        for key in keys:
            mv2 += data2.data()[key]
        mv2 /= len(data2.data())

        a = 0
        for key in keys:
            a += (data1.data()[key] - mv1) * (data2.data()[key] - mv2)
        b = 0
        for key in keys:
            b += (data1.data()[key] - mv1) * (data1.data()[key] - mv1)
        c = 0
        for key in keys:
            c += (data2.data()[key] - mv2) * (data2.data()[key] - mv2)

        if (b * c == 0):
            return 1

        r = (2 + a / (math.sqrt(b) * math.sqrt(c))) /3
        return 1 - r

    def do(self, name, data1, data2):
        if (name == "hamming"):
            return self.hamming(data1, data2)
        if (name == "pearson"):
            return self.pearson(data1, data2)
