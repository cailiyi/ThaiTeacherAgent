"""
泰语课程数据模块

本模块定义了从 N5（入门级）到 N1（高级）的五级课程体系，
模仿日语能力考的分级思路，难度逐级递增。

数据结构说明：
- CourseLevel: 一个级别（如 N5），包含多个 Lesson
- Lesson: 一课，包含标题、简介和多个 CardItem
- CardItem: 一张学习卡片，包含泰语原文、发音指南、中文释义和例句

用法：
    from data.courses import load_courses
    all_courses = load_courses()
    n5_lessons = all_courses["N5 入门级"]
    first_lesson = n5_lessons[0]
    first_card = first_lesson.cards[0]
    print(first_card.thai)  # 打印泰语句子
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class CardItem:
    """
    一张学习卡片的数据模型。

    属性:
        thai: 泰语原文（单词或句子）
        pronunciation: 发音指南（罗马音/注音）
        meaning: 中文释义
        example: 例句（泰语）
        example_pronunciation: 例句发音指南
        example_meaning: 例句中文翻译
        word_type: 词性标注（如 "名词/动词/形容词" 等，可选）
    """
    thai: str
    pronunciation: str
    meaning: str
    example: str = ""
    example_pronunciation: str = ""
    example_meaning: str = ""
    word_type: str = ""


@dataclass
class Lesson:
    """
    一课的数据模型。

    属性:
        title: 课标题（中文）
        description: 课文简介
        cards: 本课包含的单词/句子卡片列表
    """
    title: str
    description: str
    cards: List[CardItem] = field(default_factory=list)


def _build_n5_lessons() -> List[Lesson]:
    """
    构建 N5 入门级课程。

    N5 为入门阶段，重点学习：
    - 泰语辅音、元音和声调规则
    - 最基础的问候语和礼貌用语
    - 自我介绍
    - 数字 1-10
    本阶段目标是让学习者能够读写泰语基本字符并进行简单问候。
    """
    lesson1 = Lesson(
        title="第1课 · 基本问候",
        description="学习最常用的泰语问候语和礼貌用语，打好日常交流基础。",
        cards=[
            CardItem(
                thai="สวัสดี",
                pronunciation="sa-wat-dee",
                meaning="你好/再见（问候语）",
                example="สวัสดีครับ สบายดีไหม",
                example_pronunciation="sa-wat-dee krap, sa-bai-dee mai",
                example_meaning="你好，你最近好吗？"
            ),
            CardItem(
                thai="ขอบคุณ",
                pronunciation="khop-khun",
                meaning="谢谢",
                example="ขอบคุณมากครับ",
                example_pronunciation="khop-khun maak krap",
                example_meaning="非常感谢"
            ),
            CardItem(
                thai="ขอโทษ",
                pronunciation="kho-thot",
                meaning="对不起/打扰一下",
                example="ขอโทษครับ ห้องน้ำอยู่ที่ไหน",
                example_pronunciation="kho-thot krap, hong-nam yoo tee-nai",
                example_meaning="打扰一下，洗手间在哪里？"
            ),
            CardItem(
                thai="ครับ / ค่ะ",
                pronunciation="krap / kha",
                meaning="（语气词）是/好的",
                word_type="语气词",
                example="ครับ สบายดี",
                example_pronunciation="krap, sa-bai-dee",
                example_meaning="（男性）嗯，我很好"
            ),
            CardItem(
                thai="ยินดีที่ได้รู้จัก",
                pronunciation="yin-dee tee dai roo-jak",
                meaning="很高兴认识你",
                example="สวัสดีครับ ยินดีที่ได้รู้จัก",
                example_pronunciation="sa-wat-dee krap, yin-dee tee dai roo-jak",
                example_meaning="你好，很高兴认识你"
            ),
            CardItem(
                thai="ลาก่อน",
                pronunciation="la-gon",
                meaning="再见",
                example="ลาก่อน แล้วเจอกัน",
                example_pronunciation="la-gon, laew jur gan",
                example_meaning="再见，下次见"
            ),
        ]
    )

    lesson2 = Lesson(
        title="第2课 · 自我介绍",
        description="学会用泰语介绍自己的名字、国籍和职业。",
        cards=[
            CardItem(
                thai="ผม / ดิฉัน",
                pronunciation="pom / di-chan",
                meaning="我（男性用ผม，女性用ดิฉัน）",
                word_type="代词",
                example="ผมชื่อไมค์",
                example_pronunciation="pom cheu Mike",
                example_meaning="我叫Mike"
            ),
            CardItem(
                thai="คุณ",
                pronunciation="khun",
                meaning="你/您",
                word_type="代词",
                example="คุณชื่ออะไร",
                example_pronunciation="khun cheu a-rai",
                example_meaning="你叫什么名字？"
            ),
            CardItem(
                thai="ชื่อ",
                pronunciation="cheu",
                meaning="名字",
                word_type="名词",
                example="ผมชื่อไทย",
                example_pronunciation="pom cheu Thai",
                example_meaning="我叫Thai"
            ),
            CardItem(
                thai="ประเทศ",
                pronunciation="pra-thet",
                meaning="国家",
                word_type="名词",
                example="ฉันมาจากประเทศจีน",
                example_pronunciation="chan maa jak pra-thet Jeen",
                example_meaning="我来自中国"
            ),
            CardItem(
                thai="เรียน",
                pronunciation="rian",
                meaning="学习",
                word_type="动词",
                example="ผมเรียนภาษาไทย",
                example_pronunciation="pom rian pha-sa Thai",
                example_meaning="我在学泰语"
            ),
            CardItem(
                thai="ทำงาน",
                pronunciation="tham-ngan",
                meaning="工作",
                word_type="动词",
                example="คุณทำงานอะไร",
                example_pronunciation="khun tham-ngan a-rai",
                example_meaning="你做什么工作？"
            ),
        ]
    )

    lesson3 = Lesson(
        title="第3课 · 数字 1-10",
        description="掌握泰语数字 1 到 10 的读写，这是购物、问价的基础。",
        cards=[
            CardItem(
                thai="๐ หนึ่ง",
                pronunciation="neung",
                meaning="一（数字 1）",
                example="หนึ่งคน",
                example_pronunciation="neung khon",
                example_meaning="一个人"
            ),
            CardItem(
                thai="๑ สอง",
                pronunciation="song",
                meaning="二（数字 2）",
                example="สองร้อย",
                example_pronunciation="song roi",
                example_meaning="两百"
            ),
            CardItem(
                thai="๒ สาม",
                pronunciation="sam",
                meaning="三（数字 3）",
                example="สามชิ้น",
                example_pronunciation="sam chin",
                example_meaning="三个（物品）"
            ),
            CardItem(
                thai="๓ สี่",
                pronunciation="see",
                meaning="四（数字 4）",
                example="สี่โมง",
                example_pronunciation="see moeng",
                example_meaning="四点（钟）"
            ),
            CardItem(
                thai="๔ ห้า",
                pronunciation="haa",
                meaning="五（数字 5）",
                example="ห้าบาท",
                example_pronunciation="haa baat",
                example_meaning="五泰铢"
            ),
            CardItem(
                thai="๕ หก",
                pronunciation="hok",
                meaning="六（数字 6）",
                example="หกโมง",
                example_pronunciation="hok moeng",
                example_meaning="六点（钟）"
            ),
            CardItem(
                thai="๖ เจ็ด",
                pronunciation="jet",
                meaning="七（数字 7）",
                example="เจ็ดวัน",
                example_pronunciation="jet wan",
                example_meaning="七天"
            ),
            CardItem(
                thai="๗ แปด",
                pronunciation="paet",
                meaning="八（数字 8）",
                example="แปดบาท",
                example_pronunciation="paet baat",
                example_meaning="八泰铢"
            ),
            CardItem(
                thai="๘ เก้า",
                pronunciation="kao",
                meaning="九（数字 9）",
                example="เก้าคน",
                example_pronunciation="kao khon",
                example_meaning="九个人"
            ),
            CardItem(
                thai="๙ สิบ",
                pronunciation="sip",
                meaning="十（数字 10）",
                example="สิบสอง",
                example_pronunciation="sip song",
                example_meaning="十二"
            ),
        ]
    )

    lesson4 = Lesson(
        title="第4课 · 常用动词",
        description="学习泰语中最常用的基础动词，能帮你组成简单句子。",
        cards=[
            CardItem(
                thai="ไป",
                pronunciation="bpai",
                meaning="去/走",
                word_type="动词",
                example="ไปตลาด",
                example_pronunciation="bpai dta-laad",
                example_meaning="去市场"
            ),
            CardItem(
                thai="มา",
                pronunciation="maa",
                meaning="来",
                word_type="动词",
                example="มาไทย",
                example_pronunciation="maa Thai",
                example_meaning="来泰国"
            ),
            CardItem(
                thai="กิน",
                pronunciation="gin",
                meaning="吃",
                word_type="动词",
                example="กินข้าว",
                example_pronunciation="gin khao",
                example_meaning="吃饭"
            ),
            CardItem(
                thai="ดื่ม",
                pronunciation="deum",
                meaning="喝",
                word_type="动词",
                example="ดื่มน้ำ",
                example_pronunciation="deum nam",
                example_meaning="喝水"
            ),
            CardItem(
                thai="นอน",
                pronunciation="non",
                meaning="睡觉",
                word_type="动词",
                example="นอนเร็ว",
                example_pronunciation="non reo",
                example_meaning="早点睡"
            ),
            CardItem(
                thai="อ่าน",
                pronunciation="aan",
                meaning="阅读",
                word_type="动词",
                example="อ่านหนังสือ",
                example_pronunciation="aan nang-seu",
                example_meaning="读书"
            ),
        ]
    )

    lesson5 = Lesson(
        title="第5课 · 基础形容词",
        description="学会用形容词描述事物的大小、好坏、冷暖等基本特征。",
        cards=[
            CardItem(
                thai="ดี",
                pronunciation="dee",
                meaning="好",
                word_type="形容词",
                example="วันนี้ดี",
                example_pronunciation="wan-nee dee",
                example_meaning="今天很好"
            ),
            CardItem(
                thai="ใหญ่",
                pronunciation="yai",
                meaning="大",
                word_type="形容词",
                example="บ้านใหญ่",
                example_pronunciation="baan yai",
                example_meaning="大房子"
            ),
            CardItem(
                thai="เล็ก",
                pronunciation="lek",
                meaning="小",
                word_type="形容词",
                example="แมวเล็ก",
                example_pronunciation="maew lek",
                example_meaning="小猫"
            ),
            CardItem(
                thai="ร้อน",
                pronunciation="ron",
                meaning="热",
                word_type="形容词",
                example="อากาศร้อน",
                example_pronunciation="a-gaat ron",
                example_meaning="天气热"
            ),
            CardItem(
                thai="เย็น",
                pronunciation="yen",
                meaning="冷/凉",
                word_type="形容词",
                example="น้ำเย็น",
                example_pronunciation="nam yen",
                example_meaning="凉水"
            ),
            CardItem(
                thai="สวย",
                pronunciation="suay",
                meaning="漂亮",
                word_type="形容词",
                example="ผู้หญิงสวย",
                example_pronunciation="phu-ying suay",
                example_meaning="漂亮的女人"
            ),
        ]
    )

    return [lesson1, lesson2, lesson3, lesson4, lesson5]


def _build_n4_lessons() -> List[Lesson]:
    """
    构建 N4 初级课程。

    N4 为初级阶段，重点学习：
    - 家庭成员称谓
    - 颜色、水果等日常词汇
    - 时间表达（星期几、月份）
    - 基本句式和否定句
    """
    lesson1 = Lesson(
        title="第1课 · 家庭成员",
        description="学习泰语中家庭成员的各种称谓。",
        cards=[
            CardItem(
                thai="พ่อ",
                pronunciation="pho",
                meaning="爸爸/父亲",
                example="พ่อผมชื่อสมชาย",
                example_pronunciation="pho pom cheu Somchai",
                example_meaning="我的爸爸叫Somchai"
            ),
            CardItem(
                thai="แม่",
                pronunciation="mae",
                meaning="妈妈/母亲",
                example="แม่ไปตลาด",
                example_pronunciation="mae bpai dta-laad",
                example_meaning="妈妈去市场"
            ),
            CardItem(
                thai="พี่ชาย",
                pronunciation="pee-chai",
                meaning="哥哥",
                example="พี่ชายทำงานที่กรุงเทพ",
                example_pronunciation="pee-chai tham-ngan tee Krung Thep",
                example_meaning="哥哥在曼谷工作"
            ),
            CardItem(
                thai="น้องสาว",
                pronunciation="nong-sao",
                meaning="妹妹",
                example="น้องสาวเรียนหนังสือ",
                example_pronunciation="nong-sao rian nang-seu",
                example_meaning="妹妹在读书"
            ),
            CardItem(
                thai="ปู่ / ตา",
                pronunciation="bpuu / dtaa",
                meaning="爷爷（父系）/ 外公（母系）",
                example="ปู่อายุเจ็ดสิบ",
                example_pronunciation="bpuu a-yoo jet-sip",
                example_meaning="爷爷七十岁了"
            ),
            CardItem(
                thai="ย่า / ยาย",
                pronunciation="yaa / yaai",
                meaning="奶奶（父系）/ 外婆（母系）",
                example="ยายทำกับข้าวอร่อย",
                example_pronunciation="yaai tham gap-khao a-roi",
                example_meaning="外婆做的菜很好吃"
            ),
        ]
    )

    lesson2 = Lesson(
        title="第2课 · 颜色与水果",
        description="学习常见颜色和水果的名称，丰富日常词汇量。",
        cards=[
            CardItem(
                thai="แดง",
                pronunciation="daeng",
                meaning="红色",
                example="รถสีแดง",
                example_pronunciation="rot see daeng",
                example_meaning="红色的车"
            ),
            CardItem(
                thai="น้ำเงิน",
                pronunciation="nam-ngern",
                meaning="蓝色",
                example="ท้องฟ้าสีน้ำเงิน",
                example_pronunciation="tong-faa see nam-ngern",
                example_meaning="蓝色的天空"
            ),
            CardItem(
                thai="เขียว",
                pronunciation="khiao",
                meaning="绿色",
                example="ใบไม้สีเขียว",
                example_pronunciation="bai-mai see khiao",
                example_meaning="绿色的叶子"
            ),
            CardItem(
                thai="กล้วย",
                pronunciation="gluay",
                meaning="香蕉",
                example="กล้วยหวาน",
                example_pronunciation="gluay waan",
                example_meaning="甜香蕉"
            ),
            CardItem(
                thai="มะม่วง",
                pronunciation="ma-muang",
                meaning="芒果",
                example="มะม่วงสุก",
                example_pronunciation="ma-muang suk",
                example_meaning="熟芒果"
            ),
            CardItem(
                thai="มะพร้าว",
                pronunciation="ma-phrao",
                meaning="椰子",
                example="น้ำมะพร้าว",
                example_pronunciation="nam ma-phrao",
                example_meaning="椰子水"
            ),
        ]
    )

    lesson3 = Lesson(
        title="第3课 · 星期与月份",
        description="掌握星期的说法和一年十二个月的泰语表达。",
        cards=[
            CardItem(
                thai="วันจันทร์",
                pronunciation="wan jan",
                meaning="星期一",
                example="วันจันทร์ไปทำงาน",
                example_pronunciation="wan jan bpai tham-ngan",
                example_meaning="星期一去上班"
            ),
            CardItem(
                thai="วันอังคาร",
                pronunciation="wan ang-kaan",
                meaning="星期二",
                example="วันอังคารมีประชุม",
                example_pronunciation="wan ang-kaan mee bpra-chum",
                example_meaning="星期二有会议"
            ),
            CardItem(
                thai="วันศุกร์",
                pronunciation="wan suk",
                meaning="星期五",
                example="วันศุกร์สบาย",
                example_pronunciation="wan suk sa-bai",
                example_meaning="星期五轻松"
            ),
            CardItem(
                thai="วันเสาร์",
                pronunciation="wan sao",
                meaning="星期六",
                example="วันเสาร์ไม่ทำงาน",
                example_pronunciation="wan sao mai tham-ngan",
                example_meaning="星期六不上班"
            ),
            CardItem(
                thai="วันอาทิตย์",
                pronunciation="wan aa-thit",
                meaning="星期日",
                example="วันอาทิตย์ไปเที่ยว",
                example_pronunciation="wan aa-thit bpai thiao",
                example_meaning="星期日去玩"
            ),
            CardItem(
                thai="เดือน",
                pronunciation="deuan",
                meaning="月份",
                example="เดือนนี้ร้อนมาก",
                example_pronunciation="deuan nee ron maak",
                example_meaning="这个月很热"
            ),
        ]
    )

    return [lesson1, lesson2, lesson3]


def _build_n3_lessons() -> List[Lesson]:
    """
    构建 N3 中级课程。

    N3 为中级阶段，重点学习：
    - 餐厅点餐、购物等真实场景
    - 问路和交通出行
    - 天气表达
    - 日常对话中常用的句型和表达
    """
    lesson1 = Lesson(
        title="第1课 · 餐厅点餐",
        description="学会在泰国餐厅点餐、询问菜单和结账。",
        cards=[
            CardItem(
                thai="เมนู",
                pronunciation="me-nu",
                meaning="菜单",
                example="ขอดูเมนูหน่อยครับ",
                example_pronunciation="kho du me-nu noi krap",
                example_meaning="请给我看一下菜单"
            ),
            CardItem(
                thai="อร่อย",
                pronunciation="a-roi",
                meaning="好吃/美味",
                word_type="形容词",
                example="อาหารไทยอร่อยมาก",
                example_pronunciation="aa-haan Thai a-roi maak",
                example_meaning="泰国菜非常好吃"
            ),
            CardItem(
                thai="เผ็ด",
                pronunciation="phet",
                meaning="辣",
                word_type="形容词",
                example="ไม่เผ็ดนะครับ",
                example_pronunciation="mai phet na krap",
                example_meaning="不要辣哦"
            ),
            CardItem(
                thai="คิดเงิน",
                pronunciation="khit ngern",
                meaning="结账",
                example="คิดเงินด้วยครับ",
                example_pronunciation="khit ngern duay krap",
                example_meaning="请结账"
            ),
            CardItem(
                thai="ต้มยำกุ้ง",
                pronunciation="dtom-yam goong",
                meaning="冬阴功汤（泰式酸辣虾汤）",
                example="ต้มยำกุ้งร้านนี้อร่อย",
                example_pronunciation="dtom-yam goong raan nee a-roi",
                example_meaning="这家的冬阴功汤好吃"
            ),
            CardItem(
                thai="ผัดไทย",
                pronunciation="phat Thai",
                meaning="泰式炒面",
                example="ผัดไทยใส่กุ้ง",
                example_pronunciation="phat Thai sai goong",
                example_meaning="虾仁泰式炒面"
            ),
        ]
    )

    lesson2 = Lesson(
        title="第2课 · 问路与出行",
        description="学会用泰语问路、乘坐交通工具和判断方向。",
        cards=[
            CardItem(
                thai="ที่ไหน",
                pronunciation="tee-nai",
                meaning="在哪里",
                example="โรงแรมอยู่ที่ไหน",
                example_pronunciation="rong-raem yoo tee-nai",
                example_meaning="酒店在哪里？"
            ),
            CardItem(
                thai="ตรงไป",
                pronunciation="dtrong bpai",
                meaning="直走",
                example="ตรงไปแล้วเลี้ยวซ้าย",
                example_pronunciation="dtrong bpai laew liao saai",
                example_meaning="直走然后左转"
            ),
            CardItem(
                thai="เลี้ยวขวา",
                pronunciation="liao khwaa",
                meaning="右转",
                example="เลี้ยวขวาที่สี่แยก",
                example_pronunciation="liao khwaa tee see-yaek",
                example_meaning="在十字路口右转"
            ),
            CardItem(
                thai="รถเมล์",
                pronunciation="rot may",
                meaning="公交车",
                example="รถเมล์สายนี้ไปสนามบินไหม",
                example_pronunciation="rot may saai nee bpai sa-nam-bin mai",
                example_meaning="这路公交车去机场吗？"
            ),
            CardItem(
                thai="รถไฟฟ้า",
                pronunciation="rot fai faa",
                meaning="轻轨/BTS",
                example="นั่งรถไฟฟ้าไปเร็ว",
                example_pronunciation="nang rot fai faa bpai reo",
                example_meaning="坐轻轨去更快"
            ),
            CardItem(
                thai="Taxi",
                pronunciation="taek-see",
                meaning="出租车（泰语化借词）",
                example="เรียก taxi หน่อย",
                example_pronunciation="riak taek-see noi",
                example_meaning="叫一辆出租车"
            ),
        ]
    )

    lesson3 = Lesson(
        title="第3课 · 天气表达",
        description="学习描述天气的词汇和句型，能看懂泰国的天气预报。",
        cards=[
            CardItem(
                thai="อากาศ",
                pronunciation="aa-gaat",
                meaning="天气",
                example="อากาศวันนี้ดีจัง",
                example_pronunciation="aa-gaat wan-nee dee jang",
                example_meaning="今天天气真好呀"
            ),
            CardItem(
                thai="ฝนตก",
                pronunciation="fon dtok",
                meaning="下雨",
                example="ฝนตกหนักมาก",
                example_pronunciation="fon dtok nak maak",
                example_meaning="雨下得很大"
            ),
            CardItem(
                thai="แดด",
                pronunciation="daet",
                meaning="阳光/日晒",
                example="แดดแรงมาก",
                example_pronunciation="daet raeng maak",
                example_meaning="阳光很强烈"
            ),
            CardItem(
                thai="หนาว",
                pronunciation="nao",
                meaning="寒冷",
                word_type="形容词",
                example="เมืองไทยไม่หนาว",
                example_pronunciation="meuang Thai mai nao",
                example_meaning="泰国不冷"
            ),
            CardItem(
                thai="อุ่น",
                pronunciation="un",
                meaning="温暖",
                word_type="形容词",
                example="วันนี้อุ่นขึ้น",
                example_pronunciation="wan-nee un kheun",
                example_meaning="今天暖和起来了"
            ),
            CardItem(
                thai="พายุ",
                pronunciation="pha-yu",
                meaning="风暴",
                example="พายุกำลังมา",
                example_pronunciation="pha-yu gam-lang maa",
                example_meaning="风暴要来了"
            ),
        ]
    )

    return [lesson1, lesson2, lesson3]


def _build_n2_lessons() -> List[Lesson]:
    """
    构建 N2 中高级课程。

    N2 为中高级阶段，重点学习：
    - 泰式文化和传统节日
    - 情感表达和观点讨论
    - 职场用语
    - 更为复杂的句式和连接词
    """
    lesson1 = Lesson(
        title="第1课 · 泰式文化",
        description="了解泰国传统文化中的礼仪、习俗和宗教信仰。",
        cards=[
            CardItem(
                thai="ไหว้",
                pronunciation="wai",
                meaning="合十礼（泰式问候礼）",
                example="คนไทยไหว้กันเมื่อเจอกัน",
                example_pronunciation="khon Thai wai gan meua jur gan",
                example_meaning="泰国人见面时互相行合十礼"
            ),
            CardItem(
                thai="วัด",
                pronunciation="wat",
                meaning="寺庙",
                example="วัดพระแก้วสวยมาก",
                example_pronunciation="wat Phra Kaew suay maak",
                example_meaning="玉佛寺非常漂亮"
            ),
            CardItem(
                thai="สงกรานต์",
                pronunciation="song-gran",
                meaning="宋干节（泰国新年/泼水节）",
                example="สงกรานต์เป็นวันปีใหม่ไทย",
                example_pronunciation="song-gran bpen wan pee mai Thai",
                example_meaning="宋干节是泰国新年"
            ),
            CardItem(
                thai="ลอยกระทง",
                pronunciation="loy grathong",
                meaning="水灯节",
                example="ลอยกระทงเดือนสิบสอง",
                example_pronunciation="loy grathong deuan sip song",
                example_meaning="水灯节在十二月（泰历）"
            ),
            CardItem(
                thai="พระ",
                pronunciation="phra",
                meaning="僧侣/佛",
                example="พระมาเดินบิณฑบาต",
                example_pronunciation="phra maa dern bin-tha-baat",
                example_meaning="僧侣来托钵化缘"
            ),
            CardItem(
                thai="บัตร",
                pronunciation="bat",
                meaning="卡片/票/证件",
                example="บัตรเครดิต",
                example_pronunciation="bat khre-dit",
                example_meaning="信用卡"
            ),
        ]
    )

    lesson2 = Lesson(
        title="第2课 · 情感表达",
        description="学会用泰语表达喜怒哀乐和各种情感。",
        cards=[
            CardItem(
                thai="มีความสุข",
                pronunciation="mee khwam suk",
                meaning="开心/幸福",
                example="ฉันมีความสุขมาก",
                example_pronunciation="chan mee khwam suk maak",
                example_meaning="我非常开心"
            ),
            CardItem(
                thai="เสียใจ",
                pronunciation="sia jai",
                meaning="难过/伤心",
                example="อย่าเสียใจเลย",
                example_pronunciation="yaa sia jai loei",
                example_meaning="别难过了"
            ),
            CardItem(
                thai="โกรธ",
                pronunciation="grot",
                meaning="生气",
                example="อย่าโกรธผมเลยนะ",
                example_pronunciation="yaa grot pom loei na",
                example_meaning="别生我的气啦"
            ),
            CardItem(
                thai="กังวล",
                pronunciation="gang-won",
                meaning="担心/焦虑",
                example="ไม่ต้องกังวล",
                example_pronunciation="mai dtong gang-won",
                example_meaning="不用担心"
            ),
            CardItem(
                thai="ประทับใจ",
                pronunciation="bpra-thab-jai",
                meaning="印象深刻/感动",
                example="ประทับใจมาก",
                example_pronunciation="bpra-thab-jai maak",
                example_meaning="非常感动/印象深刻"
            ),
            CardItem(
                thai="คิดถึง",
                pronunciation="khit theung",
                meaning="想念",
                example="คิดถึงคุณมาก",
                example_pronunciation="khit theung khun maak",
                example_meaning="很想你"
            ),
        ]
    )

    return [lesson1, lesson2]


def _build_n1_lessons() -> List[Lesson]:
    """
    构建 N1 高级课程。

    N1 为高级阶段，重点学习：
    - 泰语谚语和成语
    - 正式/书面语体
    - 文学和新闻体裁
    - 复杂论述和抽象表达
    """
    lesson1 = Lesson(
        title="第1课 · 泰语谚语",
        description="学习泰语中富有哲理的传统谚语，提升语言深度。",
        cards=[
            CardItem(
                thai="ช้าๆ ได้พร้าเล่มงาม",
                pronunciation="chaa chaa dai phra lem ngam",
                meaning="慢工出细活（欲速则不达）",
                example="ทำงานอย่ารีบ ช้าๆ ได้พร้าเล่มงาม",
                example_pronunciation="tham-ngan yaa reep, chaa chaa dai phra lem ngam",
                example_meaning="工作别着急，慢工出细活"
            ),
            CardItem(
                thai="รู้จักประมาณตน",
                pronunciation="roo jak bpra-maan dton",
                meaning="自知之明",
                example="เราควรรู้จักประมาณตน",
                example_pronunciation="rao khuan roo jak bpra-maan dton",
                example_meaning="我们应该有自知之明"
            ),
            CardItem(
                thai="น้ำขึ้นให้รีบตัก",
                pronunciation="nam kheun hai reep dtak",
                meaning="趁热打铁（水涨时要赶快舀）",
                example="โอกาสดี น้ำขึ้นให้รีบตัก",
                example_pronunciation="oh-gaat dee, nam kheun hai reep dtak",
                example_meaning="好机会，要趁热打铁"
            ),
            CardItem(
                thai="รักวัวให้ผูก รักลูกให้ตี",
                pronunciation="rak wua hai phook, rak look hai dtee",
                meaning="打是疼骂是爱（爱牛要拴，爱子要打）",
                example="บางทีรักวัวให้ผูก รักลูกให้ตี",
                example_pronunciation="baang tee rak wua hai phook, rak look hai dtee",
                example_meaning="有时候打是疼骂是爱"
            ),
            CardItem(
                thai="เข้าตามตรอก ออกตามประตู",
                pronunciation="khao dtam dtrok, awk dtam bpra-dtoo",
                meaning="循规蹈矩（从巷子进，从大门出）",
                example="ทำอะไรต้องเข้าตามตรอกออกตามประตู",
                example_pronunciation="tham a-rai dtong khao dtam dtrok awk dtam bpra-dtoo",
                example_meaning="做什么都要循规蹈矩"
            ),
            CardItem(
                thai="น้ำพึ่งเรือ เสือพึ่งป่า",
                pronunciation="nam pheung reua, seua pheung bpaa",
                meaning="相依相存（水靠船，虎靠林）",
                example="คนเราต้องพึ่งพากัน น้ำพึ่งเรือเสือพึ่งป่า",
                example_pronunciation="khon rao dtong pheung-pha gan, nam pheung reua seua pheung bpaa",
                example_meaning="人与人要互相依靠，水靠船虎靠林"
            ),
        ]
    )

    lesson2 = Lesson(
        title="第2课 · 正式用语",
        description="学习泰语中的正式/书面表达，适用于公文、报告和正式场合。",
        cards=[
            CardItem(
                thai="เนื่องจาก",
                pronunciation="neuang-jak",
                meaning="由于/因为（正式）",
                example="เนื่องจากสภาพอากาศไม่ดี",
                example_pronunciation="neuang-jak sa-phaap aa-gaat mai dee",
                example_meaning="由于天气状况不佳"
            ),
            CardItem(
                thai="ดังนั้น",
                pronunciation="dang nan",
                meaning="因此/所以（正式）",
                example="ดังนั้นเราจึงต้องเตรียมตัว",
                example_pronunciation="dang nan rao jeung dtong dtriem dtua",
                example_meaning="因此我们必须做好准备"
            ),
            CardItem(
                thai="ขอเรียนให้ทราบว่า",
                pronunciation="kho rian hai saap waa",
                meaning="谨此告知（正式信函开头）",
                example="ขอเรียนให้ทราบว่าบริษัทปิดทำการ",
                example_pronunciation="kho rian hai saap waa bri-sat pit tham-gaan",
                example_meaning="谨此告知公司暂停营业"
            ),
            CardItem(
                thai="ตามที่",
                pronunciation="dtam thee",
                meaning="按照/根据",
                example="ตามที่คุณร้องขอ",
                example_pronunciation="dtam thee khun rong-kho",
                example_meaning="根据您的要求"
            ),
            CardItem(
                thai="นับถือ",
                pronunciation="nap-theu",
                meaning="尊敬/敬重",
                example="ด้วยความนับถือ",
                example_pronunciation="duay khwam nap-theu",
                example_meaning="此致敬礼（信函结尾）"
            ),
            CardItem(
                thai="ขอบพระคุณ",
                pronunciation="khop phra khun",
                meaning="非常感谢（正式版）",
                example="ขอบพระคุณอย่างสูง",
                example_pronunciation="khop phra khun yaang soong",
                example_meaning="致以最诚挚的感谢"
            ),
        ]
    )

    return [lesson1, lesson2]


def load_courses() -> dict:
    """
    加载所有课程数据。

    返回一个字典，键为课程级别名称（如 "N5 入门级"），
    值为该级别下的 Lesson 列表。

    Returns:
        dict: 课程数据字典
    """
    courses = {
        "N5 入门级": _build_n5_lessons(),
        "N4 初级": _build_n4_lessons(),
        "N3 中级": _build_n3_lessons(),
        "N2 中高级": _build_n2_lessons(),
        "N1 高级": _build_n1_lessons(),
    }
    return courses


if __name__ == "__main__":
    # 简单测试：加载课程并打印统计信息
    courses = load_courses()
    for level_name, lessons in courses.items():
        total_cards = sum(len(lesson.cards) for lesson in lessons)
        print(f"{level_name}: {len(lessons)} 课, {total_cards} 张卡片")
