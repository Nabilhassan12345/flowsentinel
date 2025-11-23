# FlowSentinel Frontend - Lovable Prompt

Copy and paste this entire prompt into Lovable to generate the frontend:

---

## 🎯 PROJECT BRIEF

Create a modern, professional dashboard for **FlowSentinel** - an AI-powered project intelligence system that monitors software development workflows in real-time.

**Tech Stack Required:**
- React 18+ with TypeScript
- Tailwind CSS for styling
- Shadcn/ui components
- Recharts for data visualization
- Lucide React for icons
- Axios for API calls
- React Query for data fetching
- React Router for navigation

**Backend API:** `http://localhost:8000` (Already built and running)

---

## 🎨 DESIGN REQUIREMENTS

### Color Scheme
- **Primary:** Blue (#0066CC) - IBM watsonx brand color
- **Success:** Green (#10B981) - For GREEN status
- **Warning:** Yellow/Amber (#F59E0B) - For YELLOW status
- **Danger:** Red (#EF4444) - For RED status
- **Background:** Dark mode with gradients (#0F172A, #1E293B)
- **Text:** White/Gray for readability
- **Accents:** Purple (#8B5CF6) for AI features

### Typography
- **Headings:** Inter or Poppins (bold, modern)
- **Body:** Inter (clean, readable)
- **Monospace:** JetBrains Mono (for code/IDs)

### Layout Style
- Modern, clean, professional
- Card-based layout with glassmorphism effects
- Smooth animations and transitions
- Responsive design (mobile, tablet, desktop)
- Dark theme with neon accents

---

## 📄 PAGES TO BUILD

### 1. **Dashboard (Home Page)** `/`

**Top Section - Hero Stats:**
- Large status indicator (GREEN/YELLOW/RED) with pulsing animation
- 4 metric cards in a row:
  - Total Events (with 24h change percentage)
  - Active Blockers (red badge if > 0)
  - Risk Score (0-100 with progress bar)
  - Team Health (letter grade A-F with color)

**Middle Section - Project State:**
- "Current Project State" card with:
  - Status badge (large, prominent)
  - Last updated timestamp
  - Quick actions buttons: "Run Analysis", "Ask Question", "View Details"
  
- Three columns:
  - **Blockers** (left) - Red theme
    - List of current blockers with source tags
    - Empty state: "No blockers detected ✅"
  - **Risks** (middle) - Yellow theme
    - List of risks with impact level
    - Empty state: "No risks identified 🎯"
  - **Completed** (right) - Green theme
    - List of completed items today
    - Empty state: "No items completed yet"

**Bottom Section - Real-Time Activity:**
- Live event feed with auto-refresh
- Each event shows:
  - Source icon (Slack/Jira/GitHub/Calendar)
  - Event type badge
  - Timestamp (relative: "2 mins ago")
  - Event description (truncated)
- Scrollable list, max 10 events

**Right Sidebar:**
- "Autonomous Agent Status" widget:
  - Running/Stopped indicator (animated dot)
  - Next run countdown timer
  - Start/Stop toggle button
  - Run count badge
- "Quick Actions" widget:
  - Load Demo Data button
  - Export Analytics button
  - Refresh Dashboard button

---

### 2. **AI Intelligence** `/intelligence`

**Header:**
- Page title: "AI-Powered Intelligence"
- Subtitle: "IBM watsonx.ai Granite 3 8B Instruct"

**Q&A Section (Top):**
- Large input field with placeholder: "Ask anything about your project..."
- Pre-filled question buttons:
  - "What's blocking the team?"
  - "Is the project at risk?"
  - "What's the overall status?"
  - "Why might we miss the deadline?"
- Submit button with AI sparkle icon
- Q&A history below (expandable cards):
  - Question (bold)
  - Answer (formatted text)
  - Reasoning steps (collapsible list)
  - Timestamp

**Predictions Section (Middle):**
Three cards in a row:

1. **Deadline Risk Prediction**
   - Large percentage: "78% Risk"
   - Progress bar colored by risk level
   - Confidence score
   - List of contributing factors
   - Recommendations (bullets)

2. **Bottleneck Detection**
   - List of predicted bottlenecks
   - Each with:
     - Area name
     - Probability percentage
     - Impact level badge
     - Suggested action

3. **Team Health Score**
   - Large number: "72/100"
   - Letter grade badge: "C"
   - Status description
   - Health trend chart (7 days)
   - Improvement suggestions

**Insights Section (Bottom):**
- Pattern discovery cards
- Anomaly detection alerts
- Trend analysis charts

---

### 3. **Analytics** `/analytics`

**Top Metrics Bar:**
- 5 KPI cards:
  - Total Events
  - Risk Score (with trend)
  - Velocity (events/day)
  - Completion Rate %
  - Response Time (avg)

**Charts Section:**

1. **Event Distribution** (Pie/Donut Chart)
   - Events by source (Slack, Jira, GitHub, Calendar)
   - Color-coded, interactive

2. **Event Timeline** (Line Chart)
   - Events over time (last 7 days)
   - Multiple lines for each source
   - Smooth curves, interactive tooltips

3. **Risk Score Trend** (Area Chart)
   - Risk score over time
   - Color gradient (green to red)
   - Threshold lines at 30 (YELLOW) and 60 (RED)

4. **Action Success Rate** (Bar Chart)
   - Success rate by action type
   - Green bars for successful, red for failed

5. **Temporal Patterns** (Heatmap)
   - Busiest hours/days
   - Color intensity for activity level

**Bottom Section:**
- **Response Times Table:**
  - Average, P50, P95 response times
  - Sortable columns
  - Export button

**Filters (Sidebar):**
- Date range picker (last 7/30/90 days, custom)
- Source filter (checkboxes)
- Event type filter
- Team filter (if multi-team)
- Apply/Reset buttons

---

### 4. **Events** `/events`

**Top Bar:**
- Search input (filter by keyword)
- Filters: Source, Type, Team
- "Ingest Event" button (opens modal)
- "Load Demo Data" button

**Events Table:**
- Columns:
  - Source (icon + text)
  - Type (badge)
  - Timestamp (relative + absolute on hover)
  - Description (truncated, expandable)
  - Team (if applicable)
  - Processed status (checkmark icon)
  - Actions (View Details button)
- Pagination (10/25/50/100 per page)
- Sortable columns
- Row highlighting on hover

**Event Details Modal:**
- Full event JSON (formatted, syntax highlighted)
- Event metadata
- Related actions (if any)
- Close button

**Ingest Event Modal:**
- Form fields:
  - Event ID (auto-generated option)
  - Source (dropdown: Slack/Jira/GitHub/Calendar)
  - Type (dropdown based on source)
  - Timestamp (datetime picker, default: now)
  - Data (JSON editor with validation)
  - Team (optional, dropdown)
- Submit button
- Cancel button

---

### 5. **Teams** `/teams`

**Top Bar:**
- "Create Team" button
- Search teams input

**Teams Grid:**
- Card for each team:
  - Team name (large)
  - Description
  - Member count badge
  - Created date
  - Quick stats:
    - Events (24h)
    - Current status (GREEN/YELLOW/RED)
    - Risk score
  - Actions: View, Edit, Delete

**Create/Edit Team Modal:**
- Form fields:
  - Team name (required)
  - Description (textarea)
  - Members (multi-select, future feature)
- Save/Cancel buttons

**Team Detail Page** `/teams/:id`
- Team header with info
- Team-specific analytics (same as main analytics but filtered)
- Team-specific events list
- Team-specific state
- Team members list (future)

---

### 6. **Webhooks** `/webhooks`

**Top Bar:**
- "Register Webhook" button
- Active/Inactive filter tabs

**Webhooks Table:**
- Columns:
  - URL (truncated, copy button)
  - Event Types (badges)
  - Active status (toggle switch)
  - Last Triggered (timestamp)
  - Success Rate (percentage badge)
  - Actions (Test, Edit, Delete, View Activity)
- Sortable, filterable

**Register/Edit Webhook Modal:**
- Form fields:
  - Webhook URL (required, validated)
  - Event types (checkboxes):
    - event.created
    - state.changed
    - action.taken
  - Active (toggle, default: true)
  - Secret (optional, for signature verification)
  - Retry count (number, default: 3)
- Save/Cancel buttons

**Webhook Activity Modal:**
- Table of webhook deliveries:
  - Timestamp
  - Event type
  - HTTP status code
  - Response time
  - Retry attempt
  - Success/Failure badge
- Pagination
- Export logs button

**Test Webhook:**
- "Send Test" button
- Shows test result (success/failure)
- Response preview

---

### 7. **Actions** `/actions`

**Top Bar:**
- Filter by type (All, Notify, Create Task, Generate Report)
- Filter by status (All, Sent, Created, Completed, Failed)
- Date range filter

**Actions Timeline:**
- Vertical timeline view (like activity feed)
- Each action card shows:
  - Type icon (bell/clipboard/document)
  - Action type (large badge)
  - Status badge
  - Timestamp (relative)
  - Payload summary (expandable)
  - Related team (if applicable)
  - "View Details" link

**Action Details Modal:**
- Full action payload (formatted JSON)
- Metadata
- Related events (links)
- Retry history (if applicable)

---

### 8. **Settings** `/settings`

**Tabs:**

1. **Agent Configuration**
   - Enable/Disable autonomous agent (toggle)
   - Run interval (slider: 1-60 minutes)
   - Lookback hours (slider: 1-48 hours)
   - Auto-alert on status change (toggle)
   - Save button

2. **API Configuration**
   - watsonx.ai settings:
     - API Key (password field)
     - Project ID (text field)
     - Model ID (dropdown)
     - Temperature (slider: 0-1)
   - Slack settings:
     - Webhook URL (text field)
     - Test connection button
   - Save button

3. **Database**
   - Current database type (PostgreSQL/SQLite)
   - Connection status (green/red indicator)
   - Database statistics:
     - Total events
     - Total actions
     - Total teams
     - Database size
   - Export database button
   - Clear old data button (with confirmation)

4. **Appearance**
   - Dark/Light theme toggle (default: dark)
   - Accent color picker
   - Font size adjustment
   - Animation speed

---

## 🔧 TECHNICAL IMPLEMENTATION

### API Integration (Critical!)

**Base URL:** `http://localhost:8000`

**API Endpoints to Use:**

```typescript
// Core APIs
GET    /                           - API info
GET    /health                     - Health check
POST   /events/ingest              - Ingest single event
POST   /events/ingest/batch        - Ingest multiple events
GET    /events/list?limit=10       - List events
POST   /agent/run                  - Run AI analysis
GET    /state/latest               - Get project state
GET    /actions/list?limit=10      - List actions
POST   /qa/ask                     - Ask questions

// Agent
POST   /agent/start                - Start autonomous agent
POST   /agent/stop                 - Stop autonomous agent
GET    /agent/status               - Get agent status
POST   /simulation/run             - Load demo data

// Analytics
GET    /analytics/summary          - Overall analytics
GET    /analytics/events           - Event statistics
GET    /analytics/actions          - Action statistics
GET    /analytics/patterns         - Temporal patterns
GET    /analytics/response-times   - Performance metrics
GET    /analytics/export           - Export data

// Intelligence
GET    /intelligence/predict-deadline-risk
GET    /intelligence/predict-bottlenecks
POST   /intelligence/recommendations
GET    /intelligence/team-health
GET    /intelligence/insights
GET    /intelligence/forecast

// Teams
POST   /teams                      - Create team
GET    /teams                      - List teams
GET    /teams/{id}                 - Get team
PUT    /teams/{id}                 - Update team
DELETE /teams/{id}                 - Delete team
GET    /teams/{id}/analytics       - Team analytics

// Webhooks
POST   /webhooks                   - Register webhook
GET    /webhooks                   - List webhooks
GET    /webhooks/{id}              - Get webhook
PUT    /webhooks/{id}              - Update webhook
DELETE /webhooks/{id}              - Delete webhook
POST   /webhooks/{id}/test         - Test webhook
GET    /webhooks/{id}/activity     - Webhook activity log
```

### React Query Hooks to Create

```typescript
// Create these custom hooks using React Query

// Dashboard
useProjectState()    - GET /state/latest
useRecentEvents()    - GET /events/list?limit=10
useRecentActions()   - GET /actions/list?limit=10
useAgentStatus()     - GET /agent/status

// Intelligence
useAskQuestion()     - POST /qa/ask (mutation)
useDeadlineRisk()    - GET /intelligence/predict-deadline-risk
useBottlenecks()     - GET /intelligence/predict-bottlenecks
useTeamHealth()      - GET /intelligence/team-health

// Analytics
useAnalyticsSummary() - GET /analytics/summary
useEventStats()       - GET /analytics/events
useActionStats()      - GET /analytics/actions

// Events
useEvents()          - GET /events/list
useIngestEvent()     - POST /events/ingest (mutation)
useLoadDemo()        - POST /simulation/run (mutation)

// Teams
useTeams()           - GET /teams
useTeam(id)          - GET /teams/{id}
useCreateTeam()      - POST /teams (mutation)
useUpdateTeam()      - PUT /teams/{id} (mutation)
useDeleteTeam()      - DELETE /teams/{id} (mutation)

// Webhooks
useWebhooks()        - GET /webhooks
useCreateWebhook()   - POST /webhooks (mutation)
useTestWebhook()     - POST /webhooks/{id}/test (mutation)

// Agent
useRunAgent()        - POST /agent/run (mutation)
useStartAgent()      - POST /agent/start (mutation)
useStopAgent()       - POST /agent/stop (mutation)
```

### Components to Create

**Layout Components:**
```
- Sidebar.tsx          - Navigation sidebar with logo
- Navbar.tsx           - Top navbar with user menu
- Layout.tsx           - Main layout wrapper
- PageHeader.tsx       - Reusable page header
```

**Dashboard Components:**
```
- StatusIndicator.tsx  - Large status badge with animation
- MetricCard.tsx       - Reusable metric card component
- ProjectStateCard.tsx - Project state display
- BlockersList.tsx     - List of blockers
- RisksList.tsx        - List of risks
- CompletedList.tsx    - List of completed items
- EventFeed.tsx        - Real-time event feed
- AgentStatusWidget.tsx - Agent status widget
```

**Intelligence Components:**
```
- QAInterface.tsx      - Q&A input and history
- DeadlineRiskCard.tsx - Deadline prediction card
- BottleneckCard.tsx   - Bottleneck detection card
- TeamHealthCard.tsx   - Team health score card
- InsightsList.tsx     - Pattern insights list
```

**Analytics Components:**
```
- EventPieChart.tsx    - Event distribution chart
- TimelineChart.tsx    - Event timeline chart
- RiskTrendChart.tsx   - Risk score trend
- SuccessBarChart.tsx  - Action success rate
- HeatmapChart.tsx     - Temporal patterns heatmap
- AnalyticsFilters.tsx - Filter sidebar
```

**Shared Components:**
```
- StatusBadge.tsx      - Status indicator (GREEN/YELLOW/RED)
- SourceIcon.tsx       - Icon for event source
- EventTypeChip.tsx    - Badge for event type
- LoadingSpinner.tsx   - Loading indicator
- EmptyState.tsx       - Empty state illustration
- ConfirmDialog.tsx    - Confirmation dialog
- Toast.tsx            - Toast notifications
```

---

## 🎨 UI/UX FEATURES TO INCLUDE

### Animations & Interactions
- Smooth page transitions (fade in/out)
- Card hover effects (lift, glow)
- Button hover states with scale
- Loading skeletons for data fetching
- Pulsing animation for live status
- Confetti animation on successful actions
- Toast notifications for all actions

### Status Indicators
- **GREEN:** Pulsing green dot, "Healthy" text
- **YELLOW:** Warning yellow triangle, "At Risk" text
- **RED:** Red alert icon, "Critical" text
- Animated transitions between states

### Real-Time Features
- Auto-refresh dashboard every 30 seconds
- Live agent status with countdown timer
- Event feed with auto-scroll to new events
- WebSocket support (future enhancement)

### Responsive Design
- Mobile: Single column, collapsible sidebar
- Tablet: Two columns, partial sidebar
- Desktop: Full layout with sidebar

### Accessibility
- ARIA labels on all interactive elements
- Keyboard navigation support
- High contrast mode option
- Focus indicators
- Screen reader friendly

---

## 🚀 QUICK START CODE STRUCTURE

### App.tsx
```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Intelligence from './pages/Intelligence';
import Analytics from './pages/Analytics';
import Events from './pages/Events';
import Teams from './pages/Teams';
import Webhooks from './pages/Webhooks';
import Actions from './pages/Actions';
import Settings from './pages/Settings';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="intelligence" element={<Intelligence />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="events" element={<Events />} />
            <Route path="teams" element={<Teams />} />
            <Route path="teams/:id" element={<TeamDetail />} />
            <Route path="webhooks" element={<Webhooks />} />
            <Route path="actions" element={<Actions />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
```

### API Client (api/client.ts)
```typescript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    // Show toast notification on error
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);
```

---

## ✅ DELIVERABLES CHECKLIST

**Must Have (MVP):**
- [ ] Dashboard page with status, metrics, blockers/risks
- [ ] Event feed with real-time updates
- [ ] AI Intelligence page with Q&A
- [ ] Analytics page with charts
- [ ] Events list and ingestion
- [ ] Agent control (start/stop/status)
- [ ] Load demo data button
- [ ] Responsive design (mobile-friendly)
- [ ] Dark theme
- [ ] Toast notifications

**Nice to Have:**
- [ ] Teams management
- [ ] Webhooks management
- [ ] Actions timeline
- [ ] Settings page
- [ ] Export functionality
- [ ] Advanced filters
- [ ] Search functionality
- [ ] Keyboard shortcuts

---

## 📝 COPY & PASTE INSTRUCTIONS

1. **Copy this entire prompt**
2. **Go to Lovable (lovable.dev)**
3. **Create new project: "FlowSentinel Dashboard"**
4. **Paste this prompt in the chat**
5. **Add:** "Build this step by step. Start with the dashboard page first."
6. **Let Lovable generate the code**
7. **Review and request modifications as needed**
8. **Export the generated code**
9. **I'll help you integrate it with the FastAPI backend**

---

## 🎯 PRIORITY ORDER

Ask Lovable to build in this order:

1. **First:** Layout + Sidebar + Dashboard page (30 min)
2. **Second:** Intelligence page with Q&A (20 min)
3. **Third:** Analytics page with charts (30 min)
4. **Fourth:** Events page with table (20 min)
5. **Fifth:** Teams, Webhooks, Actions pages (40 min)
6. **Sixth:** Settings page (20 min)
7. **Final:** Polish, animations, responsive (20 min)

**Total time estimate: 3 hours**

---

## 🚨 IMPORTANT NOTES

- **API is already running at http://localhost:8000**
- **No authentication required for MVP**
- **All endpoints return JSON**
- **Use React Query for all data fetching**
- **Dark theme by default**
- **IBM watsonx blue as primary color**
- **Mobile-first responsive design**
- **TypeScript for type safety**

---

Ready to copy and paste! 🚀
b