https://airtable.com/appRSkwfK4tGHPJqO/shrchmSdLoNcMpc6u/tbl1dM90vNx9iWU5c/viwBmYWPHr8HTKc28

```markdown
# Airtable Contractor System Documentation

## Overview

The Airtable Contractor System is a comprehensive solution for managing contractor applications through Airtable with automated processing, LLM evaluation, and intelligent shortlisting. The system uses multiple linked tables to store applicant data and automated scripts to process and evaluate candidates.

## System Architecture

### Table Structure

**Main Tables:**
- **Applicants** (`tbl1dM90vNx9iWU5c`) - Primary table with applicant metadata and evaluation results
- **Personal Details** (`tbliQIuyagwYx85I2`) - Contact and personal information
- **Work Experience** (`tblC7e5XeQT22Lc9q`) - Employment history and skills
- **Salary Preferences** (`tbltZZEsH06HwUcVH`) - Compensation expectations and availability
- **Shortlisted Leads** (`tblmNFvsGEVYyRgHY`) - Qualified candidates for outreach

### Field Definitions

#### Applicants Table
- `Applicant ID` (AutoNumber) - Unique identifier
- `Compressed JSON` (Long Text) - Consolidated applicant data in JSON format
- `Shortlist Status` (Single Select) - Manual shortlisting status
- `LLM Summary` (Long Text) - AI-generated applicant summary
- `LLM Score` (Number) - Quality score (0-100)
- `LLM Follow-Ups` (Long Text) - Suggested questions for follow-up

#### Personal Details Table
- `Applicant ID` (Link to Applicants) - Reference to main applicant
- `Full Name` (Single Line Text)
- `Email` (Email)
- `Location` (Single Line Text)
- `LinkedIn` (URL)

#### Work Experience Table
- `Applicant ID` (Link to Applicants)
- `Company` (Single Line Text)
- `Title` (Single Line Text)
- `Start` (Date)
- `End` (Date)
- `Technologies` (Multiple Select)

#### Salary Preferences Table
- `Applicant ID` (Link to Applicants)
- `Preferred Rate` (Currency)
- `Minimum Rate` (Currency)
- `Currency` (Single Select)
- `Availability` (Number) - Hours per week

#### Shortlisted Leads Table
- `Applicant ID` (Link to Applicants)
- `Compressed JSON` (Long Text)
- `Score Reason` (Long Text) - Explanation of shortlisting decision

## Setup Instructions

### Prerequisites
- Python 3.9+
- Airtable account with API access
- OpenAI API key (for LLM features)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd airtable-contractor-system
   ```

2. **Set up environment**
   ```bash
   make setup-complete
   ```

3. **Configure environment variables**
   Edit the `.env` file with your API keys:
   ```bash
   AIRTABLE_API_KEY=your_airtable_api_key_here
   AIRTABLE_BASE_ID=your_base_id_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Find your Airtable Base ID**
   ```bash
   make find-base-id
   ```

### Airtable Base Setup

Run the setup script to create the necessary tables and fields:

```bash
make check-airtable
```

### Form Creation

The system includes helper scripts to create Airtable forms for data entry:

```bash
make forms-help
```

## Automation Workflows

### 1. JSON Compression

The compression script gathers data from all linked tables and creates a consolidated JSON object stored in the main Applicants table.

**Script:** `scripts/compress_json.py`

```python
def compress_applicant_data(applicant_id: str) -> Dict[str, Any]:
    client = AirtableClient()
    applicant_data = client.get_applicant_data(applicant_id)
    
    compressed_json = {
        "personal": {
            "full_name": applicant_data["personal_details"]["Full Name"],
            "email": applicant_data["personal_details"]["Email"],
            "location": applicant_data["personal_details"]["Location"],
            "linkedin": applicant_data["personal_details"]["LinkedIn"],
        },
        "experience": [],
        "salary": {
            "preferred_rate": applicant_data["salary_preferences"]["Preferred Rate"],
            "minimum_rate": applicant_data["salary_preferences"]["Minimum Rate"],
            "currency": applicant_data["salary_preferences"]["Currency"],
            "availability": applicant_data["salary_preferences"]["Availability"],
        },
    }
    
    client.update_applicant_json(applicant_id, compressed_json)
    return compressed_json
