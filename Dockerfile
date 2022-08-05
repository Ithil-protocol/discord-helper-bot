FROM python:3.8

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the container as a non-root user
RUN groupadd -r discord_bot && useradd --no-log-init -r -g discord_bot discord_bot
USER discord_bot:discord_bot

# Run app
ENTRYPOINT ["python"]
CMD ["-m", "discord_bot", "config.ini"]
