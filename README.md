# Docker Update Checker

## Description
This script/container informs about updates of docker containers running on a local system. It fetches Updates of the images your containers use and informs about new tags available.



## Usage

It's thought to be run e.g by a crontab on the local machine:
```
0 3 * * * docker start <your container name>
```
### Messaging

For convenience reasons the default version uses messaging via Telegram by now. It expects you to have created a telegram bot and a chat that the bot can post to. (More info here: https://core.telegram.org/bots ).

Accordingly two environment variables have to be set too: `TELEGRAM_BOT_ID` and `TELEGRAM_CHAT_ID`.

In a next version, you can decide between that and a simple Web hook sending a post request to a custom url of your liking.

### Example

The example uses a container. (First of course build the container.)

```
docker run --name my_docker_updater -v /var/run/docker.sock:/var/run/docker.sock -v /usr/bin/docker:/usr/bin/docker -e TELEGRAM_BOT_ID=< your telegram bot > -e TELEGRAM_CHAT_ID=<your chat> <your image name>
```