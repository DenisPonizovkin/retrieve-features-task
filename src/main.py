import random
import xlrd
import argparse
import os
import time

from math_model.agent_content import AgentContent as AC
from math_model.target_content import TargetContent as TC
from distance_calculator import DistanceCalculator as DC
from math_model.cluster import ClusterWithCenter as CWC

class CantCreateClusterException(Exception):
    pass

# TODO: singleton "set of contents"
# -------------- MAIN -------------------------------------------
def main():
    while True:
        try:
            __main()
            break
        except CantCreateClusterException:
            next
    # TODO: if test
    # precision = 0
    # for i in range(1, 100):
    #     precision += __main()
    # print(precision / 100)
# -------------- MAIN ACTIONS -------------------------------------------
# 1. читаем Excell
# 2. дробим на 80/20
# 3. по 80 строим модель
# 4. результат модели: user и mask пишем в файлы
# 5. 20 - это для тестов. То, что пойдет в data
# 6. считаем точность
# 7. делаем Excell с результатом
def __main():
    # 1/2
    # read contents
    acontents_train = []
    acontents_test = []
    read_contents(acontents_train, acontents_test)
    #-------------------------------------------------------------------------
    # 3.
    # get from data about agents data about targets
    tcontents = []
    get_targets_contents(acontents_train, tcontents)

    threshold = []
    dists_matrix = create_dist_matrix(acontents_train, "hamming", threshold)
    clusters = create_clusters(acontents_train, dists_matrix, 0.05)
    transitivity_clusters = find_transitivity_cluster(clusters, acontents_train)
    features_set = get_correlated_features(transitivity_clusters, tcontents)

    if len(transitivity_clusters) == 0:
        raise CantCreateClusterException()

    data = dict()
    for c in transitivity_clusters:
        v = 0
        cdata = c.center().data()
        for f in features_set:
            if (f in data.keys()):
                data[f] += cdata[f] / c.size()
            else:
                data[f] = cdata[f]
    agent = AC("main_agent", data)
    rslt = write_results(agent, features_set, acontents_test)
    # TODO: if test
    rslt = topN(acontents_test, features_set, agent)
    f = open("rslt.txt", "w")
    for id in rslt:
        f.write(id + "\n")
    f.close()

    success = []
    read_success(success)
    intersection = rslt.intersection(success)
    print("Precision: " + str(len(intersection) / len(rslt)))
    rslt = topN(acontents_test, features_set, agent)
    intersection = rslt.intersection(success)
    print("Precision: " + str(len(intersection) / len(rslt)))
    # print("Recall: " + str(len(intersection) / len(goods)))
    # return len(intersection) / 10
# -------------- TODO: comment -------------------------------------------
def write_results(agent, features_set, acontents_test):
    id2num = dict()
    fid2num = dict()
    i = 0
    for f in acontents_test[0].data():
        fid2num[i] = f
        i += 1

    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", required=True,
                    help="output path")
    args = vars(ap.parse_args())
    path = args["out"]
    # path = os.path.sep.join([args["dataset"], "training"])
    #user_file = os.path.sep.join(path, "user.txt")
    f = open(path + "\\user.txt", "w")
    for id in fid2num.keys():
        if fid2num[id] in agent.data():
            f.write(str(agent.data()[fid2num[id]]) + "\n")
        else:
            f.write("0\n")
    f.close()

    #f = open(os.path.sep.join(path, "mask.txt"))
    f = open(path + "\\mask.txt", "w")
    for id in fid2num.keys():
        if fid2num[id] in features_set:
            f.write("1\n")
        else:
            f.write("0\n")
    f.close()

    # f = open(os.path.sep.join(path, "data.txt"))
    f = open(path + "\\data.txt", "w")
    cid2num = dict()
    i = 1
    for id in fid2num.keys():
        out = ""
        for c in acontents_test:
            if not c.id() in cid2num:
                cid2num[i] = c.id()
                i += 1
            out += str(c.data()[fid2num[id]]) + " "
        f.write(out + "\n")
    f.close()

    f = open(path + "\\request.txt", "w")
    f.write("1")
    f.close()

    while not os.path.isfile(path + "\\rslt.txt"):
        time.sleep(1)

    f = open(path + "\\request.txt", "w")
    f.write("0")
    f.close()

    rslt = set()
    f = open(path + "\\rslt.txt")
    for line in f:
        print(cid2num[int(line)])
        rslt.add(cid2num[int(line)])
    f.close()

    os.remove(path + "\\rslt.txt")

    return rslt
# -------------- TODO: comment -------------------------------------------
def topN(data, features, agent):
    success = []
    read_success(success)

    dc = DC()
    out = ""
    dists = dict()
    for c in data:
        dists[c.id()] = dc.do("hamming", delta_c(c, features), agent)
    sort = sorted(dists.items(), key = lambda kv: kv[1])
    rslt = set()
    i = 0
    print("-----------------------")
    for (k, v) in sort:
        rslt.add(k)
        print(k)
        i += 1
        if (i >= 10):
            break;
    return rslt
