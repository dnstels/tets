import importlib.util
import json
import sys
spec = importlib.util.spec_from_file_location("models", "core\models.py")
models = importlib.util.module_from_spec(spec)
sys.modules["models"] = models
spec.loader.exec_module(models)



class FakeProjModel(models.AbstractProjectModel):
    def __init__(self) -> None:
        super().__init__()
    
    def init(self):
        self._AbstractProjectModel__flowlines=[
            'kg202.Flowline_1',
            'kg202-205.Flowline_1',
            'kg205.Flowline_1'
        ]
        self._AbstractProjectModel__sources=['KG_202','KG_205']
        self._AbstractProjectModel__sinks=['u2-202-205']
        self._AbstractProjectModel__junctions=['t-u2-202-205']
        self._AbstractProjectModel__chokes=['Ck','Ckc']
    
    def load(self):
        pass
    
    def save(self, filename: str):
        pass
    
json_string='{"flowlines": ["kg202.Flowline_1", "kg202-205.Flowline_1", "kg205.Flowline_1"], "sources": ["KG_202", "KG_205"], "sinks": ["u2-202-205"], "junctions": ["t-u2-202-205"], "chokes": ["Ck", "Ckc"], "dates": []}'

def test_is_current_count_flows():
    sut=FakeProjModel()
    sut.init()
    assert len(sut.flowlines)==3

def test_is_currect_to_json():
    sut=FakeProjModel()
    sut.init()
    assert sut.to_json()==json_string

def test_is_currect_from_json():
    sut=FakeProjModel()
    assert len(sut.flowlines)==0
    sut.from_json(json_string)
    assert len(sut.flowlines)==3

