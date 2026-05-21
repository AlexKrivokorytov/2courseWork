-- Пересоздание базы данных
DROP DATABASE IF EXISTS game_db;
CREATE DATABASE game_db;
USE game_db;

-- Таблица разработчиков игр
CREATE TABLE IF NOT EXISTS developers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    country VARCHAR(100) NOT NULL
);

-- Таблица издателей игр
CREATE TABLE IF NOT EXISTS publishers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    country VARCHAR(100) NOT NULL
);

-- Справочник жанров
CREATE TABLE IF NOT EXISTS genres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Справочник игровых платформ
CREATE TABLE IF NOT EXISTS platforms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    abbreviation VARCHAR(20) NOT NULL UNIQUE
);

-- Таблица пользователей системы
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_admin TINYINT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Основная таблица игр
CREATE TABLE IF NOT EXISTS games (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL UNIQUE,
    release_date DATE NOT NULL,
    description TEXT NOT NULL,
    developer_id INT NOT NULL,
    publisher_id INT NOT NULL,
    cover_url VARCHAR(255),
    FOREIGN KEY (developer_id) REFERENCES developers(id) ON DELETE CASCADE,
    FOREIGN KEY (publisher_id) REFERENCES publishers(id) ON DELETE CASCADE
);

-- Связующая таблица: Игры <-> Жанры
CREATE TABLE IF NOT EXISTS game_genres (
    game_id INT NOT NULL,
    genre_id INT NOT NULL,
    PRIMARY KEY (game_id, genre_id),
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
);

-- Связующая таблица: Игры <-> Платформы
CREATE TABLE IF NOT EXISTS game_platforms (
    game_id INT NOT NULL,
    platform_id INT NOT NULL,
    PRIMARY KEY (game_id, platform_id),
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
    FOREIGN KEY (platform_id) REFERENCES platforms(id) ON DELETE CASCADE
);

-- Таблица отзывов пользователей
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    game_id INT NOT NULL,
    user_id INT NOT NULL,
    score DECIMAL(4,1) NOT NULL CHECK (score >= 0.0 AND score <= 10.0),
    review_text TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_reviews_game_user (game_id, user_id),
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Таблица логов аудита
CREATE TABLE IF NOT EXISTS review_audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    review_id INT,
    action_type ENUM('INSERT', 'UPDATE', 'DELETE'),
    action_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    old_score DECIMAL(4,1),
    new_score DECIMAL(4,1),
    user_info VARCHAR(255)
);

-- Функция статуса оценки
DELIMITER //
CREATE FUNCTION fn_get_rating_status(score DECIMAL(4,1)) 
RETURNS VARCHAR(20)
DETERMINISTIC
BEGIN
    DECLARE status VARCHAR(20);
    IF score >= 9.0 THEN SET status = 'Masterpiece';
    ELSEIF score >= 7.5 THEN SET status = 'Great';
    ELSEIF score >= 5.0 THEN SET status = 'Mediocre';
    ELSE SET status = 'Poor';
    END IF;
    RETURN status;
END //
DELIMITER ;

-- Представление рейтингов игр (Включает оконную функцию RANK)
CREATE OR REPLACE VIEW v_game_rankings AS
SELECT 
    g.id, 
    g.title,
    d.name as developer,
    p.name as publisher,
    COALESCE(avg_rev.score, 0) as total_score,
    fn_get_rating_status(COALESCE(avg_rev.score, 0)) as rating_status,
    RANK() OVER (ORDER BY COALESCE(avg_rev.score, 0) DESC) as global_rank
FROM games g
JOIN developers d ON g.developer_id = d.id
JOIN publishers p ON g.publisher_id = p.id
LEFT JOIN (SELECT game_id, AVG(score) as score FROM reviews GROUP BY game_id) avg_rev ON g.id = avg_rev.game_id;

-- Хранимая Процедура: Добавление игры
DELIMITER //
CREATE PROCEDURE sp_add_game_full(
    IN p_title VARCHAR(255),
    IN p_release_date DATE,
    IN p_description TEXT,
    IN p_developer_id INT,
    IN p_publisher_id INT,
    IN p_cover_url VARCHAR(255)
)
BEGIN
    INSERT INTO games (title, release_date, description, developer_id, publisher_id, cover_url)
    VALUES (p_title, p_release_date, p_description, p_developer_id, p_publisher_id, p_cover_url);
    
    SELECT LAST_INSERT_ID() AS game_id;
END //
DELIMITER ;

-- Триггер: Автоматическое логирование отзывов
DELIMITER //
CREATE TRIGGER tr_after_review_insert
AFTER INSERT ON reviews
FOR EACH ROW
BEGIN
    INSERT INTO review_audit_log (review_id, action_type, new_score, user_info)
    VALUES (NEW.id, 'INSERT', NEW.score, CONCAT('User ID: ', NEW.user_id));
END //
DELIMITER ;
