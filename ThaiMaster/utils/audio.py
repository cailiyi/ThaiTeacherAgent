"""
音频录制和播放工具模块

提供音频录制（从麦克风）和音频播放功能。
基于 sounddevice 和 soundfile 库实现。

核心功能：
- record_audio(): 录制麦克风输入并保存为 WAV 文件
- play_audio(): 播放音频文件（支持 MP3、WAV）
- list_audio_devices(): 列出可用的音频设备

依赖：
    sounddevice: 跨平台音频录制库（底层基于 PortAudio）
    soundfile: 读写 WAV 文件
    pygame: 用于音频播放（支持多种格式）

注意事项：
    - 首次使用可能需要选择正确的麦克风设备
    - 录音时请保持环境安静，以获得最佳识别效果
    - 播放功能依赖于 pygame.mixer 初始化
"""

import os
import time
import threading
from typing import Optional

import sounddevice as sd
import soundfile as sf

from config import SAMPLE_RATE, RECORD_SECONDS, AUDIO_CHANNELS, AUDIO_TEMP_DIR

# pygame 混音器（用于播放音频）
_pygame_initialized = False


def _ensure_temp_dir():
    """
    确保临时音频目录存在。

    所有录音文件统一保存在 temp_audio 目录下，
    程序退出时不会自动清理，可手动删除。
    """
    os.makedirs(AUDIO_TEMP_DIR, exist_ok=True)


def list_audio_devices() -> list:
    """
    列出系统所有可用的音频设备（输入和输出）。

    包含设备名称、采样率、输入/输出通道数等信息。
    可用于调试麦克风或扬声器问题。

    Returns:
        list: 设备信息字典列表，每个字典包含：
            - index: 设备索引
            - name: 设备名称
            - max_input_channels: 最大输入通道数（0 表示纯输出设备）
            - max_output_channels: 最大输出通道数
            - default_samplerate: 默认采样率

    示例:
        >>> devices = list_audio_devices()
        >>> for d in devices:
        ...     if d["max_input_channels"] > 0:
        ...         print(f"麦克风: {d['name']}")
    """
    devices = []
    try:
        device_list = sd.query_devices()
        for i, device in enumerate(device_list):
            devices.append({
                "index": i,
                "name": device["name"],
                "max_input_channels": device["max_input_channels"],
                "max_output_channels": device["max_output_channels"],
                "default_samplerate": device["default_samplerate"],
            })
    except Exception as e:
        print(f"[音频] 获取设备列表失败: {e}")

    return devices


def record_audio(duration: int = None,
                 samplerate: int = None,
                 filename: str = None,
                 blocking: bool = True) -> str:
    """
    从麦克风录制音频并保存为 WAV 文件。

    这是核心录音函数，支持阻塞和异步两种模式。
    异步模式（blocking=False）在后台线程录音，不会阻塞 UI。

    Args:
        duration: 录音时长（秒），默认使用 config 中的 RECORD_SECONDS
        samplerate: 采样率，默认使用 16000 Hz
        filename: 保存的文件名（不含路径），自动生成唯一名称
        blocking: 是否阻塞等待录音完成

    Returns:
        str: 保存的音频文件路径。如果 blocking=False，返回文件路径占位符。
             录音完成时通过传入的回调函数通知。

    示例:
        >>> # 阻塞模式
        >>> filepath = record_audio(duration=5)
        >>> print(f"录音已保存: {filepath}")
    """
    if duration is None:
        duration = RECORD_SECONDS
    if samplerate is None:
        samplerate = SAMPLE_RATE

    _ensure_temp_dir()

    # 生成唯一文件名
    if filename is None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"

    filepath = os.path.join(AUDIO_TEMP_DIR, filename)

    if blocking:
        # 阻塞模式：直接录制
        return _record_blocking(filepath, duration, samplerate)
    else:
        # 异步模式：启动后台线程
        thread = threading.Thread(
            target=_record_blocking,
            args=(filepath, duration, samplerate),
            daemon=True,
        )
        thread.start()
        return filepath


