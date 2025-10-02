"""
For example, if we find that 12 bits are needed to represent 6 elements, then the first representation will write:
- the first  integer compressed onto the first 12 bits of the first integer in the output,
- the second integer compressed onto the next 12 bits of the first integer in the output,
- the third  integer compressed on bits 25 to 32 on the first integer in the output and on the first 4 bits of the second integer in the output
- the fourth integer compressed on bits 5 to 16 on the second integer in the output
- the fifth  integer compressed on bits 17 to 28 on the second integer in the output
- the sixth  integer compressed over bits 29 to 32 of the second integer output and over the first 8 bits of the third integer output
"""

# maxBits = 12  # Example bit size for compression
# maxBits = max(array).bit_length() # On recupère le nombre de bits nécessaires pour représenter le plus grand entier
# print(f"Max value: {max(array)}, Max bits needed: {maxBits}")
SIZE_OF_INT = 32  # Assuming a 32-bit integer representation


def affiche(arr : list) -> None:
    print("Array: ", end='')
    print(arr)
    print("Binary representation:")
    for num in arr:
        print(f"{num:032b}")

def get_bin(num: int, bits: int) -> str:
    """
    Retourne la représentation binaire de num sur 'bits' bits
    ----------
    :param num: l'entier à convertir
    :param bits: le nombre de bits à utiliser pour la représentation
    :return: la chaîne binaire représentant l'entier
    """
    return f"{num:0{bits}b}"

def compress_array(arr : list) -> list:
    output = []
    maxBits = max(array).bit_length() # On recupère le nombre de bits nécessaires pour représenter le plus grand entier
    print(f"Max value: {max(array)}, Max bits needed: {maxBits}")
    chaine = "" # on va passer par des chaines de texte pour faire les manipulations de bits
    chaine += get_bin(maxBits, 6) # on encode la taille des données sur 6 bits (max 32 = int)
    for num in arr:
        bin_repr = get_bin(num, maxBits)
        print(f"Number: {num}, Binary: {bin_repr}")
        chaine += bin_repr # un fait une grande chaine de bits
    
    # on découpe cette grande chaine en morceaux de sizeOfInt
    while len(chaine) > 0:
        if len(chaine) >= SIZE_OF_INT:
            output.append(int(chaine[:SIZE_OF_INT], 2))
            chaine = chaine[SIZE_OF_INT:]
        else:
            output.append(int(chaine.ljust(SIZE_OF_INT, '0'), 2))
            chaine = ""
    arr = output
    print(get_bin(output[0], SIZE_OF_INT))
    print(get_bin(output[0], SIZE_OF_INT)[:6], end=':')
    print(get_bin(output[0], SIZE_OF_INT)[6:6+maxBits], end=':')
    print(get_bin(output[0], SIZE_OF_INT)[6+maxBits:6+2*maxBits], end=':')
    print(get_bin(output[0], SIZE_OF_INT)[6+2*maxBits:6+3*maxBits], end=':')
    print(get_bin(output[0], SIZE_OF_INT)[6+3*maxBits:], end=' ')

    print(get_bin(output[1], SIZE_OF_INT)[:maxBits-2], end=':')

    print()
    return output

def decompress_array_en_place(arr: list) -> None:
    bit_string = get_bin(arr.pop(0), SIZE_OF_INT) # on commence par le premier entier
    size = len(arr) # nombre d'entiers dans le tableau compressé (- 1) parce qu'on a pop le premier
    maxBits = int(bit_string[:6], 2)  # On récupère les 6 premiers bits qui contiennent maxBits
    bit_string = bit_string[6:] 

    while len(bit_string) >= maxBits or size>0 : # tant qu'on a pas tout lu

        if len(bit_string) < maxBits and size > 0:
            # on recupere le prochain entier
            bit_string += get_bin(arr.pop(0), SIZE_OF_INT)
            size -= 1
            
        arr.append(int(bit_string[:maxBits], 2)) # on ajoute le nouvel entier décompressé
        bit_string = bit_string[maxBits:]

    if len(bit_string) > 0 :
        print("Last bits remaining:", bit_string)
        
    return

