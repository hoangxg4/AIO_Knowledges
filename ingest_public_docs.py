import subprocess
import os
import re

def run_ingest():
    if not os.path.exists("source.txt"):
        print("Lỗi: Không tìm thấy file source.txt")
        return

    with open("source.txt", "r") as f:
        repos = [line.strip() for line in f if line.strip()]

    output_dir = "consolidated-docs"
    os.makedirs(output_dir, exist_ok=True)

    # Chỉ lấy các định dạng tài liệu để tối ưu cho AI
    doc_patterns = "*.md,*.txt,*.rst,*.adoc,*.wiki"

    for repo_url in repos:
        # Tạo tên file từ URL: gộp username và repo-name
        # Ví dụ: https://github.com/microsoft/vscode -> microsoft-vscode.md
        clean_name = re.sub(r'https?://(github\.com|gitlab\.com|bitbucket\.org)/', '', repo_url)
        clean_name = re.sub(r'[/.]', '-', clean_name).strip('-')
        output_file = os.path.join(output_dir, f"{clean_name}.md")
        
        print(f"--- Đang fetch Public Docs từ: {repo_url} ---")
        
        # Lệnh GitIngest không dùng token
        cmd = ["gitingest", repo_url, "-o", output_file, "-i", doc_patterns]

        try:
            # Chạy lệnh và giới hạn thời gian chờ (timeout) để tránh treo workflow
            subprocess.run(cmd, check=True, timeout=300) 
            print(f"✅ Thành công: {output_file}")
        except Exception as e:
            print(f"❌ Thất bại: {repo_url} - Lỗi: {e}")

if __name__ == "__main__":
    run_ingest()
