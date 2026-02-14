import sys
import os

def search_in_file(filepath, search_text, verbose=True):
    try:
        with open (filepath, 'r', encoding='utf-8') as f:
            found = 0
            for line_num, line in enumerate(f, start=1):
                if search_text in line:
                    if verbose:
                        print(f"Строка {line_num}: {line.rstrip()}")
                    found += 1
                return found
    except (UnicodeDecodeError, PermissionError):
        return 0
    except Exception as e:
        return 0
    
def search_in_dir(dir, search_text, extensions=None):
    total_found = 0
    for root, dirs, files in os.walk(dir):
        for file in files:
            filepath = os.path.join(root, file)
            if extensions:
                ext = os.path.splitext(file)[1].lower()
                if ext not in extensions:
                    continue

            found = search_in_file(filepath, search_text, verbose=True)
            total_found += found

    return total_found

def main():
    if len(sys.argv) != 3:
        print("Использование: python search_file_cli.py <dir> <text>")
        sys.exit(1)

    dir = sys.argv[1]
    search_text = sys.argv[2]

    if not os.path.isdir(dir):
        print(f"Error - {dir} is not directory")
        sys.exit(1)

    print(f"Поиск '{search_text}' в директории {dir}")
    count = search_in_dir(dir, search_text, extensions=['.txt'])

    if count >= 0:
        print(f"Всего вхождений: {count}")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

    
