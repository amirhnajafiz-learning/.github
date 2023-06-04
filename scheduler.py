from taskset import TaskSet



class Scheduler(object):
    def __init__(self, data):
        """constructor

        Args:
            data (json): json object of tasks data
        """
        self.taskSet = TaskSet(data)
        
        self.resources = []
    
    def run(self, limit):
        """execute scheduler in an amount of time

        Args:
            limit (int): timeline

        Returns:
            dict: time and jobs
        """
        jobsList = {}
        
        for time in limit:
            job = None
            
            jobs = [job for job in self.taskSet.getJobs() if job.isActive(time)] # get all active jobs
            jobs.sort(key=lambda x: x.getFP(), reverse=True) # sort jobs by deadline monothonic
            
            if len(jobs) > 0: # schedule
                job = jobs[0]
            
            jobsList[time] = job
        
        return jobsList
