from dotenv import load_dotenv
import mysql.connector
import os
import random

# Загружаем настройки базы данных
load_dotenv()

# Функция для подключения к БД
def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "game_db"),
    )

def main():
    connection = get_db()
    cursor = connection.cursor()

    # Список команд для очистки таблиц перед заполнением
    statements = [
        "SET FOREIGN_KEY_CHECKS = 0",
        "TRUNCATE TABLE reviews",
        "TRUNCATE TABLE review_audit_log",
        "TRUNCATE TABLE game_genres",
        "TRUNCATE TABLE game_platforms",
        "TRUNCATE TABLE games",
        "TRUNCATE TABLE users",
        "TRUNCATE TABLE genres",
        "TRUNCATE TABLE platforms",
        "TRUNCATE TABLE developers",
        "TRUNCATE TABLE publishers",
        "SET FOREIGN_KEY_CHECKS = 1",
        
        # Добавляем разработчиков
        """
        INSERT INTO developers (name, country) VALUES
        ('CD Projekt Red', 'Poland'),
        ('Rockstar Games', 'USA'),
        ('Valve', 'USA'),
        ('FromSoftware', 'Japan'),
        ('Naughty Dog', 'USA'),
        ('Bethesda Game Studios', 'USA'),
        ('Larian Studios', 'Belgium'),
        ('Nintendo EPD', 'Japan'),
        ('Santa Monica Studio', 'USA'),
        ('Guerrilla Games', 'Netherlands'),
        ('Bungie', 'USA'),
        ('Epic Games', 'USA'),
        ('Blizzard Entertainment', 'USA'),
        ('Kojima Productions', 'Japan')
        """,
        
        # Добавляем издателей
        """
        INSERT INTO publishers (name, country) VALUES
        ('Bandai Namco', 'Japan'),
        ('Take-Two Interactive', 'USA'),
        ('Valve Corporation', 'USA'),
        ('Sony Interactive', 'USA'),
        ('Bethesda Softworks', 'USA'),
        ('Nintendo', 'Japan'),
        ('Larian Studios', 'Belgium'),
        ('Electronic Arts', 'USA'),
        ('Activision', 'USA'),
        ('Xbox Game Studios', 'USA'),
        ('505 Games', 'Italy')
        """,
        
        # Основные игровые жанры
        """
        INSERT INTO genres (name) VALUES
        ('Action'),
        ('Adventure'),
        ('Open World'),
        ('RPG'),
        ('Shooter'),
        ('Souls-like'),
        ('Strategy'),
        ('Platformer'),
        ('Simulation'),
        ('Sports'),
        ('Horror')
        """,
        
        # Игровые платформы
        """
        INSERT INTO platforms (name, abbreviation) VALUES
        ('PC', 'PC'),
        ('PlayStation 5', 'PS5'),
        ('Xbox Series X', 'XSX'),
        ('Nintendo Switch', 'NSW'),
        ('PlayStation 4', 'PS4'),
        ('Xbox One', 'XONE')
        """,
        
        # Тестовые пользователи (пароль везде 'password123' в зашифрованном виде)
        """
        INSERT INTO users (username, email, password_hash, is_admin, created_at) VALUES
        ('admin', 'admin@example.com', 'scrypt:32768:8:1$fUv1jA6rTHe6zMeI$86e4f9fe1398277f175c526c0953a15dc23d08ef192da8ad857a03f6ec0478de0a5bccf4507fa54d541e13cb9a78e8a83034a5a69ddd0a66d6a78389a0f94ffc', 1, '2025-01-01 10:00:00'),
        ('denis', 'denis@example.com', 'scrypt:32768:8:1$fUv1jA6rTHe6zMeI$86e4f9fe1398277f175c526c0953a15dc23d08ef192da8ad857a03f6ec0478de0a5bccf4507fa54d541e13cb9a78e8a83034a5a69ddd0a66d6a78389a0f94ffc', 0, '2025-01-02 11:30:00'),
        ('maria', 'maria@example.com', 'scrypt:32768:8:1$fUv1jA6rTHe6zMeI$86e4f9fe1398277f175c526c0953a15dc23d08ef192da8ad857a03f6ec0478de0a5bccf4507fa54d541e13cb9a78e8a83034a5a69ddd0a66d6a78389a0f94ffc', 0, '2025-01-03 14:15:00'),
        ('john', 'john@example.com', 'scrypt:32768:8:1$fUv1jA6rTHe6zMeI$86e4f9fe1398277f175c526c0953a15dc23d08ef192da8ad857a03f6ec0478de0a5bccf4507fa54d541e13cb9a78e8a83034a5a69ddd0a66d6a78389a0f94ffc', 0, '2025-01-04 09:20:00'),
        ('sarah', 'sarah@example.com', 'scrypt:32768:8:1$fUv1jA6rTHe6zMeI$86e4f9fe1398277f175c526c0953a15dc23d08ef192da8ad857a03f6ec0478de0a5bccf4507fa54d541e13cb9a78e8a83034a5a69ddd0a66d6a78389a0f94ffc', 0, '2025-01-05 18:45:00'),
        ('mike', 'mike@example.com', 'scrypt:32768:8:1$fUv1jA6rTHe6zMeI$86e4f9fe1398277f175c526c0953a15dc23d08ef192da8ad857a03f6ec0478de0a5bccf4507fa54d541e13cb9a78e8a83034a5a69ddd0a66d6a78389a0f94ffc', 0, '2025-01-06 20:10:00'),
        ('emma', 'emma@example.com', 'scrypt:32768:8:1$fUv1jA6rTHe6zMeI$86e4f9fe1398277f175c526c0953a15dc23d08ef192da8ad857a03f6ec0478de0a5bccf4507fa54d541e13cb9a78e8a83034a5a69ddd0a66d6a78389a0f94ffc', 0, '2025-01-07 12:05:00'),
        ('lucas', 'lucas@example.com', 'scrypt:32768:8:1$fUv1jA6rTHe6zMeI$86e4f9fe1398277f175c526c0953a15dc23d08ef192da8ad857a03f6ec0478de0a5bccf4507fa54d541e13cb9a78e8a83034a5a69ddd0a66d6a78389a0f94ffc', 0, '2025-01-08 16:30:00'),
        ('olivia', 'olivia@example.com', 'scrypt:32768:8:1$fUv1jA6rTHe6zMeI$86e4f9fe1398277f175c526c0953a15dc23d08ef192da8ad857a03f6ec0478de0a5bccf4507fa54d541e13cb9a78e8a83034a5a69ddd0a66d6a78389a0f94ffc', 0, '2025-01-09 08:50:00'),
        ('noah', 'noah@example.com', 'scrypt:32768:8:1$fUv1jA6rTHe6zMeI$86e4f9fe1398277f175c526c0953a15dc23d08ef192da8ad857a03f6ec0478de0a5bccf4507fa54d541e13cb9a78e8a83034a5a69ddd0a66d6a78389a0f94ffc', 0, '2025-01-10 22:15:00')
        """,
        
        # Набор популярных игр для демонстрации
        """
        INSERT INTO games (title, release_date, description, developer_id, publisher_id, cover_url) VALUES
        ('The Witcher 3', '2015-05-19', 'An open-world action RPG about Geralt of Rivia.', 1, 1, 'https://upload.wikimedia.org/wikipedia/en/0/0c/Witcher_3_cover_art.jpg'),
        ('Grand Theft Auto V', '2013-09-17', 'Open-world action adventure set in Los Santos.', 2, 2, 'https://upload.wikimedia.org/wikipedia/en/a/a5/Grand_Theft_Auto_V.png'),
        ('Elden Ring', '2022-02-25', 'An epic adventure in the Lands Between.', 4, 1, 'https://upload.wikimedia.org/wikipedia/en/b/b9/Elden_Ring_Box_art.jpg'),
        ('The Last of Us Part II', '2020-06-19', 'A dramatic story of survival and revenge.', 5, 4, 'https://upload.wikimedia.org/wikipedia/en/4/4f/TLOU_P2_Box_Art_2.png'),
        ('Baldurs Gate 3', '2023-08-03', 'A story-rich, party-based RPG set in the universe of Dungeons & Dragons.', 7, 7, 'https://upload.wikimedia.org/wikipedia/en/1/12/Baldur%27s_Gate_3_cover_art.jpg'),
        ('The Legend of Zelda: Breath of the Wild', '2017-03-03', 'Step into a world of discovery, exploration, and adventure.', 8, 6, 'https://upload.wikimedia.org/wikipedia/en/c/c6/The_Legend_of_Zelda_Breath_of_the_Wild.jpg'),
        ('God of War Ragnarök', '2022-11-09', 'Kratos and Atreus must journey to each of the Nine Realms.', 9, 4, 'https://upload.wikimedia.org/wikipedia/en/e/ee/God_of_War_Ragnar%C3%B6k_cover.jpg'),
        ('Cyberpunk 2077', '2020-12-10', 'An open-world, action-adventure story set in Night City.', 1, 1, 'https://upload.wikimedia.org/wikipedia/en/9/9f/Cyberpunk_2077_box_art.jpg'),
        ('Half-Life 2', '2004-11-16', 'A pioneering first-person shooter with physics-based puzzles.', 3, 3, 'https://upload.wikimedia.org/wikipedia/en/2/25/Half-Life_2_cover.jpg'),
        ('The Elder Scrolls V: Skyrim', '2011-11-11', 'Epic fantasy RPG with dragons and endless exploration.', 6, 5, 'https://upload.wikimedia.org/wikipedia/en/1/15/The_Elder_Scrolls_V_Skyrim_cover.png'),
        ('Horizon Zero Dawn', '2017-02-28', 'Experience Aloy''s legendary quest to unravel the mysteries of a future Earth.', 10, 4, 'https://upload.wikimedia.org/wikipedia/en/3/3e/Horizon_Zero_Dawn_cover_art.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail_unscaled'),
        ('Bloodborne', '2015-03-24', 'A fast-paced action RPG set in the ancient city of Yharnam.', 4, 4, 'https://upload.wikimedia.org/wikipedia/en/6/68/Bloodborne_Cover_Wallpaper.jpg'),
        ('Red Dead Redemption 2', '2018-10-26', 'An epic tale of life in America’s unforgiving heartland.', 2, 2, 'https://upload.wikimedia.org/wikipedia/en/4/44/Red_Dead_Redemption_II.jpg'),
        ('Portal 2', '2011-04-18', 'The sequel to the award-winning puzzle game.', 3, 3, 'https://upload.wikimedia.org/wikipedia/en/f/f9/Portal2cover.jpg'),
        ('Super Mario Odyssey', '2017-10-27', 'Join Mario on a massive, globe-trotting 3D adventure.', 8, 6, 'https://upload.wikimedia.org/wikipedia/en/8/8d/Super_Mario_Odyssey.jpg'),
        ('Sekiro: Shadows Die Twice', '2019-03-22', 'Carve your own clever path to vengeance.', 4, 11, 'https://upload.wikimedia.org/wikipedia/en/6/6e/Sekiro_art.jpg'),
        ('Ghost of Tsushima', '2020-07-17', 'Uncover the hidden wonders of Tsushima.', 9, 4, 'https://upload.wikimedia.org/wikipedia/en/b/b6/Ghost_of_Tsushima.jpg'),
        ('Death Stranding', '2019-11-08', 'A journey to reconnect a fractured society.', 14, 4, 'https://upload.wikimedia.org/wikipedia/en/2/22/Death_Stranding.jpg'),
        ('Overwatch', '2016-05-24', 'A team-based multiplayer first-person shooter.', 13, 9, 'https://upload.wikimedia.org/wikipedia/en/5/51/Overwatch_cover_art.jpg'),
        ('Destiny 2', '2017-09-06', 'Dive into the world of Destiny to experience cinematic story campaigns.', 11, 9, 'https://upload.wikimedia.org/wikipedia/en/0/05/Destiny_2_%28artwork%29.jpg')
        """
    ]

    # Выполняем все SQL-команды в цикле
    for stmt in statements:
        try:
            cursor.execute(stmt)
        except Exception as e:
            print(f"Ошибка при выполнении: {stmt[:50]}... \nОшибка: {e}")
            connection.rollback()
            return

    # Случайным образом назначаем жанры и платформы играм
    cursor.execute("SELECT id FROM games")
    games = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM genres")
    genres = [row[0] for row in cursor.fetchall()]

    for game_id in games:
        g_genres = random.sample(genres, k=random.randint(1, 3))
        for genre_id in g_genres:
            cursor.execute("INSERT IGNORE INTO game_genres (game_id, genre_id) VALUES (%s, %s)", (game_id, genre_id))

    cursor.execute("SELECT id FROM platforms")
    platforms = [row[0] for row in cursor.fetchall()]

    for game_id in games:
        g_platforms = random.sample(platforms, k=random.randint(1, 4))
        for platform_id in g_platforms:
            cursor.execute("INSERT IGNORE INTO game_platforms (game_id, platform_id) VALUES (%s, %s)", (game_id, platform_id))

    # Генерируем случайные отзывы для каждой игры
    cursor.execute("SELECT id FROM users")
    users = [row[0] for row in cursor.fetchall()]

    review_texts = [
        "Absolutely fantastic experience.",
        "Good, but could be better.",
        "Overrated in my opinion.",
        "Masterpiece! I played it for 100 hours.",
        "The story is amazing, but the gameplay is clunky.",
        "A truly unforgettable journey.",
        "Not my type of game, but I respect it.",
        "Incredible graphics and sound design.",
        "Too many bugs at launch, but it's fine now.",
        "I couldn't put it down.",
        "Just average.",
        "A letdown compared to the prequel."
    ]

    review_count = 0
    for game_id in games:
        # Каждая игра получает от 3 до 8 отзывов
        num_reviews = random.randint(3, 8)
        reviewers = random.sample(users, k=num_reviews)
        
        for user_id in reviewers:
            score = round(random.uniform(5.0, 10.0), 1)
            text = random.choice(review_texts)
            # Разбрасываем отзывы по датам для наглядности статистики
            year = random.choice(['2025', '2026'])
            month = str(random.randint(1, 12)).zfill(2)
            day = str(random.randint(1, 28)).zfill(2)
            date = f"{year}-{month}-{day}"
            
            cursor.execute(
                "INSERT IGNORE INTO reviews (game_id, user_id, score, review_text, created_at) VALUES (%s, %s, %s, %s, %s)",
                (game_id, user_id, score, text, date)
            )
            review_count += 1

    connection.commit()
    cursor.close()
    connection.close()
    print(f"БД успешно заполнена тестовыми данными. Игр: {len(games)}, Отзывов: {review_count}.")

if __name__ == "__main__":
    main()
