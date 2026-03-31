# Zaragoza Pools 🏊‍♂️📊

A project to query the real-time and historical occupancy and capacity of the municipal public pools in Zaragoza.

This system automatically extracts (via *scraping*) occupancy data and exposes it on a visual Dashboard, allowing users to better plan their visit by comparing the crowd levels across different facilities.

## 🚀 Features

- **Automated Scraper**: A scheduled Cloud Function that periodically extracts capacity data.
- **Historical Storage**: Saves readings in Cloud Firestore (NoSQL) for historical analysis.
- **Visual Dashboard**: Fast, server-side rendered web interface using Jinja2, TailwindCSS, and interactive charts via Chart.js.
- **Infrastructure as Code (IaC)**: 100% automated deployment using Terraform and Google Cloud Platform (GCP).

## 📁 Project Structure

The project is divided into two main folders to separate application code from infrastructure:

- `src/`: Contains the Python source code for the application.
  - `scraper.py`: Logic for data extraction.
  - `dashboard.py`: Web server logic to visualize the data.
  - `templates/`: HTML templates (Jinja2) for the visual dashboard.
  - `requirements.txt`: Required Python dependencies.
- `terraform/`: Terraform infrastructure definitions to reproducibly deploy resources (functions, database, scheduler) on GCP.
- `ARCHITECTURE.md`: Detailed document regarding technical decisions and architecture.

## 🛠 Setup and Deployment

### Prerequisites
1. Have a Google Cloud Platform (GCP) account with a created project.
2. Install and configure the [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install).
3. Install [Terraform](https://developer.hashicorp.com/terraform/downloads).

### Deployment

The entire infrastructure is automatically deployed using Terraform. The code inside the `src/` folder will be packaged and uploaded to GCP to run as 2nd Generation Cloud Functions.

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

*(Make sure to configure necessary variables like your Google Cloud `project_id` and set up a state bucket if you deploy to a remote environment).*

## 💻 Local Development

To work on the Python code locally:

```bash
# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r src/requirements.txt
```
