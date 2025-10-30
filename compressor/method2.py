from typing import List, Optional
from .base import CompressorBase, Config
from .utils import get_bin, SIZE_OF_INT
import importlib

# _method1 = importlib.import_module("Method1")


class Method2Compressor(CompressorBase):
    def __init__(self, config: Optional[Config] = None) -> None:
        super().__init__(config)

    def compress(self, arr: List[int]) -> None:
        """
        Cette fois, les nombres ne peuvent pas chevaucher plusieurs entiers.
        ----------
        :param arr: le tableau d'entiers à compresser
        :param max_bits: le nombre de bits à utiliser pour les entiers normaux
        :return: None
        1 bit pour indiquer si c'est un overflow ou pas + max_bits pour la valeur ou l'indice d'overflow
        6 bits pour indiquer le max_bits
        6 bits pour indiquer le big_max_bits
        6 bits pour indiquer la taille du tableau
        6 + 6 + 6 = 18 bits au début
        1 + max_bits bits par entier
        big_max_bits bits par entier en overflow
        """
        first_int = ""
        bit_string = ""
        nb_overflow = 0
        overflow_list = []
        arr_len = len(arr)
        # bit_string += get_bin(arr_len, SIZE_OF_INT)
        big_max_bits = max(arr).bit_length()
        bit_string += get_bin(self.config.max_bits, 6)
        bit_string += get_bin(big_max_bits, 6)
        nb_of_nb_on_int = SIZE_OF_INT // (self.config.max_bits + 1) # nombre de nombres pouvant tenir dans un entier
        to_compress= []

        first_int +=  get_bin(self.config.max_bits, 6)
        first_int +=  get_bin(big_max_bits, 6)
        first_int +=  get_bin(arr_len, 6)
        first_int = first_int.ljust(SIZE_OF_INT, '0')
        # print(f"max_bits={self.config.max_bits}, big_max_bits={big_max_bits}, arr_len={arr_len}")
        # print(f"nb_of_nb_on_int={nb_of_nb_on_int}")
        # print(f"bit_string start: {bit_string[:6]}:{bit_string[6:12]}:{bit_string[12:18]}:{bit_string[18:]}")
        while arr :
            num = arr.pop(0)
            if num < 2**self.config.max_bits:
                # bit_string += '0' + get_bin(num, max_bits)
                txt = '0' + get_bin(num, self.config.max_bits)
                # print(f"Normal: {num}, Binary: \t0{get_bin(num, self.config.max_bits)}")
                to_compress.append(txt)
            else:
                # bit_string += '1' + get_bin(nb_overflow, max_bits)
                # nb_overflow += 1
                # overflow_list.append(get_bin(num, big_max_bits))
                txt = '1' + get_bin(nb_overflow, self.config.max_bits)
                to_compress.append(txt)
                nb_overflow += 1
                overflow_list.append(get_bin(num, big_max_bits))
                
            #     print(f"Overflow: {num}, Binary: \t{get_bin(num, big_max_bits)}")
            # print(f"Number: {num}, Binary: \t{bit_string[:6]}:{bit_string[6:12]}:{bit_string[12:18]}:{bit_string[18:]}")
        # print("1>>",bit_string)
        # for num in overflow_list:
        #     bit_string += num
        # print("2>>",bit_string)
        # affiche_bit_string(bit_string)
        arr.clear() # Clear the original array to fill it with compressed data
        arr.append(int(arr_len))                       # on ajoute la taille du tableau en premier
        arr.append(int(first_int, 2))
        while to_compress:
            if len(to_compress) >= nb_of_nb_on_int:
                chunk = to_compress[:nb_of_nb_on_int]
                to_compress = to_compress[nb_of_nb_on_int:]
            else:
                chunk = to_compress
                to_compress = []
            txt = ""
            for num in chunk:
                txt += num
            # Pad the chunk to SIZE_OF_INT if necessary
            txt = txt.ljust(SIZE_OF_INT, '0')
            arr.append(int(txt, 2))
            # print(f"Appending compressed int: {txt} -> {int(txt, 2)}")

        for num in overflow_list:
            txt = num
            # Pad the chunk to SIZE_OF_INT if necessary
            arr.append(int(txt, 2))
            # print(f"Appending overflow int: {txt} -> {int(txt, 2)}")

    def decompress(self, arr: List[int]) -> None:
        """
        Décompresse un tableau d'entiers compressés en un tableau d'entiers originaux 
        En place
        ----------
        :arr: le tableau d'entiers compressés
        :return: None
        """
        overflow_list = []                              # liste des indices des elements en overflow

        arr_len = arr.pop(0)
        first_int = arr.pop(0)
        bit_string = get_bin(first_int, SIZE_OF_INT)   # on recupere le premier entier
        max_bits = int(bit_string[:6], 2)               # on recupere la taille des entiers normaux
        big_max_bits = int(bit_string[6:12], 2)         # on recupere la taille des entiers en overflow
        # arr_len = int(bit_string[12:18], 2)           # on recupere la taille du tableau
        
        nb_of_nb_on_int = SIZE_OF_INT // (max_bits + 1) # nombre de nombres pouvant tenir dans un entier

        bit_string = ""


        temp = [0] * arr_len  # tableau temporaire pour stocker les valeurs décompressées
        cpt = 0
        while len(arr) > 0 and cpt < arr_len:
            current_int = arr.pop(0)
            string_int = get_bin(current_int, SIZE_OF_INT)
            split_strings = [string_int[i:i + (max_bits + 1)] for i in range(0, SIZE_OF_INT, max_bits + 1)]
            for s in split_strings:
                if len(s) < max_bits + 1:
                    break
                if s[0] == '0':
                    bit_string += s
                    temp[cpt] = int(s[1:], 2)
                else:
                    indice_overflow = int(s[1:], 2)
                    temp[cpt] = indice_overflow  # Placeholder, will be replaced later
                    bit_string += s
                    overflow_list.append(cpt)           # stock l'indice a remplacer plus tard
                cpt += 1
                if cpt >= arr_len:
                    # print("Reached the end of the original array length.") # on est pas censé lire plus que la taille originale
                    break
        

        for i in overflow_list:
            temp[i] = arr.pop(0)
        
        arr.clear()
        arr.extend(temp)

    def get(self, arr: List[int], index: int) -> int:
        """
        Récupère l'élément à l'indice i du tableau compressé arr.
        ----------
        :param arr: le tableau compressé
        :param i: l'indice de l'élément à récupérer
        :return: l'élément à l'indice i
        """
        overflow_list = []                              # liste des indices des elements en overflow

        arr_len = arr[0]
        first_int = arr[1]
        bit_string = get_bin(first_int, SIZE_OF_INT)   # on recupere le premier entier
        max_bits = int(bit_string[:6], 2)               # on recupere la taille des entiers normaux
        big_max_bits = int(bit_string[6:12], 2)         # on recupere la taille des entiers en overflow
        # arr_len = int(bit_string[12:18], 2)           # on recupere la taille du tableau
        
        nb_of_nb_on_int = SIZE_OF_INT // (max_bits + 1) # nombre de nombres pouvant tenir dans un entier

        bit_string = ""

        if index >= arr_len:
            print(f"Index {index} out of range (array length: {arr_len})")
            raise IndexError("Index out of range")

        indice_elem = index // nb_of_nb_on_int + 2 # +2 car on a enleve les 2 premier entier
        # on calcule l'indice du i-eme element dans la chaine de bits
        indice_int = index % nb_of_nb_on_int
        # print(f"Getting index {index}: elem_index={indice_elem}, int_index={indice_int} in array of length {arr_len}")

        current_int = arr[indice_elem]
        string_int = get_bin(current_int, SIZE_OF_INT)
        from_bit = indice_int * (max_bits + 1)
        to_bit = from_bit + (max_bits + 1)
        value = string_int[from_bit:to_bit]
        if value[0] == '0':
            return int(value[1:], 2)
        



        # value[0] == '1'
        indice_overflow = int(value[1:], 2)
        overflow_start = arr_len // nb_of_nb_on_int + 3  # indice du debut de l'overflow dans le tableau arr
        return arr[overflow_start + indice_overflow]
    


if __name__ == "__main__":
    compressor = Method1Compressor(Config(debug=True, max_bits=4))
    data = [3, 7, 15, 16, 8, 23, 1024, 4, 2, 1]
    original_data = data.copy()
    print("Original data:", data)
    compressor.compress(data)
    print("Compressed data:", data)
    
    for i in range(len(original_data)):
        value = compressor.get(data, i)
        print(f"Get index {i}: {value}")
        if value != original_data[i]:
            print(f"Error at index {i}: expected {original_data[i]}, got {value}")
            exit(1)
    
    compressor.decompress(data)
    print("Decompressed data:", data)
    if data != original_data:
        print("Error: decompressed data does not match original data")
        exit(1)
    print("Success: decompressed data matches original data")