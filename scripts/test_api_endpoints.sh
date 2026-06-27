#!/bin/bash
# Testa todos os endpoints da API TerraPilot
# Uso: bash scripts/test_api_endpoints.sh

BASE="http://localhost:8001"

echo "🧪 Testando endpoints TerraPilot..."
echo ""

# 1. Health check
echo "1. GET /health"
curl -s "$BASE/health" | python -m json.tool
echo ""

# 2. Capability matrix
echo "2. GET /api/capability/matrix"
curl -s "$BASE/api/capability/matrix" | python -m json.tool | head -20
echo ""

# 3. Analyst templates
echo "3. GET /api/analyst/templates"
curl -s "$BASE/api/analyst/templates" | python -m json.tool
echo ""

# 4. Analyst prioritize — body é array JSON direto (list[Case])
echo "4. POST /api/analyst/prioritize"
curl -s -X POST "$BASE/api/analyst/prioritize" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "case_id": "1",
      "producer_name": "Seu Raimundo",
      "producer_id": "p1",
      "municipality": "Itaberaba-BA",
      "property_size_ha": 30,
      "modulo_fiscal": 1,
      "issue_code": "APP_RIVER_WIDTH",
      "days_since_notification": 5,
      "days_since_last_contact": 3,
      "historical_fix_rate": 0.6,
      "channel_reached": "whatsapp",
      "biome": "Caatinga",
      "has_pending_fines": false,
      "is_small_property": true
    }
  ]' | python -m json.tool
echo ""

# 5. Decision support
echo "5. POST /api/analyst/decision-support"
curl -s -X POST "$BASE/api/analyst/decision-support" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "123",
    "producer_name": "Seu Raimundo",
    "property_size_ha": 30,
    "municipality": "Itaberaba-BA",
    "state": "BA",
    "biome": "Caatinga",
    "issue_code": "APP_RIVER_WIDTH",
    "overlaps_uc": false,
    "uc_type": null,
    "overlaps_ti": false,
    "overlaps_quilombo": false,
    "overlaps_border": false,
    "has_pending_fines": false,
    "fine_count": 0,
    "consolidated_before_2008": true,
    "property_size_modulos": 1,
    "legal_issues": ["Art. 4º"]
  }' | python -m json.tool
echo ""

# 6. Detect patterns — body é array JSON direto (list[ErrorRecord])
echo "6. POST /api/analyst/detect-patterns"
curl -s -X POST "$BASE/api/analyst/detect-patterns" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "case_id": "1",
      "issue_code": "APP_RIVER_WIDTH",
      "producer_id": "p1",
      "municipality": "Itaberaba-BA",
      "biome": "Caatinga",
      "property_size_ha": 30,
      "modulo_fiscal": 1,
      "days_to_fix": 3,
      "fixed": true,
      "fix_attempt_count": 1,
      "channel": "whatsapp",
      "translated_notification_used": true
    }
  ]' | python -m json.tool
echo ""

# 7. Impact report
echo "7. POST /api/analyst/impact-report"
curl -s -X POST "$BASE/api/analyst/impact-report" \
  -H "Content-Type: application/json" \
  -d '{
    "analyst_id": "luana_01",
    "actions": [
      {
        "analyst_id": "luana_01",
        "case_id": "1",
        "producer_id": "p1",
        "producer_name": "Seu Raimundo",
        "action_type": "approved",
        "issue_code": "APP_RIVER_WIDTH",
        "channel": "whatsapp",
        "timestamp": "2026-06-26T10:00:00",
        "days_to_fix": 3,
        "fixed": true,
        "property_size_ha": 30,
        "credit_rural_value_brl": 15000
      }
    ],
    "benchmark": {
      "first_try_success_rate": 0.5,
      "avg_days_to_fix": 10
    }
  }' | python -m json.tool
echo ""

# 8. Unified view
echo "8. POST /api/analyst/unified-view"
curl -s -X POST "$BASE/api/analyst/unified-view" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "123",
    "producer_name": "Seu Raimundo",
    "producer_id": "p1",
    "municipality": "Itaberaba-BA",
    "property_size_ha": 30,
    "biome": "Caatinga",
    "sicar_data": {"status": "pending"},
    "sigef_data": null,
    "car_submission_date": "2026-01-15T10:00:00",
    "notifications": [],
    "producer_responses": [],
    "analyst_actions": [],
    "sent_messages": [],
    "received_messages": [],
    "pending_issues": [{"issue_code": "APP_RIVER_WIDTH"}]
  }' | python -m json.tool
echo ""

# 9. Render template
echo "9. POST /api/analyst/render-template"
curl -s -X POST "$BASE/api/analyst/render-template" \
  -H "Content-Type: application/json" \
  -d '{
    "issue_code": "APP_RIVER_WIDTH",
    "context": {
      "producer_name": "Seu Raimundo",
      "river_name": "Rio Paraguaçu",
      "required_m": 50
    },
    "channel": "whatsapp"
  }' | python -m json.tool
echo ""

echo "✅ Testes concluídos"
