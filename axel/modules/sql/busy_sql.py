import threading

from sqlalchemy import Column, UnicodeText, Boolean, Integer

from axel.modules.sql import BASE, SESSION


class BUSY(BASE):
    __tablename__ = "busy_users"

    user_id = Column(Integer, primary_key=True)
    is_busy = Column(Boolean)
    reason = Column(UnicodeText)

    def __init__(self, user_id, reason="", is_busy=True):
        self.user_id = user_id
        self.reason = reason
        self.is_busy = is_busy

    def __repr__(self):
        return "busy_status for {}".format(self.user_id)


BUSY.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()

BUSY_USERS = {}


def is_busy(user_id):
    return user_id in BUSY_USERS


def check_busy_status(user_id):
    if user_id in BUSY_USERS:
        return True, BUSY_USERS[user_id]
    return False, ""


def set_busy(user_id, reason=""):
    with INSERTION_LOCK:
        curr = SESSION.query(BUSY).get(user_id)
        if not curr:
            curr = BUSY(user_id, reason, True)
        else:
            curr.is_busy = True
            curr.reason = reason

        BUSY_USERS[user_id] = reason

        SESSION.add(curr)
        SESSION.commit()


def rm_busy(user_id):
    with INSERTION_LOCK:
        curr = SESSION.query(BUSY).get(user_id)
        if curr:
            if user_id in BUSY_USERS:  # sanity check
                del BUSY_USERS[user_id]

            SESSION.delete(curr)
            SESSION.commit()
            return True

        SESSION.close()
        return False


def __load_busy_users():
    global BUSY_USERS
    try:
        all_busy = SESSION.query(BUSY).all()
        BUSY_USERS = {user.user_id: user.reason for user in all_busy if user.is_busy}
    finally:
        SESSION.close()


__load_busy_users()
