class Table:  # 窗口
    def __init__(self):
        self.finish_time = 0  # 结束时间
        self.peopleList = []  # 总排队人次
        self.queue = []  # 当前队列
        self.is_use = 0  # 是否正在使用 使用为1，不使用为0
        self.use_ratio = 0  # 利用率
        self.serve_time = 0  # 服务总时间

    def insertPeople(self, people):
        self.peopleList.append(people)


