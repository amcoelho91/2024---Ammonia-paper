from numpy import *
from pyomo.environ import *
import pandas as pd
from pathlib import Path
import json

INPUT_DIR = Path(__file__).parent.parent / "data_input"


def get_resources(case_nr: int) -> dict:
    ''' Get resources data '''

    electrical_storage = {'efficiency': 0.9,
                        'initial_soc': 50000 * 0.7,
                        'max_capacity': 50000,
                        'min_capacity': 2500,
                        'max_discharging': 25000,
                        'max_charging': 25000,
                         }




    if case_nr in [1, 2, 3]:
        PV =            {"max_power": 50000 * 0.5,              # kW
                         "PV_profile": get_PV_profile(case_nr)}  # profile (%)
    else:
        PV = {"max_power": 50000 * 1,  # kW
              "PV_profile": get_PV_profile(case_nr)}  # profile (%)

    if case_nr in [1, 3]:
        electrolyzer = {    'efficiency': 0.78,
                            'max_power': 50000 * 1,                   # kW    ############################################################################################
                            'transformation_factor': 25.35/1000,  # kg H2/kWh -> 25.35 kg H2/MWh
                            'c_H2O': 10,                          # 10 L/kg H2
                            'c_O2': 8.304,                        # 8.304 kg O2 / kg H2
                            'cooling_power': 962                  # kW
                        }

        hydrogen_compressor = {'alpha': 1.79,       # kW/kg
                               'max_power': 1267.5 * 1, # kg
                         }
    else:
        electrolyzer = {'efficiency': 0.78,
                        'max_power': 50000 * 2,
                        # kW    ############################################################################################
                        'transformation_factor': 25.35 / 1000,  # kg H2/kWh -> 25.35 kg H2/MWh
                        'c_H2O': 10,  # 10 L/kg H2
                        'c_O2': 8.304,  # 8.304 kg O2 / kg H2
                        'cooling_power': 962  # kW
                        }

        hydrogen_compressor = {'alpha': 1.79,  # kW/kg
                               'max_power': 1267.5 * 2,  # kg
                               }




    hydrogen_storage = {'efficiency': 1,
                        'max_capacity': 4000,   # kg
                        'min_capacity': 400,    # kg
                        'max_discharging': 1267.5, # kg/h
                        'max_charging': 1267.5,    # kg/h
                        'initial_soc': 2000      # kg
                        }

    air_compressor = {'alpha': 0.0157,    # kW/kg
                        'max_power': 8700 * 1.1, # kg/h
                     }

    air_separation = {'alpha_E': 0.2544,                # kW/kg N2
                      'max_energy_N2': 3455 * 1.1,            # kg N2/h
                      'transformation_factor': 1/2.444,# kg N2 /kg air ##############################################
                     }

    nitrogen_compressor = {'alpha': 0.195,  # kW/kg
                        'max_power': 3455 * 1.1,   # kg/h
                     }

    nitrogen_storage = {'efficiency': 1,
                        'max_capacity': 136818,  # kg ##############################################
                        'min_capacity': 20408,   # kg
                        'max_discharging': 3455 * 1.1, # kg/h
                        'max_charging': 3455 * 1.1,    # kg/h
                        'initial_soc': 60000     # kg
                        }

    ammonia_plant = {   'alpha_H2': 1/0.177, # kg NH3/ kg H2
                        'alpha_N2': 1/0.823, # kg NH3/ kg N2
                        'alpha_E': 0.217,  # kW/ kg NH3
                        'efficiency_H2': 1,
                        'efficiency_N2': 1,
                        'max_power_H2': 1267.5,   # kg H2/h
                        'max_power_N2': 3455 * 1.1,  # kg N2/h
                        'max_power_NH3': 4200 * 1.1  # kg NH3/h
                    }

    ammonia_storage = {'efficiency': 1,
                        'max_capacity': 236145,  # kg  ##############################################
                        'min_capacity': 4200 * 36,    # kg
                        'max_discharging': 5000 * 1.1, # kg/g
                        'max_charging': 5000 * 1.1,    # kg/h
                        'initial_soc': 4200 * 36,    # kg
                        'alpha_E': 0.196             # KW/kg
                        }

    load_ammonia = [4200 for i in range(0, 24)]

    resources = {       'PV': PV,
                        'electrical_storage': electrical_storage,
                        'electrolyzer': electrolyzer,
                        'hydrogen_compressor': hydrogen_compressor,
                        'hydrogen_storage': hydrogen_storage,

                        'air_compressor': air_compressor,
                        'air_separation': air_separation,
                        'nitrogen_compressor': nitrogen_compressor,
                        'nitrogen_storage': nitrogen_storage,

                        'ammonia_plant': ammonia_plant,
                        'ammonia_storage': ammonia_storage,
                        'load_ammonia': load_ammonia
                 }

    return resources



def get_PV_profile(case_nr) -> list:
    ''' Load PV data from JSON and read the swflx values'''

    if case_nr == 1:
        ''' Gets the data from JSON and transforms it '''
        with open(INPUT_DIR / "Montijo.json", encoding='utf-8') as inputfile:
            df = pd.read_json(inputfile)

        PV_profile = []
        PV_profile_data = []
        test_date = df['data'][0]['datetime']
        for i in range(0, len(df)):
            if 1:
                if df['data'][i]['datetime']  != test_date and df['data'][i]['datetime'][0:4] == '2022':
                    test_date = df['data'][i]['datetime']
                    PV_profile_data.append([df['data'][i]['datetime'][0:10],
                                            df['data'][i]['datetime'][11:],
                                            df['data'][i]['variable']['swflx'],
                                            df['data'][i]['variable']['swflx']/1030]) # 1030 is the maximum swflx, used to
                                                                                      # put PV in percentage
                    PV_profile.append(df['data'][i]['variable']['swflx'])
        PV_profile.append(0)
        pd.DataFrame(PV_profile_data).to_csv(INPUT_DIR / 'PV_profile_data.csv')

        PV_profile = [i/max(PV_profile) for i in PV_profile]

    elif case_nr == 2:
        ''' Loads the data from excel file '''
        df = pd.read_csv(INPUT_DIR / 'PV_profile_data_short.csv')
        PV_profile = df['2'].values.tolist()
        PV_profile = [i/max(PV_profile) for i in PV_profile]
        PV_profile.reverse()
    else:
        ''' Loads the data from excel file '''
        df = pd.read_csv(INPUT_DIR / 'PV_profile_data_4days.csv')
        PV_profile = df['2'].values.tolist()
        PV_profile = [i/max(PV_profile) for i in PV_profile]
        PV_profile.reverse()

    print(PV_profile)
    print(max(PV_profile))
    return PV_profile
