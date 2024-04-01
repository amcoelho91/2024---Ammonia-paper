from numpy import *
from pyomo.environ import *

def run_optimization_model(m: ConcreteModel, h: int, number_resources: int, resources: dict, prices: dict, case: int) -> None:
    ''' Run optimization model as per the objective function '''
    c_H2O = resources['electrolyzer']['c_H2O']
    c_O2 = resources['electrolyzer']['c_O2']

    price_E = prices['energy']
    price_E_market = prices['energy_market']

    price_B = prices['band']
    price_E_D = prices['downward']
    price_E_U = prices['upward']
    ratio_D = prices['downward']
    ratio_U = prices['upward']
    price_hy = prices['hydrogen']
    price_water = prices['water']
    price_oxyg = prices['oxygen']
    price_ammonia = prices['ammonia']

    P_H2O = []
    P_O2 = []
    for t in range(0, h):
        P_H2O.append(sum(m.P_EL_E[i, t] for i in range(0, number_resources)) * c_H2O)
        P_O2.append(sum(m.P_EL_E[i, t] for i in range(0, number_resources)) * c_O2)

    if case == 3:
        f_E = sum(price_E[t] * m.P_E_pos[t] - price_E_market[t] * m.P_E_neg[t]
                  - price_B[t] * (m.U_sto_E[0, t] + m.D_sto_E[0, t]) +
                  (price_E_D[t] * ratio_D[t] * m.D_sto_E[0, t] -
                   price_E_U[t] * ratio_U[t] * m.U_sto_E[0, t]) for t in range(0, h))
        f_hy = price_hy * sum(m.P_H2[t] for t in range(0, h))
    elif case == 2:
        f_E = sum(price_E[t] * m.P_E_pos[t] - price_E_market[t] * m.P_E_neg[t] for t in range(0, h))
        f_hy = price_hy * sum(m.P_H2[t] for t in range(0, h))
    else:
        f_E = sum(price_E[t] * m.P_E_pos[t] for t in range(0, h))
        f_hy = 0

    f_water = price_water * sum(m.P_EL_E[i, t] for i in range(0, number_resources)) * c_H2O
    f_oxyg = price_oxyg * sum(m.P_EL_E[i, t] for i in range(0, number_resources)) * c_O2
    f_ammonia = price_ammonia * sum(resources['load_ammonia'][0] for t in range(0, h))

    m.value = Objective(expr= f_E + f_water - f_hy  - f_oxyg - f_ammonia
                        , sense=minimize)

    solver = SolverFactory("cplex")
    results = solver.solve(m, tee=False)

    if (results.solver.status == SolverStatus.ok) and \
            (results.solver.termination_condition == TerminationCondition.optimal):
        print("Flow optimized")
    else:
        print("Did no converge")

    return 0