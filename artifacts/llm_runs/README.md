# LLM Run Evidence

Running:

```bash
python -m scripts.llm_demo
```

creates a timestamped JSON file in this directory. The record contains the
prompt, generated response, model configuration, and token usage metadata.

Before committing a run record to GitHub, review it and make sure the prompt
and response contain no sensitive or private information. The API key is never
written to these files.
