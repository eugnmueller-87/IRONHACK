# EXTRA 3 — Error Handling and Scheduled Workflows

## Files

| File | Description |
|---|---|
| [workflows/daily_data_fetcher.json](workflows/daily_data_fetcher.json) | Workflow 1: HTTP fetch with retry logic + error branch + error notification |
| [workflows/daily_summary_generator.json](workflows/daily_summary_generator.json) | Workflow 2: Scheduled (daily 9 AM) fetch with idempotency check + error handling |
| [lab_summary.md](lab_summary.md) | Required narrative paragraph for submission |
| [screenshots/](screenshots/) | Execution history screenshots (add after running in n8n) |

## How to run

1. Open [n8n](https://n8n.io) (local or cloud).
2. Go to **Workflows → Import from file**.
3. Import each `.json` file from the `workflows/` folder.
4. Click **Execute Workflow** to test manually.
5. For the scheduler: activate the workflow toggle — it will run automatically at 09:00 daily.

## Workflow 1: Daily Data Fetcher

```
Manual Trigger
  └─→ Fetch GitHub User  (retry: 3× / 5 s delay, continueErrorOutput)
        ├─→ [success] Process Success   → logs login, repos, timestamp
        └─→ [error]   Format Error Message → Log Notification
```

**Key settings on the HTTP Request node:**

- `onError: continueErrorOutput` — routes failures to output 2 instead of crashing
- `retry.maxTries: 3` / `retry.waitBetweenTries: 5000` — handles transient failures

## Workflow 2: Daily Summary Generator

```
Schedule Trigger (cron: 0 9 * * *)
  └─→ Set Today Date  (record_id = YYYY-MM-DD)
        └─→ Fetch Daily Data  (retry: 3× / 5 s, continueErrorOutput)
              ├─→ [success] Shape Summary Record
              │         └─→ Already Exists Today? (IF node)
              │               ├─→ [true]  Skip (Already Exists)
              │               └─→ [false] Append New Record
              └─→ [error]   Format Scheduled Error
```

**Idempotency:** the `record_id` is today's UTC date. The IF node blocks duplicate writes on the same day.

## Success criteria checklist

- [x] Error Trigger / error output connected
- [x] Retry logic on HTTP Request (3×, 5 s)
- [x] Error notification formatted
- [x] Schedule Trigger configured (daily 9 AM, cron `0 9 * * *`)
- [x] Idempotency check via date-keyed IF node
- [ ] Screenshots of execution history (add after running in n8n)
