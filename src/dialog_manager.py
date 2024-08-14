import logging

logger = logging.getLogger(__name__)


class DialogManager:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.current_node_id = 1
        logger.info("Initialized DialogManager")

    def process_input(self, user_input):
        logger.debug(f"Processing user input: {user_input}")
        clean_input = user_input.lower().strip()

        if clean_input == "главное меню":
            logger.debug("User requested main menu")
            return self.return_to_main_menu()
        elif clean_input == "другой вопрос":
            logger.debug("User requested another question")
            return self.return_to_previous_question()

        # Сначала проверяем, соответствует ли ввод одной из кнопок текущего узла
        buttons = self.kb.get_buttons(self.current_node_id)
        for button in buttons:
            if clean_input == button.lower():
                node = self.kb.get_node_by_button(button)
                if node:
                    logger.debug(f"Found node for button: {node}")
                    self.current_node_id = node[0]
                    return self.process_node()

        # Если не найдена соответствующая кнопка, выполняем поиск
        logger.debug("No matching button found, searching for answer")
        return self.search_answer(clean_input)

    def process_node(self):
        logger.debug(f"Processing node with id: {self.current_node_id}")
        node = self.kb.get_node(self.current_node_id)
        if not node:
            logger.warning(f"Node not found for id: {self.current_node_id}")
            return self.default_response()

        node_type, question, answer = node[1:]
        logger.debug(f"Node type: {node_type}, Question: {question}, Answer: {answer}")

        if node_type == "question":
            return self.ask_question(question)
        elif node_type == "answer":
            return self.provide_answer(answer)
        else:
            logger.warning(f"Unknown node type: {node_type}")
            return self.default_response()

    def search_answer(self, query):
        results = self.kb.search_nodes(query)
        if results:
            # Сортируем результаты, отдавая приоритет ответам и точным совпадениям
            sorted_results = sorted(results, key=lambda x: (
                x[1] != "answer",  # Приоритет ответам
                query.lower() not in (x[2] or '').lower() if x[2] else True,  # Затем точным совпадениям в вопросах
                len(x[3] or '') if x[3] else 0  # Затем длине ответа
            ))

            best_match = sorted_results[0]
            self.current_node_id = best_match[0]

            if best_match[1] == "answer":
                return self.provide_answer(best_match[3])
            else:
                return self.process_node()
        else:
            return self.default_response()


    def ask_question(self, question):
        buttons = self.kb.get_buttons(self.current_node_id)
        return {
            "response": question,
            "buttons": buttons
        }

    def provide_answer(self, answer):
        buttons = self.kb.get_buttons(self.current_node_id)
        if not buttons:
            buttons = ["Главное меню", "Другой вопрос"]
        return {
            "response": answer,
            "buttons": buttons
        }

    def return_to_main_menu(self):
        self.current_node_id = 1
        return self.process_node()

    def return_to_previous_question(self):
        parent_node = self.get_parent_node()
        if parent_node:
            self.current_node_id = parent_node
            return self.process_node()
        else:
            return self.return_to_main_menu()

    def get_parent_node(self):
        self.kb.cursor.execute("""
            SELECT from_node_id 
            FROM transitions 
            WHERE to_node_id = ?
        """, (self.current_node_id,))
        result = self.kb.cursor.fetchone()
        return result[0] if result else None

    def default_response(self):
        return {
            "response": "Извините, я не могу ответить на этот вопрос. Попробуйте сформулировать его иначе или выберите другую категорию.",
            "buttons": ["Главное меню", "Другой вопрос"]
        }