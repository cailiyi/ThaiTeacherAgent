"""
ThaiMaster 配置文件

本文件集中管理所有可配置参数，包括：
- 语音识别模型（whisper）的型号和运行设备
- 音频录制参数（采样率、时长等）
- 发音评分阈值
- 应用窗口尺寸
- 课程等级列表
- 文件路径配置

修改本文件即可调整应用行为，无需深入业务逻辑代码。
"""

import os

# ============================================================
# 语音识别（ASR）配置
# ============================================================
# faster-whisper 支持的模型大小: tiny, base, small, medium, large-v3
# 在 CPU 上推荐使用 small 或 base，速度与准确率平衡较好
# 你的 i5-7200U + 32GB RAM 运行 small 模型约需 2-4 秒/次识别
WHISPER_MODEL_SIZE = "small"

# 运行设备: "cpu" 或 "cuda"
# 你的 NVIDIA GeForce 940MX 只有 2GB 显存，不够运行 whisper 模型
# 因此强烈建议使用 cpu
WHISPER_DEVICE = "cpu"

# 计算精度: "float16" | "int8_float16" | "int8"
# CPU 上推荐 "int8" 以提升速度
WHISPER_COMPUTE_TYPE = "int8"

# 语言设置（Thai = "th"，不指定则自动检测）
WHISPER_LANGUAGE = "th"

# 课程级别标签（从易到难）
COURSE_LEVELS = [
    "N5 入门级",
    "N4 初级",
    "N3 中级",
    "N2 中高级",
    "N1 高级"
]


# ============================================================
# 路径配置
# ============================================================
# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据目录
DATA_DIR = os.path.join(BASE_DIR, "data")

# 临时音频文件目录（用于录音和 TTS 缓存）
AUDIO_TEMP_DIR = os.path.join(BASE_DIR, "temp_audio")

# 模型下载根目录（避免 Windows 符号链接问题）
WHISPER_DOWNLOAD_ROOT = os.path.join(BASE_DIR, "models", "whisper_cache")


# ============================================================
# 音频录制配置
# ============================================================
# 采样率（Hz），whisper 要求 16000
SAMPLE_RATE = 16000

# 每次录音的默认时长（秒）
RECORD_SECONDS = 5

# 音频通道数（单声道）
AUDIO_CHANNELS = 1


# ============================================================
# 发音评分配置
# ============================================================
# 及格分数线（0-100）
SCORE_THRESHOLD_PASS = 60

# 良好分数线（0-100）
SCORE_THRESHOLD_GOOD = 80

# 优秀分数线
SCORE_THRESHOLD_EXCELLENT = 90


# ============================================================
# 应用界面配置
# ============================================================
APP_TITLE = "ThaiMaster - 泰语学习助手"
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700

# 卡片区域的宽高比
CARD_WIDTH = 600
CARD_HEIGHT = 300
