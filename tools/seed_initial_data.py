#!/usr/bin/env python3
"""
БелФлекс — seed-скрипт для инициализации данных в PocketBase.
Запуск: python tools/seed_initial_data.py

Что делает:
1. Создаёт/обновляет site_settings (контакты, реквизиты)
2. Создаёт/обновляет страницы: home, o-kompanii, kontakty
3. Проверяет наличие данных в chemical_resistance, при необходимости загружает из chem.csv
"""

import requests
import json
import sys
import os
from pathlib import Path

PB_URL = os.environ.get('PB_URL', 'http://127.0.0.1:8090')
PB_ADMIN_EMAIL = os.environ.get('PB_ADMIN_EMAIL', 'admin@belfleks.by')
PB_ADMIN_PASSWORD = os.environ.get('PB_ADMIN_PASSWORD', 'password')

def pb_auth():
    """Получить токен администратора"""
    resp = requests.post(f'{PB_URL}/api/collections/_superusers/auth-with-password', json={
        'identity': PB_ADMIN_EMAIL,
        'password': PB_ADMIN_PASSWORD,
    })
    if resp.status_code != 200:
        print(f'❌ Auth failed: {resp.status_code} — {resp.text}')
        print('Убедитесь что PocketBase запущен и учётные данные верны.')
        print(f'PB_URL: {PB_URL}')
        sys.exit(1)
    token = resp.json().get('token')
    print(f'✅ Authenticated as {PB_ADMIN_EMAIL}')
    return token

def get_or_create(token, collection, filter_field, filter_value, data):
    """Создать запись или обновить существующую."""
    headers = {'Authorization': token}
    # Try to find existing
    resp = requests.get(
        f'{PB_URL}/api/collections/{collection}/records',
        params={'filter': f'{filter_field}="{filter_value}"', 'perPage': 1},
        headers=headers
    )
    if resp.status_code == 200:
        items = resp.json().get('items', [])
        if items:
            record_id = items[0]['id']
            # Update
            r = requests.patch(
                f'{PB_URL}/api/collections/{collection}/records/{record_id}',
                json=data, headers=headers
            )
            if r.status_code in (200, 201):
                print(f'  ✅ Updated {collection}/{filter_value}')
            else:
                print(f'  ⚠️  Update failed: {r.status_code} {r.text[:200]}')
            return r.json()
    # Create
    r = requests.post(
        f'{PB_URL}/api/collections/{collection}/records',
        json=data, headers=headers
    )
    if r.status_code in (200, 201):
        print(f'  ✅ Created {collection}/{filter_value}')
    else:
        print(f'  ❌ Create failed: {r.status_code} {r.text[:200]}')
    return r.json()

def count_records(token, collection):
    headers = {'Authorization': token}
    resp = requests.get(
        f'{PB_URL}/api/collections/{collection}/records',
        params={'perPage': 1},
        headers=headers
    )
    if resp.status_code == 200:
        return resp.json().get('totalItems', 0)
    return -1

def seed_site_settings(token):
    print('\n📋 Seeding site_settings...')
    data = {
        'site_name': 'ООО БелФлекс',
        'site_description': 'Официальный дилер промышленных рукавов, соединений и хомутов в Беларуси. Склад в Гродно.',
        'phone_main': '+375 (44) 780-00-59',
        'phone_secondary': '+375 (17) 300-00-00',
        'email': 'zakaz@belfleks.by',
        'address': 'г. Гродно, ул. Лидская 15',
        'working_hours': 'Пн–Пт: 8:30 – 17:00\nСб–Вс: выходной',
        'telegram_link': '',   # Заполните при необходимости: https://t.me/yourbot
        'viber_link': '',      # Заполните при необходимости: viber://chat?number=+375447800059
    }
    # site_settings usually has only one record — get first or create
    headers = {'Authorization': token}
    resp = requests.get(f'{PB_URL}/api/collections/site_settings/records', headers=headers)
    if resp.status_code == 200:
        items = resp.json().get('items', [])
        if items:
            record_id = items[0]['id']
            r = requests.patch(
                f'{PB_URL}/api/collections/site_settings/records/{record_id}',
                json=data, headers=headers
            )
            if r.status_code in (200, 201):
                print('  ✅ Updated site_settings')
            else:
                print(f'  ⚠️  {r.status_code}: {r.text[:200]}')
        else:
            r = requests.post(f'{PB_URL}/api/collections/site_settings/records', json=data, headers=headers)
            if r.status_code in (200, 201):
                print('  ✅ Created site_settings')
            else:
                print(f'  ❌ {r.status_code}: {r.text[:200]}')

