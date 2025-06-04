# Diagnostic Validation

This repo contains a FastAPI application that validates Philips engineers’ PDBE checklists via six concurrent Azure GPT‐4o calls—one per defined aspect. The final combined output is merged into a single JSON under the `case_id` key, preserving each aspect’s LLM response and comment.

- **Toggle prompts**: `USE_LOCAL_PROMPT=true|false`  
- **Prompt folder**: `prompts/local/validation/` must contain 6 pairs of `*_system.txt` & `*_user.txt`.  
- **Databases**:  
  - **PostgreSQL** (SQLAlchemy) for audit tables (`audit_logs`, `audit_events`).  
  - **Azure Cosmos DB** for PDBE templates (`prompts` container), raw I/O (`io` container), and configs (`configs` container).  
- **Azure AD** JWT + AD‐group (`AZ_T_PDP_Validation`) authentication on all APIs.  
- **Terraform** for VPC & EKS cluster (us-east-1).  
- **Kubernetes** manifests for deploying to EKS.  
- **Jenkins** pipeline for CI/CD.