def _record_blocking(filepath: str, duration: int, samplerate: int) -> str:
    """
    录音的内部阻塞实现。

    使用 sounddevice 录制指定时长的音频，
    并保存为 WAV 文件（16-bit PCM 格式）。

    Args:
        filepath: 保存路径
        duration: 录音时长（秒）
        samplerate: 采样率

    Returns:
        str: 保存的音频文件路径
    """
    try:
        print(f"[录音] 开始录制 {duration} 秒音频...")

        # 录制音频
        audio_data = sd.rec(
            int(duration * samplerate),
            samplerate=samplerate,
            channels=AUDIO_CHANNELS,
            dtype="float32",
        )
        sd.wait()  # 等待录音完成

        # 保存为 WAV 文件
        sf.write(filepath, audio_data, samplerate, subtype="PCM_16")

        file_size = os.path.getsize(filepath)
        print(f"[录音] 录制完成: {filepath} ({file_size/1024:.1f} KB)")
        return filepath

    except Exception as e:
        print(f"[录音错误] {e}")
        return ""


def record_and_wait(duration: int = None,
                    samplerate: int = None,
                    callback: callable = None) -> str:
    """
    录音并等待完成，完成后可选回调通知。

    相比 record_audio，这个函数提供了更灵活的完成通知机制。

    Args:
        duration: 录音时长（秒）
        samplerate: 采样率
        callback: 录音完成后的回调函数，参数为文件路径

    Returns:
        str: 音频文件路径
    """
    filepath = record_audio(duration, samplerate, blocking=True)
    if callback and filepath:
        callback(filepath)
    return filepath


def play_audio(filepath: str, blocking: bool = False) -> bool:
    """
    播放音频文件。

    支持 WAV 和 MP3 格式。使用 pygame.mixer 进行播放。
    首次调用时会自动初始化 pygame。

    Args:
        filepath: 音频文件路径
        blocking: 是否等待播放完成

    Returns:
        bool: 播放是否成功

    示例:
        >>> play_audio("temp_audio/tts_sample.mp3")
        True
    """
    global _pygame_initialized

    if not os.path.exists(filepath):
        print(f"[播放错误] 文件不存在: {filepath}")
        return False

    try:
        # 延迟导入 pygame（避免不必要的依赖加载）
        if not _pygame_initialized:
            import pygame
            pygame.mixer.init(frequency=SAMPLE_RATE)
            _pygame_initialized = True

        import pygame

        # 加载并播放音频
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()

        if blocking:
            # 等待播放完成
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

        print(f"[播放] 正在播放: {filepath}")
        return True

    except Exception as e:
        print(f"[播放错误] {e}")
        return False


def stop_playback():
    """
    停止当前正在播放的音频。

    如果正在播放音频，调用此函数会立即停止。
    如果没有播放，调用此函数无任何效果。
    """
    try:
        if _pygame_initialized:
            import pygame
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                print("[播放] 已停止")
    except Exception as e:
        print(f"[停止错误] {e}")


def get_audio_duration(filepath: str) -> float:
    """
    获取音频文件的时长（秒）。

    使用 soundfile 库读取音频文件信息。

    Args:
        filepath: 音频文件路径

    Returns:
        float: 音频时长（秒），失败返回 0.0
    """
    try:
        with sf.SoundFile(filepath) as f:
            return float(len(f)) / f.samplerate
    except Exception as e:
        print(f"[音频信息错误] {e}")
        return 0.0


def cleanup_temp_files(max_age_hours: int = 24):
    """
    清理临时音频文件。

    删除 temp_audio 目录中超过指定时间的文件，
    避免临时文件占用过多磁盘空间。

    Args:
        max_age_hours: 最大保留时间（小时），默认 24
    """
    _ensure_temp_dir()
    now = time.time()
    deleted_count = 0

    for filename in os.listdir(AUDIO_TEMP_DIR):
        filepath = os.path.join(AUDIO_TEMP_DIR, filename)
        if os.path.isfile(filepath):
            file_age = now - os.path.getmtime(filepath)
            if file_age > max_age_hours * 3600:
                os.remove(filepath)
                deleted_count += 1

    if deleted_count > 0:
        print(f"[清理] 已删除 {deleted_count} 个过期临时文件")


if __name__ == "__main__":
    # 列出音频设备
    print("=== 可用音频设备 ===")
    devices = list_audio_devices()
    for d in devices:
        print(f"  [{d['index']}] {d['name']}")
        if d["max_input_channels"] > 0:
            print(f"      输入通道: {d['max_input_channels']}")
        if d["max_output_channels"] > 0:
            print(f"      输出通道: {d['max_output_channels']}")
        print(f"      采样率: {d['default_samplerate']}")
