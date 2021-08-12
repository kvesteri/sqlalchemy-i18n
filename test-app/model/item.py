from model.sqlalchemy import db
from sqlalchemy_i18n import translation_base, I18IdColumn, RuneTranslatable

from sqlalchemy import sql

from model.db_types import UTCDateTime


class Item(db.Model, RuneTranslatable):
    """
    Represents a resource that is loggable.
    Can include medications, symptoms influences.

    """

    __tablename__ = "items"
    __table_args__ = (
        db.Index("index_items_on_disabler_id", "disabler_id"),
        db.Index("index_items_on_rune_classification", "rune_classification"),
        db.Index("index_items_on_study_id", "study_id"),
    )

    id_seq = db.Sequence("items_id_seq", metadata=db.metadata)
    id = db.Column(db.BigInteger, server_default=id_seq.next_value(), primary_key=True)
    name = db.Column(db.String)
    active = db.Column(db.Boolean, server_default=sql.expression.true())
    _global = db.Column("global", db.Boolean, server_default=sql.expression.true())
    created_at = db.Column(UTCDateTime, nullable=False)
    updated_at = db.Column(UTCDateTime, nullable=False)
    item_type = db.Column(db.String)
    disabler_id = db.Column(db.BigInteger)
    study_id = db.Column(db.BigInteger)
    rune_classification = db.Column(db.String)


class ItemTranslation(translation_base(Item, create_columns=False)):
    __tablename__ = "item_translations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_id = I18IdColumn('item_id', db.BigInteger, parent_column='id')
    name = db.Column(db.String())
    created_at = db.Column(db.DateTime())
    updated_at = db.Column(db.DateTime())
