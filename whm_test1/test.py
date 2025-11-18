import os
import akshare as ak
import requests
import datetime
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# 加载环境变量
load_dotenv()

class NLDataQuery:
    def __init__(self):
        """初始化自然语言数据查询工具"""
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_api_url = "https://api.deepseek.com/v1/chat/completions"
        
        if not self.deepseek_api_key:
            raise ValueError("请设置DEEPSEEK_API_KEY环境变量")
        
        # 移除错误的set_option调用，akshare没有这个方法
        # 如需控制缓存，可以在具体函数中通过参数控制（部分akshare函数有use_cache参数）

    def call_deepseek(self, prompt: str) -> Optional[str]:
        """调用DeepSeek API解析自然语言查询为akshare代码"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.deepseek_api_key}"
            }
            
            # 构造提示词，指导模型生成正确的akshare代码
            system_prompt = """
            你是一个数据查询助手，需要将用户的自然语言查询转换为使用akshare库获取数据的Python代码。
            请遵循以下规则：
            1. 只返回可执行的Python单行表达式，不要添加任何解释说明
            2. 代码必须是完整的，可以直接执行并返回数据
            3. 使用akshare库获取数据，返回的结果应为pandas DataFrame或基本数据类型
            4. 不要包含print语句，只需返回数据的代码
            5. 如果无法确定如何实现，返回"无法解析该查询"
            6. 返回的代码不需要任何格式，以纯文本形式返回
            7. 不要导入任何库（已导入的库如下：import os; import akshare as ak; import requests; import datetime; from dotenv import load_dotenv; from typing import Dict, Any, Optional）
            例如：
            用户问"获取上证指数最近10天的数据"，应返回：
            ak.stock_zh_index_daily(symbol="sh000001").tail(10)
            """
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            }
            
            response = requests.post(
                self.deepseek_api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            response_json = response.json()
            
            if "choices" in response_json and len(response_json["choices"]) > 0:
                return response_json["choices"][0]["message"]["content"].strip()
            else:
                return None
                
        except Exception as e:
            print(f"调用DeepSeek API出错: {str(e)}")
            return None

    def execute_code(self, code: str) -> Any:
        """执行生成的代码并返回结果"""
        try:
            # 创建一个安全的执行环境
            local_vars = {"ak": ak}
            exec(f"result = {code}", globals(), local_vars)
            return local_vars.get("result")
        except Exception as e:
            print(f"执行代码出错: {str(e)}")
            return f"执行代码时出错: {str(e)}"

    def query(self, natural_language: str) -> Any:
        """主函数：接收自然语言查询，返回数据结果"""
        print(f"正在解析查询: {natural_language}")
        
        # 调用DeepSeek生成代码
        code = self.call_deepseek(natural_language)
        
        if not code or code == "无法解析该查询":
            return "抱歉，无法理解您的查询，请尝试用其他方式表述"
            
        print(f"生成的代码: {code}")
        
        # 执行代码并返回结果
        result = self.execute_code(code)
        return result

if __name__ == "__main__":
    try:
        query_tool = NLDataQuery()
        
        print("欢迎使用自然语言金融数据查询工具")
        print("示例查询：")
        print("1. 获取上证指数最近10天的数据")
        print("2. 获取贵州茅台的最新股价")
        print("3. 获取国内成品油价格调整信息")
        print("输入'exit'退出")
        
        while True:
            user_input = input("\n请输入您的查询: ")
            if user_input.lower() == "exit":
                break
                
            result = query_tool.query(user_input)
            print("\n查询结果:")
            print(result)
            
    except Exception as e:
        print(f"程序出错: {str(e)}")