from numpy import *
from pyomo.environ import *


def create_model(m: ConcreteModel, h: int, number_resources: int, resources: dict, case: int) -> ConcreteModel:
    ''' Create models of resources '''

    m = create_bidding_model(m, h, number_resources, case)
    m = create_PV_model(m, h, number_resources, resources)

    m = create_electrolyzer_model(m, h, number_resources, resources)
    m = create_compressor_hydrogen_model(m, h, number_resources, resources, case)
    m = create_storage_hydrogen_model(m, h, number_resources, resources, case)

    m = create_compressor_air_model(m, h, number_resources, resources)
    m = create_air_separation_model(m, h, number_resources, resources)
    m = create_compressor_nitrogen_model(m, h, number_resources, resources)
    m = create_storage_nitrogen_model(m, h, number_resources, resources)

    m = create_ammonia_plant_model(m, h, number_resources, resources)
    m = create_storage_ammonia_model(m, h, number_resources, resources)
    m = create_ammonia_load_model(m, h, number_resources, resources)

    if case == 3:
        1
        m = create_storage_electrical_model(m, h, number_resources, resources)
        m = create_market_constraints(m, h, number_resources)

    return m


def create_bidding_model(m: ConcreteModel(), h: int, number_resources: int, case: int) -> ConcreteModel:
    ''' Create bidding model '''
    for t in range(0, h):
        resources_power = 0

        #resources_power = resources_power + \
        #                  sum(m.P_sto_E_ch[i, t] - m.P_sto_E_dis[i, t]
        #                      for i in range(0, number_resources))

        resources_power = resources_power + \
                          sum(m.P_C_air_E[i, t] for i in range(0, number_resources))
        resources_power = resources_power + \
                          sum(m.P_AS_E[i, t] for i in range(0, number_resources))
        resources_power = resources_power + \
                          sum(m.P_C_N2_E[i, t] for i in range(0, number_resources))
        resources_power = resources_power + \
                          sum(m.P_EL_E[i, t] + m.P_EL_cooling[i, t] for i in range(0, number_resources))
        resources_power = resources_power + \
                          sum(m.P_C_H2_E[i, t] for i in range(0, number_resources))
        resources_power = resources_power + \
                          sum(m.P_AP_E[i, t] for i in range(0, number_resources))
        resources_power = resources_power + \
                          sum(m.P_sto_NH3_E[i, t] for i in range(0, number_resources))
        resources_power = resources_power + \
                          sum(- m.P_PV[i, t] for i in range(0, number_resources))

        if case == 3:
            resources_power = resources_power + \
                              sum(m.P_sto_E_ch[i, t] for i in range(0, number_resources))
            resources_power = resources_power + \
                              sum(- m.P_sto_E_dis[i, t] for i in range(0, number_resources))

        m.c1.add(m.P_E[t] == resources_power)
        m.c1.add(m.P_E_pos[t] - m.P_E_neg[t] == m.P_E[t])
        m.c1.add(m.P_E_pos[t] + m.P_E_neg[t] == m.P_E[t])
        if case != 1:
            for t in range(0, h):
                m.c1.add(m.P_H2[t] == sum(m.P_C_H2_market[i, t] + m.P_sto_H2_market[i, t]
                                          for i in range(0, number_resources)))



    return m

def create_market_constraints(m: ConcreteModel(), h: int, number_resources: int) -> ConcreteModel:
    ''' Create market constraints model '''
    for i in range(0, number_resources):
        for t in range(0, h):
            m.c1.add(m.U_sto_E[i, t] == 2 * m.D_sto_E[i, t])

    return m

def create_PV_model(m: ConcreteModel(), h: int, number_resources: int, resources: dict) -> ConcreteModel:
    ''' Create PV model '''
    max_power = resources['PV']['max_power']
    PV_profile = resources['PV']['PV_profile']
    print(max_power)
    print(PV_profile)
    for i in range(0, number_resources):
        for t in range(0, h):
            m.c1.add(m.P_PV[i, t] <= max_power * PV_profile[t])

    return m

