"""
泰语文本转语音（TTS）模块

基于微软 edge-tts 库，调用在线 Edge 浏览器 TTS 服务，
生成泰语标准发音的音频文件。

核心功能：
- 将泰语文本转换为 MP3 音频文件
- 自动选择泰语语音（支持泰语发音）
- 生成的文件可被播放模块调用播放

依赖：
    edge-tts（需联网，首次使用自动下载语音模型）

注意事项：
    - 本模块需要互联网连接才能工作
    - 生成的音频文件保存在 temp_audio 目录下
    - 如果 edge-tts 发音不理想，可尝试切换不同语音角色
"""

import asyncio
import os
import edge_tts
from config import AUDIO_TEMP_DIR


# 泰语语音角色列表
# edge-tts 支持的泰语语音
THAI_VOICES = [
    "th-TH-PremwadeeNeural",   # 女性语音，标准泰语（推荐）
    "th-TH-NiwatNeural",       # 男性语音，标准泰语
]

# 默认使用的语音角色（索引 0 为女性语音）
DEFAULT_VOICE = THAI_VOICES[0]


def _ensure_temp_dir():
    """
    确保临时音频目录存在。

    如果 temp_audio 目录不存在则自动创建，
    所有 TTS 生成的音频文件都保存在此目录中。
    """
    os.makedirs(AUDIO_TEMP_DIR, exist_ok=True)


def get_available_voices() -> list:
    """
    获取可用的泰语语音角色列表。

    Returns:
        list: 语音角色名称列表
    """
    return THAI_VOICES.copy()


async def _async_speak(text: str, voice: str = DEFAULT_VOICE,
                       rate: str = "+0%", volume: str = "+0%") -> str:
    """
    异步执行 TTS 转换的核心函数。

    使用 edge-tts 将文本转为音频文件，支持调节语速和音量。

    Args:
        text: 要朗读的泰语文本
        voice: 语音角色，默认使用泰语女性语音
        rate: 语速调节，如 "+10%" 加速 10%，"-10%" 减速 10%
        volume: 音量调节，如 "+20%" 提高 20%

    Returns:
        str: 生成的音频文件路径

    Raises:
        Exception: TTS 生成失败时抛出
    """
    _ensure_temp_dir()

    # 生成唯一文件名（用文本哈希避免重复生成）
    import hashlib
    text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()[:12]
    output_file = os.path.join(AUDIO_TEMP_DIR, f"tts_{text_hash}.mp3")

    # 如果文件已存在，直接返回（避免重复请求）
    if os.path.exists(output_file):
        return output_file

    # 调用 edge-tts 生成语音
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate, volume=volume)
    await communicate.save(output_file)

    return output_file


def speak(text: str, voice: str = DEFAULT_VOICE,
          rate: str = "+0%", volume: str = "+0%") -> str:
    """
    将泰语文本转换为语音文件（同步接口）。

    这是外部调用的入口函数，内部通过 asyncio.run() 执行异步操作。
    tkinter 界面中直接调用此函数即可。

    Args:
        text: 要朗读的泰语文本
        voice: 语音角色名称
        rate: 语速（默认正常）
        volume: 音量（默认正常）

    Returns:
        str: 生成的音频文件路径，失败时返回空字符串

    示例:
        >>> audio_file = speak("สวัสดี")
        >>> print(audio_file)  # 输出: temp_audio/tts_xxxx.mp3
    """
    try:
        return asyncio.run(_async_speak(text, voice, rate, volume))
    except Exception as e:
        print(f"[TTS 错误] 生成语音失败: {e}")
        return ""


def change_voice(voice_idx: int) -> str:
    """
    切换 TTS 语音角色。

    Args:
        voice_idx: 语音角色索引（0 为女性，1 为男性）

    Returns:
        str: 当前使用的语音角色名称
    """
    global DEFAULT_VOICE
    if 0 <= voice_idx < len(THAI_VOICES):
        DEFAULT_VOICE = THAI_VOICES[voice_idx]
    return DEFAULT_VOICE


if __name__ == "__main__":
    # 简单测试
    audio = speak("สวัสดีครับ สบายดีไหม")
    print(f"生成的音频文件: {audio}")
