import os

def merge_project(output_filename="toan_bo_code.txt"):
    # Các thư mục không cần đọc
    ignore_dirs = {'venv', '.git', '__pycache__', 'raw', 'processed_data', '.pytest_cache'}
    
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk('.'):
            # Bỏ qua các thư mục rác/data
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                # Chỉ lấy các file code hoặc cấu hình quan trọng
                if file.endswith(('.py', '.json', '.yaml', '.md', '.txt')) and file != output_filename:
                    file_path = os.path.join(root, file)
                    outfile.write(f"\n\n{'='*60}\n")
                    outfile.write(f"--- FILE: {file_path} ---\n")
                    outfile.write(f"{'='*60}\n\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"[Không thể đọc file này: {e}]\n")
                        
    print(f"Đã gộp xong! Hãy mở file {output_filename} và copy cho AI.")

if __name__ == "__main__":
    merge_project()