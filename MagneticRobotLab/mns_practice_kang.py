#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Software License Agreement (BSD License)

import rospy
import numpy as np
from std_msgs.msg import String, Float32, Float32MultiArray
from sensor_msgs.msg import Joy
import sys
import signal
import time
#rosrun serial_example serial_example_node   rosrun mns_pkg mns_practice.py

# 조이스틱 입력을 받아서 저장하기 위한 2차원 리스트 변수 초기화
joy = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # button
       [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]  # axes

# node 내부의 시간의 흐름을 구현하기 위한 값 선언
turntime = Float32()
turntime.data = 0

robot_mode = 9  # 알고리즘 모드를 설정하는 변수 초기화

# [Ctrl]+[C] 누르면 탈출하게끔 하는 코드 (강제종료 안 될때를 대비한 코드)
def signal_handler(signal, frame):  # ctrl + c -> exit program
    print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


# joystick 값을 받아오는 함수
def joycallback(data):
    global joy
    joy[0] = data.buttons
    joy[1] = data.axes

# joysitck 모드변환
def joy_mode():
    global robot_mode  # 전역 변수 사용 선언


    if joy[0][9] == 1:   # start
        robot_mode = 0   # PSU 통신 mode

    elif joy[0][4] == 1:  # LB
        robot_mode = 1   # helical mode

    elif joy[0][5] == 1: # RB
        robot_mode = 2   # gradient mode

    elif joy[0][6] == 1: # LT
        robot_mode = 3   #escape

    
    
    return robot_mode  # 함수 내부에서 return 사용

#변수 초기화

f = 0
omega = 2*np.pi*f
theta = 0
phi = 0
H0 = 4.5
volt = 0
g_g = 0
I_g = 1
flag = 0

# B
Hh = 0
Huy = 0
Huz = 0

# Coil constants
k_h  = 1.6146
k_uy = 1.6149
k_uz = 1.6174
k_m  = 5.4125
k_g  = 6.6220

# Resistance
Rh  = 8.4
Ruy = 11.0
Ruz = 9.2
Rm  = 6.2
Rg  = 10.4

Ig = 1
Im = 1
F = 0

# Helical Cal
def cal_H_r(): 
    global Hh, Huy, Huz
    global k_h, k_uy, k_uz, k_m, k_g
    global Rh, Ruy, Ruz, Rm, Rg
    global V, Ig, Im

    turntime.data += 0.000004
    delta = (np.pi/2)
    omega = 2*np.pi*f

    U = np.array([np.sin(theta), -np.cos(theta) * np.cos(phi), -np.cos(theta) * np.sin(phi)])
    N = np.array([np.cos(theta), np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi)])
    H_r = np.array(H0 * (np.cos(delta) * N + np.sin(delta) * np.cos(omega * turntime.data)*U +  np.sin(delta) * np.sin(omega * turntime.data)*np.cross(N, U)))

    #print('***************H_r***************\n\n')    
    #print(H_r)

    print('\n\n*********FREQUENCY***************\n\n')
    print(f)

    #print('\n\n***********TURN TIME*************\n\n')
    #print(turntime.data)

    Hh = H_r[0]
    Huy = H_r[1]
    Huz = H_r[2]

    # Current
    Ih  = Hh/k_h
    Iuy = Huy/k_uy
    Iuz = Huz/k_uz
    

    # Voltage
    Vh  = Ih*Rh
    Vuy = Iuy*Ruy
    Vuz = Iuz*Ruz
    
    
    V = np.array([Vh, Vuy, Vuz, 0, 0])
    #print(V)

    volt_msg = Float32MultiArray()
    volt_msg.data = V.tolist()
    pub_volt.publish(volt_msg)

