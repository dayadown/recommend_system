import math
import random


# 将数据分为M组，其中M-1组为训练组，1组为测试组
def SplitData(data, M, k, seed):
    test = []
    train = []
    random.seed(seed)
    for user, item in data:
        if random.randint(0, M) == k:
            test.append([user, item])
        else:
            train.append([user, item])
    return train, test


# 召回率
def Recall(train, test, N):
    hit = 0
    all = 0
    for user in train.keys():
        tu = test[user]
        rank = GetRecommendation(user, N)
        for item, pui in rank:
            if item in tu:
                hit += 1
        all += len(tu)
    return hit / (all * 1.0)


# 准确率
def Precision(train, test, N):
    hit = 0
    all = 0
    for user in train.keys():
        tu = test[user]
        rank = GetRecommendation(user, N)
        for item, pui in rank:
            if item in tu:
                hit += 1
        all += N
    return hit / (all * 1.0)


# 覆盖率
def Coverage(train, test, N):
    recommend_items = set()
    all_items = set()
    for user in train.keys():
        for item in train[user].keys():
            all_items.add(item)
        rank = GetRecommendation(user, N)
        for item, pui in rank:
            recommend_items.add(item)
    return len(recommend_items) / (len(all_items) * 1.0)


# 计算用户相似度v1
# (N(u)&N(v)).len  /  N(u).len*N(v).len
def UserSimilarityV1(train):
    W = dict()
    for u in train.keys():
        for v in train.keys():
            if u == v:
                continue
            W[u][v] = len(train[u] & train[v])  # 时间浪费在这一步，很多train[u] & train[v]=0，白算
            W[u][v] /= math.sqrt(len(train[u]) * len(train[v]))
    return W


# 计算用户相似度v2，
# 记录物品到用户的倒排表，通过倒排表可以很清楚得算出所有的(N(u)&N(v)).len情况
def UserSimilarityV2(train):
    # 创建物品到用户的倒排表
    item_users = dict()
    for u, items in train.items():
        for i in items.keys():
            if i not in item_users:
                item_users[i] = set()
            item_users[i].add(u)
    # 计算用户两两感兴趣的交集
    C = dict()
    N = dict()
    for i, users in item_users.items():
        for u in users:
            N[u] += 1  # 用户感兴趣的物品数
            for v in users:
                if u == v:
                    continue
                C[u][v] += 1
    # 计算用户相似度矩阵W
    W = dict()
    for u, related_users in C.items():
        for v, cuv in related_users.items():
            W[u][v] = cuv / math.sqrt(N[u] * N[v])
    return W


def GetRecommendation(user, N):
    return []
