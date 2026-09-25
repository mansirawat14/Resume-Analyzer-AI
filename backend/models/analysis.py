from datetime import datetime


class Analysis:
    def __init__(
        self,
        user_id=None,
        resume_score=0,
        ats_score=0,
        job_match=0,
        resume_health=0
    ):
        self.user_id = user_id
        self.resume_score = resume_score
        self.ats_score = ats_score
        self.job_match = job_match
        self.resume_health = resume_health
        self.created_at = datetime.now()