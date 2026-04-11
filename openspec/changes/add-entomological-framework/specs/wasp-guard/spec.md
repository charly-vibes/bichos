# Wasp Guard Agent Specification

> **Implementation status: Planned.** This capability is gated on the Phase 6 go/no-go decision. Configuration values (model, TTL, quorum settings) are defined by `HiveConfig` and `StigmergyConfig`; this spec references illustrative defaults that will be reconciled with the canonical config when implemented.

## ADDED Requirements

### Requirement: Security Hydrocarbon Profile Analysis
The system SHALL analyze source code regions as "chemical signatures" to detect security anti-patterns and vulnerabilities.

#### Scenario: Analyze function for security anti-patterns
- **WHEN** guard analyzes a code region
- **THEN** CodeSecurityContext model contains file_path, function_name, source_code, imports, external_inputs fields
- **AND** chemical profile is checked for security anomalies

#### Scenario: Detect SQL injection pattern
- **WHEN** source code constructs SQL queries with string concatenation of external inputs
- **THEN** SecurityVerdict marks is_safe=False
- **AND** threat_level is set to 9
- **AND** threat_type is "sql_injection"

#### Scenario: Detect XSS pattern
- **WHEN** source code renders user-supplied data without escaping in template output
- **THEN** SecurityVerdict marks is_safe=False
- **AND** threat_level is set to 8
- **AND** threat_type is "xss"

### Requirement: Threat Severity Classification
The system SHALL classify security threats on a scale of 0-10 with reasoning.

#### Scenario: Critical threat (9-10)
- **WHEN** SQL injection or RCE vulnerability is detected
- **THEN** threat_level ≥ 9
- **AND** alarm pheromone is immediately released

#### Scenario: High threat (7-8)
- **WHEN** XSS or CSRF vulnerability is detected
- **THEN** threat_level is 7-8
- **AND** warning is logged

#### Scenario: Low threat (1-3)
- **WHEN** minor sanitization issue is detected
- **THEN** threat_level is 1-3
- **AND** informational report is created

#### Scenario: No threat (0)
- **WHEN** code region has no security concerns
- **THEN** SecurityVerdict marks is_safe=True
- **AND** threat_level is 0
- **AND** threat_type is "none"

### Requirement: Alarm Pheromone System
The system SHALL propagate security alerts through pheromone deposition and structured logging.

#### Scenario: Release alarm for critical threat
- **WHEN** threat_level > 7
- **THEN** alert pheromone is deposited with intensity = threat_level * 5
- **AND** Loguru error log is created with tags ["security", "wasp_alarm", "defcon_1"]

#### Scenario: Alarm attracts more guard wasps
- **WHEN** alert pheromone is deposited in module "payment"
- **THEN** other wasps' probability of inspecting "payment" increases
- **AND** swarm focuses on high-threat areas

#### Scenario: Update global hive state
- **WHEN** critical threat is detected
- **THEN** hive_state is set to "ALERT_MODE" in cache
- **AND** all other agents become more defensive

### Requirement: Agent Tool: analyze_hydrocarbon_profile
The system SHALL provide a tool for threat detection via LLM reasoning over source code.

#### Scenario: Tool returns SecurityVerdict
- **WHEN** analyze_hydrocarbon_profile(code_context) is called with a CodeSecurityContext
- **THEN** SecurityVerdict Pydantic model is returned
- **AND** contains is_safe, threat_level, threat_type, reasoning fields

#### Scenario: Tool uses large context model
- **WHEN** guard analyzes complex code patterns across a module
- **THEN** a large-context model is used as configured in HiveConfig
- **AND** enables detection of subtle vulnerability patterns spanning multiple functions

#### Scenario: Tool validates output schema
- **WHEN** LLM returns threat analysis
- **THEN** Pydantic validates threat_level is in range 0-10
- **AND** ValidationError prevents hallucinated threat levels

### Requirement: Agent Tool: release_alarm_pheromone
The system SHALL provide a tool for broadcasting security alerts with file and function location.

#### Scenario: Deposit alarm pheromone
- **WHEN** release_alarm_pheromone(verdict, file_path, function_name) is called with threat_level=9
- **THEN** alert pheromone is deposited with intensity 45.0
- **AND** TTL is set to 24 hours

