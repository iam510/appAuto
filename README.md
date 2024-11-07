# 手机UI自动化测试工具

## 文件说明

### controller.py
手机控制基础功能模块，包含：
- `capture_phone_screen()`: 截取手机屏幕
- `click_position()`: 点击指定坐标
- `press_home()`: 返回主页
- `press_back()`: 返回上一页
- `press_recent()`: 显示最近任务

### test_cnocr.py
文字识别模块，用于检测和定位屏幕上的文字：
- `detect_text_buttons()`: 检测指定关键词的文字位置
- `process_all_images()`: 批量处理图片中的指定文字
- `process_all_text()`: 检测图片中的所有文字

### test_cross.py
关闭按钮检测模块：
- `preprocess_image()`: 图像预处理
- `find_template_matches()`: 多尺度模板匹配
- `process_cross_detection()`: 批量处理关闭按钮检测

### grounding_dino.py
通用目标检测模块：
- `convert_to_xyxy()`: 坐标格式转换
- `filter_nested_boxes()`: 嵌套框过滤
- `handle_app_startup()`: 处理应用启动弹窗
- `click_detected_boxes()`: 按顺序点击检测到的目标

### test.py
YOLO模型检测模块：
- `test_detection()`: 使用YOLO模型检测并点击UI元素

## 使用说明

1. 环境准备：
   - 安装Python依赖包
   - 确保ADB连接正常
   - 准备相应的模型文件

2. 文字检测：