# Sentinel Curator -- User Guide

**Version:** 0.1.0
**Date:** 2026-03-25
**Audience:** Analysts, Intel Officers, Logistics Managers

---

## 1. What is Sentinel Curator?

Sentinel Curator is a secure natural-language interface for querying a military
asset tracking database. You type a question in plain English; the system
translates it to a database query, executes it safely, and returns the answer
filtered to your clearance level.

You do not need to know SQL or understand the database structure.

---

## 2. Your Clearance Level

Your clearance level determines what data you can see. It is set by your
system administrator and supplied automatically when you connect.

| Role | What you can see |
|---|---|
| ANALYST / LOGISTICS_MANAGER | Platform class names, descriptions, country of manufacture, operator country |
| RESTRICTED | Above plus platform GPS locations and timestamps |
| INTEL_OFFICER / CONFIDENTIAL | Above plus weapon mount details and RWR blind spot data |

If data is above your clearance, it will simply be absent from your results.
You will not receive an error -- the system silently omits columns you are
not cleared to see.

---

## 3. How to Ask a Question

Send your question to the /query endpoint with your role header set.

**Example -- find a platform by location:**

```
Question: Where was the USS Nimitz at 0800 UTC on 25 March 2026?
```

**Example -- find platforms by country:**

```
Question: List all platforms manufactured in the UK but operated by allied nations.
```

**Example -- find RWR vulnerabilities (requires INTEL_OFFICER clearance):**

```
Question: Which emitter IDs cannot be detected by the Type 45 destroyer RWR suite?
```

---

## 4. Understanding Responses

A typical response includes:

- **question** -- your original question
- **sql** -- the query that was generated and executed (for transparency and audit)
- **results** -- a list of matching records
- **clearance** -- the clearance level used to filter your results
- **duration_ms** -- how long the query took

If no matching records are found, results will be an empty list. This is normal.

If the system cannot answer your question from the available data (for example,
if you ask about data that does not exist in the schema), the message field will
explain this.

---

## 5. Tips for Better Questions

- Be specific about platform names. Use official designations where possible
  (e.g. USS Nimitz rather than just Nimitz).
- Include dates and times in ISO format or plain English
  (e.g. at 0800 UTC on 25 March 2026, or yesterday at noon UTC).
- For country queries, use full country names or ISO codes
  (e.g. United Kingdom or GB).
- If you get no results, try rephrasing or broadening your question.

---

## 6. What You Cannot Do

The system is read-only for all standard users. You cannot:

- Add or update platform records
- Delete data
- Grant access to other users

Any attempt to perform these actions (even if phrased as a question) will be
blocked by the SQL Guard and logged as a security event.

---

## 7. Getting Help

Contact your system administrator if:

- Your role does not match the data you expect to see.
- You receive a 401 (Unauthorised) error.
- The system is unavailable (503 error).

For query phrasing help, refer to the example questions in Section 3 above.
