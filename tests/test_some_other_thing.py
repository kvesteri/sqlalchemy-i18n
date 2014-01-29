import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.relationships import RelationshipProperty
from tests import TestCase


class ProxyDict(object):
    def __init__(self, parent, collection_name, mapping_attr):
        self.parent = parent
        self.collection_name = collection_name
        self.mapping_attr = mapping_attr
        self.child_class = mapping_attr.class_
        self.key_name = mapping_attr.key
        self.cache = {}

    @property
    def collection(self):
        return getattr(self.parent, self.collection_name)

    def keys(self):
        descriptor = getattr(self.child_class, self.key_name)
        return [x[0] for x in self.collection.values(descriptor)]

    def __contains__(self, key):
        if key in self.cache:
            return self.cache[key] is not None
        return self.fetch(key) is not None

    def has_key(self, key):
        return self.__contains__(key)

    def fetch(self, key):
        session = sa.orm.object_session(self.parent)
        if session and sa.orm.util.has_identity(self.parent):
            relationship = getattr(
                self.parent.__class__, self.collection_name
            ).property
            pairs = relationship.local_remote_pairs

            primary_key = self.child_class.__table__.primary_key

            if (
                len(primary_key.columns) == 2 and
                pairs[0][1].key in primary_key.columns and
                self.key_name in primary_key.columns
            ):
                identity = []
                for column_name, column in primary_key.columns.items():
                    if column_name == self.key_name:
                        identity.append(key)
                    elif column_name == pairs[0][1].key:
                        identity.append(getattr(self.parent, pairs[0][0].key))
                obj = (
                    session.query(self.child_class).get(identity)
                )
            else:
                obj = (
                    session.query(self.child_class)
                    .filter(
                        pairs[0][1] == getattr(self.parent, pairs[0][0].key)
                    )
                    .filter_by(**{self.key_name: key}).first()
                )
            self.cache[key] = obj
            return obj

    def update_cache(self, obj):
        self.cache[getattr(obj, self.key_name)] = obj

    def create_new_instance(self, key):
        value = self.child_class(**{self.key_name: key})
        self.collection.append(value)
        self.cache[key] = value
        return value

    def __getitem__(self, key):
        if key in self.cache:
            if self.cache[key] is not None:
                return self.cache[key]
        else:
            value = self.fetch(key)
            if value:
                return value

        return self.create_new_instance(key)

    def __setitem__(self, key, value):
        try:
            existing = self[key]
            self.collection.remove(existing)
        except KeyError:
            pass
        self.collection.append(value)
        self.cache[key] = value


class TranslationComparator(RelationshipProperty.Comparator):
    def __getitem__(self, key):
        return getattr(self._parentmapper.class_, '_translation_%s' % key)

    def __getattr__(self, attr):
        class_ = self._parentmapper.class_
        if not hasattr(class_, '_collection_%s' % attr):
            setattr(
                class_,
                '_collection_%s' % attr,
                sa.orm.relationship(
                    'Child',
                    primaryjoin=sa.and_(
                        self.property.primaryjoin,
                        getattr(self.property.mapper.class_, 'key') == attr
                    ),
                    viewonly=True
                )
            )
        return getattr(class_, '_collection_%s' % attr)


class TestSomething(TestCase):
    def create_models(self):
        class Parent(self.Model):
            __tablename__ = 'parent'
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.String(50))
            _collection = sa.orm.relationship(
                'Child',
                backref='parent',
                cascade='all, delete-orphan',
                comparator_factory=TranslationComparator
            )
            default_key = sa.Column(sa.String(50))

            @hybrid_property
            def child_map(self):
                if not hasattr(self, '_child_map'):
                    self._child_map = ProxyDict(
                        self, '_collection', Child.key
                    )
                return self._child_map

            @child_map.expression
            def child_map(self):
                return self._collection

        class Child(self.Model):
            __tablename__ = 'child'
            id = sa.Column(
                sa.Integer, sa.ForeignKey('parent.id'), primary_key=True
            )
            key = sa.Column(sa.String(50), primary_key=True)

            def __repr__(self):
                return "Child(key=%r)" % self.key

        Parent.default_child = sa.orm.relationship(
            'Child',
            primaryjoin=sa.and_(
                Parent.default_key == Child.key,
                Parent.id == Child.id
            ),
            viewonly=True,
            uselist=False
        )


        @sa.event.listens_for(sa.orm.mapper, 'load')
        def load_listener(target, context, propagate=True):
            if isinstance(target, Child):
                if '_collection' in target.parent.__dict__:
                    target.parent.child_map.update_cache(target)

        @sa.event.listens_for(sa.orm.mapper, 'refresh')
        def receive_refresh(target, context, attrs, propagate=True):
            #print 'refreshing!', target, attrs

            if isinstance(target, Parent):
                #assert 0
                pass

        # @sa.event.listens_for(sa.orm.mapper, 'populate_instance')
        # def receive_populate_instance(mapper, context, row, target, **kw):
        #     print 'populating instance', mapper.class_, target.__dict__

        self.Parent = Parent
        self.Child = Child

    def create_objects(self):
        p1 = self.Parent(name='p1')
        self.session.add(p1)
        p1.child_map['k1'] = self.Child(key='k1')
        p1.child_map['k2'] = self.Child(key='k2')
        self.session.commit()

    def test_child_map_cache_with_refreshing(self):
        self.create_objects()
        first_count = self.connection.query_count
        query = self.session.query(self.Parent).options(
            sa.orm.joinedload(self.Parent.child_map)
        )
        p1 = query.first()
        p1.child_map['k1']
        p1.child_map['k2']
        assert first_count + 1 == self.connection.query_count

    def test_child_map_cache_with_fresh_loading(self):
        self.create_objects()
        self.session.expunge_all()

        first_count = self.connection.query_count
        query = self.session.query(self.Parent).options(
            sa.orm.joinedload(self.Parent.child_map)
        )
        p1 = query.first()
        p1.child_map['k1']
        p1.child_map['k2']
        assert first_count + 1 == self.connection.query_count

    def test_smart_loading(self):
        self.create_objects()
        self.session.expunge_all()
        parent = self.session.query(self.Parent).first()
        child = self.session.query(self.Child).filter_by(key='k1').first()
        first_count = self.connection.query_count
        parent.child_map['k1'] == child
        assert first_count == self.connection.query_count

    def test_partial_loading(self):
        self.create_objects()
        self.session.expunge_all()
        first_count = self.connection.query_count
        query = self.session.query(self.Parent).options(
            sa.orm.joinedload(self.Parent.child_map.k1)
        )
        p1 = query.first()
        assert p1.child_map['k1']
        assert p1.child_map['k2']
        assert first_count + 2 == self.connection.query_count
