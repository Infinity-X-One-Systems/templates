"""Education Platform Engine – courses, enrollment, progress tracking, and certificates."""
from __future__ import annotations

import uuid
from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Course(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    instructor_id: str
    modules: List[str]
    duration_hours: float
    level: str


class Enrollment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    course_id: str
    progress: List[Optional[float]] = Field(default_factory=list)
    status: str = "active"


class Certificate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    enrollment_id: str
    student_id: str
    course_id: str
    issue_date: str
    credential_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class EducationPlatformEngine:
    """Manages courses, student enrollments, progress, and certificate issuance."""

    def __init__(self) -> None:
        self._courses: Dict[str, Course] = {}
        self._enrollments: Dict[str, Enrollment] = {}

    def create_course(
        self,
        title: str,
        instructor_id: str,
        modules: List[str],
        duration_hours: float,
        level: str,
    ) -> Course:
        course = Course(
            title=title,
            instructor_id=instructor_id,
            modules=modules,
            duration_hours=duration_hours,
            level=level,
        )
        self._courses[course.id] = course
        return course

    def enroll_student(self, student_id: str, course_id: str) -> Enrollment:
        course = self._get_course(course_id)
        enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id,
            progress=[None] * len(course.modules),
        )
        self._enrollments[enrollment.id] = enrollment
        return enrollment

    def record_progress(
        self, enrollment_id: str, module_index: int, score: float
    ) -> Enrollment:
        enrollment = self._get_enrollment(enrollment_id)
        if module_index < 0 or module_index >= len(enrollment.progress):
            raise IndexError(f"module_index {module_index} out of range")
        enrollment.progress[module_index] = score
        if all(s is not None for s in enrollment.progress):
            enrollment.status = "completed"
        return enrollment

    def calculate_completion_rate(self, course_id: str) -> float:
        enrollments = [e for e in self._enrollments.values() if e.course_id == course_id]
        if not enrollments:
            return 0.0
        completed = sum(1 for e in enrollments if e.status == "completed")
        return round(completed / len(enrollments), 4)

    def generate_certificate(self, enrollment_id: str) -> Certificate:
        enrollment = self._get_enrollment(enrollment_id)
        if enrollment.status != "completed":
            raise ValueError("Enrollment is not yet completed")
        cert = Certificate(
            enrollment_id=enrollment_id,
            student_id=enrollment.student_id,
            course_id=enrollment.course_id,
            issue_date=date.today().isoformat(),
        )
        return cert

    def _get_course(self, course_id: str) -> Course:
        if course_id not in self._courses:
            raise KeyError(f"Course {course_id} not found")
        return self._courses[course_id]

    def _get_enrollment(self, enrollment_id: str) -> Enrollment:
        if enrollment_id not in self._enrollments:
            raise KeyError(f"Enrollment {enrollment_id} not found")
        return self._enrollments[enrollment_id]


if __name__ == "__main__":
    engine = EducationPlatformEngine()
    course = engine.create_course("Python 101", "INST001", ["Basics", "OOP", "Testing"], 10.0, "beginner")
    print(f"Course created: {course.title} (id={course.id})")
