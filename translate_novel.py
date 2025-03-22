from ebooklib import epub, ITEM_DOCUMENT  # 修正导入
from bs4 import BeautifulSoup
import re
import openai
import time
import json


def read_epub(file_path):
    # 打开 EPUB 文件
    book = epub.read_epub(file_path)

    # 初始化一个空字符串来存储文本
    text = ""

    # 遍历书籍中的所有项目
    for item in book.get_items():
        # 检查项目类型是否为文档（通常是 HTML 或 XHTML）
        if item.get_type() == ITEM_DOCUMENT:  # 使用正确的 ITEM_DOCUMENT
            # 将内容添加到文本字符串中
            text += item.get_content().decode('utf-8')

    return text


def clean_html(html):
    # 使用 BeautifulSoup 清理 HTML 标签
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()


def save_to_txt(text, output_path):
    # 将文本保存到 TXT 文件
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(text)


def load_and_split_text(file_path, chunk_size=1000, max_deviation=100):
    """
    从文本文件中加载内容并按指定大小拆分文本。
    在句号处截停，允许在 chunk_size 附近波动，统一换行符为 \n，并确保段落之间有双换行符。

    :param file_path: 文本文件路径
    :param chunk_size: 每个 chunk 的目标字符数
    :param max_deviation: 允许的 chunk_size 波动范围（正负值）
    :return: 拆分后的文本列表
    """
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # 统一换行符为 \n
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # 确保段落之间有双换行符
    text = re.sub(r'\n+', '\n\n', text)
    # 将双换行符替换为单换行符
    # text = text.replace('\n\n', '\n')

    chunks = []
    start = 0

    while start < len(text):
        # 计算当前 chunk 的结束位置
        end = start + chunk_size

        # 如果结束位置超出文本长度，直接取到文本末尾
        if end >= len(text):
            chunks.append(text[start:])
            break

        # 在 chunk_size 附近查找最近的句号
        # 向前查找
        stop_index_forward = text.rfind('.', start, end + max_deviation) + 1  # +1 是为了包含句号
        # 向后查找
        stop_index_backward = text.find('.', end - max_deviation, end + max_deviation) + 1  # +1 是为了包含句号

        # 选择最接近 chunk_size 的句号位置
        if stop_index_forward == 0:  # 向前查找未找到句号
            stop_index = stop_index_backward if stop_index_backward != 0 else end
        elif stop_index_backward == 0:  # 向后查找未找到句号
            stop_index = stop_index_forward
        else:
            # 选择距离 chunk_size 更近的句号位置
            stop_index = (
                stop_index_forward
                if abs(stop_index_forward - end) < abs(stop_index_backward - end)
                else stop_index_backward
            )

        # 如果找不到句号，则直接截取到 end
        if stop_index <= start:
            stop_index = end

        # 提取 chunk
        chunk = text[start:stop_index].strip()
        if chunk:  # 忽略空 chunk
            chunks.append(chunk)

        # 更新 start 位置，紧挨着上一次截取的结束位置
        start = stop_index

    return chunks


class Translator:
    def __init__(self, api_key, system_prompt="You are a helpful assistant that translates text."):
        self.api_key = api_key
        self.system_prompt = system_prompt
        openai.api_key = self.api_key

    def translate_text(self, text, target_language="Chinese"):
        prompt = f"Translate the following text to {target_language}. Only return the translated text, do not include any additional explanations or notes. Text to translate: {text}"

        response = openai.chat.completions.create(
            model="gpt-4-turbo",  # 使用 GPT-4 Turbo 模型以获得优化的性能
            messages=[
                {"role": "system", "content": self.system_prompt},  # 定义系统级行为
                {"role": "user", "content": prompt}  # 用户输入提示
            ],
            temperature=0.5,  # 降低随机性以确保结构化和稳定的响应
            top_p=0.9,  # 防止极端或高度不可能的输出
            n=1,  # 只生成一个响应
            # response_format={"type": "json_object"},  # 强制 GPT 返回 JSON 对象
            presence_penalty=0.2,  # 稍微鼓励响应中的新内容
            frequency_penalty=0.2,  # 稍微减少重复短语
            # stop=["\n\n"]  # 在段落结束时停止响应
        )

        # 提取翻译后的文本
        translated_text = response.choices[0].message.content
        finish_reason = response.choices[0].finish_reason
        if finish_reason == 'length':
            print("响应被截断，可能需要增加 max_tokens 或分页处理。")
        elif finish_reason == 'stop':
            print("响应完整。")
        else:
            print(f"响应状态: {finish_reason}")
        return translated_text


def save_translated_chunks(novel_chunks, output_file, target_language="Chinese", delay_seconds=2, api_key=None):
    translator = Translator(api_key)
    with open(output_file, 'w', encoding='utf-8') as file:
        for i, chunk in enumerate(novel_chunks):
            print(f"正在翻译第 {i+1}/{len(novel_chunks)} 个文本块...")
            try:
                # 翻译每个 chunk
                translated_chunk = translator.translate_text(chunk, target_language=target_language)
                
                # 将翻译后的 chunk 写入文件
                file.write(translated_chunk)  # 写入翻译后的文本
                file.write("\n")  # 保留原文本中的换行符
                file.flush()  # 确保内容立即写入文件

                # 在每次请求后添加延迟，避免触发速率限制
                if i < len(novel_chunks) - 1:  # 最后一个 chunk 不需要延迟
                    time.sleep(delay_seconds)

            except Exception as e:
                print(f"处理第 {i+1} 个文本块时出错: {e}")
                file.write(chunk)  # 如果翻译失败，写入原文
                file.write("\n")  # 保留原文本中的换行符
                file.flush()  # 确保内容立即写入文件

    print(f"翻译后的文本已保存到 {output_file}")


if __name__ == "__main__":
    # 读取 JSON 文件
    with open("trans.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    # 使用函数读取 EPUB 文件
    file_path = config["Trans"]["epub_path"]  # 替换为你的 EPUB 文件路径
    output_path = config["Trans"]["txt_path"]  # 替换为你想保存的 TXT 文件路径
    # 读取 EPUB 文件内容
    text = read_epub(file_path)
    # 清理 HTML 标签
    cleaned_text = clean_html(text)
    # 将清理后的文本保存到 TXT 文件
    save_to_txt(cleaned_text, output_path)
    print(f"文本已保存到 {output_path}")
    # 访问配置数据
    novel_pth = output_path
    chunk_size = config["Trans"]["chunk_size"]
    max_deviation = config["Trans"]["max_deviation"]
    # 读取小说文本并拆分成片段
    novel_chunks = load_and_split_text(novel_pth, chunk_size=chunk_size, max_deviation=max_deviation)
    print("chunk_size:", chunk_size)
    print("max_deviation:", max_deviation)
    print(f"Total {len(novel_chunks)} scene segments extracted")  # Display the number of text chunks
    
    output_file = config["Trans"]["output"]
    target_language = config["Trans"]["target_language"]
    api_key = config["Trans"]["OPENAI_API_KEY"]
    save_translated_chunks(novel_chunks, output_file, target_language, delay_seconds=1, api_key=api_key)