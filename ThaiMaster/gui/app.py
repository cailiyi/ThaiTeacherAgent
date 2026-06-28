"""
主窗口模块

定义泰语学习应用的主窗口，包含标题栏、菜单和主要内容区域。
"""

import tkinter as tk
from tkinter import ttk, messagebox

from ThaiMaster.config import (
    APP_TITLE,
    APP_WIDTH,
    APP_HEIGHT
)
from ThaiMaster.gui.card_view import WordCardView


class MainApp(tk.Tk):
    """主应用窗口
    
    泰语学习助手的主窗口，包含单词卡片学习界面。
    """
    
    def __init__(self):
        """初始化主应用窗口"""
        super().__init__()
        
        self._title = APP_TITLE
        self._width = APP_WIDTH
        self._height = APP_HEIGHT
        
        # 初始化界面
        self._init_window()
        self._init_menu()
        self._init_content()
        
        # 设置样式
        self._setup_styles()
    
    def _init_window(self):
        """初始化窗口属性"""
        self.title(self._title)
        
        # 计算居中位置
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - self._width) // 2
        y = (screen_height - self._height) // 2
        
        # 设置窗口大小和位置
        self.geometry(f"{self._width}x{self._height}+{x}+{y}")
        self.resizable(True, True)
        
        # 设置最小窗口大小
        self.minsize(500, 400)
    
    def _init_menu(self):
        """初始化菜单栏"""
        menubar = tk.Menu(self)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="退出", command=self._quit_app)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="关于", command=self._show_about)
        menubar.add_cascade(label="帮助", menu=settings_menu)
        
        # 设置菜单栏
        self.config(menu=menubar)
    
    def _init_content(self):
        """初始化内容区域"""
        # 创建单词卡片视图
        self._card_view = WordCardView(self, on_level_change=self._on_level_change)
        self._card_view.pack(fill=tk.BOTH, expand=True)
    
    def _setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        
        # 设置按钮样式
        style.configure(
            "Primary.TButton",
            font=("微软雅黑", 12),
            padding=10
        )
        
        style.configure(
            "Success.TButton",
            font=("微软雅黑", 12),
            padding=10
        )
        
        # 设置 LabelFrame 样式
        style.configure(
            "TLabelframe",
            font=("微软雅黑", 12, "bold"),
            foreground="#333333"
        )
        
        style.configure(
            "TLabelframe.Label",
            font=("微软雅黑", 12, "bold"),
            foreground="#333333"
        )
    
    def _on_level_change(self, level: str):
        """课程级别变更回调
        
        参数:
            level: 新的课程级别代码
        """
        print(f"课程级别变更为: {level}")
    
    def _quit_app(self):
        """退出应用"""
        if messagebox.askyesno("确认退出", "确定要退出泰语学习助手吗？"):
            self.destroy()
    
    def _show_about(self):
        """显示关于对话框"""
        about_text = """
泰语学习助手 (ThaiMaster)
版本: 1.0.0

一款帮助您学习泰语发音的桌面应用。

功能特性:
- 单词卡片学习
- 标准发音播放（使用 Edge TTS）
- 录音并评分（使用 Whisper ASR）
- 基于 Levenshtein 算法的发音评分

技术栈:
- Python 3.11
- Tkinter GUI
- edge-tts (文本转语音)
- faster-whisper (语音识别)
- python-Levenshtein (编辑距离)
- pyaudio (音频处理)
"""
        messagebox.showinfo("关于 ThaiMaster", about_text)
    
    def run(self):
        """启动应用主循环"""
        self.mainloop()
