from langchain.text_splitter import RecursiveCharacterTextSplitter
import json

# 读取 JSON 文件
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)


def load_and_split_text(file_path, chunk_size=2000, chunk_overlap=200):
    """
    Reads a novel text file and splits it into smaller chunks for processing.

    Parameters:
        file_path (str): The path to the novel text file.
        chunk_size (int): The maximum number of characters per chunk. Default is 2000.
        chunk_overlap (int): The number of overlapping characters between chunks to preserve context. Default is 200.

    Returns:
        list: A list of text chunks.
    """
    # Read the novel text file
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Use recursive text splitting to maintain coherence
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_text(text)

    return chunks

if __name__ == "__main__":
    # 访问配置数据
    novel_pth = config["project_paths"]["data_dir"]
    chunk_size=config["text_splitter"]["chunk_size"]
    chunk_overlap=config["text_splitter"]["chunk_overlap"]
    # 读取小说文本并拆分成片段
    novel_chunks = load_and_split_text(novel_pth, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    print("chunk_size:", chunk_size)
    print("chunk_overlap:", chunk_overlap)
    # ✅ Verify the output
    print(type(novel_chunks))  # Check the data type of the output
    print(f"Total {len(novel_chunks)} scene segments extracted")  # Display the number of text chunks
    print(novel_chunks[0])  # Preview the first chunk