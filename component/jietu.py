import pyautogui
import os
import tkinter as tk
from tkinter import messagebox
import keyboard

# 获取当前工作目录
current_directory = os.getcwd()

# 指定截图保存的文件夹
screenshot_folder = os.path.join(current_directory, 'screenshots')

# 确保文件夹存在
if not os.path.exists(screenshot_folder):
    os.makedirs(screenshot_folder)

# 全局变量来控制截图功能
is_taking_screenshots = False

def take_screenshot():
    # 截图
    screenshot = pyautogui.screenshot()
    
    # 生成文件名
    base_filename = 'image'
    file_extension = '.png'
    file_number = 1
    while True:
        filename = os.path.join(screenshot_folder, f'{base_filename}{file_number}{file_extension}')
        if not os.path.exists(filename):
            break
        file_number += 1
    
    # 保存截图
    screenshot.save(filename)
    print(f'Screenshot saved as {filename}')

def start_screenshots():
    global is_taking_screenshots
    is_taking_screenshots = True
    take_screenshot_button.config(state=tk.DISABLED)
    stop_screenshots_button.config(state=tk.NORMAL)
    keyboard.add_hotkey('s', take_screenshot)  # 监听's'键

def stop_screenshots():
    global is_taking_screenshots
    is_taking_screenshots = False
    take_screenshot_button.config(state=tk.NORMAL)
    stop_screenshots_button.config(state=tk.DISABLED)
    keyboard.remove_all_hotkeys()  # 移除所有热键监听

# 创建主窗口
root = tk.Tk()
root.title("截图脚本")
root.geometry("512x512")

# 创建按钮
take_screenshot_button = tk.Button(root, text="开始脚本", command=start_screenshots)
take_screenshot_button.pack(pady=20)

stop_screenshots_button = tk.Button(root, text="中止脚本", command=stop_screenshots, state=tk.DISABLED)
stop_screenshots_button.pack(pady=20)

# 主循环
root.mainloop()