# Tamil Words Search - Frontend

Vue.js 3 frontend for searching Tamil words across classical literature.

## Features

- **Search Interface**: Search for Tamil words with partial or exact matching
- **Work Filtering**: Filter results by specific literary works
- **Two-Panel Layout**:
  - Left: Search controls and filters
  - Right: Results with word details, lines, and hierarchical context
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Tamil Unicode Support**: Full support for Tamil script display

## Setup

1. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

2. **Configure API endpoint (optional):**
   Create `.env` file:
   ```
   VITE_API_URL=http://localhost:8000
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```

4. **Access the application:**
   - Frontend: http://localhost:5173
   - API automatically proxied to backend

## Build for Production

```bash
npm run build
```

Built files will be in `dist/` directory.

## Docker Deployment

### Build Docker Image

```bash
# From the frontend directory
docker build -t tamil-words-frontend .
```

### Run Docker Container

```bash
# Run with default settings (port 80)
docker run -p 80:80 tamil-words-frontend

# Run on custom port
docker run -p 8080:80 tamil-words-frontend
```

### Build with Custom Backend URL

The frontend needs to know the backend API URL at build time. You can set it as a build argument:

```bash
# Build with production backend URL
docker build --build-arg VITE_API_URL=https://your-backend.railway.app -t tamil-words-frontend .
```

To use build arguments, update the Dockerfile to accept it:

```dockerfile
# Add before RUN npm run build:
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
```

### Railway Deployment

1. **Using Railway CLI:**
   ```bash
   railway login
   railway link
   railway variables set VITE_API_URL=https://your-backend.railway.app
   railway up
   ```

2. **Using GitHub Integration:**
   - Push frontend code to GitHub
   - Connect repository to Railway
   - Set build environment variable in Railway dashboard:
     - Key: `VITE_API_URL`
     - Value: `https://your-backend.railway.app`
   - Railway will automatically build and deploy

## Project Structure

```
frontend/
├── src/
│   ├── App.vue          # Main application component
│   ├── api.js           # API client
│   ├── main.js          # Vue app initialization
│   └── style.css        # Global styles
├── public/              # Static assets
├── index.html           # HTML template
├── package.json         # Dependencies
└── vite.config.js       # Vite configuration
```

## Usage

1. **Search**: Enter a Tamil word in the search box
2. **Match Type**: Choose between partial or exact matching
3. **Filter**: Select specific works to search within
4. **Results**: Click on any result to highlight it
5. **Load More**: Scroll down and click "Load More" for additional results

## Technologies

- Vue.js 3 (Composition API)
- Vite (Build tool)
- Axios (HTTP client)
- CSS3 (Responsive design)
