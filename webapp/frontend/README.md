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
