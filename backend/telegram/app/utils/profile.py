import re


class ValidateUserInput:

    def validate_field(self, type, field):
        field_to_update = {
            'username': self.validate_username(field),
            'email': self.validate_email(field),
            'first_name': self.validate_first_name(field),
            'last_name': self.validate_last_name(field),
            'patronymic': self.validate_patronymic(field),
            'phone_number': self.validate_phone(field),
            'birthday': self.format_birthday(field),
            'balance': self.validate_balannce(field),
            'custom_name': self.validate_custom_name(field),
            'note': self.validate_note(field),
            'amount': self.validate_amount(field),
            'datetime': self.validate_datetime(field),
            'comment': self.validate_comment(field),
            'location': self.validate_location(field),
            'vendor': self.validate_vendor(field),
            'source': self.validate_source(field),
        }
        return field_to_update[type]

    def validate_source(self, value):
        if not (0 <= len(value) <= 99):
            return False, ValueError("Источник транзакции не должен быть пуст и при этом должен содержать до 99 символов.")
        return True, value

    def validate_vendor(self, value):
        if not (0 <= len(value) <= 99):
            return False, ValueError("Адресат транзакции не должен быть пуст и при этом должен содержать до 99 символов.")
        return True, value

    def validate_location(self, value):
        if not (0 <= len(value) <= 99):
            return False, ValueError("Запись местоположения совершения транзакции не должно быть пустым и при этом должно содержать до 99 символов.")
        return True, value

    def validate_comment(self, value):
        if not (0 <= len(value) <= 99):
            return False, ValueError("Комментарий не должен быть пуст и при этом должен содержать до 99 символов.")
        return True, value

    def validate_datetime(self, value):
        from datetime import datetime
        try:
            if len(value.split()) == 1:
                # Если указана только дата
                date_str = value.strip()
                datetime_obj = datetime.strptime(date_str, "%d.%m.%Y")
                # Устанавливаем время на полдень
                datetime_obj = datetime_obj.replace(hour=12, minute=0, second=0, microsecond=0)
            else:
                # Если указана дата и время
                date_str, time_str = value.split()
                datetime_str = f"{date_str} {time_str}"
                datetime_obj = datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")

            return True, datetime_obj.strftime("%Y-%m-%d %H:%M:%S.%f")

        except ValueError:
            return False, ValueError(
                "Некорректный формат даты или времени. Пожалуйста, используйте ДД.ММ.ГГГГ для даты и ЧЧ:ММ для времени.")

    def validate_amount(self, value):
        if not bool(re.match(r'^-?\d+(\.\d+)?$', value)):
            return False, ValueError("Сумма транзакции может содержать только цифры и знак точки (199.99).")
        return True, float(value)

    def validate_note(self, value):
        if not (0 <= len(value) <= 99):
            return False, ValueError("Кастомное имя должно содержать до 99 символов.")
        return True, value

    def validate_custom_name(self, value):
        if not (2 <= len(value) <= 64):
            return False, ValueError("Кастомное имя должно содержать от 2 до 64 символов.")
        if not re.match(r'^[A-Za-zА-Яа-яЁё\s-]+$', value):
            return False, ValueError("Кастомное имя может содержать только буквы, пробелы и дефисы.")
        return True, value

    def validate_balannce(self, value):
        if not bool(re.match(r'^-?\d+(\.\d+)?$', value)):
            return False, ValueError("Баланс может содержать только цифры и знак точки (199.99).")
        return True, float(value)

    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9]{1,64}$', value):
            return False, ValueError("Пользовательское имя должно содержать только латинские буквы и цифры, длина от 1 до 64 символов.")
        return True, value

    def validate_email(self, value):
        if len(value) > 120:
            return False, ValueError("Email должен содержать не более 120 символов.")
        if len(value) < 2:
            return False, ValueError("Email должен содержать не менее 2 символов.")
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
            return False, ValueError("Некорректный формат email.")
        return True, value

    def validate_first_name(self, value):
        if not (2 <= len(value) <= 64):
            return False, ValueError("Имя должно содержать от 2 до 64 символов.")
        if not re.match(r'^[A-Za-zА-Яа-яЁё\s-]+$', value):
            return False, ValueError("Имя может содержать только буквы, пробелы и дефисы.")
        return True, value

    def validate_last_name(self, value):
        if not (2 <= len(value) <= 64):
            return False, ValueError("Фамилия должна содержать от 2 до 64 символов.")
        if not re.match(r'^[A-Za-zА-Яа-яЁё\s-]+$', value):
            return False, ValueError("Фамилия может содержать только буквы, пробелы и дефисы.")
        return True, value

    def validate_patronymic(self, value):
        if not (2 <= len(value) <= 64):
            return False, ValueError("Отчество должно содержать от 2 до 64 символов.")
        if not re.match(r'^[A-Za-zА-Яа-яЁё\s-]+$', value):
            return False, ValueError("Отчество может содержать только буквы, пробелы и дефисы.")
        return True, value

    def validate_phone(self, value):
        pattern = re.compile(r'^\+?[78]?\d{10}$')
        if not pattern.match(value):
            return False, ValueError("Номер телефона должен быть в формате: +7 (123) 456-78-90 или 89131234567.")
        return True, value

    def format_birthday(self, value):
        try:
            from datetime import datetime
            birthday = datetime.strptime(value, "%d.%m.%Y")
            return True, birthday.strftime("%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            return False, ValueError("Дата рождения должна быть в формате: ДД.ММ.ГГГГ.")
