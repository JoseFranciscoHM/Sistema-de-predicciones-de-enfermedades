# Data Model: [Model Name]

> **Specification Reference:** [Link to spec]
> **Plan Reference:** [Link to plan]
> **Date:** [YYYY-MM-DD]

---

## 1. Overview

_Brief description of this data model and its purpose within the system._

---

## 2. Entities

### 2.1. [Entity Name]

_Description of what this entity represents._

**Fields:**

| Field Name | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `id` | `int` / `uuid` | Yes | auto | Primary key | Unique identifier |
| `name` | `string` | Yes | — | max 255 chars | Display name |
| `created_at` | `datetime` | Yes | now() | Immutable | Creation timestamp |
| `[field_n]` | `[type]` | Yes/No | `[default]` | `[constraints]` | [Description] |

**Validations:**
- `name` MUST NOT be empty or contain only whitespace.
- [Additional validation rules]

**Indexes:**
- Primary: `id`
- [Additional indexes for query optimization]

---

### 2.2. [Entity Name 2]

_Description of this entity._

**Fields:**

| Field Name | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `[field]` | `[type]` | Yes/No | `[default]` | `[constraints]` | [Description] |

---

## 3. Relationships

_Define how entities relate to each other._

| Source Entity | Relationship | Target Entity | Cardinality | Description |
|--------------|-------------|---------------|-------------|-------------|
| [Entity A] | has_many | [Entity B] | 1:N | [Description] |
| [Entity B] | belongs_to | [Entity A] | N:1 | [Description] |

### Relationship Diagram

```
[Entity A] 1 ──── N [Entity B]
    │
    └── 1 ──── 1 [Entity C]
```

---

## 4. Data Structures (Non-Database)

_For embedded/firmware projects: define structs, enums, and data formats._

### 4.1. [Struct/Enum Name]

```
// Pseudocode or language-specific definition
struct [StructName] {
    field_1: type    // Description
    field_2: type    // Description
}
```

**Memory Layout:** [Total size in bytes, alignment requirements]

### 4.2. Communication Protocols

_Define data formats for serial, I2C, SPI, or network communication._

| Byte Offset | Field | Size (bytes) | Type | Description |
|------------|-------|------|------|-------------|
| 0 | header | 1 | uint8 | Packet identifier |
| 1 | payload_length | 2 | uint16 | Length of payload |
| 3 | payload | N | bytes | Data payload |
| 3+N | checksum | 1 | uint8 | XOR checksum |

---

## 5. Migrations / State Transitions

_If applicable, describe how data evolves over time._

### State Machine

| Current State | Event | Next State | Side Effects |
|--------------|-------|------------|--------------|
| [State A] | [Event] | [State B] | [What happens] |

---

## 6. Constraints and Invariants

_List all constraints that MUST hold true at all times._

- **INV-01:** [Invariant description — e.g., "sensor_value MUST be between 0 and 4095"]
- **INV-02:** [Invariant description]

---

## 7. Example Data

_Provide concrete examples to clarify the model._

```json
{
  "id": 1,
  "name": "example_sensor",
  "value": 2048,
  "created_at": "2026-01-15T10:30:00Z"
}
```
