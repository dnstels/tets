
# import os
# print(os.getcwd())
import json
import sys
sys.path.append('.')
from  core.models import ProjectDataModel,Names


with open('./tests/proj_test.json', 'r') as json_file:
    data_json = json.load(json_file)
    proj_model= ProjectDataModel(**data_json)

def test_init_correct_lenData_of_field():
    sut=proj_model

    assert len(sut.FlowlineData)>0
    assert len(sut.Names)>0
    assert len(sut.Network)>0
    assert len(sut.InData)>0
    assert len(sut.OutData)==1

def test_get_typesofNames():
    sut=Names.get_types()
    assert type(sut) is list 
    assert len(sut) > 0 



if __name__ == '__main__':
    # for k,v in data_json.items():
    #     print(k,type(v))
    # print(len(proj_model.Network))
    # for n in proj_model.Network:
    #     print(n.__dict__)
    # print(proj_model.to_json(True))

    print(proj_model.to_json(True))

    pass
