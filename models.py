from abc import ABC, abstractmethod
import json

import importlib.util
import sys
spec = importlib.util.spec_from_file_location("models", "core/tools.py")
tools = importlib.util.module_from_spec(spec)
sys.modules["tools"] = tools
spec.loader.exec_module(tools)


class AbstractProjectModel(ABC):

    def __init__(self) -> None:
        super().__init__()
        self.__flowlines=[]
        self.__sources=[]
        self.__sinks=[]
        self.__junctions=[]
        self.__chokes=[]
        self.__dates=[]

    @abstractmethod
    def load(self, filename: str):
        raise NotImplementedError
    
    @abstractmethod
    def save(self, filename: str):
        raise NotImplementedError
    
    @property
    def flowlines(self):
        return self.__flowlines
    @property
    def sources(self):
        return self.__sources
    @property
    def sinks(self):
        return self.__sinks
    @property
    def junctions(self):
        return self.__junctions
    @property
    def chokes(self):
        return self.__chokes
    
    def to_json(self,is_indent=False)->str:
        out={}
        out['flowlines']=self.flowlines
        out['sources']=self.sources
        out['sinks']=self.sinks
        out['junctions']=self.junctions
        out['chokes']=self.chokes
        out['dates']=self.__dates

        return json.dumps(out,cls=tools.JsonClassEncoder, indent=4 if is_indent else None)
    
    def from_json(self,json_str:str)->None:
        model = json.loads(json_str)
        self.__flowlines=model['flowlines']
        self.__sources=model['sources']
        self.__sinks=model['sinks']
        self.__junctions=model['junctions']
        self.__chokes=model['chokes']
        self.__dates=model['dates']
        
