from datetime import datetime
import os
import re
from db_actions import *
from spacy_llm.util import assemble


"""
Define environment variable for OpenAI API key: os.environ["OPENAI_API_KEY"] = "your_key_here"
"""

nlp = assemble("config.cfg")
test_d = ["Покажи список 4Б", "Я хочу отримати список усіх учнів з 10А.", "Покажи список учнів з 10Б.", "Хто навчається в 10А?",
          "Скільки учнів навчається в 6А?", "Скільки учнів в 1Б?", "Які учні навчаються в 9А?",
          "Хто викладає Англійську мову?", "Скільки вчителів в школі?", "Які вчителі викладають Математику?",
          "Покажи розклад 10А на понеділок.", "Покажи розклад 10Б на середу.", "Покажи розклад 11А на четвер.",
          "Які уроки у 3А на понеділок?", "Які заняття у 8Б в середу?", "Розклад 4А на четвер",
          "Скільки учнів в школі?", "Скільки вчителів в школі?"]


def class_students_answer(ents):
    class_ = [ent.text.upper() for ent in ents if ent.label_ == 'код класу'][0]
    students = get_students_by_class(class_)
    print(f"Ось список учнів {class_} класу:\n")
    for student in students:
        print("\t", student)


def subject_teachers_answer(ents):
    if ents == []:
        print("Не вказано предмет, повторіть запит")
        return
    subject = [ent.text.capitalize() for ent in ents if ent.label_ == 'шкільний предмет'][0]
    like_filter = f"%{subject[:5]}%{subject.split(' ')[1][1:3]}%" if ' ' in subject else f"%{subject[:5]}%"
    teachers = get_teacher_by_subject(like_filter, like=True)
    if teachers:
        print(f"{subject} викладає: {teachers}")
    else:
        print(f"{subject} не викладається в цій школі")

def schedule_answer(ents):
    class_ = [ent.text.upper() for ent in ents if ent.label_ == 'код класу']
    day = [ent for ent in ents if ent.label_ == 'день тижня']

    if not class_:
        print("Не вказано клас, повторіть запит")
        return
    if not day:
        print("Не вказано день тижня, повторіть запит")
        return

    day_lemma = day[0].lemma_.capitalize()
    schedule = get_class_schedule_by_day(class_[0], day_lemma)
    if schedule:
        print(f"Розклад уроків {class_[0]} класу на {day[0].text}:")
        for i in schedule:
            print("\t", i)
    else:
        print(f"У цей день у цьому класі немає занять")

def add_student():
    while True:
        name_surname = input('Введіть ім\'я та прізвище нового учня: ')
        if len(name_surname.split()) == 2:
            break
        print("Ім'я та прізвище не розпізнано, повторіть введення")

    while True:
        try:
            birth_date = datetime.strptime(input('Введіть дату народження учня (ДД.ММ.РРРР): '), '%d.%m.%Y')
            break
        except ValueError:
            print('Неправильний формат дати, повторіть введення')

    while True:
        class_ = input('Введіть клас, в якому від навчатиметься: ')
        if re.match(r'\d{1,2}[А-Яа-я]', class_):
            break
        print('Неправильний формат класу, повторіть введення')

    try:
        add_new_student(name_surname.split()[0], name_surname.split()[1], birth_date, class_)
        print(f'{name_surname} успішно доданий до класу {class_}')
    except ValueError:
        print('Введеного класу не існує, спробуйте ще раз')

while True:
    usr_input = input('Ви: ')
    if usr_input == 'вихід':
        break
    doc = nlp(usr_input)
    action = doc.cats
    ents = doc.ents
    if action['cписок учнів класу']:
        class_students_answer(ents)
    elif action['кількість всіх учнів']:
        print(f"У школі {len(get_all(Students))} учнів")
    elif action['вчитель предмету']:
        subject_teachers_answer(ents)
    elif action['кількість всіх вчителів']:
        print(f"У школі {len(get_all(Teachers))} вчителів")
    elif action['розклад уроків класу']:
        schedule_answer(ents)
    elif action['кількість учнів класу']:
        class_ = [ent.text.upper() for ent in ents if ent.label_ == 'код класу'][0]
        print(f"У {class_} класі навчається {count_students_by_class(class_)} учнів")
    elif action['додати учня']:
        add_student()
    else:
        print('Не зрозумів, перефразуйте')

