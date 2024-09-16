from myfloat import MyFloat

ty = MyFloat(e=5, m=10)

if ty.toDec("1100010101000000") == -5.25:
    print("Test case 1 passed")
else:
    print("Test case 1 failed")


if ty.toDec("0100111010000000") == 26.0:
    print("Test case 2 passed")
else:
    print("Test case 2 failed")


if ty.add("1100010101000000", "0100111010000000") == "0100110100110000":
    print("Test case 3 passed")
else:
    print("Test case 3 failed")

