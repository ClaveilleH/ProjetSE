"""
the second representation will write
- the first integer compressed over the first 12 bits of the first integer output,
- the second integer compressed over the next 12 bits of the first integer output,
- the third compressed integer on the first 12 bits of the second output integer,
- the fourth compressed integer on the next 12 bits of the second output integer,
- the fifth compressed integer on the first 12 bits of the third output integer,
- the sixth compressed integer on the next 12 bits of the third output integer,



We now want to perform compression with overflow areas. 
Indeed, if a single number in the initial array requires a large number of bits k and the other numbers require
 k' bits with k' < k, it is a waste to represent all numbers with k bits. In this case, we can assign a special value to a compressed integer that indicates that the true value is located elsewhere at a certain position in my table, called the overflow area.

For example, if we want to encode the numbers 1, 2, 3, 1024, 4, 5, and 2048. We can encode 1, 2, 3, and 4 using 3 bits and the other numbers using 11 bits at the end. Since we don't want to lose direct access, we must precalculate the number of integers in the overflow area and then integrate this into our encoding.
 Here, we have 2 integers in the overflow area, which requires 1 bit to be encoded. We will use 1 bit of the encoding to express the fact that we are not directly representing a number but a position in the overflow area. If 1 corresponds to the overflow area, and x-y means that the first bit is x and the others are y, we will represent the sequence of numbers 1, 2, 3, 1024, 4, 5, 2048 
 as 0-1, 0-2, 0-3, 1-0, 0-4, 0-5, 1-1, 1024, 2048

"""
SIZE_OF_INT = 32  # Assuming a 32-bit integer representation

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


def compress_array(arr: list, max_bits: int) -> str:
    "on essaie de tt mettre dans un string puis de le spliter"
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
    for num in arr:
        # liste.append(get_bin(num, max_bits))
        if num < 2**max_bits:
            bit_string += '0' + get_bin(num, max_bits)
        else:
            bit_string += '1' + get_bin(nb_overflow, max_bits)
            nb_overflow += 1
            overflow_list.append(get_bin(num, big_max_bits))
            print(f"Overflow: {num}, Binary: \t{get_bin(num, big_max_bits)}")
        print(f"Number: {num}, Binary: \t{bit_string}")
    # output += overflow_list
    print(bit_string)
    for num in overflow_list:
        bit_string += num
    print(bit_string)
    affiche_bit_string(bit_string)
    while len(bit_string) >= SIZE_OF_INT:
        output.append(int(bit_string[:SIZE_OF_INT], 2))
        bit_string = bit_string[SIZE_OF_INT:]
    if bit_string:
        output.append(int(bit_string.ljust(SIZE_OF_INT, '0'), 2))  # Pad the last chunk if necessary
    # output += overflow_list
    return output


def affiche(arr : list) -> None:
    print("Array: ", end='')
    print(arr)
    print("Binary representation:")
    for num in arr:
        print(num[0], '-', int(num[1:], 2), sep='')


def get(arr: list, i: int) -> int:
    bit_string = get_bin(arr[0], SIZE_OF_INT)
    max_bits = int(bit_string[:6], 2)
    big_max_bits = int(bit_string[6:12], 2)
    arr_len = int(bit_string[12:18], 2)
    indice_elem = i * (max_bits + 1) + 18 # 18 pour les 3x6 bits du début

    indice_liste = indice_elem // SIZE_OF_INT
    indice_bit = indice_elem % SIZE_OF_INT
    # print(f"i={i}, indice_elem={indice_elem}, indice_liste={indice_liste}, indice_bit={indice_bit}")
    elem = arr[indice_liste]
    elem = get_bin(elem, SIZE_OF_INT)
    value = elem[indice_bit:indice_bit + max_bits + 1]
    # print(f"elem={elem}")
    # print(f"value={value}")
    if value[0] == '0':
        print(f"Value : 0 - {int(value[1:], 2)}")
        return int(value[1:], 2)
    else:
        
        indice_overflow = int(value[1:], 2)
        overflow_start = arr_len * (max_bits + 1) + 18  # 18 pour les 3x6 bits du début
        indice_overflow_bit = overflow_start + indice_overflow * big_max_bits
        elem_overflow = arr[indice_overflow_bit // SIZE_OF_INT]
        elem_overflow = get_bin(elem_overflow, SIZE_OF_INT)
        indice_overflow_bit_in_elem = indice_overflow_bit % SIZE_OF_INT
        if indice_overflow_bit_in_elem + big_max_bits > SIZE_OF_INT:
            # le bit est splitté entre deux entiers
            next_elem_overflow = arr[indice_overflow_bit // SIZE_OF_INT + 1]
            # print(type(next_elem_overflow))
            next_elem_overflow = get_bin(next_elem_overflow, SIZE_OF_INT)
            elem_overflow += next_elem_overflow
        value_overflow = elem_overflow[indice_overflow_bit_in_elem:indice_overflow_bit_in_elem + big_max_bits]
        # elem_overflow = arr[arr_len* (max_bits + 1) // SIZE_OF_INT + indice_overflow * (big_max_bits // SIZE_OF_INT)]
        # elem_overflow = get_bin(elem_overflow, SIZE_OF_INT)
        # print(f"Overflow index: {indice_overflow}, Overflow bit index: {indice_overflow_bit}, elem_overflow: {elem_overflow}, indice_overflow_bit_in_elem: {indice_overflow_bit_in_elem}")
        print(f"Value : 1 - {int(value[1:], 2)} --> {int(value_overflow, 2)}")
        #! la fin est dans un auree entier
        return int(value_overflow, 2)
    pass


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
    while arr and cpt < arr_len:
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
        if len(bit_string) < big_max_bits:
            bit_string += get_bin(arr[0], SIZE_OF_INT)
            arr = arr[1:]
        current_bits = bit_string[:big_max_bits]
        bit_string = bit_string[big_max_bits:]
        output[i] = int(current_bits, 2)
    return output

# affiche_bit_string(get_bin(1024, 12))

if __name__ == "__main__":
    pass
    arr = [1, 2, 3, 1024, 4, 5, 2048]
    max_bits = 3  # Example bit size for compression (3 bits for values 1-5, 11 bits for overflow values)

    # aa = compress_array(arr, max_bits)
    aa = compress_array(arr, max_bits)
    print("=========")
    for i in range(7):
        get(aa, i)
    print("=========")
    print(aa)
    aa = decompress_array(aa)
    print(aa)
    # affiche(arr)
    # compressed = compress_array(arr)
    # print("Compressed:")
    # affiche(compressed)
    # decompressed = decompress_array(compressed)
    # print("Decompressed:")
    # affiche(decompressed)
    print("=========")
    print(get_bin(1024, 12))




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