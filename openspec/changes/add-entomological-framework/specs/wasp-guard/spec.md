# Wasp Guard Agent Specification

## ADDED Requirements

### Requirement: Security Hydrocarbon Profile Analysis
The system SHALL analyze code inputs and patterns as "chemical signatures" to detect threats.

#### Scenario: Analyze function input validation
- **WHEN** guard analyzes function that accepts user input
- **THEN** IncomingRequest model contains headers, payload, source_ip fields
- **AND** chemical profile is checked for anomalies

#### Scenario: Detect SQL injection pattern
- **WHEN** input contains SQL keywords without proper escaping
- **THEN** SecurityVerdict marks is_safe=False
- **AND** threat_level is set to 9
- **AND** threat_type is "sql_injection"

#### Scenario: Detect XSS pattern
- **WHEN** input contains `<script>` tags in untrusted context
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

### Requirement: Alarm Pheromone System
The system SHALL propagate security alerts through pheromone deposition and structured logging.

#### Scenario: Release alarm for critical threat
- **WHEN** threat_level > 7
- **THEN** alert pheromone is deposited with intensity = threat_level * 10
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
The system SHALL provide a tool for threat detection via LLM reasoning.

#### Scenario: Tool returns SecurityVerdict
- **WHEN** analyze_hydrocarbon_profile(request_data) is called
- **THEN** SecurityVerdict Pydantic model is returned
- **AND** contains is_safe, threat_level, threat_type, reasoning fields

#### Scenario: Tool uses large context model
- **WHEN** guard analyzes complex input patterns
- **THEN** model `google:gemini-1.5-pro` is used for large context window
- **AND** enables detection of subtle mimicry attacks

#### Scenario: Tool validates output schema
- **WHEN** LLM returns threat analysis
- **THEN** Pydantic validates threat_level is in range 0-10
- **AND** ValidationError prevents hallucinated threat levels

### Requirement: Agent Tool: release_alarm_pheromone
The system SHALL provide a tool for broadcasting security alerts.

#### Scenario: Deposit alarm pheromone
- **WHEN** release_alarm_pheromone(verdict, source_ip) is called with threat_level=9
- **THEN** alert pheromone is deposited with intensity 90.0
- **AND** TTL is set to 24 hours

#### Scenario: Structured logging for alerting
- **WHEN** alarm is released
- **THEN** Loguru log entry includes: threat_level, source_ip, reasoning, timestamp
- **AND** log level is ERROR for threat_level > 7

#### Scenario: Optional defensive action
- **WHEN** alarm is released and firewall integration is configured
- **THEN** IP blocking can be triggered (disabled by default)
- **AND** action is logged

### Requirement: Agent Tool: scan_for_vulnerabilities
The system SHALL provide a tool for static security analysis of code.

#### Scenario: Scan for hardcoded secrets
- **WHEN** code contains strings matching pattern "password = 'secret123'"
- **THEN** vulnerability is flagged with type="hardcoded_secret"
- **AND** severity is set to 9

#### Scenario: Scan for unsafe deserialization
- **WHEN** code uses `pickle.loads()` on untrusted input
- **THEN** vulnerability is flagged with type="unsafe_deserialization"
- **AND** severity is set to 10

#### Scenario: Scan for missing authentication
- **WHEN** API endpoint has no authentication decorator
- **THEN** vulnerability is flagged with type="missing_auth"
- **AND** severity is set to 8

### Requirement: Quorum Sensing for Consensus
The system SHALL use multiple guard agents with different models to reduce false positives.

#### Scenario: Spawn 5 guard wasps
- **WHEN** critical input needs validation
- **THEN** 5 wasp agents are spawned with different models (GPT-4, Claude, Gemini, Llama, etc.)
- **AND** each returns independent SecurityVerdict

#### Scenario: Quorum requires 3/5 agreement
- **WHEN** verdicts are [unsafe, unsafe, unsafe, safe, safe]
- **THEN** quorum consensus is "unsafe" (3/5)
- **AND** action is taken based on majority vote

#### Scenario: Quorum reduces false positives
- **WHEN** one model hallucinates a threat
- **AND** other 4 models mark input as safe
- **THEN** quorum overrides single false positive
- **AND** improves reliability

### Requirement: Guard Agent Configuration
The system SHALL configure wasp agents with large-context LLM models.

#### Scenario: Agent uses large context model
- **WHEN** guard agent is initialized
- **THEN** it uses `google:gemini-1.5-pro` (1M token context)
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

#### Scenario: Swarm focuses on breached module
- **WHEN** multiple alerts are detected in module "auth"
- **THEN** more wasps are allocated to inspect "auth"
- **AND** intensive scanning is performed

#### Scenario: Defensive posture escalates
- **WHEN** hive_state is "ALERT_MODE"
- **THEN** all wasps increase scrutiny threshold
- **AND** lower threat_level triggers alarms

### Requirement: Read-Only Security Analysis
The system SHALL only report vulnerabilities without taking defensive actions.

#### Scenario: No code modification
- **WHEN** vulnerability is detected
- **THEN** report is generated with fix suggestions
- **AND** no source code is modified

#### Scenario: No network blocking by default
- **WHEN** threat is detected from IP address
- **THEN** alert is logged
- **AND** IP is NOT blocked unless explicitly configured

#### Scenario: User applies fixes manually
- **WHEN** analysis completes
- **THEN** SecurityReport contains all vulnerabilities
- **AND** user reviews and applies fixes
