#!/usr/bin/env python

"""
taskset.py - parser for task set from JSON file
"""

import json
import sys


class TaskSetJsonKeys(object):
    # Task set
    KEY_TASKSET = "taskset"

    # Task
    KEY_TASK_ID = "taskId"
    KEY_TASK_PERIOD = "period"
    KEY_TASK_WCET = "wcet"
    KEY_TASK_DEADLINE = "deadline"
    KEY_TASK_OFFSET = "offset"
    KEY_TASK_SECTIONS = "sections"

    # Schedule
    KEY_SCHEDULE_START = "startTime"
    KEY_SCHEDULE_END = "endTime"

    # Release times
    KEY_RELEASETIMES = "releaseTimes"
    KEY_RELEASETIMES_JOBRELEASE = "timeInstant"
    KEY_RELEASETIMES_TASKID = "taskId"


class TaskSetIterator:
    def __init__(self, taskSet):
        self.taskSet = taskSet
        self.index = 0
        self.keys = iter(taskSet.tasks)

    def __next__(self):
        key = next(self.keys)
        return self.taskSet.tasks[key]


class TaskSet(object):
    def __init__(self, data):
        self.parseDataToTasks(data)
        self.buildJobReleases(data)

    def parseDataToTasks(self, data):
        taskSet = {}

        for taskData in data[TaskSetJsonKeys.KEY_TASKSET]:
            task = Task(taskData)

            if task.id in taskSet:
                print("Error: duplicate task ID: {0}".format(task.id))
                return

            if task.period < 0 and task.relativeDeadline < 0:
                print("Error: aperiodic task must have positive relative deadline")
                return

            taskSet[task.id] = task

        self.tasks = taskSet

    def buildJobReleases(self, data):
        jobs = []

        if TaskSetJsonKeys.KEY_RELEASETIMES in data:  # necessary for sporadic releases
            for jobRelease in data[TaskSetJsonKeys.KEY_RELEASETIMES]:
                releaseTime = float(jobRelease[TaskSetJsonKeys.KEY_RELEASETIMES_JOBRELEASE])
                taskId = int(jobRelease[TaskSetJsonKeys.KEY_RELEASETIMES_TASKID])

                job = self.getTaskById(taskId).spawnJob(releaseTime)
                jobs.append(job)
        else:
            scheduleStartTime = float(data[TaskSetJsonKeys.KEY_SCHEDULE_START])
            scheduleEndTime = float(data[TaskSetJsonKeys.KEY_SCHEDULE_END])
            for task in self:
                t = max(task.offset, scheduleStartTime)
                while t < scheduleEndTime:
                    job = task.spawnJob(t)
                    if job is not None:
                        jobs.append(job)

                    if task.period >= 0:
                        t += task.period  # periodic
                    else:
                        t = scheduleEndTime  # aperiodic

        self.jobs = jobs

    def __contains__(self, elt):
        return elt in self.tasks

    def __iter__(self):
        return TaskSetIterator(self)

    def __len__(self):
        return len(self.tasks)

    def getTaskById(self, taskId):
        return self.tasks[taskId]
    
    def getJobs(self):
        """get all of the jobs

        Returns:
            list: a list of all jobs
        """
        jobs = []
        for task in self:
            jobs = jobs + task.getJobs()
        return jobs

    def printTasks(self):
        print("\nTask Set:")
        for task in self:
            print(task)

    def printJobs(self):
        print("\nJobs:")
        for task in self:
            for job in task.getJobs():
                print(job)