# -------------- TODO: comment -------------------------------------------
def split(all, train, test):
    n = int((80 * len(all)) / 100)
    i = 0
    while i < n:
        id = int(random.random() * len(all)) % len(all)
        if all[id] in train:
            continue
        train.append(all[id])
        i += 1

    for e in all:
        if e in train:
            continue
        test.append(e)
# -------------- TODO: comment -------------------------------------------
def read_success(success):
    wb = xlrd.open_workbook("data/success.xlsx")
    sht = wb.sheet_by_index(0)
    for i in range(sht.nrows):
        tmp = sht.cell_value(i, 0)
        success.append(tmp)
# -------------- TODO: comment -------------------------------------------
def read_contents(contents_train, contents_test):
    contents = []
    wb = xlrd.open_workbook("data/characters.xlsx")
    sht = wb.sheet_by_index(0)
    feature_ids = []
    for i in range(sht.nrows):
        # miss these records
        if (sht.cell_value(i, 1) == 'Итого'):
            continue

        data = dict()
        id = ""
        for j in range(sht.ncols):
            if (i == 0):
                if (j < 3):
                    continue
                feature_ids.append(sht.cell_value(i, j))
            if (j == 1):
                id = sht.cell_value(i, j)
                continue
            if (j < 3):
                continue
            data[feature_ids[j - 3]] = sht.cell_value(i, j)
        if (i > 0):
            c = AC(id, data)
            contents.append(AC(id, data))
    split(contents, contents_train, contents_test)
    # for c in contents:
    #     contents_train.append(c)
# -------------- TODO: comment -------------------------------------------
def create_dist_matrix(contents, dist_name, threshold):
    dists_set = []
    dist_matrix = []
    dc = DC()
    for c1 in contents:
        dists = dict()
        for c2 in contents:
            if (c1.id() == c2.id()):
                continue
            d = dc.do(dist_name, c1, c2)
            dists[c2.id()] = d
            print("d(" + c1.id() + ", " + c2.id() + ") = " + str(d))
            if d in dists_set:
                continue
            dists_set.append(d)
        dist_matrix.append(AC(c1.id(), dists))
    dists_set.sort()
    # id = int(len(dists_set) * 0.002)
    number_of_dists = len(dists_set)
    id = int(number_of_dists * 0.001)
    d = dists_set[id]
    threshold.append(d)
    return dist_matrix
# -------------- TODO: comment -------------------------------------------
def get_by_id(id, contents):
    for c in contents:
        if (c.id() == id):
            return c
# -------------- TODO: comment -------------------------------------------
def create_clusters(contents, dist_matrix, tv):
    clusters = []
    for content_dists in dist_matrix:
        center = get_by_id(content_dists.id(), contents)
        clstr = CWC(center, tv)

        for id in content_dists.data().keys():
            if (center.id() == id):
                continue
            element = get_by_id(id, contents)
            dists = content_dists.data()
            clstr.add(element, dists[id])
        if (clstr.size() > 0):
            clusters.append(clstr)
    return clusters
# -------------- TODO: comment -------------------------------------------
def check_transitivity(cluster, contents):
    dc = DC()
    for c1 in cluster.set():
        for c2 in cluster.set():
            if (c1 == c2):
                continue
            if (dc.do("hamming", get_by_id(c1, contents), get_by_id(c2, contents)) > cluster.tv()):
                return False
    return True
# -------------- TODO: comment -------------------------------------------
def find_transitivity_cluster(clusters, contents):
    transitivity_clusters = []
    for c in clusters:
        if (c.size() <= 1):
            continue
        if (check_transitivity(c, contents)):
            transitivity_clusters.append(c)
            print("cluster with center " + c.to_string())
    return transitivity_clusters
# -------------- TODO: comment -------------------------------------------
def get_targets_contents(acontents_train, tcontents):
    features = []
    for c in acontents_train:
        for f in c.data().keys():
            features.append(f)
        break

    for f in features:
        data = dict()
        for c in acontents_train:
            data[c.id()] = c.data()[f]
        tcontents.append(TC(f, data))
# -------------- RETRIEVE FEATURES THAT CORRELATES -------------------------------------------
def get_correlated_features(clusters, contents):
    threshold = []
    dists_matrix = create_dist_matrix(contents, "pearson", threshold)
    correlated_features = create_clusters(contents, dists_matrix, 0.05)
    features_set = set()
    for cf in correlated_features:
        if (cf.size() > 2):
            for f in cf.set():
                features_set.add(f)
    return features_set
# -------------- FUZZY IMAGINE FUNCTION -------------------------------------------
def delta_c(c, features):
    data = dict()
    cdata = c.data()
    for f in c.data():
        if f in features:
            data[f] = cdata[f]
    c = AC(c.id(), data)
    return c
# -------------- MAIN -------------------------------------------
if __name__ == "__main__":
    main()
