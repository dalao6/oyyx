#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
弹窗显示商品图片+信息模块
"""

import tkinter as tk
from PIL import Image, ImageTk
import os
import logging

class GUIDisplay:
    """
    GUI显示类，负责在弹窗中显示商品图片和信息
    """
    
    def __init__(self):
        """
        初始化GUI显示模块
        """
        self.root = None
        self.window = None
        self.on_close_callback = None
        
    def set_close_callback(self, callback):
        """
        设置窗口关闭时的回调函数
        
        Args:
            callback (function): 回调函数
        """
        self.on_close_callback = callback
        
    def show_product(self, product_info):
        """
        显示商品信息弹窗
        
        Args:
            product_info (dict): 商品信息
        """
        # 创建主窗口
        if not self.root:
            self.root = tk.Tk()
            self.root.withdraw()  # 隐藏主窗口
            
        # 创建弹窗
        self.window = tk.Toplevel(self.root)
        self.window.title("相似商品推荐")
        self.window.geometry("400x600")
        
        # 设置窗口关闭事件
        def on_window_close():
            if self.on_close_callback:
                self.on_close_callback()
            self.window.destroy()
            self.window = None
            
        self.window.protocol("WM_DELETE_WINDOW", on_window_close)
        
        # 显示商品名称
        name_label = tk.Label(self.window, text=product_info.get("name", "未知商品"), 
                             font=("Arial", 16, "bold"), wraplength=380)
        name_label.pack(pady=10)
        
        # 显示商品图片
        image_frame = tk.Frame(self.window, width=300, height=300)
        image_frame.pack(pady=10)
        image_frame.pack_propagate(False)  # 固定框架大小
        
        image_path = product_info.get("image_path", "")
        if os.path.exists(image_path):
            try:
                image = Image.open(image_path)
                # 调整图片大小以适应显示区域
                image.thumbnail((280, 280), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                image_label = tk.Label(image_frame, image=photo)
                image_label.image = photo  # 保持引用
                image_label.pack(expand=True)
            except Exception as e:
                error_label = tk.Label(image_frame, text=f"图片加载失败: {str(e)}", 
                                      wraplength=280, fg="red")
                error_label.pack(expand=True)
        else:
            placeholder = tk.Label(image_frame, text="[商品图片未找到]", 
                                 width=200, height=200, bg="lightgray")
            placeholder.pack(expand=True)
        
        # 显示相似度
        similarity_label = tk.Label(self.window, 
                                   text=f"相似度: {product_info.get('similarity', 0)*100:.1f}%",
                                   font=("Arial", 12))
        similarity_label.pack(pady=5)
        
        # 显示价格
        price_label = tk.Label(self.window, text=f"价格: ¥{product_info.get('price', 0.0):.2f}",
                              font=("Arial", 14, "bold"), fg="red")
        price_label.pack(pady=5)
        
        # 显示描述
        desc_text = product_info.get("description", "暂无描述")
        desc_label = tk.Label(self.window, text=f"描述: {desc_text}", 
                             font=("Arial", 10), wraplength=380, justify="left")
        desc_label.pack(pady=5)
        
        # 按钮框架
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=20)
        
        # 关闭按钮
        close_btn = tk.Button(button_frame, text="我不要了", 
                             command=on_window_close,
                             bg="lightcoral", fg="white", 
                             font=("Arial", 12))
        close_btn.pack(side=tk.LEFT, padx=10)
        
        # 返回主页面按钮
        back_btn = tk.Button(button_frame, text="返回主页面", 
                            command=self._return_to_main,
                            bg="lightblue", fg="white", 
                            font=("Arial", 12))
        back_btn.pack(side=tk.LEFT, padx=10)
        
    def _return_to_main(self):
        """
        返回主页面处理函数
        """
        if self.on_close_callback:
            self.on_close_callback("return_to_main")
        if self.window:
            self.window.destroy()
            self.window = None
        if self.root:
            self.root.quit()
            self.root.destroy()
            self.root = None
        
    def close_all(self):
        """
        关闭所有显示窗口
        """
        if self.window:
            self.window.destroy()
            self.window = None
        if self.root:
            self.root.quit()
            self.root.destroy()
            self.root = None

if __name__ == "__main__":
    # 测试代码
    display = GUIDisplay()
    
    # 示例商品信息
    sample_product = {
        "name": "测试T恤",
        "similarity": 0.87,
        "price": 199.0,
        "description": "这是一件高质量的测试T恤，舒适透气，适合日常穿着。",
        "image_path": "/path/to/image.jpg"
    }
    
    def close_callback(action=None):
        print(f"窗口关闭，动作: {action}")
    
    display.set_close_callback(close_callback)
    display.show_product(sample_product)
    
    # 启动GUI主循环
    if display.root:
        display.root.mainloop()