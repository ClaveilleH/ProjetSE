from typing import List, Optional
from .base import CompressorBase, Config
import importlib
from .utils import get_bin, SIZE_OF_INT

# _method1 = importlib.import_module("Method1")


class Method2Compressor(CompressorBase):
    def __init__(self, config: Optional[Config] = None) -> None:
        super().__init__(config)

    def compress(self, arr: List[int]) -> None:
        bit_string = ""
        nb_overflow = 0
        overflow_list = []
        big_max_bits = max(arr).bit_length()
        bit_string += get_bin(self.config.max_bits, 6)
        bit_string += get_bin(big_max_bits, 6)
        arr_len = len(arr)
        bit_string += get_bin(arr_len, 6)
        # print(f"max_bits={self.config.max_bits}, big_max_bits={big_max_bits}, arr_len={arr_len}")
        while arr:
            num = arr.pop(0)
            if num < 2 ** self.config.max_bits: # nombre normal
                bit_string += '0' + get_bin(num, self.config.max_bits)
            else: # overflow
                bit_string += '1' + get_bin(nb_overflow, self.config.max_bits)
                nb_overflow += 1
                overflow_list.append(get_bin(num, big_max_bits))

        # print("bitstring:")
        # for i in range(18, len(bit_string), self.config.max_bits + 1):
        #     print(bit_string[i:i+self.config.max_bits + 1], end=' ')
        # print()
        # print("overflow list:", overflow_list)

        for num in overflow_list:
            bit_string += num
        arr.clear()
        while len(bit_string) >= SIZE_OF_INT:
            arr.append(int(bit_string[:SIZE_OF_INT], 2))
            bit_string = bit_string[SIZE_OF_INT:]
        if bit_string:
            arr.append(int(bit_string.ljust(SIZE_OF_INT, '0'), 2))  # Pad the last chunk if necessary

    def decompress(self, arr: List[int]) -> None:
        """
        Décompresse un tableau d'entiers compressés en un tableau d'entiers originaux 
        En place
        ----------
        :arr: le tableau d'entiers compressés
        :return: None
        """
        overflow_list = []                              # liste des indices des elements en overflow
        bit_string = get_bin(arr.pop(0), SIZE_OF_INT)   # on recupere le premier entier
        max_bits = int(bit_string[:6], 2)               # on recupere la taille des entiers normaux
        big_max_bits = int(bit_string[6:12], 2)         # on recupere la taille des entiers en overflow
        nb_of_int = int(bit_string[12:18], 2)           # on recupere la taille du tableau
        bit_string = bit_string[18:]                    # Remove the first 18 bits used for metadata
        arr_len = len(arr)
        cpt = 0
        while (arr_len > 0 or len(bit_string) >= max_bits + 1) and cpt < nb_of_int:
            if len(bit_string) < max_bits + 1:
                bit_string += get_bin(arr.pop(0), SIZE_OF_INT)
                arr_len -= 1
            current_bits = bit_string[:max_bits + 1]
            bit_string = bit_string[max_bits + 1:]
            if current_bits[0] == '0':
                arr.append(int(current_bits[1:], 2))
                # print(f"0 - {int(current_bits[1:], 2)}")
            else:
                # print(f"1 - {int(current_bits[1:], 2)} -->")
                indice_overflow = int(current_bits[1:], 2)
                arr.append(indice_overflow)         # il faut mettre un nombre quelconque
                overflow_list.append(cpt)           # stock l'indice a remplacer plus tard
            # print(arr)
            cpt += 1

        while arr_len > 0:
            bit_string += get_bin(arr.pop(0), SIZE_OF_INT)
            arr_len -= 1

        for i in overflow_list:
            if len(bit_string) < big_max_bits:
                raise ValueError("Not enough bits to read overflow value")
            current_bits = bit_string[:big_max_bits]
            bit_string = bit_string[big_max_bits:]
            arr[i] = int(current_bits, 2)

    def get(self, compressed_data: List[int], index: int) -> int:
        """
        Récupère l'élément à l'indice i du tableau compressé arr.
        ----------
        :param arr: le tableau compressé
        :param i: l'indice de l'élément à récupérer
        :return: l'élément à l'indice i
        """
        bit_string = get_bin(compressed_data[0], SIZE_OF_INT)   # on recupere le premier entier
        max_bits = int(bit_string[:6], 2)           # on recupere la taille des entiers normaux
        big_max_bits = int(bit_string[6:12], 2)     # on recupere la taille des entiers en overflow 
        arr_len = int(bit_string[12:18], 2)         # on recupere la taille du tableau
        indice_elem = index * (max_bits + 1) + 18       # on calcule l'indice du i-eme element dans la chaine de bits
        
        if arr_len <= index:
            raise IndexError("Index out of range")
        
        indice_liste = indice_elem // SIZE_OF_INT   # indice de l'entier
        indice_bit = indice_elem % SIZE_OF_INT      # indice dans l'entier
        if indice_bit + max_bits + 1 > SIZE_OF_INT:
            # le bit est splitté entre deux entiers
            next_elem = compressed_data[indice_liste + 1]
            next_elem = get_bin(next_elem, SIZE_OF_INT)
            elem = compressed_data[indice_liste]
            elem = get_bin(elem, SIZE_OF_INT)
            elem += next_elem
        else:
            elem = compressed_data[indice_liste]
            elem = get_bin(elem, SIZE_OF_INT)
        
        value = elem[indice_bit:indice_bit + max_bits + 1]
        # if self.config.debug: print(f"elem={elem}")
        # if self.config.debug: print(f"value={value}")
        if value[0] == '0':
            # if self.config.debug: print(f"Value : 0 - {int(value[1:], 2)}")
            return int(value[1:], 2)
        
        # value[0] == '1'
        indice_overflow = int(value[1:], 2)
        overflow_start = arr_len * (max_bits + 1) + 18  # 18 pour les 3x6 bits du début
        indice_overflow_bit = overflow_start + indice_overflow * big_max_bits # indice du debut de l'overflow dans la chaine de bits
        elem_overflow = compressed_data[indice_overflow_bit // SIZE_OF_INT] 
        elem_overflow = get_bin(elem_overflow, SIZE_OF_INT)
        indice_overflow_bit_in_elem = indice_overflow_bit % SIZE_OF_INT # indice dans l'entier

        if indice_overflow_bit_in_elem + big_max_bits > SIZE_OF_INT:
            # le nombre est splitté entre deux entiers
            next_elem_overflow = compressed_data[indice_overflow_bit // SIZE_OF_INT + 1]
            next_elem_overflow = get_bin(next_elem_overflow, SIZE_OF_INT)
            elem_overflow += next_elem_overflow
        
        value_overflow = elem_overflow[indice_overflow_bit_in_elem:indice_overflow_bit_in_elem + big_max_bits]
        # if self.config.debug: print(f"Value : 1 - {int(value[1:], 2)} --> {int(value_overflow, 2)}")
            
        return int(value_overflow, 2)
    
if __name__ == "__main__":
    compressor = Method2Compressor(Config(debug=True, max_bits=4))
    data = [3, 7, 15, 16, 8, 23, 1024, 4, 2, 1]
    original_data = data.copy()
    print("Original data:", data)
    compressor.compress(data)
    print("Compressed data:", data)
    for i in range(10):
        value = compressor.get(data, i)
        print(f"Value at index {i}: {value}")
        if value != original_data[i]:
            print(f"Error at index {i}: expected {original_data[i]}, got {value}")
            exit(1)
    compressor.decompress(data)
    print("Decompressed data:", data)
    if data != original_data:
        print("Error: decompressed data does not match original data")
        exit(1)
    print("Success: decompressed data matches original data")


# python3 -m compressor.method1