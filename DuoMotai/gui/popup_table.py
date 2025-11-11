# popup_table.py
import tkinter as tk
from tkinter import ttk

def show_table_popup(table_data, title="商品参数"):
    """
    弹出窗口显示表格
    table_data: dict 或 list of dict
        例如: {"颜色": "红色", "尺码": "M", "材质": "棉"}
    """
    root = tk.Tk()
    root.title(title)

    # 创建Treeview表格
    tree = ttk.Treeview(root, columns=("key", "value"), show="headings")
    tree.heading("key", text="属性")
    tree.heading("value", text="值")
    tree.column("key", width=150)
    tree.column("value", width=200)
    tree.pack(fill=tk.BOTH, expand=True)

    # 填充数据
    if isinstance(table_data, dict):
        for k, v in table_data.items():
            tree.insert("", tk.END, values=(k, v))
    elif isinstance(table_data, list):
        for row in table_data:
            for k, v in row.items():
                tree.insert("", tk.END, values=(k, v))
    else:
        print("[popup_table] 不支持的数据格式")

    # 居中显示窗口
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 400
    window_height = 300
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    root.mainloop()
