# -*- coding: utf-8 -*-
from random import randint
SIZE_OF_INT = 32  # Assuming a 32-bit integer representation
DEBUG = False

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


def compress_array(arr: list, max_bits: int) -> list:
    """
    Compresse un tableau d'entiers en un tableau d'entiers compressés avec gestion des débordements.
    ----------
    :param arr: le tableau d'entiers à compresser
    :param max_bits: le nombre de bits à utiliser pour les entiers normaux
    :return: le tableau d'entiers compressés
    1 bit pour indiquer si c'est un overflow ou pas + max_bits pour la valeur ou l'indice d'overflow
    6 bits pour indiquer le max_bits
    6 bits pour indiquer le big_max_bits
    6 bits pour indiquer la taille du tableau
    6 + 6 + 6 = 18 bits au début
    1 + max_bits bits par entier
    big_max_bits bits par entier en overflow
    1 + max_bits <= SIZE_OF_INT
    """
    # "on essaie de tt mettre dans un string puis de le spliter"
    output = []
    bit_string = ""
    nb_overflow = 0
    overflow_list = []
    big_max_bits = max(arr).bit_length()
    bit_string += get_bin(max_bits, 6)
    bit_string += get_bin(big_max_bits, 6)
    arr_len = len(arr)
    bit_string += get_bin(arr_len, 6)
    print(f"max_bits={max_bits}, big_max_bits={big_max_bits}, arr_len={arr_len}")
    print(f"bit_string start: {bit_string[:6]}:{bit_string[6:12]}:{bit_string[12:18]}:{bit_string[18:]}")
    for num in arr:
        if num < 2**max_bits:
            bit_string += '0' + get_bin(num, max_bits)
        else:
            bit_string += '1' + get_bin(nb_overflow, max_bits)
            nb_overflow += 1
            overflow_list.append(get_bin(num, big_max_bits))
            print(f"Overflow: {num}, Binary: \t{get_bin(num, big_max_bits)}")
        print(f"Number: {num}, Binary: \t{bit_string[:6]}:{bit_string[6:12]}:{bit_string[12:18]}:{bit_string[18:]}")
    print("1>>",bit_string)
    for num in overflow_list:
        bit_string += num
    print("2>>",bit_string)
    # affiche_bit_string(bit_string)
    while len(bit_string) >= SIZE_OF_INT:
        output.append(int(bit_string[:SIZE_OF_INT], 2))
        bit_string = bit_string[SIZE_OF_INT:]
    if bit_string:
        output.append(int(bit_string.ljust(SIZE_OF_INT, '0'), 2))  # Pad the last chunk if necessary
    # output += overflow_list
    return output

