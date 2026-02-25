# Fixture Bug MANIFEST

Ground truth for all planted bugs in the `tests/fixtures/` directory.
Used as the benchmark oracle for precision/recall calculations in Phase 6.

Each row records the **exact location** of a `# BUG:` marker in a fixture
file.  Line numbers are the line on which the `# BUG:` comment appears.

---

## simple_bugs

| File | Line | Function | Bug Type | Severity | Description |
|------|------|----------|----------|----------|-------------|
| simple_bugs/calculator.py | 22 | divide | division-by-zero | 8 | No guard for denominator == 0; raises ZeroDivisionError instead of a meaningful error |
| simple_bugs/user_store.py | 30 | UserStore.get_user | missing-None-check | 7 | Returns None silently when user not found; callers that chain .attribute access raise AttributeError |
| simple_bugs/user_store.py | 38 | UserStore.deactivate | missing-None-check | 7 | Propagation: dereferences get_user() result without None guard, raising AttributeError on missing user |
| simple_bugs/config_loader.py | 17 | load_config | hardcoded-creds | 9 | Fallback value "changeme" for SECRET_KEY env var is a hardcoded credential; insecure in production |

### Clean files (no bugs)

- simple_bugs/data_processor.py
- simple_bugs/event_bus.py

---

## medium_bugs

| File | Line | Function | Bug Type | Severity | Description |
|------|------|----------|----------|----------|-------------|
| medium_bugs/db_users.py | 34 | UserRepository.find_by_username | sql-injection | 9 | Username interpolated directly into SQL string via f-string; allows SQL injection |
| medium_bugs/db_orders.py | 35 | OrderRepository.find_by_status | sql-injection | 9 | Status interpolated directly into SQL string via f-string; allows SQL injection |
| medium_bugs/auth_service.py | 18 | module-level | hardcoded-creds | 9 | JWT secret hardcoded as module-level constant; used as fallback when JWT_SECRET env var is absent |
| medium_bugs/email_client.py | 15 | module-level | hardcoded-creds | 9 | SendGrid API key hardcoded as module-level constant; credential committed to source |
| medium_bugs/session_cache.py | 30 | SessionCache.put | race-condition | 8 | Shared class-level dict mutated without a lock; concurrent writes from multiple threads can corrupt state |
| medium_bugs/job_queue.py | 36 | JobQueue.__init__ | race-condition | 8 | Job registry dict mutated from multiple worker threads without synchronisation; susceptible to data races |
| medium_bugs/product_service.py | 54 | ProductService.get_price | missing-None-check | 7 | find_by_sku() may return None; accessing .price_cents on None raises AttributeError |
| medium_bugs/invoice_service.py | 66 | InvoiceService.get_total | missing-None-check | 7 | find() may return None; accessing .total_cents on None raises AttributeError |
| medium_bugs/file_watcher.py | 49 | FileWatcher._fire | bare-except | 5 | Bare except clause silently swallows all exceptions from callbacks, including SystemExit and KeyboardInterrupt |
| medium_bugs/metrics_collector.py | 10 | module-level | unused-import | 2 | `import json` is unused; the module never references json after importing it |

### Clean files (no bugs)

- medium_bugs/config_manager.py
- medium_bugs/csv_parser.py
- medium_bugs/date_utils.py
- medium_bugs/email_validator.py
- medium_bugs/event_logger.py
- medium_bugs/file_utils.py
- medium_bugs/http_retry.py
- medium_bugs/pagination.py
- medium_bugs/rate_limiter.py
- medium_bugs/text_normalizer.py
