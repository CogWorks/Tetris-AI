from simulator import TetrisSimulator


## UNTESTED - Predict function - given a board and a zoid and a controller, returns best placement as determined by the controller 

def predict(space, zoid, controller):
        sim = TetrisSimulator(controller = controller)
        sim.space = sim.convert_space(space)
        sim.curr_z = zoid
        
        sim.get_options()
        return sim.control()
        
        