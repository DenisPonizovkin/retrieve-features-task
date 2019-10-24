from math_model.content import Content as Content

# Convert values of features to intervals.
# For that we compute min and max values for each feature.
# Then we build interval (min, min + (max - min)/10, min + 2 * (max - min)/10, ....)
# Then we assign value of feature to (interval id)/10
class Converter:
    def __init__(self, data):
        self.__data = data
        self.__nsteps = 10

    #----------------------------------------------------------------
    # determines min and max for each feature
    #----------------------------------------------------------------
    def __max_min(self):
        minv = []
        maxv = []
        step = []
        for i in range(len(self.__data)):
            cmax = 0
            cmin = 100000000
            for j in range(self.__data[i].fnum()):
                if (self.__data[i].fval(j) < cmin):
                    cmin = self.__data[i].fval(j)
                if (self.__data[i].fval(j) > cmax):
                    cmax = self.__data[i].fval(j)
            minv.append(cmin)
            maxv.append(cmax)
            step.append((cmax - cmin) / self.__nsteps)
        return (minv, maxv, step)

    #----------------------------------------------------------------
    #
    #----------------------------------------------------------------
    def __construct_intervals(self, minv, step):
        intervals = []
        for i in range(self.__data[0].fnum()):
            intrvl = []
            s = minv[i] + step[i]
            for j in range(self.__nsteps):
                intrvl.append(s)
                s = s + step[i]
            intervals.append(intrvl)
        return intervals

    #----------------------------------------------------------------
    #
    #----------------------------------------------------------------
    def cnvr2intvl(self):
        (minv, maxv, step) = self.__max_min()
        intervals = self.__construct_intervals(minv, step)

        cnvrt = []
        for c in self.__data:
            cc = Content() # converted content
            cc.id(c.gid())
            cd = [] # convert data
            for i in range(c.fnum()):
                intrvl = intervals[i]
                min_id = 0
                diff = abs(c.fval(i) - intrvl[0])
                for j in range(len(intrvl)):
                    if (abs(c.fval(i) - intrvl[j]) < diff):
                        diff = abs(c.fval(i) - intrvl[j])
                        min_id = j

                cd.append((min_id + 1) / 10)
            cc.data(cd)
            cnvrt.append(cc)

        return cnvrt

