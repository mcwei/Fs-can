import can
import logging
import time
from cybergear.pcan_cybergear import CANMotorController
from fashionstar.fashionstar_CANservo import servo_control

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # bus = can.interface.Bus(interface="pcan", channel="PCAN_USBBUS1", bitrate=1000000)
    bus = can.interface.Bus(bustype='canalystii', channel=0, bitrate=1000000)#初始化CAN1通道用来发送
    
    # Initialize both motors
    mi_motor = CANMotorController(bus, motor_id=127, main_can_id=254)
    servo = servo_control(bus, is_logging=True)
    
    servo_id = 0x00 # 0x00 is the ID of the first servo

    # Setup MI motor
    mi_motor.disable()
    mi_motor.set_run_mode(mi_motor.RunModes.POSITION_MODE)
    mi_motor.enable()

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
    last_mi_time = time.time()
    loc_ref_value = 0
    angle_value = 20

    try:
        while True:
            current_time = time.time()
            
            # 每1毫秒发送MI电机控制命令
            if (current_time - last_mi_time) >= 0.001:  # 1毫秒
                # MI电机控制：移动到目标位置
                mi_motor.set_motor_position_control(limit_spd=1, loc_ref=loc_ref_value)
                last_mi_time = current_time
            
            # 每5000毫秒发送舵机控制命令
            if (current_time - last_servo_time) >= 5.0:  # 5000毫秒
                # 舵机控制：设置角度并读取
                servo.set_angle(servo_id, angle_value)
                time.sleep(0.001)
                # servo.read_angle(servo_id)
                # time.sleep(0.01)
                last_servo_time = current_time
                
                # 切换目标位置（可选）
                if loc_ref_value == 3.14:
                    loc_ref_value = 0
                    angle_value = 20
                else:
                    loc_ref_value = 3.14
                    angle_value = 90

            # 添加短暂延迟避免CPU过载
            time.sleep(0.0001)
            
    except KeyboardInterrupt:
        logging.info("Program terminated by user")
        mi_motor.disable()
        bus.shutdown()

if __name__ == "__main__":
    main()