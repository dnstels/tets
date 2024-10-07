import importlib.util
import json
import ast
from memory_profiler import profile

import sys
spec = importlib.util.spec_from_file_location("models", "core/models.py")
models = importlib.util.module_from_spec(spec)
sys.modules["models"] = models
spec.loader.exec_module(models)
spec1 = importlib.util.spec_from_file_location("models", "core/tools.py")
tools = importlib.util.module_from_spec(spec1)
sys.modules["tools"] = tools
spec1.loader.exec_module(tools)



class FakeProjModel(models.AbstractProjectModel):
    def __init__(self) -> None:
        super().__init__()
    
    def init(self):
        # self._AbstractProjectModel__flowlines=[
        #     'kg202.Flowline_1',
        #     'kg202-205.Flowline_1',
        #     'kg205.Flowline_1'
        # ]
        # self._AbstractProjectModel__sources=['KG_202','KG_205']
        # self._AbstractProjectModel__sinks=['u2-202-205']
        # self._AbstractProjectModel__junctions=['t-u2-202-205']
        # self._AbstractProjectModel__chokes=['Ck','Ckc']
        d_names={}
        d_names['Flowline']=[
            'kg202.Flowline_1',
            'kg202-205.Flowline_1',
            'kg205.Flowline_1'
        ]
        d_names['Source']=['KG_202','KG_205']
        d_names['Sink']=['u2-202-205']
        d_names['Junction']=['t-u2-202-205']
        d_names['Choke']=['Ck','Ckc']
    
        self._AbstractProjectModel__Name=d_names
    
    def load(self):
        pass
    
    def save(self, filename: str):
        pass
    
json_Names='{"Flowline": ["kg202.Flowline_1", "kg202-205.Flowline_1", "kg205.Flowline_1"], "Source": ["KG_202", "KG_205"], "Sink": ["u2-202-205"], "Junction": ["t-u2-202-205"], "Choke": ["Ck", "Ckc"]}'
json_string=f'{{"Names":{json_Names}}}'
json_network="[{'Source': 'kg202-205.Flowline_1', 'Destination': 'u2-202-205'}, {'Source': 'Ck', 'Destination': 'kg202.Flowline_1'}, {'Source': 't-u2-202-205', 'Destination': 'kg202-205.Flowline_1'}, {'Source': 'KG_205', 'Destination': 'Ckc'}, {'Source': 'kg205.Flowline_1', 'Destination': 't-u2-202-205'}, {'Source': 'Ckc', 'Destination': 'kg205.Flowline_1'}, {'Source': 'Ck', 'Destination': 'KG_202'}, {'Source': 'kg202.Flowline_1', 'Destination': 't-u2-202-205'}]"

def test_is_current_count_flows():
    sut=FakeProjModel()
    sut.init()
    assert len(sut.Flowlines)==3

def test_is_found_dates_to_json_str():
    sut=FakeProjModel()
    sut.init()
    assert sut.to_json().find('"Flowlines": [') > -1

def test_is_currect_from_json():
    sut=FakeProjModel()
    assert len(sut.Names['Flowline'])==0
    sut.from_json(json_string)
    assert len(sut.Names['Flowline'])==3
    assert 'kg202-205.Flowline_1' in sut.Names['Flowline']

def test_network():
    # sut=FakeProjModel()
    network=ast.literal_eval(json_network)
    print(type(network))
    assert len(network) > 0
    # assert len(sut.network) > 0
    pass

# class T():
#     # __slots__ =['__private','public'] 
#     def __init__(self) -> None:
#         self.__private="Private"
#         self.public="Public"

# @profile
# def t():
#     a=T()
#     return a

if __name__=='__main__':
    sut=FakeProjModel()
    o=sut.from_json(json_string)
    print(sut.to_json(True))
    print(sut.Names)
    # for k,v in sut.to_dict().items():
    #     print(k,v)
    # # for f in sut:
    # members = [attr for attr in dir(sut) if not callable(getattr(sut, attr)) and not attr.startswith("_")]
    # print(members)
    # print(sut.get_attr('Flowlines'))
    # print(sut.get_attr('Flowlines_ttt'))
    # # print(sut.to_json(True))

    # # network=ast.literal_eval(json_network)
    
    # # for n in network:
    # #     print(n['Source'])
    # tt=t()
    # tt.tt="123"
    # print(json.dumps(tt,cls=tools.JsonClassEncoder,skipkeys=True))

    # print(json_string)
    # obj=json.loads(json_string)
    # for k,v in obj.items():
    #     print(k,v)

    pass
    
