# 🌱 TerraPilot

**Autonomous AI agent for environmental validation using Qwen Cloud, MCP, and Alibaba Cloud.**

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-green.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-009688.svg)](https://fastapi.tiangolo.com)
[![Alibaba Cloud](https://img.shields.io/badge/Alibaba%20Cloud-Deployment%20Ready-ff6a00.svg)](alicloud/deployment.py)

## 🎯 Overview

TerraPilot is an **Autopilot Agent** that automates validation of Brazil's Rural Environmental Registry (CAR), reducing processing time from weeks to minutes while preserving human oversight for critical decisions.

The project is built for two simultaneous public-interest challenges:

- **Alibaba Cloud Global AI Hackathon** - Track 4: Autopilot Agent
- **haCARthon 2026** - ENAP/Governo Federal, CAR as a Digital Public Good

## ✨ Key Features

- 📱 **Offline-first PWA** for farmers to capture CAR data without connectivity.
- 🤖 **Qwen-powered validation** for autonomous environmental reasoning.
- 🔧 **MCP tool integration** for protected-area and compliance checks.
- 👩‍💼 **Human-in-the-loop dashboard** for analyst review.
- 📊 **Audit trail** through Alibaba Cloud Simple Log Service.
- 🔓 **Open source by design** under Apache 2.0.

## 🏗️ Architecture

```text
[Farmer PWA] ──sync──> [FastAPI Backend on ECS] ──prompt──> [Qwen/DashScope]
      │                         │                              │
      │                         ├──MCP tools───────────────────┘
      │                         ├──CAR memory──> [Tablestore + Geo Index]
      │                         ├──audit logs──> [SLS]
      │                         └──photos──────> [OSS]
      │
      └──────────────review events────────────> [Analyst Dashboard]
```

See the full technical architecture in [`docs/architecture.md`](docs/architecture.md).

## ☁️ Alibaba Cloud Deployment

**Status:** Code ready, awaiting account verification. Alibaba Cloud identity verification was submitted on **08/06/2026**. The ECS instance will be provisioned as soon as verification completes. All services were tested locally with mocks that mirror production behavior.

Services used:

- **ECS:** hosts the Dockerized FastAPI backend.
- **Tablestore:** stores CAR submissions, decisions, and geospatial index fields.
- **Simple Log Service (SLS):** records structured Qwen/MCP decisions for auditability.
- **Object Storage Service (OSS):** stores farmer evidence photos and documents.
- **Qwen via DashScope:** powers the Autopilot Agent reasoning flow.

Quick ECS deploy:

```bash
curl -fsSL https://raw.githubusercontent.com/kaiquetheodoro/TerraPilot/main/deploy/ecs-deploy.sh | bash
```

Required environment variables are documented in [`.env.example`](.env.example):

```text
ALIBABA_CLOUD_ACCESS_KEY_ID
ALIBABA_CLOUD_ACCESS_KEY_SECRET
ECS_INSTANCE_ID
ECS_REGION
TABLESTORE_ENDPOINT
TABLESTORE_INSTANCE
TABLESTORE_TABLE
SLS_ENDPOINT
SLS_PROJECT
SLS_LOGSTORE
OSS_ENDPOINT
OSS_BUCKET
QWEN_API_KEY
QWEN_MODEL
ENVIRONMENT
LOG_LEVEL
```

Proof files for the Alibaba Cloud hackathon form:

- Main proof: [`alicloud/deployment.py`](alicloud/deployment.py)
- Container proof: [`Dockerfile`](Dockerfile)
- ECS deploy automation: [`deploy/ecs-deploy.sh`](deploy/ecs-deploy.sh)

Hackathon URLs:

- `https://github.com/kaiquetheodoro/TerraPilot/blob/main/alicloud/deployment.py`
- `https://github.com/kaiquetheodoro/TerraPilot/blob/main/Dockerfile`
- `https://github.com/kaiquetheodoro/TerraPilot/tree/main/deploy`

## 🧰 Tech Stack

- **Backend:** FastAPI, Uvicorn, Pydantic v2
- **AI:** Qwen Cloud / DashScope
- **Agent tools:** Model Context Protocol (MCP)
- **Cloud:** Alibaba Cloud ECS, Tablestore, SLS, OSS
- **Frontend:** Progressive Web App and analyst dashboard
- **Automation:** Docker, Playwright demo recording

## 🚀 Quick Start

Prerequisites:

- Python 3.12+
- Git
- Alibaba Cloud account with Qwen/DashScope access for production mode

Install and run locally:

```bash
git clone https://github.com/kaiquetheodoro/TerraPilot.git
cd TerraPilot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python alicloud/deployment.py
```

Start the backend API:

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Start the PWA and dashboard:

```bash
cd frontend/pwa && python3 -m http.server 8080
cd frontend/dashboard && python3 -m http.server 8081
```

## 📖 Usage

Farmers use the PWA to fill property details, capture GPS coordinates, attach photos, save offline, and sync later. Analysts use the dashboard to review submissions flagged by the agent, inspect reasoning, and approve or reject with a recorded audit trail.

## 🔧 MCP Servers

TerraPilot includes custom MCP servers for environmental data. The protected areas server exposes `check_protected_area(lat, lng)` to detect overlap with conservation units, indigenous territories, and protected permanent preservation areas.

## 🧪 Testing

```bash
python alicloud/deployment.py
python3 -m py_compile alicloud/deployment.py
curl http://localhost:8000/health
```

Demo automation:

```bash
python3 tests/demo_with_recording.py --headless=false
```

## ⚠️ Known Limitations

Qwen and Alibaba Cloud production calls are credential-gated. Until account verification completes, TerraPilot runs local mocks with the same request/response shape used by the production integrations. Once credentials and ECS are active, the same environment variables switch the backend to production clients.

## 🗺️ Roadmap

- Qwen-VL integration for satellite image analysis.
- Connection to official SICAR APIs.
- Multi-language support for Portuguese, Spanish, and English.
- Edge-first workflows for rural offline operation.
- Federated learning across regions.

## 🤝 Contributing

Contributions are welcome. TerraPilot is designed as a Digital Public Good for environmental governance and rural inclusion.

## 📝 License

Apache License 2.0. See [`LICENSE`](LICENSE) for details.

## 🙏 Acknowledgments

Thanks to Alibaba Cloud, Qwen Cloud, the haCARthon organizers, ENAP, and the Brazilian public-sector teams working to modernize CAR.

## 📧 Contact

Repository: `github.com/kaiquetheodoro/TerraPilot`

Keywords: Qwen Cloud, MCP, Alibaba Cloud, Environmental AI, Autopilot Agent, CAR, Rural Development, Open Source, Digital Public Good.
