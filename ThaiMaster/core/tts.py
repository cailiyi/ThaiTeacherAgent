"""
泰语文本转语音模块

使用 Edge TTS API 将泰语文本转换为语音。
Edge TTS 是微软提供的免费文本转语音服务，支持多种语言和音色。
"""

import os
import asyncio
from typing import Optional

import edge_tts

from ThaiMaster.config import (
    TTS_VOICE,
    TTS_RATE,
    TTS_VOLUME,
    TEMP_AUDIO_DIR,
    AUDIO_FORMAT
)


class ThaiTTS:
    """泰语文本转语音处理器
    
    使用 edge-tts 库调用微软语音服务，生成泰语语音。
    """
    
    def __init__(self):
        """初始化泰语TTS处理器"""
        self._voice = TTS_VOICE
        self._rate = TTS_RATE
        self._volume = TTS_VOLUME
        
        # 确保临时目录存在
        os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
    
    def _get_output_filename(self, text: str) -> str:
        """生成输出文件名
        
        根据文本内容生成唯一的文件名，避免重复。
        
        参数:
            text: 要转换的文本
            
        返回:
            str: 输出文件路径
        """
        # 使用文本的哈希值生成文件名
        hash_value = hash(text)
        filename = f"tts_{abs(hash_value)}.{AUDIO_FORMAT}"
        return os.path.join(TEMP_AUDIO_DIR, filename)
    
    async def _generate_audio(self, text: str, output_file: str) -> str:
        """异步生成音频文件
        
        参数:
            text: 要转换的泰语文本
            output_file: 输出文件路径
            
        返回:
            str: 生成的音频文件路径
        """
        # 创建 TTS 通信对象
        communicate = edge_tts.Communicate(
            text=text,
            voice=self._voice,
            rate=self._rate,
            volume=self._volume
        )
        
        # 生成音频文件
        await communicate.save(output_file)
        return output_file
    
    def speak(self, text: str, output_file: Optional[str] = None) -> str:
        """生成泰语语音并保存为音频文件
        
        参数:
            text: 要转换的泰语文本
            output_file: 输出文件路径，默认为自动生成
            
        返回:
            str: 生成的音频文件路径
            
        抛出:
            ValueError: 如果文本为空
        """
        if not text or not text.strip():
            raise ValueError("文本不能为空")
        
        # 如果未指定输出文件，自动生成
        if output_file is None:
            output_file = self._get_output_filename(text)
        
        print(f"正在生成泰语语音: {text}")
        
        # 运行异步任务
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果事件循环正在运行，创建新任务
            task = loop.create_task(self._generate_audio(text, output_file))
            loop.run_until_complete(task)
        else:
            # 否则直接运行
            loop.run_until_complete(self._generate_audio(text, output_file))
        
        print(f"语音生成完成，保存到: {output_file}")
        return output_file
    
    def set_voice(self, voice: str):
        """设置语音包
        
        参数:
            voice: 语音包名称，如 "th-TH-Premium"
        """
        self._voice = voice
    
    def set_rate(self, rate: str):
        """设置语速
        
        参数:
            rate: 语速值，如 "+0%", "+50%", "-25%"
        """
        self._rate = rate
    
    def set_volume(self, volume: str):
        """设置音量
        
        参数:
            volume: 音量值，如 "+0%", "+50%"
        """
        self._volume = volume


# 创建全局泰语TTS实例
thai_tts = ThaiTTS()
"""全局泰语TTS实例，用于在应用中共享"""
