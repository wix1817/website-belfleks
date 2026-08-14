import requests
import json

PB_URL = "http://127.0.0.1:8090"
ADMIN_EMAIL = "admin@bflex.by"
ADMIN_PASS = "AdminPassword123!"

def login():
    res = requests.post(f"{PB_URL}/api/collections/_superusers/auth-with-password", json={
        "identity": ADMIN_EMAIL,
        "password": ADMIN_PASS
    })
    return res.json()["token"]

def main():
    token = login()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Create Home Page
    requests.post(f"{PB_URL}/api/collections/pages/records", headers=headers, json={
        "title": "ООО БелФлекс",
        "slug": "home",
        "content": "<p>ООО «БелФлекс» — официальный дилер промышленных рукавов, соединительной арматуры и хомутов на территории Республики Беларусь. Мы предлагаем продукцию ведущих европейских производителей.</p>",
        "hero_title": "Промышленные рукава и соединения",
        "hero_subtitle": "Официальный дилер в Беларуси. Надежность и качество для вашего производства.",
        "meta_title": "Купить промышленные рукава в Гродно | ООО БелФлекс",
        "meta_description": "Промышленные рукава, шланги, соединения Kamlock, хомуты. Официальный дилер в Беларуси. Склад в Гродно.",
        "is_active": True
    })

    # Create About Page
    requests.post(f"{PB_URL}/api/collections/pages/records", headers=headers, json={
        "title": "О компании БелФлекс",
        "slug": "o-kompanii",
        "content": "<h2>Кто мы такие</h2><p>Компания БелФлекс работает на рынке Республики Беларусь много лет. Основным направлением деятельности является поставка промышленных рукавов для любых сред: воды, пара, пищевых продуктов, абразивов, химии и нефтепродуктов.</p><h2>Наши преимущества</h2><ul><li>Собственный склад в Гродно</li><li>Только оригинальная сертифицированная продукция</li><li>Профессиональные консультации инженеров</li><li>Официальная гарантия</li></ul>",
        "meta_title": "О компании БелФлекс",
        "meta_description": "Узнайте больше о компании БелФлекс - вашем надежном партнере в поставках промышленных рукавов и соединений в Беларуси.",
        "is_active": True
    })

    # Create Contacts Page
    requests.post(f"{PB_URL}/api/collections/pages/records", headers=headers, json={
        "title": "Контакты",
        "slug": "kontakty",
        "content": "<p>Свяжитесь с нами любым удобным для вас способом. Мы всегда готовы ответить на ваши вопросы и помочь подобрать необходимые комплектующие.</p>",
        "meta_title": "Контакты | ООО БелФлекс",
        "meta_description": "Свяжитесь с нами. Телефоны, адрес, email и схема проезда к складу ООО БелФлекс в Гродно.",
        "is_active": True
    })

    # Create Site Settings
    requests.post(f"{PB_URL}/api/collections/site_settings/records", headers=headers, json={
        "site_name": "ООО БелФлекс",
        "site_description": "Официальный дилер промышленных рукавов",
        "phone_main": "+375 (33) 123-45-67",
        "phone_secondary": "+375 (152) 12-34-56",
        "email": "info@bflex.by",
        "address": "г. Гродно, ул. Промышленная, 1",
        "working_hours": "Пн-Пт: 9:00 - 17:00, Сб-Вс: выходной",
        "telegram_link": "https://t.me/belfleks",
        "viber_link": "viber://chat?number=375331234567",
        "analytics_code": "<!-- Analytics Code Here -->",
        "footer_text": "<p>&copy; 2026 ООО «БелФлекс». Все права защищены.</p>"
    })
    print("Seeded test data for pages and settings.")

if __name__ == '__main__':
    main()
