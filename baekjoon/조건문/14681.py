# 사분면 고르기

x = int(input())
y = int(input())

quadrant_1 = 1
quadrant_2 = 2
quadrant_3 = 3
quadrant_4 = 4

if (-1000<=x<=1000) and (-1000<=y<=1000) and (x !=0 ) and (y != 0):
    if x > 0 and y > 0:   print(quadrant_1)
    elif x > 0 and y < 0: print(quadrant_4)
    elif x < 0 and y > 0: print(quadrant_2)
    else:                 print(quadrant_3)
else:
    print('error')