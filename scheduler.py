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
        
        for time in range(limit):
            currentJob = None
            jobs = [job for job in self.taskSet.getJobs()] # get all jobs
            
            activeJobs = [job for job in jobs if job.isActive(time)] # get all active jobs
            activeJobs.sort(key=lambda x: x.getFP(), reverse=True) # sort jobs by deadline monothonic
            
            if len(activeJobs) > 0: # schedule
                currentJob = activeJobs[0]
            
            jobsList[time] = currentJob
        
        return jobsList
