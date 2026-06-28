"""
音频工具模块

提供录音和播放功能，基于 pyaudio 实现。
主要功能：
- 录制麦克风输入的音频
- 播放音频文件
- 管理临时音频文件
"""

import os
import wave
import pyaudio
from typing import Optional

from ThaiMaster.config import (
    AUDIO_SAMPLE_RATE,
    AUDIO_CHANNELS,
    RECORD_DURATION,
    TEMP_AUDIO_DIR
)


class AudioRecorder:
    """音频录制器
    
    使用 pyaudio 录制麦克风输入的音频，保存为 WAV 文件。
    """
    
    def __init__(self):
        """初始化音频录制器"""
        self._pyaudio = pyaudio.PyAudio()
        self._stream = None
        self._is_recording = False
        
        # 确保临时目录存在
        os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
    
    def _get_audio_format(self) -> int:
        """获取音频格式
        
        返回:
            int: pyaudio 格式常量，这里使用 paInt16（16位整数）
        """
        return pyaudio.paInt16
    
    def _get_sample_width(self) -> int:
        """获取样本宽度（字节）
        
        返回:
            int: 每个样本的字节数，16位为2字节
        """
        return self._pyaudio.get_sample_size(self._get_audio_format())
    
    def start_recording(self, duration: Optional[int] = None) -> str:
        """开始录制音频
        
        参数:
            duration: 录制时长（秒），默认使用配置文件中的 RECORD_DURATION
            
        返回:
            str: 录制的音频文件路径
            
        抛出:
            RuntimeError: 如果正在录制中
        """
        if self._is_recording:
            raise RuntimeError("正在录制中，无法重复开始")
        
        duration = duration or RECORD_DURATION
        self._is_recording = True
        
        # 创建临时文件名
        temp_file = os.path.join(TEMP_AUDIO_DIR, "recording.wav")
        
        # 打开音频流
        self._stream = self._pyaudio.open(
            format=self._get_audio_format(),
            channels=AUDIO_CHANNELS,
            rate=AUDIO_SAMPLE_RATE,
            input=True,
            frames_per_buffer=1024
        )
        
        print(f"开始录制，时长 {duration} 秒...")
        
        # 录制音频数据
        frames = []
        for _ in range(0, int(AUDIO_SAMPLE_RATE / 1024 * duration)):
            data = self._stream.read(1024)
            frames.append(data)
        
        # 停止录制
        self._stream.stop_stream()
        self._stream.close()
        self._stream = None
        self._is_recording = False
        
        # 保存为 WAV 文件
        with wave.open(temp_file, 'wb') as wf:
            wf.setnchannels(AUDIO_CHANNELS)
            wf.setsampwidth(self._get_sample_width())
            wf.setframerate(AUDIO_SAMPLE_RATE)
            wf.writeframes(b''.join(frames))
        
        print(f"录制完成，保存到: {temp_file}")
        return temp_file
    
    def is_recording(self) -> bool:
        """检查是否正在录制
        
        返回:
            bool: True 表示正在录制，False 表示未录制
        """
        return self._is_recording
    
    def close(self):
        """关闭音频录制器，释放资源"""
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
        self._pyaudio.terminate()


class AudioPlayer:
    """音频播放器
    
    使用 pyaudio 播放 WAV 格式的音频文件。
    """
    
    def __init__(self):
        """初始化音频播放器"""
        self._pyaudio = pyaudio.PyAudio()
        self._stream = None
        self._is_playing = False
    
    def play(self, file_path: str):
        """播放音频文件
        
        参数:
            file_path: 音频文件路径（WAV格式）
            
        抛出:
            FileNotFoundError: 如果文件不存在
            RuntimeError: 如果正在播放中
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"音频文件不存在: {file_path}")
        
        if self._is_playing:
            raise RuntimeError("正在播放中，无法重复播放")
        
        self._is_playing = True
        
        # 打开 WAV 文件
        with wave.open(file_path, 'rb') as wf:
            # 打开音频流
            self._stream = self._pyaudio.open(
                format=self._pyaudio.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True
            )
            
            print(f"开始播放音频: {file_path}")
            
            # 播放音频数据
            chunk = 1024
            data = wf.readframes(chunk)
            while data != b'':
                self._stream.write(data)
                data = wf.readframes(chunk)
            
            # 停止播放
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
            self._is_playing = False
        
        print("播放完成")
    
    def is_playing(self) -> bool:
        """检查是否正在播放
        
        返回:
            bool: True 表示正在播放，False 表示未播放
        """
        return self._is_playing
    
    def close(self):
        """关闭音频播放器，释放资源"""
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
        self._pyaudio.terminate()


# 创建全局音频录制器和播放器实例
audio_recorder = AudioRecorder()
"""全局音频录制器实例"""

audio_player = AudioPlayer()
"""全局音频播放器实例"""
