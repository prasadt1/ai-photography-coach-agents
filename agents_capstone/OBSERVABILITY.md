# Observability Guide – AI Photography Coach

This document describes the observability infrastructure (logs, traces, metrics) and how to extend it for production use.

---

## Architecture

The observability layer consists of three pillars:

1. **Logs** – Structured JSON logs of all agent operations
2. **Traces** – Call chains and latency information  
3. **Metrics** – Counters, histograms, and summaries

These are collected locally and displayed in the Streamlit UI. In production, they can be exported to cloud monitoring systems (e.g., Google Cloud Logging, Datadog).

---

## Logs

### Configuration

**File:** `logging_config.py`

```python
def configure_logging():
    """Set up JSON logging with custom formatter."""
```

Logging is configured on app startup in `app_streamlit.py`:

```python
from agents_capstone.logging_config import configure_logging
configure_logging()
```

### Log Format

All logs are emitted as JSON to stderr:

```json
{
  "timestamp": "2025-12-01T10:15:30.123Z",
  "level": "INFO",
  "logger": "agents_capstone.agents.vision_agent",
  "message": "Analyzing image with Gemini",
  "agent": "VisionAgent",
  "user_id": "default_user",
  "image_path": "tmp_uploaded.jpg",
  "latency_ms": 2340
}
```

### Key Fields

| Field | Description |
|-------|---|
| `timestamp` | ISO 8601 timestamp of log event |
| `level` | Log level (INFO, WARNING, ERROR, DEBUG) |
| `logger` | Python logger name (module path) |
| `message` | Human-readable log message |
| `agent` | Agent name (e.g., "VisionAgent", "KnowledgeAgent") |
| `user_id` | User session ID (default: "default_user") |
| `latency_ms` | Operation latency in milliseconds |
| `error` | Exception message (for ERROR logs) |
| `session_keys` | Persisted session keys (for DEBUG) |

### Viewing Logs

**Local terminal (when running Streamlit):**
```bash
export GOOGLE_API_KEY="..."
export PYTHONPATH=$PWD:$PYTHONPATH
python3 -m streamlit run agents_capstone/app_streamlit.py 2>&1 | tee app.log
```

Each log line will be JSON. Parse with `jq`:
```bash
grep '"agent":"VisionAgent"' app.log | jq .latency_ms
```

**In Streamlit UI:**
- Open the "Debug & Observability" expander (right side).
- View `last_debug_logs` (last 10 logs).
- Filter by agent, user_id, or level.

---

## Traces

### Call Traces

Agent calls are traced in the orchestrator (`agents/orchestrator.py`):

```python
def run(self, user_id: str, image_path: Optional[str], query: str):
    # ... trace starts
    session = self._get_session(user_id)
    
    # Vision agent call
    vision_result = self.vision_agent.analyze(image_path, skill_level)
    
    # Knowledge agent call
    coach_result = self.knowledge_agent.coach(query, vision_result, session)
    
    # ... trace ends
```

### Trace Information Captured

- **Agent name** — which agent was invoked
- **Input summary** — image path, query, session skill level
- **Output summary** — vision analysis fields, coaching response text
- **Latency** — time from call start to return
- **Errors** — any exceptions during execution
- **Session state** — session keys before and after

### Viewing Traces

**In Streamlit UI:**
- "Debug & Observability" panel shows a trace of the last agent run.
- Includes vision agent output (EXIF, composition) and knowledge agent output (text, issues, exercise).
- Collapsed by default; click to expand.

**In terminal logs:**
```bash
grep '"message":"Orchestrator.run"' app.log | jq '.'
```

### Future: ADK Trace Export

When using ADK, wrap orchestrator calls with ADK's trace decorator:

```python
from google.adk.observability import trace

@trace
def run(self, user_id: str, image_path: Optional[str], query: str):
    # ... existing code
```

ADK will automatically export traces to Google Cloud Trace for visualization.

---

## Metrics

### Metrics Collected

| Metric | Type | Description |
|--------|------|---|
| `agent_call_count` | Counter | Total number of agent invocations |
| `agent_latency_ms` | Histogram | Latency distribution per agent |
| `agent_errors` | Counter | Number of agent errors by type |
| `session_new` | Counter | New sessions created |
| `session_reuse` | Counter | Existing sessions loaded |
| `memory_set` | Counter | Long-term memory writes |
| `memory_get` | Counter | Long-term memory reads |

### Metrics Collection (app_streamlit.py)

```python
# In run_turn function
metrics = {
    "agent": "VisionAgent",
    "latency_ms": int((time.time() - t0) * 1000),
    "status": "success" if res else "error",
    "user_id": user_id,
}

# Update session state
st.session_state["metrics"].append(metrics)
```

