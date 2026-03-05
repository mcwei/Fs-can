import can
import logging
import time
import math

CAN_ID = 0x321
PING_MAX_ID = 10
CONTROL_DELAY = 0.002

class fashionstar_servo:

    CONTROL_TABLE = {
        "Default": 0x00,
        "ControlByTime": 0x01,
        "ControlBySpeed": 0x02,
    }

    BAUDRATE_TABLE = {
        "BaudRate_50kbps" : 0x00,
        "BaudRate_100kbps": 0x01,
        "BaudRate_125kbps": 0x02,
        "BaudRate_200kbps": 0x03,
        "BaudRate_250kbps": 0x04,
        "BaudRate_400kbps": 0x05,
        "BaudRate_500kbps": 0x06,
        "BaudRate_750kbps": 0x07,
        "BaudRate_800kbps": 0x08,
        "BaudRate_1Mbps": 0x09,

    }

    ADDRESS_TABLE = {
        # ==== 身份参数 ====
        "SERVO_Model": 0x01,              # 舵机型号 (只读)
        "SERVO_FirmwareVersion": 0x02,     # 固件版本 (只读)
        "SERVO_SerialNoLow": 0x03,         # 舵机序号低字节 (只读)
        "SERVO_SerialNoHigh": 0x04,        # 舵机序号高字节 (只读)
        
        # ==== 状态监测 ====
        "SERVO_Voltage": 0x10,             # 舵机当前电压 (mV)
        "SERVO_Current": 0x11,             # 舵机当前电流 (mA)
        "SERVO_Power": 0x12,               # 舵机当前功率 (mW)
        "SERVO_Temperature": 0x13,         # 舵机温度 (°C)
        "SERVO_Status": 0x14,              # 舵机状态寄存器
        "SERVO_MultiTurnAngleLow": 0x15,   # 多圈模式当前角度低字节 (0.1°)
        "SERVO_MultiTurnAngleHigh": 0x16,  # 多圈模式当前角度高字节 (0.1°)
        "SERVO_TurnCount": 0x17,           # 累计旋转圈数
        "SERVO_SingleTurnAngle": 0x18,     # 单圈模式当前角度 (0.1°)
        
        # ==== 运动控制 ====
        "SERVO_DampingPower": 0x28,        # 阻尼模式功率设置 (设置后进入阻尼模式)
        "SERVO_TargetIntervalLow": 0x50,       # 到目标角度时间低字节 (ms)
        "SERVO_TargetIntervalHigh": 0x51,      # 到目标角度时间高字节 (ms)
        "SERVO_ControlModeFlag": 0x52,       # 角度模式切换标志 (0:默认 1:加减速 2:速度)
        "SERVO_TargetAngleLow": 0x53,      # 目标角度低字节 (0.1°)
        "SERVO_TargetAngleHigh": 0x54,     # 目标角度高字节 (0.1°)
        "SERVO_TargetPower": 0x55,          # 角度模式执行功率 (0-1000)
        "SERVO_AccelTime": 0x56,           # 启动加速段时间 (ms)
        "SERVO_DecelTime": 0x57,           # 接近目标减速段时间 (ms)
        "SERVO_TargeetVelocity": 0x58,         # 最大运动速度 (rpm)
        "SERVO_ExecuteMovement": 0x59,     # 执行角度运动 (0:停止 1:执行80-88位置命令)
        
        # ==== 系统控制 ====
        "SERVO_AsyncCommandFlag": 0x64,    # 异步命令标志 (0:清除缓存 1:开始 2:执行)
        "SERVO_UserDataReset": 0x78,       # 用户数据重置标志 (写任意值恢复出厂设置)
        "SERVO_MultiTurnReset": 0x79,      # 多圈角度重置标志 (1:重置多圈角度)
        "SERVO_OriginSetting": 0x7A,       # 原点设置标志 (0:设当前位置为0°)
        "SERVO_StopMode": 0x7B,            # 停止模式 (0x10:卸力 0x11:保持 0x12:阻尼)
        
        # ==== 配置参数 ====
        "SERVO_ResponseConfig": 0x80,      # 控制响应级别设置
        "SERVO_ID": 0x81,                  # 舵机ID设置 (0-253)
        "SERVO_BaudRate": 0x82,            # 串口波特率 (bps)
        "SERVO_StallProtection": 0x83,     # 堵转保护功能开关
        "SERVO_StallPowerLimit": 0x84,     # 堵转功率上限 (mW)
        "SERVO_UnderVoltageProtect": 0x85, # 低压保护阈值 (mV)
        "SERVO_OverVoltageProtect": 0x86,  # 高压保护阈值 (mV)
        "SERVO_TempProtection": 0x87,      # 温度保护阈值 (°C)
        "SERVO_OverPowerProtect": 0x88,    # 功率保护阈值 (mW)
        "SERVO_CurrentProtection": 0x89,   # 电流保护阈值 (mA)
        "SERVO_Acceleration": 0x8A,        # 加速度参数 (rpm/s)      
        "SERVO_PowerProtectHyst": 0x8B,    # 功率保护迟滞参数
        "SERVO_PowerOnLock": 0x8C,         # 上电锁力开关 (0:关 1:开)
        "SERVO_WheelModeBrake": 0x8D,      # 轮式模式刹车开关
        "SERVO_AngleLimitEnable": 0x8E,    # 角度限制开关 (0:关 1:开)
        "SERVO_SoftStartEnable": 0x8F,     # 上电缓启动开关
        "SERVO_SoftStartTime": 0x90,       # 缓启动S时间 (ms)
        "SERVO_AngleUpperLimit": 0x91,     # 角度上限 (0.1°)
        "SERVO_AngleLowerLimit": 0x92,     # 角度下限 (0.1°)
        "SERVO_MidpointOffset": 0x93,      # 机械中点偏移量 (0.1°)
        
        # ==== PID控制参数 ====
        "SERVO_Kp": 0xC8,                  # 比例增益 (位置环)
        "SERVO_Kd": 0xC9,                  # 微分增益 (位置环)
        "SERVO_Ki": 0xCA,                  # 积分增益 (位置环)
        "SERVO_PwmBias": 0xCB,             # PWM偏置补偿
        "SERVO_HoldKp": 0xCC,              # 保持状态比例增益
        "SERVO_HoldKd": 0xCD,              # 保持状态微分增益
        "SERVO_HoldPwmBias": 0xCE,         # 保持状态PWM偏置
        "SERVO_FullDegrees": 0xCF,         # 单圈全行程角度 (通常3600=360°)
        "SERVO_PwmLimit": 0xD0,            # PWM输出限制 (0-100%)
        "SERVO_NegativeDirection": 0xD1,   # 反向转动映射设置
        "SERVO_PwmFrequency": 0xD2,        # PWM频率 (Hz)
        "SERVO_DeadBand": 0xD3,            # 死区控制范围
        "SERVO_MotorDirection": 0xD4,      # 电机方向映射 (0:正常 1:反向)
        "SERVO_VersionInfo": 0xD5          # 参数表版本信息
    }
    def __init__(self,bus):
        self.canbus = bus
      

    def _send_message(self,data):
        msg =can.Message(is_extended_id=False,arbitration_id=CAN_ID,data=data,is_remote_frame = False)
        self.canbus.send(msg)

    def clear_rx(self,timeout=0.001):
        while(1):
            received_msg = self.canbus.recv(timeout)
            if received_msg is None:
                break

    def _reveive_single_message(self,servo_id,address,timeout=0.01):
        data = bytearray()
        _received_msg = None
        t_start = time.time() # 获取开始时间

        while(1):
            _received_msg = self.canbus.recv(0.001)
            if _received_msg:
                data.extend(_received_msg.data)                
                if len(data) >=5 :
                    
                    if data[0] != ord('v') or data[1] != servo_id or data[2] != address:
                        return None
                    else :
                        msg = data[3]|data[4]<<8
                        # print(data)
                        return msg
                
                elif time.time()-t_start > timeout:
                    return None
            else :
                if time.time()-t_start > timeout:
                    return None
                
    def _reveive_multiple_message(self,servo_id,address1,address2,timeout=0.01):
        data = bytearray()
        _received_msg = None
        t_start = time.time() # 获取开始时间

        while(1):
            _received_msg = self.canbus.recv(0.001)
            if _received_msg:
                data.extend(_received_msg.data)                
                if len(data) >=8 :
                    
                    if data[0] != ord('V') or data[1] != servo_id or data[2] != address1 or data[5] != address2:
                        return None
                    else :
                        msg = data[3]|data[4]<<8|data[6]<<16|data[7]<<24
                        if msg & 0x80000000:
                            msg = msg - 0x100000000
                        return msg
                    
                elif time.time()-t_start > timeout:
                    return None
            else :
                if time.time()-t_start > timeout:
                    return None


    def read_single_parameter(self,servo_id ,address):
        data = bytearray(8) 
        data[0] = ord('r')
        data[1] = servo_id
        data[2] = self.ADDRESS_TABLE[address]

        self.clear_rx()
        self._send_message(data)     
        return self._reveive_single_message(servo_id,self.ADDRESS_TABLE[address]) 

    def read_multiple_parameter(self,servo_id,address1,address2):
        data = bytearray(8)

        data[0] = ord('R')
        data[1] = servo_id
        data[2] = self.ADDRESS_TABLE[address1]       
        data[3] = self.ADDRESS_TABLE[address2]

        self.clear_rx()
        self._send_message(data) 
        return self._reveive_multiple_message(servo_id,address1=self.ADDRESS_TABLE[address1],address2=self.ADDRESS_TABLE[address2]) 


    def write_single_parameter(self,servo_id,address,parameter):
        data = bytearray(8) 
        data[0] = ord('w')
        data[1] = servo_id
        data[2] = self.ADDRESS_TABLE[address]
        data[3] = parameter & 0xFF
        data[4] = (parameter >> 8) & 0xFF
        self._send_message(data)
        time.sleep(CONTROL_DELAY)

    def write_multiple_parameter(self,servo_id,address1,parameter1,address2,parameter2):
        data = bytearray(8) 
        data[0] = ord('W')
        data[1] = servo_id

        data[2] = self.ADDRESS_TABLE[address1]
        data[3] = parameter1 & 0xFF
        data[4] = (parameter1 >> 8) & 0xFF

        data[5] = self.ADDRESS_TABLE[address2]
        data[6] = parameter2 & 0xFF
        data[7] = (parameter2 >> 8) & 0xFF
        self._send_message(data)
        time.sleep(CONTROL_DELAY)

        

