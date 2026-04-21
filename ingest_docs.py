import subprocess
import os
import re

def get_token(url):
    """Lấy token dựa trên nền tảng của URL"""
    if "github.com" in url:
        return os.getenv("GITHUB_TOKEN")
    elif "gitlab.com" in url:
        return os.getenv("GITLAB_TOKEN")
    elif "bitbucket.org" in url:
        return os.getenv("BITBUCKET_TOKEN")
    return None

def run_ingest():
    if not os.path.exists("source.txt"):
        print("Lỗi: Không tìm thấy file source.txt")
        return

    with open("source.txt", "r") as f:
        repos = [line.strip() for line in f if line.strip()]

    output_dir = "consolidated-docs"
    os.makedirs(output_dir, exist_ok=True)

    # Chỉ tập trung vào các định dạng tài liệu
    # Thêm .rst, .txt, .pdf (nếu GitIngest hỗ trợ) hoặc các file config nếu cần
    doc_patterns = "*.md,*.txt,*.rst,*.adoc,*.wiki"

    for repo_url in repos:
        # Xử lý tên file an toàn từ URL
        clean_name = re.sub(r'https?://|/|\.', '-', repo_url).strip('-')
        output_file = os.path.join(output_dir, f"{clean_name}.md")
        
        token = get_token(repo_url)
        
        print(f"--- Đang xử lý tài liệu từ: {repo_url} ---")
        
        # Xây dựng lệnh GitIngest
        cmd = ["gitingest", repo_url, "-o", output_file, "-i", doc_patterns]
        
        if token:
            cmd.extend(["-t", token])

        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Đã tạo: {output_file}")
        except subprocess.CalledProcessError:
            print(f"❌ Lỗi xử lý: {repo_url}")

if __name__ == "__main__":
    run_ingest()
