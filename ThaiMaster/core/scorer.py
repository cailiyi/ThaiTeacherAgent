"""
发音评分模块

基于 Levenshtein 编辑距离算法对发音进行评分。
通过比较用户录音识别出的文本与标准文本的相似度来评估发音准确性。
"""

from typing import Dict, Any
from Levenshtein import distance as levenshtein_distance

from ThaiMaster.config import (
    SCORE_THRESHOLD_EXCELLENT,
    SCORE_THRESHOLD_GOOD,
    SCORE_THRESHOLD_PASS
)


class PronunciationScorer:
    """发音评分器
    
    使用 Levenshtein 编辑距离计算用户发音与标准发音的相似度。
    编辑距离越小，相似度越高，评分也越高。
    """
    
    def __init__(self):
        """初始化发音评分器"""
        self._excellent_threshold = SCORE_THRESHOLD_EXCELLENT
        self._good_threshold = SCORE_THRESHOLD_GOOD
        self._pass_threshold = SCORE_THRESHOLD_PASS
    
    def _normalize_text(self, text: str) -> str:
        """标准化文本
        
        移除多余空格、标点符号，转换为小写（如果适用）。
        
        参数:
            text: 原始文本
            
        返回:
            str: 标准化后的文本
        """
        if not text:
            return ""
        
        # 移除首尾空格
        text = text.strip()
        
        # 移除标点符号
        punctuation = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
        text = ''.join(char for char in text if char not in punctuation)
        
        # 合并多个空格为一个
        text = ' '.join(text.split())
        
        return text
    
    def _calculate_similarity(self, reference: str, target: str) -> float:
        """计算两个文本的相似度
        
        使用 Levenshtein 编辑距离计算相似度。
        相似度 = 1 - (编辑距离 / 最大长度)
        
        参数:
            reference: 参考文本（标准发音）
            target: 目标文本（用户发音识别结果）
            
        返回:
            float: 相似度，范围 0.0 ~ 1.0
        """
        if not reference and not target:
            return 1.0
        
        if not reference or not target:
            return 0.0
        
        # 标准化文本
        ref_norm = self._normalize_text(reference)
        tgt_norm = self._normalize_text(target)
        
        if not ref_norm and not tgt_norm:
            return 1.0
        
        if not ref_norm or not tgt_norm:
            return 0.0
        
        # 计算编辑距离
        dist = levenshtein_distance(ref_norm, tgt_norm)
        
        # 计算相似度
        max_len = max(len(ref_norm), len(tgt_norm))
        similarity = 1.0 - (dist / max_len)
        
        return max(0.0, min(1.0, similarity))
    
    def _get_grade(self, score: float) -> str:
        """根据分数获取评级
        
        参数:
            score: 评分值，范围 0.0 ~ 1.0
            
        返回:
            str: 评级，可选值: 优秀, 良好, 及格, 不及格
        """
        if score >= self._excellent_threshold:
            return "优秀"
        elif score >= self._good_threshold:
            return "良好"
        elif score >= self._pass_threshold:
            return "及格"
        else:
            return "不及格"
    
    def _get_feedback(self, score: float, reference: str, target: str) -> str:
        """生成反馈信息
        
        根据评分和识别结果生成具体的反馈建议。
        
        参数:
            score: 评分值
            reference: 参考文本
            target: 用户识别文本
            
        返回:
            str: 反馈信息
        """
        if score >= self._excellent_threshold:
            return "太棒了！发音非常标准，请继续保持！"
        elif score >= self._good_threshold:
            return "不错！发音比较标准，继续努力！"
        elif score >= self._pass_threshold:
            return f"还需要练习。标准发音: {reference}，你的发音: {target}"
        else:
            return f"请多听标准发音并模仿。标准发音: {reference}，你的发音: {target}"
    
    def score(self, reference_text: str, recognized_text: str) -> Dict[str, Any]:
        """对发音进行评分
        
        参数:
            reference_text: 标准文本（期望发音的文本）
            recognized_text: 识别文本（用户发音识别出的文本）
            
        返回:
            Dict[str, Any]: 评分结果字典，包含以下字段:
                - score: 评分值（0.0 ~ 1.0）
                - grade: 评级（优秀, 良好, 及格, 不及格）
                - feedback: 反馈建议
                - reference: 标准化后的参考文本
                - recognized: 标准化后的识别文本
        """
        print(f"正在评分 - 参考: {reference_text}, 识别: {recognized_text}")
        
        # 计算相似度
        similarity = self._calculate_similarity(reference_text, recognized_text)
        
        # 获取评级
        grade = self._get_grade(similarity)
        
        # 生成反馈
        feedback = self._get_feedback(similarity, reference_text, recognized_text)
        
        # 标准化文本用于显示
        ref_norm = self._normalize_text(reference_text)
        rec_norm = self._normalize_text(recognized_text)
        
        result = {
            "score": round(similarity, 4),
            "grade": grade,
            "feedback": feedback,
            "reference": ref_norm,
            "recognized": rec_norm
        }
        
        print(f"评分完成 - 分数: {result['score']}, 评级: {result['grade']}")
        
        return result
    
    def set_thresholds(self, excellent: float, good: float, pass_: float):
        """设置评分阈值
        
        参数:
            excellent: 优秀阈值
            good: 良好阈值
            pass_: 及格阈值
            
        注意:
            阈值应满足: excellent > good > pass_
        """
        self._excellent_threshold = excellent
        self._good_threshold = good
        self._pass_threshold = pass_


# 创建全局发音评分器实例
pronunciation_scorer = PronunciationScorer()
"""全局发音评分器实例，用于在应用中共享"""