class servo_control:   

    def __init__(self,bus,is_logging = False):
        self.servo = fashionstar_servo(bus)

        #debug
        self.is_logging = is_logging
        if self.is_logging:
            logging.basicConfig(
            level=logging.INFO,  # 设置日志级别
            format='[fashionstar_servo] %(asctime)s - %(levelname)s - %(message)s',  # 日志格式
            datefmt='%H:%M:%S' ) # 时间格式
            self._logging("servo_control_init")


    def _logging(self,message):
        if self.is_logging:
            logging.info(message)

    def read_Voltage(self,servo_id):
        Voltage = self.servo.read_single_parameter(servo_id,"SERVO_Voltage")
        if Voltage is not None:
            Voltage = Voltage *0.001
        else:
            self._logging("servo[%d],read voltage failed" % servo_id)
            return None

        if  Voltage is not None:
            self._logging("servo[%d],voltage:%.1fV" % (servo_id,Voltage))
        else:
            self._logging("read voltage failed")
        return Voltage
    def read_SERVO_status(self,servo_id):
        status = self.servo.read_single_parameter(servo_id,"SERVO_Status")

        if  status is not None:
            
            self._logging("servo[%d],status: %d " % (servo_id,status))
        else:
            self._logging("read voltage failed")
        return status    

    def read_angle(self,servo_id):
        angle = self.servo.read_multiple_parameter(servo_id,"SERVO_MultiTurnAngleLow","SERVO_MultiTurnAngleHigh")
        if angle is not None:
            angle = angle *0.1
        else:
            self._logging("servo[%d],read angle failed" % servo_id)
            return None


        if angle is not None:
            self._logging("servo[%d],current angle: %.1f°" % (servo_id,angle))
        else:
            self._logging("servo[%d],read angle failed" % servo_id)
        return angle
    
    def read_power(self,servo_id):
        power = self.servo.read_single_parameter(servo_id,"SERVO_Power")
        if power is not None:
            power = power *0.001
        else:
            self._logging("servo[%d],read power failed" % servo_id)
            return None


        if power is not None:
            self._logging("servo[%d],power: %.1fW" % (servo_id,power))
        else:
            self._logging("servo[%d],read power failed" % servo_id)
        return power   

    def read_temperature(self,servo_id):
        raw_value  = self.servo.read_single_parameter(servo_id,"SERVO_Temperature")
        if raw_value  is not None:
            temperature = float(1/((math.log(10000*raw_value/(10000*(4096-raw_value)))/3435)+1/(273.15+25))-273.15)
        else:
            self._logging("servo[%d],read temperature failed" % servo_id)
            return None

        if  temperature is not None:
            self._logging("servo[%d],temperature:%.1f°C" % (servo_id,temperature))
        else:
            self._logging("read temperature failed")
        return temperature
    
    def set_angle(self,servo_id,angle):
        _angle = int(angle*10)
        _param1 = (_angle) & 0xFFFF
        _param2 = (_angle>>16) & 0xFFFF
        self._logging("servo[%d],move to angle %.1f°" % (servo_id,angle))
        self.servo.write_multiple_parameter(servo_id,"SERVO_TargetAngleLow",_param1,"SERVO_TargetAngleHigh",_param2)
        self.servo.write_single_parameter(servo_id,"SERVO_ExecuteMovement",1)

    def set_SERVO_TargetInterval(self,servo_id,Interval):
        Interval = int(Interval)
        _param1 = (Interval) & 0xFFFF
        _param2 = (Interval>>16) & 0xFFFF

        self.servo.write_multiple_parameter(servo_id,"SERVO_TargetIntervalLow",_param1,"SERVO_TargetIntervalHigh",_param2)

    def set_SERVO_TargetPower(self,servo_id,power):
        self.servo.write_single_parameter(servo_id,"SERVO_TargetPower",int(power))

    def set_SERVO_TargetVelocity(self,servo_id,Velocity):
        #单位
        self.servo.write_single_parameter(servo_id,"SERVO_TargeetVelocity",int(Velocity))
    def set_SERVO_StallPowerLimit(self,servo_id,parameter):
        self.servo.write_single_parameter(servo_id,"SERVO_StallPowerLimit",int(parameter))

    def set_SERVO_OverPowerProtect(self,servo_id,parameter):
        self.servo.write_single_parameter(servo_id,"SERVO_OverPowerProtect",int(parameter))

    def set_SERVO_PowerProtectHyst(self,servo_id,parameter):
        self.servo.write_single_parameter(servo_id,"SERVO_PowerProtectHyst",int(parameter))

    # 设置高压保护阈值 (mV),通常情况下请设置12.6V
    def set_SERVO_OverVoltageProtect(self,servo_id,parameter):
        self.servo.write_single_parameter(servo_id,"SERVO_OverVoltageProtect",int(parameter*1000))
        self._logging("servo[%d], set OverVoltageProtect to %.1f" % (servo_id,parameter))
    
    def set_SERVO_BaudRate(self,servo_id,parameter):
        self.servo.write_single_parameter(servo_id,"SERVO_BaudRate", self.servo.BAUDRATE_TABLE[parameter])

    #重新设置舵机零点(舵机须失能)
    def set_SERVO_zero(self,servo_id):
        self.servo.write_single_parameter(servo_id,"SERVO_OriginSetting",0)

    #清除多圈圈数，规范为-180~+180度
    def reset_multi_turn(self,servo_id):
        self.servo.write_single_parameter(servo_id,"SERVO_MultiTurnReset",1)

    #ping舵机 servo_id = None时ping总线上所有舵机。
    def ping(self,servo_id = None):
        if servo_id is None:
            for i in range(PING_MAX_ID+1):
                id = self.servo.read_single_parameter(i,"SERVO_ID")
                if id is not None:
                    self._logging("servo[%d], ping success" % (id))
        else:
            id = self.servo.read_single_parameter(servo_id,"SERVO_ID")
            if id is not None:
                self._logging("servo[%d], ping success" % (servo_id))
                return True
            else:
                self._logging("servo[%d], ping failed" % (servo_id))
                return False
            
    def set_SERVO_ID(self,servo_id,set_id):
        self.servo.write_single_parameter(servo_id,"SERVO_ID",int(set_id))

    def set_SERVO_ControlMode(self,servo_id,mode):
        self.servo.write_single_parameter(servo_id,"SERVO_ControlModeFlag",self.servo.CONTROL_TABLE[mode])
    
    def set_SERVO_accel_decel_Time(self,servo_id,acc_time,dec_time):
        if acc_time <20:
            acc_time = 20
        if dec_time <20:
            dec_time = 20

        self.servo.write_single_parameter(servo_id,"SERVO_AccelTime",int(acc_time))
        self.servo.write_single_parameter(servo_id,"SERVO_DecelTime",int(dec_time))

    #使舵机失锁，后续给任意控制命令恢复锁力。
    def unlock_SERVO(self,servo_id):
        self.servo.write_single_parameter(servo_id,"SERVO_StopMode",0x10)

    def lock_SERVO(self,servo_id):
        self.servo.write_single_parameter(servo_id,"SERVO_StopMode",0x11)

    def damp_SERVO(self,servo_id,power):
        self.servo.write_single_parameter(servo_id,"SERVO_DampingPower",int(power))

