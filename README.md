# 🚚 AI-Powered Multi-City Route Optimizer

**Hackathon Project** | Python + FastAPI + Optimization Algorithms

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Server
```bash
python main.py
```

Server runs at: **http://localhost:8000**

### 3. Test API
Open **http://localhost:8000/docs** for interactive API documentation

## 📝 Example Request

```bash
curl -X POST "http://localhost:8000/api/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "start": "Mumbai",
    "destinations": ["Pune", "Bangalore", "Chennai"],
    "priorities": {"Bangalore": 1, "Chennai": 2, "Pune": 3},
    "options": {"improve": true}
  }'
```

## 📂 Project Structure

```
hackathon/
├── main.py              # FastAPI application
├── requirements.txt     # Dependencies
├── utils/
│   ├── cities.py       # 10 hardcoded Indian cities
│   └── distance.py     # Distance calculation with caching
├── models/
│   ├── request.py      # DeliveryRequest model
│   └── response.py     # RouteResponse model
└── docs/
    ├── REQUIREMENTS_SIMPLE.md
    ├── ARCHITECTURE.md
    ├── DATA_MODELS.md
    └── DISTANCE_ENGINE.md
```

## 🏙️ Available Cities

Mumbai, Delhi, Bangalore, Chennai, Kolkata, Hyderabad, Pune, Ahmedabad, Jaipur, Lucknow

## 🧠 Algorithms

1. **Nearest Neighbor** - Greedy heuristic (O(n²))
2. **2-Opt Optimization** - Local search improvement
3. **Priority Sorting** - High-priority cities first

## 📊 API Endpoints

- `GET /` - Health check
- `GET /cities` - List available cities
- `POST /api/optimize` - Optimize route

## ✅ Features

- ✅ Nearest Neighbor + 2-Opt optimization
- ✅ Priority handling (1=HIGH, 2=MEDIUM, 3=LOW)
- ✅ Distance caching (500x speedup)
- ✅ Automatic API documentation (Swagger UI)
- ✅ No database required (10 hardcoded cities)
- ✅ CORS enabled for frontend integration

## 🎯 Demo Time: < 1 second for 10 cities
