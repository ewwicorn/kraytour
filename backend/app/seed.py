"""
Seed: теги + локации + пользователи + посты
Запуск: python -m app.seed  (из папки backend/)

Идемпотентный — повторный запуск не создаёт дубликаты.
"""
import asyncio
import uuid

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.location import Tag, Location
from app.models.user import User
from app.models.post import Post

# ─── Теги ────────────────────────────────────────────────────────────────────

TAGS = [
    # Сезонность
    {"slug": "season-spring",  "label_ru": "весна",        "group": "season"},
    {"slug": "season-summer",  "label_ru": "лето",          "group": "season"},
    {"slug": "season-autumn",  "label_ru": "осень",         "group": "season"},
    {"slug": "season-winter",  "label_ru": "зима",          "group": "season"},
    {"slug": "season-all",     "label_ru": "круглый год",   "group": "season"},
    # Активность
    {"slug": "activity-wine",      "label_ru": "винный туризм",     "group": "activity"},
    {"slug": "activity-gastro",    "label_ru": "гастрономия",       "group": "activity"},
    {"slug": "activity-eco",       "label_ru": "эко-туризм",        "group": "activity"},
    {"slug": "activity-agro",      "label_ru": "агро-туризм",       "group": "activity"},
    {"slug": "activity-trekking",  "label_ru": "трекинг",           "group": "activity"},
    {"slug": "activity-culture",   "label_ru": "культурный",        "group": "activity"},
    {"slug": "activity-wellness",  "label_ru": "оздоровительный",   "group": "activity"},
    # Аудитория
    {"slug": "audience-family",  "label_ru": "семья с детьми",     "group": "audience"},
    {"slug": "audience-senior",  "label_ru": "пенсионный возраст", "group": "audience"},
    {"slug": "audience-remote",  "label_ru": "удалёнщик",          "group": "audience"},
    {"slug": "audience-solo",    "label_ru": "соло",               "group": "audience"},
    {"slug": "audience-couple",  "label_ru": "пара",               "group": "audience"},
]

# ─── Локации ──────────────────────────────────────────────────────────────────

LOCATIONS = [
    {
        "slug": "vedernikov-winery",
        "name": "Винодельня Ведерников",
        "short_description": "Старейшая казачья винодельня на берегу Дона с дегустациями автохтонных сортов.",
        "lat": 47.6231, "lng": 40.8317,
        "address": "Ростовская область, ст. Раздорская",
        "photos": ["https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?w=800"],
        "price_from": 1500,
        "tag_slugs": ["activity-wine", "activity-gastro", "season-autumn", "season-summer", "audience-couple"],
    },
    {
        "slug": "abrau-durso",
        "name": "Абрау-Дюрсо",
        "short_description": "Знаменитое шампанское озеро и винный завод с экскурсиями в тоннели.",
        "lat": 44.6870, "lng": 37.5612,
        "address": "Краснодарский край, с. Абрау-Дюрсо",
        "photos": ["https://images.unsplash.com/photo-1470158499416-75be9aa0c4db?w=800"],
        "price_from": 800,
        "tag_slugs": ["activity-wine", "season-all", "audience-couple", "audience-family"],
    },
    {
        "slug": "guzeripl-reserve",
        "name": "Кордон Гузерипль",
        "short_description": "Вход в Кавказский биосферный заповедник — зубры, горные тропы, тишина.",
        "lat": 43.9928, "lng": 40.1872,
        "address": "Краснодарский край, пос. Гузерипль",
        "photos": ["https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800"],
        "price_from": 300,
        "tag_slugs": ["activity-eco", "activity-trekking", "season-spring", "season-summer", "season-autumn", "audience-solo"],
    },
    {
        "slug": "farm-kuban-berries",
        "name": "Ферма «Кубанская ягода»",
        "short_description": "Агротуризм: сбор клубники, мастер-классы по варенью, ночёвка в домиках.",
        "lat": 45.1234, "lng": 38.9876,
        "address": "Краснодарский край, Динской район",
        "photos": ["https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=800"],
        "price_from": 2000,
        "tag_slugs": ["activity-agro", "activity-gastro", "season-summer", "audience-family", "audience-couple"],
    },
    {
        "slug": "stanitsa-taman",
        "name": "Станица Тамань",
        "short_description": "Казачья станица, музей Лермонтова, виноградники у Керченского пролива.",
        "lat": 45.2107, "lng": 36.7144,
        "address": "Краснодарский край, ст. Тамань",
        "photos": ["https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=800"],
        "price_from": 500,
        "tag_slugs": ["activity-culture", "activity-wine", "season-spring", "season-autumn", "audience-senior", "audience-couple"],
    },
]

