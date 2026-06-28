"""
语音识别（ASR）模块

基于 faster-whisper 库，将用户的泰语发音录音转换为文本。
使用 OpenAI Whisper small 模型，在 CPU 上运行。

核心功能：
- 加载 faster-whisper 模型（首次运行自动下载到本地 models/ 目录）
- 将用户录音文件（WAV 格式）转为泰语文本
- 返回识别结果和置信度

依赖：
    faster-whisper（自动下载 whisper small 模型，约 1.5GB）
    soundfile（读取 WAV 文件）

Windows 兼容性说明：
    如果遇到 [WinError 14007] 激活上下文错误，原因是 Windows 在加载
    ctranslate2 的 C 扩展 DLL 时找不到正确的 side-by-side 配置。

    已内置以下处理策略：
    1. 使用本地 models/whisper_cache/ 目录（避免 huggingface 符号链接问题）
    2. 自动重试不同 compute_type（int8 → int8_float16 → float16 → default）
    3. 如果所有尝试都失败，提供清晰的修复指引

    如果问题持续，请尝试：
    pip uninstall faster-whisper ctranslate2 -y
    pip install faster-whisper --no-cache-dir
"""

import os
import time
import glob
import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel
from config import (
    WHISPER_MODEL_SIZE,
    WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE,
    WHISPER_LANGUAGE,
    SAMPLE_RATE,
    WHISPER_DOWNLOAD_ROOT,
)

# 全局模型实例（单例模式，避免重复加载）
_model = None
_model_load_attempted = False


def _get_model():
    """
    获取或初始化 Whisper 模型实例（单例）。

    包含 Windows 兼容性处理：
    - 首次加载失败时自动切换 compute_type 重试
    - 使用本地目录避免符号链接问题
    - 失败时给出清晰的解决指引

    Returns:
        WhisperModel or None: faster-whisper 模型实例，失败返回 None
    """
    global _model, _model_load_attempted

    if _model is not None:
        return _model

    if _model_load_attempted:
        # 已经尝试过加载但失败了，不再重复尝试
        return None

    _model_load_attempted = True

    # 确保下载目录存在
    os.makedirs(WHISPER_DOWNLOAD_ROOT, exist_ok=True)
    print(f"[ASR] 模型将下载到: {WHISPER_DOWNLOAD_ROOT}")

    # 检查是否已有缓存（如果目录非空则可用）
    cached_files = list(glob.glob(os.path.join(WHISPER_DOWNLOAD_ROOT, "**", "*"), recursive=True))
    if cached_files:
        print(f"[ASR] 检测到已有缓存文件 {len(cached_files)} 个")
    else:
        print(f"[ASR] 首次运行，需要下载模型（约 1.5GB），请稍候...")

    # 尝试不同的 compute_type 组合
    compute_types_to_try = [
        WHISPER_COMPUTE_TYPE,       # 配置中指定的（默认 int8）
        "int8_float16",              # int8 的另一种实现
        "float16",                   # 半精度浮点（CPU 上用 int8 转换）
        "default",                   # 使用 ctranslate2 默认值（float32）
    ]

    # 去重：如果配置的 compute_type 排在前面，移除后面的重复项
    seen = set()
    unique_types = []
    for ct in compute_types_to_try:
        if ct not in seen:
            seen.add(ct)
            unique_types.append(ct)

    last_error = None

    for compute_type in unique_types:
        try:
            print(f"[ASR] 尝试加载模型 (compute_type={compute_type})...")
            start_time = time.time()

            _model = WhisperModel(
                model_size_or_path=WHISPER_MODEL_SIZE,
                device=WHISPER_DEVICE,
                compute_type=compute_type,
                download_root=WHISPER_DOWNLOAD_ROOT,
                # 在 Windows 上强制不使用符号链接
                local_files_only=False,
            )

            # 做一个快速测试：用静音音频验证模型能工作
            _dummy = np.zeros(int(0.5 * SAMPLE_RATE), dtype=np.float32)
            _model.transcribe(_dummy, language=WHISPER_LANGUAGE)

            elapsed = time.time() - start_time
            print(f"[ASR] 模型加载成功 (compute_type={compute_type}), 耗时 {elapsed:.1f} 秒")
            return _model

        except Exception as e:
            last_error = e
            error_str = str(e)
            print(f"[ASR] compute_type={compute_type} 加载失败: {error_str[:120]}")

            # 如果是 Windows 激活上下文错误（WinError 14007），
            # 尝试清除 huggingface 符号链接缓存
            if "14007" in error_str or "激活上下文" in error_str:
                print("[ASR] 检测到 Windows 激活上下文错误，尝试修复...")
                _clear_hf_symlinks()
            continue

    # 所有 compute_type 都失败了
    print(f"\n[ASR 错误] 所有尝试均失败。")
    print(f"[ASR 错误] {last_error}")
    print(f"\n[ASR 解决方案] 请尝试以下步骤：")
    print(f"  1. 删除模型缓存: rmdir /s /q \"{WHISPER_DOWNLOAD_ROOT}\"")
    print(f"  2. 重新安装 faster-whisper:")
    print(f"     pip uninstall faster-whisper ctranslate2 -y")
    print(f"     pip install faster-whisper --no-cache-dir")
    print(f"  3. 或在 config.py 中将 WHISPER_MODEL_SIZE 改为 \"base\"（更小的模型）")
    return None


