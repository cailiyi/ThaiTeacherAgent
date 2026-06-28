"""
单词卡片界面模块

提供一个美观的"学习卡片"组件，用于显示泰语单词/句子的学习内容。
卡片以类似 Anki 记忆卡片的方式展示，包含：

界面布局（从上到下）：
    1. 课程标题和进度指示
    2. 泰语大字体显示区（卡片主体）
    3. 发音指南（罗马音）
    4. 中文释义
    5. 例句展示
    6. 操作按钮区（播放发音、录音评分）
    7. 评分结果显示区

交互功能：
    - 显示当前卡片内容
    - 点击"播放"按钮听标准发音
    - 点击"录音"按钮开始录音并获取评分
    - 切换上一张/下一张卡片
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from data.courses import CardItem, Lesson


class CardView(ttk.Frame):
    """
    单词学习卡片视图组件。

    这是一个可复用的 tkinter Frame 组件，
    用于展示泰语学习卡片的所有内容。

    Attributes:
        master: 父级窗口/容器
        current_lesson: 当前正在学习的课程
        current_card_index: 当前显示的卡片索引
        current_cards: 当前课程的所有卡片列表
        _on_play_callback: 播放按钮回调函数
        _on_record_callback: 录音按钮回调函数
    """

    def __init__(self, master, **kwargs):
        """
        初始化卡片视图。

        Args:
            master: 父级 tkinter 组件
            **kwargs: 传递给 ttk.Frame 的额外参数
        """
        super().__init__(master, **kwargs)

        # 内部状态
        self.current_lesson: Optional[Lesson] = None
        self.current_card_index: int = 0
        self.current_cards: list = []
        self._on_play_callback = None
        self._on_record_callback = None
        self._on_speak_callback = None  # 点击卡片文本朗读

        # 创建界面
        self._setup_ui()

        # 配置网格权重，使卡片能自适应缩放
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def _setup_ui(self):
        """
        初始化卡片界面的所有 UI 组件。

        布局结构：
        ┌────────────────────────────────┐
        │     课程标题 / 进度 (x/x)       │  ← header_frame
        ├────────────────────────────────┤
        │                                │
        │     泰语文本（大字体）           │  ← card_frame
        │     发音指南                    │
        │     中文释义                    │
        │     例句                        │
        │                                │
        ├────────────────────────────────┤
        │  [播放] [录音]  评分: 98分      │  ← button_frame
        │       评分详情                  │
        └────────────────────────────────┘
        """

        # ========== 样式配置 ==========
        style = ttk.Style()
        style.configure("CardTitle.TLabel", font=("", 14, "bold"))
        style.configure("CardProgress.TLabel", font=("", 10))

        # ========== 顶部：课程标题和进度 ==========
        self.header_frame = ttk.Frame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.header_frame.columnconfigure(0, weight=1)

        self.label_lesson_title = ttk.Label(
            self.header_frame,
            text="请选择一个课程开始学习",
            style="CardTitle.TLabel",
        )
        self.label_lesson_title.grid(row=0, column=0, sticky="w")

        self.label_progress = ttk.Label(
            self.header_frame,
            text="0/0",
            style="CardProgress.TLabel",
        )
        self.label_progress.grid(row=0, column=1, sticky="e")

        # ========== 中间：卡片主体区域 ==========
        # 使用 Canvas + Frame 实现卡片效果（带边框和背景色）
        self.card_frame = tk.Frame(
            self,
            bg="white",
            highlightbackground="#ddd",
            highlightthickness=1,
            relief=tk.FLAT,
        )
        self.card_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.card_frame.columnconfigure(0, weight=1)

        # 内边距，让内容不要紧贴边框
        self.card_inner = tk.Frame(self.card_frame, bg="white")
        self.card_inner.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)

        # 泰语文本（大字体显示）
        self.label_thai = tk.Label(
            self.card_inner,
            text="",
            font=("", 32, "bold"),
            fg="#2c3e50",
            bg="white",
            wraplength=500,
            cursor="hand2",  # 手型光标提示可点击
        )
        self.label_thai.pack(pady=(10, 5))
        self.label_thai.bind("<Button-1>", lambda e: self._on_thai_click())

        # 分隔线
        self.separator = tk.Frame(self.card_inner, height=2, bg="#eee")
        self.separator.pack(fill=tk.X, pady=8)

        # 发音指南（罗马音）
        self.label_pronunciation = tk.Label(
            self.card_inner,
            text="",
            font=("", 14),
            fg="#7f8c8d",
            bg="white",
        )
        self.label_pronunciation.pack(pady=2)

        # 词性标注
        self.label_word_type = tk.Label(
            self.card_inner,
            text="",
            font=("", 10),
            fg="#95a5a6",
            bg="white",
        )
        self.label_word_type.pack(pady=2)

        # 中文释义
        self.label_meaning = tk.Label(
            self.card_inner,
            text="",
            font=("", 16),
            fg="#34495e",
            bg="white",
            wraplength=500,
        )
        self.label_meaning.pack(pady=(5, 15))

        # 例句区域
        self.example_frame = tk.Frame(self.card_inner, bg="#f8f9fa",
                                      highlightbackground="#e9ecef",
                                      highlightthickness=1)
        self.example_frame.pack(fill=tk.X, pady=5, ipady=5)

        self.label_example_label = tk.Label(
            self.example_frame,
            text="📖 例句",
            font=("", 10, "bold"),
            fg="#6c757d",
            bg="#f8f9fa",
        )
        self.label_example_label.pack(anchor="w", padx=10, pady=(5, 0))

        self.label_example_thai = tk.Label(
            self.example_frame,
            text="",
            font=("", 13),
            fg="#2c3e50",
            bg="#f8f9fa",
            wraplength=480,
        )
        self.label_example_thai.pack(anchor="w", padx=10, pady=(2, 0))

        self.label_example_pronunciation = tk.Label(
            self.example_frame,
            text="",
            font=("", 11),
            fg="#7f8c8d",
            bg="#f8f9fa",
            wraplength=480,
        )
        self.label_example_pronunciation.pack(anchor="w", padx=10, pady=(0, 2))

        self.label_example_meaning = tk.Label(
            self.example_frame,
            text="",
            font=("", 11),
            fg="#6c757d",
            bg="#f8f9fa",
            wraplength=480,
        )
        self.label_example_meaning.pack(anchor="w", padx=10, pady=(0, 5))

        # ========== 底部：按钮和评分区域 ==========
        self.control_frame = ttk.Frame(self)
        self.control_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.control_frame.columnconfigure(0, weight=1)

        # 第一行：操作按钮
        self.button_frame = ttk.Frame(self.control_frame)
        self.button_frame.pack(fill=tk.X)

        self.btn_play = ttk.Button(
            self.button_frame,
            text="🔊 播放标准发音",
            command=self._on_play_click,
        )
        self.btn_play.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_record = ttk.Button(
            self.button_frame,
            text="🎤 录音并评分",
            command=self._on_record_click,
        )
        self.btn_record.pack(side=tk.LEFT, padx=(0, 10))

        # 导航按钮
        self.btn_prev = ttk.Button(
            self.button_frame,
            text="◀ 上一张",
            command=self._on_prev_click,
        )
        self.btn_prev.pack(side=tk.RIGHT, padx=(5, 0))

        self.btn_next = ttk.Button(
            self.button_frame,
            text="下一张 ▶",
            command=self._on_next_click,
        )
        self.btn_next.pack(side=tk.RIGHT, padx=(5, 0))

        # 第二行：评分结果显示
        self.score_frame = ttk.Frame(self.control_frame)
        self.score_frame.pack(fill=tk.X, pady=(10, 0))

        # 评分标签（大号显示）
        self.label_score = tk.Label(
            self.score_frame,
            text="",
            font=("", 28, "bold"),
            fg="#bdc3c7",
        )
        self.label_score.pack()

        # 评分详情
        self.label_score_detail = tk.Label(
            self.score_frame,
            text="点击「录音并评分」开始练习发音",
            font=("", 10),
            fg="#95a5a6",
        )
        self.label_score_detail.pack()

        # 差异提示
        self.label_diff = tk.Label(
            self.score_frame,
            text="",
            font=("", 10),
            fg="#e74c3c",
            wraplength=550,
        )
        self.label_diff.pack(pady=2)

        # 初始状态：清空卡片
        self._clear_card()

    def _clear_card(self):
        """
        清空卡片上显示的所有内容。

        当没有选择课程时调用，显示空状态提示。
        """
        self.label_thai.config(text="")
        self.label_pronunciation.config(text="")
        self.label_word_type.config(text="")
        self.label_meaning.config(text="")
        self.label_example_thai.config(text="")
        self.label_example_pronunciation.config(text="")
        self.label_example_meaning.config(text="")
        self.label_progress.config(text="0/0")
        self.label_lesson_title.config(text="请选择一个课程开始学习")

    def _on_thai_click(self):
        """
        点击泰语文本时的回调。

        点击泰语大字体区域会触发发音播放，
        方便用户快速听读音。
        """
        if self._on_speak_callback and self.current_cards:
            card = self.current_cards[self.current_card_index]
            if card.thai:
                self._on_speak_callback(card.thai)

    def _on_play_click(self):
        """
        点击"播放标准发音"按钮的回调。

        调用注册的外部播放回调函数。
        """
        if self._on_play_callback and self.current_cards:
            card = self.current_cards[self.current_card_index]
            self._on_play_callback(card.thai)

    def _on_record_click(self):
        """
        点击"录音并评分"按钮的回调。

        调用注册的外部录音回调函数。
        """
        if self._on_record_callback and self.current_cards:
            card = self.current_cards[self.current_card_index]
            self._on_record_callback(card.thai)

    def _on_prev_click(self):
        """
        点击"上一张"按钮的回调。

        切换到当前卡片的上一张（循环）。
        """
        if not self.current_cards:
            return
        total = len(self.current_cards)
        self.current_card_index = (self.current_card_index - 1) % total
        self.show_card(self.current_card_index)

    def _on_next_click(self):
        """
        点击"下一张"按钮的回调。

        切换到当前卡片的下一张（循环）。
        """
        if not self.current_cards:
            return
        total = len(self.current_cards)
        self.current_card_index = (self.current_card_index + 1) % total
        self.show_card(self.current_card_index)

    def set_lesson(self, lesson: Optional[Lesson]):
        """
        设置当前课程并显示第一张卡片。

        Args:
            lesson: 要学习的课程对象，为 None 时清空显示
        """
        self.current_lesson = lesson
        self.current_card_index = 0

        if lesson and lesson.cards:
            self.current_cards = lesson.cards
            self.show_card(0)
        else:
            self.current_cards = []
            self._clear_card()

    def show_card(self, index: int):
        """
        显示指定索引的卡片内容。

        Args:
            index: 卡片在 current_cards 列表中的索引
        """
        if not self.current_cards or index < 0 or index >= len(self.current_cards):
            return

        self.current_card_index = index
        card = self.current_cards[index]

        # 更新课程标题和进度
        lesson_title = self.current_lesson.title if self.current_lesson else ""
        self.label_lesson_title.config(text=lesson_title)
        self.label_progress.config(text=f"{index + 1}/{len(self.current_cards)}")

        # 更新卡片内容
        self.label_thai.config(text=card.thai)

        # 发音指南
        pron_text = f"[{card.pronunciation}]" if card.pronunciation else ""
        self.label_pronunciation.config(text=pron_text)

        # 词性标注
        word_type_text = f"({card.word_type})" if card.word_type else ""
        self.label_word_type.config(text=word_type_text)

        # 中文释义（带词性）
        meaning_text = card.meaning
        self.label_meaning.config(text=meaning_text)

        # 例句
        has_example = bool(card.example)
        if has_example:
            self.label_example_thai.config(text=card.example)
            self.label_example_pronunciation.config(
                text=f"[{card.example_pronunciation}]" if card.example_pronunciation else ""
            )
            self.label_example_meaning.config(text=card.example_meaning)

        # 控制例句区域的显示/隐藏
        if has_example:
            self.example_frame.pack(fill=tk.X, pady=5, ipady=5)
        else:
            self.example_frame.pack_forget()

        # 重置评分显示
        self._reset_score_display()

    def _reset_score_display(self):
        """
        重置评分显示区域到初始状态。

        切换卡片时调用，清除之前的评分结果。
        """
        self.label_score.config(text="", fg="#bdc3c7")
        self.label_score_detail.config(text="点击「录音并评分」开始练习发音")

    def show_score(self, score: int, details: dict):
        """
        显示评分结果。

        根据分数显示不同颜色的评分结果和详情。

        Args:
            score: 评分（0-100）
            details: 评分详情字典（来自 scorer.calculate_score 的返回值）
        """
        from core.scorer import get_score_color

        # 分数和等级颜色
        color = get_score_color(score)
        score_text = f"{score} 分 · {details.get('score_level', '')}"

        self.label_score.config(text=score_text, fg=color)

        # 详细对比信息
        expected = details.get("expected_text", "")
        actual = details.get("actual_text", "")

        if details.get("is_exact_match"):
            detail_text = "🎉 完全正确！发音非常标准！"
        else:
            detail_text = (
                f"标准: 「{expected}」\n"
                f"您的发音: 「{actual}」\n"
                f"相似度: {details.get('similarity', 0) * 100:.1f}%"
            )

            # 如果有差异，补充说明
            differences = details.get("differences", [])
            if differences:
                diff_parts = []
                for diff in differences[:5]:  # 最多显示 5 个差异
                    if diff["type"] == "missing":
                        diff_parts.append(f"缺少「{diff['expected_char']}」")
                    elif diff["type"] == "extra":
                        diff_parts.append(f"多余「{diff['actual_char']}」")
                    elif diff["type"] == "mismatch":
                        diff_parts.append(
                            f"「{diff['expected_char']}」→「{diff['actual_char']}」"
                        )
                if diff_parts:
                    detail_text += "\n" + " | ".join(diff_parts)

        self.label_score_detail.config(text=detail_text)

    def show_recording_status(self):
        """
        显示录音中的状态提示。

        在录音过程中调用，替换评分区域的文字为"正在录音..."
        """
        self.label_score.config(text="🎤 正在录音...", fg="#e67e22")
        self.label_score_detail.config(text="请对着麦克风朗读上面的泰语句子")
        self.label_diff.config(text="")

    def show_processing_status(self):
        """
        显示处理中的状态提示。

        在 ASR 识别过程中调用，提示用户正在分析。
        """
        self.label_score.config(text="⏳ 正在分析发音...", fg="#3498db")
        self.label_score_detail.config(text="AI 正在识别您的发音并计算评分")

    def set_play_callback(self, callback):
        """
        设置播放按钮的回调函数。

        Args:
            callback: 回调函数，接受一个参数（泰语文本）
        """
        self._on_play_callback = callback

    def set_record_callback(self, callback):
        """
        设置录音按钮的回调函数。

        Args:
            callback: 回调函数，接受一个参数（泰语文本）
        """
        self._on_record_callback = callback

    def set_speak_callback(self, callback):
        """
        设置点击文本播放发音的回调函数。

        Args:
            callback: 回调函数，接受一个参数（泰语文本）
        """
        self._on_speak_callback = callback

    def get_current_card(self) -> Optional[CardItem]:
        """
        获取当前显示的卡片。

        Returns:
            CardItem: 当前卡片对象，无卡片时返回 None
        """
        if self.current_cards and 0 <= self.current_card_index < len(self.current_cards):
            return self.current_cards[self.current_card_index]
        return None
