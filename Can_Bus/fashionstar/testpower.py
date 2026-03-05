import fashionstar_CANservo
import can
import matplotlib.pyplot as plt
import numpy as np
import time

if __name__ == "__main__":

    # bus = can.interface.Bus(interface="pcan", channel="PCAN_USBBUS1", bitrate=1000000)
    bus = can.interface.Bus(bustype='canalystii', channel=0, bitrate=1000000)#初始化CAN1通道用来发送
    control = fashionstar_CANservo.servo_control(bus,is_logging = True)
    SERVO_ID = 0X00

    start_time = time.time()
    xpoints = [0]
    ypoints = [0]


    plt.ion()  # 开启交互模式
    fig, ax = plt.subplots()
    line, = ax.plot(xpoints, ypoints, 'b-')  # 创建蓝色实线
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('')
    ax.set_title('test')

    
    angle_value=10
    last_switch_time=0
    control.set_angle(SERVO_ID,angle_value)

    try:
        while(1):
            current_time = time.time() - start_time

            elapsed = current_time - last_switch_time
        
        # 每0.6秒切换一次角度
            if elapsed >= 2:
                angle_value = 90 if angle_value == 10 else 10
                control.set_angle(SERVO_ID, angle_value)
                last_switch_time = current_time  # 重置计时

            voltage = control.read_power(SERVO_ID) #修改Y轴数据源

            # 添加数据点
            xpoints.append(current_time)
            ypoints.append(voltage)
            
            # 更新图表数据
            line.set_xdata(xpoints)
            line.set_ydata(ypoints)
            
            # 自动调整坐标轴范围
            ax.relim()  # 重新计算数据范围
            ax.autoscale_view()  # 自动调整视图
            
            # 重绘图表
            fig.canvas.draw()
            fig.canvas.flush_events()
            
            # 控制采样频率（每秒10次）
            time.sleep(0.01)
        
    except KeyboardInterrupt:
        plt.ioff()
        plt.show()