def create_storage_electrical_model(m: ConcreteModel(), h: int, number_resources: int, resources: dict) -> ConcreteModel:
    ''' Create electrical storage model '''
    rend_sto_E = resources['electrical_storage']['efficiency']
    soc_sto_E_max = resources['electrical_storage']['max_capacity']
    soc_sto_E_min = resources['electrical_storage']['min_capacity']
    P_sto_E_dis_max = resources['electrical_storage']['max_discharging']
    P_sto_E_ch_max = resources['electrical_storage']['max_charging']
    soc_sto_E_init = resources['electrical_storage']['initial_soc']

    for i in range(0, number_resources):
        m.c1.add(m.soc_sto_E[i, 0] == soc_sto_E_init)
        m.c1.add(m.soc_sto_E[i, h] >= soc_sto_E_init)

        for t in range(0, h):
            m.c1.add(m.soc_sto_E[i, t + 1] == m.soc_sto_E[i, t] + (m.P_sto_E_ch[i, t] * rend_sto_E - m.P_sto_E_dis[i, t] / rend_sto_E))

            m.c1.add(m.soc_sto_E[i, t + 1] <= soc_sto_E_max)
            m.c1.add(m.soc_sto_E[i, t + 1] >= soc_sto_E_min)

            m.c1.add(m.P_sto_E_dis[i, t] + m.P_sto_E_dis_space[i, t] >= (1 - m.b_sto_E[i, t]) * P_sto_E_dis_max)
            m.c1.add(m.P_sto_E_ch[i, t] + m.P_sto_E_ch_space[i, t] >=  m.b_sto_E[i, t] * P_sto_E_ch_max)

            if t == h - 1:
                m.c1.add(m.U_sto_E_dis[i, t] == 0)
                m.c1.add(m.U_sto_E_ch[i, t] == 0)
                m.c1.add(m.D_sto_E_dis[i, t] == 0)
                m.c1.add(m.D_sto_E_ch[i, t] == 0)

            m.c1.add(m.U_sto_E_dis[i, t] <= P_sto_E_dis_max - m.P_sto_E_dis[i, t])
            m.c1.add(m.U_sto_E_ch[i, t] <= m.P_sto_E_ch[i, t])
            m.c1.add(m.D_sto_E_ch[i, t] <= P_sto_E_ch_max - m.P_sto_E_ch[i, t])
            m.c1.add(m.D_sto_E_dis[i, t] <= m.P_sto_E_dis[i, t])

            m.c1.add(m.U_sto_E_dis[i, t] / rend_sto_E + m.U_sto_E_ch[i, t] * rend_sto_E <= m.soc_sto_E[i, t + 1] - soc_sto_E_min)
            m.c1.add(m.D_sto_E_dis[i, t] / rend_sto_E + m.D_sto_E_ch[i, t] * rend_sto_E <= soc_sto_E_max - m.soc_sto_E[i, t + 1])

            m.c1.add(m.U_sto_E[i, t] == m.U_sto_E_ch[i, t] + m.U_sto_E_dis[i, t])
            m.c1.add(m.D_sto_E[i, t] == m.D_sto_E_ch[i, t] + m.D_sto_E_dis[i, t])

            m.c1.add(m.U_sto_E_ch[i, t] + m.U_sto_E_dis[i, t] + m.D_sto_E_ch[i, t] + m.D_sto_E_dis[i, t] <=
                m.P_sto_E_ch_space[i, t + 1] + m.P_sto_E_dis_space[i, t + 1])

            m.c1.add(m.U_sto_E_ch[i, t] + m.U_sto_E_dis[i, t] + m.D_sto_E_ch[i, t] + m.D_sto_E_dis[i, t] <=
                m.b_sto_E_space[i, t] * 10000000)

            m.c1.add(m.P_sto_E_ch_space[i, t] + m.P_sto_E_dis_space[i, t] <= (1 - m.b_sto_E_space[i, t]) * 10000000)


    return m



