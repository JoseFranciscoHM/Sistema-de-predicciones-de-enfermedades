# Specification: [SPEC-ID] [Feature Name]

> **Status:** Draft | Under Review | Approved | Superseded
> **Author:** [Name]
> **Date:** [YYYY-MM-DD]
> **Approved by:** [Name] on [YYYY-MM-DD]

---

## 1. Summary / Resumen

_Provide a clear, concise description of the feature or change in 2-3 sentences.
This section answers: "What problem are we solving and why?"_

**Problem:**
[Describe the current situation or pain point.]

**Proposed Solution:**
[Describe the solution at a high level.]

---

## 2. Actors / Stakeholders

_List all entities that interact with this feature._

| Actor | Description | Role |
|-------|-------------|------|
| [Actor 1] | [Who/what is this actor] | [How they interact] |
| [Actor 2] | [Who/what is this actor] | [How they interact] |

---

## 3. Functional Requirements

_Use RFC-2119 keywords: **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, **MAY**._

### 3.1. Core Requirements

- **FR-01:** The system **MUST** [requirement description].
- **FR-02:** The system **MUST** [requirement description].
- **FR-03:** The system **SHOULD** [requirement description].

### 3.2. Input / Output

_Define the inputs and outputs of the feature._

**Inputs:**
| Input | Type | Source | Validation |
|-------|------|--------|------------|
| [Input 1] | [Type] | [Where it comes from] | [Constraints] |

**Outputs:**
| Output | Type | Destination | Format |
|--------|------|-------------|--------|
| [Output 1] | [Type] | [Where it goes] | [Format details] |

---

## 4. Non-Functional Requirements

- **NFR-01:** [Performance] The system **SHOULD** [requirement].
- **NFR-02:** [Reliability] The system **MUST** [requirement].
- **NFR-03:** [Portability] The system **MAY** [requirement].

---

## 5. Acceptance Criteria

_Each criterion MUST be testable. Use Given/When/Then format._

- **AC-01:** Given [precondition], when [action], then [expected result].
- **AC-02:** Given [precondition], when [action], then [expected result].

---

## 6. Constraints and Assumptions

### Constraints
- [Constraint 1: e.g., "Must run on ESP32 with 4MB flash"]
- [Constraint 2: e.g., "Must complete processing within 10ms"]

### Assumptions
- [Assumption 1: e.g., "User has Python 3.11+ installed"]
- [Assumption 2: e.g., "Network connectivity is available"]

---

## 7. Open Questions

> [!IMPORTANT]
> These questions MUST be resolved before this specification can be approved.

- **Q1:** [Question about ambiguous requirement]
- **Q2:** [Question about edge case or boundary condition]

---

## 8. Diagrams (Optional)

_Include any diagrams that help clarify the specification: flow diagrams,
sequence diagrams, state machines, data flow diagrams, etc._

```
[Diagram placeholder — use mermaid, ASCII art, or reference an image file]
```

---

## 9. References

- [Reference 1: link to related specification, documentation, or standard]
- [Reference 2: link to related specification, documentation, or standard]
