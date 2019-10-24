from distance_calculator import DistanceCalculator as DC

class ClusterWithCenter:
    def __init__(self, c, tv):
        self.__center = c
        self.__set = dict()
        self.__tv = tv

    def center(self):
        return self.__center

    def add(self, c, dist):
        if (dist <= self.__tv):
            self.__set[c.id()] = dist
        pass

    def size(self):
        return len(self.__set)

    def set(self):
        return self.__set

    def tv(self):
        return self.__tv

    def to_string(self):
        out = self.__center.id() + ": "
        for c in self.__set:
            out += c + " "
        return out

