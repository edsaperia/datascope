from __future__ import unicode_literals, absolute_import, print_function, division

from core.management.commands.grow_community import Command as GrowCommand
from core.utils.configuration import DecodeConfigAction


class Command(GrowCommand):

    def add_arguments(self, parser):
        parser.add_argument('community', type=str, nargs="?", default="FutureFashionCommunity")
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})
        parser.add_argument('-a', '--args', type=str, nargs="*", default="")

    def handle_community(self, community, *args, **options):
        community.signature = "kleding"
        super(Command, self).handle_community(community, *args, **options)
