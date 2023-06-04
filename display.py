import matplotlib.pyplot as plt



class Display(object):
    def __init__(self, jobs, xlimit, ylimit):
        """constructor

        Args:
            jobs (dict): list of jobs and time
        """
        fig, gnt = plt.subplots()
        
        # Setting Y-axis and X-axis limits
        gnt.set_ylim(0, ylimit+1)
        gnt.set_xlim(0, xlimit)
        
        # Setting labels for x-axis and y-axis
        gnt.set_xlabel('Time in seconds')
        gnt.set_ylabel('Tasks')
        
        # Setting ticks on y-axis
        gnt.set_yticks([1 for _ in range(ylimit)])
        
        # Labelling tickes of y-axis
        gnt.set_yticklabels([f'Task {x}' for x in range(ylimit)])
        
        gnt.grid(True)
        
        for t, j in jobs.items():
            if j != None:
                gnt.broken_barh([(t, 1)], (j.getTaskId(), 1), facecolors=('tab:orange'))
        
        plt.show()
        