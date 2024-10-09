import json
import logging
from functools import wraps
from typing import OrderedDict

from numpy import nan
from sixgill.pipesim import Model
from sixgill.definitions import Units,Parameters,ModelComponents,ProfileVariables,SystemVariables
import pandas as pd
import sys
import time
sys.path.append('.')
from  core.models import AbstractProjectModel,type_property,Flowline
from  core import tools

from io import StringIO

import six


# manta.server.manager.logger.addHandler(logging.NullHandler())
# log_stream = StringIO()
# # logging.basicConfig(stream=log_stream)
# logging.basicConfig(filename='app.log', filemode='w',level=logging.INFO)
fileHandler = logging.FileHandler('app.log')
class LogStream(object):
    def __init__(self):
        self.logs = ''

    def write(self, str):
        self.logs += str

    def flush(self):
        pass

    def __str__(self):
        return self.logs

log_stream = LogStream()
# logging.basicConfig(stream=log_stream,level=logging.ERROR)

# log=logging.getLogger('manta.server.manager')
# log=logging.getLogger()
# FORMAT = "%(process)s %(thread)s: %(message)s"
FORMAT = "%(levelname)s: %(name)s: %(message)s"
formatter=logging.Formatter(fmt=FORMAT)
fileHandler.setFormatter(formatter)
# log.addHandler(fileHandler)
# log.propagate = False
# log.info('1234567890')
loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
for l in loggers:
    l.propagate=False
    l.addHandler(fileHandler)
# loggers = [name for name in logging.root.manager.loggerDict]
# print(loggers)

def log_function_call(func):
    def wrapper(*args, **kwargs):
        print("Wrapper")
        logging.info(f"Calling {func.__name__} with args: {args} and kwargs: {kwargs}")
        result = func(*args, **kwargs)
        logging.info(f"{func.__name__} returned: {result}")
        return result
    return wrapper

# -----------------------------------------------------------------------------
#  Logging Decorators
# -----------------------------------------------------------------------------

