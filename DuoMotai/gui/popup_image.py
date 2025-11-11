import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class ProductPopup:
    def __init__(self, product_info):
        self.product = product_info
        self.window = tk.Toplevel()
        self.window.title(self.product.get("name", "商品展示"))
        self.window.configure(bg="white")
        
        # 设置窗口属性，避免出现空白根窗口
        self.window.transient()
        self.window.grab_set()
        
        # 窗口关闭时的回调
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)

        # 保持图片引用
        img_path = self.product.get("image")
        try:
            if img_path and os.path.exists(img_path):
                img = Image.open(img_path).resize((300, 300))
                self.photo = ImageTk.PhotoImage(img)  # 保持引用在 self
                # 图片
                self.image_label = tk.Label(self.window, image=self.photo, bg="white")
                self.image_label.pack(pady=10)
            else:
                # 如果没有图片，显示一个占位文本
                no_image_label = tk.Label(self.window, text="无图片", bg="white", fg="gray")
                no_image_label.pack(pady=10)
        except Exception as e:
            # 图片加载失败时显示错误信息
            error_label = tk.Label(self.window, text="图片加载失败", bg="white", fg="red")
            error_label.pack(pady=10)

        # 名称
        tk.Label(
            self.window,
            text=self.product.get("name", "未知商品"),
            font=("微软雅黑", 14, "bold"),
            bg="white"
        ).pack(pady=5)

        # 价格
        tk.Label(
            self.window,
            text=f"价格：{self.product.get('price', '未知')}",
            font=("微软雅黑", 12),
            fg="#007ACC",
            bg="white"
        ).pack(pady=2)

        # 描述
        desc_box = tk.Text(self.window, height=4, wrap="word", bg="#F9F9F9", relief="flat")
        desc_box.insert(tk.END, self.product.get("description", "暂无描述"))
        desc_box.config(state="disabled")
        desc_box.pack(padx=10, pady=5, fill="x")

        # 标签
        tag_frame = ttk.Frame(self.window)
        tag_frame.pack(pady=5)
        for tag in self.product.get("tags", []):
            tag_label = tk.Label(
                tag_frame,
                text=tag,
                bg="#E8F0FE",
                fg="#1A73E8",
                padx=8,
                pady=4,
                font=("微软雅黑", 10)
            )
            tag_label.pack(side="left", padx=5, pady=2)

        # 关闭按钮
        tk.Button(
            self.window,
            text="关闭",
            command=self._on_closing,
            bg="#007ACC",
            fg="white",
            font=("微软雅黑", 11),
            relief="flat",
            padx=10,
            pady=5
        ).pack(pady=10)

        # 设置窗口大小并更新布局
        self.window.geometry("400x520")
        self.window.update()
    
    def _on_closing(self):
        """窗口关闭时的回调函数"""
        self.window.destroy()