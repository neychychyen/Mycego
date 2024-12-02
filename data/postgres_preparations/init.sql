-- 'psql -h db -U ${POSTGRES_USER} -d ${POSTGRES_DB}'

-- Создание таблицы download
CREATE TABLE download (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    type VARCHAR(1) NOT NULL CHECK (type IN ('i', 'd')),
    url VARCHAR(255) NOT NULL,
    public_key VARCHAR(255) NOT NULL
);


-- Создание таблицы response с дополнительными полями
CREATE TABLE response (
    id SERIAL PRIMARY KEY,
    download_id INTEGER REFERENCES download(id) ON DELETE CASCADE,
    ready_to_use BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Время создания записи
    file_md5 VARCHAR(32),  -- Хеш MD5 файлов, может быть пустым
    directory_md5 VARCHAR(32),  -- Хеш MD5 директории, может быть пустым
    UNIQUE (download_id)
);