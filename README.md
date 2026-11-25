# Лабораторная работа: Автоматизированное UI-тестирование веб-приложений с использованием Page Object Model

## 🎯 Цель работы

Изучить основы автоматизированного тестирования пользовательского интерфейса (UI), освоить паттерн проектирования Page Object Model (POM) и получить практические навыки работы с библиотекой Selenium WebDriver.

## 🛠 Технологический стек

- **Язык программирования:** Python 3.X
- **Автоматизация UI:** Selenium WebDriver
- **Тестирование:** unittest (встроенная библиотека)

## 📋 Техническое задание

Вам необходимо разработать проект автоматизированного UI-тестирования, демонстрирующий применение паттерна Page Object Model. Для реализации выберите **один** из предложенных веб-проектов:

1. **Simple Calculator:** [https://www.globalsqa.com/angularJs-protractor/SimpleCalculator/](https://www.globalsqa.com/angularJs-protractor/SimpleCalculator/)
2. **Search Filter:** [https://www.globalsqa.com/angularJs-protractor/SearchFilter/](https://www.globalsqa.com/angularJs-protractor/SearchFilter/)

Проект должен состоять из следующих логических компонентов:

### Модуль 1: Компоненты страниц (пакет `pages/`)

Реализуйте классы страниц (Page Objects), которые инкапсулируют логику взаимодействия с интерфейсом выбранного веб-приложения.

**Требования к Page Object:**
- Класс должен хранить локаторы элементов (кнопок, полей ввода, выпадающих списков) в виде приватных или защищенных переменных (кортежей `By`).
- Взаимодействие с элементами (ввод текста, клики, выбор опций) должно быть реализовано через понятные методы класса (например, `enter_first_number(num)`, `select_operation(op)`).
- Прямое обращение к драйверу (`driver.find_element`) из кода тестов **категорически запрещено**. Все действия должны выполняться через методы Page Object.

### Модуль 2: Автоматизированные тесты (пакет `tests/`)

Создайте тестовые сценарии на базе `unittest.TestCase` для верификации бизнес-логики веб-приложения.

**Требования к покрытиям:**
- Количество тестов определяется исходя из полного функционала выбранного приложения.
- Для **Simple Calculator**: тесты на все арифметические операции (`+`, `-`, `*`, `/`, `**`), граничные значения и обработку деления на ноль.
- Для **Search Filter**: тесты на поиск по различным критериям (Payee, Account, Type), проверку сброса фильтров и обработку пустых результатов поиска.
- Тесты должны быть независимыми: инициализация браузера происходит в `setUp()`, закрытие сессии — в `tearDown()`.

---

## 📂 Структура проекта и настройка

Рекомендуется использовать стандартную архитектуру папок для изоляции модулей и зависимостей:

```text
calculator_tests/
├── .gitignore
├── README.md
├── requirements.txt
├── pages/
│   ├── __init__.py
│   └── calculator_page.py
└── tests/
    ├── __init__.py
    └── test_calculator.py
```

### Быстрый запуск окружения

1. **Создайте и активируйте виртуальное окружение:**
   ```bash
   # В основной директории проекта
   python -m venv .venv
   # Windows: venv\Scripts\activate
   # Linux/macOS: source venv/bin/activate
   ```
2. **Установите зависимости:**
   ```bash
   python.exe pip install --upgrade pip
   # В первый раз:
   pip install selenium
   pip freeze > requirements.txt
   # Когда уже есть requirements.txt:
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
3. **Запустите тесты:**
   ```bash
   python -m unittest discover -s tests
   ```

## 📚 Полезные ссылки

- [Документация Selenium WebDriver](https://www.selenium.dev/documentation/)
- [Паттерн Page Object Model на Хабре](https://habr.com/ru/companies/otus/articles/888450/)
- [Документация модуля unittest](https://docs.python.org/3/library/unittest.html)
