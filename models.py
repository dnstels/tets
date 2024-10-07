from abc import ABC, abstractmethod
from dataclasses import dataclass
import json

import importlib.util
import sys
from typing import List
spec = importlib.util.spec_from_file_location("models", "core/tools.py")
tools = importlib.util.module_from_spec(spec)
sys.modules["tools"] = tools
spec.loader.exec_module(tools)

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
    Ucoeffuserair:float 
    '''Температурный коэффициент'''

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
        self.pipesim_file=''
        self.project_name=''
        self.__Networks=[]
        self.__Names={}
        self.__Data={}
        self.__InData={}
        self.__OutData={}

    @property
    def Names(self)->List:return self.__Names
    @property
    def Network(self)->List:return self.__Networks
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
        for member in [attr for attr in dir(self) 
                       if not callable(getattr(self, attr)) 
                       and (attr in self.__slots__ or attr.startswith("_AbstractProjectModel__"))]:
            out[member.replace('_AbstractProjectModel__','')]=self.get_attr(member)

        return out

    def to_json(self,is_indent=False)->str:
        return json.dumps(self.to_dict(), indent=4 if is_indent else None)

    def from_json(self,json_str:str):
        obj=json.loads(json_str)
        for key in obj.keys():
            self.__setattr__('_AbstractProjectModel__'+key,obj[key])
        # if 'Names' in obj:self.__Names=obj['Names']
        # if 'Networks' in obj: self.__Networks=obj['Networks']
        # if 'Data' in obj: self.__Data=obj['Data']
        # if 'InData' in obj: self.__InData=obj['InData']
        # if 'OutData' in obj: self.__OutData=obj['OutData']