if __name__ == "__main__":
    bus = can.interface.Bus(interface="pcan", channel="PCAN_USBBUS1", bitrate=1000000)
    # bus = can.interface.Bus(bustype='canalystii', channel=0, bitrate=500000)
    control = servo_control(bus,is_logging = True)
    servo_id = 0x00 #舵机ID

    # control.set_SERVO_ID(servo_id,0x01)                               #设置舵机ID
    # control.set_SERVO_BaudRate(servo_id,9)ERVO_BaudRate(servo_id,9)   #设置舵机波特率
    # control.set_SERVO_OverVoltageProtect(servo_id,12.6)               #设置高压保护阈值 (mV),通常情况下请设置12.6V
    # control.set_SERVO_zero(servo_id)                                  #设置舵机零点
    # control.set_SERVO_TargetPower(servo_id,0)                         #设置舵机执行功率大小，0为默认
    # control.set_angle(servo_id,90)                                    #设置舵机目标角度
    # control.read_angle(servo_id)                                      #读取舵机当前角度
    # control.set_SERVO_TargetVelocity(servo_id,100)                    #设置舵机目标运行速度
    # control.set_SERVO_TargetInterval(servo_id,1000)                   #设置舵机目标运行时间
    # control.set_SERVO_StallPowerLimit(servo_id,4000)                  #设置堵转保护阈值
    # control.set_SERVO_OverPowerProtect(servo_id,4000)                 #设置过载保护阈值
    # control.set_SERVO_ControlMode(servo_id,"Default")                 #设置舵机控制模式
    # control.set_SERVO_accel_decel_Time(servo_id,20,20)                #设置舵机加减速时间
    # control.unlock_SERVO(servo_id)                                    #使舵机失锁，后续给任意控制命令恢复锁力。
    # control.lock_SERVO(servo_id)                                      #使舵机上锁，后续给任意控制命令恢复失锁状态。
    # control.damp_SERVO(servo_id,100)                                  #设置阻尼模式
    # control.ping()                                                    #ping舵机
    # control.read_power(servo_id)                                      #读取舵机当前功率
    # control.set_SERVO_PowerProtectHyst(servo_id,80)                   #设置迟滞百分比
    # control.read_temperature(servo_id)                                #读取舵机温度
    time.sleep(2)
    try:
        while True:
            control.set_angle(servo_id,20)
            control.read_power(servo_id)
            control.read_temperature(servo_id)
            time.sleep(5)

            control.set_angle(servo_id,90)
            control.read_power(servo_id)
            control.read_temperature(servo_id)
            time.sleep(5)


    except KeyboardInterrupt:
        logging.info("Program terminated by user")
        # Cleanup
        bus.shutdown()