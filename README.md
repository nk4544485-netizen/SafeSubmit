# SafeSubmit
TrustForm is a smart document verification system that analyzes uploaded files and user descriptions to generate a trust score and classify submissions as Accepted, Flagged, or Rejected using real backend validation logic.

# TrustForm – Document Trust Verification System

TrustForm is a full‑stack web application that helps verify user‑submitted documents and measure how trustworthy they are.

It takes a document upload and a short user description, runs multiple backend checks, and produces a **Trust Score (0–100)** along with a clear decision: **ACCEPTED, FLAGGED, or REJECTED**.

This project was built to simulate how real‑world systems validate files, detect duplicates, and assess content quality in applications like assignment portals, resume screening tools, and fraud‑detection platforms.

---

## 🚀 What TrustForm Can Do

* Upload documents in **PDF, DOCX, or TXT** format
* Validate user inputs (name, email, description)
* Extract readable text from uploaded files
* Compare document content with the user’s description
* Detect duplicate documents using file hashing
* Analyze content quality (length and word diversity)
* Generate a **Trust Score** based on multiple checks
* Classify submissions as:

  * **ACCEPTED** – looks valid and trustworthy
  * **FLAGGED** – needs manual review
  * **REJECTED** – likely invalid or low quality

---

## 🛠 Tech Stack

* **Backend:** Python, Flask
* **Frontend:** HTML, CSS
* **File Processing:** PyPDF2, python‑docx
* **Database:** SQLite
* **APIs:** JSON endpoints

---

## 📂 Project Structure

```
smart_submission_system/
│
├── app.py
├── database.db
├── uploads/
├── templates/
│   ├── index.html
│   └── result.html
├── static/
│   └── style.css
└── README.md
```

---

## ⚙️ Installation & Setup

1. Clone the repository

```bash
git clone https://github.com/yourusername/trustform.git
cd trustform
```

2. Install dependencies

```bash
pip install flask PyPDF2 python-docx
```

3. Run the application

```bash
python app.py
```

4. Open in your browser

```
http://127.0.0.1:5000/
```

---

## 🔍 How It Works

1. The user fills out a form and uploads a document
2. The backend extracts text from the uploaded file
3. The system performs several checks:

   * Duplicate detection using file hashing
   * Content quality analysis (length and diversity)
   * Description–document keyword matching
   * Basic metadata and input validation
4. A **Trust Score** is calculated (0–100)
5. The final result is displayed with a status and clear reasons

---

## 📊 Trust Score Logic

* Starting score: **100**
* Penalties are applied for:

  * Very short or low‑quality content
  * Duplicate files
  * Description mismatch
  * Invalid or missing metadata
  * File parsing errors

### Decision Rules

* **Score ≥ 75** → ACCEPTED
* **Score 50–74** → FLAGGED
* **Score < 50** → REJECTED

---

## 🧪 Example Output

```
Submission Status: FLAGGED
Trust Score: 62
Reasons:
- Low content length
- Description mismatch
```

---

## 📌 Use Cases

* Internship or assignment report verification
* Online submission portals
* Resume screening systems
* Basic document fraud‑detection tools

---

## 👨‍💻 Author

**Nirmal Kumar**
B.Tech – Artificial Intelligence & Data Science

---

## 📜 License

This project is built for educational and portfolio purposes.