def create_electrolyzer_model(m: ConcreteModel(), h: int, number_resources: int, resources: dict) -> ConcreteModel:
    ''' Create electrolyzer model '''
    efficiency = resources['electrolyzer']['efficiency']
    maximum_power = resources['electrolyzer']['max_power']
    transformation_factor = resources['electrolyzer']['transformation_factor']
    cooling_power = resources['electrolyzer']['cooling_power']

    for j in range(0, number_resources):
        for t in range(0, h):
            m.c1.add(m.P_EL_H2[j, t] == transformation_factor * efficiency * m.P_EL_E[j, t])
            m.c1.add(m.P_EL_H2[j, t] == m.P_EL_C_H2[j, t])
            m.c1.add(m.P_EL_cooling[j, t] == m.P_EL_E[j, t] / maximum_power * cooling_power)
            m.c1.add(m.P_EL_E[j, t] <= maximum_power)

    return m

def create_compressor_hydrogen_model(m: ConcreteModel(), h: int, number_resources: int, resources: dict, case: int) -> ConcreteModel:
    ''' Create hydrogen compressor model '''
    alpha = resources['hydrogen_compressor']['alpha']
    maximum_power = resources['hydrogen_compressor']['max_power']
    for t in range(0, h):
        for j in range(0, number_resources):
            m.c1.add(m.P_C_H2[j, t] == m.P_EL_C_H2[j, t])
            m.c1.add(m.P_C_H2_E[j, t] == alpha * m.P_C_H2[j, t])
            m.c1.add(m.P_C_H2[j, t] <= maximum_power)

            if case in [2, 3]:
                m.c1.add(m.P_C_H2[j, t] == m.P_C_H2_sto_H2[j, t] + m.P_C_H2_AP[j, t] + m.P_C_H2_market[j, t])
            else:
                m.c1.add(m.P_C_H2[j, t] == m.P_C_H2_sto_H2[j, t] + m.P_C_H2_AP[j, t])

    return m

def create_storage_hydrogen_model(m: ConcreteModel(), h: int, number_resources: int, resources: dict, case: int) -> ConcreteModel:
    ''' Create hydrogen storage model '''
    efficiency = resources['hydrogen_storage']['efficiency']
    max_soc = resources['hydrogen_storage']['max_capacity']
    min_soc = resources['hydrogen_storage']['min_capacity']
    max_power_dis = resources['hydrogen_storage']['max_discharging']
    max_power_ch = resources['hydrogen_storage']['max_charging']
    soc_initial = resources['hydrogen_storage']['initial_soc']

    for i in range(0, number_resources):
        m.c1.add(m.soc_sto_H2[i, 0] == soc_initial)
        m.c1.add(m.soc_sto_H2[i, h] >= soc_initial)

        for t in range(0, h):
            m.c1.add(m.soc_sto_H2[i, t + 1] == m.soc_sto_H2[i, t] +
                     (m.P_sto_H2_ch[i, t] * efficiency - m.P_sto_H2_dis[i, t] / efficiency))
            m.c1.add(m.soc_sto_H2[i, t] <= max_soc)
            m.c1.add(m.soc_sto_H2[i, t] >= min_soc)
            m.c1.add(m.P_sto_H2_ch[i, t] == m.P_C_H2_sto_H2[i, t])
            m.c1.add(m.P_sto_H2_ch[i, t] <= m.b_sto_H2_ch[i, t] * max_power_ch)
            m.c1.add(m.P_sto_H2_dis[i, t] <= (1 - m.b_sto_H2_ch[i, t]) * max_power_dis)

            if case in [2, 3]:
                m.c1.add(m.P_sto_H2_dis[i, t] == m.P_sto_H2_AP[i, t] + m.P_sto_H2_market[i, t])
            else:
                m.c1.add(m.P_sto_H2_dis[i, t] == m.P_sto_H2_AP[i, t])

    return m


