import os
import akshare as ak
import requests
import datetime
import pandas as pd
from dotenv import load_dotenv
from typing import Dict, Any, Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich import box

# 加载环境变量
load_dotenv()

# 创建全局console对象
console = Console()

class NLDataQuery:
    def __init__(self, debug_mode: bool = False):
        """初始化自然语言数据查询工具
        
        Args:
            debug_mode: 是否显示生成的代码（默认False）
        """
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_api_url = "https://api.deepseek.com/v1/chat/completions"
        self.debug_mode = debug_mode
        
        if not self.deepseek_api_key:
            raise ValueError("请设置DEEPSEEK_API_KEY环境变量")

    def call_deepseek(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        """调用DeepSeek API解析自然语言查询
        
        Returns:
            Tuple[query_type, content]: 查询类型和内容
            - query_type: "code" (数据查询) 或 "explain" (解释说明) 或 None
            - content: 生成的代码或解释文本
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.deepseek_api_key}"
            }
            
            # 改进的提示词，能够识别问题类型
            system_prompt = """
你是一个智能金融数据查询助手。你需要分析用户的输入并做出判断：

【判断规则】
1. 如果用户是要查询具体的金融数据（如股价、指数、价格等），返回格式：
   CODE|akshare代码
   
2. 如果用户是在提问、寻求解释、咨询建议等，返回格式：
   EXPLAIN|你的回答

【代码生成规则】
- 只返回可执行的Python单行表达式
- 使用akshare库（已导入为ak）获取数据
- 不要包含print语句
- 不要导入任何库(已导入库如下：
import os
import akshare as ak
import requests
import datetime
import pandas as pd
from dotenv import load_dotenv
from typing import Dict, Any, Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich import box)
- 代码应返回pandas DataFrame或基本数据类型

【示例】
用户："获取上证指数最近10天的数据" 
返回：CODE|ak.stock_zh_index_daily(symbol="sh000001").tail(10)

用户："贵州茅台的股票代码是什么？"
返回：EXPLAIN|贵州茅台的股票代码是600519（上交所）。您可以询问我获取该股票的实时数据。

用户："什么是市盈率？"
返回：EXPLAIN|市盈率（PE Ratio）是股票价格与每股收益的比率，用于衡量股票估值水平。市盈率越高，说明投资者愿意为每一元盈利支付更高的价格，通常意味着市场对公司未来增长预期较高。

用户："帮我分析一下今天的股市"
返回：EXPLAIN|我可以帮您获取实时的股市数据。您想了解哪些具体指数或股票的信息？比如上证指数、深证成指、创业板指等。
"""
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
            
            response = requests.post(
                self.deepseek_api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            response_json = response.json()
            
            if "choices" in response_json and len(response_json["choices"]) > 0:
                content = response_json["choices"][0]["message"]["content"].strip()
                
                # 解析返回内容
                if content.startswith("CODE|"):
                    return "code", content[5:].strip()
                elif content.startswith("EXPLAIN|"):
                    return "explain", content[8:].strip()
                else:
                    # 兼容旧格式
                    return "code", content
            else:
                return None, None
                
        except Exception as e:
            console.print(f"[red]✗[/red] API调用失败: {str(e)}")
            return None, None

    def execute_code(self, code: str) -> Any:
        """执行生成的代码并返回结果"""
        try:
            local_vars = {"ak": ak, "pd": pd, "datetime": datetime}
            exec(f"result = {code}", globals(), local_vars)
            return local_vars.get("result")
        except Exception as e:
            return f"执行出错: {str(e)}"

    def format_dataframe(self, df: pd.DataFrame, max_rows: int = 10) -> Table:
        """将DataFrame转换为Rich Table格式"""
        # 限制显示行数
        if len(df) > max_rows:
            df_display = pd.concat([df.head(max_rows//2), df.tail(max_rows//2)])
            show_ellipsis = True
        else:
            df_display = df
            show_ellipsis = False
        
        # 创建表格
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
        
        # 添加列
        for col in df_display.columns:
            table.add_column(str(col))
        
        # 添加行
        for idx, row in df_display.iterrows():
            table.add_row(*[str(val) for val in row])
            
            # 在中间插入省略号
            if show_ellipsis and idx == df.head(max_rows//2).index[-1]:
                table.add_row(*["..." for _ in df.columns], style="dim")
        
        return table

    def query(self, natural_language: str) -> None:
        """主函数：接收自然语言查询，返回数据结果"""
        # 显示处理状态
        with console.status("[cyan]正在分析您的查询...", spinner="dots"):
            query_type, content = self.call_deepseek(natural_language)
        
        if not query_type or not content:
            console.print(Panel(
                "[yellow]抱歉，无法理解您的查询，请尝试用其他方式表述",
                title="[red]✗ 查询失败",
                border_style="red"
            ))
            return
        
        # 处理解释类问题
        if query_type == "explain":
            console.print(Panel(
                Markdown(content),
                title="[green]💡 回答",
                border_style="green",
                padding=(1, 2)
            ))
            return
        
        # 处理数据查询
        if self.debug_mode:
            console.print(f"[dim]生成的代码: {content}[/dim]")
        
        with console.status("[cyan]正在获取数据...", spinner="dots"):
            result = self.execute_code(content)
        
        # 格式化输出结果
        if isinstance(result, str) and "出错" in result:
            console.print(Panel(
                f"[red]{result}[/red]",
                title="[red]✗ 执行错误",
                border_style="red"
            ))
        elif isinstance(result, pd.DataFrame):
            console.print(Panel(
                self.format_dataframe(result),
                title=f"[green]✓ 查询结果[/green] [dim]({len(result)} 条记录)[/dim]",
                border_style="green"
            ))
        else:
            console.print(Panel(
                str(result),
                title="[green]✓ 查询结果",
                border_style="green",
                padding=(1, 2)
            ))

def main():
    """主程序入口"""
    try:
        # 显示欢迎界面
        console.print(Panel.fit(
            "[bold cyan]金融数据智能查询助手[/bold cyan]\n"
            "[dim]基于 AKShare 和 DeepSeek AI[/dim]",
            border_style="cyan"
        ))
        
        console.print("\n[bold]使用说明:[/bold]")
        console.print("• 您可以用自然语言查询金融数据")
        console.print("• 也可以提出问题寻求解释和建议")
        console.print("• 输入 [yellow]'exit'[/yellow] 或 [yellow]'quit'[/yellow] 退出程序")
        console.print("• 输入 [yellow]'debug'[/yellow] 切换调试模式\n")
        
        console.print("[bold]示例查询:[/bold]")
        examples = [
            "获取上证指数最近10天的数据",
            "查询贵州茅台的最新股价",
            "什么是市盈率？",
            "获取国内成品油价格调整信息"
        ]
        for i, example in enumerate(examples, 1):
            console.print(f"  {i}. [cyan]{example}[/cyan]")
        
        console.print()
        
        # 创建查询工具实例
        query_tool = NLDataQuery(debug_mode=False)
        
        while True:
            try:
                # 获取用户输入
                user_input = console.input("[bold green]❯[/bold green] ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["exit", "quit", "退出"]:
                    console.print("\n[cyan]感谢使用，再见！[/cyan]")
                    break
                
                if user_input.lower() == "debug":
                    query_tool.debug_mode = not query_tool.debug_mode
                    status = "开启" if query_tool.debug_mode else "关闭"
                    console.print(f"[yellow]调试模式已{status}[/yellow]\n")
                    continue
                
                # 执行查询
                query_tool.query(user_input)
                console.print()  # 空行分隔
                
            except KeyboardInterrupt:
                console.print("\n\n[cyan]感谢使用，再见！[/cyan]")
                break
            except Exception as e:
                console.print(f"[red]✗ 出错: {str(e)}[/red]\n")
    
    except Exception as e:
        console.print(f"[red]程序初始化失败: {str(e)}[/red]")

if __name__ == "__main__":
    main()