```

### 2. LLM Evaluation

The LLM evaluation script analyzes each applicant's compressed JSON data and provides scores, summaries, and follow-up questions.

**Script:** `scripts/llm_evaluation.py`

```python
def evaluate_applicant(applicant_data: Dict) -> Dict:
    llm_client = LLMClient()
    prompt = f"""
    Evaluate this applicant data and provide:
    - summary: 2-3 sentence summary
    - score: 0-100 quality score
    - follow_ups: suggested follow-up questions
    
    Applicant data: {json.dumps(applicant_data)}
    """
    
    evaluation = llm_client.evaluate_applicant(applicant_data)
    
    return {
        'LLM Summary': evaluation['summary'],
        'LLM Score': evaluation['score'],
        'LLM Follow-Ups': "\n".join(evaluation['follow_ups'])
    }
```

### 3. Candidate Shortlisting

The shortlisting script applies configurable criteria to identify qualified candidates.

**Script:** `scripts/shortlist_candidates.py`

```python
def shortlist_candidates():
    client = AirtableClient()
    applicants = client.get_records(settings.APPLICANTS_TABLE)
    
    for applicant in applicants:
        compressed_json = json.loads(applicant['fields']['Compressed JSON'])
        
        # Evaluate against criteria
        meets_criteria = (
            len(compressed_json['experience']) >= settings.MIN_EXPERIENCE and
            compressed_json['salary']['preferred_rate'] <= settings.MAX_HOURLY_RATE and
            any(loc in compressed_json['personal']['location'] 
                for loc in settings.ELIGIBLE_LOCATIONS) and
            compressed_json['salary']['availability'] >= settings.MIN_AVAILABILITY
        )
        
        if meets_criteria:
            client.create_record(settings.SHORTLISTED_LEADS_TABLE, {
                'Applicant ID': [applicant['id']],
                'Compressed JSON': applicant['fields']['Compressed JSON'],
                'Score Reason': f"Meets all shortlisting criteria"
            })
```

### 4. JSON Decompression

The decompression script reads compressed JSON and updates child tables, useful for data restoration or migration.

**Script:** `scripts/decompress_json.py`

```python
def decompress_json(applicant_id: str, compressed_json: Dict):
    client = AirtableClient()
    
    # Update personal details
    client.update_or_create_record(
        settings.PERSONAL_DETAILS_TABLE,
        {'Applicant ID': applicant_id},
        compressed_json['personal']
    )
    
    # Update work experience (clear and recreate)
    client.delete_matching_records(
        settings.WORK_EXPERIENCE_TABLE,
        {'Applicant ID': applicant_id}
    )
    for exp in compressed_json['experience']:
        client.create_record(settings.WORK_EXPERIENCE_TABLE, {
            **exp,
            'Applicant ID': [applicant_id]
        })
    
    # Update salary preferences
    client.update_or_create_record(
        settings.SALARY_PREFERENCES_TABLE,
        {'Applicant ID': applicant_id},
        compressed_json['salary']
    )
```

## LLM Integration Configuration

### Provider Setup

The system supports multiple LLM providers configured through environment variables:

```python
# config/settings.py
LLM_PROVIDER = config('LLM_PROVIDER', default='openai')  # openai, anthropic, gemini
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
```

### Security Measures

1. **API Key Management**
   - Keys stored in environment variables
   - Never committed to version control
   - Validated during setup

2. **Data Sanitization**
   - JSON parsing with error handling
   - Input validation before LLM processing
   - Response validation before storage

3. **Rate Limiting**
   - Built-in retry mechanism with exponential backoff
   - Configurable maximum retries

```python
# utils/llm_client.py
class LLMClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"
    
    def evaluate_applicant(self, applicant: dict) -> dict:
        for attempt in range(3):  # Retry mechanism
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[...],
                    temperature=0.2  # Low temperature for consistent results
                )
                # Validate and parse response
                return self._parse_response(response)
            except Exception as e:
                if attempt == 2:  # Final attempt
                    return fallback_response()
