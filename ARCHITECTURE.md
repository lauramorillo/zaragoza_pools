# Architecture and Decisions Document (Zaragoza Pools)

This document gathers the project's context, technical decisions, and general system architecture to facilitate future work for both human developers and AI assistants.

## 🎯 Project Goal
Provide an accessible web dashboard to query real-time and historical capacity of Zaragoza's public pools, helping users plan their visit by comparing crowd levels.

## 🏗️ System Architecture

The system is composed of the following main components deployed on Google Cloud Platform (GCP):

1. **Scraper (`scraper.py`)**: 
   - Automated scheduled task that extracts capacity information from the municipal website.
   - **Compute**: Cloud Functions (Python).
   - **Orchestration**: Cloud Scheduler (Periodic execution, e.g., every 15 mins).

2. **Database (Firestore)**:
   - Stores historical occupancy readings of all pools using documents. 
   - Advantage: Flexible NoSQL model, generous free tier, and easy integration with Cloud Functions.

3. **Dashboard / Frontend (`dashboard.py` + `templates/index.html`)**:
   - Lightweight service responsible for reading from Firestore and rendering a responsive web page.
   - **Backend**: Cloud Functions (Python) using `functions_framework.http`.
   - **Template Engine**: Jinja2.
   - **UI**: TailwindCSS (styles via CDN) and Chart.js (historical and comparative charts).

4. **Infrastructure as Code (IaC) (`terraform/`)**:
   - The entire deployment (functions, job schedulers, etc.) is defined using Terraform.
   - Allows exact reproduction of the environment, keeping infrastructure history in Git, and facilitates long-term maintenance.

## 📝 Architecture Decision Records (ADR)

Below are the most relevant decisions made during development:

*   **SERVERLESS TECHNOLOGY STACK**: Decided to use Google Cloud Functions instead of dedicated servers (VMs or persistent containers) due to the intermittent nature of the load (a scraper that runs every few minutes and sporadic web visits). This reduces costs to practically 0€ thanks to the free tier.
*   **SEPARATION OF SCRAPER AND DASHBOARD**: Instead of scraping on-demand for each user (which would saturate the source and be very slow), the scraper is a background process. The dashboard is simply a viewer for the Firestore database, guaranteeing instant load times for the end user.
*   **FLAT TIME-SERIES STORAGE IN FIRESTORE**: Each reading is saved as an individual document with its `timestamp`. For the current MVP this is optimal, although if the history grows massively over the years, a daily cleanup or aggregation strategy might be needed.
*   **FRAMEWORK-LESS FRONTEND DESIGN (NO REACT/VUE)**: For the current complexity of the application, injecting calculated data from the server (Server-Side Rendering with Jinja) and hydrating with a bit of Vanilla JS (Chart.js) was the fastest, most maintainable, and lightest solution.
*   **INCLUSION OF CURRENT DAY COMPARISON**: Added to observe the percentage capacity comparison (Occupancy Rate) in parallel for all pools in a user-friendly way using Chart.js, and dynamically adjusted using the `Europe/Madrid` timezone.

## 🤖 Best Practices for Collaborating with AI

For future developments working on this same project with the AI assistant:

1. **Keep this file updated**: If we add a different database, a native REST API, or change the model, we must reflect it here. 
2. **Explicit Context**: The AI can read this file when starting a new task to immerse itself in the entire stack and avoid making contradictory technology suggestions (like adding AWS Lambda when we are on GCP).
3. **Isolated Files Workflow**: Ask the AI for modifications or the addition of "isolated components" (for example: "Create a third function in `terraform/stats_function.tf` based on the dashboard one").