def create_compressor_air_model(m: ConcreteModel(), h: int, number_resources: int, resources: dict) -> ConcreteModel:
    ''' Create air compressor model '''
    alpha = resources['air_compressor']['alpha']
    maximum_power = resources['air_compressor']['max_power']
    for t in range(0, h):
        for j in range(0, number_resources):
            m.c1.add(m.P_C_air[j, t] == m.P_C_air_AS[j, t])
            m.c1.add(m.P_C_air_E[j, t] == alpha * m.P_C_air[j, t])
            m.c1.add(m.P_C_air[j, t] <= maximum_power)

    return m

def create_air_separation_model(m: ConcreteModel(), h: int, number_resources: int, resources: dict) -> ConcreteModel:
    ''' Create air seperation model '''
    alpha_E = resources['air_separation']['alpha_E']
    transformation_factor = resources['air_separation']['transformation_factor']
    maximum_energy_N2 = resources['air_separation']['max_energy_N2']
    for t in range(0, h):
        for j in range(0, number_resources):
            m.c1.add(m.P_AS_N2[j, t] == transformation_factor * m.P_AS_air[j, t])
            m.c1.add(m.P_AS_E[j, t] == alpha_E * m.P_AS_N2[j, t])
            m.c1.add(m.P_AS_air[j, t] == m.P_C_air_AS[j, t])
            m.c1.add(m.P_AS_N2[j, t] == m.P_AS_C_N2[j, t])
            m.c1.add(m.P_AS_N2[j, t] <= maximum_energy_N2)

    return m

def create_compressor_nitrogen_model(m: ConcreteModel(), h: int, number_resources: int, resources: dict) -> ConcreteModel:
    ''' Create air compressor model '''
    alpha = resources['nitrogen_compressor']['alpha']
    maximum_power = resources['nitrogen_compressor']['max_power']
    for t in range(0, h):
        for j in range(0, number_resources):
            m.c1.add(m.P_C_N2[j, t] == m.P_AS_C_N2[j, t])
            m.c1.add(m.P_C_N2[j, t] == m.P_C_N2_sto_N2[j, t] + m.P_C_N2_AP[j, t])
            m.c1.add(m.P_C_N2_E[j, t] == alpha * m.P_C_N2[j, t])
            m.c1.add(m.P_C_N2[j, t] <= maximum_power)

    return m

def create_storage_nitrogen_model(m: ConcreteModel(), h: int, number_resources: int, resources: dict) -> ConcreteModel:
    ''' Create nitrogen storage model '''
    efficiency = resources['nitrogen_storage']['efficiency']
    max_soc = resources['nitrogen_storage']['max_capacity']
    min_soc = resources['nitrogen_storage']['min_capacity']
    max_power_dis = resources['nitrogen_storage']['max_discharging']
    max_power_ch = resources['nitrogen_storage']['max_charging']
    soc_initial = resources['nitrogen_storage']['initial_soc']

    for i in range(0, number_resources):
        m.c1.add(m.soc_sto_N2[i, 0] == soc_initial)
        m.c1.add(m.soc_sto_N2[i, h] >= soc_initial)

        for t in range(0, h):
            m.c1.add(m.soc_sto_N2[i, t + 1] == m.soc_sto_N2[i, t] +
                     (m.P_sto_N2_ch[i, t] * efficiency - m.P_sto_N2_dis[i, t] / efficiency))
            m.c1.add(m.soc_sto_N2[i, t] <= max_soc)
            m.c1.add(m.soc_sto_N2[i, t] >= min_soc)
            m.c1.add(m.P_sto_N2_ch[i, t] == m.P_C_N2_sto_N2[i, t])
            m.c1.add(m.P_sto_N2_dis[i, t] == m.P_sto_N2_AP[i, t])
            m.c1.add(m.P_sto_N2_ch[i, t] <= m.b_sto_N2_ch[i, t] * max_power_ch)
            m.c1.add(m.P_sto_N2_dis[i, t] <= (1 - m.b_sto_N2_ch[i, t]) * max_power_dis)

    return m




