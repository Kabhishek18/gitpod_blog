# Portfolio Platform Architecture

## System Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Django/Wagtail │    │   External APIs │
│   (Templates)   │◄──►│   Application    │◄──►│   & Services    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │   Database   │
                       │   Layer      │
                       └──────────────┘
```

## Core Technology Stack

### Backend Framework
- **Django 5.+** with **Wagtail CMS 7.x**
- **Python 3.11+** for better performance
- **Django REST Framework** for API endpoints
- **Celery** for background tasks (AI processing, email sending)
- **Redis** for caching and Celery broker
