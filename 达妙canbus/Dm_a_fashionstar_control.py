#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import can
import logging
import time
import math
from damiao_motor.damiao_motor import Motor, MotorControl, DM_Motor_Type, Control_Type
from fashionstar.fashionstar_CANservo import servo_control

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    # bus = can.interface.Bus(interface="pcan", channel="PCAN_USBBUS1", bitrate=1000000)
    bus = can.interface.Bus(bustype='canalystii', channel=0, bitrate=1000000)#初始化CAN1通道用来发送
    
    # 创建电机控制对象
    control = MotorControl(canbus = bus)
    servo = servo_control(bus, is_logging=True)
    
    servo_id = 0x00 # 0x00 is the ID of the first servo
    # 创建并添加电机
    motors = []
    for i in range(NUM_MOTORS):
        motor = Motor(MOTOR_TYPE, i + 1, i + 0X10)  # CAN ID从1开始
        control.addMotor(motor)
        motors.append(motor)
        control.enable(motor)
        print(f"电机 {i + 1} 已使能")

    # Initial delay
    time.sleep(1)

    # Unlock servo
    servo.unlock_SERVO(servo_id)
    time.sleep(0.5)

    # Reset multi-turn
    current_angle = servo.read_angle(servo_id)
    if current_angle is not None and abs(current_angle) > 180.0:
        servo.reset_multi_turn(servo_id)
        time.sleep(0.1)

    # 初始化计时器
    last_servo_time = time.time()
    last_dm_time = time.time()
    angle_value = 0  

    try:
        start_time = time.time()
        while True:
            current_time = time.time()
            position = 0
            # 每1毫秒发送MI电机控制命令
            if (current_time - last_dm_time) >= 0.001:  # 1毫秒
                # 计算正弦波位置
                position = AMPLITUDE * math.sin(2 * math.pi * FREQUENCY * (current_time-start_time))
                last_dm_time = current_time
            # 控制所有电机
            for motor in motors:
                control.control_Pos_Vel(motor, position, 20.0)
                print(position)
            
            # 每2000毫秒发送舵机控制命令
            if (current_time - last_servo_time) >= 2.0:  # 2000毫秒
                # 舵机控制：设置角度并读取
                servo.set_angle(servo_id, angle_value)
                time.sleep(0.01)
                # servo.read_angle(servo_id)
                # time.sleep(0.01)
                last_servo_time = current_time
                
                # 切换目标位置（可选）
                angle_value = 150 if angle_value == 0 else 0

            # 添加短暂延迟避免CPU过载
            time.sleep(0.0001)
            
    except KeyboardInterrupt:
        logging.info("Program terminated by user")
        control.disable()
        bus.shutdown()

if __name__ == "__main__":
    main()