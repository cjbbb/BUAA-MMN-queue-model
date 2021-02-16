import random
from queue import Queue
import time

import numpy as npy
import math

from Person import Person
from Table import Table


class MM:
    def __init__(self, arrive_time, serve_time, custom_num, table_number):  # done
        # 读入
        self.average_arrive_time = arrive_time  # 平均到达时间
        self.average_serve_time = serve_time  # 平均服务是见
        self.custom_num = custom_num  # 顾客数量
        self.table_number = table_number  # 窗口数量
        # 输出
        self.finish = 0  # finish = 1 not finish = 0
        self.now_time = 0  # 现在的时间
        self.average_wait_time = 0  # 平均等待时间
        self.average_people_number = 0  # 平均顾客数
        # 队列
        self.arrive_space = []  # 到达时间间隔（泊松分布）
        self.arrive_time = []  # 到达时间
        self.serve_time = []  # 服务时间（指数分布）
        self.tableList = []  # 窗口列表
        self.personList = []  # 顾客列表
        self.eventTime = []  # 记录时间
        self.queue_time = 0  # 用于计算平均等待人数
        self.wait_time = 0  # 用于计算平局等待时间
        self.nowPersonNumber = 0  # 用于计算平均等待时间

    def maopao(self):  # 冒泡排序
        n = len(self.personList)
        for i in range(n - 1):
            for j in range(i + 1, n):
                if self.personList[i].arrive_time > self.personList[j].arrive_time:  # 通过交换让最小的在最前面
                    self.personList[i], self.personList[j] = self.personList[j], self.personList[i]

    def produce(self):  # 生成 时间间隔

        # 生成指数分布的时间分布
        for i in range(0, self.custom_num):
            arrive_time = -1 * self.average_arrive_time * math.log(random.uniform(0, 1))
            self.arrive_space.append(arrive_time)

        # 到达时间 = 上一人到达时间 + 到达时间间隔
        self.arrive_time.append(self.arrive_space[0])
        for i in range(1, self.custom_num):
            self.arrive_time.append(self.arrive_time[i - 1] + self.arrive_space[i])

        # 生成服从指数分布的服务时间
        for i in range(0, self.custom_num):
            ran = -self.average_serve_time * math.log(random.uniform(0, 1))
            self.serve_time.append(ran)

        for i in range(0, self.custom_num):
            person = Person(i, self.arrive_time[i], self.serve_time[i])
            self.personList.append(person)

        for i in range(0, self.table_number):  # 创建窗口
            table = Table()
            self.tableList.append(table)

        self.maopao()  # 进行排序

    def leave(self):  # 计算离开时间最优解
        for i in self.personList:
            minTable = 0
            minTime = 100000000
            # 找到结束时间最早的窗口
            self.eventTime.append(i.arrive_time)  # 记录到来时间
            for j in range(0, len(self.tableList)):
                if self.tableList[j].finish_time < minTime:
                    minTime = self.tableList[j].finish_time
                    minTable = j

            i.table_number = minTable
            self.tableList[minTable].peopleList.append(i)
            # 计算离开时间
            if len(self.tableList[minTable].peopleList) == 1:  # 第一个人
                i.leave_time = i.arrive_time + i.serve_time
            else:
                prePeople = self.tableList[minTable].peopleList[-2]  # 前一个人
                if prePeople.leave_time < i.arrive_time:  # 前一个人已经走了
                    i.leave_time = i.arrive_time + i.serve_time
                else:  # 前一个人还没走
                    i.leave_time = prePeople.leave_time + i.serve_time
            # 计算队列结束时间，个人排队时间等
            self.eventTime.append(i.leave_time - i.serve_time)
            self.eventTime.append(i.leave_time)  # 记录离开时间
            self.tableList[minTable].finish_time = i.leave_time  # 更新finishTime
            i.wait_time = i.leave_time - i.arrive_time  # 顾客等待时间 = 顾客离开时间- 顾客到达的时间
            i.queue_time = i.leave_time - i.arrive_time - i.serve_time  # 顾客排队时间 = 顾客等待时间- 顾客服务时间
        self.finish = 1  # 更新整体状态

    def run(self, timeI):  # 运行仿真
        times = self.eventTime[timeI]
        #time.sleep(0.01)
        self.now_time = times

        for person in self.personList:
            # 人到了 加入队列
            if person.arrive_time == times:
                self.nowPersonNumber += 1
                table = self.tableList[person.table_number]
                table.queue.append(person)  # 队列加入顾客
                if (len(table.queue) != 0):
                    table.is_use = 1  # 设置队列状态为正在使用
                if timeI >= 1:
                    waitPeople = 0  # 当前排队人数
                    for j in self.tableList:
                        waitPeople += len(j.queue)
                    self.queue_time += waitPeople * (self.now_time - self.eventTime[timeI - 1])  # 计算总排队时间
                    self.average_people_number = self.queue_time / (self.now_time)  # 计算平均等待人数
                self.wait_time += person.wait_time  # 计算总等待时间
                self.average_wait_time = self.wait_time / self.nowPersonNumber  # 计算平均等待时间
                table.serve_time += person.serve_time  # 计算总服务时常
                table.use_ratio = round(float(table.serve_time / self.now_time), 2)  # 计算窗口利用率
                return "Time " + str(int(self.now_time)) + "第" + str(person.table_number + 1) \
                       + "号窗口加入排队人员" + str(
                    person.id + 1)
            # 人走了，移除队列
            elif person.leave_time == times:
                table = self.tableList[person.table_number]
                if person in table.queue:
                    table.queue.remove(person)  # 队列移除顾客
                    if (len(table.queue) == 0):
                        table.is_use = 0  # 设置队列状态为没有在使用
                    table.use_ratio = round(float(table.serve_time / self.now_time), 2)  # 计算窗口利用率
                    if timeI >= 1:
                        waitPeople = 0  # 当前排队人数
                        for j in self.tableList:
                            waitPeople += len(j.queue)
                        self.queue_time += waitPeople * (self.now_time - self.eventTime[timeI - 1])  # 计算总排队时间
                        self.average_people_number = self.queue_time / (self.now_time)  # 计算平均等待人数
                    return "Time " + str(int(self.now_time)) + " 第" + str(person.table_number + 1) \
                           + "号窗口移除排队人员" + str(
                        person.id + 1)
