from datetime import datetime, timedelta
from typing import Optional

from src.utils.time import utcnow


def compute_deadline (started_at :datetime ,time_limit_minutes :int )->datetime :
    return started_at +timedelta (minutes =max (0 ,int (time_limit_minutes or 0 )))

def compute_remaining_seconds (
started_at :datetime ,
time_limit_minutes :int ,
now :Optional [datetime ]=None ,
)->int :
    deadline =compute_deadline (started_at ,time_limit_minutes )
    current =now or utcnow ()
    return max (0 ,int ((deadline -current ).total_seconds ()))

def format_seconds (seconds :int )->str :
    seconds =max (0 ,int (seconds or 0 ))
    minutes ,secs =divmod (seconds ,60 )
    return f"{minutes :02d}:{secs :02d}"
