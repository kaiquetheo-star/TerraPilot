
```markdown
# TerraPilot Demo Script Guide

**Video Length**: 2:45 - 3:00 minutes  
**Format**: Screen recording with voiceover  
**Target Audience**: Hackathon judges, government officials, environmental NGOs

---

## 🎬 Demo Structure

### Opening Hook (0:00 - 0:15)

**Visual**: Split screen showing:
- Left: PWA on mobile device (offline mode)
- Right: Dashboard on desktop

**Voiceover Script**:
> "Every year, Brazil's environmental agencies process over 6 million rural property registrations. Each one requires manual validation against protected areas, vegetation types, and legal requirements. The backlog stretches into months, leaving small farmers in limbo and forests unprotected."

---

### Problem Statement (0:15 - 0:30)

**Visual**: 
- Show crowded government office (stock image or illustration)
- Overlay text: "Average wait time: 3-6 months"
- Cut to rural farmer looking at phone with "No Service" indicator

**Voiceover Script**:
> "Small farmers in remote areas often lack internet connectivity, making online submission impossible. They travel hours to government offices, only to face long queues and bureaucratic delays. Meanwhile, illegal deforestation continues unchecked."

---

### Solution Introduction (0:30 - 0:45)

**Visual**:
- TerraPilot logo animation
- Quick cuts of: PWA form, GPS capture, photo upload
- Dashboard showing real-time validations

**Voiceover Script**:
> "TerraPilot is an autonomous validation agent that works offline, processes submissions instantly, and maintains human oversight for critical decisions. Built on Qwen Cloud and Alibaba Cloud infrastructure, it's designed for Brazil's rural reality."

---

### Live Demo: Farmer Experience (0:45 - 1:30)

**Visual**: Screen recording of PWA on mobile device

**Step 1: Offline Data Collection (0:45 - 1:00)**
- Show "OFFLINE" status indicator (red)
- Fill form: "ID: raimundo_001, Area: 50 ha, Vegetation: Cerrado"
- Capture GPS coordinates
- Upload 3 photos of property

**Voiceover Script**:
> "Meet Raimundo, a small farmer in Goiás. He opens TerraPilot on his phone—no internet required. He enters his property details, captures GPS coordinates, and takes photos of his land. Everything is stored locally."

**Step 2: Automatic Sync (1:00 - 1:15)**
- Show connection restored (green indicator)
- Click "Sincronizar Agora"
- Progress bar fills: "Sincronizando 1/1... Concluído!"

**Voiceover Script**:
> "When Raimundo reaches an area with connectivity, TerraPilot automatically syncs his submission to the cloud. The entire process takes seconds, not hours."

**Step 3: AI Validation (1:15 - 1:30)**
- Show backend terminal with logs
- Highlight MCP tool invocation: `check_protected_area(lat, lng)`
- Show Qwen reasoning output

**Voiceover Script**:
> "Behind the scenes, our Qwen-powered agent validates the submission. It queries protected area databases using MCP, analyzes vegetation patterns, and generates a confidence score with detailed reasoning."

---

### Live Demo: Analyst Experience (1:30 - 2:15)

**Visual**: Screen recording of Luana Dashboard

**Step 1: Priority Queue (1:30 - 1:45)**
- Show dashboard with 6 submissions
- Highlight color-coded priority badges (🔴 High, 🟡 Medium, 🟢 Low)
- Sort by priority

**Voiceover Script**:
> "Environmental analyst Luana logs into her dashboard. Submissions are automatically prioritized by AI confidence score. High-priority cases requiring human review appear at the top."

**Step 2: Detailed Review (1:45 - 2:00)**
- Click "Ver Detalhes" on high-priority submission
- Show modal with:
  - Property details
  - AI reasoning
  - Confidence score (45%)
  - Protected area map

**Voiceover Script**:
> "Luana reviews a flagged submission. The AI explains its reasoning: 'Área de 120 hectares próxima a Terra Indígena. Requer validação presencial.' She can see the GPS coordinates, photos, and AI analysis all in one place."

**Step 3: Human Decision (2:00 - 2:15)**
- Click "✅ Aprovar" button
- Show button animation (green pulse)
- Toast notification: "Cadastro aprovado!"
- Status updates to "Aprovado"

**Voiceover Script**:
> "After reviewing the evidence, Luana approves the submission with one click. The decision is logged with full audit trail, and the farmer receives instant notification. Total time: 2 minutes instead of 2 months."

---

### Technical Architecture (2:15 - 2:45)

**Visual**: Animated architecture diagram

**Components to highlight**:
1. PWA (offline-first)
2. FastAPI backend
3. Qwen Agent with MCP
4. Alibaba Cloud services (ECS, Tablestore, SLS)
5. Human-in-the-loop dashboard

**Voiceover Script**:
> "TerraPilot's architecture is built for scale and reliability. The offline-first PWA ensures data capture in remote areas. FastAPI handles thousands of concurrent validations. Qwen's reasoning capabilities are extended through MCP tool integration. Alibaba Cloud provides enterprise-grade infrastructure with automatic scaling."

---

### Impact & Future Vision (2:45 - 3:00)

**Visual**: 
- Split screen: Before (long queue) vs After (instant approval)
- Overlay statistics:
  - "Validation time: 6 months → 2 minutes"
  - "Cost per validation: R$150 → R$2"
  - "Coverage: Urban → Rural"

**Voiceover Script**:
> "TerraPilot transforms environmental governance. Validation time drops from months to minutes. Costs plummet. Rural farmers gain access. Forests gain protection. This is the future of digital public goods—open source, scalable, and built for Brazil's unique challenges."

**Closing Visual**:
- TerraPilot logo
- GitHub repository link
- "Built with Qwen Cloud | Track 4: Autopilot Agent"

**Voiceover Script**:
> "TerraPilot: Autonomous validation, human oversight, environmental protection. Open source and ready for deployment. Visit our GitHub to learn more."

---

## 🎥 Production Checklist

### Pre-Recording

- [ ] Clean browser (clear bookmarks, disable extensions)
- [ ] Set screen resolution to 1920x1080
- [ ] Disable notifications (Do Not Disturb mode)
- [ ] Prepare test data:
  - Farmer ID: raimundo_001
  - Area: 50 ha
  - Vegetation: Cerrado
  - GPS: -15.7801, -47.9292
  - Photos: 3 sample images
- [ ] Test all flows end-to-end
- [ ] Prepare script (print or teleprompter)

### Recording Setup

**Software Options**:
- **OBS Studio** (free, professional)
- **Loom** (easy, cloud-based)
- **ScreenFlow** (Mac, paid)
- **Windows Game Bar** (built-in, basic)

**Audio**:
- Use external microphone (even basic USB mic)
- Record in quiet room
- Test audio levels before recording
- Speak slowly and clearly

**Video**:
- Record at 1080p, 30fps minimum
- Use mouse highlighter for clarity
- Zoom in on important UI elements
- Smooth mouse movements (no erratic clicking)

### Post-Production

**Editing Software**:
- **DaVinci Resolve** (free, professional)
- **iMovie** (Mac, free)
- **CapCut** (free, easy)
- **Adobe Premiere Rush** (paid, mobile-friendly)

**Editing Checklist**:
- [ ] Trim to 3:00 maximum
- [ ] Add fade transitions between sections
- [ ] Normalize audio levels
- [ ] Add text overlays for key statistics
- [ ] Include GitHub URL in final frame
- [ ] Export as MP4, H.264 codec
- [ ] Upload to YouTube (unlisted) or Vimeo

---

## 📊 Key Talking Points

### For Government Officials

- "Reduz tempo de validação de 6 meses para 2 minutos"
- "Custo por validação: R$150 → R$2"
- "Cobertura total: zonas urbanas e rurais"
- "Auditoria completa com trilha de decisões"

### For Technical Judges

- "MCP integration for dynamic tool discovery"
- "Offline-first PWA with IndexedDB queue"
- "Multi-model fallback strategy for resilience"
- "Human-in-the-loop with confidence scoring"

### For Environmental NGOs

- "Proteção florestal em tempo real"
- "Acesso democratizado para pequenos produtores"
- "Código aberto e replicável"
- "Parceria com comunidades rurais"

---