import os

def save_to_file(content, output_path):
    """
    Сохраняет указанный контент в файл по заданному пути.

    :param content: Строка, содержащая текст для сохранения.
    :param output_path: Путь к файлу, в который нужно сохранить контент.
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Error writing to {output_path}: {str(e)}")

def generate_project_tree(root_dir, folders_to_scan, items_to_exclude, prefix=""):
    """
    Генерирует строки, представляющие структуру проекта.

    :param root_dir: Корневая директория проекта.
    :param folders_to_scan: Список папок для сканирования в корневой директории.
    :param items_to_exclude: Список файлов и папок, которые нужно исключить.
    :param prefix: Префикс для отступа в выводе.
    :return: Список строк, представляющих структуру дерева проекта.
    """
    lines = []  # Линии для хранения вывода структуры дерева
    lines.append(f"{prefix}├── {os.path.basename(root_dir)}/")
    prefix += "│   "

    # Получение списка файлов в корневой директории, исключая указанные элементы
    root_files = [f for f in os.listdir(root_dir) if
                  os.path.isfile(os.path.join(root_dir, f)) and f not in items_to_exclude]
    for file in root_files:
        lines.append(f"{prefix}├── {file}")

    # Обработка указанных папок
    for i, folder in enumerate(folders_to_scan):
        folder_path = os.path.join(root_dir, folder)
        if os.path.isdir(folder_path) and folder not in items_to_exclude:
            if i == len(folders_to_scan) - 1:
                lines.append(f"{prefix}└── {folder}/")
                lines.extend(generate_folder_tree(folder_path, prefix + "    ", items_to_exclude))
            else:
                lines.append(f"{prefix}├── {folder}/")
                lines.extend(generate_folder_tree(folder_path, prefix + "│   ", items_to_exclude))
    return lines

def generate_folder_tree(folder_path, prefix="", items_to_exclude=[]):
    """
    Генерирует строки, представляющие структуру содержимого папки.

    :param folder_path: Путь к папке для сканирования.
    :param prefix: Префикс для отступа в выводе.
    :param items_to_exclude: Список файлов и папок, которые нужно исключить.
    :return: Список строк, представляющих структуру дерева папки.
    """
    lines = []  # Линии для хранения вывода структуры дерева папки
    items = os.listdir(folder_path)  # Получение списка элементов в папке
    items.sort()  # Сортировка элементов для упорядоченного вывода
    for i, item in enumerate(items):
        item_path = os.path.join(folder_path, item)
        rel_path = os.path.relpath(item_path, start=project_root)
        if item in items_to_exclude or rel_path in items_to_exclude:
            continue
        if i == len(items) - 1:
            if os.path.isdir(item_path):
                lines.append(f"{prefix}└── {item}/")
                lines.extend(generate_folder_tree(item_path, prefix + "    ", items_to_exclude))
            else:
                lines.append(f"{prefix}└── {item}")
        else:
            if os.path.isdir(item_path):
                lines.append(f"{prefix}├── {item}/")
                lines.extend(generate_folder_tree(item_path, prefix + "│   ", items_to_exclude))
            else:
                lines.append(f"{prefix}├── {item}")
    return lines

def generate_file_info(root_dir, folders_to_scan, items_to_exclude):
    """
    Генерирует полную информацию о проекте, включая структуру дерева и содержимое файлов.

    :param root_dir: Корневая директория проекта.
    :param folders_to_scan: Список папок для сканирования в корневой директории.
    :param items_to_exclude: Список файлов и папок, которые нужно исключить.
    :return: Строка, содержащая всю информацию о проекте.
    """
    output = []  # Список строк для хранения вывода информации о проекте
    output.append("Project Tree Structure:")
    output.extend(generate_project_tree(root_dir, folders_to_scan, items_to_exclude))
    output.append("\n" + "=" * 80 + "\n")

    # Обработка файлов в корневой директории
    for file in os.listdir(root_dir):
        file_path = os.path.join(root_dir, file)
        if os.path.isfile(file_path) and file not in items_to_exclude:
            output.append(generate_file_content(file_path))

    # Обработка указанных папок
    for folder in folders_to_scan:
        folder_path = os.path.join(root_dir, folder)
        if os.path.isdir(folder_path) and folder not in items_to_exclude:
            for root, dirs, files in os.walk(folder_path):
                # Фильтрация папок, которые нужно исключить
                dirs[:] = [d for d in dirs if d not in items_to_exclude and os.path.join(root, d) not in items_to_exclude]
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, start=project_root)
                    if file not in items_to_exclude and rel_path not in items_to_exclude:
                        output.append(generate_file_content(file_path))

    return "\n".join(output)

def generate_file_content(file_path):
    """
    Читает содержимое файла и форматирует его для вывода.

    :param file_path: Путь к файлу, который нужно прочитать.
    :return: Строка, содержащая форматированное содержимое файла и информацию о нём.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        output = []
        output.append(f"Path: {file_path}")  # Путь к файлу
        output.append(f"File Name: {os.path.basename(file_path)}")  # Имя файла
        output.append("Code:")  # Заголовок для содержимого файла
        output.append(content)  # Содержимое файла
        output.append("-" * 80)  # Разделитель между файлами
        return "\n".join(output)
    except Exception as e:
        return f"Error reading {file_path}: {str(e)}"

# Укажите корневую директорию, папки для сканирования, элементы для исключения и путь для сохранения
project_root = '/Users/mikhailryazanov/PycharmProjects/crypto_trend_bot'  # Корневая директория
# проекта
folders_to_scan = ['bot', 'database', 'services', 'utils', 'handlers', '']  # Список папок для
# сканирования
items_to_exclude = ['extractor_code.py', 'price_trend_db.sqlite', 'project_tree_output.txt',
                    'code_extractor.py', ''
                    ]  # Список файлов и папок,
# которые нужно исключить
output_path = '/Users/mikhailryazanov/PycharmProjects/crypto_trend_bot/project_tree_output.txt'  # Путь для сохранения результата

# Генерация информации о проекте и сохранение в файл
output_content = generate_file_info(project_root, folders_to_scan, items_to_exclude)

# Создание директории, если она не существует
os.makedirs('/Users/mikhailryazanov/PycharmProjects/crypto_trend_bot', exist_ok=True)

save_to_file(output_content, output_path)  # Сохранение результата в файл