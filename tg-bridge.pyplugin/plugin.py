
# /local/bin/python
# -*- coding: utf-8 -*-
"""
Plugin: TelegramBridge (https://github.com/dmytrohoi/tg-bridge-pyplugin)
File: plugin.py
Version: 0.0.2
Author: hedgehoi (Dmytro Hoi)
License: MIT License

Dependencies:
    - PyPlugins v0.0.1 / https://github.com/pyplugins/pyplugins

"""
import urllib


class TelegramChatCommands(PythonCommandExecutor):
    commands = [
        PyCommand('telegram', 'telegramCommand', 'telegramOnTabComplete'),
        PyCommand('telegram-chat-response', 'responseCommand', 'telegramOnTabComplete')
    ]

    def telegramCommand(self, sender, command, label, args):
        sender_name = sender.getName()
        message_text = " ".join(args)
        if not message_text:
            sender.sendMessage(
                self.plugin.placeholder
                + " Please add text to command, for example: /telegram Test"
            )
            return True

        self.plugin.logger.info('{sender} try to send message to Telegram: {message}'.format(
            sender=sender_name,
            message=message_text
        ))

        template = self.plugin.config.getString(
            'outcoming_msg_template',
            "{message_text}"
        )

        # Encode "&", "<" and ">" in message_text
        text = template.format(
            username=sender_name,
            message_text=message_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )

        result = self.plugin.sendTelegramMessage(text)

        if result:
            sender.sendMessage(
                self.plugin.placeholder
                + " Message sent to Telegram Chat."
            )

            bc_message = self.plugin.config.getString(
                'outcoming_msg_broadcast_template',
                "[ Telegram Chat << ] <{username}> {message_text}"
            ).format(
                username=sender_name,
                message_text=message_text
            )

            Bukkit.getServer().broadcastMessage(bc_message)
        else:
            sender.sendMessage(
                self.plugin.placeholder
                + " Message not sent, please call to Server Admins."
            )

        return True

    def responseCommand(self, sender, command, label, args):
        message_text = " ".join(args)
        if not sender.isOp():
            sender.sendMessage(self.plugin.placeholder + " Command only for console usage")
            return True

        if not message_text:
            sender.sendMessage(
                self.plugin.placeholder + " Please add text to command, for example: "
                "/telegram-chat-response Test"
            )
            return True

        self.plugin.logger.info(
            'Console command sent message from Telegram: {message}'.format(
                message=message_text
            )
        )

        bc_message = self.plugin.config.getString(
            "incoming_msg_template",
            "[ Telegram Chat >> ] {message_text}"
        ).format(message_text=message_text)

        Bukkit.getServer().broadcastMessage(bc_message)
        sender.sendMessage(self.plugin.placeholder + " Message sent to Minecraft Chat.")
        return True

    def telegramOnTabComplete(self, sender, command, alias, args):
        if len(args) == 1:
            return ['<text for message>']
        else:
            return []


class TelegramBridgePlugin(PythonPlugin):

    def onEnable(self):
        # Plugin custom placeholder
        self.placeholder = u'[ \u00A75tg-bridge\u00A7r ]'
        # Add commands
        self.apply_command_executor(TelegramChatCommands)

        # Add bStats metrics
        self.add_bstats(8809)
        self.add_configuration(
            available_options=[
                "outcoming_msg_template",
                "outcoming_msg_broadcast_template",
                "incoming_msg_template"
            ]
        )
        self.logger.info("plugin enabled!")

        bot_token = self.config.getString('TOKEN')

        if not bot_token:
            self.logger.warning(
                "Plugin is not configured, please set TOKEN in config.yml"
            )

        chat_id = self.config.getString('CHAT_ID')
        if not chat_id:
            self.logger.warning(
                "Plugin is not configured, please set CHAT_ID in config.yml"
            )
        # Startup notification
        self.notification("startup_notification")

    def onDisable(self):
        # Shutdown notification
        self.notification("shutdown_notification")

        self.logger.info("plugin disabled!")

    def notification(self, name):
        section = self.config.get(name)
        if not section or (section and not section.getBoolean('enable')):
            self.logger.info("{} skipped".format(name))
            return

        self.logger.info("{} option is enabled!".format(name))

        template = section.getString(
            "template",
            "Server {ip} " + "started!" if "start" in name else "stopped!"
        )

        server = Bukkit.getServer()

        # Lazy load placeholders
        serverIp = "{}:{}".format(server.getIp(), server.getPort()) if "{ip}" in template else ""
        serverMOTD = server.getMotd() if "{motd}" in template else ""

        text = template.format(
            ip=serverIp,
            motd=serverMOTD
        )
        self.sendTelegramMessage(text)

    def sendTelegramMessage(self, text):

        chat_id = self.config.getString('CHAT_ID')
        bot_token = self.config.getString('TOKEN')

        if not chat_id or not bot_token:
            self.logger.warning(
                "Plugin is not configured, please set CHAT_ID and TOKEN in "
                "config.yml"
            )
            return False

        # Make data query for url
        data_options = {
            'text': text,
            'chat_id': chat_id,
            'parse_mode': 'HTML'
        }

        # Replace "<br/>" to new line char
        data = urllib.urlencode(data_options).replace("%3Cbr%2F%3E", "%0A")
        telegramRequestURL = "https://api.telegram.org/bot{bot_token}/sendMessage?{data}".format(
            bot_token=bot_token,
            data=data
        )

        # Send message to Telegram
        raw_response = urllib.urlopen(telegramRequestURL)
        response = raw_response.read().decode('utf-8')

        result = '"ok":true' in response

        if result:
            self.logger.info(
                'Message sent to Telegram: {text}'.format(
                    text=text
                )
            )
        else:
            self.logger.warning(
                'Message not sent to Telegram: '
                'url="{url}" message="{text}" response="{response}"'.format(
                    url=telegramRequestURL,
                    text=text,
                    response=response
                )
            )

        return result
