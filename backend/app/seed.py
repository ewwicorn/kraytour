"""
Seed: теги + 5 тестовых локаций Краснодарского края
Запуск: python -m app.seed  (из папки backend/)
"""
import asyncio
import uuid

from app.db.session import AsyncSessionLocal
from app.models.location import Tag, Location

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
    {"slug": "audience-family",    "label_ru": "семья с детьми",    "group": "audience"},
    {"slug": "audience-senior",    "label_ru": "пенсионный возраст","group": "audience"},
    {"slug": "audience-remote",    "label_ru": "удалёнщик",         "group": "audience"},
    {"slug": "audience-solo",      "label_ru": "соло",              "group": "audience"},
    {"slug": "audience-couple",    "label_ru": "пара",              "group": "audience"},
]

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


async def seed():
    async with AsyncSessionLocal() as db:
        tag_map: dict[str, Tag] = {}
        for t in TAGS:
            tag = Tag(id=uuid.uuid4(), **t)
            db.add(tag)
            tag_map[t["slug"]] = tag

        await db.flush()

        for loc_data in LOCATIONS:
            tag_slugs = loc_data.pop("tag_slugs")
            location = Location(
                id=uuid.uuid4(),
                is_active=True,
                **loc_data,
            )
            location.tags = [tag_map[s] for s in tag_slugs]
            db.add(location)

        await db.commit()
        print(f"✓ Seeded {len(TAGS)} tags and {len(LOCATIONS)} locations")


if __name__ == "__main__":
    asyncio.run(seed())
