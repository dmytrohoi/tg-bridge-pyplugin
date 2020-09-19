# tg-bridge-pyplugin
[![GitHub](https://img.shields.io/github/license/dmytrohoi/tg-bridge-pyplugin)](https://github.com/dmytrohoi/tg-bridge-pyplugin/blob/master/LICENSE)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/dmytrohoi/tg-bridge-pyplugin)](https://github.com/dmytrohoi/tg-bridge-pyplugin/releases)
[![GitHub Release Date](https://img.shields.io/github/release-date/dmytrohoi/tg-bridge-pyplugin)](https://github.com/dmytrohoi/tg-bridge-pyplugin/releases)
[![GitHub All Releases](https://img.shields.io/github/downloads/dmytrohoi/tg-bridge-pyplugin/total)](https://github.com/dmytrohoi/tg-bridge-pyplugin/releases)
[![Required](https://img.shields.io/badge/required-PyPlugins-blue)](https://github.com/pyplugins/pyplugins)
[![Spigot](https://img.shields.io/badge/spigot-1.15.2-orange)](https://www.spigotmc.org/resources/telegrambridge.83743/)
[![Spiget Downloads](https://img.shields.io/spiget/downloads/83743)](https://www.spigotmc.org/resources/telegrambridge.83743/)
[![Spiget Stars](https://img.shields.io/spiget/rating/83743)](https://www.spigotmc.org/resources/telegrambridge.83743/)
[![Spiget tested server versions](https://img.shields.io/spiget/tested-versions/83743)](https://www.spigotmc.org/resources/telegrambridge.83743/)
[![bStats Players](https://img.shields.io/bstats/players/8809)](https://www.spigotmc.org/resources/telegrambridge.83743/)
[![bStats Servers](https://img.shields.io/bstats/servers/8809)](https://www.spigotmc.org/resources/telegrambridge.83743/)



## About

Minecraft Spigot plugin on [@pyplugins](https://github.com/pyplugins/pyplugins) interpreter to connect Telegram Bot with Server chat.

This plugin provides messaging between Telegram Chat (through Telegram Bot) and Minecraft Chat.

## Installation

Install [@pyplugins](https://github.com/pyplugins/pyplugins) first (_**required!**_).

[Download latest release](https://github.com/dmytrohoi/tg-bridge-pyplugin/releases) and copy file to `server/plugins/` directory.

Run server.

## Configuration

You can configure the plugin in `/plugins/TelegramBridge/config.yml` file.

## FAQ

### Q: How it's works?

The plugin sends messages using the Telegram Bot API. You just need to set the Telegram Bot Token in config.yml.

To make bridge from Telegram to Minecraft just add RCON connection and command `tg-response <text>` request to your implemented Telegram Bot.


## Donation

If you like it, please use the Sponsor button at the top of this page on GitHub.
Or [liberapay.com](https://liberapay.com/dmytrohoi) / [monobank.ua](https://donate.dmytrohoi.com/).

![Statistics](https://bstats.org/signatures/bukkit/TelegramBridge.svg)
