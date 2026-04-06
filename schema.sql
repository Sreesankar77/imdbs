-- Admin table
CREATE TABLE admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL
);

-- User table
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,    mysql> USE imdbs;                  -- or whatever your DB is named
    mysql> DELIMITER $$
    mysql> CREATE TRIGGER limit_favourites_per_user
        -> BEFORE INSERT ON favourites
        -> FOR EACH ROW
        -> BEGIN
        ->     IF (SELECT COUNT(*) FROM favourites WHERE user_id = NEW.user_id) >= 4 THEN
        ->         SIGNAL SQLSTATE '45000'
        ->             SET MESSAGE_TEXT = 'Cannot add more than 4 favourites per user';
        ->     END IF;
        -> END$$
    mysql> DELIMITER ;
    password_hash VARCHAR(200) NOT NULL
);

-- Movie table
CREATE TABLE movie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    director VARCHAR(120),
    rating FLOAT DEFAULT 0.0,
    description TEXT,
    poster VARCHAR(300),
    detail_poster VARCHAR(300),
    scene1 VARCHAR(300),
    scene2 VARCHAR(300),
    scene3 VARCHAR(300)
);

-- Watchlist junction table (User-Movie many-to-many)
CREATE TABLE watchlist (
    user_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES movie(id) ON DELETE CASCADE
);

-- Watched junction table (User-Movie many-to-many)
CREATE TABLE watched (
    user_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES movie(id) ON DELETE CASCADE
);

-- Favourites junction table (User-Movie many-to-many)
CREATE TABLE favourites (
    user_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES movie(id) ON DELETE CASCADE
);

-- Trigger to limit each user to at most 4 favourites
CREATE TRIGGER limit_favourites_per_user
BEFORE INSERT ON favourites
FOR EACH ROW
BEGIN
    SELECT
        CASE
            WHEN (SELECT COUNT(*) FROM favourites WHERE user_id = NEW.user_id) >= 4
            THEN RAISE(ABORT, 'Cannot add more than 4 favourites per user')
        END;
END;
