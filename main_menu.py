import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import threading

class MainMenuUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DuoMotai 智能客服系统")
        self.root.geometry("500x400")
        self.root.configure(bg="#f0f0f0")
        
        # 保存正在运行的进程和相关信息
        self.running_process = None
        self.current_mode = None  # 记录当前运行的模式
        
        # 设置窗口居中
        self.center_window()
        
        # 创建界面元素
        self.create_widgets()
        
    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_widgets(self):
        """创建界面元素"""
        # 标题
        title_label = tk.Label(
            self.root,
            text="DuoMotai 智能客服系统",
            font=("微软雅黑", 20, "bold"),
            bg="#f0f0f0",
            fg="#333"
        )
        title_label.pack(pady=30)
        
        # 按钮框架
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(expand=True)
        
        # 语音购物按钮
        voice_shopping_btn = tk.Button(
            button_frame,
            text="语音购物",
            font=("微软雅黑", 14),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=15,
            relief="flat",
            command=self.voice_shopping,
            width=20
        )
        voice_shopping_btn.pack(pady=10)
        
        # 识别相似商品购物按钮
        image_shopping_btn = tk.Button(
            button_frame,
            text="识别相似商品购物",
            font=("微软雅黑", 14),
            bg="#2196F3",
            fg="white",
            padx=20,
            pady=15,
            relief="flat",
            command=self.image_shopping,
            width=20
        )
        image_shopping_btn.pack(pady=10)
        
        # 返回主页面按钮
        main_menu_btn = tk.Button(
            button_frame,
            text="返回主页面",
            font=("微软雅黑", 14),
            bg="#FF9800",
            fg="white",
            padx=20,
            pady=15,
            relief="flat",
            command=self.return_to_main,
            width=20
        )
        main_menu_btn.pack(pady=10)
        
        # 退出按钮
        exit_btn = tk.Button(
            button_frame,
            text="退出系统",
            font=("微软雅黑", 14),
            bg="#f44336",
            fg="white",
            padx=20,
            pady=15,
            relief="flat",
            command=self.exit_system,
            width=20
        )
        exit_btn.pack(pady=10)
        
    def voice_shopping(self):
        """启动语音购物功能"""
        self.run_script("DuoMotai/fin.py", "voice")
        
    def image_shopping(self):
        """启动识别相似商品购物功能"""
        self.run_script("find_something/main_find.py", "image")
        
    def _async_wait_for_process_exit(self, timeout=3000):
        """异步等待子进程退出，不阻塞界面"""
        if not self.running_process:
            return

        # 如果进程已经退出，清理状态
        if self.running_process.poll() is not None:
            self.running_process = None
            return

        # 若仍未退出，则继续等待
        self.root.after(100, self._async_wait_for_process_exit)

    def _force_kill_process(self):
        """强制结束子进程（用于超时）"""
        if self.running_process and self.running_process.poll() is None:
            try:
                self.running_process.kill()
            except Exception:
                pass

            self.running_process = None

    def return_to_main(self):
        """返回主页面，不阻塞 UI"""
        if self.running_process and self.running_process.poll() is None:
            try:
                self.running_process.terminate()

                # 异步等待子进程退出
                self._async_wait_for_process_exit()

                # 设置超时强杀（3秒）
                self.root.after(3000, self._force_kill_process)

            except Exception as e:
                messagebox.showerror("错误", f"停止进程出错: {str(e)}")
        else:
            messagebox.showinfo("提示", "没有正在运行的程序")
        
    def exit_system(self):
        """退出系统（同样不阻塞 UI）"""
        if messagebox.askokcancel("确认", "确定要退出系统吗？"):
            if self.running_process and self.running_process.poll() is None:
                try:
                    self.running_process.terminate()
                    self._async_wait_for_process_exit()
                    self.root.after(3000, self._force_kill_process)
                except:
                    pass

            self.root.quit()
            self.root.destroy()
            
    def run_script(self, script_name, mode):
        """运行指定的Python脚本（不阻塞 UI）"""
        try:
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
            if os.path.exists(script_path):

                # 若已有进程，安全终止
                if self.running_process and self.running_process.poll() is None:
                    self.running_process.terminate()
                    self._async_wait_for_process_exit()
                    self.root.after(3000, self._force_kill_process)

                self.current_mode = mode

                # 启动新进程
                self.running_process = subprocess.Popen([sys.executable, script_path])

            else:
                messagebox.showerror("错误", f"找不到脚本文件: {script_name}")

        except Exception as e:
            messagebox.showerror("错误", f"启动脚本时出错: {str(e)}")
        
    def run(self):
        """运行主界面"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MainMenuUI()
    app.run()