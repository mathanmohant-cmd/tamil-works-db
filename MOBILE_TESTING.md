# Mobile Testing Guide

This guide explains how to test the Tamil Literature application on your mobile device over your local network.

## Problem

When accessing the app from a mobile device using your laptop's IP address (e.g., `http://192.168.1.198:5173`), the frontend needs to connect to the backend API, which must also be accessible over the network.

## Solution

We've implemented automatic API URL detection and flexible CORS configuration.

## Setup Instructions

### 1. Configure Backend for Network Access

The backend needs to:
- Listen on all network interfaces (not just localhost)
- Allow CORS requests from your mobile device

**Create/Update `.env` file** in `webapp/backend/`:

```env
# Database connection
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tamil_literature

# Listen on all interfaces (allows network access)
API_HOST=0.0.0.0
API_PORT=8000

# Allow CORS from all origins (for development/testing)
CORS_ALLOW_ALL=true
```

### 2. Start Backend Server

```bash
cd webapp/backend
python main.py
```

The backend will start on `http://0.0.0.0:8000`, which makes it accessible from:
- Localhost: `http://localhost:8000`
- Your laptop IP: `http://192.168.1.198:8000`

### 3. Start Frontend Server with Network Access

Vite dev server needs to be accessible over the network:

```bash
cd webapp/frontend
npm run dev -- --host
```

Or update `vite.config.js` to always allow network access:

```javascript
export default defineConfig({
  server: {
    host: '0.0.0.0',  // Listen on all interfaces
    port: 5173
  }
})
```

### 4. Find Your Laptop's IP Address

**Windows:**
```cmd
ipconfig
```
Look for "IPv4 Address" under your active network adapter (usually starts with 192.168.x.x)

**Mac/Linux:**
```bash
ifconfig
# or
ip addr show
```

### 5. Access from Mobile Device

On your mobile device (connected to the same WiFi network):

1. Open browser
2. Navigate to: `http://192.168.1.198:5173` (use your actual IP)
3. The app should load and filters should work!

## How It Works

### Frontend API Detection

The frontend (`src/api.js`) automatically detects the correct backend URL:

```javascript
const getApiBaseUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL  // Override if set
  }
  // Auto-detect: use same hostname as frontend, port 8000
  const protocol = window.location.protocol  // http: or https:
  const hostname = window.location.hostname  // localhost or 192.168.1.198
  return `${protocol}//${hostname}:8000`
}
```

**Examples:**
- Access `http://localhost:5173` → API at `http://localhost:8000` ✅
- Access `http://192.168.1.198:5173` → API at `http://192.168.1.198:8000` ✅

### Backend CORS Configuration

The backend (`main.py`) supports two modes:

**Development Mode** (CORS_ALLOW_ALL=true):
- Allows requests from ANY origin
- Perfect for mobile testing
- Use only for development/testing

**Production Mode** (CORS_ALLOW_ALL=false):
- Restricts to specific origins in ALLOWED_ORIGINS
- More secure
- Use in production

## Troubleshooting

### "Network Error" when loading collections

**Cause**: Backend not accessible from mobile device

**Solutions**:
1. ✅ Check backend is running: `http://192.168.1.198:8000/health` from mobile browser
2. ✅ Verify `API_HOST=0.0.0.0` in backend `.env`
3. ✅ Verify `CORS_ALLOW_ALL=true` in backend `.env`
4. ✅ Check firewall isn't blocking port 8000
5. ✅ Ensure mobile and laptop are on the same WiFi network

### Frontend loads but API calls fail

**Cause**: CORS blocking requests

**Solution**:
- Set `CORS_ALLOW_ALL=true` in backend `.env`
- Restart backend server

### Can't access frontend from mobile

**Cause**: Vite server only listening on localhost

**Solution**:
- Run: `npm run dev -- --host`
- Or update `vite.config.js` to set `server.host = '0.0.0.0'`

### Different IP address each time

**Cause**: DHCP assigns dynamic IPs

**Solution**:
- Set static IP in router settings for your laptop
- Or configure router to always assign same IP to your laptop's MAC address

## Windows Firewall Configuration

If backend is not accessible from mobile, Windows Firewall might be blocking it:

1. Open **Windows Defender Firewall with Advanced Security**
2. Click **Inbound Rules** → **New Rule**
3. Select **Port** → **Next**
4. Enter port **8000** → **Next**
5. Select **Allow the connection** → **Next**
6. Check all profiles (Domain, Private, Public) → **Next**
7. Name: "Tamil Literature Backend" → **Finish**

## Production Deployment

For production, use proper CORS configuration:

```env
# Production .env
CORS_ALLOW_ALL=false
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

This restricts API access to only your production domain.

## Files Changed (2025-12-29)

1. ✅ `webapp/frontend/src/api.js` - Added `getBaseURL()` method
2. ✅ `webapp/frontend/src/components/CollectionTree.vue` - Use centralized API config
3. ✅ `webapp/frontend/src/components/TreeNode.vue` - Use centralized API config
4. ✅ `webapp/backend/main.py` - Add CORS_ALLOW_ALL configuration
5. ✅ `webapp/backend/.env.example` - Document CORS settings

## Testing Checklist

- [ ] Backend starts with `API_HOST=0.0.0.0`
- [ ] Backend accessible from laptop: `http://localhost:8000/health`
- [ ] Backend accessible from mobile: `http://192.168.1.198:8000/health`
- [ ] Frontend accessible from laptop: `http://localhost:5173`
- [ ] Frontend accessible from mobile: `http://192.168.1.198:5173`
- [ ] Search works on mobile
- [ ] Filters load and work on mobile
- [ ] Collection tree expands/collapses on mobile
- [ ] Touch targets are 44px minimum (already implemented)

---

**Last Updated**: 2025-12-29
**Issue**: Filters not working when accessing from mobile (192.168.1.198:5173)
**Root Cause**: CollectionTree/TreeNode using hardcoded localhost API URL
**Solution**: Use centralized `api.js` with auto-detection + flexible CORS
