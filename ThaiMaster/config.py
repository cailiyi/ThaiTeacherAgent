"""
ThaiMaster 配置文件

包含项目中所有可配置的参数，如模型路径、音频设置、评分阈值等。
通过修改此文件可以调整应用行为而无需修改核心代码。
"""

# ==================== Whisper 语音识别配置 ====================
WHISPER_MODEL_SIZE = "small"
"""Whisper 模型大小，可选值: tiny, base, small, medium, large"""

WHISPER_LANGUAGE = "th"
"""语音识别的目标语言代码，泰语为 "th" """

# ==================== TTS 文本转语音配置 ====================
TTS_VOICE = "th-TH-Premium"
"""Edge TTS 使用的泰语语音包名称"""

TTS_RATE = "+0%"
"""TTS 语速，默认正常速度，可设置为 "+50%" 或 "-25%" """

TTS_VOLUME = "+0%"
"""TTS 音量，默认正常音量"""

# ==================== 音频配置 ====================
AUDIO_SAMPLE_RATE = 16000
"""音频采样率，Whisper 推荐使用 16000Hz"""

AUDIO_CHANNELS = 1
"""音频通道数，1 表示单声道"""

AUDIO_FORMAT = "wav"
"""音频文件格式，支持 wav, mp3"""

RECORD_DURATION = 5
"""默认录音时长（秒）"""

# ==================== 评分配置 ====================
SCORE_THRESHOLD_EXCELLENT = 0.9
"""优秀评分阈值，高于此值判定为优秀"""

SCORE_THRESHOLD_GOOD = 0.7
"""良好评分阈值，高于此值判定为良好"""

SCORE_THRESHOLD_PASS = 0.5
"""及格评分阈值，高于此值判定为及格"""

# ==================== 课程配置 ====================
DEFAULT_COURSE_LEVEL = "N5"
"""默认课程级别，可选值: N5, N4, N3, N2, N1"""

COURSE_LEVELS = {
    "N5": "入门级",
    "N4": "初级",
    "N3": "中级",
    "N2": "中高级",
    "N1": "高级"
}
"""课程级别映射字典，键为级别代码，值为中文名称"""

# ==================== GUI 配置 ====================
APP_TITLE = "ThaiMaster - 泰语学习助手"
"""应用窗口标题"""

APP_WIDTH = 600
"""应用窗口宽度（像素）"""

APP_HEIGHT = 500
"""应用窗口高度（像素）"""

FONT_SIZE_LARGE = 36
"""泰语单词显示字体大小"""

FONT_SIZE_MEDIUM = 16
"""普通文本字体大小"""

FONT_SIZE_SMALL = 12
"""小字文本字体大小"""

# ==================== 路径配置 ====================
TEMP_AUDIO_DIR = "temp"
"""临时音频文件存放目录"""

OUTPUT_AUDIO_DIR = "output"
"""输出音频文件存放目录"""
