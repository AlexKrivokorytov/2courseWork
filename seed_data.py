from dotenv import load_dotenv
import mysql.connector

from app import get_db_config


load_dotenv()


def main():
    connection = mysql.connector.connect(**get_db_config())
    cursor = connection.cursor()

    statements = [
        "DELETE FROM user_reviews",
        "DELETE FROM game_genres",
        "DELETE FROM game_platforms",
        "DELETE FROM games",
        "DELETE FROM users",
        "DELETE FROM genres",
        "DELETE FROM platforms",
        "DELETE FROM developers",
        "DELETE FROM publishers",
        """
        INSERT INTO developers (name, country) VALUES
        ('CD Projekt Red', 'Poland'),
        ('Rockstar Games', 'USA'),
        ('Valve', 'USA')
        """,
        """
        INSERT INTO publishers (name, country) VALUES
        ('Bandai Namco', 'Japan'),
        ('Take-Two Interactive', 'USA'),
        ('Valve Corporation', 'USA')
        """,
        """
        INSERT INTO genres (name) VALUES
        ('Action'),
        ('Adventure'),
        ('Open World'),
        ('RPG'),
        ('Shooter')
        """,
        """
        INSERT INTO platforms (name, abbreviation) VALUES
        ('PC', 'PC'),
        ('PlayStation 5', 'PS5'),
        ('Xbox Series X', 'XSX')
        """,
        """
        INSERT INTO users (username, email, password_hash) VALUES
        ('alex', 'alex@example.com', '12345'),
        ('denis', 'denis@example.com', '12345'),
        ('maria', 'maria@example.com', '12345')
        """,
        """
        INSERT INTO games (title, release_date, description, developer_id, publisher_id, cover_url) VALUES
        (
            'The Witcher 3',
            '2015-05-19',
            'Open world action RPG about Geralt of Rivia.',
            (SELECT id FROM developers WHERE name = 'CD Projekt Red'),
            (SELECT id FROM publishers WHERE name = 'Bandai Namco'),
            'https://upload.wikimedia.org/wikipedia/en/0/0c/Witcher_3_cover_art.jpg'
        ),
        (
            'Grand Theft Auto V',
            '2013-09-17',
            'Open world action game set in Los Santos.',
            (SELECT id FROM developers WHERE name = 'Rockstar Games'),
            (SELECT id FROM publishers WHERE name = 'Take-Two Interactive'),
            'https://upload.wikimedia.org/wikipedia/en/a/a5/Grand_Theft_Auto_V.png'
        ),
        (
            'Half-Life 2',
            '2004-11-16',
            'Story-driven first-person shooter from Valve.',
            (SELECT id FROM developers WHERE name = 'Valve'),
            (SELECT id FROM publishers WHERE name = 'Valve Corporation'),
            'https://upload.wikimedia.org/wikipedia/en/2/25/Half-Life_2_cover.jpg'
        )
        """,
        """
        INSERT INTO game_genres (game_id, genre_id)
        SELECT g.id, ge.id
        FROM games g
        JOIN genres ge
        WHERE
            (g.title = 'The Witcher 3' AND ge.name IN ('Action', 'Open World', 'RPG'))
            OR (g.title = 'Grand Theft Auto V' AND ge.name IN ('Action', 'Adventure', 'Open World'))
            OR (g.title = 'Half-Life 2' AND ge.name IN ('Action', 'Shooter'))
        """,
        """
        INSERT INTO game_platforms (game_id, platform_id)
        SELECT g.id, p.id
        FROM games g
        JOIN platforms p
        WHERE
            (g.title = 'The Witcher 3' AND p.abbreviation IN ('PC', 'PS5'))
            OR (g.title = 'Grand Theft Auto V' AND p.abbreviation IN ('PC', 'XSX'))
            OR (g.title = 'Half-Life 2' AND p.abbreviation = 'PC')
        """,
        """
        INSERT INTO user_reviews (game_id, user_id, score, review_text) VALUES
        (
            (SELECT id FROM games WHERE title = 'The Witcher 3'),
            (SELECT id FROM users WHERE username = 'alex'),
            9.5,
            'Great story, strong characters and a huge world.'
        ),
        (
            (SELECT id FROM games WHERE title = 'Grand Theft Auto V'),
            (SELECT id FROM users WHERE username = 'maria'),
            9.0,
            'Very fun open world with many activities.'
        ),
        (
            (SELECT id FROM games WHERE title = 'Half-Life 2'),
            (SELECT id FROM users WHERE username = 'denis'),
            9.7,
            'Classic shooter with excellent atmosphere.'
        )
        """,
    ]

    for statement in statements:
        cursor.execute(statement)

    connection.commit()
    cursor.close()
    connection.close()
    print("Seed data inserted.")


if __name__ == "__main__":
    main()
