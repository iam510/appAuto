from app_detector import AppUIDetector
from action_controller import ActionController

def main():
    # 初始化检测器，使用较低的置信度阈值
    detector = AppUIDetector(conf_threshold=0.3)
    
    # 初始化控制器
    controller = ActionController(detector)
    
    # 定义要点击的元素类型序列
    target_sequence = [0, 1, 2]
    
    # 执行点击序列
    controller.run_sequence(target_sequence)

if __name__ == "__main__":
    main()