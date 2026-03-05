import os
import sys
import time


# 添加当前目录的父目录到Python搜索路径
# sys.path.append(os.path.join(".\cybergear"))

# from pcan_cybergear import CANMotorController

# import can
# import logging
# import time
# # Initialize logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # Connect to the CAN bus with 1 Mbit/s bitrate
# bus = can.interface.Bus(interface="pcan", channel="PCAN_USBBUS1", bitrate=1000000)
# motor = CANMotorController(bus, motor_id=127, main_can_id=254)

# # 定义音符到电机参数的映射，为后面的音符分配更高的转速值
# note_to_speed = {"C": 6.6, "D": 6.8, "E": 7.3, "F": 8, "G": 9, "A": 10, "B": 13}

# # 定义小星星的音符和时长
# # 完整定义小星星的音符和时长
# notes = ["C", "C", "G", "G", "A", "A", "G",
#          "F", "F", "E", "E", "D", "D", "C",
#          "G", "G", "F", "F", "E", "E", "D",
#          "G", "G", "F", "F", "E", "E", "D",
#          "C", "C", "G", "G", "A", "A", "G",
#          "F", "F", "E", "E", "D", "D", "C"]

# durations = [1, 1, 1, 1, 1, 1, 2,
#              1, 1, 1, 1, 1, 1, 2,
#              1, 1, 1, 1, 1, 1, 2,
#              1, 1, 1, 1, 1, 1, 2,
#              1, 1, 1, 1, 1, 1, 2,
#              1, 1, 1, 1, 1, 1, 2]  # 以四分音符为单位

# x_speed = 1.5 # 速度倍数
# x_duration = 0.4 # 间隔倍数，如果小于1，就是减小时间间隔


# # 初始化电机的当前位置和方向标志
# current_loc_ref = 0
# direction_flag = 1  # 1表示正方向，-1表示反方向

# motor.disable() #
# motor.set_run_mode(motor.RunModes.POSITION_MODE)
# motor.set_motor_position_control(limit_spd=10, loc_ref=0)
# motor.set_0_pos()  # 当前0位
# motor.enable()

# # 播放小星星
# for note, duration in zip(notes, durations):
#     duration = duration * x_duration
    
#     # 计算电机的转速和目标位置
#     limit_spd = note_to_speed[note] * x_speed
#     loc_ref = current_loc_ref + (direction_flag * limit_spd * duration * 1.5)

#     # 使用电机参数设置函数
#     motor.set_motor_position_control(limit_spd=limit_spd, loc_ref=loc_ref)

#     # 更新电机的当前位置
#     current_loc_ref = loc_ref

#     # 反转方向标志
# #     direction_flag *= -1

#     # 休眠一段时间以模拟音符的时长（这里假设一个四分音符的时长是1秒）
#     time.sleep(duration * x_speed)
# motor.disable()


if __name__ == "__main__":
    from pcan_cybergear import CANMotorController
    import can
    import logging
    import time
    import os
    import sys
    import math
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # Initialize logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Connect to the CAN bus with 1 Mbit/s bitrate
    # bus = can.interface.Bus(interface="pcan", channel="PCAN_USBBUS1", bitrate=1000000)
    bus = can.interface.Bus(bustype='canalystii', channel=0, bitrate=1000000)#初始化CAN1通道用来发送

    mi_motor = CANMotorController(bus, motor_id=127, main_can_id=254)

    mi_motor.disable() #
    mi_motor.set_run_mode(mi_motor.RunModes.POSITION_MODE)

    mi_motor.enable() #
    # mi_motor.set_0_pos()  # 当前0位

    try:
        while True:
            mi_motor.set_motor_position_control(limit_spd=1, loc_ref=3.14)
            time.sleep(0.01)
            mi_motor.set_motor_position_control(limit_spd=1, loc_ref=0)
            time.sleep(0.01)
    except KeyboardInterrupt:
        mi_motor.disable() #

   