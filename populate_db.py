import sys
import os
from datetime import datetime, timedelta
import random

# Добавляем путь к текущей директории для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, create_tables
from models import Incident, IncidentStatus, IncidentSource

def create_test_data():
    """Создание тестовых данных инцидентов"""
    
    # Тестовые описания инцидентов
    descriptions = [
        "Самокат не в сети более 2 часов",
        "Точка выдачи не отвечает на запросы",
        "Отчёт по продажам не выгрузился",
        "Проблема с GPS у самоката #12345",
        "Ошибка при пополнении баланса",
        "Приложение вылетает при сканировании QR",
        "Сервер API недоступен",
        "Проблема с подключением к платежному шлюзу",
        "Данные не синхронизируются с облаком",
        "Высокая загрузка CPU на сервере",
        "Медленная работа мобильного приложения",
        "Ошибка 500 при создании заказа",
        "Утечка памяти в сервисе геолокации",
        "Проблема с SMS-уведомлениями",
        "База данных перегружена",
        "Файлы логов не создаются",
        "Кэш не очищается автоматически",
        "Ошибка валидации данных формы",
        "Дублирующиеся уведомления",
        "Проблема с экспортом в Excel"
    ]
    
    # Создаем сессию базы данных
    db = SessionLocal()
    
    try:
        # Очищаем существующие данные (опционально)
        db.query(Incident).delete()
        db.commit()
        
        incidents = []
        
        # Создаем 20 тестовых инцидентов
        for i in range(20):
            # Случайный статус с распределением
            status_weights = [0.3, 0.4, 0.2, 0.1]  # new, in_progress, resolved, closed
            status = random.choices(
                [IncidentStatus.NEW, IncidentStatus.IN_PROGRESS, IncidentStatus.RESOLVED, IncidentStatus.CLOSED],
                weights=status_weights
            )[0]
            
            # Случайный источник
            source = random.choice([IncidentSource.OPERATOR, IncidentSource.MONITORING, IncidentSource.PARTNER])
            
            # Случайное время создания (последние 7 дней)
            created_at = datetime.now() - timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            incident = Incident(
                description=descriptions[i],
                status=status,
                source=source,
                created_at=created_at
            )
            
            incidents.append(incident)
        
        # Добавляем все инциденты в базу
        db.add_all(incidents)
        db.commit()
        
        print(f"✅ Успешно создано {len(incidents)} тестовых инцидентов")
        print("\n📊 Статистика по статусам:")
        
        # Получаем статистику
        stats = db.query(Incident.status, db.func.count(Incident.id)).group_by(Incident.status).all()
        for status, count in stats:
            print(f"   {status.value}: {count} инцидентов")
        
        print("\n📊 Статистика по источникам:")
        source_stats = db.query(Incident.source, db.func.count(Incident.id)).group_by(Incident.source).all()
        for source, count in source_stats:
            print(f"   {source.value}: {count} инцидентов")
            
        print(f"\n📅 Диапазон дат: от {min(inc.created_at for inc in incidents).strftime('%Y-%m-%d %H:%M')}")
        print(f"                до {max(inc.created_at for inc in incidents).strftime('%Y-%m-%d %H:%M')}")
        
    except Exception as e:
        print(f"❌ Ошибка при создании тестовых данных: {e}")
        db.rollback()
    finally:
        db.close()

def show_incidents():
    """Показать созданные инциденты"""
    db = SessionLocal()
    
    try:
        incidents = db.query(Incident).order_by(Incident.created_at.desc()).all()
        
        print(f"\n📋 Список созданных инцидентов ({len(incidents)}):")
        print("-" * 80)
        
        for incident in incidents:
            print(f"ID: {incident.id:2d} | "
                  f"Статус: {incident.status.value:12} | "
                  f"Источник: {incident.source.value:10} | "
                  f"Создан: {incident.created_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"     Описание: {incident.description}")
            print("-" * 80)
            
    except Exception as e:
        print(f"❌ Ошибка при получении данных: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Заполнение базы данных тестовыми инцидентами")
    print("=" * 50)
    
    # Создаем таблицы если их нет
    create_tables()
    print("✅ Таблицы базы данных созданы/проверены")
    
    # Создаем тестовые данные
    create_test_data()
    
    # Показываем созданные данные
    show_incidents()
    
    print("\n🎉 Заполнение базы данных завершено!")
    print("\n💡 Для использования API запустите: uvicorn main:app --reload")
    print("📚 Документация будет доступна по адресу: http://127.0.0.1:8000/docs")