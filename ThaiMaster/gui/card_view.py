"""
单词卡片界面模块

定义单词学习卡片的GUI组件，包含泰语单词显示、发音播放、录音评分等功能。
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Callable

from ThaiMaster.config import (
    FONT_SIZE_LARGE,
    FONT_SIZE_MEDIUM,
    FONT_SIZE_SMALL,
    RECORD_DURATION,
    COURSE_LEVELS
)
from ThaiMaster.core.tts import thai_tts
from ThaiMaster.core.asr import thai_asr
from ThaiMaster.core.scorer import pronunciation_scorer
from ThaiMaster.utils.audio import audio_player, audio_recorder
from ThaiMaster.data.courses import courses_manager, WordItem


class WordCardView(tk.Frame):
    """单词卡片视图
    
    显示单个单词的学习卡片，包含：
    - 泰语单词/句子显示
    - 播放标准发音按钮
    - 录音并评分按钮
    - 评分结果显示区域
    """
    
    def __init__(self, parent: tk.Widget, on_level_change: Callable[[str], None] = None):
        """初始化单词卡片视图
        
        参数:
            parent: 父容器
            on_level_change: 课程级别变更回调函数
        """
        super().__init__(parent, padx=20, pady=20)
        
        self._on_level_change = on_level_change
        self._current_word: WordItem = None
        self._current_words = []
        self._current_index = 0
        self._current_level = "N5"
        self._is_recording = False
        
        # 初始化界面
        self._init_widgets()
        
        # 加载初始课程
        self.load_level(self._current_level)
    
    def _init_widgets(self):
        """初始化界面组件"""
        # 课程级别选择区域
        level_frame = ttk.Frame(self)
        level_frame.pack(fill=tk.X, pady=(0, 15))
        
        level_label = ttk.Label(level_frame, text="课程级别:", font=("微软雅黑", FONT_SIZE_MEDIUM))
        level_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self._level_var = tk.StringVar(value=self._current_level)
        self._level_combo = ttk.Combobox(
            level_frame,
            textvariable=self._level_var,
            values=list(COURSE_LEVELS.keys()),
            state="readonly",
            font=("微软雅黑", FONT_SIZE_MEDIUM)
        )
        self._level_combo.pack(side=tk.LEFT)
        self._level_combo.bind("<<ComboboxSelected>>", self._on_level_selected)
        
        level_name_label = ttk.Label(
            level_frame,
            text=COURSE_LEVELS[self._current_level],
            font=("微软雅黑", FONT_SIZE_MEDIUM),
            foreground="#666666"
        )
        level_name_label.pack(side=tk.LEFT, padx=(10, 0))
        self._level_name_label = level_name_label
        
        # 进度显示
        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        self._progress_label = ttk.Label(
            progress_frame,
            text="进度: 1/20",
            font=("微软雅黑", FONT_SIZE_SMALL),
            foreground="#888888"
        )
        self._progress_label.pack(side=tk.RIGHT)
        
        # 单词卡片区域
        card_frame = ttk.LabelFrame(self, text="单词卡片", padding=20)
        card_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 泰语单词显示
        thai_word_frame = ttk.Frame(card_frame)
        thai_word_frame.pack(fill=tk.X, pady=(0, 10))
        
        self._thai_word_label = ttk.Label(
            thai_word_frame,
            text="",
            font=("微软雅黑", FONT_SIZE_LARGE),
            anchor=tk.CENTER
        )
        self._thai_word_label.pack(fill=tk.X)
        
        # 发音显示
        pron_frame = ttk.Frame(card_frame)
        pron_frame.pack(fill=tk.X, pady=(0, 10))
        
        self._pron_label = ttk.Label(
            pron_frame,
            text="",
            font=("微软雅黑", FONT_SIZE_MEDIUM),
            foreground="#666666",
            anchor=tk.CENTER
        )
        self._pron_label.pack(fill=tk.X)
        
        # 中文翻译显示
        chinese_frame = ttk.Frame(card_frame)
        chinese_frame.pack(fill=tk.X, pady=(0, 15))
        
        self._chinese_label = ttk.Label(
            chinese_frame,
            text="",
            font=("微软雅黑", FONT_SIZE_MEDIUM),
            foreground="#333333",
            anchor=tk.CENTER
        )
        self._chinese_label.pack(fill=tk.X)
        
        # 例句显示
        example_frame = ttk.Frame(card_frame)
        example_frame.pack(fill=tk.X)
        
        self._example_label = ttk.Label(
            example_frame,
            text="",
            font=("微软雅黑", FONT_SIZE_SMALL),
            foreground="#888888",
            anchor=tk.CENTER,
            wraplength=500
        )
        self._example_label.pack(fill=tk.X)
        
        # 操作按钮区域
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 播放按钮
        self._play_button = ttk.Button(
            button_frame,
            text="播放标准发音",
            command=self._play_pronunciation,
            style="Primary.TButton"
        )
        self._play_button.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        # 录音按钮
        self._record_button = ttk.Button(
            button_frame,
            text="录音并评分",
            command=self._start_recording,
            style="Success.TButton"
        )
        self._record_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 导航按钮区域
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill=tk.X)
        
        self._prev_button = ttk.Button(
            nav_frame,
            text="上一个",
            command=self._prev_word,
            state=tk.DISABLED
        )
        self._prev_button.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        self._next_button = ttk.Button(
            nav_frame,
            text="下一个",
            command=self._next_word
        )
        self._next_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 评分结果显示区域
        result_frame = ttk.LabelFrame(self, text="评分结果", padding=15)
        result_frame.pack(fill=tk.X, pady=(15, 0))
        
        # 分数显示
        score_frame = ttk.Frame(result_frame)
        score_frame.pack(fill=tk.X, pady=(0, 10))
        
        self._score_label = ttk.Label(
            score_frame,
            text="得分: --",
            font=("微软雅黑", FONT_SIZE_MEDIUM, "bold")
        )
        self._score_label.pack(side=tk.LEFT)
        
        self._grade_label = ttk.Label(
            score_frame,
            text="评级: --",
            font=("微软雅黑", FONT_SIZE_MEDIUM, "bold")
        )
        self._grade_label.pack(side=tk.RIGHT)
        
        # 反馈显示
        self._feedback_label = ttk.Label(
            result_frame,
            text="",
            font=("微软雅黑", FONT_SIZE_SMALL),
            foreground="#555555",
            wraplength=520
        )
        self._feedback_label.pack(fill=tk.X)
        
        # 识别文本显示
        self._recognized_label = ttk.Label(
            result_frame,
            text="",
            font=("微软雅黑", FONT_SIZE_SMALL),
            foreground="#888888",
            wraplength=520
        )
        self._recognized_label.pack(fill=tk.X, pady=(5, 0))
    
    def _on_level_selected(self, event):
        """课程级别选择事件处理
        
        参数:
            event: 事件对象
        """
        level = self._level_var.get()
        self._level_name_label.config(text=COURSE_LEVELS[level])
        self.load_level(level)
        
        if self._on_level_change:
            self._on_level_change(level)
    
    def load_level(self, level: str):
        """加载指定级别的课程
        
        参数:
            level: 课程级别代码
        """
        self._current_level = level
        self._current_words = courses_manager.get_words(level)
        self._current_index = 0
        
        if not self._current_words:
            messagebox.showinfo("提示", f"{COURSE_LEVELS[level]}课程暂未开放，请选择其他级别")
            return
        
        self._update_progress()
        self._show_word()
    
    def _update_progress(self):
        """更新进度显示"""
        total = len(self._current_words)
        current = self._current_index + 1
        self._progress_label.config(text=f"进度: {current}/{total}")
        
        # 更新导航按钮状态
        self._prev_button.config(state=tk.NORMAL if self._current_index > 0 else tk.DISABLED)
        self._next_button.config(state=tk.NORMAL if self._current_index < total - 1 else tk.DISABLED)
    
    def _show_word(self):
        """显示当前单词"""
        if not self._current_words:
            return
        
        self._current_word = self._current_words[self._current_index]
        word = self._current_word
        
        # 更新显示内容
        self._thai_word_label.config(text=word["thai"])
        self._pron_label.config(text=f"/{word['thai_pronunciation']}/")
        self._chinese_label.config(text=word["chinese"])
        self._example_label.config(text=f"例句: {word['example']} ({word['example_chinese']})")
        
        # 清空评分结果
        self._clear_score()
    
    def _clear_score(self):
        """清空评分结果显示"""
        self._score_label.config(text="得分: --")
        self._grade_label.config(text="评级: --")
        self._feedback_label.config(text="")
        self._recognized_label.config(text="")
    
    def _play_pronunciation(self):
        """播放标准发音"""
        if not self._current_word:
            messagebox.showwarning("警告", "请先选择一个单词")
            return
        
        # 禁用按钮防止重复点击
        self._play_button.config(state=tk.DISABLED)
        
        # 在后台线程中生成并播放语音
        def play_task():
            try:
                audio_file = thai_tts.speak(self._current_word["thai"])
                audio_player.play(audio_file)
            except Exception as e:
                messagebox.showerror("错误", f"播放发音失败: {str(e)}")
            finally:
                self._play_button.config(state=tk.NORMAL)
        
        threading.Thread(target=play_task, daemon=True).start()
    
    def _start_recording(self):
        """开始录音"""
        if not self._current_word:
            messagebox.showwarning("警告", "请先选择一个单词")
            return
        
        if self._is_recording:
            messagebox.showwarning("警告", "正在录音中...")
            return
        
        self._is_recording = True
        self._record_button.config(text=f"录音中 ({RECORD_DURATION}秒)...", state=tk.DISABLED)
        self._play_button.config(state=tk.DISABLED)
        
        # 在后台线程中录音
        def record_task():
            try:
                audio_file = audio_recorder.start_recording(RECORD_DURATION)
                
                # 录音完成后进行识别和评分
                self._recognize_and_score(audio_file)
            except Exception as e:
                messagebox.showerror("错误", f"录音失败: {str(e)}")
            finally:
                self._is_recording = False
                self._record_button.config(text="录音并评分", state=tk.NORMAL)
                self._play_button.config(state=tk.NORMAL)
        
        threading.Thread(target=record_task, daemon=True).start()
    
    def _recognize_and_score(self, audio_file: str):
        """识别录音并评分
        
        参数:
            audio_file: 录音文件路径
        """
        try:
            # 语音识别
            result = thai_asr.recognize(audio_file)
            recognized_text = result["text"]
            
            # 发音评分
            if recognized_text:
                score_result = pronunciation_scorer.score(
                    self._current_word["thai"],
                    recognized_text
                )
                self._show_score(score_result)
            else:
                self._score_label.config(text="得分: --")
                self._grade_label.config(text="评级: --")
                self._feedback_label.config(text="无法识别，请重试")
                self._recognized_label.config(text="")
                
        except Exception as e:
            messagebox.showerror("错误", f"识别评分失败: {str(e)}")
    
    def _show_score(self, result: Dict[str, Any]):
        """显示评分结果
        
        参数:
            result: 评分结果字典
        """
        score = result["score"]
        grade = result["grade"]
        feedback = result["feedback"]
        recognized = result["recognized"]
        
        # 设置分数和评级颜色
        if grade == "优秀":
            color = "#27ae60"
        elif grade == "良好":
            color = "#3498db"
        elif grade == "及格":
            color = "#f39c12"
        else:
            color = "#e74c3c"
        
        self._score_label.config(text=f"得分: {score:.2f}", foreground=color)
        self._grade_label.config(text=f"评级: {grade}", foreground=color)
        self._feedback_label.config(text=feedback)
        self._recognized_label.config(text=f"识别结果: {recognized}" if recognized else "")
    
    def _prev_word(self):
        """上一个单词"""
        if self._current_index > 0:
            self._current_index -= 1
            self._update_progress()
            self._show_word()
    
    def _next_word(self):
        """下一个单词"""
        if self._current_index < len(self._current_words) - 1:
            self._current_index += 1
            self._update_progress()
            self._show_word()
    
    def get_current_level(self) -> str:
        """获取当前课程级别
        
        返回:
            str: 当前课程级别代码
        """
        return self._current_level
    
    def get_current_word(self) -> WordItem:
        """获取当前单词
        
        返回:
            WordItem: 当前单词对象
        """
        return self._current_word
