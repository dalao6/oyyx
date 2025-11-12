#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GUI显示模块
负责创建和管理图形用户界面
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import logging
import os
from pathlib import Path

logger = logging.getLogger("gui_display")

class GUIDisplay:
    """
    GUI显示类，负责创建和管理商品展示窗口
    """
    
    def __init__(self):
        """
        初始化GUI显示模块
        """
        self.windows = {}  # 存储所有创建的窗口
        self.close_callback = None
        self.current_product = None
        self.detecting_window = None  # 用于显示"检测中"提示的窗口
        
    def set_close_callback(self, callback):
        """
        设置窗口关闭回调函数
        
        Args:
            callback: 回调函数
        """
        self.close_callback = callback
        
    def show_detecting(self):
        """
        显示"检测中"提示窗口
        """
        if self.detecting_window is None:
            self.detecting_window = tk.Toplevel()
            self.detecting_window.title("检测中")
            self.detecting_window.geometry("300x100")
            self.detecting_window.configure(bg='lightblue')
            
            # 居中显示提示文字
            label = tk.Label(
                self.detecting_window, 
                text="识别稳定中...\n请稍候", 
                font=("Arial", 14),
                bg='lightblue'
            )
            label.pack(expand=True)
            
            # 确保窗口始终在最前面
            self.detecting_window.attributes('-topmost', True)
            
    def hide_detecting(self):
        """
        隐藏"检测中"提示窗口
        """
        if self.detecting_window:
            self.detecting_window.destroy()
            self.detecting_window = None
            
    def show_product(self, product_info):
        """
        显示商品信息（但不立即显示窗口）
        
        Args:
            product_info (dict): 商品信息字典
        """
        self.current_product = product_info
        
    def show_product_window(self, parent=None):
        """
        显示商品信息窗口
        
        Args:
            parent: 父窗口
        """
        # 隐藏检测中窗口
        self.hide_detecting()
        
        if not self.current_product:
            logger.warning("没有要显示的商品信息")
            return
            
        product = self.current_product
        
        # 创建新窗口
        window_key = f"product_{product['name']}"
        if window_key in self.windows:
            try:
                self.windows[window_key].lift()
                return
            except tk.TclError:
                pass
                
        window = tk.Toplevel(parent) if parent else tk.Toplevel()
        window.title(f"发现商品: {product.get('name', '未知商品')}")
        window.geometry("800x600")
        window.minsize(600, 400)
        
        # 存储窗口引用
        self.windows[window_key] = window
        
        # 配置窗口关闭事件
        def on_closing():
            del self.windows[window_key]
            window.destroy()
            if self.close_callback:
                self.close_callback()
                
        window.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 创建主框架
        main_frame = ttk.Frame(window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text=product.get('name', '未知商品'), 
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # 创建左右两栏布局
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：商品图片
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 尝试加载并显示商品图片
        image_path = product.get("image_path")
        if image_path and os.path.exists(image_path):
            try:
                # 读取并调整图片大小
                img = cv2.imread(image_path)
                if img is not None:
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img_pil = Image.fromarray(img_rgb)
                    img_pil.thumbnail((300, 300))
                    photo = ImageTk.PhotoImage(img_pil)
                    
                    img_label = ttk.Label(left_frame, image=photo)
                    img_label.image = photo  # 保持引用
                    img_label.pack(pady=10)
            except Exception as e:
                logger.error(f"加载商品图片时出错: {e}")
                error_label = ttk.Label(left_frame, text="图片加载失败", foreground="red")
                error_label.pack(pady=10)
        else:
            # 如果没有图片，显示占位符
            placeholder_label = ttk.Label(
                left_frame, 
                text="暂无图片", 
                font=("Arial", 12),
                foreground="gray"
            )
            placeholder_label.pack(pady=10)
        
        # 右侧：商品信息
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 价格信息
        price = product.get("price", "未知")
        if isinstance(price, (int, float)):
            price_text = f"¥{price:.2f}"
        else:
            price_text = str(price)
            
        price_label = ttk.Label(
            right_frame, 
            text=f"价格: {price_text}", 
            font=("Arial", 16, "bold")
        )
        price_label.pack(anchor=tk.W, pady=(0, 10))
        
        # 描述信息
        desc_label = ttk.Label(right_frame, text="商品描述:", font=("Arial", 12, "bold"))
        desc_label.pack(anchor=tk.W, pady=(10, 5))
        
        description = product.get("description", "暂无描述信息")
        desc_text = tk.Text(right_frame, height=8, wrap=tk.WORD)
        desc_text.insert(tk.END, description)
        desc_text.config(state=tk.DISABLED)
        desc_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 相似度信息
        similarity = product.get("similarity")
        if similarity:
            sim_label = ttk.Label(
                right_frame, 
                text=f"识别置信度: {similarity:.2%}", 
                font=("Arial", 10)
            )
            sim_label.pack(anchor=tk.W)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 我不要了按钮
        close_btn = ttk.Button(
            button_frame, 
            text="我不要了", 
            command=lambda: self._close_window(window, window_key)
        )
        close_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 返回主页面按钮
        return_btn = ttk.Button(
            button_frame, 
            text="返回主页面", 
            command=lambda: self._return_to_main(window)
        )
        return_btn.pack(side=tk.LEFT)
        
        # 确保窗口获得焦点
        window.lift()
        window.focus_force()
        
    def _close_window(self, window, key):
        """
        关闭特定窗口
        
        Args:
            window: 要关闭的窗口
            key: 窗口键名
        """
        if key in self.windows:
            del self.windows[key]
        window.destroy()
        if self.close_callback:
            self.close_callback()
            
    def _return_to_main(self, window):
        """
        返回主页面
        
        Args:
            window: 当前窗口
        """
        window.destroy()
        self.windows.clear()
        if self.close_callback:
            self.close_callback("return_to_main")
            
    def close_all(self):
        """
        关闭所有窗口
        """
        # 销毁所有窗口
        for window in list(self.windows.values()):
            try:
                window.destroy()
            except tk.TclError:
                pass
        self.windows.clear()
        
        # 关闭检测中窗口
        if self.detecting_window:
            self.detecting_window.destroy()
            self.detecting_window = None
            
        # 重置当前商品
        self.current_product = None