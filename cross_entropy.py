from simulator import TetrisSimulator
import random, numpy, argparse


###Functions
def generate_controller(start, tols):
    new_controller = []
    
    #for each feature
    for i in range(0,len(start)):
        #generate a new value around the mean
        val = random.gauss(start[i][1],tols[i])
        
        #and add this pair to the new controller
        new_controller.append([start[i][0],val])
        
    return new_controller

#Takes a list of controllers (lists) with the same number of features
#outputs a new average controller, and the stdev for each value
def merge_controllers(controllers):
    new_controller = []
    tolerances = []
    #for each feature (of all controllers)
    for i in range(0,len(controllers[0])):
        feature = controllers[0][i][0]
        vals = []
        for j in controllers:
            vals.append(j[i][1])
        mean = float(sum(vals)) / float(len(vals))
        tol = numpy.std(vals)
        
        new_controller.append([feature,mean])
        tolerances.append(tol)
    
    return new_controller, tolerances
        


###Script

#staring from Dellacherie model
target_controller = [["landing_height",-1],
                ["eroded_cells",1],
                ["row_trans",-1],
                ["col_trans",-1],
                ["pits",-4],
                ["cuml_wells",-1]]
                
start_controller = [["landing_height",0],
                ["eroded_cells",0],
                ["row_trans",0],
                ["col_trans",0],
                ["pits",0],
                ["cuml_wells",0]]
                
tolerances = [1,1,1,1,1,1]

if __name__ == '__main__':
    
    #defaults from Thierry and Scherrer paper:
        #original controller centered on 0, 
        #original variance 100, (they used variance, we use Standard Deviation; figure out how that works)
        #100 controllers, 
        #10 survivors, 
        #all new variances were varied by the constant 4
    
    parser = argparse.ArgumentParser( formatter_class = argparse.ArgumentDefaultsHelpFormatter )
    
    parser.add_argument( '-d', '--depth',
                        action = "store", dest = "depth",
                        type = int, default = 5,
                        help = "Set how many cross-entropy generations to traverse.")
    
    parser.add_argument( '-c', '--controllers',
                        action = "store", dest = "controllers",
                        type = int, default = 10,
                        help = "Set the number of controllers to spawn in each generation.")
    
    parser.add_argument( '-s', '--survivors',
                        action = "store", dest = "survivors",
                        type = int, default = 4,
                        help = "Set how many of the best controllers survive each generation.")
    
    parser.add_argument( '-e', '--episodes',
                        action = "store", dest = "episodes",
                        type = int, default = -1,
                        help = "Set maximum number of episodes for all controllers to play.")
    parser.add_argument( '-r', '--report_every',
                        action = "store", dest = "report_every",
                        type = int, default = 500,
                        help = "How often, in episodes, to report the current scores. -1 disables")
    
    args = parser.parse_args()
    
    depth = args.depth
    controllers = args.controllers
    survivors = args.survivors
    episodes = args.episodes
    report_every = args.report_every
    
    
    for x in range (0, depth):
        results = []
    
        for a in range(0, controllers):
            random_controller = generate_controller(start_controller, tolerances)
            print(random_controller)
            sim = TetrisSimulator(controller = random_controller)
            sim_result = sim.run(eps = episodes, printstep = report_every)
            results.append([random_controller, sim_result])
            
            
        sorted_results = sorted(results, key=lambda k: k[1]['lines'])
    
        for d in sorted_results:
            print d[1]["lines"]
    
        top_results = sorted_results[-survivors:]
    
        for e in top_results:
            print e[1]["lines"]
    
        top_controllers = []
            
        for f in top_results:
            top_controllers.append(f[0])
    
        start_controller, tolerances = merge_controllers(top_controllers)
    
        print start_controller
        print tolerances
        
    
    
    