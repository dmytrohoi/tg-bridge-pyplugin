
# /local/bin/python
# -*- coding: utf-8 -*-
"""
Plugin: TelegramBridge (https://github.com/dmytrohoi/tg-bridge-pyplugin)
File: plugin.py
Version: 0.1.0
Author: hedgehoi (Dmytro Hoi)
License: MIT License

Dependencies:
    - PyPlugins  >0.0.1 / https://github.com/pyplugins/pyplugins

"""
import urllib
import json
import re


class TelegramChatCommands(PythonCommandExecutor):
    commands = [
        PyCommand('telegram', 'telegramCommand', 'telegramOnTabComplete'),
        PyCommand('telegram-chat-response', 'responseCommand', 'telegramOnTabComplete'),
        PyCommand('link', 'linkCommand', 'linkOnTabComplete')
    ]

    def telegramCommand(self, sender, command, label, args):

        sender_name = sender.getName()
        message_text = " ".join(args)
        self.plugin.logger.info('{sender} try to send message to Telegram: {message}'.format(
            sender=sender_name,
            message=message_text
        ))

        bridge_section = self.plugin.config.get("bridge")
        if not bridge_section \
           or not bridge_section.getBoolean("enable") \
           or not bridge_section.getString("chat_id"):
            sender.sendMessage(
                self.plugin.placeholder
                + " Bridge disabled."
            )
            self.plugin.logger.info('Bridge disabled.')
            return True

        if not message_text:
            sender.sendMessage(
                self.plugin.placeholder
                + " Please add text to command, for example: /telegram Test"
            )
            return True

        template = bridge_section.getString(
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

            bc_message = bridge_section.getString(
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

        bridge_section = self.plugin.config.get("bridge")
        if not bridge_section or not bridge_section.getBoolean("enable"):
            self.plugin.logger.info('Bridge not enabled.')
            return True

        bc_message = bridge_section.getString(
            "incoming_msg_template",
            "[ Telegram Chat >> ] {message_text}"
        ).format(message_text=message_text)

        Bukkit.getServer().broadcastMessage(bc_message)
        sender.sendMessage(
            self.plugin.placeholder
            + " Message sent to Minecraft Chat."
        )
        return True

    def telegramOnTabComplete(self, sender, command, alias, args):
        if len(args) == 1:
            return ['<text for message>']
        else:
            return []

    def linkCommand(self, sender, command, label, args):
        section = self.plugin.config.get("linking")
        if not section or not section.getBoolean("enable"):
            sender.sendMessage(self.plugin.placeholder + " Linking disabled.")
            return True

        if sender.getName() == "CONSOLE":
            sender.sendMessage(self.plugin.placeholder + " Command only for player in-game usage")
            return True

        if len(args) > 1:
            sender.sendMessage(
                self.plugin.placeholder + " You sent more than 1 argument with /link command"
            )
            return True
        elif not len(args):
            sender.sendMessage(
                self.plugin.placeholder + " To connect Minecraft account and "\
                "Telegram account please go to Server's Telegram bot and "\
                "perform /link command to get start!"
            )
            return True

        # User code
        code = args[0]

        self.plugin.logger.info(
            '{player} try to link Minecraft account to Telegram user with code: {code}'.format(
                player=sender.getName(),
                code=code
            )
        )

        text = section.getString(
            "message_text_template",
            "Player with username <b>{username}</b> try to link Minecraft account to this Telegram account"
        ).format(
            username=sender.getName()
        )

        #Validate code
        validation_regex = section.getString("code_validation_regexp")
        if validation_regex and not re.match(r'^' + validation_regex + r'$', code):
            sender.sendMessage(self.plugin.placeholder + " Invalid code, please check code or call Server Admin.")
            return True

        result = self.plugin.sendTelegramMessage(text, button_confirm_code=code)
        if result:
            sender.sendMessage(self.plugin.placeholder + " Please check your Telegram dialog and confirm linking.")
        else:
            sender.sendMessage(self.plugin.placeholder + " Somethink went wrong, please check code or call Server Admin.")
        return True

    def linkOnTabComplete(self, sender, command, alias, args):
        if len(args) == 1:
            return ['<telegram bot code>']
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
        self.add_configuration()
        self.logger.info("plugin enabled!")

        bot_token = self.config.getString('TOKEN')

        if not bot_token:
            self.logger.warning(
                "Plugin is not configured, please set TOKEN in config.yml"
            )

        bridge = self.config.get('bridge')
        if not bridge or not bridge.getString("chat_id"):
            self.logger.warning("Bridge disabled in config.yml")
        else:
            # Startup notification
            self.notification("startup_notification")

    def onDisable(self):
        # Shutdown notification
        bridge = self.config.get('bridge')
        if bridge and bridge.getString("chat_id"):
            self.notification("shutdown_notification")

        self.logger.info("plugin disabled!")

    def notification(self, name):
        section = self.config.get("bridge").get(name)
        if not section or (section and not section.getBoolean('enable')):
            self.logger.info("{} disabled.".format(name.replace("_", " ").capitalize()))
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

    def sendTelegramMessage(self, text, button_confirm_code=None):

        bot_token = self.config.getString('TOKEN')

        if not bot_token:
            self.logger.warning(
                "Plugin is not configured, please set TOKEN in "
                "config.yml"
            )
            return False

        # Make data query for url
        data_options = {
            'text': text,
            'parse_mode': 'HTML'
        }

        # Link command
        if button_confirm_code:
            # Default button text
            confirm_button_text = "Confirm linking"

            # Check config
            linking_section = self.config.get('linking')
            if linking_section and linking_section.getString("button_text"):
                confirm_button_text = linking_section.getString("button_text")

            data_options['reply_markup'] = json.dumps({
                "inline_keyboard": [
                    [{
                        "text": confirm_button_text,
                        "callback_data": "tcp:link:" + button_confirm_code
                    }]
                ]
            })
            user_id = button_confirm_code.split(":")[0] if ":" in button_confirm_code else button_confirm_code
            if user_id.startswith("-"):
                return False

            data_options["chat_id"] = user_id
        else:
            bridge_section = self.config.get('bridge')
            if not bridge_section or not bridge_section.getString('chat_id'):
                self.logger.warning(
                    "Bridge is not configured, please set 'bridge' > 'chat_id' in "
                    "config.yml"
                )
                return False

            data_options["chat_id"] = bridge_section.getString('chat_id')

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
