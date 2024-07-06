# A+B-3

case = int(input())

a = [0]*case
b = [0]*case

for i in range(case):
    m, n = map(int, input().split())
    a[i] = m
    b[i] = n

for i in range(case):
    print(a[i] + b[i])