import sys
import json

from ui.display import Display
from scheduler import Scheduler



if __name__ == "__main__":
    # get file path and time
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        mode = int(sys.argv[2])
    else:
        file_path = "taskset.json"
        mode = 1

    with open(file_path) as json_data:
        data = json.load(json_data)
    
    time = data['endTime']
    
    # create scheduler
    s = Scheduler(data=data)
    jobs = s.run(time, mode)
    
    for t, j in jobs.items():
        if j != None:
            print(f'{t:02d} | {j["job"]}')
    
    # show diagram
    Display(jobs, time, s.size())
