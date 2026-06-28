"""
ThaiMaster 主窗口应用程序

这是整个 ThaiMaster 的 GUI 主入口，负责：
1. 组织和管理所有界面组件
2. 协调核心功能模块（TTS、ASR、评分）
3. 处理用户交互事件
4. 管理课程导航和学习进度

主窗口布局：
┌─────────────────────────────────────────────────┐
│ 菜单栏: [文件] [课程] [帮助]                      │
├─────────────────────────────────────────────────┤
│ 顶部: 课程选择下拉框    [切换课程]  [重置进度]    │
├─────────────────────────────────────────────────┤
│                                                 │
│              卡片视图 (CardView)                  │
│              (单词/句子显示区)                    │
│                                                 │
├─────────────────────────────────────────────────┤
│ 状态栏: 当前课程 | 学习进度 | 得分统计            │
└─────────────────────────────────────────────────┘
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, font

from config import (
    APP_TITLE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    COURSE_LEVELS,
    AUDIO_TEMP_DIR,
)
from data.courses import load_courses, Lesson
from gui.card_view import CardView
from core.tts import speak
from core.asr import transcribe
from core.scorer import calculate_score
from utils.audio import record_audio, play_audio, list_audio_devices


class ThaiMasterApp:
    """
    ThaiMaster 主应用类。

    管理整个应用程序的生命周期，包括窗口创建、组件初始化、
    事件处理和模块协调。

    Attributes:
        root: tkinter 根窗口
        courses: 所有课程数据
        current_level: 当前课程级别名称
        current_lesson_index: 当前课程在级别中的索引
        recorded_file: 最近一次录音的文件路径
    """

    def __init__(self):
        """初始化应用程序，创建主窗口和所有组件。"""
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(800, 600)

        # 设置窗口图标（可选）
        try:
            self.root.iconbitmap(default="")
        except Exception:
            pass  # 忽略图标加载失败

        # 内部状态
        self.courses = {}
        self.current_level = COURSE_LEVELS[0]
        self.current_lesson_index = 0
        self.recorded_file = ""
        self._is_recording = False
        self._is_processing = False

        # 确保临时目录存在
        os.makedirs(AUDIO_TEMP_DIR, exist_ok=True)

        # 加载课程数据
        self._load_course_data()

        # 设置 UI
        self._setup_menu()
        self._setup_ui()
        self._setup_status_bar()

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # 加载第一课
        self._load_first_lesson()

    def _load_course_data(self):
        """
        加载课程数据。

        调用 courses.py 的 load_courses() 函数，
        获取所有分级课程数据。如果加载失败，显示错误提示。
        """
        try:
            self.courses = load_courses()
            print(f"[应用] 已加载 {len(self.courses)} 个级别课程")
            for level, lessons in self.courses.items():
                total = sum(len(l.cards) for l in lessons)
                print(f"       {level}: {len(lessons)} 课, {total} 张卡片")
        except Exception as e:
            print(f"[应用错误] 加载课程失败: {e}")
            self.courses = {}
            messagebox.showerror("错误", f"加载课程数据失败: {e}")

    # ==========================================================
    # UI 搭建
    # ==========================================================

    def _setup_menu(self):
        """
        创建菜单栏。

        包含文件、课程、帮助等菜单项。
        """
        menubar = tk.Menu(self.root)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="检查音频设备", command=self._check_audio_devices)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._on_close)
        menubar.add_cascade(label="文件", menu=file_menu)

        # 课程菜单
        course_menu = tk.Menu(menubar, tearoff=0)
        course_menu.add_command(label="重新加载课程", command=self._reload_courses)
        course_menu.add_separator()
        for level in COURSE_LEVELS:
            course_menu.add_command(
                label=level,
                command=lambda l=level: self._switch_level(l),
            )
        menubar.add_cascade(label="课程", menu=course_menu)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)

        self.root.config(menu=menubar)

    def _setup_ui(self):
        """
        搭建主界面布局。

        包含顶部控制栏、中间的卡片视图和底部的状态栏。
        """
        # 主容器
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)  # 卡片区域可伸缩

        # ======== 顶部控制栏 ========
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)

        # 课程级别选择
        ttk.Label(control_frame, text="课程级别:").grid(
            row=0, column=0, padx=(0, 5), sticky="w"
        )
        self.level_var = tk.StringVar(value=self.current_level)
        self.level_combo = ttk.Combobox(
            control_frame,
            textvariable=self.level_var,
            values=COURSE_LEVELS,
            state="readonly",
            width=15,
        )
        self.level_combo.grid(row=0, column=1, padx=5, sticky="w")
        self.level_combo.bind("<<ComboboxSelected>>", self._on_level_change)

        # 课程选择（某个级别下的具体课）
        ttk.Label(control_frame, text="选择课程:").grid(
            row=0, column=2, padx=(20, 5), sticky="w"
        )
        self.lesson_var = tk.StringVar()
        self.lesson_combo = ttk.Combobox(
            control_frame,
            textvariable=self.lesson_var,
            state="readonly",
            width=25,
        )
        self.lesson_combo.grid(row=0, column=3, padx=5, sticky="w")
        self.lesson_combo.bind("<<ComboboxSelected>>", self._on_lesson_change)

        # 语音选择
        ttk.Label(control_frame, text="语音:").grid(
            row=0, column=4, padx=(20, 5), sticky="w"
        )
        self.voice_var = tk.StringVar(value="女性语音")
        self.voice_combo = ttk.Combobox(
            control_frame,
            textvariable=self.voice_var,
            values=["女性语音", "男性语音"],
            state="readonly",
            width=10,
        )
        self.voice_combo.grid(row=0, column=5, padx=5, sticky="w")
        self.voice_combo.bind("<<ComboboxSelected>>", self._on_voice_change)

        # ======== 卡片视图（中间主体） ========
        self.card_view = CardView(main_frame)
        self.card_view.grid(row=1, column=0, sticky="nsew")

        # 注册卡片视图的回调函数
        self.card_view.set_play_callback(self._on_play_pronunciation)
        self.card_view.set_record_callback(self._on_record_and_score)
        self.card_view.set_speak_callback(self._on_play_pronunciation)

    def _setup_status_bar(self):
        """
        创建底部状态栏。

        显示当前课程级别、学习进度和评分统计。
        """
        self.status_frame = ttk.Frame(self.root, relief=tk.SUNKEN)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = ttk.Label(
            self.status_frame,
            text="ThaiMaster v1.0 | 就绪",
            padding=(10, 2),
        )
        self.status_label.pack(side=tk.LEFT)

        self.status_detail = ttk.Label(
            self.status_frame,
            text="",
            padding=(10, 2),
        )
        self.status_detail.pack(side=tk.RIGHT)

    # ==========================================================
    # 课程导航逻辑
    # ==========================================================

    def _load_first_lesson(self):
        """
        加载第一个级别的第一课。

        应用启动时自动调用，显示初始内容。
        """
        if self.courses and self.current_level in self.courses:
            lessons = self.courses[self.current_level]
            if lessons:
                self._update_lesson_list()
                self.lesson_combo.current(0)
                self.current_lesson_index = 0
                self.card_view.set_lesson(lessons[0])
                self._update_status("就绪")

    def _update_lesson_list(self):
        """
        更新课程下拉列表。

        根据当前选中的课程级别，更新可选的课程序列。
        """
        if self.current_level in self.courses:
            lessons = self.courses[self.current_level]
            lesson_names = [f"第{i + 1}课: {l.title}" for i, l in enumerate(lessons)]
            self.lesson_combo["values"] = lesson_names

    def _on_level_change(self, event=None):
        """
        课程级别选择变更事件处理。

        用户在下拉框中选择不同级别时触发。
        """
        self.current_level = self.level_var.get()
        self._update_lesson_list()
        if self.lesson_combo["values"]:
            self.lesson_combo.current(0)
            self._on_lesson_change()

    def _on_lesson_change(self, event=None):
        """
        课程选择变更事件处理。

        用户在下拉框中选择不同课程时触发。
        """
        selection = self.lesson_combo.current()
        if selection >= 0:
            self.current_lesson_index = selection
            if self.current_level in self.courses:
                lessons = self.courses[self.current_level]
                if 0 <= selection < len(lessons):
                    self.card_view.set_lesson(lessons[selection])
                    self._update_status(f"{self.current_level} - {lessons[selection].title}")

    def _on_voice_change(self, event=None):
        """
        语音角色变更事件处理。

        在女性语音和男性语音之间切换 TTS 角色。
        """
        from core.tts import change_voice
        idx = self.voice_combo.current()
        voice_name = change_voice(idx)
        print(f"[应用] 切换语音为: {voice_name}")

    def _switch_level(self, level: str):
        """
        菜单命令：切换到指定的课程级别。

        Args:
            level: 级别名称（如 "N5 入门级"）
        """
        self.level_var.set(level)
        self._on_level_change()

    # ==========================================================
    # 核心功能：播放、录音、评分
    # ==========================================================

    def _on_play_pronunciation(self, text: str):
        """
        播放标准泰语发音。

        使用 edge-tts 生成泰语语音并播放。

        Args:
            text: 要播放的泰语文本
        """
        if not text:
            return

        # 在后台线程执行 TTS 和播放，不阻塞 UI
        def _play_thread():
            try:
                self._update_status(f"正在生成发音: {text}")
                audio_file = speak(text)
                if audio_file:
                    print(f"[播放] TTS 文件: {audio_file}")
                    play_audio(audio_file, blocking=True)
                    self._update_status("就绪")
                else:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "播放失败", "无法生成语音，请检查网络连接。"
                    ))
                    self._update_status("TTS 生成失败")
            except Exception as e:
                print(f"[播放错误] {e}")
                self.root.after(0, lambda: messagebox.showerror(
                    "播放错误", str(e)
                ))
                self._update_status("播放出错")

        threading.Thread(target=_play_thread, daemon=True).start()

    def _on_record_and_score(self, text: str):
        """
        录音并评分的主要流程。

        流程：录音 → ASR 识别 → 计算评分 → 显示结果

        Args:
            text: 标准泰语文本（用于对比评分）
        """
        if not text:
            return

        if self._is_recording or self._is_processing:
            messagebox.showinfo("提示", "正在处理中，请稍候...")
            return

        # 重置评分显示
        self.card_view.show_recording_status()

        # 在后台线程执行录音和识别
        def _process_thread():
            self._is_recording = True
            self._is_processing = False
            try:
                # ====== 第1步：录音 ======
                self.root.after(0, lambda: self._update_status("正在录音..."))
                audio_file = record_audio()

                if not audio_file:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "录音失败", "未捕获到音频输入，请检查麦克风。"
                    ))
                    self._is_recording = False
                    self._update_status("录音失败")
                    return

                self.recorded_file = audio_file
                self._is_recording = False
                self._is_processing = True

                # ====== 第2步：ASR 识别 ======
                self.root.after(0, lambda: [
                    self.card_view.show_processing_status(),
                    self._update_status("正在识别语音...")
                ])

                asr_result = transcribe(audio_file)

                if not asr_result["success"]:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "识别失败", asr_result.get("error", "无法识别语音内容")
                    ))
                    self._is_processing = False
                    self._update_status("识别失败")
                    return

                user_text = asr_result["text"]
                confidence = asr_result["confidence"]

                # ====== 第3步：计算评分 ======
                self.root.after(0, lambda: self._update_status("正在计算评分..."))

                score, details = calculate_score(text, user_text)

                # 在详情中添加置信度信息
                details["asr_confidence"] = confidence

                # ====== 第4步：UI 显示结果 ======
                self.root.after(0, lambda: [
                    self.card_view.show_score(score, details),
                    self._update_status(
                        f"评分完成: {score}分 | "
                        f"ASR置信度: {confidence:.1%} | "
                        f"用时: {asr_result.get('duration', 0):.1f}s"
                    )
                ])

                self._is_processing = False

            except Exception as e:
                print(f"[录音评分错误] {e}")
                self._is_recording = False
                self._is_processing = False
                self.root.after(0, lambda: messagebox.showerror(
                    "处理错误", f"录音评分过程中出现错误: {e}"
                ))
                self._update_status("处理出错")

        threading.Thread(target=_process_thread, daemon=True).start()

    # ==========================================================
    # 菜单命令和辅助功能
    # ==========================================================

    def _check_audio_devices(self):
        """
        检查并显示可用的音频设备列表。

        用于诊断麦克风和扬声器问题。
        """
        devices = list_audio_devices()

        if not devices:
            messagebox.showinfo("音频设备", "未检测到音频设备或查询失败。")
            return

        # 构建设备列表文本
        lines = ["=== 可用音频设备 ===", ""]
        lines.append("--- 输入设备（麦克风） ---")
        for d in devices:
            if d["max_input_channels"] > 0:
                lines.append(f"  [{d['index']}] {d['name']}")
                lines.append(f"      输入通道: {d['max_input_channels']}")

        lines.append("")
        lines.append("--- 输出设备（扬声器） ---")
        for d in devices:
            if d["max_output_channels"] > 0 and d["max_input_channels"] == 0:
                lines.append(f"  [{d['index']}] {d['name']}")
                lines.append(f"      输出通道: {d['max_output_channels']}")

        messagebox.showinfo("音频设备信息", "\n".join(lines))

    def _reload_courses(self):
        """
        重新加载课程数据。

        用于课程数据更新后的刷新。
        """
        self._load_course_data()
        self._load_first_lesson()
        messagebox.showinfo("重载完成", "课程数据已重新加载。")

    def _show_help(self):
        """
        显示使用说明对话框。
        """
        help_text = """ThaiMaster 泰语学习助手