def seed_pages(token):
    print('\n📄 Seeding pages...')

    pages = [
        {
            'slug': 'home',
            'title': 'Главная',
            'meta_title': 'Промышленные рукава и соединения в Беларуси | ООО БелФлекс',
            'meta_description': 'Поставляем промышленные рукава, шланги, соединения Kamlock, хомуты и фитинги. Официальный дилер. Склад в Гродно. Доставка по РБ и СНГ.',
            'content': '',
            'is_active': True,
        },
        {
            'slug': 'o-kompanii',
            'title': 'О компании',
            'meta_title': 'О компании ООО БелФлекс | Промышленные рукава в Гродно',
            'meta_description': 'ООО «БелФлекс» — официальный дилер промышленных рукавов ведущих европейских производителей в Республике Беларусь. Более 10 лет на рынке.',
            'content': '''<p>ООО «БелФлекс» — официальный дилер промышленных рукавов и соединительной арматуры ведущих европейских производителей в Республике Беларусь. Более 10 лет мы обеспечиваем предприятия Беларуси и СНГ надёжными компонентами для технологических процессов.</p>

<p>Собственный склад в Гродно позволяет осуществлять поставки точно в срок. Наши специалисты помогут подобрать рукав под конкретную рабочую среду, давление и температурный диапазон.</p>

<h2>Наши преимущества</h2>
<ul>
<li>Официальный дилер — все сертификаты и документация</li>
<li>Широкий ассортимент: более 500 позиций в каталоге</li>
<li>Бесплатная доставка при наличии на складе в течение 1 дня</li>
<li>Техническая консультация инженеров</li>
<li>Работаем с юридическими лицами по договору</li>
</ul>''',
            'is_active': True,
        },
        {
            'slug': 'kontakty',
            'title': 'Контакты',
            'meta_title': 'Контакты ООО БелФлекс | Телефоны, адрес, схема проезда',
            'meta_description': 'Свяжитесь с нами. Телефоны, адрес склада и офиса ООО БелФлекс в Гродно, email, режим работы и схема проезда.',
            'content': '<p>Мы всегда рады помочь вам. Свяжитесь с нами любым удобным способом.</p>',
            'is_active': True,
        },
    ]

    for page in pages:
        get_or_create(token, 'pages', 'slug', page['slug'], page)

def check_chemical_data(token):
    print('\n🧪 Checking chemical_resistance data...')
    count = count_records(token, 'chemical_resistance')
    if count < 0:
        print('  ⚠️  Cannot access chemical_resistance collection (may not exist)')
        return
    print(f'  ℹ️  Records found: {count}')
    if count == 0:
        print('  ⚠️  Chemical resistance table is EMPTY!')
        # Look for CSV file
        csv_path = Path(__file__).parent.parent / 'data' / 'chem.csv'
        if not csv_path.exists():
            csv_path = Path(__file__).parent / 'chem.csv'
        if csv_path.exists():
            print(f'  📂 Found CSV at {csv_path}')
            print('  💡 Run the import script to load data:')
            print(f'     python tools/import_chem_csv.py {csv_path}')
        else:
            print('  ❌ No chem.csv found. Please load chemical resistance data manually.')
            print('     Expected location: data/chem.csv')
    else:
        print(f'  ✅ Chemical resistance data present ({count} records)')

def main():
    print('[SEED] BelFlex PocketBase Seed Script')
    print('=' * 50)
    print(f'PocketBase URL: {PB_URL}')

    token = pb_auth()

    seed_site_settings(token)
    seed_pages(token)
    check_chemical_data(token)

    print('\n' + '=' * 50)
    print('✅ Seed complete!')
    print('\nПосле заполнения данных выполните:')
    print('  cd astro && npm run build')
    print('\nНастройте следующие поля в site_settings через PocketBase Admin:')
    print('  - telegram_link: ваша ссылка на Telegram')
    print('  - viber_link: ваша ссылка на Viber')
    print('  - favicon: загрузите логотип')

if __name__ == '__main__':
    main()
