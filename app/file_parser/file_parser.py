import os

def find_files_in_directory(path, this_id):
    files = []
    base_path = os.path.join(path, this_id)  # Путь к каталогу с id
    for root, dirs, filenames in os.walk(base_path):
        for filename in filenames:
            # Относительный путь к файлу от base_path
            relative_path = os.path.relpath(os.path.join(root, filename), base_path)
            files.append(relative_path)
    return files


# Пример использования:
if __name__ == '__main__':
    path = '../../data/response/'
    this_id = 'huOF6MZIm1oSlg'
    files = find_files_in_directory(path, this_id)
    for file in files:
        print(file)