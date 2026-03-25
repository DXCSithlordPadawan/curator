# Product Requirements Document (PRD): Project Sentinel Curator

**Version:** 1.0  
**Status:** Draft  
**Date:** 2026-03-25  
**Compliance Target:** FIPS 140-3, CIS Level 2, RBAC  
**Author:** Iain Reid (Project Architect)

---

## 1. Executive Summary
The goal of **Project Sentinel** is to develop a secure, LLM-curated database system for tracking and managing global military assets. The system must handle complex relationships between platform designs (Classes), physical assets (Individual Platforms), weapon systems, and electronic warfare signatures—specifically Radar Warning Receiver (RWR) models and the "blind spots" (Emitter-IDs) they are incapable of detecting.

---

## 2. Functional Requirements

### 2.1 Data Schema & Relationships
The database utilizes a normalized relational structure to ensure data integrity and minimize redundancy across high-value military assets.

* **Platform Class:** The master template for ship/vehicle designs (e.g., Nimitz-class). Includes Country of Manufacture.
* **Individual Platform:** Specific physical instances (e.g., USS Nimitz). Includes Country of Operation, Country of Ownership, and unique hull/serial IDs.
* **Weapon Mounts:** Mapping of specific weapons to platform classes.
* **Weapons:** Mapping of specific weapons to platform Mounts.
* **Electronic Warfare (RWR):** Tracks RWR models and their specific **Emitter-ID Exclusions** (identifying specific frequencies or IDs the system is physically or logically incapable of detecting).
* **Spatiotemporal Tracking:** A time-series log of GPS coordinates (Latitude/Longitude) with UTC timestamps for every individual platform.

### 2.2 LLM Curator (The AI Layer)
The system employs a **Retrieval-Augmented Generation (RAG)** architecture to allow users to query the database using natural language.
* **SQL Generation:** The LLM translates English queries into valid SQL.
* **Validation Middleware:** A Python layer intercepts LLM-generated SQL to prevent "Write/Delete/Grant" actions unless explicitly authorized.
* **Context Awareness:** The LLM is provided with schema metadata (DDL) but does not have direct "sight" of the entire database to prevent data exfiltration.

---

## 3. Technical Specifications

### 3.1 Tech Stack
* **Database:** PostgreSQL 15+ with **PostGIS** extension for geographic calculations.
* **Language:** Python 3.11+ (SQLAlchemy / Pydantic).
* **Containerization:** Podman (Rootless) for service isolation.
* **Identity:** UUID v4 for all Primary Keys to prevent enumeration attacks.
* **API/Orchestration:** LangChain or LlamaIndex for LLM-to-DB tool-use.

### 3.2 Core Data Model (Representational)

| Entity | Key Fields |
| :--- | :--- |
| **PLATFORM_CLASS** | `UUID`, `Class_Name`, `Manufacturer_Country`, `Description` |
| **INDIVIDUAL_PLATFORM** | `UUID`, `Platform_ID (Hull #)`, `Class_FK`, `Operator_Country`, `Owner_Country` |
| **PLATFORM_Mounts** | `UUID`, `Mount_ID (Pylon #)`, `Platform_ID_FK`, `Operator_Country`, `Owner_Country` |
| **Weapon_Mounts** | `UUID`, `Mount_ID (20mm Canon #)`, `Mount_ID_FK`, `Operator_Country`, `Owner_Country` |
| **RWR_SYSTEM** | `UUID`, `Model_Name`, `Sensitivity_Range`, `Exclusion_Emitter_ID` |
| **GEOLOCATION_LOG** | `UUID`, `Platform_FK`, `Coordinates (Point)`, `Timestamp (UTC)` |

---

## 4. Security & Compliance

### 4.1 Access Control (RBAC)
To maintain operational security (OPSEC), data visibility is tiered:
* **Unclassified:** Platform Class descriptions and Country of Manufacture.
* **Restricted:** Individual platform locations (Telemetry).
* **Classified (Confidential):** Weapon mount specifics and RWR Emitter-ID exclusion lists (blind spots).

### 4.2 Security Standards
* **FIPS 140-3:** Requirement for all data-at-rest encryption.
* **CIS Level 2:** Database hardening and "Least Privilege" service accounts for the LLM agent.
* **Network Isolation:** Podman containers must communicate over an internal encrypted bridge with no external egress for the database container.

---

## 5. User Stories
* **As an Analyst,** I want to ask "Where was the USS Nimitz at 0800 UTC today?" and receive a map coordinate.
* **As an Intel Officer,** I want to know which Emitter-IDs are invisible to the Type 45 Destroyer's current RWR suite to assess vulnerability.
* **As a Logistics Manager,** I want to see a list of all platforms manufactured in the UK but operated by allied nations.

---

## 6. Implementation Roadmap (Paused)
1.  **Phase 1:** Finalize SQL DDL and Podman Compose environment.
2.  **Phase 2:** Develop the Python "Curator" Agent with LangChain/LlamaIndex.
3.  **Phase 3:** Implement RBAC filtering on the LLM output layer.
4.  **Phase 4:** Stress test with representational data and performance tuning.

---
