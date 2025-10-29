from typing import Optional
from .base import CompressorBase, Config

class CompressorFactory:
    @staticmethod
    def get_compressor(method: str, config: Optional[Config] = None) -> CompressorBase:
        if method == "method1":
            from .method1 import Method1Compressor
            return Method1Compressor(config)
        elif method == "method2":
            from .method2 import Method2Compressor
            return Method2Compressor(config)
        else:
            raise ValueError(f"Unknown compression method: {method}")
