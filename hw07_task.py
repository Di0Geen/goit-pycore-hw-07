# Псевдокод:
# Імпортувати UserDict з модуля collections.
# Імпортувати datetime і timedelta з модуля datetime.
# Створити базовий клас Field для зберігання значення поля.
# Створити клас Name для імені контакту.
# Створити клас Phone для телефону з перевіркою на 10 цифр.
# Створити клас Birthday для дня народження з перевіркою формату DD.MM.YYYY.
# Створити клас Record для одного контакту: ім'я, телефони, день народження.
# Створити клас AddressBook для зберігання всіх контактів.
# Додати метод get_upcoming_birthdays для пошуку днів народження на 7 днів.
# Створити декоратор input_error для обробки помилок введення.
# Додати команди: hello, add, change, phone, all.
# Додати команди: add-birthday, show-birthday, birthdays.
# Завершувати роботу командами close або exit.

from collections import UserDict
from datetime import datetime, timedelta


class Field:
    # Базовий клас для полів запису
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    # Клас для зберігання імені контакту
    pass


class Phone(Field):
    # Клас для зберігання телефону з валідацією
    def __init__(self, value):
        # Перевіряємо, що телефон складається тільки з цифр і має довжину 10 символів
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")

        super().__init__(value)


class Birthday(Field):
    # Клас для зберігання дня народження з валідацією
    def __init__(self, value):
        try:
            # Перевіряємо правильність формату дати DD.MM.YYYY
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

        super().__init__(value)


class Record:
    # Клас для зберігання одного контакту
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        # Додаємо телефон до контакту
        self.phones.append(Phone(phone))

    def find_phone(self, phone):
        # Шукаємо телефон у контакті
        return next((item for item in self.phones if item.value == phone), None)

    def edit_phone(self, old_phone, new_phone):
        # Редагуємо існуючий телефон
        phone_to_edit = self.find_phone(old_phone)

        if phone_to_edit is None:
            raise ValueError("Phone not found.")

        phone_to_edit.value = Phone(new_phone).value

    def remove_phone(self, phone):
        # Видаляємо телефон з контакту
        phone_to_remove = self.find_phone(phone)

        if phone_to_remove:
            self.phones.remove(phone_to_remove)

    def add_birthday(self, birthday):
        # Додаємо день народження до контакту
        self.birthday = Birthday(birthday)

    def __str__(self):
        # Формуємо рядок з телефонами контакту
        phones = "; ".join(phone.value for phone in self.phones)

        # Якщо день народження є, додаємо його до виводу
        birthday = f", birthday: {self.birthday.value}" if self.birthday else ""

        return f"Contact name: {self.name.value}, phones: {phones}{birthday}"


class AddressBook(UserDict):
    # Клас для зберігання адресної книги
    def add_record(self, record):
        # Додаємо запис до адресної книги
        self.data[record.name.value] = record

    def find(self, name):
        # Шукаємо запис за іменем
        return self.data.get(name)

    def delete(self, name):
        # Видаляємо запис за іменем
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        # Повертаємо список контактів, яких потрібно привітати протягом наступного тижня
        result = []
        today = datetime.today().date()

        for record in self.data.values():
            # Пропускаємо контакти без дня народження
            if not record.birthday:
                continue

            # Перетворюємо день народження з рядка у дату
            birthday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()

            # Створюємо дату дня народження у поточному році
            birthday_this_year = birthday.replace(year=today.year)

            # Якщо день народження вже минув, переносимо його на наступний рік
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            # Перевіряємо, чи день народження буде протягом 7 днів
            if 0 <= (birthday_this_year - today).days <= 7:
                congratulation_date = birthday_this_year

                # Якщо день народження у суботу, переносимо привітання на понеділок
                if congratulation_date.weekday() == 5:
                    congratulation_date += timedelta(days=2)

                # Якщо день народження у неділю, переносимо привітання на понеділок
                elif congratulation_date.weekday() == 6:
                    congratulation_date += timedelta(days=1)

                result.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation_date.strftime("%d.%m.%Y")
                })

        return result


def input_error(func):
    # Декоратор для обробки помилок введення
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as error:
            return str(error)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Enter the argument for the command."
        except AttributeError:
            return "Contact not found."

    return inner


def parse_input(user_input):
    # Розділяємо введений текст на команду та аргументи
    parts = user_input.split()

    if not parts:
        return "", []

    return parts[0].lower(), parts[1:]


@input_error
def add_contact(args, book):
    # Додаємо новий контакт або новий телефон до існуючого контакту
    if len(args) < 2:
        raise IndexError

    name, phone, *_ = args
    record = book.find(name)

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    else:
        message = "Contact updated."

    record.add_phone(phone)

    return message


@input_error
def change_contact(args, book):
    # Змінюємо телефон існуючого контакту
    if len(args) < 3:
        return "Give me name, old phone and new phone please."

    name, old_phone, new_phone, *_ = args
    record = book.find(name)

    if record is None:
        raise AttributeError

    record.edit_phone(old_phone, new_phone)

    return "Contact updated."


@input_error
def show_phone(args, book):
    # Показуємо телефони контакту за іменем
    if len(args) < 1:
        raise IndexError

    name = args[0]
    record = book.find(name)

    if record is None:
        raise AttributeError

    phones = "; ".join(phone.value for phone in record.phones)

    return f"{name}: {phones}" if phones else "This contact has no phone numbers."


@input_error
def show_all(book):
    # Показуємо всі контакти
    if not book.data:
        return "No contacts."

    return "\n".join(str(record) for record in book.data.values())


@input_error
def add_birthday(args, book):
    # Додаємо день народження до контакту
    if len(args) < 2:
        return "Give me name and birthday please."

    name, birthday, *_ = args
    record = book.find(name)

    if record is None:
        raise AttributeError

    record.add_birthday(birthday)

    return "Birthday added."


@input_error
def show_birthday(args, book):
    # Показуємо день народження контакту
    if len(args) < 1:
        raise IndexError

    name = args[0]
    record = book.find(name)

    if record is None:
        raise AttributeError

    if not record.birthday:
        return "Birthday is not added for this contact."

    return f"{name}'s birthday: {record.birthday.value}"


@input_error
def birthdays(args, book):
    # Показуємо дні народження на найближчий тиждень
    upcoming_birthdays = book.get_upcoming_birthdays()

    if not upcoming_birthdays:
        return "No upcoming birthdays."

    return "\n".join(
        f"{item['name']}: {item['congratulation_date']}"
        for item in upcoming_birthdays
    )


def main():
    # Створюємо нову адресну книгу
    book = AddressBook()

    print("Welcome to the Jarvis assistant!")

    while True:
        # Отримуємо команду від користувача
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        # Привітання
        if command == "hello":
            print("How can I help you sir?")

        # Додати контакт або телефон
        elif command == "add":
            print(add_contact(args, book))

        # Змінити телефон контакту
        elif command == "change":
            print(change_contact(args, book))

        # Показати телефони контакту
        elif command == "phone":
            print(show_phone(args, book))

        # Показати всі контакти
        elif command == "all":
            print(show_all(book))

        # Додати день народження
        elif command == "add-birthday":
            print(add_birthday(args, book))

        # Показати день народження контакту
        elif command == "show-birthday":
            print(show_birthday(args, book))

        # Показати дні народження на найближчий тиждень
        elif command == "birthdays":
            print(birthdays(args, book))

        # Завершення роботи бота
        elif command in ["close", "exit"]:
            print("Good bye sir!")
            break

        # Якщо команда невідома
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()