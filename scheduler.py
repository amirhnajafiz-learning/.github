from taskset import TaskSet



class Scheduler(object):
    def __init__(self, data):
        """constructor

        Args:
            data (json): json object of tasks data
        """
        self.taskSet = TaskSet(data)
        self.queue = []
        self.resources = {}
    
    def size(self):
        """return the size of task set

        Returns:
            int: len of tasks
        """
        return len(self.taskSet)

    def resourceAvailable(self, key):
        """check if resource is available or not

        Args:
            key (int): resource key

        Returns:
            bool: free or not
        """
        if key in self.resources:
            return self.resources[key] == 0
        else:
            self.resources[key] = 0
            return True
        
    def getResource(self, key, value):
        """get a resource

        Args:
            key (int): resource key
            value (int): id of that job
        """
        self.resources[key] = value
        
        # save the resource get in a queue
        self.queue.append((key, value))
    
    def freeUnusedResources(self):
        """free unused resources"""
        queue = []
        
        for item in self.queue:
            resource = item[0]
            job = self.taskSet.getJobById(item[1])
            
            if job.demandResource() != item[0]:
                self.resources[resource] = 0
            else:
                queue.append((resource, job.getId()))
        
        self.queue = queue
                
            
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
            
            # free all resources if they are done
            self.freeUnusedResources()
            
            jobs = [job for job in self.taskSet.getJobs() if job.isActive(time)] # get all active jobs
            jobs.sort(key=lambda x: x.getFP(), reverse=True) # sort jobs by deadline monothonic
            
            if len(jobs) > 0: # schedule when we have jobs
                for job in jobs:
                    currentJob = job
                    
                    # get job demand
                    jobDemand = currentJob.demandResource()
                    if jobDemand != 0: # resource wanted
                        if self.resourceAvailable(jobDemand):
                            self.getResource(jobDemand, currentJob.getId()) # get resource
                            break
                        else: # cannot be executed while the resource is in use
                            continue
                    else: # no resource wanted
                        break
                
            if currentJob != None: # do the job
                currentJob.doJob()

            jobsList[time] = currentJob
        
        return jobsList
