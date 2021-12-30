class Person:
    def __init__(self,id, arrive_time, serve_time):
        self.id = id #个人ID
        self.arrive_time = arrive_time  # 到达时间
        self.serve_time = serve_time  # 服务时间
        self.leave_time = 0  # 离开时间
        self.queue_time = 0  # 排队时间
        self.wait_time = 0  # 等待时间（从来到走）
        self.table_number = 0  # 加入的窗口号
