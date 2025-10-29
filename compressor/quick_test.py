from compressor.factory import CompressorFactory
from compressor.base import Config

c = CompressorFactory.get_compressor("method1", Config(max_bits=4))
arr = [3, 7, 15, 16, 8, 23, 1024, 4, 2, 1]
original_arr = arr.copy()
c.compress(arr)
print("orig:", original_arr)
print("packed:", arr)
c.decompress(arr)
# vérifier que l'original n'est pas modifié
assert arr == [3, 7, 15, 16, 8, 23, 1024, 4, 2, 1]