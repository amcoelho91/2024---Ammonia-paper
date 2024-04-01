from numpy import *
from pyomo.environ import *


def create_PV_variables(m: ConcreteModel, h: int, number_resources: int) -> ConcreteModel:
    ''' Create variables for the PV model'''
    m.P_PV = Var(arange(number_resources), arange(h), domain=NonNegativeReals)

    return m

def create_storage_electrical_variables(m: ConcreteModel, h: int, number_resources: int) -> ConcreteModel:
    ''' Create variables for the electrical storage model'''
    m.soc_sto_E = Var(arange(number_resources), arange(h + 1), domain=NonNegativeReals)
    m.P_sto_E_ch = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_sto_E_dis = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_sto_E_ch_space = Var(arange(number_resources), arange(h + 1), domain=NonNegativeReals)
    m.P_sto_E_dis_space = Var(arange(number_resources), arange(h + 1), domain=NonNegativeReals)
    m.U_sto_E = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.U_sto_E_ch = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.U_sto_E_dis = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.D_sto_E = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.D_sto_E_ch = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.D_sto_E_dis = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.b_sto_E = Var(arange(number_resources), arange(h), domain=Binary)
    m.b_sto_E_space = Var(arange(number_resources), arange(h), domain=Binary)

    return m

def create_electrolyzer_variables(m: ConcreteModel, h: int, number_resources: int) -> ConcreteModel:
    ''' Create variables for the electrolyzer model '''
    m.P_EL_E = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_EL_H2 = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_EL_C_H2 = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_EL_cooling = Var(arange(number_resources), arange(h), domain=NonNegativeReals)

    return m

def create_compressor_H2_variables(m: ConcreteModel, h: int, number_resources: int) -> ConcreteModel:
    ''' Create variables for the hydrogen compressor model '''
    m.P_C_H2 = Var(arange(number_resources), arange(h + 1), domain=NonNegativeReals)
    m.P_EL_CH_H2 = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_C_H2_sto_H2 = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_C_H2_market = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_C_H2_AP = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_C_H2_E = Var(arange(number_resources), arange(h), domain=NonNegativeReals)

    return m

def create_storage_H2_variables(m: ConcreteModel, h: int, number_resources: int) -> ConcreteModel:
    ''' Create variables for the hydrogen storage model '''
    m.soc_sto_H2 = Var(arange(number_resources), arange(h + 1), domain=NonNegativeReals)
    m.P_sto_H2_ch = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_sto_H2_dis = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_sto_H2_market = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_sto_H2_AP = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.b_sto_H2_ch = Var(arange(number_resources), arange(h), domain=Binary)
    #m.b_sto_H2_dis = Var(arange(number_resources), arange(h), domain=Binary)

    return m

def create_compressor_air_variables(m: ConcreteModel, h: int, number_resources: int) -> ConcreteModel:
    ''' Create variables for the air compressor storage (hydrogen) model '''
    m.P_C_air = Var(arange(number_resources), arange(h + 1), domain=NonNegativeReals)
    m.P_C_air_sto_air = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_C_air_AS = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_C_air_E = Var(arange(number_resources), arange(h), domain=NonNegativeReals)

    return m

def create_storage_air_variables(m: ConcreteModel, h: int, number_resources: int) -> ConcreteModel:
    ''' Create variables for the air storage model '''
    m.soc_sto_air = Var(arange(number_resources), arange(h + 1), domain=NonNegativeReals)
    m.P_sto_air_ch = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_sto_air_dis = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_sto_air_AS = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.b_sto_air_ch = Var(arange(number_resources), arange(h), domain=Binary)
    #m.b_sto_air_dis = Var(arange(number_resources), arange(h), domain=Binary)

    return m

def create_air_separation_variables(m: ConcreteModel, h: int, number_resources: int) -> ConcreteModel:
    ''' Create variables for the air separation unit model '''
    m.P_AS_N2 = Var(arange(number_resources), arange(h + 1), domain=NonNegativeReals)
    m.P_AS_air = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_AS_E = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_AS_C_N2 = Var(arange(number_resources), arange(h), domain=NonNegativeReals)

    return m

