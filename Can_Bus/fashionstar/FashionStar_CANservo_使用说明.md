# FashionStar CAN总线舵机SDK使用说明

本文档介绍了`fashionstar_CANservo.py`SDK文件的使用方法，该驱动用于控制FashionStar系列CAN总线舵机。

## 目录

- [环境要求](#环境要求)
- [基本使用](#基本使用)
- [初始化](#初始化)
- [舵机控制功能](#舵机控制功能)
  - [基本控制](#基本控制)
  - [状态读取](#状态读取)
  - [参数设置](#参数设置)
  - [模式控制](#模式控制)
- [完整示例](#完整示例)
- [API参考](#api参考)

## 环境要求

使用本驱动需要安装以下Python库：

```bash
pip install python-can
```

同时，您需要确保系统已正确安装CAN总线适配器的驱动程序。

## 基本使用

### 导入模块

```python
from fashionstar.fashionstar_CANservo import servo_control
import can
import time
```

## 初始化

初始化CAN总线和舵机控制器：

```python
# 使用PCAN适配器
#windows系统
bus = can.interface.Bus(interface="pcan", channel="PCAN_USBBUS1", bitrate=1000000)
#linux系统
bus = can.interface.Bus(interface="socketcan", channel="can0", bitrate=1000000)

# 或使用CANalyst适配器
bus = can.interface.Bus(bustype='canalystii', channel=0, bitrate=500000)

# 初始化舵机控制器，is_logging=True开启日志输出
control = servo_control(bus, is_logging=True)

# 设置要控制的舵机ID
servo_id = 0x00
```

## 舵机控制功能

### 基本控制

#### 设置舵机角度

```python
# 设置舵机转到90度位置
control.set_angle(servo_id, 90)
```

#### 设置运动参数

```python
# 设置舵机运行速度（单位：rpm）
control.set_SERVO_TargetVelocity(servo_id, 100)

# 设置舵机运行时间（单位：ms）
control.set_SERVO_TargetInterval(servo_id, 1000)

# 设置舵机加减速时间（单位：ms）
control.set_SERVO_accel_decel_Time(servo_id, 20, 20)
```

### 状态读取

#### 读取舵机角度

```python
# 读取当前角度
angle = control.read_angle(servo_id)
print(f"当前角度: {angle}°")
```

#### 读取舵机状态

```python
# 读取电压（单位：V）
voltage = control.read_Voltage(servo_id)
print(f"当前电压: {voltage}V")

# 读取功率（单位：W）
power = control.read_power(servo_id)
print(f"当前功率: {power}W")

# 读取温度（单位：°C）
temperature = control.read_temperature(servo_id)
print(f"当前温度: {temperature}°C")

# 读取舵机状态寄存器
status = control.read_SERVO_status(servo_id)
print(f"舵机状态: {status}")
```

### 参数设置

#### 设置舵机ID

```python
# 将舵机ID从0x00修改为0x01
control.set_SERVO_ID(servo_id, 0x01)
```

#### 设置舵机波特率

```python
# 设置舵机波特率为1Mbps
control.set_SERVO_BaudRate(servo_id, "BaudRate_1Mbps")
```

#### 设置保护参数

```python
# 设置高压保护阈值（单位：V）
control.set_SERVO_OverVoltageProtect(servo_id, 12.6)

# 设置堵转保护阈值（单位：mW）
control.set_SERVO_StallPowerLimit(servo_id, 6000)

# 设置过载保护阈值（单位：mW）
control.set_SERVO_OverPowerProtect(servo_id, 6000)

# 设置功率保护迟滞百分比
control.set_SERVO_PowerProtectHyst(servo_id, 80)
```

#### 设置舵机零点

```python
# 设置当前位置为舵机零点（舵机须失能）
control.set_SERVO_zero(servo_id)
```

#### 重置多圈角度

```python
# 清除多圈圈数，规范为-180~+180度
control.reset_multi_turn(servo_id)
```

### 模式控制

#### 设置控制模式

```python
# 设置舵机控制模式（可选："Default", "ControlByTime", "ControlBySpeed"）
control.set_SERVO_ControlMode(servo_id, "Default")
```

#### 舵机锁定/解锁

```python
# 使舵机失锁（解除锁力）
control.unlock_SERVO(servo_id)

# 使舵机上锁（恢复锁力）
control.lock_SERVO(servo_id)
```

#### 阻尼模式

```python
# 设置阻尼模式及阻尼功率
control.damp_SERVO(servo_id, 500)
```

#### 检测舵机

```python
# 检测指定ID的舵机是否在线
is_online = control.ping(servo_id)
print(f"舵机在线状态: {is_online}")

# 检测总线上所有舵机（ID范围0-10）
control.ping()
```

## 完整示例

以下是一个完整的示例，展示了如何使用驱动控制舵机在两个位置之间来回移动：

```python
import can
import time
from fashionstar.fashionstar_CANservo import servo_control

# 初始化CAN总线
bus = can.interface.Bus(interface="pcan", channel="PCAN_USBBUS1", bitrate=1000000)

# 初始化舵机控制器
control = servo_control(bus, is_logging=True)
servo_id = 0x00

try:
    # 检测舵机是否在线
    if control.ping(servo_id):
        print("舵机连接成功！")
        
        # 设置舵机参数
        control.set_SERVO_TargetVelocity(servo_id, 100)  # 设置速度
        control.set_SERVO_accel_decel_Time(servo_id, 50, 50)  # 设置加减速时间
        
        # 循环控制舵机在两个位置之间移动
        for _ in range(5):
            # 移动到20度
            control.set_angle(servo_id, 20)
            print("移动到20度")
            
            # 读取状态
            control.read_power(servo_id)
            control.read_temperature(servo_id)
            time.sleep(2)
            
            # 移动到90度
            control.set_angle(servo_id, 90)
            print("移动到90度")
            
            # 读取状态
            control.read_power(servo_id)
            control.read_temperature(servo_id)
            time.sleep(2)
    else:
        print("舵机未连接，请检查连接和ID设置")

except KeyboardInterrupt:
    print("程序被用户终止")
finally:
    # 关闭CAN总线
    bus.shutdown()
```

## API参考

### servo_control类

#### 初始化

```python
servo_control(bus, is_logging=False)
```

- `bus`: CAN总线对象
- `is_logging`: 是否开启日志输出

#### 基本控制方法

| 方法 | 描述 | 参数 |
|------|------|------|
| `set_angle(servo_id, angle)` | 设置舵机目标角度 | `servo_id`: 舵机ID，整数<br>`angle`: 目标角度，浮点数，单位：度(°) |
| `set_SERVO_TargetInterval(servo_id, interval)` | 设置舵机运行时间(ms) | `servo_id`: 舵机ID，整数<br>`interval`: 运行时间，整数，单位：毫秒(ms) |
| `set_SERVO_TargetVelocity(servo_id, velocity)` | 设置舵机目标速度(rpm) | `servo_id`: 舵机ID，整数<br>`velocity`: 目标速度，整数，单位：转/分钟(rpm) |
| `set_SERVO_TargetPower(servo_id, power)` | 设置舵机执行功率(mw(TODO)) | `servo_id`: 舵机ID，整数<br>`power`: 执行功率，整数，范围：0-5000（TODO） |
| `set_SERVO_accel_decel_Time(servo_id, acc_time, dec_time)` | 设置加减速时间(ms) | `servo_id`: 舵机ID，整数<br>`acc_time`: 加速时间，整数，单位：毫秒(ms)，最小值：20ms<br>`dec_time`: 减速时间，整数，单位：毫秒(ms)，最小值：20ms |

#### 状态读取方法

| 方法 | 描述 | 参数 |
|------|------|------|
| `read_angle(servo_id)` | 读取舵机当前角度 | `servo_id`: 舵机ID，整数 |
| `read_Voltage(servo_id)` | 读取舵机电压 | `servo_id`: 舵机ID，整数 |
| `read_power(servo_id)` | 读取舵机功率 | `servo_id`: 舵机ID，整数 |
| `read_temperature(servo_id)` | 读取舵机温度 | `servo_id`: 舵机ID，整数 |
| `read_SERVO_status(servo_id)` | 读取舵机状态寄存器 | `servo_id`: 舵机ID，整数 |
| `ping(servo_id=None)` | 检测舵机是否在线 | `servo_id`: 舵机ID，整数，可选参数，默认为None（检测所有舵机） |

#### 参数设置方法

| 方法 | 描述 | 参数 |
|------|------|------|
| `set_SERVO_ID(servo_id, set_id)` | 设置舵机ID | `servo_id`: 当前舵机ID，整数<br>`set_id`: 要设置的新舵机ID，整数，范围：0-253 |
| `set_SERVO_BaudRate(servo_id, parameter)` | 设置舵机波特率 | `servo_id`: 舵机ID，整数<br>`parameter`: 波特率参数，字符串，可选值如下  <br/>`"BaudRate_50kbps"` <br/>`"BaudRate_100kbps"` <br/>`"BaudRate_125kbps"` <br/>`"BaudRate_200kbps"` <br/>`"BaudRate_250kbps"` <br/>`"BaudRate_400kbps"` <br/>`"BaudRate_500kbps"` <br/>`"BaudRate_750kbps"` <br/>`"BaudRate_800kbps"` <br/>`"BaudRate_1Mbps"<br/>` |
| `set_SERVO_zero(servo_id)` | 设置舵机零点 | `servo_id`: 舵机ID，整数 |
| `reset_multi_turn(servo_id)` | 重置多圈角度 | `servo_id`: 舵机ID，整数 |
| `set_SERVO_OverVoltageProtect(servo_id, parameter)` | 设置高压保护阈值(V) | `servo_id`: 舵机ID，整数<br>`parameter`: 高压保护阈值，浮点数，单位：伏特(V) |
| `set_SERVO_StallPowerLimit(servo_id, parameter)` | 设置堵转保护阈值(mW) | `servo_id`: 舵机ID，整数<br>`parameter`: 堵转保护阈值，整数，单位：毫瓦(mW) |
| `set_SERVO_OverPowerProtect(servo_id, parameter)` | 设置过载保护阈值(mW) | `servo_id`: 舵机ID，整数<br>`parameter`: 过载保护阈值，整数，单位：毫瓦(mW) |
| `set_SERVO_PowerProtectHyst(servo_id, parameter)` | 设置功率保护迟滞百分比 | `servo_id`: 舵机ID，整数<br>`parameter`: 功率保护迟滞百分比，整数，必须设置80 |

#### 模式控制方法

| 方法 | 描述 | 参数 |
|------|------|------|
| `set_SERVO_ControlMode(servo_id, mode)` | 设置控制模式 | `servo_id`: 舵机ID，整数<br>`mode`: 控制模式，字符串，可选值如下：<br/>  `"Default"`: 默认模式 <br/>`"ControlByTime"`: 按时间控制模式 <br/>`"ControlBySpeed"`: 按速度控制模式 |
| `unlock_SERVO(servo_id)` | 使舵机失锁 | `servo_id`: 舵机ID，整数 |
| `lock_SERVO(servo_id)` | 使舵机上锁 | `servo_id`: 舵机ID，整数 |
| `damp_SERVO(servo_id, power)` | 设置阻尼模式及功率 | `servo_id`: 舵机ID，整数<br>`power`: 阻尼功率，整数，范围：0-5000（TODO） |

