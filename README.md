# llm-documentation-modifier
LLM-based modification for a documentation in a code repository/file. 

### Quick Start
Step 1: start an instance of the MLflow AI Gateway - [tutorial](https://mlflow.org/docs/latest/gateway/index.html#step-4-start-the-gateway-service)
* This step must be done in a isolated terminal tab/window.

```
mlflow gateway start --config-path ./gateway/config.yaml
```

Step 2: Run the CLI

```
python cli.py --read-file-path=/path/to/file --overwrite=true --gateway-route-name=chat-gpt-4
```
