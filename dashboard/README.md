# JobBot Monitoring Dashboard

Real-time monitoring dashboard for the JobBot enterprise scraping system.

## Features

### 🔍 Real-Time Monitoring
- Live system status and health metrics
- WebSocket-powered real-time updates
- Multi-site scraping orchestrator monitoring
- Performance metrics and analytics

### 📊 Analytics Dashboard
- Daily scraping trends and patterns
- Site performance comparisons
- Job market insights and analytics
- Export capabilities for reports

### 🎛️ Session Management
- Active and historical scraping sessions
- Real-time progress tracking
- Session details and logs
- Error monitoring and alerts

### ⚙️ Configuration Management
- Scraping system settings
- Site-specific configurations
- Monitoring and alert preferences
- Database maintenance settings

## Tech Stack

- **React 18** - Modern UI framework
- **Vite** - Fast build tool and dev server
- **React Query** - Data fetching and caching
- **React Router** - Client-side routing
- **Recharts** - Data visualization
- **Socket.IO Client** - Real-time communication
- **Axios** - HTTP client
- **Lucide React** - Icon library
- **Date-fns** - Date utilities

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- JobBot backend running on `http://172.22.206.209:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Development Server

The dashboard will be available at `http://localhost:3000` with:
- API proxy to `http://172.22.206.209:8000` for `/api` routes
- WebSocket proxy for real-time updates

## API Integration

### Backend Endpoints
- `GET /health` - System health check
- `GET /api/v1/monitoring/status` - System status
- `GET /api/v1/monitoring/metrics` - Performance metrics
- `GET /api/v1/monitoring/sessions` - Scraping sessions
- `GET /api/v1/orchestrator/status` - Multi-site orchestrator status
- `POST /api/v1/orchestrator/start` - Start multi-site scraping

### WebSocket Events
- `connection_status` - Connection state changes
- `metrics_update` - Real-time metrics updates
- `session_update` - Scraping session progress
- `orchestrator_update` - Multi-site orchestrator status
- `error_alert` - System error notifications

## Architecture

### Component Structure
```
src/
├── components/
│   ├── Layout.jsx           # Main layout with navigation
│   ├── Dashboard.jsx        # Main dashboard overview
│   ├── SystemStatus.jsx     # System health indicators
│   ├── MetricCard.jsx       # Reusable metric display
│   ├── SessionsList.jsx     # Scraping sessions list
│   ├── PerformanceChart.jsx # Performance visualizations
│   ├── ScrapingSessions.jsx # Session management page
│   ├── Analytics.jsx        # Analytics and reports
│   └── Settings.jsx         # Configuration management
├── hooks/
│   └── useRealTimeMetrics.js # Real-time data hooks
├── services/
│   ├── api.js              # REST API client
│   └── websocket.js        # WebSocket service
└── utils/                  # Utility functions
```

### Data Flow
1. **Initial Load**: React Query fetches initial data from REST APIs
2. **Real-time Updates**: WebSocket service provides live updates
3. **State Management**: Hooks merge REST and WebSocket data
4. **UI Updates**: Components reactively update with latest data

## Configuration

### Environment Variables
- API endpoints configured in `vite.config.js`
- WebSocket URL: `ws://172.22.206.209:8000`
- API Base URL: `http://172.22.206.209:8000`

### Proxy Configuration
Development server proxies:
- `/api/*` → Backend API
- `/ws/*` → WebSocket connections

## Features Detail

### Dashboard Overview
- System health status indicators
- Key performance metrics
- Recent scraping sessions
- Quick action buttons
- Real-time connection status

### Session Management
- Filter and search sessions
- Real-time progress tracking
- Session details and logs
- Export session data
- Start/stop controls

### Analytics
- Historical performance trends
- Site comparison charts
- Job market insights
- Location and company analytics
- Custom time range selection

### Settings
- Scraping configuration
- Site-specific settings
- Monitoring preferences
- Database maintenance
- Alert configuration

## Development

### Code Style
- ESLint for code quality
- React hooks for state management
- Responsive design patterns
- Accessibility considerations

### Performance
- React Query caching
- Component memoization
- Lazy loading where appropriate
- Optimized WebSocket usage

### Error Handling
- Graceful API error handling
- WebSocket reconnection logic
- User-friendly error messages
- Fallback to polling if WebSocket fails

## Deployment

### Production Build
```bash
npm run build
```

### Static Hosting
- Build output in `dist/` directory
- Serve static files with appropriate routing
- Configure API proxy in production

### Docker Deployment
```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
```

## Monitoring

### Performance Metrics
- Bundle size monitoring
- Render performance tracking
- API response times
- WebSocket connection health

### Error Tracking
- Client-side error boundaries
- API error logging
- WebSocket connection failures
- User experience monitoring

## Contributing

1. Follow React best practices
2. Maintain component modularity
3. Update documentation for new features
4. Test real-time functionality thoroughly
5. Ensure responsive design compatibility

## Phase 5B Deliverables

✅ **Complete React Dashboard**
- Real-time monitoring interface
- WebSocket integration for live updates
- Analytics and reporting capabilities
- Configuration management
- Session monitoring and control

🎯 **Next Steps**
- Performance optimization
- Comprehensive testing
- Business intelligence features
- Production deployment