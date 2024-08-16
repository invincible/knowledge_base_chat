from knowledge_base import KnowledgeBase


class DialogManager:
    def __init__(self, db_path):
        self.kb = KnowledgeBase(db_path)
        self.current_node_id = 1  # Начальный узел
        self.current_transitions = []

    def process_input(self, user_input):
        # Проверяем, является ли ввод пользователя выбором кнопки
        for transition in self.current_transitions:
            if user_input == transition[1]:  # transition[1] это текст кнопки
                return self.handle_node(transition[0])  # transition[0] это id следующего узла

        # Если ввод не соответствует кнопке, используем поиск
        return self.search_node(user_input)

    def handle_node(self, node_id):
        node = self.kb.get_node(node_id)
        self.current_transitions = self.kb.get_transitions(node_id)

        response = node[3]  # node's response
        buttons = [t[1] for t in self.current_transitions]  # button texts

        self.current_node_id = node_id

        return response, buttons

    def search_node(self, query):
        results = self.kb.find_similar(query)

        if results:
            response = "Возможно, вы имели в виду один из следующих вопросов:\n"
            buttons = []
            for result in results:
                response += f"- {result['name']} (схожесть: {result['similarity']})\n"
                buttons.append(result['name'])
            return response, buttons
        else:
            return "Извините, я не смог найти подходящий ответ. Попробуйте переформулировать вопрос.", []