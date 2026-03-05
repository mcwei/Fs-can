#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import math
import numpy as np
from damiao_motor.damiao_motor import Motor, MotorControl, DM_Motor_Type, Control_Type

# 配置参数
NUM_MOTORS = 1  # 控制电机数量
CAN_INTERFACE = "PCAN_USBBUS1"  # CAN接口名称
CAN_BITRATE = 1000000  # CAN波特率
MOTOR_TYPE = DM_Motor_Type.DM4310  # 电机类型

# 正弦波参数
FREQUENCY = 0.1  # 频率 (Hz)
AMPLITUDE = 6  # 幅度 (rad)
DURATION = 600.0  # 运行时间 (s)

def main():
    # 创建电机控制对象
    control = MotorControl(CAN_INTERFACE, bitrate=CAN_BITRATE)
    
    # 创建并添加电机
    motors = []
    for i in range(NUM_MOTORS):
        motor = Motor(MOTOR_TYPE, i + 1, i + 0X10)  # CAN ID从1开始
        control.addMotor(motor)
        motors.append(motor)
        control.enable(motor)
        print(f"电机 {i + 1} 已使能")
    
    try:
        start_time = time.time()
        while time.time() - start_time < DURATION:
            current_time = time.time() - start_time
            
            # 计算正弦波位置
            position = AMPLITUDE * math.sin(2 * math.pi * FREQUENCY * current_time)
            
            # 控制所有电机
            for motor in motors:
                # control.controlMIT(
                #     motor,
                #     kp=10.0,  # 位置增益
                #     kd=1.0,   # 速度增益
                #     q=position,  # 目标位置
                #     dq=0.0,   # 目标速度
                #     tau=0.0   # 前馈力矩
                # )
                control.control_Pos_Vel(motor, position, 20.0)
                print(position)
            # 控制频率
            time.sleep(0.001)  # 1kHz控制频率
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    finally:
        # 失能所有电机
        for motor in motors:
            control.disable(motor)
            print(f"电机 {motor.SlaveID} 已失能")

if __name__ == "__main__":
    main() 