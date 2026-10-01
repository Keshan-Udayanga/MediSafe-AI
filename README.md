# MediSafe-AI 

MediSafe-AI is a multi-agent AI system developed to provide users with medication-related information in a simple and reliable way.
The main idea of this project is to use AI together with a trusted document-based knowledge source instead of depending only on the LLM's own knowledge. This helps the system provide answers based on the information available in the knowledge base.

## Project Overview

The system has several main components:

* **Orchestrator Agent**
* **Information Agent**
* **Safety Agent**
* **Information Retrieval (IR)**
* **Large Language Model (LLM)**
* **Supabase Database**

The user first sends a medication-related question to the system. The Orchestrator manages the process and gets the required information from the relevant agents. The retrieved information is then given to the LLM to generate the final response.

### Basic Flow

User Query
    ↓
Orchestrator
    ↓
Information Retrieval
    ↓
Information / Safety Agents
    ↓
LLM
    ↓
Final Answer

## Information Retrieval

Information Retrieval is an important part of our system.
I worked mainly on this part. The system uses **TF-IDF** to find relevant information from the available medication documents.
When a user asks a question, the query is processed and compared with the available documents. The documents with higher relevance are selected and used as context for generating the answer.

The basic process is:

User Query
    ↓
Query Processing
    ↓
TF-IDF
    ↓
Relevant Documents
    ↓
Retrieved Information

## Agents

### Orchestrator Agent
The Orchestrator is responsible for coordinating the overall process. It receives the user query and manages the communication between the different components of the system.

### Information Agent
The Information Agent handles general medication information. It retrieves relevant information from the drug information documents.

### Safety Agent
The Safety Agent focuses on safety-related information such as warnings, precautions, side effects, and other safety considerations.

## Database
We used Supabase as the database for storing the documents used by the system.

The main document collections are:

drug_information_documents
safety_documents

These documents are used by the retrieval process to find information relevant to the user's query.

## My Contribution
My main contribution to this project was the **Orchestrator and Information Retrieval (IR) part**.

I worked on the retrieval process, including:

* Processing user queries
* Retrieving relevant documents
* Implementing TF-IDF based retrieval
* Connecting the retrieval process with the Orchestrator
* Providing the retrieved information as context for the LLM
* Testing the retrieval behaviour

## Technologies Used

* Python
* FastAPI
* Large Language Model (LLM)
* TF-IDF
* Supabase
* PostgreSQL
* Git & GitHub

## Testing
We tested the system using different testing methods to check both the functionality and security of the system.

Some of the testing areas were:

* Functional Testing
* Black Box Testing
* Negative Testing
* API Testing
* Information Retrieval Testing
* Safety Testing
* Privacy Testing
* Data Leakage Testing

## Future Improvements
The current system uses TF-IDF for information retrieval. In the future, the retrieval process could be improved using methods such as **BM25, semantic search, embeddings, or vector search**.
The system could also be improved with better safety validation, authentication, security controls, and more advanced LLM integration.

## Disclaimer
MediSafe-AI is an academic project developed for educational and research purposes.
The information provided by the system should not be considered a replacement for professional medical advice. Users should consult a qualified healthcare professional when making medical decisions.

## Project

**MediSafe-AI – Multi-Agent AI System for Medication Information**
This project demonstrates how **AI, LLMs, Information Retrieval, and multi-agent systems** can be combined to build a medication information system.
