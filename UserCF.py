import math
import random
import csv
from operator import itemgetter

# 数据处理，获得一张map，<user,movies>
# 其中user表示用户，movies表示这个用户有过交互（评分行为）的所有电影集合
def GetData(filePath):
    data = dict()
    with open(filePath, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)  # 跳过标题
        for row in reader:
            userId = row[0]
            movieId = row[1]
            if userId not in data:
                data[userId] = set()
            data[userId].add(movieId)
    return data


# 取数据的1/M为测试组
def SplitData(data, M, k, seed):
    test = dict()
    train = dict()
    random.seed(seed)
    for user, item in data.items():
        if random.randint(0, M) == k:
            test[user] = item
        else:
            train[user] = item
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
    # item_users: <movie:[user1,user2,.....]>
    item_users = dict()
    for u, items in train.items():
        for i in items:
            if i not in item_users:
                item_users[i] = set()
            item_users[i].add(u)
    # 计算用户两两感兴趣的交集
    # N: <user:user感兴趣的电影数>
    # C: < user:<与user感兴趣有交集的user:交集数量> >
    C = dict()
    N = dict()
    for i, users in item_users.items():
        for u in users:
            if u not in N:
                N[u] = 0
            N[u] += 1  # 用户感兴趣的物品数
            for v in users:
                if u == v:
                    continue
                if u not in C:
                    C[u] = dict()
                if v not in C[u]:
                    C[u][v] = 0
                C[u][v] += 1
    # 计算用户相似度矩阵W
    W = dict()
    for u, related_users in C.items():
        W[u] = dict()
        for v, cuv in related_users.items():
            W[u][v] = cuv / math.sqrt(N[u] * N[v])
    return W


# UserCF 基于用户相似度推荐算法
def Recommend(user, train, W, K):
    rank = dict()
    interacted_items = train[user]
    # v:与user相似的用户
    # wuv:相似度
    for v, wuv in sorted(W[user].items(), key=itemgetter(1), reverse=True)[0:K]:
        for i in train[v]:
            if i in interacted_items:
                # we should filter items user interacted before
                continue
            # 与user相似的用户*该用户对该movie的兴趣度（这里为1）
            if i not in rank:
                rank[i]=0
            rank[i] += wuv*1
    return rank


def GetRecommendation(user, N):
    filePath = 'ml-latest-small/ratings.csv'
    # 读取数据
    data = GetData(filePath)
    # print(len(data))

    # 数据分组
    train, test = SplitData(data, 3, 1, 42)
    # print(len(train))
    # print(len(test))

    # 获取用户相似度矩阵W
    W = UserSimilarityV2(train)

    # 计算推荐给某用户的电影，top3
    R = Recommend(user, train, W, 3)
    RN=sorted(R.items(),key=itemgetter(1),reverse=True)[0:N]
    return RN

print(GetRecommendation("1",3))
