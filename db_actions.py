
from sqlalchemy import create_engine, Column, Integer, String, Sequence, text, DateTime, ForeignKey, insert
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

db_url = 'sqlite:///identifier.sqlite'
engine = create_engine(db_url, echo=False)
Base = declarative_base()

class Classes(Base):
    __tablename__ = 'Classes'
    class_id = Column(Integer, Sequence('class_id_seq'), primary_key=True)
    class_name = Column(String(50))

class Students(Base):
    __tablename__ = 'Students'
    student_id = Column(Integer, Sequence('student_id_seq'), primary_key=True, autoincrement=True)
    name = Column(String(50))
    surname = Column(String(50))
    birth_date = Column(DateTime)
    class_id = Column(Integer, ForeignKey('Classes.class_id'))

    def __repr__(self):
        return f'{self.name} {self.surname}'

class Subjects(Base):
    __tablename__ = 'Subjects'
    subject_id = Column(Integer, Sequence('subject_id_seq'), primary_key=True)
    subject_name = Column(String(50))


class Teachers(Base):
    __tablename__ = 'Teachers'
    teacher_id = Column(Integer, Sequence('teacher_id_seq'), primary_key=True)
    teacher_name = Column(String(50))
    subject_id = Column(Integer, ForeignKey('Subjects.subject_id'))
    teacher_surname = Column(String(50))

    def __repr__(self):
        return f'{self.teacher_name} {self.teacher_surname}'

class Schedule(Base):
    __tablename__ = 'Schedule'
    schedule_id = Column(Integer, Sequence('schedule_id_seq'), primary_key=True)
    class_id = Column(Integer, ForeignKey('Classes.class_id'))
    subject_id = Column(Integer, ForeignKey('Subjects.subject_id'))
    teacher_id = Column(Integer, ForeignKey('Teachers.teacher_id'))
    room = Column(String(10))
    day = Column(String(20))
    time = Column(String(8))

    def __repr__(self):
        return f'{self.class_id} {self.subject_id} {self.teacher_id} {self.room} {self.day} {self.time}'

Session = sessionmaker(bind=engine)
session = Session()


def get_students_by_class(class_name):
    result = session.query(Students).join(Classes).filter(Classes.class_name == class_name).all()
    return result

def count_students_by_class(class_name):
    result = session.query(Students).join(Classes).filter(Classes.class_name == class_name).count()
    return result


def get_teacher_by_subject(subject_name, like=False):
    if like:
        result = session.query(Teachers).join(Subjects).filter(Subjects.subject_name.like(subject_name)).all()
    else:
        result = session.query(Teachers).join(Subjects).filter(Subjects.subject_name == subject_name).all()
    return result

def get_all(table):
    result = session.query(table).all()
    return result

def get_filtered(table, column, value, filter_table=None):
    if filter_table:
        result = session.query(table).join(filter_table).filter(column == value).all()
    else:
        result = session.query(table).filter(column == value).all()
    return result

def get_class_schedule_by_day(class_name, day):
    result = (session.query(Subjects.subject_name, Classes.class_name, Schedule.time, Teachers.teacher_name, Teachers.teacher_surname)
              .join(Classes)
              .join(Subjects)
              .join(Teachers)
              .filter(Classes.class_name == class_name).filter(Schedule.day == day)
              .all())

    if not result:
        return None

    reply_str = [f"{i[0]} о {i[2]}. Вчитель: {i[3]} {i[4]}." for i in result]
    return reply_str

def add_new_student(name, surname, birth_date, class_):
    try:
        class_id = session.query(Classes.class_id).filter(Classes.class_name == class_).one()
        session.execute(insert(Students).values(name=name, surname=surname, birth_date=birth_date, class_id=class_id[0]))
        session.commit()
    except:
        raise ValueError("Клас не знайдено")
