#!/bin/bash
set -euo pipefail

# ============================================================
# EcoMatch - Infraestructura como Código (AWS CLI)
# Todos los secretos se leen de variables de entorno o AWS Secrets Manager.
# NUNCA hardcodificar credenciales en este archivo.
# ============================================================

# --- Validación de variables de entorno requeridas ---
require_var() {
  if [[ -z "${!1:-}" ]]; then
    echo "ERROR: La variable de entorno '$1' no está definida."
    echo "Exportala antes de ejecutar este script."
    exit 1
  fi
}

require_var AWS_REGION
require_var ECS_CLUSTER_NAME
require_var ECS_SERVICE_NAME
require_var RDS_INSTANCE_ID
require_var RDS_SUBNET_GROUP
require_var EC2_SG_ID
require_var ECS_SUBNET_ID

REGION="${AWS_REGION}"

echo "=== Creando Infraestructura en AWS para EcoMatch ==="

# 1. Configuración de Seguridad Básica (Security Groups)
echo "Configurando reglas restrictivas en Security Groups..."
# Puerto 80 solo desde internet (frontend)
aws ec2 authorize-security-group-ingress \
  --group-id "${EC2_SG_ID}" \
  --protocol tcp --port 80 --cidr 0.0.0.0/0 \
  --region "${REGION}" || true
# Puerto 8080/8000 solo desde dentro de la VPC (backends + IA)
aws ec2 authorize-security-group-ingress \
  --group-id "${EC2_SG_ID}" \
  --protocol tcp --port 8080 --cidr 10.0.0.0/16 \
  --region "${REGION}" || true
aws ec2 authorize-security-group-ingress \
  --group-id "${EC2_SG_ID}" \
  --protocol tcp --port 8000 --cidr 10.0.0.0/16 \
  --region "${REGION}" || true

# 2. Base de Datos Relacional en la Nube (AWS RDS MySQL)
echo "Creando instancia de Base de Datos Relacional (AWS RDS)..."
# La contraseña se obtiene de AWS Secrets Manager (no se pasa por CLI)
DB_PASSWORD=$(aws secretsmanager get-secret-value \
  --secret-id "ecmatch/db-password" \
  --query SecretString --output text --region "${REGION}" | jq -r .password)

aws rds create-db-instance \
  --db-instance-identifier "${RDS_INSTANCE_ID}" \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --master-username root \
  --master-user-password "${DB_PASSWORD}" \
  --allocated-storage 20 \
  --db-subnet-group-name "${RDS_SUBNET_GROUP}" \
  --vpc-security-group-ids "${EC2_SG_ID}" \
  --region "${REGION}" || echo "RDS ya existe, continuando..."

# 3. Crear el Clúster de Orquestación (Amazon ECS)
echo "Creando Clúster de ECS..."
aws ecs create-cluster --cluster-name "${ECS_CLUSTER_NAME}" --region "${REGION}" || true

# 4. Registrar la Definición de la Tarea (Task Definition)
echo "Registrando definición de tareas desde manifiesto JSON..."
aws ecs register-task-definition --cli-input-json file://task-definition.json --region "${REGION}"

# 5. Crear el Servicio de ECS con Alta Disponibilidad y Escalabilidad
echo "Desplegando servicios en ECS Fargate..."
aws ecs create-service \
  --cluster "${ECS_CLUSTER_NAME}" \
  --service-name "${ECS_SERVICE_NAME}" \
  --task-definition ecmatch-task \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[${ECS_SUBNET_ID}],securityGroups=[${EC2_SG_ID}],assignPublicIp=ENABLED}" \
  --region "${REGION}" || echo "Servicio ya existe, continuando..."

echo "=== Infraestructura de Producción Creada Exitosamente ==="
