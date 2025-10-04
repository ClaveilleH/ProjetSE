SIZE_OF_INT = 32


def get_bin(num: int, bits: int = SIZE_OF_INT) -> str:
    """
    Retourne la représentation binaire de num sur 'bits' bits
    ----------
    :param num: l'entier à convertir
    :param bits: le nombre de bits à utiliser pour la représentation
    :return: la chaîne binaire représentant l'entier
    """
    return f"{num:0{bits}b}"


class Method1:
    """
    This is Method1 class.
    """
    def __init__(self, array: list):
        self.array = array
        self.maxBits = max(array).bit_length() # On recupère le nombre de bits nécessaires pour représenter le plus grand entier
        # print(f"Max value: {self.maxValue}, Max bits needed: {self.maxBits}")

    def compress(self):
        output = []
        current_int = "" # on va passer par des chaines de texte pour faire les manipulations de bits
        for num in self.array:
            bin_repr = get_bin(num, self.maxBits)
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

        return output

    def affiche(self):
        print("Array: ", end='')
        print(self.array)
        print("Binary representation:")
        for num in self.array:
            print(get_bin(num, self.maxBits))
    



if __name__ == "__main__":
    method = Method1([1, 2, 3, 4, 5, 6])
    method.affiche()