# ─── Пользователи ─────────────────────────────────────────────────────────────

USERS = [
    {
        "email": "admin@kraytour.ru",
        "password": "Admin1234",
        "first_name": "Админ",
        "last_name": "Краевед",
        "role": "admin",
    },
    {
        "email": "seller@kraytour.ru",
        "password": "Seller1234",
        "first_name": "Иван",
        "last_name": "Виноградов",
        "role": "seller",
    },
    {
        "email": "buyer1@kraytour.ru",
        "password": "Buyer1234",
        "first_name": "Алексей",
        "last_name": "Петров",
        "role": "buyer",
    },
    {
        "email": "buyer2@kraytour.ru",
        "password": "Buyer1234",
        "first_name": "Мария",
        "last_name": "Иванова",
        "role": "buyer",
    },
]

# ─── Посты ────────────────────────────────────────────────────────────────────
# author_email и location_slug — для связи при создании

POSTS = [
    {
        "title": "Лучшая дегустация в моей жизни",
        "content": "Провели на винодельне Ведерников почти весь день. Хозяин лично провёл экскурсию по погребам, рассказал про автохтонные сорта — Цимлянский чёрный, Красностоп. Вина совершенно другие, не похожие на массовые. Взяли с собой несколько бутылок.",
        "photos": ["https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?w=800"],
        "tags": ["вино", "дегустация", "казаки"],
        "author_email": "buyer1@kraytour.ru",
        "location_slug": "vedernikov-winery",
        "lat": 47.6231, "lng": 40.8317,
        "likes_count": 24,
    },
    {
        "title": "Осенний Дон — это что-то особенное",
        "content": "Приехали в октябре — виноград уже собран, но атмосфера потрясающая. Туман над рекой утром, тишина, запах выжимок. Рекомендую именно осенний визит.",
        "photos": ["https://images.unsplash.com/photo-1474722883778-792e7990302f?w=800"],
        "tags": ["осень", "вино", "природа", "Дон"],
        "author_email": "buyer2@kraytour.ru",
        "location_slug": "vedernikov-winery",
        "lat": 47.6231, "lng": 40.8317,
        "likes_count": 17,
    },
    {
        "title": "Абрау — не только вино",
        "content": "Все знают Абрау-Дюрсо как винный завод, но мало кто говорит про озеро. Можно взять лодку и покататься — вид на горы отражается в воде. Закат здесь просто нереальный.",
        "photos": ["https://images.unsplash.com/photo-1470158499416-75be9aa0c4db?w=800"],
        "tags": ["озеро", "вино", "закат", "Краснодар"],
        "author_email": "buyer1@kraytour.ru",
        "location_slug": "abrau-durso",
        "lat": 44.6870, "lng": 37.5612,
        "likes_count": 41,
    },
    {
        "title": "Экскурсия в тоннели завода",
        "content": "Тоннели уходят глубоко в гору — там постоянные 12 градусов. Ряды бутылок уходят в темноту. Экскурсовод рассказывает про метод шампанизации. В конце дегустация прямо в тоннеле.",
        "photos": ["https://images.unsplash.com/photo-1513618827672-0d7c5ad591b1?w=800"],
        "tags": ["вино", "шампанское", "экскурсия", "тоннели"],
        "author_email": "seller@kraytour.ru",
        "location_slug": "abrau-durso",
        "lat": 44.6870, "lng": 37.5612,
        "likes_count": 33,
    },
    {
        "title": "Зубры в дикой природе",
        "content": "Добрались до кордона Гузерипль ранним утром. На тропе встретили зубра метрах в тридцати — он просто смотрел на нас и жевал траву. Такого нигде больше не увидишь.",
        "photos": ["https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800"],
        "tags": ["природа", "зубры", "заповедник", "горы"],
        "author_email": "buyer2@kraytour.ru",
        "location_slug": "guzeripl-reserve",
        "lat": 43.9928, "lng": 40.1872,
        "likes_count": 58,
    },
    {
        "title": "Однодневный поход — маршрут и советы",
        "content": "Начали от кордона в 8 утра, прошли около 14 км, вернулись к 17:00. Обязательно берите пропуск заранее — без него не пустят. Из еды достаточно перекуса, воду можно набирать из горных ручьёв. Трекинговые палки очень помогут на спуске.",
        "photos": ["https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"],
        "tags": ["трекинг", "маршрут", "советы", "Кавказ"],
        "author_email": "buyer1@kraytour.ru",
        "location_slug": "guzeripl-reserve",
        "lat": 43.9928, "lng": 40.1872,
        "likes_count": 45,
    },
    {
        "title": "Весенний поход — всё в цвету",
        "content": "Май — лучшее время. Рододендроны цветут прямо на тропе, снег ещё лежит на вершинах, а внизу уже тепло. Воздух такой, что хочется дышать и дышать.",
        "photos": ["https://images.unsplash.com/photo-1519681393784-d120267933ba?w=800"],
        "tags": ["весна", "цветы", "горы", "природа"],
        "author_email": "buyer2@kraytour.ru",
        "location_slug": "guzeripl-reserve",
        "lat": 43.9928, "lng": 40.1872,
        "likes_count": 29,
    },
    {
        "title": "Клубника прямо с грядки",
        "content": "Приехали с детьми в июне. Каждый собирал сам — дети были в восторге. Потом мастер-класс по варенью: варили в медном тазу на открытом огне. Ночевали в домике — чисто, уютно, пели птицы.",
        "photos": ["https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=800"],
        "tags": ["агро", "клубника", "дети", "семья"],
        "author_email": "buyer2@kraytour.ru",
        "location_slug": "farm-kuban-berries",
        "lat": 45.1234, "lng": 38.9876,
        "likes_count": 36,
    },
    {
        "title": "Настоящая кубанская кухня",
        "content": "Хозяйка накормила борщом, варениками и домашней колбасой. Всё из своего хозяйства. После обеда показала огород — помидоры, перец, баклажаны. Такого борща я не ел нигде.",
        "photos": ["https://images.unsplash.com/photo-1547592180-85f173990554?w=800"],
        "tags": ["гастро", "кубанская кухня", "фермерское", "борщ"],
        "author_email": "buyer1@kraytour.ru",
        "location_slug": "farm-kuban-berries",
        "lat": 45.1234, "lng": 38.9876,
        "likes_count": 22,
    },
    {
        "title": "Тамань — место силы",
        "content": "Лермонтов описывал Тамань как «самый скверный городишко». Теперь здесь тихая казачья станица и прекрасный музей. Виноградники уходят прямо к проливу — вид фантастический.",
        "photos": ["https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=800"],
        "tags": ["культура", "Лермонтов", "казаки", "история"],
        "author_email": "buyer1@kraytour.ru",
        "location_slug": "stanitsa-taman",
        "lat": 45.2107, "lng": 36.7144,
        "likes_count": 19,
    },
    {
        "title": "Вина Тамани недооценены",
        "content": "Местные хозяйства делают отличное вино — совсем не то, что в магазине под тем же названием. Купили несколько бутылок прямо у фермера. Рислинг и Мускат особенно понравились.",
        "photos": ["https://images.unsplash.com/photo-1516594915697-87eb3b1c14ea?w=800"],
        "tags": ["вино", "Тамань", "фермерское", "дегустация"],
        "author_email": "buyer2@kraytour.ru",
        "location_slug": "stanitsa-taman",
        "lat": 45.2107, "lng": 36.7144,
        "likes_count": 27,
    },
    {
        "title": "Закат над Керченским проливом",
        "content": "Поднялись на холм над станицей перед закатом. Видно Керченский пролив, вдали — Крым. Оранжевое небо, виноградники внизу. Один из лучших видов в моей жизни.",
        "photos": ["https://images.unsplash.com/photo-1495616811223-4d98c6e9c869?w=800"],
        "tags": ["закат", "пролив", "вид", "Тамань"],
        "author_email": "seller@kraytour.ru",
        "location_slug": "stanitsa-taman",
        "lat": 45.2107, "lng": 36.7144,
        "likes_count": 51,
    },
    # Посты без привязки к локации — просто впечатления
    {
        "title": "Краснодарский край — открытие года",
        "content": "Объездили за две недели пять мест. Нигде не разочаровались. Цены разумные, люди приветливые, природа разнообразная — горы, степи, море рядом. Обязательно вернёмся.",
        "photos": ["https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800"],
        "tags": ["Краснодар", "путешествие", "открытие"],
        "author_email": "buyer1@kraytour.ru",
        "location_slug": None,
        "lat": 45.04, "lng": 38.98,
        "likes_count": 63,
    },
    {
        "title": "Что взять с собой в горы Адыгеи",
        "content": "Список снаряжения после трёх походов: трекинговые палки обязательны, термос важнее чем кажется, дождевик нужен даже в июле — погода меняется быстро. Берите наличные — карты не везде принимают.",
        "photos": ["https://images.unsplash.com/photo-1551632811-561732d1e306?w=800"],
        "tags": ["советы", "горы", "снаряжение", "Адыгея"],
        "author_email": "buyer2@kraytour.ru",
        "location_slug": None,
        "lat": 44.0, "lng": 40.0,
        "likes_count": 38,
    },
    {
        "title": "Лучшее время для поездки в Краснодарский край",
        "content": "Май–июнь и сентябрь–октябрь — золотые месяцы. Летом слишком жарко в степи и много людей на побережье. Весной и осенью тепло, всё зелёное, туристов меньше, цены ниже.",
        "photos": ["https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=800"],
        "tags": ["советы", "сезон", "планирование"],
        "author_email": "seller@kraytour.ru",
        "location_slug": None,
        "lat": 45.04, "lng": 38.98,
        "likes_count": 44,
    },
]