def get_from_int(num: int, start: int, length: int) -> int:
    """
    Fonction pour extraire une séquence de bits d'un entier.
    ----------
    :param num: l'entier source
    :param start: la position de départ (0-indexée, de droite à gauche)
    :param length: le nombre de bits à extraire
    :return: l'entier correspondant à la séquence de bits extraite
    """
    bit_string = get_bin(num, SIZE_OF_INT)
    return int(bit_string[start:start+length], 2)

def get(arr: list, i: int) -> int:
    """
    Fonction pour obtenir le i-ème entier du tableau compressé.
    ----------
    :param arr: le tableau compressé
    :param i: l'indice de l'entier à récupérer
    :return: l'entier à l'indice i
    """ 
    bit_string = get_bin(arr[0], SIZE_OF_INT) # on recupere le premier entier
    maxBits = int(bit_string[:6], 2)  # On récupère les 6 premiers bits qui contiennent maxBits
    indice = i * maxBits + 6 # on calcule l'indice du bit à récupérer
    indice_int = indice % SIZE_OF_INT
    # if indice // SIZE_OF_INT >= len(arr):
    #     raise IndexError("Index out of range")
    if indice < 0:
        raise IndexError("Index must be non-negative")
    if  indice % SIZE_OF_INT + maxBits > SIZE_OF_INT: 
        # si le nombre est sur deux entiers
        
        int1 = arr[indice // SIZE_OF_INT] 
        int2 = arr[indice // SIZE_OF_INT + 1]
        
        part1 = get_bin(int1, SIZE_OF_INT)[indice_int:]
        part2 = get_bin(int2, SIZE_OF_INT)[:maxBits - (SIZE_OF_INT - (indice_int))]

        val = part1 + part2
        return int(val, 2)
        
    return get_from_int(arr[indice // SIZE_OF_INT], indice % SIZE_OF_INT, maxBits)
    
def get_bin_from_int(num: int, start: int, length: int) -> str:
    """
    Fonction pour extraire une séquence de bits d'un entier.
    ----------
    :param num: l'entier source
    :param start: la position de départ (0-indexée, de droite à gauche)
    :param length: le nombre de bits à extraire
    :return: la chaîne binaire correspondant à la séquence de bits extraite
    """
    bit_string = get_bin(num, SIZE_OF_INT)
    return bit_string[start:start+length]

def bin_get(arr: list, i:int) -> str:
    bit_string = get_bin(arr[0], SIZE_OF_INT) # on commence par le premier entier
    maxBits = int(bit_string[:6], 2)  # On récupère les 6 premiers bits qui contiennent maxBits
    indice = i * maxBits + 6 # on calcule l'indice du bit à récupérer
    return get_bin_from_int(arr[indice // SIZE_OF_INT], indice % SIZE_OF_INT, maxBits)


if __name__ == "__main__":
    # array = [1, 2, 3, 4, 5, 6]
    array = [1, 2, 3, 4, 5, 6, 100, 100, 200]
    # affiche(array)
    # compressed = compress_array(array)
    # affiche(compressed)
    # print("=========")
    # decompressed = decompress_array(compressed)
    # affiche(decompressed)

    print("=========")
    print("=========")
    affiche(array)
    compressed = compress_array(array)
    for i in range(len(array)):
        print(get(compressed, i), end=' ')
    print()
    for i in range(len(array)):
        print(bin_get(compressed, i), end=' ')
    print("\n=========")

    affiche(compressed)
    decompress_array_en_place(compressed)
    affiche(compressed)




"""
[1, 2, 3, 4, 5, 6] --> [196608, 50397184, 100663296] --> [1, 2, 3, 4, 5, 6]
[1, 2, 3, 4, 5, 6] --> 000000 001, 010, 011, 100, 101, 110 --> 001010011100101110110, 001000000000... = 

[1, ...., 1, 0, 0, 0]
[1, ...., 1]

[1, ...., 1, 0, 0, 1]
[1, ...., 1, 0, 0, 0]

sizeOfint:data
    6    :data
length:sizeOfint:data
   32 :    6    :data
len(length):length:sizeOfint:data
   6       :  x   :    6    :data
"""