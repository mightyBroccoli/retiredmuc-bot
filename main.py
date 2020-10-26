#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

from slixmpp import ClientXMPP

from config import Config


class RetiredMucBot(ClientXMPP):
    def __init__(self, jid, password, nick, config):
        ClientXMPP.__init__(self, jid, password)
        self.use_message_ids = True
        self.use_ssl = True

        # passthrough the config obj
        self.config = config

        self.rooms = None
        self.nick = nick
        self.messages = self.config.get("messages")

        # feature config
        self.functions = self.config.get("features")

        # session start disconnect events
        self.add_event_handler("session_start", self.start_session)
        self.add_event_handler("disconnected", self.reconnect_session)

        # register receive handler for both groupchat and normal message events
        self.add_event_handler("message", self.message)

    def reconnect_session(self, event):
        """
        method to handle disconnects / session drops
        """
        self.connect()

    def start_session(self, event):
        """
        session start
        """
        self.send_presence()
        self.join_rooms()

    def join_rooms(self):
        """
        method to join configured rooms and register their response handlers
        """
        self.rooms = self.config.get("rooms")

        if self.rooms is not None:
            for room in self.rooms:
                self.add_event_handler(f"muc::{room}::got_online", self.notify_user)
                self.plugin["xep_0045"].join_muc(room, self.nick, wait=True)

    def message(self, msg):
        """
        method to handle incoming chat, normal messages
        :param msg: incoming msg object
        """

        # do not process our own messages
        ourself = self.plugin["xep_0045"].get_our_jid_in_room(msg.get_mucroom())
        if msg["from"] == ourself:
            return

        # ever other messages will be answered statically
        if msg["type"] in ("normal", "chat"):
            self.send_message(
                mto=msg["from"],
                mbody=self.messages["direct_msg"].format(nick=self.nick),
                mtype=msg["type"],
            )

    def notify_user(self, presence):
        """
        method to compose the redirect action
        :param presence: incoming user presence object
        """
        user_nick = presence["muc"]["nick"]

        # catch empty user_nicks slixmpp does that for some reason
        if user_nick == "":
            return

        # handle all incoming user presences, this may cause duplicates
        if user_nick != self.nick:
            new_room = self.rooms[presence.get_from().bare]
            self.send_message(
                mto=presence.get_from().bare,
                mbody=self.messages["grp_msg"].format(user_nick=user_nick, new_room=new_room),
                mtype="groupchat",
            )

            if self.functions["direct_invite"]:
                jid = presence["muc"].get_jid().bare
                self.invite_user(jid, new_room)

    def invite_user(self, jid, room):
        """
        method to invite the user to the new room
        :param jid: jid to invite
        :param room: room to which the jid should be invited
        """
        self.plugin["xep_0045"].invite(
            room=jid,
            jid=room,
            reason="redirection due to retirement",
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # init config obj
    config = Config()

    # config
    login = config.get("login", default=None)

    # init the bot and register used slixmpp plugins
    xmpp = RetiredMucBot(login["jid"], login["password"], login["nick"], config)
    xmpp.register_plugin("xep_0030")  # Service Discovery
    xmpp.register_plugin("xep_0045")  # Multi-User Chat
    xmpp.register_plugin("xep_0085")  # Chat State Notifications
    xmpp.register_plugin("xep_0092")  # Software Version
    xmpp.register_plugin("xep_0199")  # XMPP Ping
    xmpp.register_plugin("xep_0249")  # Direct MUC Invite

    # connect and start receiving stanzas
    xmpp.connect()
    xmpp.process()
