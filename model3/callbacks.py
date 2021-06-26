import docplex.cp.model as cp

class CallbackSolutionPrintingStatus(cp.CpoCallback):
    def invoke(self, solver, event, jsol):
        obj_val = jsol.get_objective_values()
        obj_bnds = jsol.get_objective_bounds()
        obj_gaps = jsol.get_objective_gaps()
        solvests = jsol.get_solve_status()
        solve_time = jsol.get_info('SolveTime')
        memory = jsol.get_info('MemoryUsage')
        if event != "Periodic":
            print("{}: {}, objective: {} bounds: {}, gaps: {}, time: {}, memory: {}".format(event, solvests, obj_val, obj_bnds, obj_gaps, solve_time, memory))