### Viewing Metrics

**In Streamlit UI:**
- "Observability" panel (right side) shows:
  - Total agent calls
  - Avg latency (per agent)
  - Error count
  - Last error message

**Aggregated metrics (from history):**
```python
import json
import statistics

# Load session metrics from memory
metrics = memory_tool.get_value("default_user", "metrics") or []

latency_ms = [m["latency_ms"] for m in metrics if m["status"] == "success"]
if latency_ms:
    print(f"Median latency: {statistics.median(latency_ms)}ms")
    print(f"P95 latency: {statistics.quantiles(latency_ms, n=20)[18]}ms")
```

### Future: Metrics Export

To export metrics to Google Cloud Monitoring:

```python
from google.cloud import monitoring_v3

client = monitoring_v3.MetricServiceClient()
project = "projects/YOUR_PROJECT_ID"

# Write time series data
metric = monitoring_v3.Metric()
metric.type = "custom.googleapis.com/agent/latency"
resource = monitoring_v3.MonitoredResource()
resource.type = "global"

# ... build and write time series
```

---

## Debug Panel

The Streamlit UI includes a collapsible "Debug & Observability" expander showing:

```
📊 Debug & Observability
├── Last Agent Call
│   ├── Vision Result: {exif, composition_summary, issues}
│   └── Coach Result: {text, issues, exercise}
├── Session
│   ├── User ID: default_user
│   ├── Skill Level: beginner
│   ├── History Length: 3 turns
│   └── Compact Summary: "Discussed ISO..."
├── Recent Logs (last 10)
│   └── [JSON log entries]
├── Metrics
│   ├── Total Calls: 5
│   ├── Avg Latency: 2.1s
│   └── Errors: 0
└── Last Error: (none)
```

### Enabling/Disabling Debug

In `app_streamlit.py`, the debug panel is always visible. To add a toggle:

```python
if st.checkbox("Show Debug Info", value=False):
    with st.expander("📊 Debug & Observability"):
        # ... debug panel content
```

---

## Extending Observability

### 1. Add Custom Metrics

In any agent or function:

```python
import logging

logger = logging.getLogger(__name__)

# Log a structured metric
logger.info(
    "Processing complete",
    extra={
        "agent": "CustomAgent",
        "metric_name": "processing_items",
        "metric_value": 42,
        "latency_ms": 1500,
    }
)
```

### 2. Export to Google Cloud Logging

Update `logging_config.py`:

```python
import google.cloud.logging

# Set up Cloud Logging handler
client = google.cloud.logging.Client()
handler = client.get_default_handler()

logging.basicConfig(handlers=[handler])
```

### 3. Add Distributed Tracing (OpenTelemetry)

```python
from opentelemetry import trace
from opentelemetry.exporter.gcp_trace import GoogleCloudTraceExporter

trace.set_tracer_provider(
    trace.TracerProvider(
        active_span_processor=trace.BatchSpanProcessor(
            GoogleCloudTraceExporter()
        )
    )
)

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("agent_run"):
    # ... agent execution
```

### 4. Add Performance Profiling

```python
import cProfile
import pstats
from io import StringIO

pr = cProfile.Profile()
pr.enable()

# ... agent execution

pr.disable()
s = StringIO()
ps = pstats.Stats(pr, stream=s)
ps.print_stats()
print(s.getvalue())
```

---

## Production Checklist

- [ ] Configure Cloud Logging export for all logs
- [ ] Set up Cloud Monitoring dashboard for key metrics
- [ ] Enable distributed tracing with OpenTelemetry
- [ ] Add alerting for error count > threshold
- [ ] Add alerting for latency p95 > SLA threshold
- [ ] Implement log retention policy (30 days default)
- [ ] Set up log-based metrics for custom queries
- [ ] Create runbooks for common failures
- [ ] Document on-call procedures

---

## Example: Custom Query

**"How many times did VisionAgent fail in the last hour?"**

```bash
gcloud logging read \
  'severity=ERROR AND jsonPayload.agent="VisionAgent" AND timestamp>="2025-12-01T09:00:00Z"' \
  --limit=10 \
  --format=json
```

---

## References

- [Google Cloud Logging](https://cloud.google.com/logging)
- [Google Cloud Monitoring](https://cloud.google.com/monitoring)
- [Google Cloud Trace](https://cloud.google.com/trace)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [ADK Observability](https://cloud.google.com/docs/agent-development-kit/observability)

---

**Built for:** Google AI Agents Intensive – Capstone Project
