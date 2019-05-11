from ..api import Base
from sqlalchemy import ForeignKey, Column, UniqueConstraint, String

class HashCode(Base):

    __tablename__ = "submission_hash"
    __table_args = (UniqueConstraing('hash', 'assignment_id', 'student_id'),)

    id = Column(String(32), primary_key=True, default=new_uuid)
    assignment_id = Column(String(32), ForeignKey('assignment.id'))
    student_id = Column(String(128), ForeignKey('student.id'))

    hash = Column(String(32))

    def to_dict(self):
        return {
            "id": self.id,
            "student": self.student_id,
            "assignment": self.assignment_id,
            "hash": self.hash
        }

    def __repr__(self):
        return "Hash {} for student {} for assignment {}".format(self.hash, self.student_id, self.assignment_id)

    