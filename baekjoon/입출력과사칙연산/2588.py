#곱셈

a = int(input())
b = int(input())

hundred = b // 100
ten = b//10 - 10*hundred
one = b - hundred*100 - ten*10

print(a*one)
print(a*ten)
print(a*hundred)
print(a*one + a*ten*10 + a*hundred*100)
