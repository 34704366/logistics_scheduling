#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：paddle
@File    ：agv.py
@IDE     ：PyCharm
@Author  ：王晨昊
@Date    ：2022/4/19 10:00
'''
from enum import Enum

import redis
from pydantic import json
from typing import Optional

import asyncio
import time
import uvicorn
import threading

from fastapi import FastAPI, HTTPException, Body


# 初始化FastAPI()
app = FastAPI()

# 小车工作状态


# 距离表
Distance = [
    [0, 1, 1, 1.5, 1.5, 2., 2., 2.5, 2.5, 3, 3, 3.5, 3.5, 4, 4, 4.5,
     8, 8.5, 8.5, 9, 9, 9.5, 4, 4, 6, 10, 10, 7, 6, 13, 6, 6, 8, 7, 15, 13, 8],
    [1, 0, 1, 1.5, 1.5, 2., 2., 2.5, 2.5, 3, 3, 3.5, 3.5, 4, 4, 4.5,
     10, 8.5, 8.5, 9, 9, 9.5, 4, 4, 6, 10, 10, 7, 13, 13, 6, 6, 8, 7, 5, 8, 5],
    [1, 1, 0, 1.5, 1.5, 2., 2., 2.5, 2.5, 3, 3, 3.5, 3.5, 4, 4, 4.5,
     8, 8, 8.5, 8.5, 9, 6, 9.5, 4, 4, 6, 10, 15, 13, 13, 6, 6, 6.5, 7, 15, 8, 5],
    [1, 1, 1, 0, 1.5, 2., 2., 2.5, 2.5, 3, 3, 3.5, 3.5, 4, 4, 4.5,
     8, 8.5, 8.5, 9, 9, 12, 4, 4, 6, 8, 10, 7, 13, 11, 6, 6, 8.5, 7, 15, 8, 5],
    [1, 1, 1, 1.5, 0, 2., 2., 2.5, 2.5, 3, 3, 3.5, 3.5, 4, 4, 4.5, 4.5, 5, 5, 5.5, 6, 6, 6, 6.5, 6.5, 7, 7.5, 7.5, 8, 8,
     8.5, 6, 8, 7, 15, 8, 5],
    [1.5, 1, 1, 1.5, 1.5, 0, 2., 2.5, 2.5, 3, 3, 3.5, 3.5, 4, 4, 4.5, 4.5, 5, 5, 5.5, 5.5, 6, 6, 6.5, 6.5, 7, 7.5, 7.5,
     8, 8, 8.5, 11, 9, 11, 9, 8, 5],
    [1.5, 1, 1, 1.5, 1.5, 2., 0, 2.5, 2.5, 3, 3, 3.5, 3.5, 4, 4, 4.5, 4.5, 5, 5, 5.5, 5.5, 6, 7.5, 8,
     8, 8.5, 8.5, 10, 7, 13, 6, 6, 6.5, 7, 15, 8, 5],
    [2, 1, 1, 1.5, 1.5, 2., 2., 0, 2.5, 3, 3, 3.5, 3.5, 4, 4, 4.5, 4.5, 5, 5, 5.5, 5.5, 6, 6, 6.5, 6, 7, 7.5, 7.5, 8, 8,
     8.5, 8.5, 11, 9, 9.5, 9, 5],
    [2, 1, 1.5, 1.5, 2., 2., 2.5, 0, 3, 3, 3.5, 3.5, 4, 4, 4.5, 4.5, 5,
     8, 8.5, 8.5, 9, 9, 9.5, 4, 4, 6, 10, 10, 7, 13, 6, 6, 6.5, 7, 15, 8, 5],
    [2.5, 1, 1, 1.5, 1.5, 2., 2., 2.5, 2.5, 0, 3, 3.5, 3.5, 4, 4, 4.5, 4.5,
     8, 8.5, 8.5, 9, 9, 9.5, 4, 13, 6, 10, 10, 7, 13, 6, 6, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 4, 4, 4.5,
     8, 8, 8.5, 9, 9, 9, 4, 4, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 4, 4,
     8, 8, 8.5, 3, 9, 9, 9, 4, 4, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 4, 4,
     8, 8, 8.5, 3, 9, 9, 9, 4, 4, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 4, 4,
     8, 8, 8.5, 3, 9, 9, 9, 4, 4, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 4, 4,
     8, 8, 8.5, 3, 9, 9, 9, 4, 4, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 4, 4,
     8, 8, 8.5, 3, 9, 9, 9, 4, 4, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 8, 0.5, 0.5, 0, 2, 3.5, 8, 6,
     8, 8, 8.5, 3, 9, 9, 9, 12, 13, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 4, 4,
     8, 8, 8.5, 3, 9, 9, 9, 5, 4, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 4, 4,
     8, 8, 8.5, 3, 9, 9, 8, 5, 5, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 4, 3,
     8, 8, 8.5, 3, 9, 9, 9, 4, 4, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 4, 12,
     8, 8, 8.5, 3, 9, 9, 9, 4, 4, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 4, 11,
     8, 8, 8.5, 3, 9, 9, 9, 4, 4, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 4, 11,
     8, 8, 8.5, 3, 9, 11, 9, 2, 2, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 4, 10,
     8, 8, 8.5, 3, 9, 11, 9, 4, 4, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 6, 4,
     8, 8, 8.5, 3, 9, 11, 9, 4, 4, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 5, 4,
     8, 8, 8.5, 3, 9, 5, 9, 2, 2, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 4, 3,
     8, 8, 8.5, 3, 9, 5, 9, 3, 3, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 4, 11,
     8, 8, 8.5, 3, 9, 5, 9, 3, 3, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 3, 4,
     8, 8, 8.5, 3, 9, 9, 9, 3, 3, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 4, 4,
     8, 8, 8.5, 3, 9, 9, 9, 4, 4, 6, 10, 10, 7, 5, 13, 6, 5, 8, 7, 15, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 13, 13, 0, 3.5, 3.5, 4, 4, 4.5,
     8, 8, 8.5, 3, 9, 9, 5, 4, 13, 6, 10, 10, 7, 5, 2, 6, 5, 12, 7, 11, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 4, 11, 4.5,
     8, 8, 8.5, 3, 9, 9, 5, 4, 13, 6, 10, 10, 7, 5, 2, 6, 5, 13, 13, 8, 5],
    [2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 4, 4, 12.5,
     8, 8, 8.5, 3, 9, 9, 5, 13, 2, 6, 10, 10, 7, 5, 13, 6, 5, 5, 7, 11, 5],
    [2.5, 2, 11, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 3.5, 3.5, 4, 4, 4.5,
     8, 8, 8.5, 3, 9, 9, 9, 8, 8, 6, 10, 10, 7, 5, 13, 6, 5, 5, 11, 12, 5],
    [2.5, 2, 11, 1.5, 5, 1, 3, 3, 0.5, 0.5, 0, 3.5, 3.5, 4, 4, 12,
     8, 8, 8.5, 3, 9, 9, 9, 7, 4, 6, 10, 10, 11, 5, 13, 6, 5, 5, 7, 8, 5],
    [2.5, 2, 22, 1.5, 1.5, 1, 1, 11, 0.5, 0.5, 0, 3.5, 3.5, 4, 4, 4.5,
     8, 8, 8.5, 3, 9, 2, 2, 6, 13, 6, 10, 23, 7, 5, 13, 6, 5, 5, 7, 8, 5],
    [2.5, 20, 11, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0, 11, 3.5, 2, 5, 9,
     8, 8, 8.5, 3, 9, 9, 9, 2, 3, 6, 10, 10, 7, 8, 13, 1, 5, 8, 1, 8, 5],
]

# 运输物料对应的信息
material_info = [
    {
        'material_id': 'A',
        'max_number_in_cardboard': 100,
    },
    {
        'material_id': 'B',
        'max_number_in_cardboard': 300,
    },
    {
        'material_id': 'C',
        'max_number_in_cardboard': 500,
    },
    {
        'material_id': 'D',
        'max_number_in_cardboard': 50,
    }
]


class Work_status(Enum):
    FREE = 0  # 空闲
    PREPROCESS = 1  # 寻找卡板等
    DELIVER_GOODS = 2  # 送货中
    BACK_TO_FREE_LOCATION = 3  # 正在回小车暂存区


# 位置节点
class Location(Enum):
    # 小车暂存区
    AGV_FREE_LOCATION = 0

    # 激光切割机
    LASER_CUTTER_01 = 1
    LASER_CUTTER_02 = 2
    LASER_CUTTER_03 = 3
    LASER_CUTTER_04 = 4
    LASER_CUTTER_05 = 5
    LASER_CUTTER_06 = 6
    LASER_CUTTER_07 = 7
    LASER_CUTTER_08 = 8
    LASER_CUTTER_09 = 9
    LASER_CUTTER_10 = 10
    LASER_CUTTER_11 = 11
    LASER_CUTTER_12 = 12
    LASER_CUTTER_13 = 13
    LASER_CUTTER_14 = 14
    LASER_CUTTER_15 = 15
    LASER_CUTTER_16 = 16
    LASER_CUTTER_17 = 17
    LASER_CUTTER_18 = 18
    LASER_CUTTER_19 = 19

    # 自动测厚机
    AUTO_THICKNESS_MEASURE_MACHINE_01 = 20
    AUTO_THICKNESS_MEASURE_MACHINE_02 = 21

    # 往复锯
    RECIPROCATE_SAW = 22

    # 砂光机
    SANDER_01 = 23
    SANDER_02 = 24

    # 液压定型机
    HYDRAULIC_MACHINE_01 = 25

    # 激光雕刻机
    LASER_ENGRAVER_01 = 26
    LASER_ENGRAVER_02 = 27

    # 手工包装线
    HAND_PACK_01 = 28
    HAND_PACK_02 = 29
    HAND_PACK_03 = 30

    # 木拼图检测机
    WOODEN_PUZZLE_DETECTION_MACHINE = 31

    # CNC机
    CNC_01 = 32

    # UV喷墨机
    UV_INKJET_MACHINE_01 = 33
    UV_INKJET_MACHINE_02 = 34
    UV_INKJET_MACHINE_03 = 35

    # 卡板库
    CARD_BOARD_WAREHOUSE = 36

    # PreIES来料检测机
    # PRE_IES =


# 单次取/卸货时间
load_time = 1

# 错误代码
ERR_CODE = -500


class Card_board:
    def __init__(self, card_id, agv_id):
        self.card_id = card_id
        self.location = Location.CARD_BOARD_WAREHOUSE
        self.agv_id = agv_id


class Agv:
    # task_id默认=-1，-1表示未分配任务
    def __init__(self, agv_id, task_id=-1):
        self.agv_id = agv_id
        # self.net = pnet.PNet()
        self.work_status = Work_status.FREE
        self.time_to_free = -1  # -1代表已经闲置
        self.time_from_free = -1  # 空闲的时间
        self.location = Location.AGV_FREE_LOCATION
        self.velocity = 2

        self.card_board = []
        self.task_id = task_id

    def get_dict(self):
        return {
            'agv_id': self.agv_id,
            'work_status': {'name': self.work_status.name, 'value': self.work_status.value},
            'time_to_free': self.time_to_free,
            'time_from_free': self.time_from_free,
            'location': {'name': self.location.name, 'value': self.location.value},
            'velocity': self.velocity,
            # 'card_board': self.card_board.get_dict(),
            'task_id': self.task_id
        }

    # 反序列化重建数据
    def reinit_status(self, data):
        destination_enum = ''
        for location in Location:
            if location.value == data['location']['value']:
                destination_enum = location
        self.location = destination_enum

        work_status_enum = ''
        for status in Work_status:
            if status.value == data['work_status']['value']:
                work_status_enum = status
        self.work_status = work_status_enum

        self.task_id = data['task_id']
        self.time_to_free = data['time_to_free']
        self.time_from_free = data['time_from_free']
        self.velocity = data['velocity']

    def print_agv_status(self):
        print(f'agv_id:{self.agv_id},work_status:{self.work_status},'
              f'time_to_free:{self.time_to_free},location:{self.location}')

    # 查询两个位置间的距离
    def _find_distance(self, source: int, destination: int):
        # 注意参数传入int而不是枚举
        return Distance[source][destination]

    # 定期更新车的状态（定期更新）
    def update_agv_status(self, time_interval, time_to_back):
        # 如果小车至上次更新为止处于工作状态
        if self.work_status != Work_status.FREE:
            # 如果任务还没有结束
            if self.time_to_free > time_interval:
                self.time_to_free -= time_interval
            else:  # 如果任务到结束的时间了
                self.time_to_free = -1
                self.work_status = Work_status.FREE
                self.task_id = -1

                # 更新自从空闲以来的时间
                self.time_from_free = time_interval - self.time_to_free

        # 如果小车空闲但是没有处于停车场
        elif self.location != Location.AGV_FREE_LOCATION:
            # 累加自从空闲以来的时间
            self.time_from_free += time_interval

            # 如果空闲等待的时间到了time_to_back
            if self.time_from_free >= time_to_back:
                self.work_status = Work_status.BACK_TO_FREE_LOCATION
                # 计算距离
                distance = self._find_distance(self.location.value, Location.AGV_FREE_LOCATION.value)
                # 计算行驶时间
                self.time_to_free = distance / self.velocity
                self.location = Location.AGV_FREE_LOCATION

    # 更改车的状态（由任务分配而修改）
    def change_agv_status(self, destination, work_status, time_to_free):
        destination_enum = ''

        for location in Location:
            if location.value == destination:
                destination_enum = location
        print(destination_enum)

        self.location = destination_enum
        self.work_status = work_status
        self.time_to_free = time_to_free

        self.time_from_free = 0


class Task:
    def __init__(self, task_id, source, destination, material_id, material_number):
        self.task_id = task_id
        self.source = source  # 源地点
        self.destination = destination  # 目的地点
        self.material_id = material_id  # 物料id
        self.material_number = material_number  # 物料数量

    def get_dict(self):
        return {
            'task_id': self.task_id,
            'source': self.source,
            'destination': self.destination,
            'material_id': self.material_id,
            'material_number': self.material_number
        }

    def compute_agv_numbers(self):
        pass
        # 根据运送物料的种类和物料的数量，来计算需要运送多少次


class Task_list:
    def __init__(self):
        self.list = []
        self.id_sequence = 0

    # 序列化
    def get_dict(self):
        list = []
        for item in self.list:
            dict = item.get_dict()
            list.append(dict)

        return {
            'list': list,
            'id_sequence': self.id_sequence
        }

    def _reinit_list(self):
        self.list = []

    def update_list_info(self, list_info):
        # 初始化列表
        self._reinit_list()
        for item in list_info['list']:
            self._rebuild_task(item)

    # 重建任务数据
    def _rebuild_task(self, data):
        if data['task_id'] == None:
            print('_rebuild_task error, task_id is null')
            return ERR_CODE
        task = Task(data['task_id'], source=data['source'], destination=data['destination'],
                    material_id=data['material_id'], material_number=data['material_number'])
        self.list.append(task)
        return task

    # 添加任务到list中
    def add_task(self, task_id, source, destination, material_id, material_number):
        task = Task(task_id, source, destination, material_id, material_number)
        self.list.append(task)
        return task

    # 选择任务的算法
    def _select_task(self):
        if self.list.__len__() == 0:
            print('队列无任务')
            return ERR_CODE
        task = self.list.pop(0)
        return task

    # 选择指定的任务
    def _select_task_specify(self, task_id):
        for index in range(len(self.list)):
            if self.list[index].task_id == task_id:
                task = self.list.pop(index)
                return task
        print('_select_task_specify error, doesn\'t exist this task_id')
        return ERR_CODE
    # 查询两个位置间的距离
    def _find_distance(self, source: int, destination: int):
        # 注意参数传入int而不是枚举
        return Distance[source][destination]

    # 处理一项任务
    def process_task(self, agv_list, task_id):
        task = ''
        if task_id == None or task_id == -1:
            # 选择一项任务来处理
            task = self._select_task()
        else:
            task = self._select_task_specify(task_id)
        if task == ERR_CODE:
            return {
                'task': -1,
                'agv_id': -1,
                'process_time': -1,
                'error': '任务队列错误'
            }

        # 如果卡板数量大于1

        # 选择一辆合适的agv车
        agv, distance_to_source = agv_list.select_agv(task.source, task.task_id)

        source = int(task.source)
        destination = int(task.destination)

        distance_source_to_dest = self._find_distance(source, destination)


        # 计算总距离
        distance = distance_to_source + distance_source_to_dest
        # 计算行驶时间
        drive_time = distance / agv.velocity

        time = drive_time + load_time

        work_status = Work_status.DELIVER_GOODS

        agv.change_agv_status(destination, work_status, time)

        result = {
            'task': task.task_id,
            'agv_id': agv.agv_id,
            'process_time': time
        }

        return result


    def print_task_list(self):
        for task in self.list:
            print(f'task_id:{task.task_id}, source:{task.source}, destination:{task.destination}'
                  f'material_id:{task.material_id}')


# 车间内现有的agv车
class Agv_list:
    def __init__(self):
        self.list = []
        self.id_sequence = 0

    # 序列化
    def get_dict(self):
        list = []
        for item in self.list:
            dict = item.get_dict()
            list.append(dict)

        return {
            'list': list,
            'id_sequence': self.id_sequence
        }

    def _reinit_list(self):
        self.list = []

    def update_list_info(self, list_info):
        # print(list_info['list'])
        # 初始化列表
        self._reinit_list()
        for item in list_info['list']:
            self._rebuild_agv(item)

    # 恢复车队数据
    def _rebuild_agv(self, data):
        if data['agv_id'] == None:
            print('_rebuild_agv error, agv_id is null')
            return ERR_CODE
        agv = Agv(data['agv_id'], data['task_id'])
        # 重建数据
        agv.reinit_status(data)
        self.list.append(agv)
        return agv

    # 添加一辆agv车到车队
    def add_agv(self, agv_id, task_id=-1):
        if agv_id == self.id_sequence:
            self.id_sequence += 1
        # 初始化一辆车
        agv = Agv(agv_id, task_id=task_id)
        # 添加到车队中
        self.list.append(agv)
        return agv

    # 查询两个位置间的距离
    def _find_distance(self, source: int, destination: int):
        # 注意参数传入int而不是枚举
        return Distance[source][destination]


    # 选择一辆合适的agv车
    def select_agv(self, source, task_id):
        print(f'开始找辆车，taskid:{task_id},source:{source}')
        index = 0  # 用来寻找最近的车辆
        _distance = 65535
        has_agv = 0  # flag
        agv = ''
        for i in range(len(self.list)):
            agv = self.list[i]
            # 如果车辆未分配任务且处于闲置
            if agv.work_status == Work_status.FREE and agv.task_id == -1:
                # 找到车辆
                has_agv = 1

                # 计算出离源库的距离
                distance_to_source = self._find_distance(agv.location.value, source)
                # 如果距离小于distance, distance置为该距离，index置为i
                if distance_to_source < _distance:
                    index = i
                    _distance = distance_to_source
                #

        # 如果找到闲置且无分配任务的车
        if has_agv == 1:
            agv = self.list[index]
            print(f'找到了距离源库最近的车辆，location:{agv.location.name}, distance:{_distance}')
            setattr(agv, 'task_id', task_id)
            return self.list[index], _distance
        else:
            # print('没找到')
            agv = self.add_agv(agv_id=self.id_sequence, task_id=task_id)
            _distance = self._find_distance(agv.location.value, source)
            # 创建一个新的车并且指定为该任务所有
            return agv, _distance

    def print_agv_list(self):
        index = 0
        for agv in self.list:
            print(f'No.{index} --- agv location is `{agv.location.name}`'
                  f',work_status is `{agv.work_status.name}'
                  f'`,task_id is `{agv.task_id}`, time_to_free is {agv.time_to_free}')
            index += 1

    def update_status(self, time_interval, time_to_back):
        for agv in self.list:
            agv.update_agv_status(time_interval=time_interval, time_to_back=time_to_back)


result = {
    'task': '',
    'status': '',
    'process_time': ''
}


def loop_update_status():
    # 连接redis
    # cache = redis.StrictRedis('127.0.0.1', 6379)
    global cache
    # ##初始化
    task_list = Task_list()
    agv_list = Agv_list()

    # print('info is ',agv_list_info)

    count = 0
    while True:
        # 程序中显示的时间
        log_process_time = 0.5
        time.sleep(log_process_time)

        # 注意一定要加异步锁
        global lock
        lock.acquire()
        # 从cache中取出agv_list信息并反序列化
        task_list_info = eval(cache.get('task_list'))
        task_list.update_list_info(task_list_info)
        agv_list_info = eval(cache.get('agv_list'))
        agv_list.update_list_info(agv_list_info)
        # print('info is ',agv_list_info)

        time_to_back = 5  # 空闲多久回到缓存区

        # await asyncio.sleep(interval_time_update_status)

        interval_time_update_status = 0.2  # 更新状态的时间
        agv_list.update_status(interval_time_update_status, time_to_back)

        count += 1

        # # 处理任务的间隔时间（单位：次更新状态的时间）
        # interval_time_process_task = 5
        # if count % interval_time_process_task == 0:
        #     # print(f"outside{temp}")
        #     print(f'该处理任务了,当前任务队列长度{task_list.list.__len__()}')
        #
        #     print(task_list)
        #     task_list.process_task(agv_list, -1)  # -1代表根据算法选择一个任务
        #
        #     agv_list.print_agv_list()

        # 将维护完毕的数据写入cache中
        cache.set('agv_list', str(agv_list.get_dict()))
        cache.set('task_list', str(task_list.get_dict()))

        lock.release()

@app.get("/logistics/hello")
def hello():
    print('收到get请求了')
    return {
        'statusCode': 200
    }


@app.get("/logistics/name")
def nameEE():
    print('name')
    global cache
    cache.set('name', 'okokokokokokokoookkkkkkk')
    return {
        'result': 'ok'
    }


@app.post('/logistics/task')
def add_task(data: Optional[str] = Body(None)):
    # print(data)
    # 将data字符串转为字典型
    data = eval(data)

    # 加异步锁
    lock.acquire()
    # 从redis读取任务列表
    task_list_info = eval(cache.get('task_list'))
    agv_list_info = eval(cache.get('agv_list'))

    print('读到的信息：',task_list_info)
    task_list = Task_list()
    task_list.update_list_info(task_list_info)
    agv_list = Agv_list()
    agv_list.update_list_info(agv_list_info)
    task_list.add_task(task_id=data['task_id'], source=data['source'],
                       destination=data['destination'], material_id=data['material_id'],
                       material_number=data['material_number'])
    task_list.print_task_list()
    print(f'收到请求，task_list 长度:{task_list.list.__len__()}, add:{task_list}')

    # 写回redis中
    print('处理后的信息：',str(task_list.get_dict()))
    result = task_list.process_task(agv_list, data['task_id'])

    cache.set('task_list', str(task_list.get_dict()))
    cache.set('agv_list', str(agv_list.get_dict()))

    lock.release()

    return result

# 连接redis
cache = redis.StrictRedis('127.0.0.1', 6379)
lock = threading.Lock()  # 创建一个锁

if __name__ == '__main__':

    agv_list = Agv_list()
    task_list = Task_list()

    for i in range(3):
        agv_list.add_agv(i)
    agv_list.list[0].location = Location.LASER_CUTTER_07
    agv_list.list[2].location = Location.SANDER_01
    agv_list.id_sequence = 3

    # agv, distance = agv_list.select_agv(source=Location.HAND_PACK_03.value, task_id=2)
    #
    # agv.print_agv_status()
    # agv_list.print_agv_list()

    task_id = 'a101'
    source = 5
    destination = 18
    material_id = 'AB_132255-01'
    material_number = 1

    task_list.add_task(task_id=task_id, source=source,
                       destination=destination, material_id=material_id,
                       material_number=material_number)

    task_id = 'a102'
    source = 2
    destination = 19
    material_id = 'SE-0173-89'
    material_number = 1
    task_list.add_task(task_id=task_id, source=source,
                       destination=destination, material_id=material_id,
                       material_number=material_number)

    task_id = 'a103'
    source = 1
    destination = 23
    material_id = 'GK-0173-29'
    material_number = 1
    task_list.add_task(task_id=task_id, source=source,
                       destination=destination, material_id=material_id,
                       material_number=material_number)

    task_list.print_task_list()

    cache.set('task_list',str(task_list.get_dict()))
    cache.set('agv_list',str(agv_list.get_dict()))


    # 创建子线程调用定时更新状态函数
    update_thread = threading.Thread(target=loop_update_status)
    update_thread.start()

    # 启动api服务
    uvicorn.run(app='api:app', host="0.0.0.0", port=8000, reload=True, debug=True)
