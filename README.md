# llm-documentation-modifier
LLM-based modification for a documentation in a code repository/file. 

### Quick Start
##### Step 0: Clone this repo and `cd` into it

##### Step 1: Start an instance of the MLflow AI Gateway - [tutorial](https://mlflow.org/docs/latest/gateway/index.html#step-4-start-the-gateway-service)
1. Open a new terminal window and cd into the above directory. This terminal window serves the gateway on local host and must remain open while using the service.
2. Install the mlflow gateway via `pip install 'mlflow[gateway]'`
3. Expose your LLM token via `export OPENAI_API_KEY=XYZ`
4. Start the gateway `mlflow deployments start-server --config-path ./gateway/config.yaml`

##### Step 2: Run the CLI

```
python cli.py --read-file-path=/path/to/file --overwrite=true --gateway-route-name=chat-gpt-4
```
