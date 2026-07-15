from http.server import HTTPServer
from controller import exchanger_Controller
from model import exchanger_Model
from service import exchanger_Service

def main():
    exchanger_model = exchanger_Model("exchanger_database.db")
    exchanger_service = exchanger_Service(exchanger_model)

    # Указываем 0.0.0.0 для приема внешних подключений со всех интерфейсов
    server = HTTPServer(('0.0.0.0', 8000), exchanger_Controller)
    server.exchanger_service = exchanger_service
    print("Сервер запущен на порту 8000 и принимает внешние подключения")
    # Запускаем бесконечный цикл прослушивания сети
    server.serve_forever()

if __name__ == "__main__":
    main()