# 🤖 MIRAI: Enterprise-Grade Hybrid Recommendation Engine

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1.svg?style=for-the-badge&logo=postgresql)](https://github.com/pgvector/pgvector)
[![Redis](https://img.shields.io/badge/Redis-Connection--Pooling-DC382D.svg?style=for-the-badge&logo=redis)](https://redis.io)
[![LangChain](https://img.shields.io/badge/LangChain-RAG-121212.svg?style=for-the-badge&logo=chainlink)](https://langchain.com)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini--Pro-4285F4.svg?style=for-the-badge&logo=google)](https://ai.google.dev/)

**MIRAI** is a sophisticated, production-ready Hybrid Recommendation System designed to aggregate, analyze, and personalize global entertainment content at scale. It leverages state-of-the-art NLP models, vector embeddings, and a hardened infrastructure to deliver highly accurate, sub-3-second discovery experiences across multiple languages.

---

## 🏗️ System Architecture

MIRAI employs a multi-stage recommendation pipeline that synthesizes diverse signals to optimize for both relevance and serendipity:

### 1. Hybrid Recommendation Core
The engine utilizes a weighted ensemble strategy:
*   **Semantic Search (Content-Based):** Deep thematic retrieval using multilingual embeddings and vector similarity.
*   **Collaborative Filtering:** Latent factor modeling via **Alternating Least Squares (ALS)** / Matrix Factorization, trained asynchronously on user interaction graphs.
*   **Dynamic Signals:** Real-time integration of trending peaks and global popularity scores.

### 2. Retrieval-Augmented Generation (RAG) & Explainable AI
MIRAI transforms "black-box" recommendations into transparent discovery:
*   **Massive Text Chunking:** Uses LangChain's `RecursiveCharacterTextSplitter` to index **40,000+ semantic text chunks**, ensuring granular thematic retrieval.
*   **Thematic Explanations:** Leverages **Google Gemini Pro** to synthesize "title-free" justifications in the user's native tongue, describing *why* a movie matches their specific mood.

### 3. True Multilingual Native Support
Engineered for a global audience with localized data ingestion:
*   **Cross-Lingual Vectors:** Native support for **English, Hindi, Telugu**, and 15+ other languages using the `paraphrase-multilingual-MiniLM-L12-v2` model.
*   **Localized Ingestion:** Automated TMDB data pipelines that fetch region-specific metadata (titles, overviews) across multiple locales.
*   **NLP Sentiment Analysis:** Employs **XLM-RoBERTa** for multilingual sentiment scoring on raw user reviews, dynamically boosting critically acclaimed content.

---

## 🛠️ Hardened Infrastructure

Designed for reliability and low-latency performance in high-concurrency environments:

-   **Vector Database Architecture:** Primary retrieval via **pgvector (PostgreSQL)** with an automated **FAISS (CPU/GPU)** fallback for local or development environments.
-   **Redis Connection Pooling:** Implements robust connection management and safe-call wrappers to ensure sub-3-second response times even during Redis downtime.
-   **Asynchronous Processing:** **Celery** handles heavy lifting, including offline model training and metadata updates, keeping the API responsive.
-   **Resilience Engineering:** Utilizes **Tenacity** for intelligent retry logic and exponential backoffs against upstream API rate limits.

---

## 📊 Performance & Evaluation

MIRAI isn't just fast; it's mathematically validated. The system includes a standalone evaluation suite that measures:
-   **Mean Average Precision (MAP@10)**
-   **NDCG@10 (Normalized Discounted Cumulative Gain)**
-   **Diversity Metrics:** MMR-based diversity filtering to prevent filter bubbles.

**Current Benchmark:** The system consistently demonstrates **>= 85% recommendation accuracy** against historical interaction hold-out sets.

---

## 🚀 Getting Started

### Prerequisites
*   Docker & Docker Compose
*   Python 3.10+
*   TMDB API Key & Google Gemini API Key

### Local Setup
1.  **Clone & Environment:**
    ```bash
    git clone https://github.com/Abhiram-0910/MRTS.git
    cd MRTS
    cp .env.example .env # Update with your API keys
    ```

2.  **Run with Docker (Recommended):**
    ```bash
    docker-compose up --build
    ```

3.  **Manual Installation:**
    ```bash
    pip install -r requirements.txt
    python backend/main.py
    ```

### Running Evaluation
To verify the system's accuracy on your local dataset:
```bash
python tests/evaluation.py --threshold 0.85
```

---

## 🤝 Support & Roadmap
MIRAI is under active development. Upcoming features include:
- [ ] Graph-based "Social Discovery" algorithms.
- [ ] Real-time stream-processing via Kafka.
- [ ] Deep reinforcement learning for session-based ranking.

**Made with ❤️ by the MIRAI Engineering Team.**