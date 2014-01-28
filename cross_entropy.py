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


#Need better randomization control

#Need to add some ability to play overhangs.

#Need to have some rudimentary constraints added in.

#Need "diminishing noise" implementation

#Need "convergence" value ; they allowed 80 generations for convergence; what do we do?

#Need 2-piece look-ahead

#Need to add post-testing; FOR EACH ITERATION'S RESULTANT AVERAGE CONTROLLER
    #i.e. Each "good" model must play a host of random games to verify its generalizability
    #could just have parameter for number of games played per controller 
    #maybe use a "criterion score"?
    #!! careful! will multiplicatively increase runtime!!

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
def merge_controllers(controllers, noise):
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
        new_tolerances[k] = tol + noise
    
    return new_controller, new_tolerances
        


header = ["session","optimize","depth","controllers","survivors","episodes",
            "noise","initial_value","variance",
            "game_seed","name"]
outputs = ["lines","l1","l2","l3","l4","score","level"]

def write_header(file, features):
    vars = []
    for i in features:
        vars.append(i + "_var")
    
    outheader = header + ["test_game"] + features + vars + outputs
    file.write("\t".join(outheader) + "\n")
    
def write_controller(file, session_vars, name, features, controller, vars = False, outs = False, test_game = False):
    outlist = []
    outlist = outlist + session_vars
    outlist.append(name)
    outlist.append(str(test_game))
    
    for f in features:
        outlist.append(str(controller[f]))
    for f in features:
        if vars:
            outlist.append(str(vars[f]))
        else:
            outlist.append("")
    for o in outputs:
        if outs:
            outlist.append(str(outs[o]))
        else:
            outlist.append("")
    file.write("\t".join(outlist) + "\n")
    

###Script




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
    
    parser.add_argument( '-n', '--noise',
                        action = "store", dest = "noise",
                        type = float, default = 0,
                        help = "Set constant noise value. Set to 0 for non-noisy variance iterations.")
    
    parser.add_argument( '-i', '--initial',
                        action = "store", dest = "initial_val",
                        type = float, default = 0,
                        help = "Set initial value for the \"start\" controller.")
    
    parser.add_argument( '-t', '--tests',
                        action = "store", dest = "tests",
                        type = int, default = 30,
                        help = "Set number of games for testing each iteration.")
    
    parser.add_argument( '-var', '--variance',
                        action = "store", dest = "variance",
                        type = float, default = 100,
                        help = "Set initial variance for cross entropy generation.")
    
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
    
    parser.add_argument( '-op', '--optimize',
                        action = "store", dest = "optimize",
                        type = str, default = "lines",
                        help = "Select what criterion to optimize via cross-entropy: lines, score, level, l1, l2, l3, l4. Defaults to 'lines'.")
    
    parser.add_argument( '-f', '--features',
                        action = "store", dest = "features",
                        type = str, nargs = '+',
                        default = ["landing_height","eroded_cells","row_trans","col_trans","pits","cuml_wells"],
                        help = "List of all features to be used in the model. See 'simulator.py' for known features.")
    
    
    #harvest argparse
    args = parser.parse_args()
    
    if not os.path.exists("runs"):
        os.makedirs("runs")
    outfile = open("runs/" + args.output_file + ".incomplete.tsv", "w")
        
    depth = args.depth
    controllers = args.controllers
    survivors = args.survivors
    episodes = args.episodes
    noise = args.noise
    report_every = args.report_every
    initial_val = args.initial_val
    variance = args.variance
    features = args.features
    optimize = args.optimize
    tests = args.tests
    
    if args.show_visuals:
        show_choice = True
    else:
        show_choice = False
    v_step = args.visual_step
    
    
    #log headers
    
    session_variables = [args.output_file, optimize, str(depth), str(controllers), str(survivors), str(episodes),
                        str(noise), str(initial_val), str(variance), str("NIL")]
    
    write_header(outfile, features)
    
    start_controller = {}
    tolerances = {}
    for f in features:
        start_controller[f] = initial_val
        tolerances[f] = variance
        
    
    write_controller(outfile, session_variables, "G" + str(0), features, start_controller, 
                        vars = tolerances)
    
    for x in range (0, depth):
        
        #session_vars, name, features, controller, vars = False, outs = False
        
        
        results = []
        
        for a in range(0, controllers):
            random_controller = generate_controller(start_controller, tolerances)
            controller_name = "G" + str(x + 1) + "_" + str(a+1)
            
            sim = TetrisSimulator(controller = random_controller, show_choice = show_choice, choice_step = v_step, name = controller_name)
            sim_result = sim.run(eps = episodes, printstep = report_every)
            
            #session_vars, name, features, controller, vars = False, outs = False
            write_controller(outfile, session_variables, controller_name, features, random_controller, 
                            outs = sim_result)
            
            results.append([random_controller, sim_result])
            
            
        sorted_results = sorted(results, key=lambda k: k[1][optimize])
        
        for d in sorted_results:
            print d[1]["lines"]
    
        top_results = sorted_results[-survivors:]
    
        top_controllers = []
            
        for f in top_results:
            top_controllers.append(f[0])
        
        start_controller, tolerances = merge_controllers(top_controllers, noise)
        
        
        ######now run start controller through a number of new games stored in 'tests'
        
        #output of each game saved to a list, for each score type
            # also write to log file
            
        #for each score type, save mean AND S.D. (or variance, or other)
            #write to log file as FINAL version
        #######
        
        #output resultant controller and its scores
        write_controller(outfile, session_variables, "G" + str(x+1), features, start_controller, 
                        vars = tolerances)
        
        
    outfile.close()
    os.rename("runs/" + args.output_file + ".incomplete.tsv", "runs/" + args.output_file+".tsv")
    