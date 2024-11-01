from app_detector import AppUIDetector
import time
from typing import Optional, Dict

class ActionController:
    def __init__(self, detector: AppUIDetector):
        self.detector = detector
        
    def find_and_click(self, target_type: int) -> bool:
        """
        查找并点击指定类型的元素
        Args:
            target_type: 目标元素类型ID
        Returns:
            bool: 是否成功点击
        """
        # 获取截图
        screenshot = self.detector.capture_phone_screen()
        if screenshot is None:
            print("获取截图失败")
            return False
            
        # 检测UI元素
        elements = self.detector.detect_ui_elements(screenshot)
        
        # 无论是否检测到元素，都保存检测结果的可视化图片
        self.detector.visualize_detection(screenshot, elements)
        
        if not elements:
            print(f"未检测到任何元素")
            return False
        
        # 查找目标元素
        element = next((e for e in elements if e['type'] == target_type), None)
        if element is None:
            print(f"未找到类型为 {target_type} 的元素")
            return False
            
        # 点击元素
        return self.detector.click_element(element)
        
    def run_sequence(self, target_types: list[int]):
        """
        按顺序执行一系列点击操作
        Args:
            target_types: 目标元素类型ID列表
        """
        for target_type in target_types:
            if self.detector.click_count >= self.detector.max_clicks:
                print("已达到最大点击次数限制，停止操作")
                break
                
            print(f"查找并点击类型 {target_type} 的元素")
            success = self.find_and_click(target_type)
            
            if not success:
                print(f"无法完成类型 {target_type} 的点击操作")