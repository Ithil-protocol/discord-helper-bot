# Discord Helper Bot
A helper bot to manage recurrent tasks on Ithil Discord server

### Description
*Fund an account*
Run `$fund 0xabc...` and get 0.1 gETH (Goerli test ETH), once per user

*Get a resource link*
Run `$resource docs` (or *blog*, *app*) to get the latest link to the resource

### Requirements

- Poetry: Python package and version management. Install from [here](https://python-poetry.org/docs/#installation).
- Python 3.8: install from [here](https://www.python.org/downloads/).

### How to run it
In *poetry.toml*:

```bash
[tool.poetry.scripts]
discord_bot = "discord_bot.main:run_app"
```

enables us to run the code as:
```bash
poetry run discord_bot
```

### Run the bot locally

You can run the bot locally. First make sure to add your API keys in the `config.ini` file.

When you are ready just run

```bash
make start
```

### Manual Google Cloud Run image upload

You can manually push a new container image to Google Container Repository using local scripts.

0. Install [Docker](https://www.docker.com/)

1. Install [Google Cloud CLI](https://cloud.google.com/sdk/docs/install).

2. Configure your local credentials with

```bash
gcloud auth login
gcloud auth configure-docker
```

3. Build a container image locally with

```bash
make build-docker-image
```

4. Push the image to Google Cloud Repository with

```bash
make push-image-to-container-registry
```

### Manual Google Cloud Run deployment

You can manage deployments from [here](https://console.cloud.google.com/home/dashboard?project=discord-bot&authuser=1&supportedpurview=project)

### Monitoring

You can get a simple status on the discord bot [here](...).

Alternatively you can get an interactive update on your terminal with

```bash
watch -n 3 curl -s ...
```