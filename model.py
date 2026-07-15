import sqlite3
from multiprocessing import connection


class exchanger_Model:
    def __init__(self, dbconnection):
        self.dbconnection = dbconnection
        with sqlite3.connect(self.dbconnection) as connection:
            cursor = connection.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS Currencies (
                                id INTEGER PRIMARY KEY,
                                FullName VARCHAR,
                                Code VARCHAR UNIQUE,
                                Sign VARCHAR 
                         )""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS ExchangeRates (
                                id INTEGER PRIMARY KEY,
                                BaseCurrencyID INTEGER,
                                TargetCurrencyID INTEGER,
                                Rate Decimal(6),
                                FOREIGN KEY (BaseCurrencyID) REFERENCES Currencies(id),
                                FOREIGN KEY (TargetCurrencyID) REFERENCES Currencies(id)
                                UNIQUE(BaseCurrencyID, TargetCurrencyID)
                           )""")
            connection.commit()

    def add_currency_object(self, cur_fullname, cur_code, cur_sign):
        with sqlite3.connect(self.dbconnection) as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO Currencies (FullName, Code, Sign) VALUES (?,?,?)",
                           (cur_fullname, cur_code, cur_sign))
            connection.commit()
            return cursor.lastrowid

    def get_all_currencies(self):
        with sqlite3.connect(self.dbconnection) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Currencies")
            return cursor.fetchall()

    def get_currency(self, cur_code):
        with sqlite3.connect(self.dbconnection) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Currencies WHERE Code = ?", (cur_code,))
            return cursor.fetchone()

    def add_exchange_rates_object(self, base_id, target_id, rate):
        with sqlite3.connect(self.dbconnection) as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO ExchangeRates (BaseCurrencyID,TargetCurrencyID,Rate) VALUES (?,?,?)",
                           (base_id, target_id, rate))
            connection.commit()
            return cursor.lastrowid

    def get_all_exchange_rates(self):
        with sqlite3.connect(self.dbconnection) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                                    SELECT
                                        ExchangeRates.id,
                                        ExchangeRates.rate,
                                        
                                        Base.id, Base.fullname, Base.code, Base.sign,
                                        Target.id, Target.fullname, Target.code, Target.sign
                                        
                                    FROM ExchangeRates
                                    JOIN Currencies as Base 
                                        ON ExchangeRates.BaseCurrencyID = Base.id
                                    JOIN Currencies as Target 
                                        ON ExchangeRates.TargetCurrencyId = Target.id
""")
            return cursor.fetchall()

    def get_exchange_rate(self, base_code,target_code):
        with sqlite3.connect(self.dbconnection) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                                                SELECT
                                                    ExchangeRates.id,
                                                    ExchangeRates.rate,

                                                    Base.id, Base.fullname, Base.code, Base.sign,
                                                    Target.id, Target.fullname, Target.code, Target.sign

                                                FROM ExchangeRates
                                                JOIN Currencies as Base 
                                                    ON ExchangeRates.BaseCurrencyID = Base.id
                                                JOIN Currencies as Target 
                                                    ON ExchangeRates.TargetCurrencyId = Target.id
                                                WHERE Base.code = ? AND Target.code = ?""", (base_code,target_code))
            return cursor.fetchone()

    def update_exchange_rate(self,base_code,target_code,new_rate):
        with sqlite3.connect(self.dbconnection) as connection:
            cursor = connection.cursor()
            cursor.execute("""UPDATE ExchangeRates
                              SET rate = ?
                              WHERE BaseCurrencyID = (SELECT id FROM Currencies WHERE code = ?) and TargetCurrencyID = (SELECT id FROM Currencies WHERE code = ?) """,(new_rate,base_code,target_code))
            connection.commit()
            return cursor.rowcount