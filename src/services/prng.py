from __future__ import annotations
from dataclasses import dataclass
from typing import List, Sequence, TypeVar
import numpy as np

T = TypeVar("T") #noe dadeye dakhel list har chi bod hamon ro bargardon

@dataclass #khodesh __init__ ro misaze
class PRNG:
    seed : int
    def __post_init__(self) -> None : 
        self.rng = np.random.Generator(np.random.PCG64(self.seed))
    