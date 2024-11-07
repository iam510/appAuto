import cv2
import os
from ultralytics import YOLO
import time
import numpy as np
import controller

def compare_screenshots(img1: np.ndarray, img2: np.ndarray, threshold: float = 0.95) -> bool:
    """
    比较两个截图是否相似
    Args:
        img1: 第一个截图
        img2: 第二个截图
        threshold: 相似度阈值
    Returns:
        bool: 是否相似
    """
    try:
        # 确保两个图片尺寸相同
        if img1.shape != img2.shape:
            return False
        
        # 计算图片相似度
        similarity = cv2.matchTemplate(img1, img2, cv2.TM_CCOEFF_NORMED)[0][0]
        return similarity >= threshold
        
    except Exception as e:
        print(f"比较截图失败: {str(e)}")
        return False

def ensure_back_to_initial_page(initial_img: np.ndarray, device_id: str = None, max_attempts: int = 5):
    """
    确保返回到初始页面
    Args:
        initial_img: 初始页面的截图
        device_id: 设备ID
        max_attempts: 最大尝试次数
    Returns:
        bool: 是否成功返回初始页面
    """
    for i in range(max_attempts):
        # 获取当前页面截图
        current_screenshot_data = controller.capture_phone_screen(device_id)
        if current_screenshot_data is None:
            continue
            
        # 转换为numpy数组
        nparr = np.frombuffer(current_screenshot_data, np.uint8)
        current_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if current_img is None:
            continue
        
        # 比较当前页面与初始页面
        if compare_screenshots(initial_img, current_img):
            print("已返回初始页面")
            return True
            
        # 如果不相同，执行返回操作
        print(f"第 {i+1} 次尝试返回...")
        controller.press_back(device_id)
        time.sleep(1)
    
    print(f"未能在 {max_attempts} 次尝试内返回初始页面")
    return False

def test_detection():
    """
    按置信度顺序点击检测到的所有目标
    """
    try:
        # 创建output文件夹
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 加载模型
        model = YOLO("best.pt")
        
        # 捕获初始页面截图
        initial_screenshot_data = controller.capture_phone_screen()
        if initial_screenshot_data is None:
            print("截图失败，退出检测")
            return
            
        # 将初始截图数据转换为numpy数组
        initial_nparr = np.frombuffer(initial_screenshot_data, np.uint8)
        initial_img = cv2.imdecode(initial_nparr, cv2.IMREAD_COLOR)
        if initial_img is None:
            print("无法解析截图数据")
            return
                
        # 运行检测
        results = model(initial_img)
        
        # 存储所有检测结果
        detected_objects = []
        
        # 在图片上绘制检测结果
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # 获取坐标和置信度
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                # 存储检测结果
                detected_objects.append({
                    'position': (x1, y1, x2, y2),
                    'confidence': conf,
                    'class': cls
                })
                
                # 绘制边界框
                cv2.rectangle(initial_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # 添加标签
                label = f"Type {cls} ({conf:.2f})"
                (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                cv2.rectangle(initial_img, (x1, y1-label_h-10), (x1+label_w, y1), (0, 255, 0), -1)
                cv2.putText(initial_img, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        if detected_objects:
            # 只在检测到目标时保存结果图片
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"detected_{timestamp}.png")
            cv2.imwrite(output_path, initial_img)
            print(f"检测结果已保存: {output_path}")
            
            # 按置信度排序
            detected_objects.sort(key=lambda x: x['confidence'], reverse=True)
            
            # 依次点击每个目标
            for i, obj in enumerate(detected_objects, 1):
                x1, y1, x2, y2 = obj['position']
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                
                print(f"\n点击第 {i} 个目标 (置信度: {obj['confidence']:.2f})")
                controller.click_position(center_x, center_y)
                print("等待2秒...")
                time.sleep(2)
                
                # 执行返回主页操作
                controller.press_home()
                print("等待2秒...")
                time.sleep(2)
            
            print(f"\n完成所有目标的点击操作！")
            print(f"共点击了 {len(detected_objects)} 个目标")
        else:
            print("未检测到任何目标")
            
    except Exception as e:
        print(f"检测过程发生错误: {str(e)}")

if __name__ == "__main__":
    test_detection() 