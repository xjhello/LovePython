#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2021/7/20 16:08
@Author  : Xu_Jian
"""
import math

# a = [1,2,13,23,12,312,3]
# a = sorted(a)


def two_point_distance(x1, y1, x2, y2):
    """两点间距离"""
    dis = math.sqrt(math.pow((x1 - x2), 2) + math.pow((y1 - y2), 2))
    return dis


def calculate_stop_point(point_list, robot_x, robot_y):
    """
    根据当前车位置算出边界的停止点
    point_list = [[1,2], [2,2]]
    """
    first_big = two_point_distance(robot_x, robot_y, point_list[0][0], point_list[0][1])
    second_big = two_point_distance(robot_x, robot_y, point_list[1][0], point_list[1][1])
    # first_big = -1
    # second_big = -1
    first_big_index = -1
    second_big_index = -1
    for index, value in enumerate(point_list):
        dis = two_point_distance(robot_x, robot_y, point_list[index][0], point_list[index][1])
        print(">> {}  dis {} first_big: {}  second_big:{}".format(index, dis, first_big, second_big))
        if dis > first_big:
            second_big = first_big
            second_big_index = first_big_index
            first_big = dis
            first_big_index = index
        elif dis > second_big:
            second_big = dis
            second_big_index = index
    print(first_big_index, second_big_index)
    print("222", first_big, second_big)

# def find_Second_large_num(num_list):
#     '''''
#     找出数组中第2大的数字
#     '''
#     #直接排序,输出倒数第二个数即可
#     tmp_list=sorted(num_list)
#     print( 'Second_large_num is:', tmp_list[-2])
#     #设置两个标志位一个存储最大数一个存储次大数
#     #two存储次大值，one存储最大值，遍历一次数组即可，先判断是否大于one，若大于将one的
#     #值给two，将num_list[i]的值给one；否则比较是否大于two，若大于直接将num_list[i]的
#     #值给two；否则pass
#     one=num_list[0]
#     two=num_list[0]
#     for i in range(1,len(num_list)):
#         if num_list[i]>one:
#           two=one
#           one=num_list[i]
#         elif num_list[i]>two:
#             two=num_list[i]
#         else:
#           pass
#     print( 'Second_large_num is:', two)
#
# a = [[2, 1], [4,1], [4,-1.1], [1, -2.2]]
# calculate_stop_point(a,0,0)
# find_Second_large_num([32,343,4,56,123])

import threading
def v():
    pass
t_name = threading.Thread(target=v, name="uusadas")
print(t_name)
t_name.start()