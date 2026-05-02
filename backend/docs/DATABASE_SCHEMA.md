# Database Schema Design - Phase 1

## Overview
This document outlines the database schema for the IBM Orchestrate Test Generator application. The schema is designed to support code analysis, AI-powered test generation, and GitHub integration.

## Core Models (apps/core)

### 1. UserProfile
Extends Django's built-in User model with GitHub integration.

**Fields:**
- `user` (OneToOne → User) - Link to Django User
- `github_username` (CharField) - GitHub username
- `github_access_token` (CharField) - OAuth token for GitHub API
- `github_id` (CharField, unique) - GitHub user ID
- `avatar_url` (URLField) - Profile picture URL
- `bio` (TextField) - User biography
- `created_at` (DateTimeField) - Account creation timestamp
- `updated_at` (DateTimeField) - Last update timestamp

**Relationships:**
- One-to-One with Django User model
- Many-to-Many with Organization (through OrganizationMembership)

---

### 2. Organization
Represents GitHub organizations or teams.

**Fields:**
- `name` (CharField) - Organization name
- `github_id` (CharField, unique) - GitHub organization ID
- `description` (TextField) - Organization description
- `avatar_url` (URLField) - Organization logo/avatar
- `created_at` (DateTimeField) - Creation timestamp
- `updated_at` (DateTimeField) - Last update timestamp

**Relationships:**
- Many-to-Many with User (through OrganizationMembership)
- One-to-Many with Repository

---

### 3. OrganizationMembership
Junction table for User-Organization relationship with roles.

**Fields:**
- `user` (ForeignKey → User)
- `organization` (ForeignKey → Organization)
- `role` (CharField) - Choices: owner, admin, member
- `joined_at` (DateTimeField) - Membership start date

**Constraints:**
- Unique together: (user, organization)

---

### 4. Repository
Represents GitHub repositories to be analyzed.

**Fields:**
- `name` (CharField) - Repository name
- `full_name` (CharField) - Full name (owner/repo)
- `github_id` (CharField, unique) - GitHub repository ID
- `owner` (ForeignKey → User) - Repository owner
- `organization` (ForeignKey → Organization, nullable) - Parent organization
- `description` (TextField) - Repository description
- `url` (URLField) - GitHub URL
- `clone_url` (URLField) - Git clone URL
- `default_branch` (CharField) - Default branch name (e.g., main)
- `language` (CharField) - Primary programming language
- `is_private` (BooleanField) - Privacy status
- `is_active` (BooleanField) - Active for analysis
- `stars_count` (IntegerField) - GitHub stars
- `forks_count` (IntegerField) - GitHub forks
- `last_synced_at` (DateTimeField) - Last sync with GitHub
- `created_at` (DateTimeField) - Creation timestamp
- `updated_at` (DateTimeField) - Last update timestamp

**Indexes:**
- github_id
- (owner, name)

**Relationships:**
- Many-to-One with User (owner)
- Many-to-One with Organization
- Many-to-Many with Project
- One-to-Many with CodeAnalysis
- One-to-Many with WebhookEvent

---

### 5. Project
Groups multiple repositories for analysis.

**Fields:**
- `name` (CharField) - Project name
- `description` (TextField) - Project description
- `owner` (ForeignKey → User) - Project owner
- `status` (CharField) - Choices: active, archived, paused
- `settings` (JSONField) - Project-specific settings
- `created_at` (DateTimeField) - Creation timestamp
- `updated_at` (DateTimeField) - Last update timestamp

**Relationships:**
- Many-to-One with User (owner)
- Many-to-Many with Repository

---

### 6. WebhookEvent
Logs GitHub webhook events for processing.

**Fields:**
- `repository` (ForeignKey → Repository)
- `event_type` (CharField) - Choices: push, pull_request, issues, release, other
- `payload` (JSONField) - Full webhook payload
- `processed` (BooleanField) - Processing status
- `processed_at` (DateTimeField) - Processing timestamp
- `error_message` (TextField) - Error details if processing failed
- `created_at` (DateTimeField) - Event receipt timestamp

**Indexes:**
- (repository, event_type)
- (processed, created_at)

---

## Analysis Models (apps/analysis)

### 7. CodeAnalysis
Represents a code analysis session.

**Fields:**
- `repository` (ForeignKey → Repository)
- `branch` (CharField) - Git branch analyzed
- `commit_sha` (CharField) - Git commit hash
- `initiated_by` (ForeignKey → User) - User who started analysis
- `status` (CharField) - Choices: pending, running, completed, failed
- `analysis_type` (CharField) - Choices: full, incremental, targeted
- `started_at` (DateTimeField) - Analysis start time
- `completed_at` (DateTimeField) - Analysis completion time
- `error_message` (TextField) - Error details if failed
- `metadata` (JSONField) - Additional analysis metadata
- `created_at` (DateTimeField) - Creation timestamp

**Relationships:**
- Many-to-One with Repository
- Many-to-One with User (initiated_by)
- One-to-Many with AnalysisResult
- One-to-Many with CodeMetrics

---

### 8. AnalysisResult
Stores detailed analysis results for code files.

