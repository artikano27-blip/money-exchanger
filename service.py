from decimal import Decimal


from dto import CurrencyDTO, ExchangeRatesDTO, ExchangeResultDTO
class DatabaseNotFoundError(Exception):
    pass

class exchanger_Service():
    def __init__(self, model):
        self.model = model

    def add_currency(self, cur_fullname, cur_code, cur_sign):
        new_currency = self.model.add_currency_object(cur_fullname, cur_code, cur_sign)
        dto_currency = CurrencyDTO(
            id=new_currency,
            name=cur_fullname,
            code=cur_code,
            sign=cur_sign
        )
        return dto_currency

    def get_all_currencies(self):
        dto_currencies = []
        all_currencies = self.model.get_all_currencies()
        for currency in all_currencies:
            dto_currency = CurrencyDTO(
                id=currency[0],
                name=currency[1],
                code=currency[2],
                sign=currency[3]
            )
            dto_currencies.append(dto_currency)
        return dto_currencies

    def get_currency(self, cur_code):
        row_currency = self.model.get_currency(cur_code)
        if row_currency is None:
            raise DatabaseNotFoundError("Одна (или обе) валюта из валютной пары не существует в БД")
        else:
            dto_currency = CurrencyDTO(
                id=row_currency[0],
                name=row_currency[1],
                code=row_currency[2],
                sign=row_currency[3]
            )
            return dto_currency

    def add_exchange_rate(self, base_currency_code, target_currency_code, rate):
        base_cur_data = self.get_currency(base_currency_code)
        target_cur_data = self.get_currency(target_currency_code)

        if base_cur_data is None or target_cur_data is None:
            raise DatabaseNotFoundError("Одна (или обе) валюта из валютной пары не существует в БД")

        target_id = target_cur_data.id
        base_id = base_cur_data.id
        new_id = self.model.add_exchange_rates_object(base_id, target_id, rate)

        dto_exchange_rate = ExchangeRatesDTO(
            id=new_id,
            baseCurrency=base_cur_data,
            targetCurrency=target_cur_data,
            rate=rate
        )
        return dto_exchange_rate

    def get_all_exchange_rates(self):
        all_exchange_rates = self.model.get_all_exchange_rates()
        dto_exchange_rates = []
        for item in all_exchange_rates:
            dto_exchange_rate = ExchangeRatesDTO(
                id=item[0],
                baseCurrency=CurrencyDTO(
                    id=item[2],
                    name=item[3],
                    code=item[4],
                    sign=item[5]
                ),
                targetCurrency=CurrencyDTO(
                    id=item[6],
                    name=item[7],
                    code=item[8],
                    sign=item[9]
                ),
                rate=item[1]
            )
            dto_exchange_rates.append(dto_exchange_rate)
        return dto_exchange_rates

    def get_exchange_rate(self, base_code, target_code):
        row_exchange_rate = self.model.get_exchange_rate(base_code, target_code)
        if row_exchange_rate is None:
            raise DatabaseNotFoundError("Одна (или обе) валюта из валютной пары не существует в БД")

        dto_exchange_rate = ExchangeRatesDTO(
            id=row_exchange_rate[0],
            baseCurrency=CurrencyDTO(
                id=row_exchange_rate[2],
                name=row_exchange_rate[3],
                code=row_exchange_rate[4],
                sign=row_exchange_rate[5]
            ),
            targetCurrency=CurrencyDTO(
                id=row_exchange_rate[6],
                name=row_exchange_rate[7],
                code=row_exchange_rate[8],
                sign=row_exchange_rate[9]
            ),
            rate=row_exchange_rate[1]
        )
        return dto_exchange_rate


    def update_exchange_rate(self, base_code, target_code, new_rate):
        row_exchange_rate = self.model.update_exchange_rate(base_code, target_code, new_rate)
        if row_exchange_rate==0:
            raise DatabaseNotFoundError("Одна (или обе) валюта из валютной пары не существует в БД")
        else:
            return self.get_exchange_rate(base_code, target_code)

    def exchange_currency(self,base_code, target_code, amount):
        final_rate = None
        base_code_info = None
        target_code_info = None
        row_exchange_rate = self.model.get_exchange_rate(base_code,target_code)
        if row_exchange_rate is not None:
            final_rate = row_exchange_rate[1]
            base_code_info = (row_exchange_rate[2],row_exchange_rate[3],row_exchange_rate[4],row_exchange_rate[5])
            target_code_info = (row_exchange_rate[6],row_exchange_rate[7],row_exchange_rate[8],row_exchange_rate[9])
        else:
            row_reverse_rate = self.model.get_exchange_rate(target_code,base_code)
            if row_reverse_rate is not None:
                final_rate = 1/row_reverse_rate[1]
                base_code_info = (row_reverse_rate[6], row_reverse_rate[7], row_reverse_rate[8], row_reverse_rate[9])
                target_code_info = (row_reverse_rate[2], row_reverse_rate[3], row_reverse_rate[4], row_reverse_rate[5])
            else:
                usd_base_row = self.model.get_exchange_rate("USD",base_code)
                usd_target_row = self.model.get_exchange_rate("USD",target_code)
                if usd_base_row is not None and usd_target_row is not None:
                    final_rate = usd_target_row[1] / usd_base_row[1]
                    base_code_info = (usd_base_row[6],usd_base_row[7],usd_base_row[8],usd_base_row[9])
                    target_code_info = (usd_target_row[6],usd_target_row[7],usd_target_row[8],usd_target_row[9])
        if final_rate is not None:
            decimal_rate = Decimal(final_rate).quantize(Decimal("0.000001"))
            converted_amount = Decimal(amount)*decimal_rate
            decimal_amount = converted_amount.quantize(Decimal("0.01"))
            final_amount = round(float(decimal_amount), 2)

        else:
            raise DatabaseNotFoundError("Одна (или обе) валюта из валютной пары не существует в БД")

        dto_exchange_currency = ExchangeResultDTO(
            baseCurrency=CurrencyDTO(
                id = base_code_info[0],
                name = base_code_info[1],
                code = base_code_info[2],
                sign = base_code_info[3]
            ),
            targetCurrency=CurrencyDTO(
                id=target_code_info[0],
                name=target_code_info[1],
                code=target_code_info[2],
                sign=target_code_info[3],
            ),
            rate= float(decimal_rate),
            amount=float(amount),
            convertedAmount=final_amount
        )
        return dto_exchange_currency
