from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import json
import sqlite3
from dataclasses import asdict


class exchanger_Controller(BaseHTTPRequestHandler):
    def extract_code(self):
        path_parts = self.path.split("/")
        cur_code = path_parts[2]
        return cur_code

    def end_headers(self):
        # Добавляем наш заголовок
        self.send_header('Access-Control-Allow-Origin', '*')
        # Вызываем оригинальный метод для завершения работы
        super().end_headers()

    def do_GET(self):
        service = self.server.exchanger_service
        if self.path == "/currencies":
            try:
                dto_currencies = service.get_all_currencies()
            except Exception as error_msg:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(str(error_msg).encode())
            else:
                currencies_list = []
                for dto_item in dto_currencies:
                    currencies_list.append(asdict(dto_item))
                all_currencies_json = json.dumps(currencies_list)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(all_currencies_json.encode())

        elif self.path.startswith("/currency/"):
            cur_code = self.extract_code()
            if len(cur_code) != 3:
                error_msg = b"Missing or invalid required form field"
                self.send_response(400)
                self.send_header("Content-Length", str(len(error_msg)))
                self.end_headers()
                self.wfile.write(error_msg)
                return
            try:
                base_code = cur_code
                currency_dto = service.get_currency(base_code)
                if currency_dto is None:
                    error_msg = b"Currency not found"
                    self.send_response(404)
                    self.send_header("Content-Length", str(len(error_msg)))
                    self.end_headers()
                    self.wfile.write(error_msg)
                    return

            except Exception as error_msg:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(str(error_msg).encode())
            else:
                currency_json = json.dumps(asdict(currency_dto))
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(currency_json.encode())

        elif self.path == "/exchangeRates":
            try:
                dto_exchange_rates = service.get_all_exchange_rates()
            except Exception as error_msg:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(str(error_msg).encode())
            else:
                dto_exchange_rates_list = []
                for dto_item in dto_exchange_rates:
                    dto_exchange_rates_list.append(asdict(dto_item))
                all_exchange_rates_json = json.dumps(dto_exchange_rates_list)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(all_exchange_rates_json.encode())

        elif self.path.startswith("/exchangeRate/"):
            cur_code = self.extract_code()
            if len(cur_code) != 6:
                error_msg = b"Missing currencies code in URL"
                self.send_response(400)
                self.send_header("Content-Length", str(len(error_msg)))
                self.end_headers()
                self.wfile.write(error_msg)
                return
            try:
                base_code = cur_code[:3]
                target_code = cur_code[3:]
                dto_exchange_rate = service.get_exchange_rate(base_code, target_code)

                if dto_exchange_rate is None:
                    error_msg = b"Exchange rate not found for the pair"
                    self.send_response(404)
                    self.send_header("Content-Length", str(len(error_msg)))
                    self.end_headers()
                    self.wfile.write(error_msg)
                    return

            except Exception as error_msg:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(str(error_msg).encode())
            else:
                currency_json = json.dumps(asdict(dto_exchange_rate))
                currency_bytes = currency_json.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Content-Length", str(len(currency_bytes)))
                self.end_headers()
                self.wfile.write(currency_bytes)

        elif self.path.startswith("/exchange"):
            parsed_url = urlparse(self.path)
            if parsed_url.path == "/exchange":
                parsed_dict = parse_qs(parsed_url.query)
                try:
                    base_code = parsed_dict["from"][0]
                    target_code = parsed_dict["to"][0]
                    amount = parsed_dict["amount"][0]
                except (KeyError, ValueError):
                    error_msg = b"Missing or invalid required form field"
                    self.send_response(400)
                    self.send_header("Content-Length", str(len(error_msg)))
                    self.end_headers()
                    self.wfile.write(error_msg)
                    return
                try:
                    dto_exchange = service.exchange_currency(base_code, target_code, amount)
                    if dto_exchange is None:
                        error_msg = b"Exchange rate not found for the pair"
                        self.send_response(404)
                        self.send_header("Content-Length", str(len(error_msg)))
                        self.end_headers()
                        self.wfile.write(error_msg)
                        return

                except Exception as error_msg:
                    self.send_response(500)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(str(error_msg).encode())
                    print(error_msg)
                else:
                    currency_json = json.dumps(asdict(dto_exchange), default=str)
                    currency_bytes = currency_json.encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Content-Length", str(len(currency_bytes)))
                    self.end_headers()
                    self.wfile.write(currency_bytes)

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
                error_msg = b"Missing required form field"
                self.send_response(400)
                self.send_header("Content-Length", str(len(error_msg)))
                self.end_headers()
                self.wfile.write(error_msg)

            except sqlite3.IntegrityError:
                error_msg = b"Duplicate error"
                self.send_response(409)
                self.send_header("Content-Length", str(len(error_msg)))
                self.end_headers()
                self.wfile.write(error_msg)

            except Exception as error_msg:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(str(error_msg).encode())
                print(error_msg)

            else:
                response_json = json.dumps(asdict(new_currency_dto))
                self.send_response(201)
                self.send_header("Content-Length", str(len(response_json.encode())))
                self.end_headers()
                self.wfile.write(response_json.encode())

        elif self.path == "/exchangeRates":

            try:
                base_cur_data = parsed_dict["baseCurrencyCode"][0]
                post_cur_data = parsed_dict["targetCurrencyCode"][0]
                cur_rate = float(parsed_dict["rate"][0])
                dto_exchange_rate = service.add_exchange_rate(base_cur_data, post_cur_data, cur_rate)

            except KeyError:
                error_msg = b"Missing required form field"
                self.send_response(400)
                self.send_header("Content-Length", str(len(error_msg)))
                self.end_headers()
                self.wfile.write(error_msg)

            except ValueError as error_msg:
                error_bytes = str(error_msg).encode()
                self.send_response(404)
                self.send_header("Content-Length", str(len(error_bytes)))
                self.end_headers()
                self.wfile.write(error_bytes)

            except sqlite3.IntegrityError:
                error_msg = b"Duplicate error"
                self.send_response(409)
                self.send_header("Content-Length", str(len(error_msg)))
                self.end_headers()
                self.wfile.write(error_msg)

            except Exception as error_msg:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(str(error_msg).encode())
                print(error_msg)

            else:
                response_json = json.dumps(asdict(dto_exchange_rate))
                self.send_response(201)
                self.send_header("Content-Length", str(len(response_json.encode())))
                self.end_headers()
                self.wfile.write(response_json.encode())

    def do_PATCH(self):
        service = self.server.exchanger_service
        cur_code = self.extract_code()
        if self.path.startswith("/exchangeRate/"):
            if len(cur_code) != 6:
                error_msg = b"Missing or invalid required form field"
                self.send_response(400)
                self.send_header("Content-Length", str(len(error_msg)))
                self.end_headers()
                self.wfile.write(error_msg)
                return

            content_length = int(self.headers.get("Content-Length", 0))
            post_data_bytes = self.rfile.read(content_length)
            text_data = post_data_bytes.decode('utf-8')
            parsed_dict = parse_qs(text_data)
            try:
                new_rate = float(parsed_dict["rate"][0])
            except (KeyError, ValueError):
                error_msg = b"Missing or invalid required form field"
                self.send_response(400)
                self.send_header("Content-Length", str(len(error_msg)))
                self.end_headers()
                self.wfile.write(error_msg)
                return
            try:
                base_code = cur_code[:3]
                target_code = cur_code[3:]
                dto_update_rate = service.update_exchange_rate(base_code, target_code, new_rate)
                if dto_update_rate is None:
                    error_msg = b"Exchange rate not found for the pair"
                    self.send_response(404)
                    self.send_header("Content-Length", str(len(error_msg)))
                    self.end_headers()
                    self.wfile.write(error_msg)
                    return
            except Exception as error_msg:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                error_json = json.dumps({"message": str(error_msg)})
                self.wfile.write(error_json.encode('utf-8'))
                print(error_msg)
            else:
                currency_json = json.dumps(asdict(dto_update_rate))
                currency_bytes = currency_json.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Content-Length", str(len(currency_bytes)))
                self.end_headers()
                self.wfile.write(currency_bytes)
