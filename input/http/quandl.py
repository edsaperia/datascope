from HIF.input.http.core import HttpJsonMixin, HttpLink
from HIF.input.helpers import sanitize_single_trueish_input


class QuandlBase(HttpLink, HttpJsonMixin):
    """
    Quandl is limited to American registered companies (that use SEC standard)
    """

    HIF_namespace = 'quandl'

    # HIF_parameters = {
    #     "trim_start": "{}-01-01",
    #     "trim_end": "{}-12-31",
    # }
    HIF_objective = {
        "data.0.1": 0,
    }

    def __init__(self, *args, **kwargs):
        super(QuandlBase, self).__init__(*args, **kwargs)
        HttpJsonMixin.__init__(self)

    def sanitize_input(self, to_check):
        return sanitize_single_trueish_input(to_check, class_name=self.__class__.__name__)

    def prepare_params(self):
        params = super(QuandlBase, self).prepare_params()
        return params.format(self.config.year_of_interest, self.config.year_of_interest)  # trim_start + trim_end formatting

    def prepare_link(self):
        link = super(QuandlBase, self).prepare_link()
        return link.format(self.input)  # TODO: this pattern is problematic when reloading and inspecting stuff (input will be None)

    @property  # TODO: how to implement these things correctly with mixins instead of having to add it all the time
    def rsl(self):
        return self.data[0]

    class Meta:
        app_label = "HIF"
        proxy = True


class QuandlAnnualNetIncome(QuandlBase):

    HIF_link = 'https://www.quandl.com/api/v1/datasets/RAYMOND/{}_NET_INCOME_A'
    HIF_translations = {
        "data.0.1": "company-year-net-income"
    }

    @property  # TODO: how to implement these things correctly with mixins instead of having to add it all the time
    def rsl(self):
        return self.data[0]['company-year-net-income']

    class Meta:
        app_label = "HIF"
        proxy = True


class QuandlAnnualStockPrice(QuandlBase):

    HIF_link = "https://www.quandl.com/api/v1/datasets/WIKI/{}.json"

    # TODO: Add a helper to do this and improve syntax looks?
    # HIF_parameters = dict(QuandlBase.HIF_parameters.copy(), **{
    HIF_parameters = {
        "column": 4,
        "sort_order": "asc",
        "collapse": "annual",
    }

    HIF_translations = {
        "data.0.1": "stock-year-closing-price"
    }

    @property  # TODO: how to implement these things correctly with mixins instead of having to add it all the time
    def rsl(self):
        return self.data[0]['stock-year-closing-price']

    class Meta:
        app_label = "HIF"
        proxy = True
