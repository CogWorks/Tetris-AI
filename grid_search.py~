#a program to expediate the process of trying different annealing schemes and parameter values
import numpy as np
import argparse
from subprocess import call
from cross_entropy import *

if __name__ == "__main__":

	parser = argparse.ArgumentParser( formatter_class = argparse.ArgumentDefaultsHelpFormatter )
	#The user will indicate the type of regularization they want to perform, as well as the upper and lower limits of the two parameters, update_value and initial_penalty. The user also indicates
	#how finely they wish to divide the interval given
	#May try to improve short form of command line flags
	
	parser.add_argument( '-mip', '--max_initial_penalty',
                        action = "store", dest = "max_initial_penalty",
                        type = int, default = 0,
                        help = "Upper limit of initial penalty.")
	parser.add_argument( '-nip', '--min_initial_penalty',
                        action = "store", dest = "min_initial_penalty",
                        type = int, default = 0,
                        help = "Lower limit of initial penalty.")
	parser.add_argument( '-muv', '--max_update_value',
                        action = "store", dest = "max_update_value",
                        type = int, default = 0,
                        help = "Upper limit of update value.")
	parser.add_argument( '-nuv', '--min_update_value',
                        action = "store", dest = "min_update_value",
                        type = int, default = 0,
                        help = "Lower limit of update value.")
	parser.add_argument( '-rt', '--regularization_type',
                        action = "store", dest = "regularization_type",
                        type = str, default = 'none',
                        help = "Type of regularization.")
	parser.add_argument( '-gr', '--granularity',
                        action = "store", dest = "granularity",
                        type = int, default = 3,
                        help = "How many samples the user wishes to divide the constructed intervals into.")						
	
	#harvest the collected arguments
	
	args = parser.parse_args()
	
	max_initial_penalty = args.max_initial_penalty
	min_initial_penalty = args.min_initial_penalty
	max_update_value = args.max_update_value
	min_update_value = args.min_update_value
	regularization_type = args.regularization_type
	granularity = args.granularity
	
	#creates the potential values the grid search will visit. Experiments or runs consist of running cross_entropy using 1 value from each of the following arrays.
	initial_penalty_samples = np.linspace(min_initial_penalty,max_initial_penalty,num=granularity)
	update_value_samples = np.linspace(min_update_value,max_initial_penalty,num=granularity)
	
	#loops over all possible combinations of the parameter values given in initial_penalty_samples and update_value_samples and runs cross_entropy using them to determine penalties.
	#NOTE: this procedure is costly, each loop calls cross_entropy. As such, it is recommended that granularity be kept rather low, not exceeding nine at the very most.
	#Point of improvement: could multithreading be used here? Something to look into.
	
	for pen>0 in initial_penalty_samples: #0 is excluded in this loop, since having zero would mean no regularization in some cases
		for upd in update_value_samples:
			#puts a string on the command line to call cross_entropy.py, passing as arguments the regularization type, pen, and upd. Other parameters will remain as the default
			# values found in cross_entropy.py for this branch of the Tetris project.
			command = "python cross_entropy.py -ip " + str(pen) + " -rtp " + str(upd) + " -rt " + regularization_type
			subprocess.call(command,shell=True)
			
