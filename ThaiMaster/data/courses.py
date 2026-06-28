"""
课程数据模块

定义泰语学习课程的数据结构和初始课程内容。
课程级别模仿日本语能力测试(JLPT)的N1~N5分级体系：
- N5：入门级 - 基础单词和日常用语
- N4：初级 - 常用词汇和简单句子
- N3：中级 - 较复杂词汇和会话
- N2：中高级 - 专业词汇和长句
- N1：高级 - 学术词汇和复杂表达

当前仅包含N5入门级课程数据。
"""

from typing import List, Dict, TypedDict


class WordItem(TypedDict):
    thai: str
    thai_pronunciation: str
    chinese: str
    example: str
    example_chinese: str


class Course(TypedDict):
    level: str
    name: str
    description: str
    words: List[WordItem]


class CoursesManager:
    def __init__(self):
        self._courses: Dict[str, Course] = self._load_courses()
    
    def _load_courses(self) -> Dict[str, Course]:
        courses = {}
        
        courses["N5"] = {
            "level": "N5",
            "name": "入门级",
            "description": "泰语入门课程，包含基础问候语、数字、颜色等日常词汇",
            "words": [
                {"thai": "สวัสดี", "thai_pronunciation": "sawasdee", "chinese": "你好", "example": "สวัสดี ครับ", "example_chinese": "你好（男性用语）"},
                {"thai": "ขอบคุณ", "thai_pronunciation": "khopkhun", "chinese": "谢谢", "example": "ขอบคุณ ครับ", "example_chinese": "谢谢（男性用语）"},
                {"thai": "ไม่เป็นไร", "thai_pronunciation": "mai pen rai", "chinese": "没关系", "example": "ไม่เป็นไร ครับ", "example_chinese": "没关系（男性用语）"},
                {"thai": "ลาก่อน", "thai_pronunciation": "lagorn", "chinese": "再见", "example": "ลาก่อน ครับ", "example_chinese": "再见（男性用语）"},
                {"thai": "ชื่อ", "thai_pronunciation": "chue", "chinese": "名字", "example": "ชื่อฉันคือ...", "example_chinese": "我的名字是..."},
                {"thai": "ฉัน", "thai_pronunciation": "chan", "chinese": "我（女性用）", "example": "ฉันชื่อ...", "example_chinese": "我叫..."},
                {"thai": "ผม", "thai_pronunciation": "phom", "chinese": "我（男性用）", "example": "ผมชื่อ...", "example_chinese": "我叫..."},
                {"thai": "คุณ", "thai_pronunciation": "khun", "chinese": "你", "example": "คุณชื่ออะไร", "example_chinese": "你叫什么名字"},
                {"thai": "หนึ่ง", "thai_pronunciation": "nueng", "chinese": "一", "example": "หนึ่ง สอง สาม", "example_chinese": "一 二 三"},
                {"thai": "สอง", "thai_pronunciation": "song", "chinese": "二", "example": "สองคน", "example_chinese": "两个人"},
                {"thai": "สาม", "thai_pronunciation": "sam", "chinese": "三", "example": "สามวัน", "example_chinese": "三天"},
                {"thai": "สีแดง", "thai_pronunciation": "si daeng", "chinese": "红色", "example": "ฉันชอบสีแดง", "example_chinese": "我喜欢红色"},
                {"thai": "สีขาว", "thai_pronunciation": "si khao", "chinese": "白色", "example": "เสื้อสีขาว", "example_chinese": "白色的衣服"},
                {"thai": "สีดำ", "thai_pronunciation": "si dam", "chinese": "黑色", "example": "กางเกงสีดำ", "example_chinese": "黑色的裤子"},
                {"thai": "อาหาร", "thai_pronunciation": "ahaan", "chinese": "食物", "example": "ฉันกินอาหาร", "example_chinese": "我在吃饭"},
                {"thai": "น้ำ", "thai_pronunciation": "nam", "chinese": "水", "example": "ฉันดื่มน้ำ", "example_chinese": "我在喝水"},
                {"thai": "กิน", "thai_pronunciation": "kin", "chinese": "吃", "example": "กินข้าว", "example_chinese": "吃饭"},
                {"thai": "ดื่ม", "thai_pronunciation": "dum", "chinese": "喝", "example": "ดื่มกาแฟ", "example_chinese": "喝咖啡"},
                {"thai": "นอน", "thai_pronunciation": "non", "chinese": "睡觉", "example": "ฉันนอน", "example_chinese": "我在睡觉"},
                {"thai": "งาน", "thai_pronunciation": "ngan", "chinese": "工作", "example": "ฉันไปทำงาน", "example_chinese": "我去工作"}
            ]
        }
        
        courses["N4"] = {"level": "N4", "name": "初级", "description": "泰语初级课程，包含常用词汇和简单句子", "words": []}
        courses["N3"] = {"level": "N3", "name": "中级", "description": "泰语中级课程，包含较复杂词汇和会话", "words": []}
        courses["N2"] = {"level": "N2", "name": "中高级", "description": "泰语中高级课程，包含专业词汇和长句", "words": []}
        courses["N1"] = {"level": "N1", "name": "高级", "description": "泰语高级课程，包含学术词汇和复杂表达", "words": []}
        
        return courses
    
    def get_course(self, level: str) -> Course:
        if level not in self._courses:
            raise ValueError(f"未知课程级别: {level}")
        return self._courses[level]
    
    def get_all_levels(self) -> List[str]:
        return ["N5", "N4", "N3", "N2", "N1"]
    
    def get_words(self, level: str) -> List[WordItem]:
        course = self.get_course(level)
        return course["words"]
    
    def get_word_count(self, level: str) -> int:
        return len(self.get_words(level))


courses_manager = CoursesManager()
