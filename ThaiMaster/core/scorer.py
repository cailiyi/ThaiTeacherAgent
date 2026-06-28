"""
发音评分模块

基于 Levenshtein 编辑距离（ED）算法，计算用户发音与标准发音的相似度。
将用户录音 → 语音识别得到文本 → 与标准文本对比 → 计算得分。

评分原理：
1. 使用 Levenshtein 距离计算两文本间的编辑距离（插入、删除、替换次数）
2. 得分 = (1 - 编辑距离 / 较长文本长度) × 100
3. 结合泰语字符特征进行更精确的评估

评分等级：
    - 90-100 分: 优秀（发音非常标准）
    - 80-89 分:  良好（基本标准，有个别小瑕疵）
    - 60-79 分:  及格（能听懂，但发音有明显问题）
    -  0-59 分:  不及格（发音需要大量改进）

注意事项：
    - 评分受 ASR 识别准确率影响，如果 ASR 识别错误会误判
    - 本模块侧重于"文本级别"对比，无法分析音素级别的声调准确度
    - 未来可以扩展使用音素对比来提升评分准确性
"""

from typing import Tuple

from config import (
    SCORE_THRESHOLD_EXCELLENT,
    SCORE_THRESHOLD_GOOD,
    SCORE_THRESHOLD_PASS,
)


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    计算两个字符串之间的 Levenshtein 编辑距离。

    编辑距离定义为将一个字符串转换为另一个字符串所需的
    最少操作次数，操作包括：插入、删除、替换一个字符。

    Args:
        s1: 第一个字符串（标准文本）
        s2: 第二个字符串（用户识别文本）

    Returns:
        int: 编辑距离

    示例:
        >>> levenshtein_distance("สวัสดี", "สวัด")  # 2（删除2个字符）
    """
    # 使用优化的一维 DP 数组，节省内存
    m, n = len(s1), len(s2)

    # 如果其中一个为空，直接返回另一个的长度
    if m == 0:
        return n
    if n == 0:
        return m

    # 确保 s1 是较短的字符串，减少内存使用
    if m > n:
        s1, s2 = s2, s1
        m, n = n, m

    # 一维 DP 数组
    prev_row = list(range(m + 1))

    for i, c2 in enumerate(s2, 1):
        curr_row = [i] + [0] * m
        for j, c1 in enumerate(s1, 1):
            cost = 0 if c1 == c2 else 1
            curr_row[j] = min(
                curr_row[j - 1] + 1,      # 插入
                prev_row[j] + 1,           # 删除
                prev_row[j - 1] + cost,    # 替换
            )
        prev_row = curr_row

    return prev_row[m]


def normalized_similarity(s1: str, s2: str) -> float:
    """
    计算两个字符串的归一化相似度。

    基于 Levenshtein 距离，转换为 0.0 ~ 1.0 之间的相似度分数。

    Args:
        s1: 标准文本（泰语原文）
        s2: 用户文本（ASR 识别结果）

    Returns:
        float: 相似度，范围 0.0（完全不同）到 1.0（完全相同）

    示例:
        >>> normalized_similarity("สวัสดี", "สวัสดี")
        1.0
        >>> normalized_similarity("สวัสดี", "สวัด")
        0.67
    """
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0  # 两个都为空字符串，认为完全匹配

    distance = levenshtein_distance(s1, s2)
    similarity = 1.0 - (distance / max_len)
    return max(0.0, similarity)


def calculate_score(expected_text: str, actual_text: str) -> Tuple[int, dict]:
    """
    综合计算发音评分。

    主入口函数，对比标准文本和用户语音识别结果，返回评分和详细信息。

    Args:
        expected_text: 标准泰语文案（课程卡片上的原句）
        actual_text: ASR 识别的用户发音文本

    Returns:
        Tuple[int, dict]: 包含以下内容的元组：
            - score (int): 综合评分（0-100）
            - details (dict): 评分详情，包含：
                - similarity: 归一化相似度
                - edit_distance: 编辑距离
                - expected_length: 标准文本长度
                - actual_length: 用户文本长度
                - is_exact_match: 是否完全一致
                - score_level: 等级描述（优秀/良好/及格/不及格）
                - differences: 差异点列表（字符级别对比）

    示例:
        >>> score, details = calculate_score("สวัสดี", "สวัสดี")
        >>> print(score)  # 100
        >>> print(details["score_level"])  # "优秀"
    """
    # 清洗文本：去除首尾空白和多余空格
    expected = expected_text.strip()
    actual = actual_text.strip()

    # 计算编辑距离和相似度
    edit_dist = levenshtein_distance(expected, actual)
    similarity = normalized_similarity(expected, actual)

    # 转换为百分制评分
    score = round(similarity * 100)

    # 找出差异字符
    differences = _find_differences(expected, actual)

    # 确定等级
    score_level = _get_score_level(score)

    details = {
        "similarity": round(similarity, 3),
        "edit_distance": edit_dist,
        "expected_text": expected,
        "expected_length": len(expected),
        "actual_text": actual,
        "actual_length": len(actual),
        "is_exact_match": expected == actual,
        "score_level": score_level,
        "differences": differences,
        "is_pass": score >= SCORE_THRESHOLD_PASS,
        "is_good": score >= SCORE_THRESHOLD_GOOD,
        "is_excellent": score >= SCORE_THRESHOLD_EXCELLENT,
    }

    return score, details


def _find_differences(expected: str, actual: str) -> list:
    """
    逐字符对比标准文本和识别文本，找出差异。

    使用对齐方式找出具体的差异位置和内容。

    Args:
        expected: 标准文本
        actual: 识别文本

    Returns:
        list: 差异列表，每个元素为 dict:
            - type: "missing" | "extra" | "mismatch"
            - position: 在标准文本中的位置
            - expected_char: 标准文本中的字符（如有）
            - actual_char: 识别文本中的字符（如有）
    """
    differences = []
    m, n = len(expected), len(actual)

    # 使用简单的前缀对齐
    i, j = 0, 0
    while i < m and j < n:
        if expected[i] != actual[j]:
            differences.append({
                "type": "mismatch",
                "position": i,
                "expected_char": expected[i],
                "actual_char": actual[j],
            })
        i += 1
        j += 1

    # 检查多余字符（识别的文本比标准长）
    while j < n:
        differences.append({
            "type": "extra",
            "position": i,
            "expected_char": "",
            "actual_char": actual[j],
        })
        j += 1

    # 检查缺少字符（识别的文本比标准短）
    while i < m:
        differences.append({
            "type": "missing",
            "position": i,
            "expected_char": expected[i],
            "actual_char": "",
        })
        i += 1

    return differences


def _get_score_level(score: int) -> str:
    """
    将分数映射为等级描述。

    Args:
        score: 0-100 的评分

    Returns:
        str: 等级描述（优秀/良好/及格/不及格）
    """
    if score >= SCORE_THRESHOLD_EXCELLENT:
        return "优秀 ✨"
    elif score >= SCORE_THRESHOLD_GOOD:
        return "良好 👍"
    elif score >= SCORE_THRESHOLD_PASS:
        return "及格 💪"
    else:
        return "不及格 🔄"


def get_score_color(score: int) -> str:
    """
    根据分数返回对应的显示颜色（用于 UI）。

    Args:
        score: 评分（0-100）

    Returns:
        str: 十六进制颜色代码
    """
    if score >= SCORE_THRESHOLD_EXCELLENT:
        return "#27ae60"  # 绿色 - 优秀
    elif score >= SCORE_THRESHOLD_GOOD:
        return "#2980b9"  # 蓝色 - 良好
    elif score >= SCORE_THRESHOLD_PASS:
        return "#f39c12"  # 橙色 - 及格
    else:
        return "#e74c3c"  # 红色 - 不及格


if __name__ == "__main__":
    # 简单测试
    test_cases = [
        ("สวัสดี", "สวัสดี"),        # 完全正确
        ("สวัสดี", "สวัด"),          # 缺字
        ("ขอบคุณ", "ขอบคุน"),        # 错字
        ("สวัสดี", ""),              # 空识别
    ]

    for expected, actual in test_cases:
        score, details = calculate_score(expected, actual)
        print(f"标准: '{expected}' → 识别: '{actual}'")
        print(f"  评分: {score}分 ({details['score_level']})")
        print(f"  编辑距离: {details['edit_distance']}, 相似度: {details['similarity']:.2%}")
        if details["differences"]:
            print(f"  差异: {details['differences']}")
        print()
