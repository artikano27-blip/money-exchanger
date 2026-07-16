from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import json
import sqlite3
from dataclasses import asdict
from decimal import Decimal, InvalidOperation
from service import DatabaseNotFoundError


class exchanger_Controller(BaseHTTPRequestHandler):
    def extract_code(self):
        path_parts = self.path.split("/")
        cur_code = path_parts[2]
        return cur_code

    def _send_cors_headers(self, status=200):
        """Единый метод для отправки HTTP-статуса и обязательных CORS-заголовков"""
        self.send_response(status)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PATCH, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        # Добавляем тип контента по умолчанию для REST API (JSON)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()

    def do_OPTIONS(self):
        self._send_cors_headers(200)

    def do_GET(self):
        service = self.server.exchanger_service
        if self.path == "/currencies":

            try:
                dto_currencies = service.get_all_currencies()

            except Exception as error_msg:
                self._send_cors_headers(500)
                error_response = {"message": f"Внутренняя ошибка сервера: {str(error_msg)}"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))

            else:
                self._send_cors_headers(200)
                dict_list = [asdict(item) for item in dto_currencies]
                self.wfile.write(json.dumps(dict_list).encode('UTF-8'))

        elif self.path.startswith("/currency/"):
            cur_code = self.extract_code()
            if len(cur_code) != 3:
                self._send_cors_headers(400)
                error_response = {"message": "Неверный формат данных"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                return

            try:
                base_code = cur_code
                currency_dto = service.get_currency(base_code)

            except DatabaseNotFoundError as error_msg:
                self._send_cors_headers(404)
                error_response = {"message": str(error_msg)}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                return

            except Exception as error_msg:
                    self._send_cors_headers(500)
                    error_response = {"message": f"Внутренняя ошибка сервера: {str(error_msg)}"}
                    self.wfile.write(json.dumps(error_response).encode('utf-8'))
            else:
                self._send_cors_headers(200)
                self.wfile.write(json.dumps(asdict(currency_dto)).encode('utf-8'))

        elif self.path == "/exchangeRates":

            try:
                dto_exchange_rates = service.get_all_exchange_rates()

            except Exception as error_msg:
                self._send_cors_headers(500)
                error_response = {"message": f"Внутренняя ошибка сервера: {str(error_msg)}"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))

            else:
                self._send_cors_headers(200)
                dict_list = [asdict(item) for item in dto_exchange_rates]
                self.wfile.write(json.dumps(dict_list).encode('utf-8'))

        elif self.path.startswith("/exchangeRate/"):
            cur_code = self.extract_code()
            if len(cur_code) != 6:
                self._send_cors_headers(400)
                error_response = {"message": "Неверный формат данных"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                return

            try:
                base_code = cur_code[:3]
                target_code = cur_code[3:]
                dto_exchange_rate = service.get_exchange_rate(base_code, target_code)

            except DatabaseNotFoundError as error_msg:
                self._send_cors_headers(404)
                error_response = {"message": str(error_msg)}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                return

            except Exception as error_msg:
                self._send_cors_headers(500)
                error_response = {"message": f"Внутренняя ошибка сервера: {str(error_msg)}"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))

            else:
                self._send_cors_headers(200)
                self.wfile.write(json.dumps(asdict(dto_exchange_rate)).encode('utf-8'))

        elif self.path.startswith("/exchange"):
            parsed_url = urlparse(self.path)
            if parsed_url.path == "/exchange":
                parsed_dict = parse_qs(parsed_url.query)

                try:
                    base_code = parsed_dict["from"][0]
                    target_code = parsed_dict["to"][0]
                    amount = parsed_dict["amount"][0]

                except (KeyError, ValueError) as error_msg:
                    self._send_cors_headers(400)
                    error_response = {"message": f"Неверный формат данных: {str(error_msg)}"}
                    self.wfile.write(json.dumps(error_response).encode('utf-8'))
                    return

                try:
                    dto_exchange = service.exchange_currency(base_code, target_code, amount)

                except DatabaseNotFoundError as error_msg:
                    self._send_cors_headers(404)
                    error_response = {"message": str(error_msg)}
                    self.wfile.write(json.dumps(error_response).encode('utf-8'))
                    return

                except Exception as error_msg:
                    self._send_cors_headers(500)
                    error_response = {"message": f"Внутренняя ошибка сервера: {str(error_msg)}"}
                    self.wfile.write(json.dumps(error_response).encode('utf-8'))

                else:
                    self._send_cors_headers(200)
                    self.wfile.write(json.dumps(asdict(dto_exchange)).encode('utf-8'))


    def do_POST(self):
        service = self.server.exchanger_service
        content_length = int(self.headers.get("Content-Length", 0))
        post_data_bytes = self.rfile.read(content_length)
        text_data = post_data_bytes.decode('utf-8')
        parsed_dict = parse_qs(text_data)

        if self.path == "/currencies":
            try:
                cur_fullname = parsed_dict["name"][0]
                cur_code = parsed_dict["code"][0]
                cur_sign = parsed_dict["sign"][0]
                new_currency_dto = service.add_currency(cur_fullname, cur_code, cur_sign)

            except KeyError:
                self._send_cors_headers(400)
                error_response = {"message": "Отсутствует нужное поле формы"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))

            except ValueError as error_msg:
                self._send_cors_headers(400)
                error_response = {"message": f"Неверный формат данных: {str(error_msg)}"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))

            except sqlite3.IntegrityError:
                self.send_response(409)
                error_response = {"message": "Валюта с таким кодом уже существует"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))

            except Exception as error_msg:
                self._send_cors_headers(500)
                error_response = {"message": f"Внутренняя ошибка сервера: {str(error_msg)}"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))

            else:
                self._send_cors_headers(201)
                self.wfile.write(json.dumps(asdict(new_currency_dto)).encode('utf-8'))

        elif self.path == "/exchangeRates":

            try:
                base_cur_data = parsed_dict["baseCurrencyCode"][0]
                post_cur_data = parsed_dict["targetCurrencyCode"][0]
                cur_rate = Decimal(parsed_dict["rate"][0])
                dto_exchange_rate = service.add_exchange_rate(base_cur_data, post_cur_data, cur_rate)

            except KeyError:
                self._send_cors_headers(400)
                error_response = {"message": "Отсутствует нужное поле формы"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))

            except ValueError as error_msg:
                self._send_cors_headers(400)
                error_response = {"message": f"Неверный формат данных: {str(error_msg)}"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))

            except sqlite3.IntegrityError:
                self.send_response(409)
                error_response = {"message": "Валютная пара с таким кодом уже существует"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))

            except DatabaseNotFoundError as error_msg:
                 self._send_cors_headers(404)
                 error_response = {"message": str(error_msg)}
                 self.wfile.write(json.dumps(error_response).encode('utf-8'))

            except Exception as error_msg:
                self._send_cors_headers(500)
                error_response = {"message": f"Внутренняя ошибка сервера: {str(error_msg)}"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))

            else:
                self._send_cors_headers(201)
                self.wfile.write(json.dumps(asdict(dto_exchange_rate)).encode('utf-8'))

    def do_PATCH(self):
        service = self.server.exchanger_service
        cur_code = self.extract_code()

        if self.path.startswith("/exchangeRate/"):
            if len(cur_code) != 6:
                self._send_cors_headers(400)
                error_response = {"message": "Неверный формат данных"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                return

            content_length = int(self.headers.get("Content-Length", 0))
            post_data_bytes = self.rfile.read(content_length)
            text_data = post_data_bytes.decode('utf-8')
            parsed_dict = parse_qs(text_data)

            try:
                new_rate = Decimal(parsed_dict["rate"][0])

            except (KeyError, InvalidOperation) as error_msg:
                self._send_cors_headers(400)
                error_response = {"message": f"Неверный формат данных: {str(error_msg)}"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                return

            try:
                base_code = cur_code[:3]
                target_code = cur_code[3:]
                dto_update_rate = service.update_exchange_rate(base_code, target_code, new_rate)

            except DatabaseNotFoundError as error_msg:
                    self._send_cors_headers(404)
                    error_response = {"message": str(error_msg)}
                    self.wfile.write(json.dumps(error_response).encode('utf-8'))
                    return

            except Exception as error_msg:
                self._send_cors_headers(500)
                error_response = {"message": f"Внутренняя ошибка сервера: {str(error_msg)}"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
            else:
                self._send_cors_headers(200)
                self.wfile.write(json.dumps(asdict(dto_update_rate)).encode('utf-8'))

