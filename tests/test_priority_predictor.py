from src.ai.priority_predictor import AIPriorityPredictor
from src.database.tables import TicketPriority

predictor = AIPriorityPredictor()


def test_predicts_critical_priority_for_system_outage() -> None:
    # priority = predictor.predict(title="Server is down", description="The university systems are unavailable and users cannot access the platform")
    # priority = predictor.predict(title="آموزشیار قطع است", description="سامانه آموزشیار قطع است و هیچ کس نمیتواند وارد شود")
    priority = predictor.predict(title="آموزشیار قطع است", description="سامانه آموزشیار برای همه دانشجویان قطع است")
    assert priority.priority == TicketPriority.CRITICAL

def test_predicts_warning_priority_for_repeated_access_problems() -> None:
    # priority = predictor.predict(title="VPN issue", description="I am unable to connect to the VPN and need access to internal resources")
    priority = predictor.predict(title="مشکل اینترنت", description="یرای دسترسی به اطلاعات درسی، اینترنت دانشگاه متصل نمیشود.")
    assert priority.priority == TicketPriority.WARNING

def test_predicts_normal_priority_for_simple_account_requests() -> None:
    # priority = predictor.predict(title="Password reset", description="I forgot my password and need to reset it")
    priority = predictor.predict(title="تغییر رمز", description="رمز عبور خود را فراموش کردم و میخواهم آن را عوض کنم.")
    assert priority.priority == TicketPriority.NORMAL
