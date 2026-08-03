from src.ai.classifier import AIClassifier

classifier = AIClassifier()


def test_users_support_classifier():
    ticket = "نمیتوانم رمز عبور خود را تغغیر دهم"
    department_id, category_id = classifier.classify(ticket)

    assert department_id == 1
    assert category_id == 1


def test_network_classifier():
    ticket = "اینترنت دانشگاه قطع شده و کار نمیکند"
    department_id, category_id = classifier.classify(ticket)

    assert department_id == 2
    assert category_id == 2


def test_university_systems_classifier():
    ticket = "هنگام انتخاب واحد سامانه آموزشیار خطا می‌دهد"
    department_id, category_id = classifier.classify(ticket)

    assert department_id == 3
    assert category_id == 5
