from http.server import HTTPServer
from controller import exchanger_Controller
from model import exchanger_Model
from service import exchanger_Service

def main():
    exchanger_model = exchanger_Model("exchanger_database.db")
    exchanger_service = exchanger_Service(exchanger_model)


    # Создаем сервер, привязываем его к адресу localhost:8000 и передаем наш класс-обработчик
    server = HTTPServer(('localhost', 8000), exchanger_Controller)
    server.exchanger_service = exchanger_service
    print("Сервер запущен на http://localhost:8000/currencies")
    # Запускаем бесконечный цикл прослушивания сети
    server.serve_forever()

if __name__ == "__main__":
    main()