def log_error(func):
    @wraps(func)
    def log_and_raise(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
            name = func.__globals__['__name__']
            print(name)
        except Exception as err:
            name = func.__globals__['__name__']
            print(name)
            func_logger = logging.getLogger(name)
            func_logger.exception(err)
            six.reraise(*sys.exc_info())
        return ret
    return log_and_raise

params_base=[
        Parameters.Flowline.GEOMETRYPROFILE,

        Parameters.Flowline.GEOTHERMALPROFILE,

        Parameters.Flowline.HORIZONTALDISTANCE,
        Parameters.Flowline.ELEVATIONDIFFERENCE,
        Parameters.Flowline.INNERDIAMETER,
        Parameters.Flowline.WALLTHICKNESS,
        Parameters.Flowline.ROUGHNESS,
        Parameters.Flowline.AMBIENTAIRTEMPERATURE,
        Parameters.Flowline.HeatTransfer.UCOEFFUSERAIR,
        Parameters.Flowline.HeatTransfer.UCOEFFUSER,
        ]
params_ext=[
        Parameters.Flowline.GEOMETRYPROFILE,
        Parameters.Flowline.GEOTHERMALPROFILE,
]

def get_names(model:Model):
    out_dict={}
    for prop in type_property:
        out_dict[prop]=[item['Name'] for item in model.find_components(component=prop)]
    return out_dict

def get_data_flowlines(model:Model):
    flow_lines=model.get_values(component=ModelComponents.FLOWLINE,parameters=params_base)
    flow_lines_dict={}
    for k,v in flow_lines.items():
        flow_lines_dict[k]=Flowline(**v)
    return flow_lines_dict

def get_network(model:Model):
    return model.connections()

def get_indata(model:Model):
    out=model.get_values(component=ModelComponents.SOURCE,
                         parameters=['Pressure','Temperature','GasFlowRate'])
    out.update(model.get_values(component=ModelComponents.SINK,
                         parameters=['Pressure','Temperature','GasFlowRate']))
    return out

def get_simulation(model:Model):
    system_variables = [
        SystemVariables.SYSTEM_OUTLET_TEMPERATURE, # (T вых)(Tout)
        SystemVariables.SYSTEM_TEMPERATURE_DIFFERENCE, # ((T вх)=(T вых)+(*))(Tin)
        
        SystemVariables.TEMPERATURE, # (T вх)(Tout) (Node)
        SystemVariables.PRESSURE, # (P вх)(Pin) (Node)
        
        SystemVariables.SYSTEM_OUTLET_PRESSURE, # (P исх)(Pout)
        SystemVariables.SYSTEM_INLET_PRESSURE, # (P вх)(Pin)
        SystemVariables.OUTLET_MASS_FLOWRATE_FLUID, # (Массовый расход газа)(MassRate) (*60 *60)
        SystemVariables.OUTLET_VOLUME_FLOWRATE_GAS_STOCKTANK, # (Расход газа)(GasRate)

        SystemVariables.MAXIMUM_VELOCITY_GAS, # (Макс скорость газа)(GasVelocity)(??)
    ]

    profile_variables = [ 
        ProfileVariables.TEMPERATURE,
        ProfileVariables.PRESSURE,
        ProfileVariables.ELEVATION,
        ProfileVariables.TOTAL_DISTANCE
    ] 
    simulation_id = model.tasks.networksimulation.start(
        profile_variables=profile_variables,
        system_variables=system_variables,options={"GenerateOutputFile":False,"Restart":False,"Parallelism":4})
    
    # results=model.tasks.networksimulation.run(options={"GenerateOutputFile":False,"Restart":False,"Parallelism":4})
    
    i=0
    start_time = time.time()
    print(f'Start simulation {start_time}')
    status = model.tasks.networksimulation.get_state(simulation_id)
    while status =='Running':
        i=i+1
        status = model.tasks.networksimulation.get_state(simulation_id)
        if (time.time() - start_time) > 25: 
            status = 'Flied'

        # print(f'{i} State simulation {model.tasks.networksimulation.get_state(simulation_id)}')
    
    print(f'-- State simulation {model.tasks.networksimulation.get_state(simulation_id)}')
    print("--- %s seconds ---" % (time.time() - start_time))

    results = model.tasks.networksimulation.get_results(simulation_id)
    return results# .system


def get_conditions(model:Model):
    return pd.DataFrame.from_dict(model.tasks.networksimulation.get_conditions()).T[[
        'Temperature', 'Pressure', 'FlowRateType', 'GasFlowRate']].T.to_dict()
def get_constraints(model:Model):
    return model.tasks.networksimulation.get_constraints()

@log_error
def open():
    filename='D:\\repos\\Pipesim_\\test-test-test.pips'
    return Model.open(filename=filename, units=Units.METRIC)


if __name__=='__main__':
    filename='D:\\repos\\Pipesim_\\test-test-test.pips'
    # flowline=Flowline
    # for member in [attr for attr in dir(flowline) 
    #                    if not callable(getattr(flowline, attr)) 
    #                    and (not attr.startswith("_"))]:
    #     print(member)
    
    # model=Model.open(filename=filename, units=Units.METRIC)
    model=open()
    # print(model.get_values(component=ModelComponents.FLOWLINE,parameters=params_base))
    names=get_names(model)
    flow_lines=get_data_flowlines(model)
    network=get_network(model)
    in_data=get_indata(model)
    conditions=get_conditions(model)
    constraints=get_constraints(model)
    # simulation=get_simulation(model)
    print(model.session)
    model.close()
    print(model.session)
    # model.close()
    # print('-'*25,'names','-'*25)
    # # print(pd.DataFrame.from_dict(in_data))
    # print(names)
    # print('-'*25,'flow_lines_dict','-'*25)
    # # print(pd.DataFrame.from_dict(in_data))
    # print(json.dumps(flow_lines,cls=tools.JsonClassEncoder))
    # print('-'*25,'network','-'*25)
    # # print(pd.DataFrame.from_dict(in_data))
    # print(network)
    # print('-'*25,'in_data','-'*25)
    # # print(pd.DataFrame.from_dict(in_data))
    # print(in_data)
    # print('-'*25,'conditions','-'*25)
    # # print(pd.DataFrame.from_dict(conditions))
    # print(conditions)
    # print('-'*25,'constraints','-'*25)
    # # print(pd.DataFrame.from_dict(constraints))
    # print(constraints)
    # print('-'*25,'simulation','-'*25)
    # print(pd.DataFrame(simulation.messages))
    # print(pd.DataFrame.from_dict(simulation.summary, orient="index").T)
    # print(pd.DataFrame.from_dict(simulation.system, orient="index").to_dict())
    # print(simulation.system)
    
    # print('-'*50)
    # for k,v in names.items():
    #     print(k,v)
    # print('-'*50)
    # for k,v in flow_lines_dict.items():
    #     print(k,v.to_json())
    
    print(log_stream)
    # print(log_stream.getvalue())
    names_dict={
        'Flowline': ['kg202-205.Flowline_1', 'kg202.Flowline_1', 'kg205.Flowline_1'], 
        'Source': ['KG_205', 'KG_202'], 
        'Sink': ['u2-202-205'], 
        'Junction': ['t-u2-202-205'], 
        'Choke': ['Ck', 'Ckc']
    }
    # flow_lines_dict={
    #     'kg202-205.Flowline_1': Flowline(HorizontalDistance=8198.0, Elevation=80.0, Diameter=426.0, WallThickness=33.0, Temperature=13.1, Roughness=0.1, UcoeffuserAir=3.302208, 
    #                                      GeoProfile=[
    #                                          Profile(HorizontalDistance=0.0, Elevation=1019.9999999999997, MeasuredDistance=0.0), 
    #                                          Profile(HorizontalDistance=839.0, Elevation=1019.9999999999997, MeasuredDistance=839.0), 
    #                                          Profile(HorizontalDistance=1256.0, Elevation=1059.9999999999993, MeasuredDistance=1257.9140723346495), 
    #                                          Profile(HorizontalDistance=3026.9999999999977, Elevation=1059.9999999999993, MeasuredDistance=3028.9140723346495), 
    #                                          Profile(HorizontalDistance=3707.999999999998, Elevation=1100.0, MeasuredDistance=3711.087803872298), 
    #                                          Profile(HorizontalDistance=4166.999999999999, Elevation=1139.9999999999998, MeasuredDistance=4171.827426652888), 
    #                                          Profile(HorizontalDistance=4414.999999999998, Elevation=1159.9999999999986, MeasuredDistance=4420.632571294232), 
    #                                          Profile(HorizontalDistance=4828.999999999997, Elevation=1159.9999999999986, MeasuredDistance=4834.632571294232), 
    #                                          Profile(HorizontalDistance=5560.000000000001, Elevation=1100.0, MeasuredDistance=5568.0908182313015), 
    #                                          Profile(HorizontalDistance=6062.999999999998, Elevation=1079.9999999999995, MeasuredDistance=6071.488275515305), 
    #                                          Profile(HorizontalDistance=6861.999999999999, Elevation=1079.9999999999995, MeasuredDistance=6870.488275515305), 
    #                                          Profile(HorizontalDistance=8197.999999999998, Elevation=1100.0, MeasuredDistance=8206.63796772797)]), 
    #     'kg202.Flowline_1': Flowline(HorizontalDistance=1161.0, Elevation=-96.0, Diameter=325.0, WallThickness=26.0, Temperature=13.1, Roughness=0.1, UcoeffuserAir=4.272857, 
    #                                  GeoProfile=[
    #                                      Profile(HorizontalDistance=0.0, Elevation=1116.0, MeasuredDistance=0.0), 
    #                                      Profile(HorizontalDistance=357.9999999999999, Elevation=1100.0, MeasuredDistance=358.35736353534026), 
    #                                      Profile(HorizontalDistance=1160.9999999999998, Elevation=1019.9999999999997, MeasuredDistance=1165.3325800073208)]), 
    #     'kg205.Flowline_1': Flowline(HorizontalDistance=11086.0, Elevation=90.0, Diameter=325.0, WallThickness=26.0, Temperature=13.1, Roughness=0.1, UcoeffuserAir=4.272857, 
    #                                  GeoProfile=[
    #                                      Profile(HorizontalDistance=0.0, Elevation=929.9999999999999, MeasuredDistance=0.0), 
    #                                      Profile(HorizontalDistance=385.99999999999994, Elevation=940.0000000000001, MeasuredDistance=386.12951195162486), 
    #                                      Profile(HorizontalDistance=1007.9999999999994, Elevation=944.9999999999991, MeasuredDistance=1008.1496080900052), 
    #                                      Profile(HorizontalDistance=1880.0000000000002, Elevation=940.0000000000001, MeasuredDistance=1880.1639428345666), 
    #                                      Profile(HorizontalDistance=2700.999999999998, Elevation=959.9999999999994, MeasuredDistance=2701.4075120635744), 
    #                                      Profile(HorizontalDistance=3618.999999999997, Elevation=979.9999999999999, MeasuredDistance=3619.6253511409905), 
    #                                      Profile(HorizontalDistance=3878.999999999998, Elevation=999.9999999999992, MeasuredDistance=3880.3934473490963), 
    #                                      Profile(HorizontalDistance=4189.0, Elevation=1019.9999999999997, MeasuredDistance=4191.037938689277), 
    #                                      Profile(HorizontalDistance=4515.999999999999, Elevation=1039.9999999999998, MeasuredDistance=4518.648988563972), 
    #                                      Profile(HorizontalDistance=5159.0, Elevation=1059.9999999999993, MeasuredDistance=5161.959955359969), 
    #                                      Profile(HorizontalDistance=5643.999999999998, Elevation=1079.9999999999995, MeasuredDistance=5647.3721513336595), 
    #                                      Profile(HorizontalDistance=6757.0, Elevation=1059.9999999999993, MeasuredDistance=6760.551831349424), 
    #                                      Profile(HorizontalDistance=8817.999999999996, Elevation=1079.9999999999995, MeasuredDistance=8821.64886933672), 
    #                                      Profile(HorizontalDistance=9143.999999999995, Elevation=1079.9999999999995, MeasuredDistance=9147.64886933672), 
    #                                      Profile(HorizontalDistance=10170.999999999995, Elevation=1079.9999999999995, MeasuredDistance=10174.64886933672), 
    #                                      Profile(HorizontalDistance=11086.0, Elevation=1019.9999999999997, MeasuredDistance=11091.613972271394)])
    #     }
    flow_lines_dict={
        "kg202-205.Flowline_1": {"Diameter": 426.0, "Elevation": 80.0, 
                                 "GeoProfile": [{"Elevation": 1019.9999999999997, "HorizontalDistance": 0.0, "MeasuredDistance": 0.0}, 
                                                {"Elevation": 1019.9999999999997, "HorizontalDistance": 839.0, "MeasuredDistance": 839.0}, 
                                                {"Elevation": 1059.9999999999993, "HorizontalDistance": 1256.0, "MeasuredDistance": 1257.9140723346495}, 
                                                {"Elevation": 1059.9999999999993, "HorizontalDistance": 3026.9999999999977, "MeasuredDistance": 3028.9140723346495}, 
                                                {"Elevation": 1100.0, "HorizontalDistance": 3707.999999999998, "MeasuredDistance": 3711.087803872298}, 
                                                {"Elevation": 1139.9999999999998, "HorizontalDistance": 4166.999999999999, "MeasuredDistance": 4171.827426652888}, 
                                                {"Elevation": 1159.9999999999986, "HorizontalDistance": 4414.999999999998, "MeasuredDistance": 4420.632571294232}, 
                                                {"Elevation": 1159.9999999999986, "HorizontalDistance": 4828.999999999997, "MeasuredDistance": 4834.632571294232}, 
                                                {"Elevation": 1100.0, "HorizontalDistance": 5560.000000000001, "MeasuredDistance": 5568.0908182313015}, 
                                                {"Elevation": 1079.9999999999995, "HorizontalDistance": 6062.999999999998, "MeasuredDistance": 6071.488275515305}, 
                                                {"Elevation": 1079.9999999999995, "HorizontalDistance": 6861.999999999999, "MeasuredDistance": 6870.488275515305}, 
                                                {"Elevation": 1100.0, "HorizontalDistance": 8197.999999999998, "MeasuredDistance": 8206.63796772797}], 
                                "HorizontalDistance": 8198.0, "Roughness": 0.1, "Temperature": 13.1, "UcoeffuserAir": 3.302208, "WallThickness": 33.0}, 
        "kg202.Flowline_1": {"Diameter": 325.0, "Elevation": -96.0, 
                             "GeoProfile": [{"Elevation": 1116.0, "HorizontalDistance": 0.0, "MeasuredDistance": 0.0}, 
                                            {"Elevation": 1100.0, "HorizontalDistance": 357.9999999999999, "MeasuredDistance": 358.35736353534026}, 
                                            {"Elevation": 1019.9999999999997, "HorizontalDistance": 1160.9999999999998, "MeasuredDistance": 1165.3325800073208}], 
                            "HorizontalDistance": 1161.0, "Roughness": 0.1, "Temperature": 13.1, "UcoeffuserAir": 4.272857, "WallThickness": 26.0}, 
        "kg205.Flowline_1": {"Diameter": 325.0, "Elevation": 90.0, 
                             "GeoProfile": [{"Elevation": 929.9999999999999, "HorizontalDistance": 0.0, "MeasuredDistance": 0.0}, 
                                            {"Elevation": 940.0000000000001, "HorizontalDistance": 385.99999999999994, "MeasuredDistance": 386.12951195162486}, 
                                            {"Elevation": 944.9999999999991, "HorizontalDistance": 1007.9999999999994, "MeasuredDistance": 1008.1496080900052}, 
                                            {"Elevation": 940.0000000000001, "HorizontalDistance": 1880.0000000000002, "MeasuredDistance": 1880.1639428345666}, 
                                            {"Elevation": 959.9999999999994, "HorizontalDistance": 2700.999999999998, "MeasuredDistance": 2701.4075120635744}, 
                                            {"Elevation": 979.9999999999999, "HorizontalDistance": 3618.999999999997, "MeasuredDistance": 3619.6253511409905}, 
                                            {"Elevation": 999.9999999999992, "HorizontalDistance": 3878.999999999998, "MeasuredDistance": 3880.3934473490963}, 
                                            {"Elevation": 1019.9999999999997, "HorizontalDistance": 4189.0, "MeasuredDistance": 4191.037938689277}, 
                                            {"Elevation": 1039.9999999999998, "HorizontalDistance": 4515.999999999999, "MeasuredDistance": 4518.648988563972}, 
                                            {"Elevation": 1059.9999999999993, "HorizontalDistance": 5159.0, "MeasuredDistance": 5161.959955359969}, 
                                            {"Elevation": 1079.9999999999995, "HorizontalDistance": 5643.999999999998, "MeasuredDistance": 5647.3721513336595}, 
                                            {"Elevation": 1059.9999999999993, "HorizontalDistance": 6757.0, "MeasuredDistance": 6760.551831349424}, 
                                            {"Elevation": 1079.9999999999995, "HorizontalDistance": 8817.999999999996, "MeasuredDistance": 8821.64886933672}, 
                                            {"Elevation": 1079.9999999999995, "HorizontalDistance": 9143.999999999995, "MeasuredDistance": 9147.64886933672}, 
                                            {"Elevation": 1079.9999999999995, "HorizontalDistance": 10170.999999999995, "MeasuredDistance": 10174.64886933672}, 
                                            {"Elevation": 1019.9999999999997, "HorizontalDistance": 11086.0, "MeasuredDistance": 11091.613972271394}], 
            "HorizontalDistance": 11086.0, "Roughness": 0.1, "Temperature": 13.1, "UcoeffuserAir": 4.272857, "WallThickness": 26.0}
    }
    network_list=[
        {'Source': 'kg202-205.Flowline_1', 'Source Port': '', 'Destination': 'u2-202-205'}, 
        {'Source': 't-u2-202-205', 'Source Port': '', 'Destination': 'kg202-205.Flowline_1'}, 
        {'Source': 'Ck', 'Source Port': '', 'Destination': 'kg202.Flowline_1'}, 
        {'Source': 'kg205.Flowline_1', 'Source Port': '', 'Destination': 't-u2-202-205'}, 
        {'Source': 'Ck', 'Source Port': '', 'Destination': 'KG_202'}, 
        {'Source': 'KG_205', 'Source Port': '', 'Destination': 'Ckc'}, 
        {'Source': 'Ckc', 'Source Port': '', 'Destination': 'kg205.Flowline_1'}, 
        {'Source': 'kg202.Flowline_1', 'Source Port': '', 'Destination': 't-u2-202-205'}
        ]
    in_data_dict={'KG_205': {'Pressure': 169.1429, 'Temperature': 18.58113437096472, 'GasFlowRate': nan}, 
                  'KG_202': {'Pressure': 159.4642, 'Temperature': 22.833473878316795, 'GasFlowRate': nan}, 
                  'u2-202-205': {'Pressure': nan, 'GasFlowRate': 7.000000000002465}}
    conditions_dict={
        'KG_205': {'Temperature': 18.58113437096472, 'Pressure': 170.0, 'FlowRateType': 'GasFlowRate', 'GasFlowRate': nan}, 
        'u2-202-205': {'Temperature': nan, 'Pressure': nan, 'FlowRateType': 'GasFlowRate', 'GasFlowRate': 0.7000000000002481}, 
        'KG_202': {'Temperature': 22.833473878316795, 'Pressure': 150.0, 'FlowRateType': 'GasFlowRate', 'GasFlowRate': nan}
        }
    constraints_dict={'KG_202': {'GasFlowRate': 0.3000000000001063}, 'KG_205': {'GasFlowRate': 0.40000000000014174}}
    out_simulation_dict={'OutletMassFlowrateFluid': OrderedDict([('Unit', 'kg/s'), ('KG_205', 3.6886914178956753), ('KG_202', 2.76644891866537), ('u2-202-205', 6.455140336557102)]), 
                         'MaximumVelocityGas': OrderedDict([('Unit', 'm/s'), ('KG_202', 0.3364579881446892), ('u2-202-205', 0.5259175107027361), ('KG_205', 0.4849806385787681)]), 
                         'SystemOutletPressure': OrderedDict([('Unit', 'bara'), ('u2-202-205', 148.4502232017729), ('KG_202', 151.60039914333154), ('KG_205', 151.61797432694075)]), 
                         'OutletVolumeFlowrateGasStockTank': OrderedDict([('Unit', 'mmsm3/d'), ('u2-202-205', 0.6999924477544864), ('KG_205', 0.4000000000001426), ('KG_202', 0.2999924477547715)]), 
                         'SystemOutletTemperature': OrderedDict([('Unit', 'degC'), ('u2-202-205', 13.320182012157034), ('KG_202', 19.229520343329), ('KG_205', 13.374231654160042)]), 
                         'SystemInletPressure': OrderedDict([('Unit', 'bara'), ('u2-202-205', 151.61798436814473), ('KG_202', 150.0023396701707), ('KG_205', 169.99713582035892)]), 
                         'SystemTemperatureDifference': OrderedDict([('Unit', 'degC'), ('KG_202', 3.6038129900044), ('KG_205', 5.2068794569511), ('u2-202-205', 2.5634229813988725)])
                         }
    out_simulation_dict={'Unit': {'SystemOutletPressure': 'bara', 
                                  'SystemOutletTemperature': 'degC', 
                                  'OutletVolumeFlowrateGasStockTank': 'mmsm3/d', 
                                  'SystemInletPressure': 'bara', 
                                  'MaximumVelocityGas': 'm/s', 
                                  'SystemTemperatureDifference': 'degC', 
                                  'OutletMassFlowrateFluid': 'kg/s'}, 
                         'u2-202-205': {'SystemOutletPressure': 148.4502232017729, 
                                        'SystemOutletTemperature': 13.320182012157034, 
                                        'OutletVolumeFlowrateGasStockTank': 0.6999924477544864, 
                                        'SystemInletPressure': 151.61798436814473, 
                                        'MaximumVelocityGas': 0.5259175107027361, 
                                        'SystemTemperatureDifference': 2.5634229813988725, 
                                        'OutletMassFlowrateFluid': 6.455140336557102}, 
                        'KG_202': {'SystemOutletPressure': 151.60039914333154, 
                                   'SystemOutletTemperature': 19.229520343329, 
                                   'OutletVolumeFlowrateGasStockTank': 0.2999924477547715, 
                                   'SystemInletPressure': 150.0023396701707, 
                                   'MaximumVelocityGas': 0.3364579881446892, 
                                   'SystemTemperatureDifference': 3.6038129900044, 
                                   'OutletMassFlowrateFluid': 2.76644891866537}, 
                        'KG_205': {'SystemOutletPressure': 151.61797432694075, 
                                   'SystemOutletTemperature': 13.374231654160042, 
                                   'OutletVolumeFlowrateGasStockTank': 0.4000000000001426, 
                                   'SystemInletPressure': 169.99713582035892, 
                                   'MaximumVelocityGas': 0.4849806385787681, 
                                   'SystemTemperatureDifference': 5.2068794569511, 
                                   'OutletMassFlowrateFluid': 3.6886914178956753}
    }
    print(json.dumps(out_simulation_dict))


    pass