#Gradient Cal
def Ca_G_F():
    global Hh, Huy, Huz
    global k_h, k_uy, k_uz, k_m, k_g
    global Rh, Ruy, Ruz, Rm, Rg
    global V, Im, F, Fm, Fg
    
    Mu0 = 1.05
    M = 1.5
    V = 0.007
    theta = np.pi / 12

    #Im = -2.8597 * Ig
    #F = 0.3616 * (Mu0*M*V) * ( Im / 0.05**2 ) * ( np.array([np.cos(theta), np.sin(theta)]) )
    Im = F / ( np.array([np.cos(theta), np.sin(theta)]) * 0.3616*(Mu0*M*V) )  * 0.05**2
    Ig = Im / -2.8597

    # 제한된 Im 값 계산
    #Im_min = -9  # 최소값
    #Im_max = 9  # 최대값
    #Im = max(Im_min, min(Im, Im_max))

    #mns
    G_m = 0.6413 * (Im / (0.195 ** 2))
    G_g = 0.3286 * ( (Im / -2.8597) / (0.140 ** 2))

    H_mns = np.array([(G_g + G_m), (-2.4398 * G_g - 0.5 * G_m)])

    Hm = H_mns[0]
    Hg = H_mns[1]
    #Fm = F[0]
    #Fg = F[1]


    I_m = Hm/k_m
    I_g = Hg/k_g
    #I_m = Fm/k_m
    #I_g = Fg/k_g
   
    # Voltage
    Vm = I_m*Rm
    Vg = I_g*Rg

    print('\n\n*********GRADIENT CURRENT***************\n\n')
    print('I_g', I_g)
    print('I_m', I_m)

    V = np.array([0, 0, 0, Vm, Vg])
    volt_msg = Float32MultiArray()
    volt_msg.data = V.tolist()
    pub_volt.publish(volt_msg)



### 해당 프로그램의 메인문 ###
def mns_practice():
    global f, phi, pub_volt, flag, theta, Ig, Im, F

    # 해당 node 설정
    rospy.init_node('mns', anonymous=True)

    #### 메세지 구독 구간 ####
    rospy.Subscriber('/joy', Joy, joycallback)  # 조이스틱 입력 값을 가져 옴

    #### 메세지 발행 구간 ####
    pub = rospy.Publisher('mns_msgs', String, queue_size=10)  # mode를 알리는 메세지를 발행
    pub_volt = rospy.Publisher('volt_array', Float32MultiArray, queue_size=10)  # 계산된 전압 값을 발행함
    rate = rospy.Rate(100)  # 100hz

    #### 본격적인 알고리즘 반복문 ####

    while not rospy.is_shutdown():

        # 현재 모드와 이전 모드를 비교하여 모드가 변경되었는지 확인
        joy_mode()

        if joy_mode() == 0:
            pub.publish("Comm_Start")  # 통신 시작 설정을 알리는 문자열 메세지 전송
            robot_mode = 9  # 이후 중립모드로 설정

        elif joy_mode() == 1:  # helical mode
            pub.publish("Control_Start")
            cal_H_r()
            ## 조이스틱 누르면 주파수 증감
            if joy[0][0] == 1 and flag == 0:  # Y
                theta += np.pi/12  # theta 증가
                flag = 1
            elif joy[0][2] == 1 and flag == 0:  # A
                theta -= np.pi/12  # theta 감소
                flag = 1
            elif joy[0][1] == 1 and flag == 0 :  # B
                phi += np.pi /12   # phi 증가
                flag = 1
                print(phi)
            elif joy[0][3] == 1 and flag == 0:  # X
                phi -= np.pi/12    # phi 감소
                flag = 1
                print(phi)
            elif joy[1][3] == 1: # right axis speed
                f += 0.01
                print(f)         # 주파수 증가
            elif joy[1][3] == -1: # right axis speed
                f -= 0.01
                print(f)         # 주파수 감소
            elif joy[0][8] == 1:  # back
                flag = 0 
            elif joy[0][10] == 1: # left axis attack
                f = 0              #주파수 초기화
                phi = 0  

        elif joy_mode() == 2:  # gradient mode
            pub.publish("Gradient_Start")
            Ca_G_F()
            if joy[1][1] == 1: # G라디언트 증가
                Ig += 0.001       # left axis up
            elif joy[1][1] == -1: # G라디언트 감소
                Ig -= 0.001       # left axis down
            elif joy[0][10] == 1: # left axis attack
                Ig = 0
                

        elif joy_mode() == 3:
            pub.publish('Comm_End')  # 통신 종료 설정을 알리는 문자열 메세지 전송
            robot_mode = 9  # 이후 중립모드로 설정
        
    
    
    rospy.spin()  # node 무한반복


# node 실행 명령어
if __name__ == '__main__':
    mns_practice()