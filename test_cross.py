import cv2
import numpy as np
import os

def preprocess_image(image):
    """
    预处理图片，减少颜色差异的影响
    Args:
        image: 输入图片
    Returns:
        处理后的图片
    """
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 使用边缘检测
    edges = cv2.Canny(gray, 50, 150)
    
    # 使用高斯模糊减少噪声
    blurred = cv2.GaussianBlur(edges, (5, 5), 0)
    
    return blurred

def find_template_matches(image, template, threshold=0.45):
    """
    在图片中查找与模板匹配的区域，使用多尺度匹配
    Args:
        image: 要搜索的图片
        template: 模板图片
        threshold: 匹配阈值
    Returns:
        list: 匹配位置列表，每项格式为(x1,y1,x2,y2)
    """
    # 预处理图片和模板
    processed_image = preprocess_image(image)
    processed_template = preprocess_image(template)
    
    matches = []
    
    # 定义缩放范围
    scales = np.linspace(0.5, 1.5, 20)
    
    # 在不同尺度下进行匹配
    for scale in scales:
        # 调整模板大小
        width = int(processed_template.shape[1] * scale)
        height = int(processed_template.shape[0] * scale)
        resized_template = cv2.resize(processed_template, (width, height))
        
        # 执行模板匹配
        result = cv2.matchTemplate(processed_image, resized_template, cv2.TM_CCOEFF_NORMED)
        
        # 找到所有匹配位置
        locations = np.where(result >= threshold)
        
        # 转换匹配位置为坐标
        for pt in zip(*locations[::-1]):
            x1, y1 = pt
            x2, y2 = (x1 + width, y1 + height)
            matches.append((x1, y1, x2, y2))
    
    # 合并重叠的框
    if matches:
        matches = non_max_suppression(matches)
    
    return matches

def non_max_suppression(boxes, overlap_thresh=0.3):
    """
    非极大值抑制，合并重叠的框
    Args:
        boxes: 边界框列表，格式为[(x1,y1,x2,y2),...]
        overlap_thresh: 重叠阈值
    Returns:
        list: 合并后的边界框列表
    """
    if len(boxes) == 0:
        return []
    
    boxes = np.array(boxes)
    
    # 计算所有框的面积
    area = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    
    # 按照框的右下角y坐标排序
    idxs = np.argsort(boxes[:, 3])
    
    pick = []
    while len(idxs) > 0:
        # 取出最后一个框
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)
        
        # 找出所有框与当前框的重叠区域
        xx1 = np.maximum(boxes[i, 0], boxes[idxs[:last], 0])
        yy1 = np.maximum(boxes[i, 1], boxes[idxs[:last], 1])
        xx2 = np.minimum(boxes[i, 2], boxes[idxs[:last], 2])
        yy2 = np.minimum(boxes[i, 3], boxes[idxs[:last], 3])
        
        # 计算重叠区域的宽度和高度
        w = np.maximum(0, xx2 - xx1)
        h = np.maximum(0, yy2 - yy1)
        
        # 计算重叠区域的面积
        overlap = (w * h) / area[idxs[:last]]
        
        # 删除重叠度高的框
        idxs = np.delete(idxs, np.concatenate(([last],
            np.where(overlap > overlap_thresh)[0])))
    
    return boxes[pick].tolist()

def process_cross_detection(template_path="imgs/cross.jpg", 
                          input_dir="imgs/cross", 
                          output_dir="output/cross"):
    """
    处理所有图片，查找与模板匹配的区域
    Args:
        template_path: 模板图片路径
        input_dir: 输入图片目录
        output_dir: 输出结果目录
    """
    try:
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 读取模板图片
        template = cv2.imread(template_path)
        if template is None:
            raise Exception(f"无法读取模板图片: {template_path}")
            
        # 获取所有图片文件
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = [f for f in os.listdir(input_dir) 
                      if any(f.lower().endswith(ext) for ext in image_extensions)]
        
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
                
            # 查找匹配
            matches = find_template_matches(img, template)
            
            # 在原始图片上绘制匹配结果
            for (x1, y1, x2, y2) in matches:
                cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), 
                            (0, 255, 0), 2)
            
            # 保存结果
            output_path = os.path.join(output_dir, f"detected_{image_file}")
            cv2.imwrite(output_path, img)
            print(f"检测结果已保存: {output_path}")
            print(f"找到 {len(matches)} 个匹配")
            
    except Exception as e:
        print(f"处理过程发生错误: {str(e)}")

if __name__ == "__main__":
    process_cross_detection()
