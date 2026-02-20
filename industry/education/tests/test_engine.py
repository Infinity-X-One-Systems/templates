"""Tests for EducationPlatformEngine."""
import pytest
from src.engine import EducationPlatformEngine


@pytest.fixture
def engine():
    return EducationPlatformEngine()


def test_create_course(engine):
    course = engine.create_course(
        "Data Science Fundamentals", "INST42", ["Stats", "Python", "ML"], 20.0, "intermediate"
    )
    assert course.title == "Data Science Fundamentals"
    assert len(course.modules) == 3
    assert course.level == "intermediate"


def test_enroll_student(engine):
    course = engine.create_course("Web Dev 101", "INST01", ["HTML", "CSS", "JS"], 12.0, "beginner")
    enrollment = engine.enroll_student("STU001", course.id)
    assert enrollment.student_id == "STU001"
    assert enrollment.course_id == course.id
    assert enrollment.status == "active"
    assert len(enrollment.progress) == 3


def test_record_progress(engine):
    course = engine.create_course("Algebra", "INST05", ["Module1", "Module2"], 8.0, "beginner")
    enrollment = engine.enroll_student("STU002", course.id)
    updated = engine.record_progress(enrollment.id, 0, 88.0)
    assert updated.progress[0] == 88.0
    assert updated.status == "active"
    engine.record_progress(enrollment.id, 1, 92.0)
    assert enrollment.status == "completed"


def test_generate_certificate(engine):
    course = engine.create_course("Cloud Basics", "INST10", ["Intro"], 5.0, "beginner")
    enrollment = engine.enroll_student("STU003", course.id)
    engine.record_progress(enrollment.id, 0, 95.0)
    cert = engine.generate_certificate(enrollment.id)
    assert cert.student_id == "STU003"
    assert cert.course_id == course.id
    assert cert.credential_id is not None
    assert cert.issue_date is not None
