from sqlmodel import Field, Relationship, SQLModel, create_engine, Session
from sqlalchemy.exc import *
from typing import List, Optional
from datetime import datetime


class PermissionGroupPermissionLink(SQLModel, table=True):
    __tablename__ = "permission_define"
    permission_group_id: int | None = Field(default=None, foreign_key="permission_group.id", primary_key=True)
    permission_id: int | None = Field(default=None, foreign_key="permission.id", primary_key=True, ondelete="RESTRICT")
    is_training: bool = False

    permission_group: "PermissionGroup" = Relationship(back_populates="permission_group_links")
    permission: "Permission" = Relationship(back_populates="permission_links")


class PermissionGroup(SQLModel, table=True):
    __tablename__ = "permission_group"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

    users: list["User"] = Relationship(back_populates="permission_group")
    permission_group_links: list["PermissionGroupPermissionLink"] | None = Relationship(
        back_populates="permission_group")


class Permission(SQLModel, table=True):
    __tablename__ = "permission"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # permision_group_id: int | None = Field(default=None, foreign_key="permission_group.id")
    permission_links: list[PermissionGroupPermissionLink] | None = Relationship(back_populates="permission")


class Log(SQLModel, table=True):
    __tablename__ = "log"
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(foreign_key="user.id")
    date_time: datetime | None
    # last_login_datatime: datetime | None
    ip_address: str

    user: "User" = Relationship(back_populates="log")


class User(SQLModel, table=True):
    __tablename__ = "user"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    mobile: str
    hashed_password: str
    age: int | None = Field(default=None, index=True)
    is_enabled: bool | None = True

    payment: List["Payment"] | None = Relationship(back_populates="user")
    enrollment: List["Enrollment"] | None = Relationship(back_populates="user")
    log: List["Log"] | None = Relationship(back_populates="user")
    permission_group_id: int | None = Field(default=None, foreign_key="permission_group.id")
    permission_group: PermissionGroup | None = Relationship(back_populates="users")


class Enrollment(SQLModel, table=True):
    __tablename__ = "enrollment"
    id: int | None = Field(default=None, primary_key=True)
    presenting_id: int | None = Field(foreign_key="presenting.id")
    student_id: int | None = Field(foreign_key="student.id")
    user_id: int | None = Field(foreign_key="user.id")

    presenting: "Presenting" = Relationship(back_populates="enrollment")
    student: "Student" = Relationship(back_populates="enrollment")
    user: "User" = Relationship(back_populates="enrollment")
    payment: List["Payment"] = Relationship(back_populates="enrollment")


class Course(SQLModel, table=True):
    __tablename__ = "course"
    id: int | None = Field(default=None, primary_key=True)
    lesson_id: int | None = Field(default=None, foreign_key="lesson.id")
    course_name: str | None = Field(default=None, index=True)
    # count_credit: int  | None = Field(default=None, index=True)

    presenting: list["Presenting"] = Relationship(back_populates="course")
    lesson: "Lesson" = Relationship(back_populates="course")


class Lesson(SQLModel, table=True):
    __tablename__ = "lesson"
    id: int | None = Field(default=None, primary_key=True)
    Category_id: int | None = Field(default=None, foreign_key="category.id")
    lesson_name: str | None = Field(default=None, index=True)
    count_credit: int | None = Field(default=None, index=True)

    course: list["Course"] = Relationship(back_populates="lesson")
    category: "Category" = Relationship(back_populates="lesson")


class Category(SQLModel, table=True):
    __tablename__ = "category"
    id: int | None = Field(default=None, primary_key=True)
    category_name: str = Field()

    lesson: list[Lesson] | None = Relationship(back_populates="category")


class Teacher(SQLModel, table=True):
    __tablename__ = "teacher"
    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=30)
    # fullname: Optional[str] = Field(default=None)
    email_address: str

    presenting: List["Presenting"] = Relationship(back_populates="teacher")
    credit: List["Credit"] = Relationship(back_populates="teacher")


class Credit(SQLModel, table=True):
    __tablename__ = "credit"
    id: int = Field(default=None, primary_key=True)
    teacher_id: int = Field(foreign_key="teacher.id")
    amount: float = Field(gt=0)  # مبلغ بستانکاری استاد
    date: datetime = Field(default=datetime.now)  # تاریخ بستانکاری استاد

    presenting_id: int | None = Field(foreign_key="presenting.id")

    payment_status: str = Field(default="Pending", max_length=20)  # وضعیت پرداخت (مثل

    teacher: Optional["Teacher"] = Relationship(back_populates="credit")
    presenting: Optional["Presenting"] = Relationship(back_populates="credit")


class Student(SQLModel, table=True):
    __tablename__ = "student"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=30)

    enrollment: List["Enrollment"] = Relationship(back_populates="student")
    survey: List["Survey"] = Relationship(back_populates="student")
    exam: List["Exam"] = Relationship(back_populates="student")
    rollcalls: List["RollCall"] = Relationship(back_populates="student")


class Schedule(SQLModel, table=True):
    __tablename__ = "schedule"
    id: int = Field(default=None, primary_key=True)
    start_time: datetime
    end_time: datetime
    presenting_id: int = Field(foreign_key="presenting.id")
    room_id: int = Field(foreign_key="room.id")
    is_canceled: bool = Field(default=False)
    is_extra: bool = Field(default=False)

    presenting: "Presenting" = Relationship(back_populates="schedule")
    room: "Room" = Relationship(back_populates="schedule")
    rollcalls: List["RollCall"] = Relationship(back_populates="schedule")


