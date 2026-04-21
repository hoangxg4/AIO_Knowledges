import subprocess
import os
import re
from datetime import datetime

def run_ingest():
    source_file = "source.txt"
    output_dir = "consolidated-docs"
    index_file = "SUMMARY.md"
    
    if not os.path.exists(source_file):
        print(f"Lỗi: Không tìm thấy {source_file}")
        return

    with open(source_file, "r") as f:
        repos = [line.strip() for line in f if line.strip()]

    os.makedirs(output_dir, exist_ok=True)
    processed_repos = []

    # 1. Chỉ tập trung vào tài liệu hữu ích
    include_patterns = "*.md,*.txt,*.rst,*.adoc,*.wiki"
    
    # 2. TRÁNH FILE RÁC: Loại bỏ các file pháp lý, lịch sử thay đổi hoặc cấu hình bot
    # Điều này giúp AI tập trung vào "Kiến thức" thay vì "Thủ tục"
    exclude_patterns = (
        "LICENSE*,COPYING*,CHANGELOG*,HISTORY*,CONTRIBUTING*,"
        "SECURITY*,CODE_OF_CONDUCT*,RELEASE*,*.log,*.tmp,.github/*"
    )

    for repo_url in repos:
        # 3. TÊN FILE THÔNG MINH: Lấy định dạng 'Organization-Repository.md'
        # Ví dụ: https://github.com/google/jax -> google-jax.md
        match = re.search(r'(?:github\.com|gitlab\.com|bitbucket\.org)/([^/]+)/([^/?#]+)', repo_url)
        if match:
            org, repo = match.groups()
            clean_name = f"{org}-{repo}".lower()
        else:
            # Fallback nếu URL lạ
            clean_name = re.sub(r'https?://|/|\.', '-', repo_url).strip('-').lower()
            
        output_path = os.path.join(output_dir, f"{clean_name}.md")
        
        print(f"🚀 Đang xử lý: {repo_url}")
        
        # Lệnh GitIngest với đầy đủ bộ lọc
        cmd = [
            "gitingest", repo_url, 
            "-o", output_path, 
            "-i", include_patterns,
            "-e", exclude_patterns
        ]

        try:
            subprocess.run(cmd, check=True, timeout=300)
            processed_repos.append({
                "url": repo_url, 
                "file": output_path, 
                "name": f"{org}/{repo}" if match else clean_name
            })
            print(f"✅ Đã lưu: {output_path}")
        except Exception as e:
            print(f"❌ Thất bại {repo_url}: {e}")

    create_index(index_file, processed_repos)

def create_index(index_file, repos):
    with open(index_file, "w", encoding="utf-8") as f:
        f.write("# 📚 AI Knowledge Base Index\n\n")
        f.write(f"**Cập nhật:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        f.write("| Dự án | Nguồn Gốc | File Digest (Tối ưu cho AI) |\n")
        f.write("| :--- | :--- | :--- |\n")
        for r in repos:
            f.write(f"| {r['name']} | [Link]({r['url']}) | [`{r['file']}`]({r['file']}) |\n")
    print(f"✨ Đã cập nhật mục lục {index_file}")

if __name__ == "__main__":
    run_ingest()