class Task(object):
    def __init__(self, taskDict):
        self.id = int(taskDict[TaskSetJsonKeys.KEY_TASK_ID])
        self.period = float(taskDict[TaskSetJsonKeys.KEY_TASK_PERIOD])
        self.wcet = float(taskDict[TaskSetJsonKeys.KEY_TASK_WCET])
        self.relativeDeadline = float(
            taskDict.get(TaskSetJsonKeys.KEY_TASK_DEADLINE, taskDict[TaskSetJsonKeys.KEY_TASK_PERIOD]))
        self.offset = float(taskDict.get(TaskSetJsonKeys.KEY_TASK_OFFSET, 0.0))
        self.sections = taskDict[TaskSetJsonKeys.KEY_TASK_SECTIONS]

        self.lastJobId = 0
        self.lastReleasedTime = 0.0

        self.jobs = []

    def getAllResources(self):
        """getAllResources

        Returns:
            dict: Dictionary of sections
        """
        return self.sections

    def spawnJob(self, releaseTime):
        if self.lastReleasedTime > 0 and releaseTime < self.lastReleasedTime:
            print("INVALID: release time of job is not monotonic")
            return None

        if self.lastReleasedTime > 0 and releaseTime < self.lastReleasedTime + self.period:
            print("INVDALID: release times are not separated by period")
            return None

        self.lastJobId += 1
        self.lastReleasedTime = releaseTime

        job = Job(self, self.lastJobId, releaseTime)

        self.jobs.append(job)
        return job
    
    def getJobs(self):
        return self.jobs

    def getJobById(self, jobId):
        if jobId > self.lastJobId:
            return None

        job = self.jobs[jobId - 1]
        if job.id == jobId:
            return job

        for job in self.jobs:
            if job.id == jobId:
                return job

        return None

    def getUtilization(self):
        """getUtilization

        Returns:
            float: Worst case execution time divided by relative deadline
        """
        return float(self.wcet / self.relativeDeadline)

    def __str__(self):
        return "task {0}: (Φ,T,C,D,∆) = ({1}, {2}, {3}, {4}, {5})".format(self.id, self.offset, self.period, self.wcet,
                                                                          self.relativeDeadline, self.sections)


class Job(object):
    def __init__(self, task, jobId, releaseTime):
        """constructor

        Args:
            task (Task): Job task
            jobId (int): an id for the job
            releaseTime (int): release time of the job
        """
        self.task = task
        self.id = jobId
        
        self.executeTime = 0
        self.releaseTime = releaseTime
        self.deadline = self.releaseTime + self.task.relativeDeadline
        
        self.fixedPriority = float(1 / self.deadline)
        self.dynamicPriority = self.fixedPriority
        
    def getTaskId(self):
        """get task id

        Returns:
            int: task id
        """
        return self.task.id
        
    def isActive(self, time):
        """check if the job is activated or not

        Args:
            time (int): the current time

        Returns:
            bool: activated or not
        """
        return self.executeTime < self.task.wcet and self.releaseTime <= time and self.deadline > time
    
    def demandResource(self):
        """return the demand id of resource

        Returns:
            int: id of resource
        """
        sections = self.task.getAllResources()
        
        overall = 0
        for section in sections:
            id = section[0]
            time = section[1]
            
            if self.executeTime < time + overall:
                return id
            
            overall = overall + time
        
        return -1
        
    def getId(self):
        """get job id

        Returns:
            int: job it
        """
        return self.id

    def getFP(self):
        """get fixed priority

        Returns:
            float: fixed priority of the job
        """
        return self.fixedPriority
    
    def getDP(self):
        """get dynamic priority

        Returns:
            float: dynamic priority of the job
        """
        return self.dynamicPriority
    
    def setDP(self, value):
        """set dynamic priority

        Args:
            value (float): dynamic priority
        """
        self.dynamicPriority = value
    
    def doJob(self):
        """execute job for 1 unit of time"""
        self.executeTime = self.executeTime + 1

    def __str__(self):
        return "[{0}:{1}] released at {2} -> deadline at {3}".format(self.task.id, self.id, self.releaseTime,
                                                                     self.deadline)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "taskset.json"

    with open(file_path) as json_data:
        data = json.load(json_data)

    taskSet = TaskSet(data)

    taskSet.printTasks()
    taskSet.printJobs()
