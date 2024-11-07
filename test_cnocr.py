from cnocr import CnOcr
import numpy as np
import cv2
import os
import re  # 添加正则表达式模块

def detect_text_buttons(image, keywords=None):
    """
    检测图片中的文字，并返回与关键词匹配的位置信息
    支持使用'.'作为通配符匹配任意字符
    Args:
        image: numpy数组格式的图片
        keywords: 要搜索的关键词列表，默认为["跳过","同意.继续"]
    Returns:
        list: 包含关键词位置信息的列表，每项格式为 {'text': str, 'position': (x1,y1,x2,y2)}
    """
    try:
        if keywords is None:
            keywords = ["跳过", "同意.继续"]  # 示例：匹配"同意并继续"、"同意和继续"等
            
        # 初始化识别器
        ocr = CnOcr()
        
        # 执行文字识别
        results = ocr.ocr(image)
        
        # 存储匹配的结果
        matched_texts = []
        
        # 处理识别结果
        for result in results:
            text = result['text'].strip()  # 去除首尾空白
            box = result['position']
            
            # 检查是否匹配关键词
            for keyword in keywords:
                # 直接使用keyword作为正则表达式模式
                if re.match(f"^{keyword}$", text):
                    # 转换坐标格式为(x1,y1,x2,y2)
                    x1 = min(box[0][0], box[3][0])
                    y1 = min(box[0][1], box[1][1])
                    x2 = max(box[1][0], box[2][0])
                    y2 = max(box[2][1], box[3][1])
                    
                    matched_texts.append({
                        'text': text,
                        'position': (int(x1), int(y1), int(x2), int(y2))
                    })
                    break
        
        return matched_texts
        
    except Exception as e:
        print(f"文字识别过程发生错误: {str(e)}")
        return []
    
'''
下面的代码为上面函数的测试代码，之后可以将下面的代码删除掉
'''

def process_all_images(input_dir="imgs/ads", output_dir="output/ads"):
    """
    处理指定目录下的所有图片
    Args:
        input_dir: 输入图片目录
        output_dir: 输出结果目录
    """
    try:
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 获取所有图片文件
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = [f for f in os.listdir(input_dir) if any(f.lower().endswith(ext) for ext in image_extensions)]
        
        print(f"找到 {len(image_files)} 个图片文件")
        
        # 处理每个图片
        for image_file in image_files:
            input_path = os.path.join(input_dir, image_file)
            print(f"\n处理图片: {input_path}")
            
            # 读取图片
            img = cv2.imread(input_path)
            if img is None:
                print(f"无法读取图片: {input_path}")
                continue
                
            # 执行文字检测
            keywords = [
                "跳过.*",
                "确认",
                "始终允许",
                "同意.继续",
                "确定",
                "是",
                "进入",
                "X",
                "同意"
            ]
            text_results = detect_text_buttons(img, keywords)
            
            # 在图片上绘制检测结果
            for result in text_results:
                # 获取位置信息
                x1, y1, x2, y2 = result['position']
                
                # 只绘制矩形框，不添加文字标签
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # 保存结果
            output_path = os.path.join(output_dir, f"detected_{image_file}")
            cv2.imwrite(output_path, img)
            print(f"检测结果已保存: {output_path}")
            print(f"检测到的文字:")
            for result in text_results:
                print(f"文字: {result['text']}, 位置: {result['position']}")
            
    except Exception as e:
        print(f"批量处理过程发生错误: {str(e)}")

def process_all_text(input_dir="imgs/ads", output_dir="output/ads"):
    """
    处理指定目录下的所有图片，标注所有识别到的文字
    Args:
        input_dir: 输入图片目录
        output_dir: 输出结果目录
    """
    try:
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 获取所有图片文件
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = [f for f in os.listdir(input_dir) if any(f.lower().endswith(ext) for ext in image_extensions)]
        
        print(f"找到 {len(image_files)} 个图片文件")
        
        # 初始化识别器
        ocr = CnOcr()
        
        # 处理每个图片
        for image_file in image_files:
            input_path = os.path.join(input_dir, image_file)
            print(f"\n处理图片: {input_path}")
            
            # 读取图片
            img = cv2.imread(input_path)
            if img is None:
                print(f"无法读取图片: {input_path}")
                continue
                
            # 执行文字检测
            results = ocr.ocr(img)
            
            # 在图片上绘制所有检测结果
            for result in results:
                # 获取位置信息
                box = result['position']  # 格式为[[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
                text = result['text']
                
                # 转换坐标格式为(x1,y1,x2,y2)
                x1 = min(box[0][0], box[3][0])
                y1 = min(box[0][1], box[1][1])
                x2 = max(box[1][0], box[2][0])
                y2 = max(box[2][1], box[3][1])
                
                # 绘制矩形框
                cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            
            # 保存结果
            output_path = os.path.join(output_dir, f"all_text_{image_file}")
            cv2.imwrite(output_path, img)
            print(f"检测结果已保存: {output_path}")
            print(f"检测到的文字:")
            for result in results:
                print(f"文字: {result['text']}")
            
    except Exception as e:
        print(f"批量处理过程发生错误: {str(e)}")

if __name__ == "__main__":
    # 原有的按关键词检测
    process_all_images()
    
    # 新增的检测所有文字
    process_all_text()
