from taskset import TaskSet



class Scheduler(object):
    def __init__(self, data):
        """constructor

        Args:
            data (json): json object of tasks data
        """
        self.taskSet = TaskSet(data)
        
        self.resources = []
        
        self.currentJob = None
        self.jobsList = []
    