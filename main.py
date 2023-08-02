from collections import UserDict
from datetime import datetime
import csv
import os
import re


class Field:
    def __init__(self, value=None):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value


class Name(Field):
    pass


class Birthday(Field):
    @Field.value.setter
    def value(self, new_value):
        try:
            datetime.strptime(new_value, '%Y/%m/%d')
            self._value = new_value
        except ValueError:
            raise ValueError(
                "Incorrect date format for 'birthday'. Use 'YYYY/MM/DD' format.")


class Phone(Field):
    @Field.value.setter
    def value(self, new_value):
        if not re.match(r'^\d{11}$', new_value):
            raise ValueError(
                "Phone numbers must be 11-digit numerical strings.")
        self._value = new_value


class Record:
    def __init__(self, name, birthday=None, phones=None):
        self.name = Name(name)
        self.birthday = Birthday(birthday) if birthday else None
        self.phones = []
        if phones:
            for phone in phones:
                self.add_phone(phone)

    def add_name(self, name):
        self.name = Name(name)

    def show_name(self):
        return self.name.value

    def edit_name(self, new_name):
        self.name.value = new_name

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        if self.birthday:
            return self.birthday.value
        return None

    def edit_birthday(self, new_birthday):
        if not self.birthday:
            self.birthday = Birthday(new_birthday)
        else:
            self.birthday.value = new_birthday

    def del_birthday(self):
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def show_phones(self):
        return [phone.value for phone in self.phones]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                break

    def delete_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def delete_record(self, name):
        if name in self.data:
            del self.data[name]

    def show_all_records(self):
        if not self.data:
            print("[-] No records found in the address book.")
        else:
            for i, (name, record) in enumerate(self.items(), start=1):
                print(f'{i}. {name}, ', end='')
                if record.birthday:
                    print(f'{record.birthday.value}, ', end='')
                print('Phones: ', end='')
                phones_str = "; ".join(
                    [f"[{i + 1}] {phone.value}" for i, phone in enumerate(record.phones)])
                print(phones_str)

    def search_record(self, query):
        found_records = []
        for name, record in self.data.items():
            if query.lower() in name.lower():
                found_records.append(name)
            for phone in record.phones:
                if query == phone.value:
                    found_records.append(name)
        return found_records

    def save_to_csv(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Name', 'Birthday', 'Phones']
            writer = csv.DictWriter(
                csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for record in self.data.values():
                phones_list = [phone.value for phone in record.phones]
                writer.writerow(
                    {'Name': record.name.value, 'Birthday': record.birthday.value if record.birthday else "", 'Phones': phones_list})

    def load_from_csv(self, filename):
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                name = row['Name']
                birthday = row['Birthday']
                phones_str = row['Phones']
                phones_list = eval(phones_str)
                record = Record(name)
                if birthday:
                    record.birthday = Birthday(birthday)
                for phone in phones_list:
                    record.add_phone(phone)
                self.add_record(record)


class Bot:
    exit_commands = ["q", "quit", "close", "exit"]

    def __init__(self):
        self.address_book = AddressBook()
        self.address_book.load_from_csv('contacts.csv')

        self.commands = {
            'help': self.handle_help,
            'hello': self.handle_hello,
            'show all': self.handle_show_all,
            'show phones': self.handle_show_phones,
            'show birthday': self.handle_show_bday,
            'days to birthday': self.handle_d2b,
            'add': self.handle_add,
            'change': self.handle_change,
            'delete': self.handle_delete,
            'search name': self.handle_search_name,
        }

    def parse_input(self, input_string, commands):
        input_string_lower = input_string.lower()

        command = None
        for key in commands:
            if input_string_lower.startswith(key.lower()):
                command = key
                break

        if command is None:
            return None, None, None, None

        parsed_name = None
        parsed_birthday = None
        parsed_phones = []

        rest_of_string = input_string[len(command):].strip()

        arguments = re.findall(r'\".*?\"|\'.*?\'|\S+', rest_of_string)
        arguments = [arg.strip('"\'') if arg[0]
                     in '\'"' else arg for arg in arguments]

        for i, arg in enumerate(arguments):
            if re.match(r'^[a-zA-Z\- ]+$', arg):
                parsed_name = arg
            elif re.match(r'^\d{4}/\d{2}/\d{2}$', arg):
                parsed_birthday = arg
            elif re.match(r'^\d{11}$', arg):
                parsed_phones.append(arg)

        return command, parsed_name, parsed_birthday, parsed_phones

    def handle_help(self, *args):

        print('[+] Usage: <command> <name> <birthday/phones>\n[+] Available commands: ')
        for key in self.commands:
            print(key)
        for exit_command in self.exit_commands:
            print(exit_command)

    def handle_hello(self, *args):
        print('[+] Hi there!')

    def handle_show_all(self, *args):
        self.address_book.show_all_records()

    def handle_show_phones(self, *args):
        if args:
            contactname = args[0]
            if contactname in self.address_book.data:
                record = self.address_book.data[contactname]
                phones_str = ", ".join(
                    [phone.value for phone in record.phones])
                print(f"[+] Phone numbers for {contactname}: {phones_str}")
            else:
                print("[-] Record not found.")
        else:
            print("[-] Missing contact name.")

    def handle_show_bday(self, *args):
        if args:
            contactname = args[0]
            if contactname in self.address_book.data:
                record = self.address_book.data[contactname]
                print(
                    f"[+] {contactname}'s birthday is: {record.show_birthday()}")
            else:
                print("[-] Record not found.")
        else:
            print("[-] Missing contact name.")

    def handle_d2b(self, name, *_):
        if not name:
            print("[-] Missing contact name.")

        if name in self.address_book.data:
            record = self.address_book.data[name]
            if record.birthday:
                today = datetime.now().date()
                next_birthday = datetime.strptime(
                    record.birthday.value, "%Y/%m/%d").date().replace(year=today.year)

                if today > next_birthday:
                    next_birthday = next_birthday.replace(year=today.year + 1)

                days_remaining = (next_birthday - today).days
                print(f"[+] {name}'s birthday is in {days_remaining} days.")
            else:
                print(f"[-] {name} does not have a birthday specified.")
        else:
            print(f"[-] Contact '{name}' not found in the address book.")

    def handle_add(self, name, birthday, phones):
        if not name:
            print("[-] Missing required 'name' field.")

        if birthday:
            try:
                datetime.strptime(birthday, '%Y/%m/%d')
            except ValueError:
                print(
                    "[-] Incorrect date format for 'birthday'. Use 'YYYY/MM/DD' format.")

        if phones:
            for phone in phones:
                if not re.match(r'^\d{11}$', phone):
                    print("[-] Phone numbers must be 11-digit numerical strings.")

        if name in self.address_book.data:
            print("[-] Name already exists.")

        record = Record(name, birthday, phones)
        self.address_book.add_record(record)
        print(f"[+] Contact '{name}' added successfully!")

    def handle_change(self, name, birthday, phones):
        if not name:
            print("[-] Missing required 'name' field.")

        existing_record = self.address_book.data.get(name)

        if existing_record:
            if birthday:
                try:
                    datetime.strptime(birthday, '%Y/%m/%d')
                    existing_record.birthday = Birthday(birthday)
                except ValueError:
                    print(
                        "[-] Incorrect date format for 'birthday'. Use 'YYYY/MM/DD' format.")

            if phones:
                for phone in phones:
                    if not re.match(r'^\d{11}$', phone):
                        return "[-] Phone numbers must be 11-digit numerical strings."
                existing_record.phones = [Phone(phone) for phone in phones]

            print(f"[+] Contact '{name}' changed successfully!")
        else:
            print("[-] Record not found.")

    def handle_delete(self, *args):
        if args:
            contactname = args[0]
            if contactname in self.address_book.data:
                self.address_book.delete_record(contactname)
                print(f"[+] Deleted record for {contactname}.")
            else:
                print("[-] Record not found.")
        else:
            print("[-] Missing contact name. Usage: delete <name>")

    def handle_search_name(self, *args):
        if args:
            query = args[0]
            found_records = self.address_book.search_record(query)
            if found_records:
                for name in found_records:
                    record = self.address_book.data[name]
                    print(f'{name}, ', end='')
                    if record.birthday:
                        print(f'{record.birthday.value}, ', end='')
                    print('Phones: ', end='')
                    phones_str = "; ".join(
                        [f"[{i + 1}] {phone.value}" for i, phone in enumerate(record.phones)])
                    print(phones_str)
            else:
                print("[-] No matching records found.")
        else:
            print("[-] Missing search query. Usage: search <query>")


def input_error(func):
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError):
            return "[-] Invalid input. Use 'help' for assistance."
        except Exception as e:
            return "[-] Exception: " + str(e)
    return wrap


@ input_error
def main():
    if not os.path.exists('contacts.csv'):
        with open('contacts.csv', 'w', newline=''):
            pass
    bot = Bot()
    bot.address_book.load_from_csv('contacts.csv')
    try:
        while True:
            try:
                contact_input = input(">>> ")
            except KeyboardInterrupt:
                break

            if contact_input.lower() in bot.exit_commands:
                break

            os.system('cls' if os.name == 'nt' else 'clear')
            command, name, birthday, phones = bot.parse_input(
                contact_input, bot.commands.keys())
            handler = bot.commands.get(command)
            print(
                f'[i] Debug: cmd: {command}; ars: {name}, {birthday}, {phones}')

            if handler:
                result = handler(name, birthday, phones)
                if result:
                    print(result)
            else:
                print("[-] Command not recognized. Try 'help'.")
    finally:
        bot.address_book.save_to_csv('contacts.csv')
        print("\n[+] Bye!")


if __name__ == "__main__":
    main()
