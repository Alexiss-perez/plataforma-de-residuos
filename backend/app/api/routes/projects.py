from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User
from app.schemas.schemas import ProjectCreate, ProjectPublic, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectPublic, status_code=201)
def create(data: ProjectCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = ProjectService(db).create(user, data)
    db.commit()
    return ProjectService(db).to_public(project)


@router.get("", response_model=list[ProjectPublic])
def list_all(skip: int = 0, limit: int = Query(default=50, le=200), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [ProjectService(db).to_public(p) for p in ProjectService(db).list_all(skip, limit)]


@router.get("/{project_id}", response_model=ProjectPublic)
def get_one(project_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ProjectService(db).to_public(ProjectService(db).get(project_id))


@router.patch("/{project_id}", response_model=ProjectPublic)
def update(project_id: int, data: ProjectUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = ProjectService(db).update(project_id, user, data)
    db.commit()
    return ProjectService(db).to_public(project)