```

### Customization

**Prompt Engineering:**
Modify the evaluation prompt in `utils/llm_client.py` to change how applicants are evaluated:

```python
PROMPT_TEMPLATE = """
You are a recruiter AI. Evaluate this applicant based on:
- Relevant experience in tier 1 companies
- Technical skills alignment with our needs
- Compensation expectations
- Availability and location

Provide:
- summary: 2-3 sentence professional summary
- score: 0-100 based on fit for contractor roles
- follow_ups: 3-5 specific follow-up questions

Applicant data: {applicant_data}
"""
```

## Customizing Shortlist Criteria

### Configuration Options

Edit the `.env` file to modify shortlisting criteria:

```bash
# Tier 1 companies for experience evaluation
TIER_1_COMPANIES=Google,Meta,OpenAI,Microsoft,Apple,Amazon,Netflix

# Eligible locations for contractors
ELIGIBLE_LOCATIONS=US,USA,United States,Canada,UK,United Kingdom,Germany,India

# Maximum acceptable hourly rate (USD)
MAX_HOURLY_RATE=100

# Minimum required availability (hours/week)
MIN_AVAILABILITY=20

# Minimum years of experience
MIN_EXPERIENCE=4
```

### Advanced Customization

For more complex criteria, modify the shortlisting logic in `scripts/shortlist_candidates.py`:

```python
def custom_evaluation(compressed_json: Dict) -> bool:
    """Example custom evaluation function"""
    experience = compressed_json['experience']
    salary = compressed_json['salary']
    
    # Custom logic: Require at least 2 tier 1 company experiences
    tier1_experience = sum(1 for exp in experience 
                          if exp['company'] in settings.TIER_1_COMPANIES)
    
    # Custom logic: Prefer candidates with specific technologies
    has_preferred_tech = any('Python' in exp.get('technologies', []) 
                            for exp in experience)
    
    return (tier1_experience >= 2 and 
            has_preferred_tech and
            salary['preferred_rate'] <= settings.MAX_HOURLY_RATE and
            salary['availability'] >= settings.MIN_AVAILABILITY)
```

### Adding New Criteria

1. **Update environment variables** in `.env`:
   ```bash
   NEW_CRITERION=value
   ```

2. **Modify settings.py** to include the new criterion:
   ```python
   NEW_CRITERION = config('NEW_CRITERION', default='default_value')
   ```

3. **Update shortlisting logic**:
   ```python
   def enhanced_evaluation(compressed_json: Dict) -> bool:
       meets_basic = basic_evaluation(compressed_json)  # Existing logic
       meets_new = compressed_json.get('new_field') == settings.NEW_CRITERION
       return meets_basic and meets_new
   ```

## Maintenance and Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify API keys in `.env`
   - Check network connectivity
   - Verify Airtable base permissions

2. **JSON Parsing Errors**
   - Run compression script to regenerate JSON
   - Check for data consistency across tables

3. **LLM Evaluation Failures**
   - Verify LLM API key and quota
   - Check prompt formatting

### Monitoring

Enable debug mode for detailed logging:
```bash
DEBUG=True
```

View logs for specific operations:
```bash
make evaluate  # View LLM evaluation logs
make shortlist  # View shortlisting logs
```

## Extension Points

### Adding New Tables

1. Create the table in Airtable
2. Add table ID to `config/settings.py`
3. Create corresponding data class in `models/__init__.py`
4. Update compression/decompression scripts
5. Modify LLM evaluation prompt if needed

### Custom Processing Hooks

Add custom processing by extending the main scripts:

```python
# scripts/custom_processing.py
def custom_post_processing(applicant_id: str):
    """Example custom processing after LLM evaluation"""
    client = AirtableClient()
    applicant_data = client.get_applicant_data(applicant_id)
    
    # Custom logic here
    if custom_condition(applicant_data):
        client.update_record(settings.APPLICANTS_TABLE, applicant_id, {
            'Custom Flag': 'Special Condition Met'
        })
```

## Best Practices

1. **Data Consistency**
   - Always use the compression/decompression scripts for data migration
   - Regularly validate JSON integrity

2. **Performance**
   - Process applicants in batches for large datasets
   - Use filtering to avoid reprocessing unchanged records

3. **Security**
   - Regularly rotate API keys
   - Monitor LLM usage and costs
   - Validate all inputs before processing

This documentation provides a comprehensive guide to setting up, using, and extending the Airtable Contractor System. The modular design allows for easy customization while maintaining data integrity and automation efficiency.
```