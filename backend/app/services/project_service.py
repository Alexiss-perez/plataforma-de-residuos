from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import RoleEnum
from app.models.models import Project, User
from app.repositories.repos import ProjectRepository
from app.schemas.schemas import ProjectCreate, ProjectPublic, ProjectUpdate


class ProjectService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ProjectRepository(db)

    def _get_org_of(self, user: User):
        from app.repositories.repos import OrganizationRepository
        org = OrganizationRepository(self.db).get_by_owner(user.id)
        return org

    def create(self, user: User, data: ProjectCreate) -> Project:
        org = self._get_org_of(user)
        if not org:
            raise ForbiddenError("Only organizations can create projects")
        project = self.repo.create(
            organization_id=org.id,
            title=data.title,
            description=data.description,
            status="ACTIVE",
            latitude=data.latitude,
            longitude=data.longitude,
            commune=data.commune,
        )
        return project

    def get(self, project_id: int) -> Project:
        project = self.repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")
        return project

    def list_all(self, skip: int = 0, limit: int = 50) -> list[Project]:
        return list(self.repo.list_all(skip, limit))

    def update(self, project_id: int, user: User, data: ProjectUpdate) -> Project:
        project = self.get(project_id)
        org = self._get_org_of(user)
        if (not org or org.id != project.organization_id) and user.role != RoleEnum.ADMIN:
            raise ForbiddenError("Only the organization owner or admin can update this project")
        fields = data.model_dump(exclude_unset=True)
        return self.repo.update(project, fields)

    def compute_progress(self, project: Project) -> float:
        needs = project.needs
        if not needs:
            return 0.0
        total_req = sum(n.quantity_required for n in needs)
        total_rec = sum(n.quantity_received for n in needs)
        if total_req <= 0:
            return 0.0
        return round(min(100.0, (total_rec / total_req) * 100.0), 2)

    def to_public(self, project: Project) -> ProjectPublic:
        progress = self.compute_progress(project)
        data = ProjectPublic.model_validate(project)
        data.progress = progress
        return data
