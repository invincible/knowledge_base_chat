from knowledge_base import KnowledgeBase

class DialogManager:
    def __init__(self):
        self.kb = KnowledgeBase()
        self.current_node_id = 1
        self.current_transitions = []
        self.is_search_result = False

    def handle_node(self, node_id):
        self.is_search_result = False
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

    def process_input(self, user_input):
        if not user_input.strip():
            return self.handle_node(1)

        user_input = user_input.lower().strip()

        # Если мы находимся в результатах поиска, обрабатываем ввод особым образом
        if self.is_search_result:
            for transition in self.current_transitions:
                if user_input == transition[1].lower():
                    return self.handle_node(transition[0])
            # Если ввод не соответствует ни одному из предложенных вариантов,
            # возвращаемся к обычному поиску
            self.is_search_result = False

        # Проверяем стандартные команды
        if user_input in ['назад', 'вернуться']:
            parent_id = self.kb.get_parent_id(self.current_node_id)
            return self.handle_node(parent_id if parent_id else 1)
        elif user_input in ['главное меню', 'меню']:
            return self.handle_node(1)

        # Проверяем, является ли ввод пользователя выбором кнопки
        for transition in self.current_transitions:
            if user_input == transition[1].lower():
                return self.handle_node(transition[0])

        # Если ввод не соответствует кнопке, используем поиск
        return self.search_node(user_input)

    def search_node(self, query):
        results = self.kb.find_similar(query)

        if results:
            # Проверяем на 100% совпадение
            exact_match = next((result for result in results if float(result['similarity'][:-1]) == 100), None)
            if exact_match:
                return self.handle_node(exact_match['node_id'])

            if len(results) == 1 and float(results[0]['similarity'][:-1]) >= 70:
                # Если найден один узел с уверенностью >= 70%, переходим к нему
                return self.handle_node(results[0]['node_id'])
            else:
                # Создаем новое меню из вероятных узлов
                self.is_search_result = True
                response = "Возможно, вы имели в виду один из следующих вопросов:\n"
                self.current_transitions = []
                for result in results[:4]:
                    response += f"- {result['name']} (схожесть: {result['similarity']})\n"
                    self.current_transitions.append((result['node_id'], result['name']))
                buttons = [t[1] for t in self.current_transitions]
                return response, buttons
        else:
            self.is_search_result = False
            return "Извините, я не смог найти подходящий ответ. Попробуйте переформулировать вопрос.", []