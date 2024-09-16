#
#   Original: Jetic Gu
#   Columbia College
#   2024-09-13
#

class MyFloat:
    def __init__(self, m, e):
        # e is an int, representing the number of bits for the exponent
        self.e = e
        # m is an int, representing the number of bits for the mantissa
        self.m = m
        return

    def toDec(self, binstring):
        """
        This method converts binstring
        It converts binstring to a normal python float, then returns it
        """
        if not isinstance(binstring, str):
            raise TypeError("Wrong datatype, expecting str")
        if len(binstring) != 1 + self.m + self.e:
            raise ValueError("Length of binary number incorrect")
            # the first bit is alwasy the sign bit, followed by exponent, then mantissa
        for i in binstring:
            if i != "0" and i != "1":
                raise ValueError("Expecting 0s and 1s only")

        result = 0
        # complete the method from here:

        sign = int(binstring[0])
        exponent_bin = binstring[1:6]
        offset = -2**(self.e-1) + 1
        exponent_dec = int(exponent_bin, 2) + offset
        mantissa = 1
        number_part = binstring[6:self.m]
        number_part_dec = 0
        for i, bit in enumerate(number_part):
            number_part_dec += int(bit) * (2 ** -(i + 1))

        number_part_dec = 1 + number_part_dec

        if int(sign) == 1:
            sign = -1
        else:
            sign = 1

        result = sign * number_part_dec * (2**exponent_dec)
        return result

    def add(self, x, y):
        """
        This method adds the two number up, then outputs the result
        """

        result = ""

        # complete the method from here:
        a = self.toDec(x)
        b = self.toDec(y)

        c = str(a+b)

        exponent = 0
        while c[0] != '1' and c[1] != '.' or (c[1] != '.') or (c[0] != '1'):
            exponent = exponent+1
            c = str(float(c)/2)

        offset = -2 ** (self.e - 1) + 1
        exponent = exponent - offset

        sign = 0
        if float(c) > 0:
            sign = 0

        else:
            c = float(c) * -1
            sign = 1

        number = c.split('.')[0]
        fraction = float(c) - int(number)

        exponent_bin = bin(exponent)[2:]

        fraction_binary = []
        while fraction:
            fraction *= 2
            bit = int(fraction)
            fraction_binary.append(str(bit))
            fraction -= bit

            if len(fraction_binary) > 9:
                break

        number = str(sign) + exponent_bin + "".join(fraction_binary)

        if len(number) != 16:
            number = number + ('0'*(16-len(number)))

        result = number
        return result


if __name__ == "__main__":
    print("local test mode")
    # write your own test code here
