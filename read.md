Below are all 34 local prompt files—17 system prompts and 17 user prompts—using Jinja2 syntax so that literal JSON schemas survive intact. Place them under:

swift
Copy
Edit
app/prompts/local/validate_pdbe_prompts/
1. alignment_case_subject_system_prompt.txt
csharp
Copy
Edit
You are an AI agent validating the “Case Subject” alignment with the PDBE context.  
Return strictly valid JSON with these keys:  
{% raw %}
{
  "original_text": string,              # the snippet about who reported the issue
  "validation": "aligned"|"not aligned",# alignment result
  "llm_response": string,               # your extracted case subject
  "llm_comment": string                 # notes on missing/incorrect details
}
{% endraw %}
2. alignment_case_subject_user_prompt.txt
javascript
Copy
Edit
Validate the “Case Subject” in the following PDBE text:
{{ pdbe_text }}

Extract who reported the issue and their role, then output JSON as per the system prompt.
3. alignment_case_description_system_prompt.txt
csharp
Copy
Edit
You are an AI agent validating the “Case Description” alignment with the PDBE context.  
Return strictly valid JSON with these keys:  
{% raw %}
{
  "original_text": string,              # the snippet describing the problem
  "validation": "aligned"|"not aligned",# alignment result
  "llm_response": string,               # your extracted case description
  "llm_comment": string                 # notes on missing/incorrect details
}
{% endraw %}
4. alignment_case_description_user_prompt.txt
javascript
Copy
Edit
Validate the “Case Description” in the following PDBE text:
{{ pdbe_text }}

Extract the problem description snippet and align it, then output JSON as per the system prompt.
5. question_1_system_prompt.txt
typescript
Copy
Edit
You are an AI agent validating “Validation Guideline 1: Customer Function/Role.”  
Return strictly valid JSON with:  
{% raw %}
{
  "validation": {
    "status": "ok"|"not ok",
    "criticality": "critical"|"non-critical"
  },
  "aspect_validation": {
    "Reporter Role": {
      "status": "covered"|"not covered",
      "llm_comment": string
    },
    "Reporter Function": {
      "status": "covered"|"not covered",
      "llm_comment": string
    }
  }
}
{% endraw %}
6. question_1_user_prompt.txt
javascript
Copy
Edit
Within this PDBE text:
{{ pdbe_text }}

Check whether the “Customer Function/Role” aspects (reporter role and function) are covered.  
Return JSON matching the system prompt.
7. question_2_system_prompt.txt
ruby
Copy
Edit
You are an AI agent validating “Validation Guideline 2: Device Usage Context.”  
Return strictly valid JSON with:  
{% raw %}
{
  "validation": "covered"|"partially covered"|"not covered",
  "aspect_validation": {
    "Device Usage Context": { "status":"covered"|"not covered","llm_comment":string },
    "Clinical Use Status": { "status":"covered"|"not covered","llm_comment":string },
    "Procedure/Protocol Details": { "status":"covered"|"not covered","llm_comment":string },
    "User Activity During Issue": { "status":"covered"|"not covered","llm_comment":string },
    "Issue Time/Frequency": { "status":"covered"|"not covered","llm_comment":string },
    "Accessories Used": { "status":"covered"|"not covered","llm_comment":string }
  }
}
{% endraw %}
8. question_2_user_prompt.txt
css
Copy
Edit
Validate Device Usage Context (clinical use, procedure details, user activity, time/frequency, accessories) in:
{{ pdbe_text }}

Return JSON as per the system prompt.
9. question_3_system_prompt.txt
ruby
Copy
Edit
You are an AI agent validating “Validation Guideline 3: Expected vs Actual Behavior.”  
Return strictly valid JSON with:  
{% raw %}
{
  "validation": "covered"|"partially covered"|"not covered",
  "aspect_validation": {
    "Procedure/Protocol Deviation": { "status":"covered"|"not covered","llm_comment":string },
    "Observed Discrepancy":      { "status":"covered"|"not covered","llm_comment":string },
    "Customer Expectation":      { "status":"covered"|"not covered","llm_comment":string }
  }
}
{% endraw %}
10. question_3_user_prompt.txt
cpp
Copy
Edit
Validate Expected vs Actual Behavior (procedure deviation, observed discrepancy, customer expectation) in:
{{ pdbe_text }}

Return JSON as per the system prompt.
11. question_4_system_prompt.txt
ruby
Copy
Edit
You are an AI agent validating “Validation Guideline 4: User Impact.”  
Return strictly valid JSON with:  
{% raw %}
{
  "validation": "covered"|"partially covered"|"not covered",
  "aspect_validation": {
    "User Impact Description":       { "status":"covered"|"not covered","llm_comment":string },
    "User Ability to Use Device":    { "status":"covered"|"not covered","llm_comment":string },
    "No-Impact Explanation (if any)":{ "status":"covered"|"not covered","llm_comment":string }
  }
}
{% endraw %}
12. question_4_user_prompt.txt
perl
Copy
Edit
Validate User Impact (impact description, ability to use device, explanation for no impact) in:
{{ pdbe_text }}