#### Scenario: Structured logging for alerting
- **WHEN** alarm is released
- **THEN** Loguru log entry includes: threat_level, file_path, function_name, reasoning, timestamp
- **AND** log level is ERROR for threat_level > 7

### Requirement: Agent Tool: scan_for_vulnerabilities
The system SHALL provide a tool for static security analysis of code.

#### Scenario: Scan for hardcoded secrets
- **WHEN** code contains strings matching pattern "password = 'secret123'"
- **THEN** vulnerability is flagged with type="hardcoded_secret"
- **AND** threat_level is set to 9

#### Scenario: Scan for unsafe deserialization
- **WHEN** code uses `pickle.loads()` on untrusted input
- **THEN** vulnerability is flagged with type="unsafe_deserialization"
- **AND** threat_level is set to 10

#### Scenario: Scan for missing authentication
- **WHEN** API endpoint has no authentication decorator
- **THEN** vulnerability is flagged with type="missing_auth"
- **AND** threat_level is set to 8

### Requirement: Quorum Sensing for Consensus (Opt-In)
The system SHALL optionally use multiple guard agents with different models to reduce false positives. Quorum sensing is disabled by default (single model) due to cost multiplier (~3-5x per security check, depending on quorum_size). Enable via `wasp.quorum_sensing: true` in config.

#### Scenario: Default single-model analysis
- **WHEN** quorum_sensing is disabled (default)
- **THEN** single wasp agent returns SecurityVerdict
- **AND** confidence is based on single model's reasoning

#### Scenario: Opt-in quorum with 3 guard wasps
- **WHEN** quorum_sensing is enabled with quorum_size=3
- **THEN** 3 wasp agents are spawned using the configured model
- **AND** each returns independent SecurityVerdict
- **AND** cost is ~3x single-model analysis

#### Scenario: Quorum requires majority agreement
- **WHEN** verdicts are [unsafe, unsafe, safe]
- **THEN** quorum consensus is "unsafe" (2/3 majority)
- **AND** action is taken based on majority vote

#### Scenario: Quorum reduces false positives
- **WHEN** one model hallucinates a threat
- **AND** other 2 models mark input as safe
- **THEN** quorum overrides single false positive
- **AND** improves reliability

### Requirement: Guard Agent Configuration
The system SHALL configure wasp agents with large-context LLM models.

#### Scenario: Agent uses large context model
- **WHEN** guard agent is initialized
- **THEN** it uses a large-context model as configured in HiveConfig (e.g. `openai:gpt-4o` or a Gemini model when supported)
- **AND** system prompt instructs it to analyze security threats

#### Scenario: Agent has access to security config
- **WHEN** agent analyzes code
- **THEN** Deps includes security_rules (allowed patterns, blocked patterns)
- **AND** pheromone_cache for alert history

### Requirement: Security Alert TTL
The system SHALL use 24-hour TTL for security alert pheromones.

#### Scenario: Alert pheromone expires after 24 hours
- **WHEN** alert pheromone is deposited
- **THEN** it expires after 86400 seconds
- **AND** reflects urgent but time-bounded nature of security alerts

#### Scenario: Persistent threats trigger recurring alarms
- **WHEN** same vulnerability is found after pheromone expires
- **THEN** new alert pheromone is deposited
- **AND** indicates unresolved security issue

### Requirement: Defense Coordination
The system SHALL coordinate defensive responses across multiple wasp agents.

#### Scenario: Swarm focuses on vulnerable module
- **WHEN** multiple alerts are detected in module "auth"
- **THEN** more wasps are allocated to inspect "auth"
- **AND** intensive scanning is performed

#### Scenario: Defensive posture escalates
- **WHEN** hive_state is "ALERT_MODE"
- **THEN** all wasps lower their reporting threshold
- **AND** findings that would normally be informational are escalated to warnings
- **NOTE** This is a reporting posture change, not a defensive action — no code is modified

### Requirement: Read-Only Security Analysis
The system SHALL only report vulnerabilities without taking defensive actions.

#### Scenario: No code modification
- **WHEN** vulnerability is detected
- **THEN** report is generated with fix suggestions
- **AND** no source code is modified

#### Scenario: Report-only output
- **WHEN** analysis completes
- **THEN** SecurityReport contains all vulnerabilities with file paths and function locations
- **AND** user reviews and applies fixes
