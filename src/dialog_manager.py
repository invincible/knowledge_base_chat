from knowledge_base import KnowledgeBase

class DialogManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.kb = None
        self.current_node_id = 1
        self.current_transitions = []
        self.is_search_result = False
        self.standard_buttons = ["Назад", "Главное меню"]
        self.connect_kb()

    def connect_kb(self):
        self.kb = KnowledgeBase(self.db_path)
        self.kb.connect()

    def handle_node(self, node_id):
        self.is_search_result = False
        node = self.kb.get_node(node_id)
        if not node:
            return "Извините, произошла ошибка при получении информации.", []

        self.current_transitions = self.kb.get_transitions(node_id)
        response = node[3]  # node's response
        buttons = [t[1] for t in self.current_transitions]  # button texts

        if node_id != 1:
            buttons.extend(self.standard_buttons)

        self.current_node_id = node_id
        return response, buttons

    def process_input(self, user_input):
        user_input = user_input.lower().strip()

        if self.is_search_result:
            return self._process_search_result(user_input)

        if user_input in ['назад', 'вернуться']:
            return self._handle_back()
        elif user_input in ['главное меню', 'меню']:
            return self.handle_node(1)

        for transition in self.current_transitions:
            if user_input == transition[1].lower():
                return self.handle_node(transition[0])

        return self.search_node(user_input)

    def _process_search_result(self, user_input):
        for transition in self.current_transitions:
            if user_input == transition[1].lower():
                return self.handle_node(transition[0])
        self.is_search_result = False
        return self.search_node(user_input)

    def _handle_back(self):
        parent_id = self.kb.get_parent_id(self.current_node_id)
        return self.handle_node(parent_id if parent_id else 1)

    def search_node(self, query):
        results = self.kb.find_similar(query)

        if results:
            # Проверяем на 100% совпадение
            exact_match = next((result for result in results if float(result['similarity'][:-1]) == 100), None)
            if exact_match:
                return self.handle_node(exact_match['node_id'])

            # Если нет точного совпадения, но есть результат с высокой схожестью
            if len(results) == 1 and float(results[0]['similarity'][:-1]) >= 70:
                return self.handle_node(results[0]['node_id'])

            # Если есть несколько результатов
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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.kb:
            self.kb.__exit__(exc_type, exc_val, exc_tb)