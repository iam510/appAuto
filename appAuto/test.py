import cv2
import os
from ultralytics import YOLO
import subprocess
import time

def capture_phone_screen(device_id: str = None) -> str:
    """
    捕获手机屏幕并返回临时图片路径
    """
    try:
        adb_command = "adb"
        if device_id:
            adb_command += f" -s {device_id}"
            
        # 清理可能存在的旧文件
        subprocess.run([adb_command, "shell", "rm", "/sdcard/screen.png"])
        
        # 截图
        result = subprocess.run([adb_command, "shell", "screencap", "-p", "/sdcard/screen.png"], 
                             check=True, capture_output=True)
        if result.returncode != 0:
            raise Exception(f"截图失败: {result.stderr}")
        
        # 拉取文件到临时路径
        temp_path = "temp_screen.png"
        result = subprocess.run([adb_command, "pull", "/sdcard/screen.png", temp_path],
                             check=True, capture_output=True)
        if result.returncode != 0:
            raise Exception(f"拉取文件失败: {result.stderr}")
            
        return temp_path
        
    except Exception as e:
        print(f"获取手机截图失败: {str(e)}")
        return None

def click_position(x: int, y: int, device_id: str = None):
    """
    点击指定坐标
    """
    try:
        adb_command = "adb"
        if device_id:
            adb_command += f" -s {device_id}"
            
        subprocess.run([adb_command, "shell", "input", "tap", str(x), str(y)])
        print(f"点击坐标: ({x}, {y})")
        return True
    except Exception as e:
        print(f"点击失败: {str(e)}")
        return False

def process_single_detection(model, iteration: int):
    """
    执行单次检测和点击
    """
    print(f"\n开始第 {iteration} 次检测...")
    
    # 捕获手机屏幕
    temp_path = capture_phone_screen()
    if temp_path is None:
        print("截图失败，跳过本次检测")
        return False
        
    try:
        # 读取图片
        img = cv2.imread(temp_path)
        if img is None:
            print(f"无法读取图片: {temp_path}")
            return False
                
        # 运行检测
        results = model(img)
        
        # 找出置信度最高的检测框
        highest_conf = 0
        highest_conf_box = None
        
        # 在图片上绘制检测结果
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # 获取坐标和置信度
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                # 更新最高置信度的框
                if conf > highest_conf:
                    highest_conf = conf
                    highest_conf_box = (x1, y1, x2, y2)
                
                # 绘制边界框
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # 添加标签
                label = f"Type {cls} ({conf:.2f})"
                (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                cv2.rectangle(img, (x1, y1-label_h-10), (x1+label_w, y1), (0, 255, 0), -1)
                cv2.putText(img, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        # 保存带检测框的结果图片
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"detected_{iteration}_{timestamp}.png")
        cv2.imwrite(output_path, img)
        print(f"检测结果已保存: {output_path}")
        
        # 点击置信度最高的框的中心位置
        if highest_conf_box is not None:
            x1, y1, x2, y2 = highest_conf_box
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            print(f"点击置信度最高的目标 (置信度: {highest_conf:.2f})")
            click_position(center_x, center_y)
            print("等待2秒...")
            time.sleep(2)
            return True
        else:
            print("未检测到任何目标")
            return False
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)

def execute_detection_sequence(iterations: int = 3):
    """
    执行指定次数的检测和点击序列
    Args:
        iterations: 执行次数，默认为3次
    Returns:
        tuple: (成功次数, 总次数)
    """
    # 创建output文件夹
    global output_dir
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 加载模型
    model = YOLO("best.pt")
    
    # 执行指定次数的循环
    successful_detections = 0
    
    print(f"\n开始执行{iterations}次检测序列...")
    
    for i in range(iterations):
        if process_single_detection(model, i + 1):
            successful_detections += 1
    
    print(f"\n检测序列执行完成！")
    print(f"成功检测并点击: {successful_detections} 次")
    print(f"总尝试��数: {iterations} 次")
    
    return successful_detections, iterations

def test_detection():
    """
    测试函数，可以根据需要设置不同的执行次数
    """
    success_count, total_count = execute_detection_sequence(3)
    
    # 可以根据返回结果做更多处理
    if success_count == total_count:
        print("所有检测都成功完成！")
    else:
        print(f"部分检测未成功，成功率: {success_count/total_count*100:.1f}%")

if __name__ == "__main__":
    test_detection() 