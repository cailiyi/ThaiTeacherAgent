"""
泰语语音识别模块

使用 faster-whisper 库进行泰语语音识别。
faster-whisper 是 OpenAI Whisper 的优化版本，支持 CPU 运行，速度更快。
"""

import os
from typing import Optional, Dict, Any

from faster_whisper import WhisperModel

from ThaiMaster.config import (
    WHISPER_MODEL_SIZE,
    WHISPER_LANGUAGE
)


class ThaiASR:
    """泰语语音识别处理器
    
    使用 faster-whisper 模型将音频转换为泰语文本。
    """
    
    def __init__(self):
        """初始化泰语ASR处理器"""
        self._model_size = WHISPER_MODEL_SIZE
        self._language = WHISPER_LANGUAGE
        self._model = None
        
        # 懒加载模型，首次使用时加载
        print(f"初始化泰语ASR，模型大小: {self._model_size}")
    
    def _load_model(self):
        """加载 Whisper 模型
        
        如果模型尚未加载，则进行加载。
        使用 CPU 运行，确保兼容性。
        """
        if self._model is None:
            print(f"正在加载 Whisper 模型: {self._model_size}...")
            try:
                # 使用 CPU 运行，设置 compute_type 为 int8 以提高速度
                self._model = WhisperModel(
                    self._model_size,
                    device="cpu",
                    compute_type="int8"
                )
                print("模型加载完成")
            except Exception as e:
                print(f"模型加载失败: {e}")
                raise
    
    def recognize(self, audio_file: str) -> Dict[str, Any]:
        """识别音频文件中的泰语文本
        
        参数:
            audio_file: 音频文件路径（WAV格式）
            
        返回:
            Dict[str, Any]: 识别结果字典，包含以下字段:
                - text: 识别出的文本
                - segments: 分段识别结果
                - confidence: 识别置信度
            
        抛出:
            FileNotFoundError: 如果音频文件不存在
            RuntimeError: 如果模型加载失败
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"音频文件不存在: {audio_file}")
        
        # 确保模型已加载
        self._load_model()
        
        print(f"正在识别音频: {audio_file}")
        
        # 进行语音识别
        segments, info = self._model.transcribe(
            audio_file,
            language=self._language,
            beam_size=5
        )
        
        # 收集识别结果
        text = ""
        segments_list = []
        total_confidence = 0
        segment_count = 0
        
        for segment in segments:
            text += segment.text.strip() + " "
            segments_list.append({
                "text": segment.text.strip(),
                "start": segment.start,
                "end": segment.end,
                "confidence": segment.confidence
            })
            total_confidence += segment.confidence
            segment_count += 1
        
        # 计算平均置信度
        avg_confidence = total_confidence / segment_count if segment_count > 0 else 0
        
        print(f"识别完成: {text.strip()} (置信度: {avg_confidence:.2f})")
        
        return {
            "text": text.strip(),
            "segments": segments_list,
            "confidence": avg_confidence
        }
    
    def set_model_size(self, model_size: str):
        """设置模型大小
        
        参数:
            model_size: 模型大小，可选值: tiny, base, small, medium, large
            
        注意:
            修改模型大小后需要重新加载模型
        """
        self._model_size = model_size
        self._model = None  # 标记模型需要重新加载
    
    def set_language(self, language: str):
        """设置识别语言
        
        参数:
            language: 语言代码，泰语为 "th"
        """
        self._language = language
    
    def get_model_size(self) -> str:
        """获取当前模型大小
        
        返回:
            str: 当前使用的模型大小
        """
        return self._model_size


# 创建全局泰语ASR实例
thai_asr = ThaiASR()
"""全局泰语ASR实例，用于在应用中共享"""
