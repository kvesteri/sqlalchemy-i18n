from sqlalchemy_i18n.expressions import current_locale


class TestCurrentLocaleExpression(object):
    def test_render(self):
        assert str(current_locale()) == ':current_locale'
