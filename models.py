from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
from typing import List

import importlib.util
import sys
sys.path.append('.')
try:
    import tools
except ImportError:
    spec = importlib.util.spec_from_file_location("models", "core/tools.py")
    tools = importlib.util.module_from_spec(spec)
    sys.modules["tools"] = tools
    spec.loader.exec_module(tools)

network_property=['Source','Destination']
# profile=['HorizontalDistance','Elevation']
flowline_property=[]

@dataclass
class Profile:
    HorizontalDistance: float
    '''Горизонтальное расстояние'''
    Elevation: float
    '''Высота'''

    MeasuredDistance:float

@dataclass
class Flowline:
    HorizontalDistance:float
    '''Длина'''
    Elevation: float 
    '''Возвышение(высота)'''
    Diameter: float 
    '''Диаметр(внешний)'''
    WallThickness: float 
    '''Толщина стенки'''
    Temperature: float 
    '''Температура'''
    Roughness:float 
    '''Шероховатость'''
    UcoeffuserAir:float 
    '''Температурный коэффициент'''

    GeoProfile:List[Profile]

    def __init__(self,**data):
        self.HorizontalDistance=round(data.get('HorizontalDistance',0),6)
        self.Elevation=round(data.get('Elevation',data.get('ElevationDifference',0)),6)
        self.WallThickness=round(data.get('WallThickness',0),6)
        innerDiameter=data.get('InnerDiameter',0)
        self.Diameter=data.get('Diameter',innerDiameter+2*self.WallThickness if innerDiameter >0 else 0)
        self.Temperature=round(data.get('Temperature',data.get('AmbientAirTemperature',0)),6)
        self.Roughness=round(data.get('Roughness',0),6)
        self.UcoeffuserAir=round(data.get('UCoeffUserAir',0),6)

        profile = data.get('GeoProfile',None)
        if profile is None:
            profile_geo= data.get('GeometryProfile',None)
            profile=profile_geo.data_frame[['MeasuredDistance',  'HorizontalDistance',  'Elevation']].to_dict(orient ='records') if profile_geo is not None else profile_geo
        else:
            if isinstance(next(iter(profile if hasattr(profile, '__iter__') else []), None), Profile):
                self.GeoProfile=profile
        
        if not hasattr(self,'GeoProfile') :
            self.GeoProfile=[Profile(**item) for item in profile] if profile is not None else []

    def to_json(self):
        return json.dumps(self.__dict__,cls=tools.JsonClassEncoder,indent=4)

class Names():
    Flowline:[]
    '''Трубопроводы'''
    Source:[]
    '''Источники'''
    Sink:[]
    '''Стоки'''
    Junction:[]
    '''Узлы'''
    Choke:[]
    '''Штуцеры'''

    def __init__(self,**data) -> None:
        self.Flowline=data.get('Flowline',[])
        self.Source=data.get('Source',[])
        self.Sink=data.get('Sink',[])
        self.Junction=data.get('Junction',[])
        self.Choke=data.get('Choke',[])
    @staticmethod
    def get_types():
        return list(Names.__annotations__)

@dataclass
class Source:
    Pressure:float
    '''Давление'''
    Temperature:float
    '''Температура'''
    GasFlowRate:float
    '''Расход газа'''

@dataclass
class Sink:
    Pressure:float
    '''Давление'''
    GasFlowRate:float
    '''Расход газа'''

@dataclass
class Branch():
    __slots__ = ('Source','Destination')
    Source:str
    Destination:str
    def __init__(self,**data):
        self.Source=data.get('Source',None)
        self.Destination=data.get('Destination',None)

class ProjectDataModel():
    # __slots__ = ('pipesim_file','project_name')
    def __init__(self,**data) -> None:
        # self.__prefix=f'_{__class__.__name__}__'
        self.pipesim_file=''
        self.project_name=''
        self.__Network=[Branch(**b) for b in data.get('Network',[])]
        self.__Names=data.get('Names',{})
        self.__FlowlineData={k:Flowline(**v) for k,v in data.get('FlowlineData',{}).items()}
        self.__InData=data.get('InData',{})
        self.__OutData=data.get('OutData',{})
    
    @property
    def Names(self):return self.__Names
    
    @property
    def Network(self):return self.__Network
    @Network.setter  
    def Network(self,network:Network): self.__Network=network
    
    @property
    def FlowlineData(self):return self.__FlowlineData
    @Network.setter 
    def FlowlineData(self,flowlines:dict): self.__FlowlineData=flowlines#{k:Flowline(**v) for k,v in flowlines.items()}

    @property
    def InData(self):return self.__InData
    @property
    def OutData(self):return self.__OutData

    def get_attr(self,attr_name: str):
        return self.__getattribute__(attr_name) if hasattr(self,attr_name) else None

    def to_dict(self):
        return {i_attr:self.__getattribute__(i_attr) for i_attr in [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("_")]}

    def to_json(self,is_indent=False)->str:
        # return json.dumps(self.to_dict(), indent=4 if is_indent else None)
        return json.dumps(self,cls=tools.JsonClassEncoder, indent=4 if is_indent else None)

    # def from_json(self,json_str:str):
    #     obj=json.loads(json_str)
    #     for key in obj.keys():
    #         self.__setattr__(self.__prefix + key, obj[key])


