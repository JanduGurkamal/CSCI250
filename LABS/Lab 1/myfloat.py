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
            # the first bit is always the sign bit, followed by exponent, then mantissa
        for i in binstring:
            if i != "0" and i != "1":
                raise ValueError("Expecting 0s and 1s only")

        result = 0
        # complete the method from here:

        sign = int(binstring[0])
        exponent_bin = binstring[1:(self.e + 1)]
        offset = -2 ** (self.e - 1) + 1
        exponent_dec = int(exponent_bin, 2) + offset
        mantissa = 1
        number_part = binstring[(self.e + 1):]
        number_part_dec = 0
        for i, bit in enumerate(number_part):
            number_part_dec += int(bit) * (2 ** -(i + 1))

        number_part_dec = 1 + number_part_dec

        if int(sign) == 1:
            sign = -1
        else:
            sign = 1

        result = sign * number_part_dec * (2 ** exponent_dec)
        return result

    def toBin(self, c):
        exponent = 0

        if c == 0:
            # Handle zero case
            exponent_bin = '0' * self.e
            fraction_binary = ['0'] * self.m
            sign = 0
        else:
            sign = 0
            if c < 0:
                c = -c
                sign = 1

            while c >= 2.0:
                c = c / 2.0
                exponent += 1
            while c < 1.0:
                c = c * 2.0
                exponent -= 1

            offset = -2 ** (self.e - 1) + 1
            exponent = exponent - offset

            exponent_bin = bin(exponent)[2:]
            if exponent < 0:
                exponent_bin = bin(exponent & ((1 << self.e) - 1))[2:]

            while len(exponent_bin) < self.e:
                exponent_bin = '0' + exponent_bin

            fraction = c - 1.0

            fraction_binary = []
            for _ in range(self.m):
                fraction *= 2
                bit = int(fraction)
                fraction_binary.append(str(bit))
                fraction -= bit

        number = str(sign) + exponent_bin + ''.join(fraction_binary)

        if len(number) < 1 + self.e + self.m:
            number = number + ('0' * (1 + self.e + self.m - len(number)))

        return number

    def add(self, x, y):
        """
        This method adds the two numbers up, then outputs the result
        """

        result = ""

        # complete the method from here:
        a = self.toDec(x)
        b = self.toDec(y)

        c = a + b

        result = self.toBin(c)
        return result

    def subtract(self, x, y):
        """
        This method subtracts y from x, then outputs the result
        """

        result = ""

        # complete the method from here:
        a = self.toDec(x)
        b = self.toDec(y)

        c = a - b

        result = self.toBin(c)
        return result

if __name__ == "__main__":
    print("local test mode")
    # write your own test code here