def create_compressor_N2_variables(m: ConcreteModel, h: int, number_resources: int) -> ConcreteModel:
    ''' Create variables for the nitrogen compressor model '''
    m.P_C_N2 = Var(arange(number_resources), arange(h + 1), domain=NonNegativeReals)
    m.P_C_N2_AP = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_C_N2_sto_N2 = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_C_N2_E = Var(arange(number_resources), arange(h), domain=NonNegativeReals)

    return m

def create_storage_N2_variables(m: ConcreteModel, h: int, number_resources: int) -> ConcreteModel:
    ''' Create variables for the nitrogen storage model '''
    m.soc_sto_N2 = Var(arange(number_resources), arange(h + 1), domain=NonNegativeReals)
    m.P_sto_N2_ch = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_sto_N2_dis = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_sto_N2_AP = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.b_sto_N2_ch = Var(arange(number_resources), arange(h), domain=Binary)
    #m.b_sto_air_dis = Var(arange(number_resources), arange(h), domain=Binary)

    return m

def create_ammonia_plant_variables(m: ConcreteModel, h: int, number_resources: int) -> ConcreteModel:
    ''' Create variables for the ammonia plant model '''
    m.P_AP = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_AP_H2 = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_AP_N2 = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_AP_E = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_AP_sto_NH3 = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_AP_load = Var(arange(number_resources), arange(h), domain=NonNegativeReals)

    return m

def create_storage_NH3_variables(m: ConcreteModel, h: int, number_resources: int) -> ConcreteModel:
    ''' Create variables for the ammonia storage model '''
    m.soc_sto_NH3 = Var(arange(number_resources), arange(h + 1), domain=NonNegativeReals)
    m.P_sto_NH3_ch = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_sto_NH3_dis = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_sto_NH3_load = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.P_sto_NH3_E = Var(arange(number_resources), arange(h), domain=NonNegativeReals)
    m.b_sto_NH3_ch = Var(arange(number_resources), arange(h), domain=Binary)
    m.b_sto_NH3_dis = Var(arange(number_resources), arange(h), domain=Binary)
    return m

def create_load_variables(m: ConcreteModel, h: int, number_resources: int) -> ConcreteModel:
    ''' Create variables for the ammonia load model '''
    m.P_load = Var(arange(number_resources), arange(h), domain=NonNegativeReals)

    return m

def create_objective_function_variables(m: ConcreteModel, h: int, number_resources: int) -> ConcreteModel:
    ''' Create variables for the objective function '''
    m.P_E = Var(arange(h), domain=Reals)
    m.P_E_pos = Var(arange(h), domain=NonNegativeReals)
    m.P_E_neg = Var(arange(h), domain=NonNegativeReals)
    m.U_E = Var(arange(h), domain=NonNegativeReals)
    m.D_E = Var(arange(h), domain=NonNegativeReals)
    m.P_H2 = Var(arange(h), domain=NonNegativeReals)
    m.P_NH3 = Var(arange(h), domain=NonNegativeReals)

    return m


def create_variables(m: ConcreteModel, h: int, number_resources: int) -> ConcreteModel:
    ''' Create variables for the optimization model '''
    m = create_objective_function_variables(m, h, number_resources)
    m = create_PV_variables(m, h, number_resources)
    m = create_storage_electrical_variables(m, h, number_resources)

    m = create_electrolyzer_variables(m, h, number_resources)
    m = create_compressor_H2_variables(m, h, number_resources)
    m = create_storage_H2_variables(m, h, number_resources)

    m = create_compressor_air_variables(m, h, number_resources)
    m = create_air_separation_variables(m, h, number_resources)
    m = create_compressor_N2_variables(m, h, number_resources)
    m = create_storage_N2_variables(m, h, number_resources)

    m = create_ammonia_plant_variables(m, h, number_resources)
    m = create_storage_NH3_variables(m, h, number_resources)
    m = create_load_variables(m, h, number_resources)

    return m
