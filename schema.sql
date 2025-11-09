-- CREATING AND USING DATABASE
CREATE DATABASE IF NOT EXISTS moviedb;
USE moviedb;

-- DROP TABLE IF IT EXISTS
DROP TABLE IF EXISTS ratings;
DROP TABLE IF EXISTS movies;


-- CREATING MOVIES TABLE
CREATE TABLE IF NOT EXISTS movies (
    movie_id INT PRIMARY KEY,
    title VARCHAR(255),
    genres VARCHAR(255),
    director VARCHAR(255),
    plot TEXT,
    box_office VARCHAR(100),
    year INT
);

-- CREATING RATINGS TABLE
CREATE TABLE IF NOT EXISTS ratings (
    user_id INT,
    movie_id INT,
    rating FLOAT,
    timestamp DATETIME,
    PRIMARY KEY (user_id, movie_id)
);
