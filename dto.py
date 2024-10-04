from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Source():
    Pressure:float
    Temperature:float
    GasFlowRate:float

@dataclass(frozen=True)
class GeometryProfile():
    HorizontalDistance:float
    MeasuredDistance:float
    Elevation:float
    

@dataclass(frozen=True)
class GeoThermalProfile():
    HorizontalDistance:float
    Temperature:float
    UCoeff:float

@dataclass(frozen=True)
class FlowLine():
    GeometryProfile:List[GeometryProfile]
    # FlowlineGeothermalProfile:List[GeoThermalProfile]
    HorizontalDistance:float
    ElevationDifference:float
    InnerDiameter:float
    Roughness:float
    Temperature:float
    UCoeffUserAir:float
