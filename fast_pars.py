from bs4 import BeautifulSoup
import json

def quick_parse(html_content):
    """Быстрый парсинг ключевых данных"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Название
    title = soup.find('h1', class_='show_h1')
    title = title.get_text().strip() if title else 'Не найдено'
    
    # Цена
    price_elem = soup.find('span', id='show_price')
    price = price_elem.get_text().strip() if price_elem else 'Не найдено'
    
    # Текущий цвет
    color_elem = soup.find('small', class_='act_color_name_show')
    color = color_elem.get_text().strip() if color_elem else 'Не указан'
    
    # Все цвета
    colors = []
    color_links = soup.find_all('a', class_='multi_color')
    for link in color_links:
        color_name = link.get('data-name-color') or link.get('title', '')
        if color_name and color_name not in colors:
            colors.append(color_name)
    
    # Изображение
    img = soup.find('img', class_='slider_photo_img')
    image_url = img.get('src') if img else 'Не найдено'
    if image_url and not image_url.startswith('http'):
        image_url = 'https://edwardpnz.ru' + image_url
    
    return {
        'title': title,
        'price': f"{price} руб." if price != 'Не найдено' else price,
        'current_color': color,
        'all_colors': colors,
        'image': image_url
    }

# Ваш HTML контент
html_content = """
<!-- вставьте сюда ваш сохраненный HTML -->
"""

# Быстрый тест
result = quick_parse(html_content)
print("⚡ БЫСТРЫЙ РЕЗУЛЬТАТ:")
print(json.dumps(result, ensure_ascii=False, indent=2))