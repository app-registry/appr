from __future__ import absolute_import, division, print_function
import yaml

from appr.commands.command_base import CommandBase
from appr.controller.models import PackageCr


class GetCmd(CommandBase):
    name = 'get'
    help_message = "Get and list packages"
    parse_unknown = True

    def __init__(self, options, other_opts):
        super(GetCmd, self).__init__(options)
        self.opts = other_opts
        self.filters = {}
        if options.digest:
            self.filters['digest'] = options.digest[0:10]
        if options.package_org:
            self.filters['packageOrg'] = options.packageOrg
        if options.package_name:
            self.filters['packageName'] = options.package_name
        if options.media_type:
            self.filters['mediaType'] = options.media_type
        self.namespace = options.namespace
        self.resource = options.resource
        self.status = {}
        self.result = None

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_output_option(parser)
        filter_group = parser.add_mutually_exclusive_group()

        filter_group.add_argument("--digest", default=None, help="get by digest")
        filter_group.add_argument("resource", nargs='?', default=None,
                                  help="kubernetes resource name")

        parser.add_argument("-n", "--namespace", default="default", help="kubernetes namespace")

        parser.add_argument('--media-type', help="Filter by mediaType", default=None)
        parser.add_argument('--package-org', help="Filter by packageOrg", default=None)
        parser.add_argument('--package-name', help="Filter by packageName", default=None)

    def _call(self):
        self.result = PackageCr.list(name=self.resource, namespace=self.namespace,
                                     filters=self.filters, output=self.output, opts=self.opts)

    def _render_dict(self):
        return self.result

    def _render_console(self):
        return self.result
