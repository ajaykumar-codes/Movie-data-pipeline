-- 1. Movie with the highest average rating
SELECT m.title, AVG(r.rating) AS avg_rating
FROM ratings r
JOIN movies m ON m.movieID = r.movieID
GROUP BY m.title
ORDER BY avg_rating DESC
LIMIT 1;

-- 2. Top 5 genres with highest average rating
SELECT m.genres, AVG(r.rating) AS avg_rating
FROM ratings r
JOIN movies m ON m.movieID = r.movieID
GROUP BY m.genres
ORDER BY avg_rating DESC
LIMIT 5;

-- 3. Director with the most movies
SELECT director, COUNT(*) AS movie_count
FROM movies
WHERE director IS NOT NULL
GROUP BY director
ORDER BY movie_count DESC
LIMIT 1;

-- 4. Average rating by year
SELECT m.year, AVG(r.rating) AS avg_rating
FROM ratings r
JOIN movies m ON m.movieID = r.movieID
GROUP BY m.year
ORDER BY m.year;