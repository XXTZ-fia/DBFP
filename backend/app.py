"""
金融数据智能查询助手 - Flask 后端 API
"""
import os
import sys
import akshare as ak
import requests
import datetime
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from typing import Optional, Tuple, Any

# 加载环境变量
load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 数据存储目录
DATA_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data')
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)


def call_deepseek(prompt: str, context: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """调用 DeepSeek API 解析自然语言查询"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        system_prompt = """
你是一个智能金融数据查询助手。你需要分析用户的输入并做出判断：

【判断规则】
1. 如果用户是要查询（如以查询开头）具体的金融数据（如股价、指数、价格等），返回格式：
   CODE|akshare代码
   
2. 如果用户是在提问、寻求解释、咨询建议等，返回格式：
   EXPLAIN|你的回答

【代码生成规则】
- 只返回可执行的Python单行表达式
- 使用akshare库（已导入为ak）获取数据
- 不要包含print语句
- 不要导入任何库
- 代码应返回pandas DataFrame或基本数据类型

【示例】
用户："获取上证指数最近10天的数据" 
返回：CODE|ak.stock_zh_index_daily(symbol="sh000001").tail(10)

用户："贵州茅台的股票代码是什么？"
返回：EXPLAIN|贵州茅台的股票代码是600519（上交所）。您可以询问我获取该股票的实时数据。

用户："帮我分析一下今天的股市"
返回：EXPLAIN|我可以帮您获取实时的股市数据。您想了解哪些具体指数或股票的信息？比如上证指数、深证成指、创业板指等。
"""
        
        if context:
            max_ctx = 3000
            ctx = context if len(context) <= max_ctx else context[:max_ctx] + "..."
            user_content = f"{prompt}\n\n参考资料（来自本地知识库，供回答参考）：\n{ctx}"
        else:
            user_content = prompt

        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.3
        }
        
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=data,
            timeout=30
        )
        
        response_json = response.json()
        
        if "choices" in response_json and len(response_json["choices"]) > 0:
            content = response_json["choices"][0]["message"]["content"].strip()
            
            if content.startswith("CODE|"):
                return "code", content[5:].strip()
            elif content.startswith("EXPLAIN|"):
                return "explain", content[8:].strip()
            else:
                return "code", content
        else:
            return None, None
            
    except Exception as e:
        return None, f"API调用失败: {str(e)}"


def execute_code(code: str) -> Any:
    """执行生成的代码并返回结果"""
    try:
        local_vars = {"ak": ak, "pd": pd, "datetime": datetime}
        exec(f"result = {code}", globals(), local_vars)
        return local_vars.get("result")
    except Exception as e:
        return f"执行出错: {str(e)}"


@app.route('/')
def index():
    """返回前端页面"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/query', methods=['POST'])
def query():
    """处理自然语言查询"""
    try:
        data = request.json
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({'success': False, 'error': '请输入查询内容'})
        
        if not DEEPSEEK_API_KEY:
            return jsonify({'success': False, 'error': '未配置 DeepSeek API Key'})
        
        # 调用 DeepSeek 解析查询
        query_type, content = call_deepseek(user_query)
        
        if not query_type or not content:
            return jsonify({'success': False, 'error': '无法理解您的查询，请尝试用其他方式表述'})
        
        # 处理解释类问题
        if query_type == "explain":
            return jsonify({
                'success': True,
                'type': 'explain',
                'content': content
            })
        
        # 处理数据查询
        result = execute_code(content)
        
        if isinstance(result, str) and "出错" in result:
            return jsonify({'success': False, 'error': result, 'code': content})
        
        if isinstance(result, pd.DataFrame):
            # 将 DataFrame 转换为 JSON
            return jsonify({
                'success': True,
                'type': 'data',
                'data': result.to_dict(orient='records'),
                'columns': list(result.columns),
                'total': len(result),
                'code': content
            })
        else:
            return jsonify({
                'success': True,
                'type': 'value',
                'content': str(result),
                'code': content
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/save', methods=['POST'])
def save_data():
    """保存查询结果到文件"""
    try:
        data = request.json
        query_name = data.get('queryName', 'data')
        records = data.get('data', [])
        
        if not records:
            return jsonify({'success': False, 'error': '没有可保存的数据'})
        
        # 生成文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_name = "".join(c if c.isalnum() or c in "._- " else "" for c in query_name)
        clean_name = clean_name[:30]
        filename = f"{clean_name}_{timestamp}.csv"
        filepath = os.path.join(DATA_FOLDER, filename)
        
        # 保存 CSV
        df = pd.DataFrame(records)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': os.path.abspath(filepath)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/history', methods=['GET'])
def get_history():
    """获取历史保存的数据文件列表"""
    try:
        files = []
        for f in os.listdir(DATA_FOLDER):
            if f.endswith('.csv'):
                filepath = os.path.join(DATA_FOLDER, f)
                stat = os.stat(filepath)
                files.append({
                    'filename': f,
                    'size': stat.st_size,
                    'modified': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # 按修改时间倒序
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({'success': True, 'files': files})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """下载历史数据文件"""
    try:
        return send_from_directory(DATA_FOLDER, filename, as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    print("=" * 50)
    print("金融数据智能查询助手 - Web 服务")
    print("=" * 50)
    print(f"服务地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
