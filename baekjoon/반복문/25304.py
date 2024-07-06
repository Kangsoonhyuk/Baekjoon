# 영수증

sum = int(input())
n = int(input())

a = [0]*n
b = [0]*n

check = 0

for i in range(n):
    a[i], b[i] = map(int, input().split())

    check += a[i]*b[i]

if sum == check:
    print('Yes')
else:
    print('No')