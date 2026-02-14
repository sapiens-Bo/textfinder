import sys

def search_in_file(filepath, search_text):
    try:
        with open (filepath, 'r', encoding='utf-8') as f:
            found = 0
            for line_num, line in enumerate(f, start=1):
                if search_text in line:
                    print(f"Строка {line_num}: {line.rstrip()}")
                    found += 1
                return found
    except FileNotFoundError:
        print(f"Ошибка: файл {filepath} не найден")
        return -1
    except Exception as e:
        print(f"Error read file {filepath}")
        return -1
    
def main():
    if len(sys.argv) != 3:
        print("Использование: python search_file_cli.py <file> <text>")
        sys.exit(1)

    filepath = sys.argv[1]
    search_text = sys.argv[2]

    print(f"Поиск '{search_text}' в файле {filepath}")
    count = search_in_file(filepath, search_text)

    if count >= 0:
        print(f"Всего вхождений: {count}")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

    