class RollCall(SQLModel, table=True):
    __tablename__ = "rollcall"
    id: int = Field(default=None, primary_key=True)
    schedule_id: int = Field(foreign_key="schedule.id")
    student_id: int = Field(foreign_key="student.id")
    status: str = Field(max_length=20)  # وضعیت (حاضر، غایب، دیرکرد)
    time: datetime = Field(default_factory=datetime.now)

    schedule: Schedule = Relationship(back_populates="rollcalls")
    student: Student = Relationship(back_populates="rollcalls")


class Exam(SQLModel, table=True):
    __tablename__ = "exam"
    id: int = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    presenting_id: int = Field(foreign_key="presenting.id")
    subject: str
    type_islocal: bool
    date: datetime
    score: Optional[float] = None  # امتیاز امتحان، می‌تواند مقدار نداشته باشد

    presenting: "Presenting" = Relationship(back_populates="exam")
    student: Student = Relationship(back_populates="exam")


class Building(SQLModel, table=True):
    __tablename__ = "building"
    id: int = Field(default=None, primary_key=True)
    building_name: str = Field(max_length=30)
    num_floors: int | None = Field(index=True)
    num_rooms: int | None = Field(index=True)
    capacity: int

    room: List["Room"] = Relationship(back_populates="building")


class Room(SQLModel, table=True):
    __tablename__ = "room"
    id: int = Field(default=None, primary_key=True)
    building_id: int = Field(foreign_key="building.id")
    name: str = Field(max_length=30)
    capacity: int

    building: "Building" = Relationship(back_populates="room")
    schedule: List["Schedule"] = Relationship(back_populates="room")


class Payment(SQLModel, table=True):
    __tablename__ = "payment"
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    enrollment_id: int = Field(foreign_key="enrollment.id")
    date_time: datetime
    status: int = Field(default=0)  # صفر: در انتظار    یک: پرداخت شده   دو: لغو شده
    price: int

    user: "User" = Relationship(back_populates="payment")
    enrollment: "Enrollment" = Relationship(back_populates="payment")


class SurveyCategory(SQLModel, table=True):
    __tablename__ = "surveycategory"
    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)

    survey: List["Survey"] = Relationship(back_populates="surveycategory")


class Survey(SQLModel, table=True):
    __tablename__ = "survey"
    id: int = Field(default=None, primary_key=True)
    score: int = Field(default=4)  # صفر:خیلی بد     یک:بد     دو:متوسط    سه:خوب    جهار:خیلی خوب
    presenting_id: int = Field(foreign_key="presenting.id")
    student_id: int = Field(foreign_key="student.id")
    surveycategory_id: int = Field(foreign_key="surveycategory.id")
    comment: str = Field(max_length=100)

    presenting: "Presenting" = Relationship(back_populates="survey")
    student: "Student" = Relationship(back_populates="survey")
    surveycategory: "SurveyCategory" = Relationship(back_populates="survey")


class Presenting(SQLModel, table=True):
    __tablename__ = "presenting"
    id: int = Field(default=None, primary_key=True)
    teacher_id: int = Field(foreign_key="teacher.id")
    course_id: int = Field(foreign_key="course.id")
    term: Optional[str] = Field(default=None)
    # price_presenting: Optional[int] = Field(default=None)
    public_student_price: int | None = Field(default=None)
    public_teacher_price: int | None = Field(default=None)
    private_student_price: int | None = Field(default=None)
    private_teacher_price: int | None = Field(default=None)

    teacher: "Teacher" = Relationship(back_populates="presenting")
    course: "Course" = Relationship(back_populates="presenting")
    enrollment: List["Enrollment"] = Relationship(back_populates="presenting")
    survey: List["Survey"] = Relationship(back_populates="presenting")
    schedule: List["Schedule"] = Relationship(back_populates="presenting")
    exam: List["Exam"] = Relationship(back_populates="presenting")
    credit: List["Credit"] = Relationship(back_populates="presenting")


class Calendar(SQLModel, table=True):
    __tablename__ = "calender"

    id: int = Field(default=None, primary_key=True)
    date: datetime = Field(unique=True)  # تاریخ هر روز
    day_of_week: str  # نام روز (مثلاً: دوشنبه)
    is_holiday: bool = Field(default=False)  # آیا تعطیل است؟


engine = create_engine("postgresql://postgres:salar0927305798@localhost:5432/postgres", echo=True)


# engine = create_engine("postgresql://postgres:1234@127.0.0.1:5432/postgres", echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def add_super_user():
    with Session(engine) as session:
        try:
            full_permission_group = PermissionGroup(name="full_permission_group")
            # permissions = [Permission(name=name) for name in ["get_user", "superuser"]]
            super_user = User(name="super_user2", mobile="05555555555",
                              hashed_password='$2b$12$3bCUlJ.TtD2m6TCGD0zv7OdZOBFUZs.Yz1uwfwIIf/y6OvdhGdVD2',
                              # "$2y$12$fMlP7vIBpLkqoshqF7faYuc6Fux2pSeuSad00w0wui6FlqGXs.h5K",
                              permission_group=full_permission_group)
            session.add(full_permission_group)

            session.add(super_user)
            session.commit()
            session.refresh(super_user)
        except IntegrityError as e:
            print("Integrity Error adding super user", e)
        except SQLAlchemyError as e:
            print("Error adding super user", e)


def main():
    create_db_and_tables()
    add_super_user()


if __name__ == "__main__":
    main()


