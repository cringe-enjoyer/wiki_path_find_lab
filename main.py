import requests
from bs4 import BeautifulSoup
import time

def get_wikipedia_links(url, base_url):
    """Получает все ссылки на другие статьи Википедии"""
    try:
        print(f"Загружаем страницу: {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        links = set()
        for a in soup.select('div.mw-parser-output a[href^="/wiki/"]'):
            href = a.get('href')
            if ":" not in href:  # Исключаем специальные страницы (например, "File:", "Help:")
                full_url = base_url + href
                links.add(full_url)

        print(f"Найдено {len(links)} ссылок на странице: {url}")
        return links
    except Exception as e:
        print(f"Ошибка при получении ссылок с {url}: {e}")
        return set()

def find_path(start_url, target_url, rate_limit):
    """Поиск пути между двумя URL-адресами"""
    visited = set()
    stack = [(start_url, [start_url])]  # Стек с текущим URL и путем до него
    requests_made = 0

    while stack:
        current_url, path = stack.pop()
        print(f"Обрабатываем URL: {current_url}, текущий путь: {' -> '.join(path)}")

        if current_url == target_url:
            print(f"Цель достигнута: {target_url}")
            return path

        if len(path) > 5:
            print(f"Глубина поиска превышена для URL: {current_url}")
            continue

        if current_url not in visited:
            visited.add(current_url)
            links = get_wikipedia_links(current_url, base_url="https://en.wikipedia.org")
            requests_made += 1

            if requests_made >= rate_limit:
                print("Достигнут лимит запросов. Ждем 1 секунду")
                time.sleep(1)
                requests_made = 0

            for link in links:
                if link not in visited:
                    print(f"Добавляем ссылку в стек: {link}")
                    stack.append((link, path + [link]))

    print(f"Путь не найден за 5 шагов от {start_url} до {target_url}")
    return None

def save_path_to_file(path, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(" -> ".join(path))
        print(f"Путь сохранен в файл: {filename}")

def search(url1, url2, rate_limit):
    print("Начат поиск пути от url1 к url2")
    path1 = find_path(url1, url2, rate_limit)
    if path1:
        print(f"Путь от {url1} к {url2}:")
        print(" -> ".join(path1))
        save_path_to_file(path1, "path_url1_to_url2.txt")
    else:
        print(f"Путь от {url1} к {url2} не найден за 5 шагов.")

    print("Начат поиск пути от url2 к url1")
    path2 = find_path(url2, url1, rate_limit)
    if path2:
        print(f"Путь от {url2} к {url1}:")
        print(" -> ".join(path2))
        save_path_to_file(path2, "path_url2_to_url1.txt")
    else:
        print(f"Путь от {url2} к {url1} не найден за 5 шагов.")

if __name__ == '__main__':
    url1 = "https://en.wikipedia.org/wiki/Six_degrees_of_separation"
    url2 = "https://en.wikipedia.org/wiki/American_Broadcasting_Company"
    rate_limit = 10

    search(url1, url2, rate_limit)