def _clear_hf_symlinks():
    """
    清除 huggingface hub 的符号链接缓存。

    Windows 上 huggingface hub 使用符号链接来管理缓存，
    这经常导致 WinError 14007 激活上下文错误。
    删除 models--Systran--faster-whisper-* 目录中的链接文件，
    下次加载时会重新下载实际文件。
    """
    import shutil

    # 查找 huggingface hub 的缓存目录
    hf_home = os.environ.get(
        "HF_HOME",
        os.path.join(os.environ.get("USERPROFILE", ""), ".cache", "huggingface")
    )
    hub_dir = os.path.join(hf_home, "hub")

    if not os.path.exists(hub_dir):
        return

    # 查找与 faster-whisper 相关的缓存
    pattern = os.path.join(hub_dir, "models--Systran--faster-whisper-*")
    for model_dir in glob.glob(pattern):
        blobs_dir = os.path.join(model_dir, "blobs")
        snapshots_dir = os.path.join(model_dir, "snapshots")

        print(f"[ASR 修复] 清理缓存: {model_dir}")

        # 删除 blobs 目录（包含符号链接文件）
        if os.path.exists(blobs_dir):
            try:
                shutil.rmtree(blobs_dir, ignore_errors=True)
                print(f"[ASR 修复] 已删除: {blobs_dir}")
            except Exception as e:
                print(f"[ASR 修复] 删除 blobs 失败: {e}")

        # 删除 snapshots 目录（包含符号链接文件）
        if os.path.exists(snapshots_dir):
            try:
                shutil.rmtree(snapshots_dir, ignore_errors=True)
                print(f"[ASR 修复] 已删除: {snapshots_dir}")
            except Exception as e:
                print(f"[ASR 修复] 删除 snapshots 失败: {e}")

    print("[ASR 修复] 缓存清理完成，下次加载会重新下载模型")


