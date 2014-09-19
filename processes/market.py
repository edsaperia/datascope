from HIF.processes.core import Process, Retrieve
from HIF.tasks import execute_process, extend_process
from HIF.helpers.data import count_2d_list


class FinancialHealthCheck(Process):

    HIF_stock_price = 'QuandlAnnualStockPrice'
    HIF_net_income = 'QuandlAnnualNetIncome'

    def process(self):

        # Setup person retriever
        stock_price_config = {
            "_link": self.HIF_stock_price,
            #"_context": query,
            "_extend": {
                "keypath": None,
                "args": ["SEC-ticker"],
                "kwargs": {},
                "extension": "Stock Info"
            },
        }
        stock_price_config.update(self.config.dict())
        stock_price_retriever = Retrieve()
        stock_price_retriever.setup(**stock_price_config)

        # Setup data retriever
        net_income_config = {
            "_link": self.HIF_net_income,
            #"_context": query,  # here only to distinct inter-query retriever configs from each other
            "_extend": {
                "keypath": None,
                "args": ["SEC-ticker"],
                "kwargs": {},
                "extension": "Net Income"
            }
        }
        net_income_retriever = Retrieve()
        net_income_retriever.setup(**net_income_config)

        # Start Celery task
        task = (
            execute_process.s('', ["Process", 1]) |
            extend_process.s(stock_price_retriever.retain(), multi=True) |
            extend_process.s(net_income_retriever.retain(), multi=True)
        )()
        self.task = task

    def post_process(self):
        pass
        #person_data = Retrieve().load(serialization=self.task.result).rsl
        #self.rsl = count_2d_list(person_data['claims'], d2_list='claimers').most_common(11)[1:]  # takes 10, but strips query person

    class Meta:
        app_label = "HIF"
        proxy = True