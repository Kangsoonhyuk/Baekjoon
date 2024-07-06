# 알람 시계

h, m = map(int, input().split())

if (0 <= h <= 24) and (0 <= m <= 59):
    if m < 45:
        if h-1 <0:
            print(23, 60-(45-m))
        else:
            print(h-1, 60-(45-m))
    else:
        print(h, m-45)