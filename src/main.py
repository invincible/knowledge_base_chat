import os
import logging
from knowledge_base import KnowledgeBase
from dialog_manager import DialogManager


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def initialize_knowledge_base(kb):
    logger.info("Initializing knowledge base")

    # Проверяем, существует ли уже главное меню
    kb.cursor.execute("SELECT id FROM nodes WHERE node_type = 'question' AND question LIKE '%Выберите категорию%'")
    existing_main_menu = kb.cursor.fetchone()

    if existing_main_menu:
        main_menu_id = existing_main_menu[0]
    else:
        main_menu_id = kb.add_node("question", "Выберите категорию: Договоры, Закупки, Финансы", None)
        kb.add_button(main_menu_id, "Договоры")
        kb.add_button(main_menu_id, "Закупки")
        kb.add_button(main_menu_id, "Финансы")

    # Ветка "Договоры"
    contracts_id = kb.add_node("question", "Вопросы по договорам: Как заключить договор? Сроки согласования договора", None)
    kb.add_transition(main_menu_id, contracts_id, "Договоры")
    kb.add_button(contracts_id, "Как заключить договор?")
    kb.add_button(contracts_id, "Сроки согласования договора")

    how_to_contract_id = kb.add_node("answer", "Как заключить договор? Процесс заключения договора. Этапы заключения договора.",
                                     "Для заключения договора необходимо: 1) Подготовить проект договора; 2) Согласовать его с юридическим отделом; 3) Подписать у руководителя.")
    kb.add_transition(contracts_id, how_to_contract_id, "Как заключить договор?")

    contract_time_id = kb.add_node("answer",
                                   "Сроки согласования договора. Как долго согласовывается договор? Время на согласование договора.",
                                   "Стандартный срок согласования договора составляет 5 рабочих дней.")
    kb.add_transition(contracts_id, contract_time_id, "Сроки согласования договора")

    # Ветка "Закупки"
    purchases_id = kb.add_node("question", "Вопросы по закупкам: Как провести тендер? Лимиты закупок", None)
    kb.add_transition(main_menu_id, purchases_id, "Закупки")
    kb.add_button(purchases_id, "Как провести тендер?")
    kb.add_button(purchases_id, "Лимиты закупок")

    tender_id = kb.add_node("question", "Выберите тип тендера: Открытый тендер, Закрытый тендер", None)
    kb.add_transition(purchases_id, tender_id, "Как провести тендер?")
    kb.add_button(tender_id, "Открытый тендер")
    kb.add_button(tender_id, "Закрытый тендер")

    open_tender_id = kb.add_node("answer", "Как провести открытый тендер? Этапы открытого тендера.",
                                 "Для проведения открытого тендера: 1) Подготовьте техническое задание; 2) Опубликуйте объявление о тендере; 3) Соберите и оцените предложения; 4) Выберите победителя.")
    kb.add_transition(tender_id, open_tender_id, "Открытый тендер")

    closed_tender_id = kb.add_node("answer", "Как провести закрытый тендер? Этапы закрытого тендера.",
                                   "Для проведения закрытого тендера: 1) Составьте список потенциальных поставщиков; 2) Отправьте им приглашения и техническое задание; 3) Соберите и оцените предложения; 4) Выберите победителя.")
    kb.add_transition(tender_id, closed_tender_id, "Закрытый тендер")

    purchase_limits_id = kb.add_node("answer", "Лимиты закупок. Ограничения по суммам закупок.",
                                     "Лимиты закупок: До 100 000 руб. - прямая закупка; От 100 000 до 1 000 000 руб. - запрос котировок; Свыше 1 000 000 руб. - тендер.")
    kb.add_transition(purchases_id, purchase_limits_id, "Лимиты закупок")

    # Ветка "Финансы"
    finances_id = kb.add_node("question", "Вопросы по финансам: Как сформировать бюджет? Сроки подачи отчетности", None)
    kb.add_transition(main_menu_id, finances_id, "Финансы")
    kb.add_button(finances_id, "Как сформировать бюджет?")
    kb.add_button(finances_id, "Сроки подачи отчетности")

    budget_id = kb.add_node("answer", "Как сформировать бюджет? Этапы формирования бюджета.",
                            "Для формирования бюджета: 1) Соберите данные от всех подразделений; 2) Проанализируйте исторические данные; 3) Составьте прогноз на следующий период; 4) Согласуйте бюджет с руководством.")
    kb.add_transition(finances_id, budget_id, "Как сформировать бюджет?")

    reporting_id = kb.add_node("answer", "Сроки подачи отчетности. Когда сдавать отчеты?",
                               "Сроки подачи отчетности: Ежемесячный отчет - до 10 числа следующего месяца; Квартальный отчет - до 20 числа месяца, следующего за отчетным кварталом; Годовой отчет - до 31 марта следующего года.")
    kb.add_transition(finances_id, reporting_id, "Сроки подачи отчетности")

    logger.info("Knowledge base initialized")


def main():
    logger.info("Starting the application")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "..", "database", "knowledge_base.db")

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    logger.info(f"Database path: {db_path}")

    kb = KnowledgeBase(db_path)
    kb.clear_database()
    initialize_knowledge_base(kb)
    #kb.print_all_data()
    dm = DialogManager(kb)

    print("Добро пожаловать в систему вопросов и ответов!")
    print("Вы можете выбрать категорию или задать вопрос напрямую.")
    print("Для выхода введите 'выход'.")

    while True:
        response = dm.process_node()
        logger.debug(f"Response from DialogManager: {response}")
        print("\n" + response["response"])
        print("Доступные опции:", ", ".join(response["buttons"]))
        print("Или задайте свой вопрос.")

        user_input = input("\nВаш выбор или вопрос: ")
        logger.debug(f"User input: {user_input}")
        if user_input.lower() == 'выход':
            logger.info("User requested to exit")
            break

        dm.process_input(user_input)

    kb.close()
    logger.info("Application shutting down")
    print("Спасибо за использование системы. До свидания!")


if __name__ == "__main__":
    main()