from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any

from database import get_db, create_tables
from models import Incident, IncidentStatus, IncidentSource
from schemas import IncidentCreate, IncidentUpdate, IncidentResponse

app = FastAPI(
    title="Incident API",
    description="API для учёта инцидентов",
    version="1.0.0"
)

# Создаем таблицы при запуске
@app.on_event("startup")
def startup_event():
    create_tables()

@app.post("/incidents/", response_model=IncidentResponse, status_code=201)
def create_incident(incident: IncidentCreate, db: Session = Depends(get_db)):
    """
    Создать новый инцидент
    """
    db_incident = Incident(
        description=incident.description,
        source=incident.source
    )
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident

@app.get("/incidents/", response_model=List[IncidentResponse])
def get_incidents(
    status: Optional[IncidentStatus] = Query(None, description="Фильтр по статусу"),
    source: Optional[IncidentSource] = Query(None, description="Фильтр по источнику"),
    db: Session = Depends(get_db)
):
    """
    Получить список инцидентов с возможностью фильтрации по статусу и источнику
    """
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    if source:
        query = query.filter(Incident.source == source)
    return query.order_by(Incident.created_at.desc()).all()

@app.get("/incidents/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """
    Получить инцидент по ID
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Инцидент не найден")
    return incident

@app.patch("/incidents/{incident_id}", response_model=IncidentResponse)
def update_incident_status(
    incident_id: int, 
    incident_update: IncidentUpdate, 
    db: Session = Depends(get_db)
):
    """
    Обновить статус инцидента по ID
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Инцидент не найден")
    
    incident.status = incident_update.status
    db.commit()
    db.refresh(incident)
    return incident

@app.delete("/incidents/{incident_id}", status_code=204)
def delete_incident(incident_id: int, db: Session = Depends(get_db)):
    """
    Удалить инцидент по ID
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Инцидент не найден")
    
    db.delete(incident)
    db.commit()
    return

@app.get("/stats/")
def get_stats(db: Session = Depends(get_db)):
    """
    Получить статистику по инцидентам
    """
    # Статистика по статусам
    status_stats = db.query(
        Incident.status, 
        func.count(Incident.id)
    ).group_by(Incident.status).all()
    
    # Статистика по источникам
    source_stats = db.query(
        Incident.source, 
        func.count(Incident.id)
    ).group_by(Incident.source).all()
    
    # Общее количество инцидентов
    total_incidents = db.query(Incident).count()
    
    # Последний инцидент
    last_incident = db.query(Incident).order_by(Incident.created_at.desc()).first()
    
    return {
        "total_incidents": total_incidents,
        "status_distribution": {status.value: count for status, count in status_stats},
        "source_distribution": {source.value: count for source, count in source_stats},
        "last_incident_date": last_incident.created_at if last_incident else None
    }

@app.get("/")
def root():
    return {"message": "Incident API Service", "version": "1.0.0"}