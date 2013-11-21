from simulator import TetrisSimulator
import random, numpy


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
                
tolerances = [10,10,10,10,10,10]


random_controller = generate_controller(start_controller, tolerances)
print(random_controller)
				
sim_test = TetrisSimulator(controller = random_controller)




#new function: to generate new tolerances (stdev):
    #get all values of a particular feature into a single vector
    #  vals = [a,b,c,d,e]
    #and call
    #  numpy.std(vals)
    #Do this for each value to generate the new tolerances
    #and, while you're at it, take the means to generate the new "base model"



result = sim_test.run()
print result