import os
from openai import OpenAI

class LocalThaiTeacher:
    def __init__(self):
        # 关键点：这里的 URL 指向你本地运行的 Ollama 引擎，完全免费，不需要 API Key
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"  # 本地运行，这里随便填个字符串占位即可
        )
        self.conversation_history = []
        
    def load_textbook(self, file_path: str):
        """原生文件读取"""
        if not os.path.exists(file_path):
            return "教材文件不存在，请先创建 textbook.txt"
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def init_teacher(self, textbook_content: str):
        """用 System Prompt 锁死本地模型的角色"""
        system_prompt = f"""
        你是一位温柔的泰语老师。
        你手上有以下这份教材内容：
        ----
        {textbook_content}
        ----
        请严格遵守以下规则：
        1. 绝不要一次性把教材念完。
        2. 请根据教材内容，每次只挑一个词汇或语法点，用中文对学生进行互动提问。
        3. 当学生回答后，你必须指出他的错误并给出辅导。
        """
        self.conversation_history.append({"role": "system", "content": system_prompt})

    def chat(self, user_input: str) -> str:
        """与本地大模型进行多轮对话"""
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # 调用本地的 llama3 模型
        response = self.client.chat.completions.create(
            model="llama3", 
            messages=self.conversation_history
        )
        
        ai_reply = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": ai_reply})
        return ai_reply

# --- 程序入口 ---
if __name__ == "__main__":
    teacher = LocalThaiTeacher()
    
    print("正在读取本地泰语教材...")
    textbook_data = teacher.load_textbook("textbook.txt")
    teacher.init_teacher(textbook_data)
    
    print("\n[本地免费版] 泰语老师已就位！(输入 'exit' 退出课室)\n" + "="*40)
    
    # 引导第一句对话
    ai_say = teacher.chat("老师好，我们开始上课吧！")
    print(f"AI 老师: {ai_say}\n")
    
    # 循环互动
    while True:
        user_say = input("你的回答 ->: ")
        if user_say.strip().lower() == "exit":
            print("下课！萨瓦迪卡~")
            break
            
        ai_say = teacher.chat(user_say)
        print(f"\nAI 老师: {ai_say}\n")