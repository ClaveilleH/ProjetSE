from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
# from utils import get_bin

@dataclass
class Config:
    debug: bool = False
    header_bits: int = 18
    max_bits: int = 4



class CompressorBase(ABC):

    def __init__(self, config: Optional[Config] = None) -> None:
        if config is None:  
            config = Config()
        self.config = config

    @abstractmethod
    def compress(self, data: list[int]) -> list[int]:
        raise NotImplementedError

    @abstractmethod
    def decompress(self, compressed_data: list[int]) -> list[int]:
        raise NotImplementedError
    
    @abstractmethod
    def get(self, compressed_data: list[int], index: int) -> int:
        raise NotImplementedError

    