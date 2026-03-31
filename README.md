# Zaragoza Pools 🏊‍♂️📊

Un proyecto para consultar la afluencia y el aforo en tiempo real e histórico de las piscinas municipales de Zaragoza. 

Este sistema extrae automáticamente (mediante *scraping*) los datos de ocupación y los expone en un panel visual (Dashboard) que permite a los usuarios planificar mejor su visita comparando la afluencia de los recintos.

## 🚀 Características

- **Scraper Automático**: Una Cloud Function programada que extrae la capacidad periódicamente.
- **Almacenamiento Histórico**: Guarda las lecturas en Cloud Firestore (NoSQL).
- **Dashboard Visual**: Interfaz web rápida renderizada desde el servidor con Jinja2, TailwindCSS y gráficos interactivos usando Chart.js.
- **Infraestructura como Código (IaC)**: Despliegue 100% automatizado mediante Terraform y Google Cloud Platform (GCP).

## 📁 Estructura del Proyecto

El proyecto está dividido principalmente en dos carpetas para separar el código de la infraestructura:

- `src/`: Contiene el código fuente de la aplicación en Python.
  - `scraper.py`: Lógica para la extracción de datos.
  - `dashboard.py`: Lógica del servidor web para visualizar los datos.
  - `templates/`: Plantillas HTML (Jinja2) del panel visual.
  - `requirements.txt`: Dependencias de Python necesarias.
- `terraform/`: Definiciones de infraestructura de Terraform para desplegar los recursos (funciones, base de datos, scheduler) en GCP de forma reproducible.
- `ARCHITECTURE.md`: Documento detallado sobre decisiones técnicas y arquitectura.

## 🛠 Instalación y Despliegue

### Requisitos Previos
1. Tener cuenta en Google Cloud Platform (GCP) con un proyecto creado.
2. Instalar y configurar [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install).
3. Instalar [Terraform](https://developer.hashicorp.com/terraform/downloads).

### Despliegue

Toda la infraestructura se despliega con Terraform de manera automática. El código de la carpeta `src/` será empaquetado y subido a GCP para correr como Cloud Functions de 2ª Generación.

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

*(Asegúrate de configurar las variables necesarias como tu `project_id` de Google Cloud y establecer un bucket de estado si aplicas el despliegue a un entorno remoto).*

## 💻 Desarrollo Local

Para trabajar en el código de Python localmente:

```bash
# Crear entorno virtual e instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install -r src/requirements.txt
```
