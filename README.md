# AI-Powered Traffic Violation Detection System

This project is an AI-powered traffic violation detection system designed to automate and streamline traffic enforcement. This system allows users to upload an image of a vehicle, which then leverages Google's Gemini 2.5 Flash model within a Python/FastAPI microservice to identify license plates and vehicle types, automatically logging violations. Built with a Next.js frontend, this project aims to make violation reporting faster and more accurate through a robust microservices architecture.

## Features

*   *AI-Powered Image Analysis:* Uses Google's Gemini 2.5 Flash to identify vehicle license plates and types from images.
*   *Automated Violation Logging:* Automatically logs violation details into a Firestore database.
*   *Web-Based Interface:* A modern, user-friendly interface built with Next.js for uploading images and viewing violation data.
*   *Microservices Architecture:* A scalable and maintainable architecture with separate services for the frontend, agent logic, and vision analysis.

## Architecture

The system is built on a microservices architecture, composed of a frontend web application, an agent backend for business logic, and a vision backend for AI-powered image analysis.

mermaid
graph TD
    A[User] -->|Uploads Image| B(Frontend - Next.js);
    B -->|POST /api/analyze| C(Agent Backend - FastAPI);
    C -->|POST /analyze_image| D(Vision Backend - FastAPI);
    D -->|Analyzes Image| E(Google Gemini 2.5 Flash);
    E -->|Returns Analysis| D;
    D -->|Returns JSON| C;
    C -->|Logs Violation| F(Firestore Database);
    C -->|Returns Violation ID| B;
    B -->|Displays Result| A;


For a more detailed explanation, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Technology Stack

*   *Frontend:* Next.js, React, TypeScript, Tailwind CSS
*   *Backend:* Python, FastAPI
*   *Database:* Google Cloud Firestore
*   *AI/ML:* Google Generative AI API (gemini-2.5-flash)
*   *Deployment:* Docker

## Getting Started

### Prerequisites

*   Node.js and npm
*   Python 3.8+ and pip
*   Access to Google Cloud Platform for Firestore and Generative AI APIs.
*   Docker (optional, for containerized deployment)

### Installation & Setup

1.  *Clone the repository:*
    bash
    git clone <your-repository-url>
    cd <your-repository-name>
    

2.  *Setup Environment Variables:*
    You will need to set up environment variables for Google Cloud credentials. Create a .env file in the root of the agent-backend and vision-backend directories with the necessary credentials.

3.  *Frontend:*
    bash
    cd frontend
    npm install
    npm run dev
    
    The frontend will be available at http://localhost:3000.

4.  *Agent Backend:*
    bash
    cd agent-backend
    # It is recommended to create a virtual environment
    python -m venv venv
    source venv/bin/activate # on Windows use `venv\Scripts\activate`
    pip install -r requirements.txt # You will need to create this file
    uvicorn server:app --reload --port 8001
    
    The agent backend will be available at http://localhost:8001.

5.  *Vision Backend:*
    bash
    cd vision-backend
    # It is recommended to create a virtual environment
    python -m venv venv
    source venv/bin/activate # on Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    uvicorn server:app --reload --port 8002
    
    The vision backend will be available at http://localhost:8002.

## Project Structure


.
├── agent-backend/      # FastAPI service for business logic and orchestration
├── vision-backend/     # FastAPI service for AI image analysis
├── frontend/           # Next.js frontend application
├── infra/              # Deployment scripts (e.g., Docker, shell scripts)
├── ARCHITECTURE.md     # Detailed architecture documentation
└── README.md           # This file
