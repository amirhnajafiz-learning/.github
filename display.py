import matplotlib.pyplot as plt



class Display(object):
    def __init__(self, jobs, xlimit, ylimit):
        """constructor

        Args:
            jobs (dict): list of jobs and time
        """
        fig, gnt = plt.subplots()
        
        # Setting Y-axis and X-axis limits
        gnt.set_ylim(0, 2*ylimit)
        gnt.set_xlim(0, xlimit)
        
        # Setting labels for x-axis and y-axis
        gnt.set_xlabel('Time in seconds')
        gnt.set_ylabel('Tasks')
        
        # Setting ticks on y-axis
        gnt.set_yticks([2*x for x in range(ylimit)])
        
        # Labelling tickes of y-axis
        gnt.set_yticklabels([f'Task {x+1}' for x in range(ylimit)])
        
        gnt.grid(True)
        
        # display jobs
        for t, j in jobs.items():
            job = j['job']
            color = 'blue'
            
            if j['resource'] != 0:
                color = 'green'
            
            if job != None:
                ycoor = 2 * (job.getTaskId() - 1)
                gnt.broken_barh([(t, 1)], (ycoor, 1), facecolors=(f'tab:{color}'))
                gnt.broken_barh([(job.releaseTime, 0.25)], (ycoor, 1.5), facecolors=('tab:orange'))
                gnt.broken_barh([(job.deadline, 0.25)], (ycoor, 1.75), facecolors=('tab:red'))
        
        plt.show()
        