**Fields:**
- `analysis` (ForeignKey → CodeAnalysis)
- `file_path` (CharField) - Relative path to file
- `file_type` (CharField) - File extension/type
- `language` (CharField) - Programming language
- `ast_data` (JSONField) - Abstract Syntax Tree data
- `complexity_score` (IntegerField) - Cyclomatic complexity
- `lines_of_code` (IntegerField) - Total lines
- `functions_count` (IntegerField) - Number of functions
- `classes_count` (IntegerField) - Number of classes
- `test_coverage` (FloatField) - Current test coverage %
- `issues` (JSONField) - List of detected issues
- `created_at` (DateTimeField) - Creation timestamp

**Indexes:**
- (analysis, file_path)

**Relationships:**
- Many-to-One with CodeAnalysis
- One-to-Many with TestSuggestion

---

### 9. CodeMetrics
Aggregated metrics for an analysis session.

**Fields:**
- `analysis` (ForeignKey → CodeAnalysis)
- `total_files` (IntegerField) - Total files analyzed
- `total_lines` (IntegerField) - Total lines of code
- `total_functions` (IntegerField) - Total functions
- `total_classes` (IntegerField) - Total classes
- `average_complexity` (FloatField) - Average complexity score
- `overall_coverage` (FloatField) - Overall test coverage %
- `high_priority_issues` (IntegerField) - Count of critical issues
- `medium_priority_issues` (IntegerField) - Count of medium issues
- `low_priority_issues` (IntegerField) - Count of low issues
- `created_at` (DateTimeField) - Creation timestamp

**Relationships:**
- One-to-One with CodeAnalysis

---

### 10. TestSuggestion
AI-generated test suggestions for code.

**Fields:**
- `analysis_result` (ForeignKey → AnalysisResult)
- `function_name` (CharField) - Target function/method
- `test_type` (CharField) - Choices: unit, integration, e2e
- `priority` (CharField) - Choices: high, medium, low
- `suggested_test_code` (TextField) - Generated test code
- `rationale` (TextField) - Why this test is needed
- `confidence_score` (FloatField) - AI confidence (0-1)
- `status` (CharField) - Choices: pending, approved, rejected, implemented
- `created_at` (DateTimeField) - Creation timestamp
- `updated_at` (DateTimeField) - Last update timestamp

**Relationships:**
- Many-to-One with AnalysisResult

---

## AI Engine Models (apps/ai_engine)

### 11. AIRequest
Tracks requests to AI services.

**Fields:**
- `user` (ForeignKey → User)
- `request_type` (CharField) - Choices: test_generation, code_review, refactoring
- `input_data` (JSONField) - Input sent to AI
- `model_used` (CharField) - AI model identifier
- `status` (CharField) - Choices: pending, processing, completed, failed
- `tokens_used` (IntegerField) - Token consumption
- `cost` (DecimalField) - API cost
- `created_at` (DateTimeField) - Request timestamp
- `completed_at` (DateTimeField) - Completion timestamp

**Relationships:**
- Many-to-One with User
- One-to-One with AIResponse

---

### 12. AIResponse
Stores AI service responses.

**Fields:**
- `request` (OneToOne → AIRequest)
- `output_data` (JSONField) - AI response data
- `processing_time` (FloatField) - Time taken (seconds)
- `error_message` (TextField) - Error details if failed
- `metadata` (JSONField) - Additional response metadata
- `created_at` (DateTimeField) - Response timestamp

**Relationships:**
- One-to-One with AIRequest

---

### 13. ModelConfiguration
Stores AI model configurations and prompts.

**Fields:**
- `name` (CharField) - Configuration name
- `model_identifier` (CharField) - Model ID (e.g., llama-3-70b)
- `provider` (CharField) - Choices: watsonx, openai, anthropic
- `system_prompt` (TextField) - System prompt template
- `temperature` (FloatField) - Model temperature
- `max_tokens` (IntegerField) - Maximum tokens
- `is_active` (BooleanField) - Active configuration
- `parameters` (JSONField) - Additional model parameters
- `created_at` (DateTimeField) - Creation timestamp
- `updated_at` (DateTimeField) - Last update timestamp

---

## Relationships Summary

```
User ←→ UserProfile (1:1)
User ←→ Organization (M:M through OrganizationMembership)
User → Repository (1:M as owner)
User → Project (1:M as owner)
User → CodeAnalysis (1:M as initiator)
User → AIRequest (1:M)

Organization → Repository (1:M)

Repository ←→ Project (M:M)
Repository → CodeAnalysis (1:M)
Repository → WebhookEvent (1:M)

CodeAnalysis → AnalysisResult (1:M)
CodeAnalysis ←→ CodeMetrics (1:1)

AnalysisResult → TestSuggestion (1:M)

AIRequest ←→ AIResponse (1:1)
```

## Indexes Strategy

**High-Priority Indexes:**
1. Repository.github_id (unique lookups)
2. Repository.(owner, name) (common queries)
3. WebhookEvent.(repository, event_type) (webhook processing)
4. WebhookEvent.(processed, created_at) (queue processing)
5. AnalysisResult.(analysis, file_path) (result lookups)

**Future Considerations:**
- Full-text search on code content
- Time-series optimization for metrics
- Partitioning for large webhook tables

## Migration Strategy

**Phase 1:** Core models (User, Repository, Organization)
**Phase 2:** Analysis models (CodeAnalysis, AnalysisResult)
**Phase 3:** AI models (AIRequest, AIResponse)
**Phase 4:** Optimization (indexes, constraints)