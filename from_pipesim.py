from sixgill.pipesim import Model
from sixgill.definitions import Units,Parameters,ModelComponents,ProfileVariables,SystemVariables
import pandas as pd
import sys
sys.path.append('.')
from  core.models import AbstractProjectModel,type_property,Flowline

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
        system_variables=system_variables)
    model.tasks.networksimulation.run(options={"GenerateOutputFile":False,"Restart":False,"Parallelism":4})
    results = model.tasks.networksimulation.get_results(simulation_id)
    return results


def get_conditions(model:Model):
    return pd.DataFrame.from_dict(model.tasks.networksimulation.get_conditions()).T[[
        'Temperature', 'Pressure', 'FlowRateType', 'GasFlowRate']].T.to_dict()
def get_constraints(model:Model):
    return model.tasks.networksimulation.get_constraints()

if __name__=='__main__':
    filename='D:\\repos\\Pipesim_\\test-test-test.pips'
    flowline=Flowline
    # for member in [attr for attr in dir(flowline) 
    #                    if not callable(getattr(flowline, attr)) 
    #                    and (not attr.startswith("_"))]:
    #     print(member)
    
    model=Model.open(filename=filename, units=Units.METRIC)
    # names=get_names(model)
    # flow_lines_dict=get_data_flowlines(model)
    # print(get_network(model))
    in_data=get_indata(model)
    conditions=get_conditions(model)
    constraints=get_constraints(model)
    simulation=get_simulation(model)
    model.close()
    print(pd.DataFrame.from_dict(in_data))
    print('-'*50)
    print(pd.DataFrame.from_dict(conditions))
    print('-'*50)
    print(pd.DataFrame.from_dict(constraints))
    print('-'*50)
    print(pd.DataFrame.from_dict(simulation))
    # print('-'*50)
    # for k,v in names.items():
    #     print(k,v)
    # print('-'*50)
    # for k,v in flow_lines_dict.items():
    #     print(k,v.to_json())
    
    pass
