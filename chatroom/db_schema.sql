DROP TABLE IF EXISTS Messages;
DROP TABLE IF EXISTS Chats;
DROP TABLE IF EXISTS Sessions;
DROP TABLE IF EXISTS Users;

CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    pk_n BLOB NOT NULL,
    pk_e BLOB NOT NULL,
    pk_d BLOB NOT NULL
);

CREATE TABLE Sessions (
    userref INTEGER REFERENCES Users(user_id),
    login_tm INTEGER CHECK (login_tm BETWEEN 1 AND CURRENT_TIMESTAMP)
);

CREATE TABLE Chats (
    chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    participant1 INTEGER REFERENCES Users(user_id),
    participant2 INTEGER REFERENCES Users(user_id),
    creation_tm TEXT,
    last_mod_tm TEXT,
    CHECK (participant1 != participant2),
    UNIQUE(participant1, participant2)
);

CREATE TABLE Messages (
    msg_id INTEGER PRIMARY KEY AUTOINCREMENT,
    chatref INTEGER REFERENCES Chats(chat_id),
    sender INTEGER REFERENCES Users(user_id),
    recipient INTEGER REFERENCES Users(user_id),
    msg_data BLOB,
    CHECK (sender != recipient)
);
