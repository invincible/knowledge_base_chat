from dialog_manager import DialogManager


def main():
    dm = DialogManager('../data/dialog.db')

    print("Добро пожаловать! Задайте свой вопрос или выберите опцию.")

    while True:
        response, buttons = dm.handle_node(dm.current_node_id)
        print("\n" + response)

        if buttons:
            print("\nДоступные опции:")
            for i, button in enumerate(buttons, 1):
                print(f"{i}. {button}")

        user_input = input("\nВаш ввод (или 'выход' для завершения): ")

        if user_input.lower() == 'выход':
            break

        if buttons and user_input.isdigit() and 1 <= int(user_input) <= len(buttons):
            user_input = buttons[int(user_input) - 1]

        response, buttons = dm.process_input(user_input)
        print("\n" + response)


if __name__ == "__main__":
    main()