# ─── Функция seed ─────────────────────────────────────────────────────────────

async def seed():
    async with AsyncSessionLocal() as db:

        # ── Теги: пропустить если уже есть ──────────────────────────────────
        existing_tags = (await db.execute(select(Tag))).scalars().all()
        tag_map: dict[str, Tag] = {t.slug: t for t in existing_tags}

        new_tags = 0
        for t in TAGS:
            if t["slug"] not in tag_map:
                tag = Tag(id=uuid.uuid4(), **t)
                db.add(tag)
                tag_map[t["slug"]] = tag
                new_tags += 1

        await db.flush()

        # ── Локации: пропустить если уже есть ───────────────────────────────
        existing_slugs = {
            row[0] for row in (await db.execute(select(Location.slug))).all()
        }

        loc_map: dict[str, Location] = {}
        new_locs = 0
        for loc_data in LOCATIONS:
            tag_slugs = loc_data.pop("tag_slugs")
            if loc_data["slug"] not in existing_slugs:
                location = Location(id=uuid.uuid4(), is_active=True, **loc_data)
                location.tags = [tag_map[s] for s in tag_slugs]
                db.add(location)
                new_locs += 1
            # загрузить в map независимо от того, новая или старая
            loc_data["tag_slugs"] = tag_slugs  # вернём обратно чтобы не ломать данные

        await db.flush()

        # перезагружаем все локации чтобы получить их id
        all_locs = (await db.execute(select(Location))).scalars().all()
        loc_map = {loc.slug: loc for loc in all_locs}

        # ── Пользователи: пропустить если уже есть ──────────────────────────
        existing_emails = {
            row[0] for row in (await db.execute(select(User.email))).all()
        }

        user_map: dict[str, User] = {}
        new_users = 0
        for u in USERS:
            if u["email"] not in existing_emails:
                user = User(
                    id=uuid.uuid4(),
                    email=u["email"],
                    password_hash=hash_password(u["password"]),
                    first_name=u["first_name"],
                    last_name=u["last_name"],
                    role=u["role"],
                )
                db.add(user)
                new_users += 1

        await db.flush()

        # перезагружаем всех пользователей
        all_users = (await db.execute(select(User))).scalars().all()
        user_map = {u.email: u for u in all_users}

        # ── Посты: пропустить если уже есть (по title + author) ─────────────
        existing_titles = {
            row[0] for row in (await db.execute(select(Post.title))).all()
        }

        new_posts = 0
        for p in POSTS:
            if p["title"] in existing_titles:
                continue

            author = user_map.get(p["author_email"])
            location = loc_map.get(p["location_slug"]) if p["location_slug"] else None

            post = Post(
                id=uuid.uuid4(),
                title=p["title"],
                content=p["content"],
                photos=p["photos"],
                tags=p["tags"],
                author_id=author.id if author else None,
                location_id=location.id if location else None,
                lat=p.get("lat"),
                lng=p.get("lng"),
                likes_count=p.get("likes_count", 0),
                is_moderated=True,
            )
            db.add(post)
            new_posts += 1

        await db.commit()

        print(f"✓ Tags:     {new_tags} new (total {len(tag_map)})")
        print(f"✓ Locations: {new_locs} new (total {len(loc_map)})")
        print(f"✓ Users:    {new_users} new (total {len(user_map)})")
        print(f"✓ Posts:    {new_posts} new")
        print()
        print("Demo credentials:")
        for u in USERS:
            print(f"  {u['role']:8} {u['email']}  /  {u['password']}")


if __name__ == "__main__":
    asyncio.run(seed())