#To-dos

#File-reading
    #be able to read generated files to "pick up where we left off"
    #may need some revisions to the logging structure (just a rough draft anyway)

#should also track the BEST model's performance,
    #i.e. keep a COMPLETE list of model runs and performances to be able to 
        #report the best of all runs.
        
#need to be able to define in argparse the 
    #base model values, base tolerance values, 
    #all printing options
    #

#must be able to control game seed. needs changes in simulator.py for this to take effect

from simulator import TetrisSimulator
import random, numpy, argparse, os
from time import gmtime, strftime

###Functions
def generate_controller(start, tols):
    new_controller = {}
    
    #for each feature
    for k in sorted(start.keys()):
        #generate a new value around the mean
        val = random.gauss(start[k],tols[k])
        
        #and add this pair to the new controller
        new_controller[k]= val
        
    return new_controller

#Takes a list of controllers (lists) with the same number of features
#outputs a new average controller, and the stdev for each value
def merge_controllers(controllers):
    new_controller = {}
    new_tolerances = {}
    #for each feature (of all controllers)
    for k in sorted(controllers[0].keys()):
        vals = []
        for c in controllers:
            vals.append(c[k])
        mean = float(sum(vals)) / float(len(vals))
        tol = numpy.std(vals)
        
        new_controller[k] = mean
        new_tolerances[k] = tol
    
    return new_controller, tolerances
        

"""
def write_controller(name, file, controller, tolerances = None):
    file.write("Controller:\t" + name + "\n")
    header = "feature\tval"
    if tolerances:
        header = header + "\ttolerance"
    file.write(header + "\n")
    for i in range(0,len(controller)):
        file.write(controller[i][0] + "\t" + str(controller[i][1]))
        if tolerances:
            file.write("\t" + str(tolerances[i]))
        file.write("\n")
    file.write("\n")

result_fields = ["lines","score","level","l1","l2","l3","l4"]
def write_result(name, file, result):
    file.write("\t" + name + " Results:\n")
    for f in result_fields:
        file.write("\t" + f + ":\t" + str(result[f]) + "\n")
    file.write("\n")
"""


###Script

#staring from Dellacherie model
target_controller = {"landing_height":-1,
                "eroded_cells":1,
                "row_trans":-1,
                "col_trans":-1,
                "pits":-4,
                "cuml_wells":-1}
                
start_controller = {"landing_height":0,
                "eroded_cells":0,
                "row_trans":0,
                "col_trans":0,
                "pits":0,
                "cuml_wells":0}
                
                #["tetris",1000],
                #["column_9",-400]]
                
tolerances = {"landing_height":100,
                "eroded_cells":100,
                "row_trans":100,
                "col_trans":100,
                "pits":100,
                "cuml_wells":100}


if __name__ == '__main__':
    
    datestring = strftime("%Y-%m-%d_%H-%M-%S", gmtime())
    
    #defaults from Thierry and Scherrer paper:
        #original controller centered on 0, 
        #original variance 100, (they used variance, we use Standard Deviation; just SQUARE stdev to get this)
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
    parser.add_argument( '-v', '--visuals',
                        action = "store_true", dest = "show_visuals", default = False,
                        help = "Show visualizations.")
    parser.add_argument( '-vs', '--visual_step',
                        action = "store", dest = "visual_step", type=float, default = 0,
                        help = "Timestep between choices in seconds.")
    parser.add_argument( '-o', '--output',
                        action = "store", dest = "output_file",
                        type = str, default = datestring,
                        help = "Output file. Extension will be .txt")
    
    
    #parse for seed
    #parse for tolerance
    #parse for initial values
    #parse for printing
    #parse for result to maximize
    
    args = parser.parse_args()
    
    if not os.path.exists("runs"):
        os.makedirs("runs")
    outfile = open("runs/" + args.output_file + ".incomplete.txt", "w")
    #logfile = open("log.txt", "a")
        
    depth = args.depth
    controllers = args.controllers
    survivors = args.survivors
    episodes = args.episodes
    report_every = args.report_every
    if args.show_visuals:
        show_choice = True
    else:
        show_choice = False
    v_step = args.visual_step
        
    
    #session, depth, controllers, survivors, episodes, 
    
    header_std = ["session","depth","controllers","survivors","base_val","base_var","episodes"]
    header_in = []
    header_out = []
    #logfile.write("Run initiated at " + datestring + "\n")
    
    outfile.write("Depth      :\t" + str(depth) + "\n")
    outfile.write("Controllers:\t" + str(controllers) + "\n")
    outfile.write("Survivors  :\t" + str(survivors) + "\n")
    outfile.write("Episodes   :\t" + str(episodes) + "\n")
    outfile.write("\n")
    
    #write_controller("INIT", outfile, start_controller, tolerances)
    
    for x in range (0, depth):
        
        #outfile.write("Run:\t" + str(x+1) + "\n\n")
        
        results = []
        
        for a in range(0, controllers):
            random_controller = generate_controller(start_controller, tolerances)
            controller_name = "R" + str(x + 1) + "_" + str(a+1)
            #write_controller(controller_name, outfile, random_controller)
            
            sim = TetrisSimulator(controller = random_controller, show_choice = show_choice, choice_step = v_step)
            sim_result = sim.run(eps = episodes, printstep = report_every)
            
            #write_result(controller_name, outfile, sim_result)
            
            results.append([random_controller, sim_result])
            
            
        sorted_results = sorted(results, key=lambda k: k[1]['lines'])
        
        #sort by "l4" or "lines" or "score"
        
        for d in sorted_results:
            print d[1]["lines"]
    
        top_results = sorted_results[-survivors:]
    
        #for e in top_results:
        #    print e[1]["lines"]
    
        top_controllers = []
            
        for f in top_results:
            top_controllers.append(f[0])
        
        start_controller, tolerances = merge_controllers(top_controllers)
        
        #write_controller("R" + str(x+1) + "_mean", outfile, start_controller, tolerances)
        
        #print start_controller
        #print tolerances
        
    
    os.rename("runs/" + datestring + ".incomplete.txt", "runs/" + datestring+".txt")
    