📖 基本用法：
1. 在顶部选择课程级别（N5~N1）
2. 选择具体课程
3. 查看卡片上的泰语单词/句子
4. 点击「播放」听标准发音
5. 点击「录音」并朗读，获得评分反馈

🎯 评分标准：
• 90-100 分: 优秀 ✨
• 80-89 分:  良好 👍
• 60-79 分:  及格 💪
•  0-59 分:  不及格 🔄

💡 提示：
• 点击泰语文字可直接播放发音
• 建议在安静环境下录音
• 可切换女性/男性语音
• 首次使用 ASR 需下载模型（约 1.5GB）

📦 数据路径：
课程数据: data/courses.py
临时音频: temp_audio/
"""
        messagebox.showinfo("使用说明", help_text)

    def _show_about(self):
        """
        显示关于对话框。
        """
        about_text = """ThaiMaster v1.0

泰语学习智能助手

技术栈:
• Python 3.11 + tkinter
• edge-tts (语音合成)
• faster-whisper (语音识别)
• Levenshtein (发音评分)

功能特点:
• N5 ~ N1 分级课程体系
• 标准泰语发音带读
• AI 发音评分反馈
• 循序渐进的学习路径

适用平台: Windows 10+"""
        messagebox.showinfo("关于 ThaiMaster", about_text)

    # ==========================================================
    # 状态管理
    # ==========================================================

    def _update_status(self, text: str):
        """
        更新状态栏文字。

        Args:
            text: 要显示的状态信息
        """
        self.status_label.config(text=f"ThaiMaster | {text}")
        self.root.update_idletasks()

    def _on_close(self):
        """
        窗口关闭事件处理。

        清理临时文件后退出应用。
        """
        try:
            from utils.audio import cleanup_temp_files
            cleanup_temp_files(max_age_hours=1)
        except Exception:
            pass
        self.root.destroy()

    # ==========================================================
    # 启动
    # ==========================================================

    def run(self):
        """
        启动应用程序主循环。

        调用此函数后进入 tkinter 事件循环。
        """
        # 检查音频设备（非阻塞提示）
        devices = list_audio_devices()
        has_input = any(d["max_input_channels"] > 0 for d in devices)
        if not has_input:
            print("[应用] 警告: 未检测到麦克风设备")

        # 设置窗口居中
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - WINDOW_WIDTH) // 2
        y = (self.root.winfo_screenheight() - WINDOW_HEIGHT) // 2
        self.root.geometry(f"+{x}+{y}")

        # 进入主循环
        self.root.mainloop()
