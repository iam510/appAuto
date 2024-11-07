import subprocess
import time
#通过adb对手机执行的各种操作

def capture_phone_screen(device_id: str = None) -> bytes:
    """
    捕获手机屏幕并返回图片数据
    Args:
        device_id: 设备ID（可选）
    Returns:
        bytes: 截图数据
    """
    try:
        adb_command = "adb"
        if device_id:
            adb_command += f" -s {device_id}"
        
        # 直接获取截图数据
        result = subprocess.run([adb_command, "exec-out", "screencap", "-p"], 
                             capture_output=True)
        if result.returncode != 0:
            raise Exception(f"截图失败: {result.stderr}")
        
        return result.stdout
        
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
    
def press_home(device_id: str = None):
    """
    执行返回主页操作
    Args:
        device_id: 设备ID（可选）
    """
    try:
        adb_command = "adb"
        if device_id:
            adb_command += f" -s {device_id}"
            
        subprocess.run([adb_command, "shell", "input", "keyevent", "KEYCODE_HOME"])
        print("执行返回主页操作")
        return True
    except Exception as e:
        print(f"返回主页失败: {str(e)}")
        return False

def press_back(device_id: str = None):
    """
    执行返回操作
    Args:
        device_id: 设备ID（可选）
    """
    try:
        adb_command = "adb"
        if device_id:
            adb_command += f" -s {device_id}"
            
        subprocess.run([adb_command, "shell", "input", "keyevent", "KEYCODE_BACK"])
        print("执行返回操作")
        return True
    except Exception as e:
        print(f"返回操作失败: {str(e)}")
        return False

def press_recent(device_id: str = None):
    """
    执行显示最近任务操作
    Args:
        device_id: 设备ID（可选）
    """
    try:
        adb_command = "adb"
        if device_id:
            adb_command += f" -s {device_id}"
            
        subprocess.run([adb_command, "shell", "input", "keyevent", "KEYCODE_APP_SWITCH"])
        print("执行显示最近任务操作")
        return True
    except Exception as e:
        print(f"显示最近任务失败: {str(e)}")
        return False

def click_position(x: int, y: int, device_id: str = None):
    """
    点击指定坐标
    Args:
        x: x坐标
        y: y坐标
        device_id: 设备ID（可选）
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
'''
下面的代码是对上面函数的测试
'''

def test_operations():
    """
    测试各种操作
    """
    try:
        # 返回主页
        press_home()
        print("等待2秒...")
        time.sleep(2)
        
        # 显示最近任务
        press_recent()
        print("等待2秒...")
        time.sleep(2)
        
        # 返回
        press_back()
        print("等待2秒...")
        time.sleep(2)
        
        print("操作测试完成")
        
    except Exception as e:
        print(f"测试过程发生错误: {str(e)}")

if __name__ == "__main__":
    test_operations()