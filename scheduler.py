from taskset import TaskSet



NO_MODE = 1
NPP = 2
HLP = 3



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
    
    def getHighPriorityJobs(self):
        """get jobs that had resource and still want that

        Returns:
            list: list of high priority jobs
        """
        highPriorityJobs = []
        
        for item in self.queue:
            resource = item[0]
            job = self.taskSet.getJobById(item[1])
            
            if job.demandResource() == resource:
                highPriorityJobs.append(item)
        
        highPriorityJobs.sort(key=lambda x: x[2], reverse=True)
        list = [x[1] for x in highPriorityJobs]
        
        return list
        
    def getResource(self, key, value, time):
        """get a resource

        Args:
            key (int): resource key
            value (int): id of that job
        """
        self.resources[key] = value
        
        # save the resource get in a queue
        self.queue.append((key, value, time))
    
    def freeUnusedResources(self):
        """free unused resources"""
        queue = []
        
        for item in self.queue:
            resource = item[0]
            job = self.taskSet.getJobById(item[1])
            time = item[2]
            
            if job.demandResource() != item[0]:
                self.resources[resource] = 0
            else:
                queue.append((resource, job.getId(), time))
        
        self.queue = queue
                   
    def run(self, limit, mode):
        """execute scheduler in an amount of time

        Args:
            limit (int): timeline

        Returns:
            dict: time and jobs
        """
        jobsList = {}
        
        for time in range(limit):
            currentJob = None
            finalDemand = 0
            
            # get all high priority jobs that use resources
            highJobs = self.getHighPriorityJobs()
            
            # free all resources if they are done
            self.freeUnusedResources()
            
            jobs = [job for job in self.taskSet.getJobs() if job.isActive(time)] # get all active jobs
            jobs.sort(key=lambda x: x.getFP(), reverse=True) # sort jobs by deadline monothonic
            
            if len(jobs) > 0: # schedule when we have jobs
                if mode == NO_MODE: # no mode for resource
                    currentJob = jobs[0]
                elif mode == NPP: # Non-Preemptive Protocol
                    # priority is for jobs that hold a resource
                    if len(highJobs) > 0:
                        currentJob = self.taskSet.getJobById(highJobs[0])
                    else:
                        # after that use other jobs
                        for job in jobs:
                            currentJob = job
                            
                            # get job demand
                            jobDemand = currentJob.demandResource()
                            if jobDemand != 0: # resource wanted
                                if self.resourceAvailable(jobDemand):
                                    self.getResource(jobDemand, currentJob.getId(), time) # get resource
                                    break
                                else: # cannot be executed while the resource is in use
                                    continue
                            else: # no resource wanted
                                break
                elif mode == HLP: # High Lock priority
                    # priority is for jobs that hold a resource
                    if len(highJobs) > 0:
                        currentJob = self.taskSet.getJobById(highJobs[0])
                        # after that use other jobs
                        for job in jobs:
                            if job.getFP() > currentJob.getFP():
                                currentJobDemand = currentJob.demandResource()
                                if currentJobDemand != 0 and not job.wantsTheResourceOrNot(currentJobDemand):
                                    currentJob = job
                                    break
                    else:
                        # after that use other jobs
                        for job in jobs:
                            currentJob = job
                            
                            # get job demand
                            jobDemand = currentJob.demandResource()
                            if jobDemand != 0: # resource wanted
                                if self.resourceAvailable(jobDemand):
                                    self.getResource(jobDemand, currentJob.getId(), time) # get resource
                                    break
                                else: # cannot be executed while the resource is in use
                                    continue
                            else: # no resource wanted
                                break
                
            if currentJob != None: # do the job
                finalDemand = currentJob.demandResource()
                currentJob.doJob()

            jobsList[time] = {
                'job': currentJob,
                'resource': finalDemand
            }
        
        return jobsList
