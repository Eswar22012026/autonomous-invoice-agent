# Autonomous Invoice Processing Agent

An autonomous AI-worker prototype that processes invoices from a simulated company system.

The agent accepts a natural-language task such as:

> Process the latest invoice from ABC Technologies

It then understands the request, creates an execution plan, searches for the latest invoice, reads and extracts the invoice data, validates financial totals, requests human approval before making a sensitive change, saves the result, verifies the saved data, and records the complete execution history.

---

## 1. Project Goal

The goal of this project is to prototype an enterprise-style AI worker rather than a simple invoice parser.

The agent follows this workflow:

```text
User Request
     ↓
Understand
     ↓
Plan
     ↓
Find Invoice
     ↓
Read Invoice
     ↓
Extract Information
     ↓
Validate
     ↓
Human Approval
     ↓
Save to Company System
     ↓
Verify
     ↓
Complete / Escalate
     ↓
Audit Log