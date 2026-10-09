# Autonomous Invoice Processing Agent

An AI-powered invoice-processing prototype that uses Python and Google Gemini to understand user requests and process invoices in a simulated company system.

## Project Overview

The agent accepts a natural-language task, identifies the requested vendor, searches for an invoice, extracts its information, validates the available financial data, requests human approval, and verifies the result.

## Features

- **Natural-language understanding:** Uses Google Gemini to identify the requested company.
- **Execution planning:** Displays the steps required to process an invoice.
- **Invoice search and retry:** Searches for the requested invoice and retries if the first attempt fails.
- **Data extraction:** Extracts invoice details from local text files.
- **Financial validation:** Checks invoice financial information using project validation logic.
- **Human approval:** Requests confirmation before attempting to save an invoice.
- **Duplicate prevention:** Avoids creating duplicate invoice records.
- **Verification:** Checks that saved invoice information matches the extracted data.
- **Audit logging:** Records execution events and errors.
- **Human escalation:** Stops and reports when an invoice cannot be found.

## Technology Stack

- Python
- Google Gemini API (`google-genai`)
- JSON for simulated company-system storage
- Text files for sample invoices

## Project Workflow

1. Receive a natural-language task.
2. Identify the requested vendor.
3. Create an execution plan.
4. Search for the invoice.
5. Read the invoice.
6. Extract invoice information.
7. Validate financial information.
8. Request human approval.
9. Save the invoice if appropriate.
10. Verify the result and record execution events.

## Requirements

- Python installed
- Google Gemini API key
- Internet connection for Gemini API requests

## Setup

1. Clone or download this repository.
2. Open a terminal in the project directory.
3. Create and activate a virtual environment.

   Windows:

   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   ```

4. Install dependencies:

   ```cmd
   pip install -r requirements.txt
   ```

5. Set the `GEMINI_API_KEY` environment variable in Windows. Obtain an API key from [Google AI Studio](https://aistudio.google.com/apikey).

   Do not put your API key directly in the source code or commit it to GitHub.

## Run the Project

Run the agent from the project directory:

```cmd
python agent.py
```

When prompted, enter a task such as:

```text
Process the latest invoice from ABC Technologies
```

Review the invoice summary and respond to the approval prompt as appropriate.

## Test Scenarios

### Successful invoice search

```text
Process the latest invoice from ABC Technologies
```

Expected behavior: The agent finds the sample invoice, extracts its details, validates the available financial information, requests approval, and verifies the company-system record.

### Missing invoice

```text
Process the latest invoice from XYZ Technologies
```

Expected behavior: The agent retries the search and reports that human assistance may be required if the invoice is not found.

### Duplicate prevention

Run the same invoice-processing task again. The agent should detect an existing invoice rather than create a duplicate record.

## Project Limitations

- This is a prototype that uses local sample files and a simulated company system.
- It does not connect to a real accounting platform or perform real payments.
- Invoice search and extraction depend on the sample data and implemented parsing logic.
- Financial validation is limited to the checks implemented in the project.
- Human approval is required before attempting to save an invoice.
- Gemini availability depends on API access, network connectivity, and applicable usage limits.

## Security

- Never commit API keys, `.env` files, or other secrets.
- Keep virtual-environment files and generated logs out of version control when appropriate.
- Use human review before making changes to financial records.

## Future Improvements

- Support PDF invoices and OCR.
- Add automated unit and integration tests.
- Improve invoice-field extraction and validation.
- Connect to a real accounting system through a secure API.
- Add structured audit reports and stronger error handling.

## Disclaimer

This project is an educational prototype demonstrating an AI-assisted workflow. It is not a production-ready financial system.
