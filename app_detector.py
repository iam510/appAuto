import cv2
import numpy as np
from ultralytics import YOLO
import pyautogui
from typing import List, Dict, Optional
import time
import subprocess
import os

class AppUIDetector:
    def __init__(self, model_path: str = "best.pt", conf_threshold: float = 0.3):
        """
        初始化UI检测器
        Args:
            model_path: YOLO模型路径
            conf_threshold: 置信度阈值
        """
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.click_count = 0
        self.max_clicks = 5
        
        # 创建imgs文件夹
        self.img_dir = "imgs"
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)
    
    def capture_phone_screen(self, device_id: str = None) -> np.ndarray:
        """
        捕获手机屏幕并保存
        """
        try:
            adb_command = "adb"
            if device_id:
                adb_command += f" -s {device_id}"
            
            # 添加重试机制
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # 清理可能存在的旧文件
                    subprocess.run([adb_command, "shell", "rm", "/sdcard/screen.png"])
                    
                    # 截图
                    result = subprocess.run([adb_command, "shell", "screencap", "-p", "/sdcard/screen.png"], 
                                         check=True, capture_output=True)
                    if result.returncode != 0:
                        raise Exception(f"截图失败: {result.stderr}")
                    
                    # 拉取文件
                    result = subprocess.run([adb_command, "pull", "/sdcard/screen.png", "temp_screen.png"],
                                         check=True, capture_output=True)
                    if result.returncode != 0:
                        raise Exception(f"拉取文件失败: {result.stderr}")
                    
                    # 读取截图
                    screenshot = cv2.imread("temp_screen.png")
                    if screenshot is None or screenshot.size == 0:
                        raise Exception("读取截图失败")
                    
                    # 检查图片尺寸
                    if screenshot.shape[0] < 100 or screenshot.shape[1] < 100:
                        raise Exception(f"截图尺寸异常: {screenshot.shape}")
                    
                    # 保存截图到imgs文件夹
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    img_name = f"screenshot_{self.click_count+1}_{timestamp}.png"
                    img_path = os.path.join(self.img_dir, img_name)
                    cv2.imwrite(img_path, screenshot)
                    print(f"截图已保存: {img_path}")
                    print(f"截图尺寸: {screenshot.shape}")
                    
                    # 删除临时文件
                    if os.path.exists("temp_screen.png"):
                        os.remove("temp_screen.png")
                        
                    return screenshot
                    
                except Exception as e:
                    print(f"第 {attempt+1} 次尝试失败: {str(e)}")
                    if attempt < max_retries - 1:
                        print("等待1秒后重试...")
                        time.sleep(1)
                    else:
                        raise Exception(f"截图失败，已重试 {max_retries} 次")
                        
        except Exception as e:
            print(f"获取手机截图失败: {str(e)}")
            return None

    def click_element(self, element: Dict) -> bool:
        """
        点击UI元素
        """
        if self.click_count >= self.max_clicks:
            print("已达到最大点击次数限制！")
            return False
            
        try:
            x1, y1, x2, y2 = element['position']
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            
            print(f"点击坐标: ({center_x}, {center_y})")
            print(f"元素类型: {element['type']}")
            print(f"置信度: {element['confidence']:.4f}")
            
            subprocess.run(["adb", "shell", "input", "tap", str(center_x), str(center_y)])
            
            self.click_count += 1
            print(f"点击成功！剩余点击次数：{self.max_clicks - self.click_count}")
            
            print("等待2秒...")
            time.sleep(2)
            return True
        except Exception as e:
            print(f"点击失败，详细错误: {str(e)}")
            return False

    def detect_ui_elements(self, screenshot: Optional[np.ndarray] = None) -> List[Dict]:
        """
        检测UI元素
        """
        if screenshot is None:
            screenshot = self.capture_phone_screen()
            if screenshot is None:
                return []
        
        # 调整图像尺寸为32的倍数
        h, w = screenshot.shape[:2]
        new_h = (h // 32) * 32
        new_w = (w // 32) * 32
        resized = cv2.resize(screenshot, (new_w, new_h))
        
        results = self.model(resized)
        return self._parse_results(results)
        
    def _parse_results(self, results) -> List[Dict]:
        """
        解析检测结果
        """
        elements = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                if conf < self.conf_threshold:
                    continue
                    
                x1, y1, x2, y2 = map(float, box.xyxy[0])
                
                elements.append({
                    'type': cls,
                    'position': (x1, y1, x2, y2),
                    'confidence': conf
                })
                
        return elements

    def find_element_by_type(self, element_type: int) -> Optional[Dict]:
        """
        查找指定类型的UI元素
        Args:
            element_type: 元素类型ID
        Returns:
            Optional[Dict]: 找到的元素信息或None
        """
        elements = self.detect_ui_elements()
        for element in elements:
            if element['type'] == element_type:
                return element
        return None

    def visualize_detection(self, screenshot: np.ndarray, elements: List[Dict]) -> np.ndarray:
        """
        可视化检测结果并保存
        Args:
            screenshot: 原始截图
            elements: 检测到的元素列表
        Returns:
            np.ndarray: 标注后的图像
        """
        img = screenshot.copy()
        for element in elements:
            x1, y1, x2, y2 = map(int, element['position'])
            conf = element['confidence']
            cls = element['type']
            
            # 使用不同颜色的边界框
            color = (0, 255, 0)  # 绿色
            
            # 绘制边界框
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            
            # 添加更清晰的标签背景
            label = f"Type {cls} ({conf:.2f})"
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(img, (x1, y1-label_h-10), (x1+label_w, y1), color, -1)
            cv2.putText(img, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        # 保存检测结果图片
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        img_name = f"detected_{self.click_count+1}_{timestamp}.png"
        img_path = os.path.join(self.img_dir, img_name)
        cv2.imwrite(img_path, img)
        print(f"检测结果已保存: {img_path}")
            
        return img 