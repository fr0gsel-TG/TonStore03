from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import psycopg2
import json
import re
import os
from datetime import datetime

load_dotenv()

class IPhoneCatalogParser:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
    
    def parse_catalog_html(self, html_content):
        """Парсинг HTML страницы каталога iPhone"""
        print("🔍 Анализируем каталог HTML...")
        
        if not html_content or len(html_content.strip()) < 100:
            print("❌ HTML слишком короткий или пустой")
            return {'success': False, 'error': 'Empty HTML'}
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Сохраним HTML для отладки
        with open('debug_catalog.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("💾 Каталог HTML сохранен в debug_catalog.html")
        
        # Ищем все карточки товаров
        products = self._extract_products(soup)
        
        result = {
            'products': products,
            'total_products': len(products),
            'parsed_at': datetime.now().isoformat(),
            'success': True
        }
        
        print(f"📊 Найдено товаров: {len(products)}")
        return result
    
    def _extract_products(self, soup):
        """Извлечение всех товаров из каталога"""
        print("🔍 Ищем карточки товаров...")
        
        products = []
        
        # Ищем все div с классом card (карточки товаров)
        card_elements = soup.find_all('div', class_='card')
        print(f"🔍 Найдено карточек товаров: {len(card_elements)}")
        
        for i, card in enumerate(card_elements):
            print(f"\n📦 Обрабатываем товар {i+1}/{len(card_elements)}...")
            
            product_data = self._parse_single_card(card)
            if product_data:
                products.append(product_data)
        
        return products
    
    def _parse_single_card(self, card):
        """Парсинг одной карточки товара"""
        try:
            # ID товара
            card_id = card.get('id', '')
            product_id = card_id.replace('card_c_', '') if 'card_c_' in card_id else 'unknown'
            
            # Название модели
            name_elem = card.find('a', class_='card_name')
            model_name = name_elem.get_text().strip() if name_elem else 'Неизвестно'
            
            # Цена
            price_elem = card.find('span', class_='card_price')
            price_text = price_elem.get_text().strip() if price_elem else ''
            numeric_price = 0
            
            if price_text:
                clean_price = price_text.replace(' ', '').replace('руб.', '')
                try:
                    numeric_price = int(clean_price)
                except ValueError:
                    numeric_price = 0
            
            # Старая цена (если есть)
            old_price_elem = card.find('strike')
            old_price = old_price_elem.get_text().strip() if old_price_elem else ''
            
            # Текущий цвет
            color_elem = card.find('small', class_='act_color_name')
            current_color = color_elem.get_text().strip() if color_elem else 'Не указан'
            
            # Все доступные цвета
            colors = []
            color_elements = card.find_all('button', class_='multi_color')
            for element in color_elements:
                color_name = element.get('data-name-color') or element.get('title', '')
                if color_name and color_name not in colors:
                    colors.append(color_name)
            
            # Память
            memory_options = []
            current_memory = 'Не указана'
            memory_elements = card.find_all('div', class_='multi_txt')
            
            for element in memory_elements:
                elem_id = element.get('id', '')
                if 'two_' in elem_id:
                    memory_text = element.get_text().strip()
                    if memory_text:
                        memory_options.append(memory_text)
                        if 'multi_txt_act' in element.get('class', []):
                            current_memory = memory_text
            
            # SIM
            sim_options = []
            current_sim = 'Не указано'
            
            for element in memory_elements:
                elem_id = element.get('id', '')
                if 'three_' in elem_id:
                    sim_text = element.get_text().strip()
                    if sim_text:
                        sim_options.append(sim_text)
                        if 'multi_txt_act' in element.get('class', []):
                            current_sim = sim_text
            
            # Изображение
            img_elem = card.find('img', class_='card_photo_img')
            image_url = img_elem.get('src', '') if img_elem else ''
            image_alt = img_elem.get('alt', '') if img_elem else ''
            
            if image_url and not image_url.startswith('http'):
                image_url = 'https://edwardpnz.ru' + image_url
            
            # Ссылка на товар
            link_elem = card.find('a', class_='card_btn')
            product_url = link_elem.get('href', '') if link_elem else ''
            if product_url and not product_url.startswith('http'):
                product_url = 'https://edwardpnz.ru' + product_url
            
            product_data = {
                'product_id': product_id,
                'model': model_name,
                'price': f"{numeric_price:,} руб.".replace(',', ' ') if numeric_price > 0 else 'Не указана',
                'numeric_price': numeric_price,
                'old_price': old_price,
                'current_color': current_color,
                'available_colors': colors,
                'current_memory': current_memory,
                'memory_options': memory_options,
                'current_sim': current_sim,
                'sim_options': sim_options,
                'image_url': image_url,
                'image_alt': image_alt,
                'product_url': product_url,
                'colors_count': len(colors),
                'memory_count': len(memory_options)
            }
            
            print(f"✅ Товар {product_id}: {model_name} - {numeric_price} руб.")
            return product_data
            
        except Exception as e:
            print(f"❌ Ошибка парсинга карточки: {e}")
            return None

class iPhoneDatabase:
    def __init__(self, db_url):
        self.db_url = db_url
    
    def save_catalog(self, catalog_data):
        """Сохранение всего каталога в базу данных"""
        if not catalog_data.get('success', False):
            return False
            
        conn = psycopg2.connect(self.db_url)
        cursor = conn.cursor()
        
        saved_count = 0
        try:
            for product in catalog_data.get('products', []):
                cursor.execute('''
                    INSERT INTO iphones_catalog 
                    (product_id, model, price, currency, old_price, current_color, 
                     current_memory, current_sim, image_url, product_url, parsed_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (product_id) DO UPDATE SET
                        model = EXCLUDED.model,
                        price = EXCLUDED.price,
                        currency = EXCLUDED.currency,
                        old_price = EXCLUDED.old_price,
                        current_color = EXCLUDED.current_color,
                        current_memory = EXCLUDED.current_memory,
                        current_sim = EXCLUDED.current_sim,
                        image_url = EXCLUDED.image_url,
                        product_url = EXCLUDED.product_url,
                        parsed_at = EXCLUDED.parsed_at
                ''', (
                    product.get('product_id'),
                    product.get('model'),
                    product.get('numeric_price'),
                    'RUB',
                    product.get('old_price'),
                    product.get('current_color'),
                    product.get('current_memory'),
                    product.get('current_sim'),
                    product.get('image_url'),
                    product.get('product_url'),
                    catalog_data.get('parsed_at')
                ))
                
                product_id = product.get('product_id')
                
                # Сохраняем цвета
                cursor.execute('DELETE FROM iphone_catalog_colors WHERE product_id = %s', (product_id,))
                for color in product.get('available_colors', []):
                    cursor.execute('INSERT INTO iphone_catalog_colors (product_id, color_name) VALUES (%s, %s)', (product_id, color))
                
                # Сохраняем память
                cursor.execute('DELETE FROM iphone_catalog_memory WHERE product_id = %s', (product_id,))
                for memory in product.get('memory_options', []):
                    cursor.execute('INSERT INTO iphone_catalog_memory (product_id, memory_size) VALUES (%s, %s)', (product_id, memory))
                
                saved_count += 1
            
            conn.commit()
            print(f"💾 Сохранено товаров: {saved_count}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка сохранения каталога: {e}")
            return False
        finally:
            conn.close()

def main_catalog():
    """Основная функция для парсинга каталога"""
    parser = IPhoneCatalogParser()
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise Exception("DATABASE_URL environment variable not set")
    db = iPhoneDatabase(db_url)
    
    # Читаем HTML из файла
    try:
        with open('site-html.txt', 'r', encoding='utf-8') as f:
            catalog_html = f.read()
        print(f"📁 HTML загружен из файла, размер: {len(catalog_html)} символов")
    except FileNotFoundError:
        print("❌ Файл site-html.txt не найден")
        return
    
    print("=== ПАРСИНГ КАТАЛОГА IPHONE ===")
    
    result = parser.parse_catalog_html(catalog_html)
    
    if result.get('success'):
        print(f"\n✅ УСПЕШНЫЙ РЕЗУЛЬТАТ ПАРСИНГА КАТАЛОГА:")
        print(f"📊 Всего товаров: {result['total_products']}")
        
        # Покажем первые 5 товаров для проверки
        for i, product in enumerate(result['products'][:5]):
            print(f"\n--- Товар {i+1} ---")
            print(f"📱 Модель: {product['model']}")
            print(f"💰 Цена: {product['price']}")
            print(f"🎨 Цвет: {product['current_color']}")
            print(f"💾 Память: {product['current_memory']}")
            print(f"🆔 ID: {product['product_id']}")
        
        # Сохраняем в базу
        if db.save_catalog(result):
            print(f"\n💾 Весь каталог сохранен в базу данных")
        else:
            print("❌ Ошибка сохранения каталога в базу")
    else:
        print("❌ Ошибка парсинга каталога")

if __name__ == "__main__":
    # Запускаем парсинг каталога
    main_catalog()
