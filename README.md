# PR Campaign Ideation System

An AI-powered system that performs daily trend analysis across multiple platforms and generates digital PR campaign ideas for agencies. The system detects lasting trends, analyzes their PR potential over time, and creates actionable campaign angles that brands can execute over several days.

## Features

- **Daily Trend Collection**: Automatically collects trending topics from Google Trends, Reddit, news APIs, and social media
- **AI-Powered Analysis**: Uses LangChain with OpenAI/Anthropic APIs to analyze trend sustainability and PR potential
- **Campaign Generation**: Generates specific campaign angles with execution briefs and media hooks
- **Dashboard Interface**: Modern Next.js dashboard for viewing trends and campaign ideas
- **Scheduled Processing**: Celery Beat handles daily analysis and email digests
- **Search & Analytics**: Elasticsearch integration for powerful search and analytics

## Tech Stack

### Backend
- **FastAPI** (Python 3.11+) - REST API with automatic OpenAPI documentation
- **PostgreSQL** - Primary database for trends and campaigns
- **Redis** - Caching and Celery message broker
- **Elasticsearch** - Search and analytics
- **Celery Beat** - Scheduled background tasks
- **SQLAlchemy** - Database ORM with async support
- **Pydantic** - Data validation and serialization

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Shadcn/ui** - Modern component library
- **TanStack Query** - Data fetching and caching

### AI/ML
- **LangChain** - LLM workflow orchestration
- **OpenAI/Anthropic APIs** - Large language models
- **spaCy** - Natural language processing
- **Sentence Transformers** - Semantic similarity

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Environment Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd pr-campaign-system
```

2. **Create environment file**:
```bash
cp .env.example .env
```

3. **Configure API keys in `.env`**:
```bash
# Required for full functionality
OPENAI_API_KEY=your_openai_api_key_here
NEWS_API_KEY=your_news_api_key_here

# Optional for enhanced data collection
TWITTER_API_KEY=your_twitter_api_key_here
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
```

### Running with Docker

1. **Start all services**:
```bash
docker-compose up --build
```

2. **Access the application**:
- Frontend Dashboard: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- API Health Check: http://localhost:8000/health

### Manual Setup (Development)

#### Backend Setup

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Start PostgreSQL and Redis** (via Docker or locally)

5. **Run database migrations**:
```bash
alembic upgrade head
```

6. **Start the API server**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. **Start Celery worker** (in another terminal):
```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

8. **Start Celery Beat scheduler** (in another terminal):
```bash
celery -A app.tasks.celery_app beat --loglevel=info
```

#### Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Start development server**:
```bash
npm run dev
```

4. **Access frontend**: http://localhost:3000

## API Endpoints

### Trends
- `GET /api/v1/trends/` - List trends with filtering
- `GET /api/v1/trends/{id}` - Get specific trend
- `POST /api/v1/trends/` - Create new trend
- `GET /api/v1/trends/stats/summary` - Trend statistics

### Campaigns
- `GET /api/v1/campaigns/` - List campaigns with filtering
- `GET /api/v1/campaigns/{id}` - Get specific campaign
- `POST /api/v1/campaigns/{id}/view` - Increment view count
- `GET /api/v1/campaigns/types/summary` - Campaign type summary

### Analytics
- `GET /api/v1/analytics/dashboard` - Dashboard metrics
- `GET /api/v1/analytics/trends/performance` - Trend performance data
- `GET /api/v1/analytics/campaigns/performance` - Campaign performance data
- `GET /api/v1/analytics/system/health` - System health check

## Configuration

### Environment Variables

#### Database & Infrastructure
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `ELASTICSEARCH_URL` - Elasticsearch endpoint

#### AI/ML APIs
- `OPENAI_API_KEY` - OpenAI API key for GPT models
- `ANTHROPIC_API_KEY` - Anthropic API key for Claude models

#### Data Sources
- `NEWS_API_KEY` - NewsAPI.org API key
- `TWITTER_API_KEY` - Twitter API credentials
- `REDDIT_CLIENT_ID` - Reddit API credentials

#### Email (Optional)
- `SMTP_HOST` - Email server for daily digests
- `SMTP_USER` - Email username
- `SMTP_PASSWORD` - Email password

### Scheduled Tasks

The system runs several scheduled tasks:

- **Daily Trend Analysis**: 6:00 AM UTC - Collects and analyzes trends
- **Trend Score Updates**: Every 4 hours - Updates trend scoring
- **Daily Digest Email**: 8:00 AM UTC - Sends summary email
- **Cleanup**: Weekly on Mondays - Archives old data

## Database Schema

### Key Models

- **Trends**: Stores trending topics with scoring and metadata
- **Campaigns**: Generated PR campaign ideas linked to trends
- **Angles**: Specific story angles and execution details

### Key Fields

#### Trends
- `title`, `description`, `category`
- `score`, `velocity`, `volume`, `sustainability_score`
- `platforms`, `keywords`, `regions`
- `is_analyzed`, `is_brand_safe`

#### Campaigns
- `title`, `headline`, `description`, `brief`
- `campaign_type`, `industry`, `target_audience`
- `potential_score`, `virality_score`, `brand_safety_score`
- `suggested_channels`, `media_hooks`, `key_messages`

## Development

### Code Style

- **Python**: PEP 8 with 88-character line limit (Black formatter)
- **TypeScript**: Strict mode with proper type annotations
- **Components**: Functional components with hooks

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests  
cd frontend
npm run test

# Type checking
npm run type-check
```

### Adding New Data Sources

1. Create service in `backend/app/services/trend_detection/`
2. Implement `get_trending_topics()` method
3. Add to `daily_analysis.py` task
4. Update configuration and documentation

## Deployment

### Production Considerations

1. **Environment Variables**: Set production API keys and secrets
2. **Database**: Use managed PostgreSQL service
3. **Redis**: Use managed Redis service  
4. **Elasticsearch**: Use managed Elasticsearch cluster
5. **Monitoring**: Add application monitoring (Sentry, DataDog)
6. **SSL**: Enable HTTPS for production
7. **Scaling**: Consider horizontal scaling for high traffic

### Docker Production

```bash
# Production build
docker-compose -f docker-compose.prod.yml up --build -d
```

## Monitoring

### Health Checks
- `/health` - Basic API health
- `/api/v1/analytics/system/health` - Detailed system status

### Key Metrics
- Daily trends collected and processed
- Campaign generation success rate
- API response times
- Background task completion

## Troubleshooting

### Common Issues

1. **Database Connection**: Check PostgreSQL is running and credentials are correct
2. **API Keys**: Verify all API keys are valid and have sufficient quotas
3. **Celery Tasks**: Ensure Redis is running for task queue
4. **Frontend Proxy**: Check API URL configuration in Next.js

### Logs

- **Backend**: Structured JSON logs via structlog
- **Frontend**: Browser console and Next.js logs
- **Celery**: Worker and beat scheduler logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following code style guidelines
4. Add tests for new functionality
5. Submit a pull request

## License

[License details] 