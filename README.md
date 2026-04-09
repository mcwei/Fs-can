# 达妙电机 & FashionStar CAN舵机 联合控制SDK使用说明
本文档介绍如何联合使用达妙（Damiao）电机控制SDK与FashionStar CAN总线舵机SDK，实现对两类设备的统一CAN总线控制，包含环境配置、初始化、基础控制及完整示例。

## 目录
- [环境要求](#环境要求)
- [核心依赖与模块导入](#核心依赖与模块导入)
- [CAN总线初始化](#can总线初始化)
- [设备初始化](#设备初始化)
  - [达妙电机初始化](#达妙电机初始化)
  - [FashionStar舵机初始化](#fashionstar舵机初始化)
- [设备控制功能](#设备控制功能)
  - [达妙电机控制](#达妙电机控制)
  - [FashionStar舵机控制](#fashionstar舵机控制)
- [联合控制完整示例](#联合控制完整示例)
- [注意事项](#注意事项)

## 环境要求
**基础依赖**

1. Python版本：推荐3.7及以上
2. 必装Python库：
   ```bash
   pip install python-can  # CAN总线基础库
   pip install math        # 数学计算（示例中正弦控制用到）
   pip install logging     # 日志输出（可选）
   ```
3. 硬件驱动：
   - 安装CAN总线适配器驱动（如PCAN-USB、CANalyst-II）
   - 确保达妙电机、FashionStar舵机均接入同一CAN总线，且终端电阻配置正确

**硬件兼容**

- CAN适配器：PCAN-USB（推荐）、CANalyst-II
- 达妙电机：支持DM4310等系列（需匹配对应Motor_Type）
- FashionStar舵机：全系列CAN总线舵机

## 核心依赖与模块导入
联合控制需同时导入达妙电机控制模块与FashionStar舵机模块，基础导入示例：
```python
import sys
import can
import logging
import time
import math

# 达妙电机模块
from damiao_motor.damiao_motor import Motor, MotorControl, DM_Motor_Type, Control_Type
# FashionStar舵机模块
from fashionstar.fashionstar_CANservo import servo_control
```

## CAN总线初始化
两类设备共享同一CAN总线对象，需优先完成总线初始化，以PCAN-USB为例：
```python
# 常量配置
CAN_BITRATE = 1000000  # 达妙电机默认1Mbps，FashionStar舵机可适配

try:
    bus = can.interface.Bus(
        interface="pcan",
        channel="PCAN_USBBUS1",  # 通道名根据实际适配器调整
        bitrate=CAN_BITRATE,
        receive_own_messages=False  # 禁止接收自身发送的消息
    )
    logging.info("✅ CAN总线初始化成功！")   
    # PCAN-USB初始化（Windows）
    #linux系统
    #bus = can.interface.Bus(interface="socketcan", channel="can0", bitrate=1000000)
    #或使用CANalyst适配器
    #bus = can.interface.Bus(bustype='canalystii', channel=0, bitrate=1000000)#初始化CAN1通道用来发送    


except Exception as e:
    print(f"❌ CAN总线初始化失败：{e}")
    sys.exit(1)
```

## 设备初始化
### 达妙电机初始化
1. 创建电机控制器实例
2. 添加电机并使能（支持多电机扩展）
```python
# 初始化达妙电机控制器
dm_control = MotorControl(canbus=bus)

# 配置电机参数（示例为1个DM4310电机）
NUM_MOTORS = 1
MOTOR_TYPE = DM_Motor_Type.DM4310  # 匹配实际电机型号
motors = []

# 添加并使能电机
for i in range(NUM_MOTORS):
    motor_id = i + 1               # 电机编号（自定义）
    can_id = i + 0X10              # 电机CAN ID（需与硬件匹配）
    motor = Motor(MOTOR_TYPE, motor_id, can_id)
    dm_control.addMotor(motor)
    dm_control.enable(motor)       # 使能电机
    motors.append(motor)
    print(f"✅ 达妙电机 {motor_id} 已使能")

time.sleep(1)  # 等待电机初始化完成
```

### FashionStar舵机初始化
1. 创建舵机控制器实例
2. 解锁舵机（解除锁力，可选）
```python
# 初始化FashionStar舵机控制器（开启日志）
servo = servo_control(bus, is_logging=True)
servo_id = 0x00  # 舵机ID（需与硬件匹配）

# 解锁舵机（解除锁力，允许转动）
servo.unlock_SERVO(servo_id)
time.sleep(0.5)
print(f"✅ FashionStar舵机 {servo_id} 已解锁")
```

## 设备控制功能
### 达妙电机控制
#### 位置+速度闭环控制（核心）
```python
# 控制电机到指定位置（弧度），并设置最大速度（rad/s）
position = 0.5  # 目标位置（弧度）
max_velocity = 20.0  # 最大速度
dm_control.control_Pos_Vel(motor, position, max_velocity)
```

#### 其他常用控制（参考达妙电机SDK）
- 禁用电机：`dm_control.disable(motor)`
- 批量禁用电机：`dm_control.disableAll()`
- 读取电机状态：`dm_control.read_motor_status(motor)`

### FashionStar舵机控制
#### 基础角度控制
```python
# 设置舵机目标角度（单位：度）
servo.set_angle(servo_id, 90)  # 转到90度

# 带速度/时间参数的角度控制（可选）
servo.set_SERVO_TargetVelocity(servo_id, 100)  # 设置速度100rpm
servo.set_SERVO_TargetInterval(servo_id, 1000) # 设置运行时间1000ms
```

#### 状态读取
```python
# 读取舵机当前角度
angle = servo.read_angle(servo_id)
print(f"舵机当前角度：{angle}°")

# 读取舵机电压/温度/功率
voltage = servo.read_Voltage(servo_id)
temperature = servo.read_temperature(servo_id)
power = servo.read_power(servo_id)
print(f"电压：{voltage}V | 温度：{temperature}°C | 功率：{power}mW")
```

#### 模式控制
```python
# 锁定/解锁舵机
servo.lock_SERVO(servo_id)    # 上锁（恢复锁力）
servo.unlock_SERVO(servo_id)  # 解锁（解除锁力）

# 设置阻尼模式
servo.damp_SERVO(servo_id, 500)  # 阻尼功率500mW
```

## 联合控制完整示例
实现达妙电机正弦波位置控制 + FashionStar舵机2秒周期角度切换：
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import can
import logging
import time
import math

# 导入驱动模块
from damiao_motor.damiao_motor import Motor, MotorControl, DM_Motor_Type
from fashionstar.fashionstar_CANservo import servo_control

# ======================== 配置项 ========================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
NUM_MOTORS = 1          # 达妙电机数量
CAN_BITRATE = 1000000   # CAN总线波特率
SERVO_ID = 0x00         # FashionStar舵机ID
FREQUENCY = 0.1         # 达妙电机正弦频率（Hz）
AMPLITUDE = 6           # 达妙电机正弦振幅（弧度）
DURATION = 600.0        # 运行时长（秒）

def main():
    bus = None
    dm_control = None
    servo = None

    # 1. 初始化CAN总线
    try:
        bus = can.interface.Bus(
            interface="pcan",
            channel="PCAN_USBBUS1",
            bitrate=CAN_BITRATE,
            receive_own_messages=False
        )
        logging.info("✅ CAN总线初始化成功")
    except Exception as e:
        logging.error(f"❌ CAN总线初始化失败：{e}")
        sys.exit(1)

    # 2. 初始化达妙电机
    try:
        dm_control = MotorControl(canbus=bus)
        motors = []
        for i in range(NUM_MOTORS):
            motor = Motor(DM_Motor_Type.DM4310, i + 1, i + 0X10)
            dm_control.addMotor(motor)
            dm_control.enable(motor)
            motors.append(motor)
            logging.info(f"✅ 达妙电机 {i+1} 已使能")
        time.sleep(1)
    except Exception as e:
        logging.error(f"❌ 达妙电机初始化失败：{e}")
        bus.shutdown()
        sys.exit(1)

    # 3. 初始化FashionStar舵机
    try:
        servo = servo_control(bus, is_logging=True)
        servo.unlock_SERVO(SERVO_ID)
        time.sleep(0.5)
        logging.info(f"✅ FashionStar舵机 {SERVO_ID} 已解锁")
    except Exception as e:
        logging.error(f"❌ FashionStar舵机初始化失败：{e}")
        dm_control.disableAll()
        bus.shutdown()
        sys.exit(1)

    # 4. 联合控制逻辑
    last_servo_time = time.time()
    last_dm_time = time.time()
    servo_angle = 0  # 舵机初始角度
    start_time = time.time()

    try:
        logging.info("✅ 开始联合控制（Ctrl+C 停止）")
        while (time.time() - start_time) < DURATION:
            current_time = time.time()

            # 达妙电机：1ms刷新一次正弦位置
            if (current_time - last_dm_time) >= 0.001:
                pos = AMPLITUDE * math.sin(2 * math.pi * FREQUENCY * (current_time - start_time))
                for motor in motors:
                    dm_control.control_Pos_Vel(motor, pos, 20.0)
                last_dm_time = current_time

            # FashionStar舵机：2秒切换一次角度（0° ↔ 150°）
            if (current_time - last_servo_time) >= 2.0:
                servo.set_angle(SERVO_ID, servo_angle)
                logging.info(f"📌 舵机角度更新为：{servo_angle}°")
                servo_angle = 150 if servo_angle == 0 else 0
                last_servo_time = current_time

            time.sleep(0.0001)  # 降低CPU占用

    except KeyboardInterrupt:
        logging.info("🛑 用户终止程序")
    except Exception as e:
        logging.error(f"❌ 控制循环异常：{e}")
    finally:
        # 5. 安全关闭
        logging.info("🔌 开始安全关闭设备...")
        if dm_control:
            dm_control.disableAll()  # 禁用所有达妙电机
        if servo:
            servo.lock_SERVO(SERVO_ID)  # 锁定舵机
        if bus:
            bus.shutdown()  # 关闭CAN总线
        logging.info("✅ 设备已安全关闭")

if __name__ == "__main__":
    main()
```

## 注意事项
1. **CAN总线波特率统一**：
   - 达妙电机默认1Mbps，FashionStar舵机需通过`set_SERVO_BaudRate`设置为相同波特率，避免通信异常。
   - 若使用CANalyst-II，需确认适配器波特率与设备一致。

2. **设备ID冲突**：
   - 达妙电机与FashionStar舵机的CAN ID需错开（如电机用0x10 - 0x1F，舵机用0x00 - 0x0F），避免指令冲突。

3. **时序控制**：
   - 电机/舵机控制指令发送间隔建议≥1ms，避免CAN总线拥塞。
   - 舵机解锁/上锁后需等待500ms以上，再发送角度指令。

4. **异常处理**：
   - 必须在`finally`块中执行设备禁用、CAN总线关闭操作，防止硬件损坏。
   - 可通过`servo.ping(servo_id)`检测舵机在线状态，`dm_control.read_motor_status`检测电机状态。

5. **功率保护**：
   - 舵机需提前设置过载/堵转保护阈值（参考FashionStar SDK的`set_SERVO_OverPowerProtect`）。
   - 达妙电机需根据负载调整最大速度/电流，避免过载。