def transcribe(audio_path: str) -> dict:
    """
    对音频文件进行语音识别，返回识别结果。

    支持 WAV 格式的音频文件，采样率会自动适配。
    默认识别为泰语，如需自动检测语言可将 language 设为 None。

    Args:
        audio_path: 音频文件路径（WAV 格式，建议 16kHz 采样率）

    Returns:
        dict: 包含以下字段的识别结果字典：
            - success (bool): 是否识别成功
            - text (str): 识别出的泰语文本
            - confidence (float): 平均置信度（0.0 ~ 1.0）
            - duration (float): 音频时长（秒）
            - error (str): 错误信息（success 为 False 时）

    示例:
        >>> result = transcribe("temp_audio/recording.wav")
        >>> print(result["text"])  # "สวัสดี"
        >>> print(result["confidence"])  # 0.92
    """
    result = {
        "success": False,
        "text": "",
        "confidence": 0.0,
        "duration": 0.0,
        "error": "",
    }

    # 检查音频文件是否存在
    if not os.path.exists(audio_path):
        result["error"] = f"音频文件不存在: {audio_path}"
        return result

    # 检查模型是否可用
    model = _get_model()
    if model is None:
        result["error"] = (
            "模型加载失败，请参考上方提示修复。\n"
            "快速修复: pip uninstall faster-whisper ctranslate2 -y "
            "&& pip install faster-whisper --no-cache-dir"
        )
        print(f"[ASR 错误] {result['error']}")
        return result

    try:
        # 加载音频文件
        audio_data, sr = sf.read(audio_path)

        # 确保是单声道
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)

        # 重采样到 16kHz（如果采样率不匹配）
        if sr != SAMPLE_RATE:
            import scipy.signal
            target_len = int(len(audio_data) * SAMPLE_RATE / sr)
            audio_data = scipy.signal.resample(audio_data, target_len)
            sr = SAMPLE_RATE

        # 确保是 float32 类型（Whisper 要求 float32，而 sf.read 可能返回 float64）
        audio_data = audio_data.astype(np.float32)

        result["duration"] = len(audio_data) / sr

        # 执行语音识别
        print(f"[ASR] 正在识别泰语语音...")
        segments, info = model.transcribe(
            audio_data,
            language=WHISPER_LANGUAGE,
            beam_size=5,
            vad_filter=True,         # 启用语音活动检测，过滤静音
            vad_parameters=dict(
                threshold=0.5,         # VAD 阈值
                min_speech_duration_ms=500,
                max_speech_duration_s=30,
            ),
        )

        # 收集所有识别片段
        full_text = ""
        total_confidence = 0.0
        segment_count = 0

        for segment in segments:
            full_text += segment.text + " "
            total_confidence += segment.avg_logprob
            segment_count += 1

            # 打印每个片段的详细信息（调试用）
            print(f"[ASR] 片段 [{segment.start:.1f}s-{segment.end:.1f}s]: "
                  f"'{segment.text}' (置信度: {segment.avg_logprob:.2f})")

        full_text = full_text.strip()

        # 计算平均置信度（将 log prob 映射到 0-1 范围）
        avg_confidence = 0.0
        if segment_count > 0:
            avg_logprob = total_confidence / segment_count
            # log_prob 通常在 -1 到 0 之间，映射到 0-1
            avg_confidence = max(0, min(1, 1 + avg_logprob))

        if full_text:
            result["success"] = True
            result["text"] = full_text
            result["confidence"] = round(avg_confidence, 3)
            print(f"[ASR] 识别完成: '{full_text}' (置信度: {avg_confidence:.2%})")
        else:
            result["error"] = "未能识别到任何语音内容"
            print(f"[ASR] 警告: 没有识别到语音内容")

    except Exception as e:
        result["error"] = f"语音识别错误: {str(e)}"
        print(f"[ASR 错误] {result['error']}")

    return result


def transcribe_text(audio_path: str) -> str:
    """
    简化接口：只返回识别出的文字，不返回详细信息。

    对于只需要文本的场景，此函数更简洁。

    Args:
        audio_path: 音频文件路径

    Returns:
        str: 识别出的泰语文本，失败返回空字符串
    """
    result = transcribe(audio_path)
    return result.get("text", "")


if __name__ == "__main__":
    # 测试：加载模型（不进行识别）
    print("=== 测试模型加载 ===")
    model = _get_model()
    if model:
        print("模型加载成功！")
    else:
        print("模型加载失败")
