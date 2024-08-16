from knowledge_base import KnowledgeBase


class DialogManager:
    def __init__(self, db_path):
        self.kb = KnowledgeBase(db_path)
        self.current_node_id = 1  # Начальный узел
        self.current_transitions = []

    def process_input(self, user_input):
        user_input = user_input.lower().strip()  # Приводим ввод к нижнему регистру и убираем пробелы

        # Проверяем стандартные команды
        if user_input in ['назад', 'вернуться']:
            parent_id = self.kb.get_parent_id(self.current_node_id)
            return self.handle_node(parent_id if parent_id else 1)
        elif user_input in ['главное меню', 'меню']:
            return self.handle_node(1)

        # Проверяем, является ли ввод пользователя выбором кнопки
        for transition in self.current_transitions:
            if user_input == transition[1].lower():  # transition[1] это текст кнопки
                return self.handle_node(transition[0])  # transition[0] это id следующего узла

        # Если ввод не соответствует кнопке, используем поиск
        return self.search_node(user_input)

    def handle_node(self, node_id):
        node = self.kb.get_node(node_id)
        self.current_transitions = self.kb.get_transitions(node_id)

        response = node[3]  # node's response
        buttons = [t[1] for t in self.current_transitions]  # button texts

        # Добавляем стандартные кнопки, если это не главное меню
        if node_id != 1:
            parent_id = self.kb.get_parent_id(node_id)
            if parent_id:
                buttons.append("Назад")
            buttons.append("Главное меню")

        self.current_node_id = node_id

        return response, buttons

    def search_node(self, query):
        results = self.kb.find_similar(query)

        if results:
            if len(results) == 1 and float(results[0]['similarity'][:-1]) >= 70:
                # Если найден один узел с уверенностью >= 70%, переходим к нему
                return self.handle_node(results[0]['node_id'])
            else:
                # Создаем новое меню из вероятных узлов
                response = "Возможно, вы имели в виду один из следующих вопросов:\n"
                buttons = []
                for result in results[:4]:  # Ограничиваем количество вариантов до 4
                    response += f"- {result['name']} (схожесть: {result['similarity']})\n"
                    buttons.append(result['name'])
                return response, buttons
        else:
            return "Извините, я не смог найти подходящий ответ. Попробуйте переформулировать вопрос.", []