def compresse(arr: list, max_bits: int) -> None:
    """
    Meme chose que compress_array mais compresse en place
    """
    bit_string = ""
    nb_overflow = 0
    overflow_list = []
    big_max_bits = max(arr).bit_length()
    bit_string += get_bin(max_bits, 6)
    bit_string += get_bin(big_max_bits, 6)
    arr_len = len(arr)
    bit_string += get_bin(arr_len, 6)
    print(f"max_bits={max_bits}, big_max_bits={big_max_bits}, arr_len={arr_len}")
    print(f"bit_string start: {bit_string[:6]}:{bit_string[6:12]}:{bit_string[12:18]}:{bit_string[18:]}")
    while arr:
        num = arr.pop(0)
        if num < 2**max_bits:
            bit_string += '0' + get_bin(num, max_bits)
        else:
            bit_string += '1' + get_bin(nb_overflow, max_bits)
            nb_overflow += 1
            overflow_list.append(get_bin(num, big_max_bits))
            print(f"Overflow: {num}, Binary: \t{get_bin(num, big_max_bits)}")
        print(f"Number: {num}, Binary: \t{bit_string[:6]}:{bit_string[6:12]}:{bit_string[12:18]}:{bit_string[18:]}")
    print("1>>",bit_string)
    for num in overflow_list:
        bit_string += num
    print("2>>",bit_string)
    # affiche_bit_string(bit_string)
    while len(bit_string) >= SIZE_OF_INT:
        arr.append(int(bit_string[:SIZE_OF_INT], 2))
        bit_string = bit_string[SIZE_OF_INT:]
    if bit_string:
        arr.append(int(bit_string.ljust(SIZE_OF_INT, '0'), 2))  # Pad the last chunk if necessary
    # output += overflow_list
    # return output



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
    bit_string = get_bin(arr[0], SIZE_OF_INT)   # on recupere le premier entier
    max_bits = int(bit_string[:6], 2)           # on recupere la taille des entiers normaux
    big_max_bits = int(bit_string[6:12], 2)     # on recupere la taille des entiers en overflow 
    arr_len = int(bit_string[12:18], 2)         # on recupere la taille du tableau
    indice_elem = i * (max_bits + 1) + 18       # on calcule l'indice du i-eme element dans la chaine de bits
    
    if arr_len <= i:
        raise IndexError("Index out of range")
    
    indice_liste = indice_elem // SIZE_OF_INT   # indice de l'entier
    indice_bit = indice_elem % SIZE_OF_INT      # indice dans l'entier
    if indice_bit + max_bits + 1 > SIZE_OF_INT:
        # le bit est splitté entre deux entiers
        next_elem = arr[indice_liste + 1]
        next_elem = get_bin(next_elem, SIZE_OF_INT)
        elem = arr[indice_liste]
        elem = get_bin(elem, SIZE_OF_INT)
        elem += next_elem
    else:
        elem = arr[indice_liste]
        elem = get_bin(elem, SIZE_OF_INT)
    
    value = elem[indice_bit:indice_bit + max_bits + 1]
    if DEBUG: print(f"elem={elem}")
    if DEBUG: print(f"value={value}")
    if value[0] == '0':
        if DEBUG: print(f"Value : 0 - {int(value[1:], 2)}")
        return int(value[1:], 2)
    
    # value[0] == '1'
    indice_overflow = int(value[1:], 2)
    overflow_start = arr_len * (max_bits + 1) + 18  # 18 pour les 3x6 bits du début
    indice_overflow_bit = overflow_start + indice_overflow * big_max_bits # indice du debut de l'overflow dans la chaine de bits
    elem_overflow = arr[indice_overflow_bit // SIZE_OF_INT] 
    elem_overflow = get_bin(elem_overflow, SIZE_OF_INT)
    indice_overflow_bit_in_elem = indice_overflow_bit % SIZE_OF_INT # indice dans l'entier

    if indice_overflow_bit_in_elem + big_max_bits > SIZE_OF_INT:
        # le nombre est splitté entre deux entiers
        next_elem_overflow = arr[indice_overflow_bit // SIZE_OF_INT + 1]
        next_elem_overflow = get_bin(next_elem_overflow, SIZE_OF_INT)
        elem_overflow += next_elem_overflow
    
    value_overflow = elem_overflow[indice_overflow_bit_in_elem:indice_overflow_bit_in_elem + big_max_bits]
    if DEBUG: print(f"Value : 1 - {int(value[1:], 2)} --> {int(value_overflow, 2)}")
    
    return int(value_overflow, 2)


def decompress_array(arr: list) -> list:
    output = []
    overflow_list = []
    bit_string = get_bin(arr[0], SIZE_OF_INT)
    max_bits = int(bit_string[:6], 2)
    big_max_bits = int(bit_string[6:12], 2)
    arr_len = int(bit_string[12:18], 2)
    bit_string = bit_string[18:] # Remove the first 18 bits used for metadata
    arr = arr[1:]
    cpt = 0
    print(f"max_bits={max_bits}, big_max_bits={big_max_bits}, arr_len={arr_len}")
    while (arr or len(bit_string) >= max_bits + 1) and cpt < arr_len:
        print(f"--- Step {cpt} ---")
        if len(bit_string) < max_bits + 1:
            bit_string += get_bin(arr[0], SIZE_OF_INT)
            arr = arr[1:]
        current_bits = bit_string[:max_bits + 1]
        bit_string = bit_string[max_bits + 1:]
        print(f"bits : {current_bits} - {bit_string}")
        if current_bits[0] == '0':
            output.append(int(current_bits[1:], 2))
        else:
            pass
            indice_overflow = int(current_bits[1:], 2)
            output.append(indice_overflow)  # Placeholder, will be replaced later
            overflow_list.append(len(output) - 1)  # Store the index to replace later
        print(f"Decompressed so far: {output}")
        cpt += 1
    for i in overflow_list:
        print(f"--- Overflow at index {i} ---")
        print(f"bit_string : {bit_string}")
        if len(bit_string) < big_max_bits:
            bit_string += get_bin(arr[0], SIZE_OF_INT)
            arr = arr[1:]
            print(f"After adding new int, bit_string : {bit_string}")
        current_bits = bit_string[:big_max_bits]
        bit_string = bit_string[big_max_bits:]
        output[i] = int(current_bits, 2)
    return output

def decompress(arr: list) -> None:
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
    # arr = arr[1:]
    arr_len = len(arr)
    cpt = 0
    while (arr_len > 0 or len(bit_string) >= max_bits + 1) and cpt < nb_of_int:
        print(f"--- Step {cpt} ---")
        if len(bit_string) < max_bits + 1:
            bit_string += get_bin(arr.pop(0), SIZE_OF_INT)
        current_bits = bit_string[:max_bits + 1]
        bit_string = bit_string[max_bits + 1:]
        print(f"bits : {current_bits} - {bit_string}")
        if current_bits[0] == '0':
            arr.append(int(current_bits[1:], 2))
        else:
            pass
            indice_overflow = int(current_bits[1:], 2)
            arr.append(indice_overflow)  
            overflow_list.append(cpt)           # stock l'indice a remplacer plus tard
        print(f"Decompressed so far: {cpt}")
        print(f"Current array: {arr}")
        cpt += 1

    print("========================================================")
    for i in overflow_list:
        print(f"--- Overflow at index {i} ---")
        print(f"bit_string : {bit_string}")
        if len(bit_string) < big_max_bits:
            bit_string += get_bin(arr.pop(0), SIZE_OF_INT)
            print(f"After adding new int, bit_string : {bit_string}")
        current_bits = bit_string[:big_max_bits]
        bit_string = bit_string[big_max_bits:]
        arr[i] = int(current_bits, 2)
        print(f"Replaced index {i} with value {arr[i]}")

# affiche_bit_string(get_bin(1024, 12))

def test():
    longeur = randint(2, 1000)
    longeur = 20
    arr = [randint(1, 1000) for _ in range(longeur)]
    max_bits = 4  # Example bit size for compression (4 bits for values 1-5, 12 bits for overflow values)
    arr_compressed = compress_array(arr, max_bits)
    arr_decompressed = decompress_array(arr_compressed)
    assert arr == arr_decompressed, f"Test failed: {arr} != {arr_decompressed}"
    print("Test passed!")

if __name__ == "__main__":
    pass
    arr = [1, 2, 3, 1024, 4, 5, 2048]
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
    aa = decompress_array(aa)
    # decompress(aa)
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