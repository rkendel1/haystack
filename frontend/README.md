# Haystack RAG Frontend

A modern, production-ready React frontend for interacting with Haystack's RAG (Retrieval-Augmented Generation) backend. Built with React, TypeScript, Vite, and Tailwind CSS.

## Features

- 🎯 **Chat Interface**: Conversational UI for querying your documents with highlighted citations
- 📁 **Document Management**: Drag-and-drop file upload with support for PDF, TXT, and MD files
- 🔄 **Multiple Pipeline Modes**: 
  - Standard RAG for question-answering
  - Agent mode with step-by-step reasoning traces
  - Semantic search for finding relevant documents
- 💾 **Chat History**: Persistent conversation history stored in browser localStorage
- 🎨 **Modern UI**: Built with Tailwind CSS and shadcn/ui components
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🌙 **Dark Mode Support**: Built-in dark mode with CSS variables
- ⚡ **Fast Development**: Powered by Vite for instant HMR

## Prerequisites

- Node.js 18+ and npm
- Haystack backend running (typically on http://localhost:8000)

## Getting Started

### Installation

1. Install dependencies:
```bash
npm install
```

2. Copy the environment example file:
```bash
cp .env.example .env
```

3. Update the `.env` file with your Haystack backend URL:
```
VITE_API_URL=http://localhost:8000
```

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at http://localhost:3000

### Building for Production

Build the application:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## Docker Deployment

### Build the Docker image:
```bash
docker build -t haystack-frontend .
```

### Run the container:
```bash
docker run -p 3000:80 -e VITE_API_URL=http://your-backend:8000 haystack-frontend
```

### Docker Compose

The frontend can be integrated into your existing Docker Compose setup. Add this service to your `docker-compose.yml`:

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=http://backend:8000
    depends_on:
      - backend
```

## Backend API Requirements

The frontend expects the following endpoints from the Haystack backend:

### POST /query
Query the RAG system.

**Request:**
```json
{
  "query": "What is the capital of France?",
  "pipeline": "rag",
  "top_k": 5
}
```

**Response:**
```json
{
  "answer": "The capital of France is Paris.",
  "documents": [
    {
      "id": "doc1",
      "content": "Paris is the capital and most populous city of France...",
      "meta": {
        "name": "france.txt",
        "file_path": "/data/france.txt"
      },
      "score": 0.95
    }
  ],
  "steps": []
}
```

### POST /index
Upload a document for indexing.

**Request:** multipart/form-data with `file` field

**Response:**
```json
{
  "message": "Document uploaded successfully",
  "document_id": "doc123",
  "file_name": "example.pdf"
}
```

### GET /documents
List all indexed documents.

**Response:**
```json
[
  {
    "id": "doc1",
    "content": "...",
    "meta": {
      "name": "example.pdf",
      "size": 12345
    }
  }
]
```

### DELETE /documents/{id}
Delete a specific document.

**Response:**
```json
{
  "message": "Document deleted successfully"
}
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # Reusable UI components
│   │   ├── Chat.tsx         # Main chat interface
│   │   ├── FileUploader.tsx # File upload component
│   │   ├── DocumentList.tsx # Document management
│   │   ├── PipelineSwitcher.tsx # Pipeline mode selector
│   │   └── CitationCard.tsx # Citations display
│   ├── hooks/
│   │   ├── useHaystackQuery.ts # API query hook
│   │   ├── useFileUpload.ts    # File upload hook
│   │   └── useChatHistory.ts   # Chat history management
│   ├── pages/
│   │   └── Home.tsx         # Main page layout
│   ├── lib/
│   │   ├── api.ts          # Axios instance
│   │   └── utils.ts        # Utility functions
│   ├── types/
│   │   └── index.ts        # TypeScript types
│   ├── App.tsx             # Root component
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
├── public/                  # Static assets
├── Dockerfile              # Production Docker image
├── nginx.conf              # Nginx configuration
├── package.json            # Dependencies
├── vite.config.ts          # Vite configuration
├── tailwind.config.js      # Tailwind CSS config
└── tsconfig.json           # TypeScript config
```

## Technologies Used

- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **TanStack Query (React Query)**: Data fetching and caching
- **Axios**: HTTP client
- **React Dropzone**: File upload
- **Sonner**: Toast notifications
- **Lucide React**: Icon library

## Development Tips

- The app uses React Query for API state management with automatic caching
- All API calls go through the `/api` proxy in development (configured in `vite.config.ts`)
- Chat history is stored in browser localStorage
- The UI is built with shadcn/ui principles for easy customization
- Dark mode variables are defined in `index.css` and can be customized

## Customization

### Colors
Edit CSS variables in `src/index.css` to customize the color scheme.

### Components
All UI components are in `src/components/ui/` and can be modified to fit your design needs.

### API Configuration
Update `src/lib/api.ts` to modify API client settings like timeouts, headers, or interceptors.

## Troubleshooting

### CORS Issues
If you encounter CORS errors, ensure your Haystack backend has CORS enabled for the frontend origin:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Connection Refused
Make sure the `VITE_API_URL` in your `.env` file points to the correct backend URL.

## License

This project follows the same license as the Haystack repository.

## Contributing

Contributions are welcome! Please follow the existing code style and add tests for new features.
