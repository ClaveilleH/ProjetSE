"""
For example, if we find that 12 bits are needed to represent 6 elements, then the first representation will write:
- the first  integer compressed onto the first 12 bits of the first integer in the output,
- the second integer compressed onto the next 12 bits of the first integer in the output,
- the third  integer compressed on bits 25 to 32 on the first integer in the output and on the first 4 bits of the second integer in the output
- the fourth integer compressed on bits 5 to 16 on the second integer in the output
- the fifth  integer compressed on bits 17 to 28 on the second integer in the output
- the sixth  integer compressed over bits 29 to 32 of the second integer output and over the first 8 bits of the third integer output
"""

array = [1, 2, 3, 4, 5, 6]
maxBits = 12  # Example bit size for compression
maxBits = max(array).bit_length() # On recupère le nombre de bits nécessaires pour représenter le plus grand entier
print(f"Max value: {max(array)}, Max bits needed: {maxBits}")
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
    current_int = "" # on va passer par des chaines de texte pour faire les manipulations de bits
    for num in arr:
        bin_repr = get_bin(num, maxBits)
        print(f"Number: {num}, Binary: {bin_repr}")
        current_int += bin_repr # un fait une grande chaine de bits
    
    # on découpe cette grande chaine en morceaux de sizeOfInt
    while len(current_int) > 0:
        if len(current_int) >= SIZE_OF_INT:
            output.append(int(current_int[:SIZE_OF_INT], 2))
            current_int = current_int[SIZE_OF_INT:]
        else:
            output.append(int(current_int.ljust(SIZE_OF_INT, '0'), 2))
            current_int = ""
    arr = output
    return output

def decompress_array(arr: list) -> list:
    output = []
    bit_string = ""
    for num in arr:
        bit_string += get_bin(num, SIZE_OF_INT)
    
    while len(bit_string) != 0:
        if len(bit_string) >= maxBits:
            output.append(int(bit_string[:maxBits], 2))
            bit_string = bit_string[maxBits:]
        else:
            output.append(int(bit_string.ljust(maxBits, '0'), 2))
            bit_string = ""
    return output



if __name__ == "__main__":
    affiche(array)
    compressed = compress_array(array)
    # affiche(compressed)
    print("Compressed:", array)
    decompressed = decompress_array(compressed)
    affiche(decompressed)