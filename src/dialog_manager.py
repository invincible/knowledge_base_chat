import logging

logger = logging.getLogger(__name__)


class DialogManager:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.current_node_id = 1
        self.main_menu_id = 1
        self.previous_node_id = None
        logger.info("Initialized DialogManager")

    def process_input(self, user_input):
        logger.debug(f"Processing user input: {user_input}")
        clean_input = user_input.lower().strip()

        if clean_input == "главное меню":
            logger.debug("User requested main menu")
            return self.return_to_main_menu()
        elif clean_input == "назад":
            logger.debug("User requested to go back")
            return self.go_back()

        # Сначала проверяем, соответствует ли ввод одной из кнопок текущего узла
        buttons = self.kb.get_buttons(self.current_node_id)
        for button in buttons:
            if clean_input == button.lower():
                node = self.kb.get_node_by_button(button)
                if node:
                    logger.debug(f"Found node for button: {node}")
                    self.previous_node_id = self.current_node_id
                    self.current_node_id = node[0]
                    return self.process_node()

        # Если не найдена соответствующая кнопка, выполняем поиск
        logger.debug("No matching button found, searching for answer")
        return self.search_answer(clean_input)

    def search_answer(self, query):
        results = self.kb.fuzzy_search_nodes(query)
        if results:
            logger.debug(f"Fuzzy search results: {results}")

            answer_nodes = [node for node in results if node[1] == 'answer']
            if answer_nodes:
                best_match = answer_nodes[0]
            else:
                best_match = results[0]

            self.previous_node_id = self.current_node_id
            self.current_node_id = best_match[0]

            if best_match[1] == "answer":
                return self.provide_answer(best_match[3])
            else:
                buttons = self.kb.get_buttons(self.current_node_id)
                return {
                    "response": f"Похоже, вы интересуетесь темой: {best_match[2]}\nВыберите конкретный вопрос:",
                    "buttons": buttons
                }
        else:
            return self.default_response()

    def return_to_main_menu(self):
        self.previous_node_id = self.current_node_id
        self.current_node_id = self.main_menu_id
        return self.process_node()

    def go_back(self):
        if self.previous_node_id:
            self.current_node_id, self.previous_node_id = self.previous_node_id, self.current_node_id
            return self.process_node()
        else:
            return self.return_to_main_menu()

    def provide_answer(self, answer):
        buttons = self.kb.get_buttons(self.current_node_id)
        if "Главное меню" not in buttons:
            buttons.append("Главное меню")
        if self.current_node_id != self.main_menu_id:
            buttons.append("Назад")
        return {
            "response": answer,
            "buttons": buttons
        }

    def ask_question(self, question):
        buttons = self.kb.get_buttons(self.current_node_id)
        if "Главное меню" not in buttons:
            buttons.append("Главное меню")
        if self.current_node_id != self.main_menu_id:
            buttons.append("Назад")
        return {
            "response": question,
            "buttons": buttons
        }

    def process_node(self):
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

    def default_response(self):
        return {
            "response": "Извините, я не могу ответить на этот вопрос. Попробуйте сформулировать его иначе или выберите другую категорию.",
            "buttons": ["Главное меню", "Назад"]
        }