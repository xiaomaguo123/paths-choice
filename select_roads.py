#_*_coding:utf-8_*_
import networkx as nx
import osmnx as ox
import geopandas as gpd
from shapely.geometry import *
import matplotlib.pyplot as plt
import numpy as np
import random
from sklearn.preprocessing import MinMaxScaler

def save_geo_data(placeName,type):
    """
    :param placeName: 地点名称
    :param type: 获取路网类型
    :return:
    """
    G = ox.graph_from_place(placeName, network_type=type)
    # ox.save_graphml(G,placeName)
    #print list(nx.connected(G))

def load_data(graph_file,start,end,depth = 30):
    """
    :param graph_file: 路网文件
    :param start: 开始
    :param end: 结束
    :param depth: 遍历深度，主要可以控制输出path数量
    :return: paths
    """
    G = nx.read_graphml(graph_file)
    paths = list(nx.all_simple_paths(G,start,end,depth))
    return paths
    # graph_dict = nx.to_dict_of_dicts(G)
    # for key,value in graph_dict.items():
    #     for v in value.keys():
    #         print key + " -> " + v

def map_data_process(node_file_name):
    """
    :param node_file_name:
    :return:
    """
    node_df = gpd.read_file(node_file_name)
    len_rows = node_df.shape[0]
    weather = []
    trans_stats = []
    for i in range(len_rows):
        #这里随机生成测试数据，天气由1-5整数表示，越高代表天气越糟
        #交通数据1-5 ，越高表示天气越糟
        weather.append(random.randint(1,5))
        trans_stats.append(random.randint(1,5))
    node_df["weather"] = weather
    node_df["trans"] = trans_stats

    return node_df

def compute_score(info_df):
    """
    :param info_df:
    :return:
    """
    scaler = MinMaxScaler()
    info_df['0-1-weather'] = scaler.fit_transform(info_df['weather'].values.reshape(-1, 1))
    info_df['0-1-trans'] = scaler.fit_transform(info_df['trans'].values.reshape(-1, 1))
    info_df['0-1-route_length'] = scaler.fit_transform(info_df['route_length'].values.reshape(-1, 1))

    #设置权重w: 天气 0.1, 交通0.3,距离0.6
    info_df['score'] = info_df.apply(lambda x: 0.1*x['0-1-weather'] + 0.3 * x['0-1-trans'] +
                                     0.6 * x['0-1-route_length'], axis=1)
    return info_df

def process_factors(paths,node_df):
    """
    :param weather:节点上的天气状况
    :param trans_stats: 节点的拥堵指数
    :param dis: 两个节点的路程
    :return:
    """
    #存储路径地理信息
    route = []
    #存储路径平均天气信息
    weather = []
    #存储路径平均交通拥堵状态信息
    trans = []
    #存储路径长度
    route_length = []
    start_point = node_df[node_df["osmid"] == paths[0][0]]["geometry"].values[0]
    end_point = node_df[node_df["osmid"] == paths[0][-1]]["geometry"].values[0]
    # print start_point
    # print end_point
    for path in paths:
        route_line = []
        w_sum = 0
        t_sum = 0
        count = len(path)
        for osmid in path:
            p = node_df[node_df["osmid"] == osmid]["geometry"].values[0]
            w_sum += node_df[node_df["osmid"] == osmid]["weather"].values[0]
            t_sum += node_df[node_df["osmid"] == osmid]["trans"].values[0]
            route_line.append([p.x,p.y])
        weather.append(float(w_sum)/count)
        trans.append(float(t_sum)/count)
        route_geo = LineString(route_line)
        route_length.append(route_geo.length)
        route.append(route_geo)
    # print weather
    # print trans
    # print route_length
    # print route[0]
    candidate_route_df = gpd.GeoDataFrame({"geometry":route,"weather":weather,
                                           "trans":trans,"route_length":route_length})
    # print candidate_route_df.info()
    print "计算得分中。。。。。。"
    reslut_df = compute_score(candidate_route_df)
    return reslut_df,start_point,end_point



if __name__ == '__main__':
    #下载地图
    #save_geo_data("Rouen","drive")
    #处理地图
    print ("处理地图中。。。。。。")
    node_df = map_data_process("./data/nodes/nodes.shp")
    #找寻路径
    print ("找寻路径中。。。。。。。")
    # #开始和结束点的osmid
    graph_file = "/Users/maguorui/PycharmProjects/订单_1/Order/data/Rouen"
    start_point = "279400197"
    end_point = "357372282"
    paths = load_data(graph_file,start_point,end_point)
    # paths = []
    # with open("test.txt") as f:
    #     lines = f.readlines()
    #     for line in lines:
    #         line = line.strip("\n").strip("[").strip("]")\
    #             .replace("'","").replace(" ","").split(",")
    #         # print line
    #         paths.append(line)
    print ("处理路径中。。。。。。。。")
    result_df,start,end = process_factors(paths,node_df)
    print ("处理完成。。。。。。。")
    final_df = gpd.GeoDataFrame(result_df.loc[[result_df['score'].idxmin()]])
    # print final_df.info()
    point_df = gpd.GeoDataFrame({"geometry":[start,end]})


    # shp_node = gpd.read_file("./data/nodes/nodes.shp")
    # node_geo = []
    # for o_id in osmid[0]:
    #     p = shp_node[shp_node["osmid"] == o_id]["geometry"].values[0]
    #     #print p
    #     node_geo.append([p.x,p.y])
    #
    # #POINT (1.0938664 49.4539501)
    # #POINT (1.0939567 49.454389)
    shp = gpd.read_file("./data/edges/edges.shp")
    fig, ax = plt.subplots(figsize=(20, 10))
    ax = shp.plot(ax=ax, color="gray")
    result_df.plot(ax=ax,color = "blue")
    final_df.plot(ax=ax,color = "r")
    point_df.plot(ax=ax,color = "r")
    plt.show()





