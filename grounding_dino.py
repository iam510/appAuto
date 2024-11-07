import cv2
import numpy as np
from modelscope.pipelines import pipeline
from modelscope.hub.snapshot_download import snapshot_download
import controller
import time
import os
from test_cnocr import detect_text_buttons

def convert_to_xyxy(boxes, img_width, img_height):
    """
    将[center_x, center_y, width, height]格式转换为[x1, y1, x2, y2]格式
    """
    boxes = np.array(boxes)
    boxes_xyxy = np.zeros_like(boxes)
    
    # 转换到像素坐标
    boxes_xyxy[:, 0] = (boxes[:, 0] - boxes[:, 2]/2) * img_width  # x1
    boxes_xyxy[:, 1] = (boxes[:, 1] - boxes[:, 3]/2) * img_height # y1
    boxes_xyxy[:, 2] = (boxes[:, 0] + boxes[:, 2]/2) * img_width  # x2
    boxes_xyxy[:, 3] = (boxes[:, 1] + boxes[:, 3]/2) * img_height # y2
    
    return boxes_xyxy

def filter_nested_boxes(boxes):
    """
    过滤掉包含其他框的大框
    boxes: 边界框列表，格式为 [[x1,y1,x2,y2],...]
    返回: 过滤后的框
    """
    if len(boxes) == 0:
        return boxes
    
    boxes = np.array(boxes)
    filtered_indices = []
    
    for i in range(len(boxes)):
        is_container = False
        box1 = boxes[i]
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        
        for j in range(len(boxes)):
            if i != j:
                box2 = boxes[j]
                area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
                
                # 检查box1是否包含box2
                if (box1[0] <= box2[0] and box1[1] <= box2[1] and 
                    box1[2] >= box2[2] and box1[3] >= box2[3] and
                    area1 > area2):  # 确保大框被过滤
                    is_container = True
                    break
        
        if not is_container:
            filtered_indices.append(i)
    
    return boxes[filtered_indices]

def handle_app_startup(max_attempts=10, interval=3):
    """
    处理应用启动后的各种弹窗和操作
    包括：开屏广告、登录提示、权限请求等
    Args:
        max_attempts: 最大尝试次数，防止无限循环
        interval: 每次检测的间隔时间(秒)
    """
    try:
        attempt = 0
        while attempt < max_attempts:
            print(f"\n第 {attempt + 1} 次检测...")
            
            # 获取屏幕截图
            screenshot_data = controller.capture_phone_screen()
            if screenshot_data is None:
                print("截图失败，等待后重试")
                time.sleep(interval)
                attempt += 1
                continue
                
            # 转换截图数据
            nparr = np.frombuffer(screenshot_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                print("图片解析失败，等待后重试")
                time.sleep(interval)
                attempt += 1
                continue
                
            # 检测文字按钮
            keywords = [
                "跳过.*",
                "确认",
                "始终允许",
                "同意.*继续",
                "确定",
                "是",
                "进入",
                "X",
                "同意"
            ]
            text_buttons = detect_text_buttons(img, keywords)
            
            # 如果没有检测到任何按钮，说明处理完成
            if not text_buttons:
                print("未检测到需要处理的按钮，处理完成")
                break
            
            # 点击检测到的按钮
            for button in text_buttons:
                x1, y1, x2, y2 = button['position']
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                
                print(f"点击文字按钮: {button['text']}")
                controller.click_position(center_x, center_y)
                time.sleep(1)  # 短暂等待按钮响应
            
            # 等待一段时间后进行下一次检测
            print(f"等待 {interval} 秒后进行下一次检测...")
            time.sleep(interval)
            attempt += 1
        
        if attempt >= max_attempts:
            print(f"达到最大尝试次数 {max_attempts}，停止处理")
        else:
            print("完成启动项处理")
        
    except Exception as e:
        print(f"处理启动项时发生错误: {str(e)}")

def click_detected_boxes(filtered_boxes):
    """
    按照位置顺序点击检测到的框
    Args:
        filtered_boxes: 过滤后的检测框列表 [[x1,y1,x2,y2],...]
    """
    try:
        if len(filtered_boxes) == 0:
            print("没有检测到可点击的目标")
            return
            
        # 计算所有框的中心点
        center_points = []
        for box in filtered_boxes:
            x1, y1, x2, y2 = map(int, box)
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            center_points.append({
                'x': center_x,
                'y': center_y,
                'position': (x1, y1, x2, y2)
            })
        
        # 按x从小到大，y从小到大排序
        # 按照顺序点击比较难实现，因为同一列的x坐标可能不一样
        #center_points.sort(key=lambda p: (p['x'], p['y']))
        
        # 依次点击每个目标
        for i, point in enumerate(center_points, 1):
            print(f"\n点击第 {i} 个目标")
            print(f"坐标: ({point['x']}, {point['y']})")
            
            # 执行点击
            controller.click_position(point['x'], point['y'])
            print("等待2秒...")
            time.sleep(2)
            
            # 处理应用启动相关操作
            handle_app_startup()
            
            # 返回主页
            controller.press_home()
            print("等待2秒...")
            time.sleep(2)
        
        print(f"\n完成所有目标的点击操作！")
        print(f"共点击了 {len(center_points)} 个目标")
        
    except Exception as e:
        print(f"点击操作发生错误: {str(e)}")

def detect_icons():
    """
    使用controller截图并检测图标
    """
    try:
        # 创建output文件夹
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 使用controller截图
        screenshot_data = controller.capture_phone_screen()
        if screenshot_data is None:
            print("截图失败")
            return []
            
        # 将截图数据转换为numpy数组
        nparr = np.frombuffer(screenshot_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            print("无法解析截图数据")
            return []
            
        # 保存截图用于GroundingDINO输入
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        input_path = os.path.join(output_dir, f"screenshot_{timestamp}.png")
        cv2.imwrite(input_path, img)
        
        # 加载模型
        model_dir = snapshot_download('AI-ModelScope/GroundingDINO')
        pipe = pipeline('grounding-dino-task', model=model_dir)
        
        # 设置输入
        inputs = {
            "IMAGE_PATH": input_path,
            "TEXT_PROMPT": "icon",
            "BOX_TRESHOLD": 0.25,
            "TEXT_TRESHOLD": 0.25
        }
        
        # 运行检测
        output = pipe(inputs)
        
        img_height, img_width = img.shape[:2]
        
        # 转换框的格式
        boxes_xyxy = convert_to_xyxy(output['boxes'], img_width, img_height)
        
        # 过滤嵌套框
        filtered_boxes = filter_nested_boxes(boxes_xyxy)
        
        # 绘制过滤后的框
        for box in filtered_boxes:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # 保存结果
        output_path = os.path.join(output_dir, f"grounding_dino_{timestamp}.png")          
        cv2.imwrite(output_path, img)
        print(f"检测结果已保存: {output_path}")
        
        # 清理临时文件
        if os.path.exists(input_path):
            os.remove(input_path)
            
        # 在保存结果图片后，添加点击操作
        if len(filtered_boxes) > 0:
            print("\n开始执行点击操作...")
            click_detected_boxes(filtered_boxes)
        else:
            print("未检测到任何目标")
            
        return filtered_boxes
        
    except Exception as e:
        print(f"检测过程发生错误: {str(e)}")
        return []

if __name__ == "__main__":
    detect_icons()
