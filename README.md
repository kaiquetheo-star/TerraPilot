# 🌱 TerraPilot

**Autonomous AI agent for environmental validation using Qwen Cloud + MCP**

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-green.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-009688.svg)](https://fastapi.tiangolo.com)

## 🎯 Overview

TerraPilot is an **Autopilot Agent** that automates validation of Brazil's Rural Environmental Registry (CAR), reducing processing time from weeks to minutes while maintaining human oversight for critical decisions.

Built for the **Global AI Hackathon Series with Qwen Cloud** - Track 4: Autopilot Agent

## ✨ Key Features

- 📱 **Offline-First PWA**: Farmers capture data without internet connectivity
- 🤖 **Qwen-Powered Validation**: Autonomous agent analyzes submissions using sophisticated reasoning
- 🔧 **MCP Tool Integration**: Dynamic tool invocation via Model Context Protocol
- 👩‍💼 **Human-in-the-Loop**: Complex cases route to environmental analysts
- 📊 **Audit Trail**: Complete observability with Alibaba Cloud SLS
- 🔓 **Open Source**: Apache 2.0 license, built as Digital Public Good

## 🏗️ Architecture
[Seu Raimundo - PWA] → [FastAPI on ECS] → [Qwen Agent] → [MCP Servers]
↓
[Dashboard Luana - HITL]
↓
[Tablestore + SLS - Observability]

### Tech Stack

- **Backend**: FastAPI, Uvicorn, Pydantic v2
- **AI**: Qwen Cloud API (qwen-max, qwen-plus, qwen-turbo)
- **Tools**: Model Context Protocol (MCP)
- **Database**: Alibaba Cloud Tablestore
- **Observability**: Alibaba Cloud Simple Log Service (SLS)
- **Storage**: Alibaba Cloud Object Storage Service (OSS)
- **Frontend**: Progressive Web App (PWA) with Tailwind CSS

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Alibaba Cloud account with Qwen Cloud API access
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/your-username/TerraPilot.git
cd TerraPilot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Edit .env with your Qwen Cloud API key

#Running Locally
1. Start Backend API:
cd src/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
API docs available at: http://localhost:8000/docs
2. Start PWA Frontend:
cd frontend/pwa
python3 -m http.server 8080
PWA available at: http://localhost:8080
3. Start Analyst Dashboard:
cd frontend/dashboard
python3 -m http.server 8081
Dashboard available at: http://localhost:8081

#📖 Usage
For Farmers (PWA)
Open PWA on mobile device
Fill property details (ID, area, vegetation type)
Capture GPS coordinates
Take photos of property
Save submission (works offline!)
Sync when internet available
For Analysts (Dashboard)
Open dashboard in browser
Review submissions flagged for manual review
View AI reasoning and confidence scores
Approve or reject with one click
All decisions logged for audit

#🔧 MCP Servers
TerraPilot includes custom MCP servers for environmental data:
Protected Areas Server
Provides tool: check_protected_area(lat, lng)
Queries ICMBio/Funai databases
Returns overlap analysis with protected areas
Supports UC, TI, APP detection

#🧪 Testing
# Run agent tests
cd src/agent
python3 orchestrator.py

# Test MCP client
python3 mcp_client.py

# Test API endpoint
curl -X POST http://localhost:8000/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "test_001",
    "gps_coords": [-15.7801, -47.9292],
    "area_ha": 50,
    "vegetation_type": "Cerrado"
  }'

#📊 API Endpoints

Method
Endpoint
Description
GET
/health
Health check
POST
/api/validate
Validate CAR submission
GET
/docs
OpenAPI documentation

#⚠️ Known Limitations
Qwen API Access
During development, we encountered 403 AccessDenied.Unpurchased errors. The system includes robust mock mode for development without API dependencies:
if not self.api_key or self.api_error:
    self.use_mock = True  # Seamless fallback

Once API access is resolved, system automatically switches to real Qwen calls.
ECS Deployment
Alibaba Cloud identity verification pending. Architecture designed for seamless migration with environment variables and Docker deployment scripts.

#🗺️ Roadmap
Qwen-VL integration for satellite image analysis
Connect to official SICAR APIs
Multi-language support (ES, EN)
Edge computing for fully offline operation
Federated learning across regions
Mobile app (React Native)

#🤝 Contributing
Contributions welcome! This is a Digital Public Good.
Fork the repository
Create feature branch (git checkout -b feature/AmazingFeature)
Commit changes (git commit -m 'Add AmazingFeature')
Push to branch (git push origin feature/AmazingFeature)
Open Pull Request

#📝 License
Apache License 2.0 - See LICENSE for details

#🙏 Acknowledgments
Alibaba Cloud for Qwen Cloud and hackathon platform
Brazilian Government for CAR system and environmental data
haCARthon organizers for problem definition
Open source community for tools and inspiration

#📧 Contact
Repository: github.com/kaiquetheo-star/TerraPilot
Blog: Technical posts on Dev.to
Hackathon: Devpost submission

#Built with ❤️ for environmental governance and rural inclusion
Keywords: Qwen Cloud, MCP, Alibaba Cloud, Environmental AI, Autopilot Agent, CAR, Rural Development, Open Source, Digital Public Good
