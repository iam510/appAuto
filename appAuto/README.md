# test.py 功能说明

## 主要功能
这个脚本用于自动检测手机屏幕上的UI元素，并点击置信度最高的目标。

## 函数说明

### capture_phone_screen(device_id: str = None)
- 功能：捕获手机屏幕截图
- 参数：device_id（可选，用于指定特定设备）
- 返回：临时图片的路径
- 说明：使用ADB命令获取手机截图，并保存为临时文件

### click_position(x: int, y: int, device_id: str = None)
- 功能：点击手机屏幕指定坐标
- 参数：x和y坐标，device_id（可选）
- 说明：使用ADB命令模拟点击操作

### process_single_detection(model, iteration: int)
- 功能：执行单次检测和点击操作
- 参数：模型对象和当前迭代次数
- 说明：包含截图、检测、保存结果图片和点击最高置信度目标的完整流程

### execute_detection_sequence(iterations: int = 3)
- 功能：执行多次检测和点击序列
- 参数：执行次数（默认3次）
- 返回：成功次数和总次数
- 说明：按指定次数重复执行检测和点击操作

### test_detection()
- 功能：测试函数，用于执行检测序列并显示结果统计
- 说明：默认执行3次检测，并显示成功率

## 使用说明
1. 确保手机已通过USB连接并开启ADB调试
2. 确保已安装所需的Python包
3. 运行脚本即可自动执行检测和点击操作