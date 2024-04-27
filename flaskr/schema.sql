DROP TABLE IF EXISTS device;
DROP TABLE IF EXISTS price;

CREATE TABLE device (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_name TEXT NOT NULL,
    device_img TEXT
);

CREATE TABLE price (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    price INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT (DATETIME('now','localtime')),
    device_id INTEGER NOT NULL,
    FOREIGN KEY (device_id) REFERENCES device(id)
);