Return JSON as per the system prompt.
13. question_5_system_prompt.txt
ruby
Copy
Edit
You are an AI agent validating “Validation Guideline 5: Patient Impact.”  
Return strictly valid JSON with:  
{% raw %}
{
  "validation": "covered"|"partially covered"|"not covered",
  "aspect_validation": {
    "Procedure Continuation":      { "status":"covered"|"not covered","llm_comment":string },
    "Procedure Repetition":         { "status":"covered"|"not covered","llm_comment":string },
    "Radiation Exposure/Flag":      { "status":"covered"|"not covered","llm_comment":string },
    "No Patient Involvement":       { "status":"covered"|"not covered","llm_comment":string },
    "Missing/Unknown Info":         { "status":"covered"|"not covered","llm_comment":string }
  }
}
{% endraw %}
14. question_5_user_prompt.txt
nginx
Copy
Edit
Validate Patient Impact (continuation, repetition, radiation exposure, no involvement, missing info) in:
{{ pdbe_text }}

Return JSON as per the system prompt.
15. question_6_system_prompt.txt
csharp
Copy
Edit
You are an AI agent validating “Validation Guideline 6: Software Version.”  
Return strictly valid JSON with:  
{% raw %}
{
  "validation": "covered"|"partially covered"|"not covered",
  "aspect_validation": {
    "Software Version": { "status":"covered"|"not covered","llm_comment":string },
    "Component Impacted":{ "status":"covered"|"not covered","llm_comment":string }
  }
}
{% endraw %}
16. question_6_user_prompt.txt
cpp
Copy
Edit
Validate Software Version (version and component) in:
{{ pdbe_text }}

Return JSON as per the system prompt.
17. psa_flag_check_system_prompt.txt
php
Copy
Edit
You are an AI agent checking for a “PSA Flag” mention in the PDBE.  
Return strictly valid JSON with:  
{% raw %}
{
  "psa_flag_validation": boolean,
  "psa_flag_description": string  # if flagged, describe how it's mentioned
}
{% endraw %}
18. psa_flag_check_user_prompt.txt
mathematica
Copy
Edit
Check if the PDBE text mentions that the device is PSA-enabled.  
Text:
{{ pdbe_text }}

Return JSON as per the system prompt.
19. attachments_check_system_prompt.txt
arduino
Copy
Edit
You are an AI agent checking for any “Attachment” mention in the PDBE text.  
Return strictly valid JSON with:  
{% raw %}
{
  "attachment": boolean,
  "attachment_description": string  # if true, snippet showing attachment
}
{% endraw %}
20. attachments_check_user_prompt.txt
scss
Copy
Edit
Check if the PDBE text contains any reference to “attachment” (e.g. files, images).  
Text:
{{ pdbe_text }}

Return JSON as per the system prompt.
21. clinical_check_system_prompt.txt
php
Copy
Edit
You are an AI agent checking whether the PDBE describes a clinical use.  
Return strictly valid JSON with:  
{% raw %}
{
  "clinical": boolean,
  "clinical_details": string  # if true, how clinical use is described
}
{% endraw %}
22. clinical_check_user_prompt.txt
mathematica
Copy
Edit
Check if the PDBE text indicates the device was in clinical use.  
Text:
{{ pdbe_text }}

Return JSON as per the system prompt.
23. overall_status_system_prompt.txt
csharp
Copy
Edit
You are an AI agent assigning an overall “status” to this PDBE.  
Return strictly valid JSON with:  
{% raw %}
{
  "status": "complete"|"incomplete"|"needs review"
}
{% endraw %}
24. overall_status_user_prompt.txt
nginx
Copy
Edit
Based on all aspects of the PDBE text:
{{ pdbe_text }}

Decide an overall status ("complete","incomplete","needs review"). Return JSON per the system prompt.
25. overall_summary_system_prompt.txt
csharp
Copy
Edit
You are an AI assistant summarizing the overall PDBE validation.  
Return strictly valid JSON with:  
{% raw %}
{
  "summary": string  # free-text summary of missing/covered aspects
}
{% endraw %}
26. overall_summary_user_prompt.txt
css
Copy
Edit
Provide a free-text summary of the overall PDBE validation, highlighting missing or incomplete fields.
Text:
{{ pdbe_text }}
27. overall_quality_system_prompt.txt
cpp
Copy
Edit
You are an AI agent assessing the overall quality of this PDBE.  
Return strictly valid JSON with:  
{% raw %}
{
  "quality": string  # e.g. "Good", "Poor", "Fair", with reasoning
}
{% endraw %}
28. overall_quality_user_prompt.txt
cpp
Copy
Edit
Assess the overall quality of this PDBE (Good/Poor/Fair) and explain your reasoning.
Text:
{{ pdbe_text }}
29. pdbe_overall_status_system_prompt.txt
matlab
Copy
Edit
You are an AI agent assigning an overall “pdbe_overall_status.”  
Return strictly valid JSON with:  
{% raw %}
{
  "pdbe_overall_status": "passed"|"failed"
}
{% endraw %}
30. pdbe_overall_status_user_prompt.txt
nginx
Copy
Edit
Based on every guideline check above, decide if the PDBE “passed” or “failed” validation.
Text:
{{ pdbe_text }}
31. pdbe_overall_llm_summary_system_prompt.txt
csharp
Copy
Edit
You are an AI assistant summarizing the PDBE validation outcome.  
Return strictly valid JSON with:  
{% raw %}
{
  "pdbe_overall_llm_summary": string
}
{% endraw %}
32. pdbe_overall_llm_summary_user_prompt.txt
css
Copy
Edit
Write a concise, free-text summary of the entire PDBE validation results.
Text:
{{ pdbe_text }}
33. pdbe_overall_quality_system_prompt.txt
cpp
Copy
Edit
You are an AI agent providing an overall “pdbe_overall_quality.”  
Return strictly valid JSON with:  
{% raw %}
{
  "pdbe_overall_quality": string  # e.g. "High", "Medium", "Low"
}
{% endraw %}
34. pdbe_overall_quality_user_prompt.txt
cpp
Copy
Edit
Rate the overall quality of this PDBE validation (High/Medium/Low) and explain.
Text:
{{ pdbe_text }}
Next steps:

Verify each system prompt wraps any literal {…} JSON in {% raw %}…{% endraw %}.

Ensure each user prompt uses {{ pdbe_text }} exactly.

In your PromptTemplate calls, set template_format="jinja2".

With all 34 files in place and Jinja2 configured, your LLM chain will correctly substitute the PDBE text and preserve your JSON‐schema braces.







You said:
You kept pdbe_text which is an input pdbe text with 2 curly braces so will it be recognised as an input and the input will be sent to prompt template or not? 


ChatGPT said:

Thought for a couple of seconds
Yes—it will. Here’s why:

Jinja2 Variable Syntax
In your user prompts you wrote:

jinja
Copy
Edit
{{ pdbe_text }}
That tells Jinja2 “take the variable pdbe_text and inject its value here.” Nothing else in your template is interpreted as a variable.

Raw Blocks for Literal Braces
Every time you needed a literal JSON schema (i.e. actual { ... } in your system prompt), you wrapped it in:

jinja
Copy
Edit
{% raw %}
{
  "key": "value"
}
{% endraw %}
That tells Jinja2 “don’t try to parse these braces—just leave them exactly as is.”

PromptTemplate Configuration
When you create your PromptTemplate with

python
Copy
Edit
PromptTemplate(
    input_variables=["pdbe_text"],
    template=your_combined_template,
    template_format="jinja2"
)



#######################
# app/shared/llm_service.py
import json, asyncio
from typing import Dict, Any
from langchain.chat_models import AzureChatOpenAI
from langchain import PromptTemplate, LLMChain
from loguru import logger
from app.config import settings
from app.shared.llm_service_utils import prompt_loader

class LLMService:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            deployment_name=settings.get_llm_deployment_name(),
            openai_api_key=settings.get_azure_openai_key(),
            openai_api_base=settings.get_azure_openai_endpoint(),
            openai_api_type="azure",
            openai_api_version="2023-05-15",
            temperature=settings.get_llm_temperature(),
            max_tokens=settings.get_llm_max_tokens(),
        )

    async def _run_agent(self, name: str, pdbe_text: str) -> Any:
        prompts = await prompt_loader.load_all_prompts()
        sys_txt = prompts[f"{name}_system_prompt"]
        usr_txt = prompts[f"{name}_user_prompt"]

        # Build a Jinja2‐based PromptTemplate
        template = sys_txt.strip() + "\n\n" + usr_txt.strip()
        prompt = PromptTemplate(
            input_variables=["pdbe_text"],
            template=template,
            template_format="jinja2"
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)

        try:
            raw = await chain.arun(pdbe_text=pdbe_text)
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"error": f"Invalid JSON from {name}: {raw}"}
        except Exception as e:
            logger.error(f"[LLMService] {name} failed: {e}")
            return {"error": str(e)}

    async def validate_pdbe_all(self, pdbe_text: str) -> Dict[str,Any]:
        agents = [
            "alignment_case_subject",
            "alignment_case_description",
            *[f"question_{i}" for i in range(1,7)],
            "psa_flag_check",
            "attachments_check",
            "clinical_check",
            "overall_status",
            "overall_summary",
            "overall_quality",
            "pdbe_overall_status",
            "pdbe_overall_llm_summary",
            "pdbe_overall_quality"
        ]
        tasks = [self._run_agent(n, pdbe_text) for n in agents]
        results = await asyncio.gather(*tasks)

        # merge as before…
        pdbe_id = f"PDBE {pdbe_text[:8]}"
        out = {
            "case_id": {
                pdbe_id: {
                    "case_subject":     results[0],
                    "case_description": results[1],
                    "PDBE": {
                        f"validation_guideline_{i}": results[1+i]
                        for i in range(1,7)
                    },
                    "psa_flag":    results[8],
                    "attachments": results[9],
                    "clinical":    results[10],
                    "overall_llm_summary": results[11],
                    "overall_quality":     results[12],
                    "overall_status":      results[13],
                    "uuid": __import__("uuid").uuid4().hex
                }
            }
        }
        return out

llm_service = LLMService()


