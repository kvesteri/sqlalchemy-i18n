import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import mapper, object_session
from sqlalchemy.schema import UniqueConstraint


def get_locale():
    return u'en'


class Translatable(object):
    language = sa.Column(sa.Unicode(10), primary_key=True)

    def mass_update(self, key, value):
        query = (
            object_session(self).query(self.__class__)
            .filter(self.__class__.id == self.id)
        )
        for obj in query:
            setattr(obj, key, value)

    @declared_attr
    def __mapper_cls__(cls):
        def _map(cls, *args, **kwargs):
            args[0].append_constraint(
                UniqueConstraint(args[0].c.id, args[0].c.language)
            )
            mp = mapper(cls, *args, **kwargs)
            return mp
        return _map


def translated_session(session, locale='en'):
    session.locale = locale
    return session