def create_ammonia_plant_model(m: ConcreteModel(), h: int, number_resources: int, resources: dict) -> ConcreteModel:
    ''' Create ammonia plant model '''
    alpha_H2 = resources['ammonia_plant']['alpha_H2']
    alpha_N2 = resources['ammonia_plant']['alpha_N2']
    alpha_E = resources['ammonia_plant']['alpha_E']
    eff_H2 = resources['ammonia_plant']['efficiency_H2']
    eff_N2 = resources['ammonia_plant']['efficiency_N2']
    max_power = resources['ammonia_plant']['max_power_NH3']
    max_power_H2 = resources['ammonia_plant']['max_power_H2']
    max_power_N2 = resources['ammonia_plant']['max_power_N2']

    for i in range(0, number_resources):
        for t in range(0, h):
            m.c1.add(m.P_AP[i, t] == alpha_H2 * m.P_AP_H2[i, t])
            m.c1.add(m.P_AP[i, t] == alpha_N2 * m.P_AP_N2[i, t])
            m.c1.add(m.P_AP_E[i, t] == alpha_E * m.P_AP[i, t])

            m.c1.add(m.P_AP_H2[i, t] == eff_H2 * (m.P_C_H2_AP[i, t] + m.P_sto_H2_AP[i, t]))
            m.c1.add(m.P_AP_N2[i, t] == eff_N2 * (m.P_sto_N2_AP[i, t] + m.P_C_N2_AP[i, t]))

            m.c1.add(m.P_AP[i, t] == m.P_AP_sto_NH3[i, t] + m.P_AP_load[i, t])
            m.c1.add(m.P_AP[i, t] <= max_power)
            m.c1.add(m.P_AP_H2[i, t] <= max_power_H2)
            m.c1.add(m.P_AP_N2[i, t] <= max_power_N2)

    return m

def create_storage_ammonia_model(m: ConcreteModel(), h: int, number_resources: int, resources: dict) -> ConcreteModel:
    ''' Create ammonia storage model '''
    efficiency = resources['ammonia_storage']['efficiency']
    max_soc = resources['ammonia_storage']['max_capacity']
    min_soc = resources['ammonia_storage']['min_capacity']
    max_power_dis = resources['ammonia_storage']['max_discharging']
    max_power_ch = resources['ammonia_storage']['max_charging']
    soc_initial = resources['ammonia_storage']['initial_soc']
    alpha_E = resources['ammonia_storage']['alpha_E']

    for i in range(0, number_resources):
        m.c1.add(m.soc_sto_NH3[i, 0] == soc_initial)
        m.c1.add(m.soc_sto_NH3[i, h] >= soc_initial)

        for t in range(0, h):
            m.c1.add(m.soc_sto_NH3[i, t + 1] == m.soc_sto_NH3[i, t] +
                     (m.P_sto_NH3_ch[i, t] * efficiency - m.P_sto_NH3_dis[i, t] / efficiency))
            m.c1.add(m.soc_sto_NH3[i, t] <= max_soc)
            m.c1.add(m.soc_sto_NH3[i, t] >= min_soc)
            m.c1.add(m.P_sto_NH3_ch[i, t] == m.P_AP_sto_NH3[i, t])
            m.c1.add(m.P_sto_NH3_dis[i, t] == m.P_sto_NH3_load[i, t])
            m.c1.add(m.P_sto_NH3_ch[i, t] <= m.b_sto_NH3_ch[i, t] * max_power_ch)
            m.c1.add(m.P_sto_NH3_dis[i, t] <= (1 - m.b_sto_NH3_ch[i, t]) * max_power_dis)
            m.c1.add(m.P_sto_NH3_E[i, t] == (m.P_sto_NH3_ch[i, t] + m.P_sto_NH3_dis[i, t]) * alpha_E)

    return m

def create_ammonia_load_model(m: ConcreteModel(), h: int, number_resources: int, resources: dict) -> ConcreteModel:
    ''' Create ammonia load model '''
    for i in range(0, number_resources):
        for t in range(0, h):
            m.c1.add(resources['load_ammonia'][0] == m.P_sto_NH3_load[i, t] + m.P_AP_load[i, t])

    return m


