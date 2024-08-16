import sqlite3

conn = sqlite3.connect('dialog.db')
cursor = conn.cursor()

# Создание таблиц
cursor.execute('''
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id INTEGER,
    response TEXT,
    FOREIGN KEY (parent_id) REFERENCES nodes(id)
)
''')

cursor.execute('''
CREATE TABLE transitions (
    id INTEGER PRIMARY KEY,
    from_node_id INTEGER NOT NULL,
    to_node_id INTEGER NOT NULL,
    button_text TEXT,
    FOREIGN KEY (from_node_id) REFERENCES nodes(id),
    FOREIGN KEY (to_node_id) REFERENCES nodes(id)
)
''')

cursor.execute('''
CREATE TABLE keywords (
    id INTEGER PRIMARY KEY,
    node_id INTEGER NOT NULL,
    keyword TEXT NOT NULL,
    FOREIGN KEY (node_id) REFERENCES nodes(id)
)
''')

# Заполнение таблиц данными
cursor.executemany('INSERT INTO nodes VALUES (?,?,?,?)', [
    (1, 'Главное меню', None, 'Добро пожаловать! Чем я могу вам помочь?'),
    (2, 'Заключение договора', 1, 'Процесс заключения договора состоит из нескольких этапов. Хотите узнать подробнее?'),
    (3, 'Этапы заключения договора', 2, 'Этапы заключения договора: 1. Подготовка документов, 2. Согласование условий, 3. Подписание. Какой этап вас интересует?'),
    (4, 'Подготовка документов', 3, 'Для подготовки документов необходимо собрать следующие бумаги: ...'),
    (5, 'Типы договоров', 1, 'У нас есть несколько типов договоров. Какой вас интересует?'),
    (6, 'Трудовой договор', 5, 'Трудовой договор - это соглашение между работодателем и работником, которое устанавливает их взаимные права и обязанности.'),
    (7, 'Договор подряда', 5, 'Договор подряда - это соглашение, по которому одна сторона (подрядчик) обязуется выполнить определенную работу по заданию другой стороны (заказчика).'),
])

cursor.executemany('INSERT INTO transitions VALUES (?,?,?,?)', [
    (1, 1, 2, 'Заключение договора'),
    (2, 1, 5, 'Типы договоров'),
    (3, 2, 3, 'Да'),
    (4, 2, 1, 'Нет'),
    (5, 3, 4, 'Подготовка документов'),
    (6, 3, 1, 'Вернуться в главное меню'),
    (7, 4, 3, 'Назад'),
    (8, 4, 1, 'Вернуться в главное меню'),
    (9, 5, 6, None),
    (10, 5, 7, None),
    (11, 5, 1, 'Вернуться в главное меню'),
    (12, 6, 5, 'Назад'),
    (13, 6, 1, 'Вернуться в главное меню'),
    (14, 7, 5, 'Назад'),
    (15, 7, 1, 'Вернуться в главное меню'),
])

cursor.executemany('INSERT INTO keywords VALUES (?,?,?)', [
    (1, 2, 'как заключить договор'),
    (2, 2, 'процесс заключения договора'),
    (3, 5, 'типы договоров'),
    (4, 5, 'виды договоров'),
    (5, 6, 'что такое трудовой договор'),
    (6, 7, 'что такое договор подряда'),
])

conn.commit()
conn.close()