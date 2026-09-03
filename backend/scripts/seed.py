"""Seed script for ReVínculo — generates demo data."""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.enums import (
    MaterialCategoryEnum,
    MaterialConditionEnum,
    NeedPriorityEnum,
    OrganizationTypeEnum,
    RoleEnum,
)
from app.models.models import (
    CollectorProfile,
    Material,
    Need,
    Organization,
    Post,
    Project,
    User,
)
from app.utils.hazardous import determine_risk_level


def run() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # --- Admin ---
    admin = User(name="Admin", email="admin@revinculo.cl", password_hash=hash_password("admin123"), role=RoleEnum.ADMIN, commune="Santiago")
    db.add(admin)

    # --- 10 personas naturales ---
    people = []
    personas_data = [
        ("María González", "maria@revinculo.cl", "Providencia", -33.45, -70.66),
        ("Pedro Martínez", "pedro@revinculo.cl", "Maipú", -33.50, -70.76),
        ("Ana López", "ana@revinculo.cl", "La Florida", -33.52, -70.58),
        ("Carlos Díaz", "carlos@revinculo.cl", "Ñuñoa", -33.46, -70.60),
        ("Patricia Rojas", "patricia@revinculo.cl", "Las Condes", -33.40, -70.57),
        ("Hugo Vera", "hugo@revinculo.cl", "San Miguel", -33.48, -70.66),
        ("Lucía Fernández", "lucia@revinculo.cl", "Pudahuel", -33.45, -70.73),
        ("Roberto Silva", "roberto@revinculo.cl", "Recoleta", -33.42, -70.64),
        ("Carmen Ruiz", "carmen@revinculo.cl", "Estación Central", -33.45, -70.70),
        ("Diego Torres", "diego@revinculo.cl", "Quilicura", -33.37, -70.72),
    ]
    for name, email, commune, lat, lon in personas_data:
        u = User(name=name, email=email, password_hash=hash_password("pass12345"), role=RoleEnum.NATURAL, commune=commune, latitude=lat, longitude=lon)
        db.add(u)
        people.append(u)

    # --- 8 recolectores ---
    collectors = []
    collectors_data = [
        ("Jorge Ramírez", "jorge@revinculo.cl", "Camioneta", 500, 30, ["WOOD", "METAL", "FURNITURE"], -33.44, -70.65, "Santiago Centro"),
        ("Felipe Castro", "felipe@revinculo.cl", "Camión", 2000, 50, ["CONSTRUCTION", "BRICKS", "METAL"], -33.46, -70.68, "Ñuñoa"),
        ("Manuel Jara", "manuel@revinculo.cl", "Furgón", 800, 25, ["WOOD", "CARDBOARD", "PLASTIC"], -33.43, -70.62, "Providencia"),
        ("Ricardo Soto", "ricardo@revinculo.cl", "Camioneta", 600, 40, ["FURNITURE", "TEXTILE", "TOOLS"], -33.48, -70.60, "La Florida"),
        ("Tomás Aguirre", "tomas@revinculo.cl", "Moto con sidecar", 150, 15, ["CARDBOARD", "PLASTIC", "TEXTILE"], -33.50, -70.72, "Maipú"),
        ("Andrés Morales", "andres@revinculo.cl", "Camión", 3000, 60, ["METAL", "WOOD", "CONSTRUCTION"], -33.41, -70.55, "Las Condes"),
        ("Pablo Núñez", "pablo@revinculo.cl", "Furgón", 1000, 35, ["WOOD", "FURNITURE", "DOORS_WINDOWS"], -33.47, -70.69, "San Miguel"),
        ("Sebastián Ríos", "sebastian@revinculo.cl", "Camioneta", 700, 30, ["PLASTIC", "METAL", "TOOLS"], -33.39, -70.71, "Quilicura"),
    ]
    for name, email, vehicle, cap, radius, mats, lat, lon, commune in collectors_data:
        u = User(name=name, email=email, password_hash=hash_password("pass12345"), role=RoleEnum.COLLECTOR, can_collect=True, commune=commune, latitude=lat, longitude=lon)
        db.add(u)
        collectors.append(u)
    db.flush()
    for (name, email, vehicle, cap, radius, mats, lat, lon, commune), u in zip(collectors_data, collectors):
        cp = CollectorProfile(user_id=u.id, vehicle_type=vehicle, max_weight_kg=cap, radius_km=radius, available=True, materials_accepted=",".join(mats), description=f"Recolector con {vehicle}")
        db.add(cp)

    # --- 5 organizaciones ---
    orgs = []
    orgs_data = [
        ("Fundación Construyendo Juntos", "fundacion@revinculo.cl", OrganizationTypeEnum.FOUNDATION, "Mobiliario comunitario para sedes sociales", "Providencia", -33.45, -70.66),
        ("ONG Recicla Ciudad", "ong@revinculo.cl", OrganizationTypeEnum.NGO, "Promoción de reciclaje urbano", "Ñuñoa", -33.46, -70.60),
        ("Taller de Madera Renacer", "taller@revinculo.cl", OrganizationTypeEnum.WORKSHOP, "Fabricación de muebles con madera recuperada", "San Miguel", -33.48, -70.66),
        ("Comunidad Verde", "comunidad@revinculo.cl", OrganizationTypeEnum.COMMUNITY, "Huertos comunitarios y construcción sostenible", "La Florida", -33.52, -70.58),
        ("Fundación Techo Chile", "techo@revinculo.cl", OrganizationTypeEnum.FOUNDATION, "Construcción de viviendas de emergencia", "Maipú", -33.50, -70.76),
    ]
    for name, email, otype, desc, commune, lat, lon in orgs_data:
        u = User(name=name, email=email, password_hash=hash_password("pass12345"), role=RoleEnum.ORGANIZATION, commune=commune, latitude=lat, longitude=lon)
        db.add(u)
        db.flush()
        org = Organization(owner_id=u.id, name=name, type=otype.value, description=desc, commune=commune, latitude=lat, longitude=lon, verified=True)
        db.add(org)
        orgs.append(org)

    db.flush()

    # --- Proyectos ---
    p1 = Project(organization_id=orgs[0].id, title="Mobiliario comunitario", description="Construcción de mesas y sillas para sedes sociales", status="ACTIVE", commune="Providencia", latitude=-33.45, longitude=-70.66)
    p2 = Project(organization_id=orgs[1].id, title="Puntos limpios", description="Instalación de puntos de reciclaje", status="ACTIVE", commune="Ñuñoa", latitude=-33.46, longitude=-70.60)
    p3 = Project(organization_id=orgs[2].id, title="Muebles recuperados", description="Fabricación de muebles con madera usada", status="ACTIVE", commune="San Miguel", latitude=-33.48, longitude=-70.66)
    p4 = Project(organization_id=orgs[3].id, title="Huerto comunitario", description="Construcción de huertos urbanos", status="ACTIVE", commune="La Florida", latitude=-33.52, longitude=-70.58)
    db.add_all([p1, p2, p3, p4])
    db.flush()

    # --- 20 publicaciones ---
    posts = []
    post_titles = [
        ("Terminé una remodelación y tengo 20 tablas de madera", "OFFER", "WOOD"),
        ("Puerta de cedro en buen estado", "OFFER", "DOORS_WINDOWS"),
        ("Ladrillos sobrantes de obra", "OFFER", "BRICKS"),
        ("Cartón acumulado de mudanza", "OFFER", "CARDBOARD"),
        ("Sillas de oficina que ya no uso", "OFFER", "FURNITURE"),
        ("Tubos de PVC", "OFFER", "PLASTIC"),
        ("Chapas de metal", "OFFER", "METAL"),
        ("Madera de palets", "OFFER", "WOOD"),
        ("Ventanas con marco de aluminio", "OFFER", "DOORS_WINDOWS"),
        ("Herramientas de carpintería", "OFFER", "TOOLS"),
        ("Telas y cortinas usadas", "OFFER", "TEXTILE"),
        ("Tablas de pino", "OFFER", "WOOD"),
        ("Need: Madera para mesas", "NEED", "WOOD"),
        ("Need: Ladrillos para construcción", "NEED", "BRICKS"),
        ("Need: Herramientas para taller", "NEED", "TOOLS"),
        ("Need: Muebles para sede", "NEED", "FURNITURE"),
        ("Impact: Mesas construidas", "IMPACT", "WOOD"),
        ("Impact: Huerto terminado", "IMPACT", "CONSTRUCTION"),
        ("Project: Mobiliario comunitario", "PROJECT", "WOOD"),
        ("Project: Puntos limpios", "PROJECT", "PLASTIC"),
    ]
    for i, (title, ptype, cat) in enumerate(post_titles):
        author = people[i % len(people)]
        post = Post(author_id=author.id, type=ptype, title=title, description=f"Descripción de {title}", latitude=author.latitude, longitude=author.longitude, commune=author.commune, status="ACTIVE")
        db.add(post)
        posts.append(post)

    db.flush()

    # --- 20 materiales ---
    materials_data = [
        (people[0], "20 tablas de madera", MaterialCategoryEnum.WOOD, 20, "unit", MaterialConditionEnum.REUSABLE, 120, posts[0].id),
        (people[1], "Puerta de cedro", MaterialCategoryEnum.DOORS_WINDOWS, 1, "unit", MaterialConditionEnum.GOOD, 25, posts[1].id),
        (people[2], "Ladrillos", MaterialCategoryEnum.BRICKS, 200, "unit", MaterialConditionEnum.GOOD, 800, posts[2].id),
        (people[3], "Cartón", MaterialCategoryEnum.CARDBOARD, 50, "kg", MaterialConditionEnum.REUSABLE, 50, posts[3].id),
        (people[4], "Sillas de oficina", MaterialCategoryEnum.FURNITURE, 6, "unit", MaterialConditionEnum.GOOD, 30, posts[4].id),
        (people[5], "Tubos de PVC", MaterialCategoryEnum.PLASTIC, 10, "unit", MaterialConditionEnum.REUSABLE, 15, posts[5].id),
        (people[6], "Chapas de metal", MaterialCategoryEnum.METAL, 30, "kg", MaterialConditionEnum.REUSABLE, 30, posts[6].id),
        (people[7], "Madera de palets", MaterialCategoryEnum.WOOD, 15, "unit", MaterialConditionEnum.REPAIRABLE, 90, posts[7].id),
        (people[8], "Ventanas aluminio", MaterialCategoryEnum.DOORS_WINDOWS, 4, "unit", MaterialConditionEnum.GOOD, 60, posts[8].id),
        (people[9], "Herramientas carpintería", MaterialCategoryEnum.TOOLS, 8, "unit", MaterialConditionEnum.GOOD, 20, posts[9].id),
        (people[0], "Telas y cortinas", MaterialCategoryEnum.TEXTILE, 12, "unit", MaterialConditionEnum.REUSABLE, 8, posts[10].id),
        (people[1], "Tablas de pino", MaterialCategoryEnum.WOOD, 18, "unit", MaterialConditionEnum.GOOD, 100, posts[11].id),
        (people[2], "Material peligroso - aceite contaminado", MaterialCategoryEnum.OTHER, 5, "litro", MaterialConditionEnum.UNKNOWN, 5, None),
        (people[3], "Madera contrachapada", MaterialCategoryEnum.WOOD, 10, "unit", MaterialConditionEnum.REUSABLE, 60, None),
        (people[4], "Bloques de cemento", MaterialCategoryEnum.CONSTRUCTION, 100, "unit", MaterialConditionEnum.GOOD, 500, None),
        (people[5], "Pallets industriales", MaterialCategoryEnum.WOOD, 8, "unit", MaterialConditionEnum.REPAIRABLE, 48, None),
        (people[6], "Tela de toldo", MaterialCategoryEnum.TEXTILE, 3, "unit", MaterialConditionEnum.REPAIRABLE, 15, None),
        (people[7], "Tubería de cobre", MaterialCategoryEnum.METAL, 20, "kg", MaterialConditionEnum.REUSABLE, 20, None),
        (people[8], "Cajas de cartón grandes", MaterialCategoryEnum.CARDBOARD, 30, "unit", MaterialConditionEnum.GOOD, 10, None),
        (people[9], "Plástico PET", MaterialCategoryEnum.PLASTIC, 40, "kg", MaterialConditionEnum.RECYCLE_ONLY, 40, None),
    ]
    materials = []
    for owner, name, cat, qty, unit, cond, weight, post_id in materials_data:
        risk = determine_risk_level(cat.value, name)
        m = Material(
            owner_id=owner.id,
            post_id=post_id,
            name=name,
            category=cat.value,
            quantity=qty,
            unit=unit,
            condition=cond.value,
            estimated_weight_kg=weight,
            risk_level=risk,
            requires_pickup=True,
            status="AVAILABLE",
        )
        db.add(m)
        materials.append(m)

    db.flush()

    # --- 12 necesidades ---
    needs_data = [
        (orgs[0], p1, MaterialCategoryEnum.WOOD, "Tablas de madera", 15, "unit", NeedPriorityEnum.HIGH),
        (orgs[0], p1, MaterialCategoryEnum.FURNITURE, "Mesas", 5, "unit", NeedPriorityEnum.MEDIUM),
        (orgs[1], p2, MaterialCategoryEnum.PLASTIC, "Contenedores", 10, "unit", NeedPriorityEnum.MEDIUM),
        (orgs[1], p2, MaterialCategoryEnum.CARDBOARD, "Cartón", 100, "kg", NeedPriorityEnum.LOW),
        (orgs[2], p3, MaterialCategoryEnum.WOOD, "Madera para muebles", 30, "unit", NeedPriorityEnum.URGENT),
        (orgs[2], p3, MaterialCategoryEnum.TOOLS, "Herramientas", 10, "unit", NeedPriorityEnum.HIGH),
        (orgs[3], p4, MaterialCategoryEnum.CONSTRUCTION, "Bloques", 150, "unit", NeedPriorityEnum.MEDIUM),
        (orgs[3], p4, MaterialCategoryEnum.WOOD, "Tablas para canteros", 12, "unit", NeedPriorityEnum.MEDIUM),
        (orgs[4], None, MaterialCategoryEnum.METAL, "Chapas para viviendas", 50, "kg", NeedPriorityEnum.HIGH),
        (orgs[4], None, MaterialCategoryEnum.DOORS_WINDOWS, "Puertas", 10, "unit", NeedPriorityEnum.URGENT),
        (orgs[0], p1, MaterialCategoryEnum.BRICKS, "Ladrillos", 100, "unit", NeedPriorityEnum.LOW),
        (orgs[2], p3, MaterialCategoryEnum.TEXTILE, "Tela para tapizar", 8, "unit", NeedPriorityEnum.LOW),
    ]
    for org, proj, cat, name, qty, unit, prio in needs_data:
        n = Need(
            organization_id=org.id,
            project_id=proj.id if proj else None,
            material_category=cat.value,
            material_name=name,
            quantity_required=qty,
            quantity_received=0,
            unit=unit,
            priority=prio.value,
            status="OPEN",
        )
        db.add(n)

    db.commit()
    db.close()
    print("Seed completado: 1 admin, 10 personas, 8 recolectores, 5 organizaciones, 4 proyectos, 20 posts, 20 materiales, 12 necesidades.")
    print("Incluye: persona con madera, ONG que necesita madera, recolector compatible, material peligroso, match listo para demo.")


if __name__ == "__main__":
    run()
