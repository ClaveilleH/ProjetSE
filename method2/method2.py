# -*- coding: utf-8 -*-
from random import randint
SIZE_OF_INT = 32  # Assuming a 32-bit integer representation
DEBUG = False
DEBUG = True

def affiche_bit_string(bit_string: str) -> None:
    """affiche la chaine entier par entier"""
    print("Bit string:")
    while len(bit_string) >= SIZE_OF_INT:
        print(bit_string[:SIZE_OF_INT])
        bit_string = bit_string[SIZE_OF_INT:]
    if bit_string:
        # print(bit_string.ljust(SIZE_OF_INT, '0'))  # Pad the last chunk if necessary
        print(bit_string)

def get_bin(num: int, bits: int) -> str:
    """
    Retourne la représentation binaire de num sur 'bits' bits
    ----------
    :param num: l'entier à convertir
    :param bits: le nombre de bits à utiliser pour la représentation
    :return: la chaîne binaire représentant l'entier
    """
    return f"{num:0{bits}b}"


def compresse(arr: list, max_bits: int) -> None:
    """
    Meme chose que compress_array mais compresse en place
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
    big_max_bits = max(arr).bit_length()
    bit_string += get_bin(max_bits, 6)
    bit_string += get_bin(big_max_bits, 6)
    arr_len = len(arr)
    bit_string += get_bin(arr_len, 6)
    nb_of_nb_on_int = SIZE_OF_INT // (max_bits + 1) # nombre de nombres pouvant tenir dans un entier
    to_compress= []

    first_int +=  get_bin(max_bits, 6)
    first_int +=  get_bin(big_max_bits, 6)
    first_int +=  get_bin(arr_len, 6)
    first_int = first_int.ljust(SIZE_OF_INT, '0')
    print(f"max_bits={max_bits}, big_max_bits={big_max_bits}, arr_len={arr_len}")
    print(f"nb_of_nb_on_int={nb_of_nb_on_int}")
    print(f"bit_string start: {bit_string[:6]}:{bit_string[6:12]}:{bit_string[12:18]}:{bit_string[18:]}")
    while arr :
        num = arr.pop(0)
        if num < 2**max_bits:
            # bit_string += '0' + get_bin(num, max_bits)
            txt = '0' + get_bin(num, max_bits)
            print(f"Normal: {num}, Binary: \t0{get_bin(num, max_bits)}")
            to_compress.append(txt)
        else:
            # bit_string += '1' + get_bin(nb_overflow, max_bits)
            # nb_overflow += 1
            # overflow_list.append(get_bin(num, big_max_bits))
            txt = '1' + get_bin(nb_overflow, max_bits)
            to_compress.append(txt)
            nb_overflow += 1
            overflow_list.append(get_bin(num, big_max_bits))
            
            print(f"Overflow: {num}, Binary: \t{get_bin(num, big_max_bits)}")
        print(f"Number: {num}, Binary: \t{bit_string[:6]}:{bit_string[6:12]}:{bit_string[12:18]}:{bit_string[18:]}")
    print("1>>",bit_string)
    # for num in overflow_list:
    #     bit_string += num
    print("2>>",bit_string)
    # affiche_bit_string(bit_string)
    arr.clear() # Clear the original array to fill it with compressed data
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
        print(f"Appending compressed int: {txt} -> {int(txt, 2)}")

    for num in overflow_list:
        txt = num
        # Pad the chunk to SIZE_OF_INT if necessary
        arr.append(int(txt, 2))
        # print(f"Appending overflow int: {txt} -> {int(txt, 2)}")



def affiche(arr : list) -> None:
    print("Array: ", end='')
    print(arr)
    print("Binary representation:")
    for num in arr:
        print(num[0], '-', int(num[1:], 2), sep='')


def get(arr: list, i: int) -> int:
    """
    Récupère l'élément à l'indice i du tableau compressé arr.
    ----------
    :param arr: le tableau compressé
    :param i: l'indice de l'élément à récupérer
    :return: l'élément à l'indice i
    """
    overflow_list = []                              # liste des indices des elements en overflow

    first_int = arr[0]
    bit_string = get_bin(first_int, SIZE_OF_INT)   # on recupere le premier entier
    max_bits = int(bit_string[:6], 2)               # on recupere la taille des entiers normaux
    big_max_bits = int(bit_string[6:12], 2)         # on recupere la taille des entiers en overflow
    arr_len = int(bit_string[12:18], 2)           # on recupere la taille du tableau
    
    nb_of_nb_on_int = SIZE_OF_INT // (max_bits + 1) # nombre de nombres pouvant tenir dans un entier

    bit_string = ""

    if i >= arr_len:
        print(f"Index {i} out of range (array length: {arr_len})")
        raise IndexError("Index out of range")
    
    indice_elem = i // nb_of_nb_on_int + 1 # +1 car on a enleve le premier entier
    # on calcule l'indice du i-eme element dans la chaine de bits
    indice_int = i % nb_of_nb_on_int
    print(f"Getting index {i}: elem_index={indice_elem}, int_index={indice_int} in array of length {arr_len}")

    current_int = arr[indice_elem]
    string_int = get_bin(current_int, SIZE_OF_INT)
    # split_strings = [string_int[j:j + (max_bits + 1)] for j in range(0, SIZE_OF_INT, max_bits + 1)]
    # value = split_strings[indice_int]
    from_bit = indice_int * (max_bits + 1)
    to_bit = from_bit + (max_bits + 1)
    value = string_int[from_bit:to_bit]
    if DEBUG: print(f"elem={string_int}")
    if DEBUG: print(f"value={value}")
    if value[0] == '0':
        if DEBUG: print(f"Value : 0 - {int(value[1:], 2)}")
        return int(value[1:], 2)
    



    # value[0] == '1'
    indice_overflow = int(value[1:], 2)
    overflow_start = arr_len // nb_of_nb_on_int + 2  # indice du debut de l'overflow dans le tableau arr
    return arr[overflow_start + indice_overflow]

    overflow_int_index = overflow_start + indice_overflow // (SIZE_OF_INT // big_max_bits)
    indice_overflow_bit_in_elem = (indice_overflow % (SIZE_OF_INT // big_max_bits)) * big_max_bits # indice dans l'entier
    elem_overflow = arr[overflow_int_index]
    elem_overflow = get_bin(elem_overflow, SIZE_OF_INT)
    value_overflow = elem_overflow[indice_overflow_bit_in_elem:indice_overflow_bit_in_elem + big_max_bits]
    if DEBUG: print(f"Value : 1 - {int(value[1:], 2)} --> {int(value_overflow, 2)}")
    return int(value_overflow, 2)



def decompress(arr: list) -> None:
    """
    Décompresse un tableau d'entiers compressés en un tableau d'entiers originaux 
    En place
    ----------
    :arr: le tableau d'entiers compressés
    :return: None
    """
    overflow_list = []                              # liste des indices des elements en overflow

    first_int = arr.pop(0)
    bit_string = get_bin(first_int, SIZE_OF_INT)   # on recupere le premier entier
    max_bits = int(bit_string[:6], 2)               # on recupere la taille des entiers normaux
    big_max_bits = int(bit_string[6:12], 2)         # on recupere la taille des entiers en overflow
    arr_len = int(bit_string[12:18], 2)           # on recupere la taille du tableau
    
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
                print("Reached the end of the original array length.") # on est pas censé lire plus que la taille originale
                break
    

    for i in overflow_list:
        temp[i] = arr.pop(0)
    
    arr.clear()
    arr.extend(temp)
    

def test():
    longeur = randint(2, 1000)
    longeur = 20
    arr = [randint(1, 1000) for _ in range(longeur)]
    max_bits = 4  # Example bit size for compression (4 bits for values 1-5, 12 bits for overflow values)
    # arr_compressed = compress_array(arr, max_bits)
    # arr_decompressed = decompress_array(arr_compressed)
    # assert arr == arr_decompressed, f"Test failed: {arr} != {arr_decompressed}"
    print("Test passed!")

if __name__ == "__main__":
    pass
    arr = [1, 2, 3, 1024, 4, 5, 2048]
    print("Original array:", arr)
    
    # arr = [579, 62, 418, 431, 34, 861, 119, 87, 695, 540, 740, 649, 233, 246, 521, 739, 546, 955, 565, 506]
    # arr = [579, 62, 418, 431, 34, 861, 119, 87, 695, 540, 740, 649, 233, 246, 521, 739, 128]
    # arr = [579, 62, 418, 431, 34, 861, 119, 87, 695, 540, 740, 649, 233, 246, 521, 739]
    max_bits = 3  # Example bit size for compression (3 bits for values 1-5, 11 bits for overflow values)
    max_bits = 4
    if 2**max_bits < len(arr):
        raise ValueError("max_bits is too small to represent all overflow indices.")
    # aa = compress_array(arr, max_bits)
    # aa = compress_array(arr, max_bits)
    aa = arr.copy()
    compresse(aa, max_bits)
    print("Compressed array:", aa)
    print("=========")
    for i in range(len(arr)):
        print(f"Index {i}: =====================")
        x = get(aa, i)
        if x != arr[i]:
            print(f"Error at index {i}: expected {arr[i]}, got {x}")
            exit(1)
    print("=========")
    print("compressed array:", aa)
    # aa = decompress_array(aa)

    decompress(aa)
    print("decompressed array:", aa)
    # affiche(arr)
    # compressed = compress_array(arr)
    # print("Compressed:")
    # affiche(compressed)
    # decompressed = decompress_array(compressed)
    # print("Decompressed:")
    # affiche(decompressed)
    print("=========")
    print(get_bin(1024, 12))
    if arr == aa:
        print("Test passed!")
    else:
        print("Test failed!")
    # test()




"""

def affiche_compressed(arr : list) -> None:
    print("Array: ", end='')
    print(arr)
    bit_string = get_bin(arr[0], SIZE_OF_INT) 
    max_bits = int(bit_string[:6], 2)
    big_max_bits = int(bit_string[6:12], 2)
    bit_string = bit_string[12:]
    arr = arr[1:]
    print(f"max_bits={max_bits}, big_max_bits={big_max_bits}")
    while len(bit_string) >= max_bits + 1 or arr:
        if len(bit_string) < max_bits + 1:
            bit_string += get_bin(arr[0], SIZE_OF_INT)
            arr = arr[1:]
        num = bit_string[:max_bits + 1]
        print(num[0], '-', int(num[1:], 2), sep='')
        bit_string = bit_string[max_bits + 1:]
    
    # get(arr, 0)
        

00
01
10
11

"""