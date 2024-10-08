from abc import ABC, abstractmethod
from dataclasses import dataclass
import json

import importlib.util
import sys
sys.path.append('.')
import tools
from typing import List
# spec = importlib.util.spec_from_file_location("models", "core/tools.py")
# tools = importlib.util.module_from_spec(spec)
# sys.modules["tools"] = tools
# spec.loader.exec_module(tools)

type_property=[
    'Flowline',
    'Source',
    'Sink',
    'Junction',
    'Choke',
]

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

    GeoProfile:List
    
    # def __init__(self,
    #              HorizontalDistance,ElevationDifference,
    #              InnerDiameter,WallThickness,AmbientAirTemperature,Roughness,UCoeffUserAir,
    #              GeometryProfile,UCoeffUser):
    def __init__(self,**data):
        self.HorizontalDistance=round(data.get('HorizontalDistance',0),6)
        self.Elevation=round(data.get('Elevation',data.get('ElevationDifference',0)),6)
        self.WallThickness=round(data.get('WallThickness',0),6)
        innerDiameter=data.get('InnerDiameter',0)
        self.Diameter=data.get('Diameter',innerDiameter+2*self.WallThickness if innerDiameter >0 else 0)
        self.Temperature=round(data.get('Temperature',data.get('AmbientAirTemperature',0)),6)
        self.Roughness=round(data.get('Roughness',0),6)
        self.UcoeffuserAir=round(data.get('UCoeffUserAir',0),6)

        profile_geo=data.get('GeometryProfile',None)
        profile=profile_geo.data_frame[['MeasuredDistance',  'HorizontalDistance',  'Elevation']].to_dict(orient ='records') if profile_geo is not None else profile_geo

        self.GeoProfile=[Profile(**item) for item in profile] if profile is not None else []
        
        # print([p for p in [attr for attr in dir(self) 
        #                if not callable(getattr(self, attr)) 
        #                and not attr.startswith("_")]])
    
    # def __init__(self):
    #     self.HorizontalDistance=0
    #     self.Elevation=0
    #     self.Diameter=0
    #     self.WallThickness=0
    #     self.Temperature=0
    #     self.Roughness=0
    #     self.Ucoeffuserair=0
    def to_json(self):
        return json.dumps(self.__dict__,cls=tools.JsonClassEncoder,indent=4)



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


class AbstractProjectModel(ABC):
    # __slots__ = ('pipesim_file','project_name')
    def __init__(self) -> None:
        super().__init__()
        self.__prefix=f'_{__class__.__name__}__'
        self.pipesim_file=''
        self.project_name=''
        self.__Network=[]
        self.__Names={}
        self.__Data={}
        self.__InData={}
        self.__OutData={}

    def init(self,network,names,data,indata):
        self.__Network=network
        self.__Names=names
        self.__Data=data
        self.__InData=indata

    @property
    def Names(self)->List:return self.__Names
    @property
    def Network(self)->List:return self.__Network
    @property
    def Data(self)->List:return self.__Data
    @property
    def InData(self)->List:return self.__InData
    @property
    def OutData(self)->List:return self.__OutData

    def get_attr(self,attr_name: str):
        return self.__getattribute__(attr_name) if hasattr(self,attr_name) else None

    def to_dict(self):
        out=dict()
        skip_attr=self.__prefix+'prefix'
        for member in [attr for attr in dir(self) 
                       if not callable(getattr(self, attr)) 
                       and (not attr.startswith("_") or 
                            (attr.startswith(self.__prefix) and attr!=skip_attr))]:
            out[member.replace(self.__prefix,'')]=self.get_attr(member)

        return out

    def to_json(self,is_indent=False)->str:
        return json.dumps(self.to_dict(), indent=4 if is_indent else None)

    def from_json(self,json_str:str):
        obj=json.loads(json_str)
        for key in obj.keys():
            self.__setattr__(self.__prefix + key, obj[key])


