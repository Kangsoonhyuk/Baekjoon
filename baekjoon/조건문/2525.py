# 오븐 시계

h, m = map(int, input().split())
r = int(input())

# 분에 더할 시간을 추가합니다.
total_minutes = h * 60 + m + r

# 시간을 24시간 형식으로 변환합니다.
final_hour = (total_minutes // 60) % 24
final_minute = total_minutes % 60

print(final_hour, final_minute)
