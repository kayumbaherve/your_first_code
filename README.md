# AI Interior Design Assistant MVP

A sophisticated AI-powered interior design assistant with room scanning, AI recommendations, 3D visualization, and virtual staging capabilities.

## 🚀 Features

- **Room Scanning**: Advanced computer vision for room analysis and object detection
- **AI Recommendations**: Machine learning-powered design suggestions based on room characteristics and user preferences
- **3D Visualization**: Interactive 3D room rendering with furniture placement and lighting simulation
- **Virtual Staging**: AR-powered virtual staging for realistic room previews

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **Room Scanner Module**: OpenCV and MediaPipe for image processing
- **AI Recommender**: TensorFlow/PyTorch for ML-based recommendations
- **Virtual Stager**: Advanced image processing and AR capabilities
- **RESTful APIs**: Comprehensive API endpoints for all features

### Frontend (React + Three.js)
- **3D Viewer**: WebGL-based 3D room visualization
- **Room Scanner Interface**: Camera integration and image upload
- **Dashboard**: Project management and user interface
- **Responsive Design**: Mobile-first approach

### Database (PostgreSQL)
- User management and authentication
- Room data and project storage
- Furniture catalog and 3D models
- Design recommendations and history

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **OpenCV**: Computer vision and image processing
- **MediaPipe**: ML solutions for perception tasks
- **TensorFlow/PyTorch**: Machine learning and AI models
- **PostgreSQL**: Robust relational database
- **SQLAlchemy**: Python SQL toolkit and ORM

### Frontend
- **React**: Modern JavaScript library for building user interfaces
- **Three.js**: 3D graphics library for WebGL
- **Material-UI**: React components for faster development
- **Axios**: HTTP client for API communication
- **React Router**: Declarative routing for React

### DevOps
- **Docker**: Containerization for easy deployment
- **Docker Compose**: Multi-container application orchestration
- **Nginx**: Web server and reverse proxy

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 16+ (for local development)
- Python 3.9+ (for local development)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-interior-design-assistant
   ```

2. **Start with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 📁 Project Structure

```
ai-interior-design-assistant/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── modules/
│   │   ├── room_scanner.py     # Room scanning and analysis
│   │   ├── ai_recommender.py   # AI recommendation engine
│   │   └── virtual_stager.py   # Virtual staging system
│   ├── api/
│   │   ├── scanning.py         # Room scanning endpoints
│   │   ├── recommendations.py  # AI recommendation endpoints
│   │   └── staging.py          # Virtual staging endpoints
│   ├── models/                 # Database models
│   ├── database/               # Database configuration
│   └── tests/                  # Backend tests
├── frontend/
│   ├── package.json            # Node.js dependencies
│   ├── src/
│   │   ├── App.js              # Main React application
│   │   ├── components/
│   │   │   ├── RoomScanner.js  # Room scanning interface
│   │   │   ├── 3DViewer.js     # 3D visualization component
│   │   │   ├── VirtualStaging.js # Virtual staging interface
│   │   │   └── Dashboard.js    # Main dashboard
│   │   ├── utils/              # Utility functions
│   │   └── styles/             # CSS styles
│   └── public/                 # Static assets
├── docker-compose.yml          # Docker services configuration
├── Dockerfile.backend          # Backend Docker configuration
├── Dockerfile.frontend         # Frontend Docker configuration
└── docs/                       # Documentation
```

## 🔧 API Endpoints

### Room Scanning
- `POST /api/scan/upload` - Upload room images for analysis
- `GET /api/scan/results/{scan_id}` - Get room analysis results
- `POST /api/scan/dimensions` - Estimate room dimensions

### AI Recommendations
- `POST /api/recommend/furniture` - Get furniture recommendations
- `POST /api/recommend/colors` - Get color palette suggestions
- `GET /api/recommend/styles` - Get design style recommendations

### 3D Visualization
- `GET /api/3d/models` - Get available 3D furniture models
- `POST /api/3d/scene` - Create 3D room scene
- `PUT /api/3d/scene/{scene_id}` - Update 3D scene

### Virtual Staging
- `POST /api/stage/create` - Create virtual staging
- `GET /api/stage/preview/{stage_id}` - Get staging preview
- `POST /api/stage/export` - Export staged design

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📚 Documentation

- [API Documentation](docs/API.md)
- [User Guide](docs/USER_GUIDE.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenCV community for computer vision tools
- Three.js team for 3D graphics capabilities
- FastAPI developers for the excellent web framework
- React team for the powerful UI library

---

**Built with ❤️ for interior design enthusiasts and professionals**

