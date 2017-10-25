from __future__ import absolute_import, division, print_function
import yaml
from appr.commands.command_base import CommandBase
from appr.controller.models import DescriptorCr, PackageCr


class GenerateCmd(CommandBase):
    name = 'generate'
    help_message = "Generate a package resource"
    output_default = 'yaml'

    def __init__(self, options):
        super(GenerateCmd, self).__init__(options)
        self.organization = options.organization
        self.media_type = options.media_type
        self.name = options.name
        self.status = {}

    @classmethod
    def _add_arguments(cls, parser):
        sub = parser.add_subparsers()
        descriptor_cmd = sub.add_parser(
            'descriptor', help='Generate a Descriptor resource to be added in a project directory')
        package_cmd = sub.add_parser(
            'package', help='Generate a Package resource to be consumed by kubenretes api')

        cls._add_sub_arguments(descriptor_cmd)
        cls._add_sub_arguments(package_cmd)
        package_cmd.add_argument("--version", required=True, default=None,
                                 help="Set/Update the packageVersion")
        package_cmd.add_argument("--from-descriptor", default=None,
                                 help="initialize values from the descriptor")
        package_cmd.add_argument("--tar-dir", default=None, help="top directory in the tarball")
        content_group = package_cmd.add_mutually_exclusive_group()
        content_group.add_argument("--source-dir", default=None, help="package directory")
        content_group.add_argument("--source-url", default=None, help="package download url")
        descriptor_cmd.set_defaults(func=cls._gen_descriptor)
        package_cmd.set_defaults(func=cls._gen_package)

    @classmethod
    def _add_sub_arguments(cls, parser):
        cls._add_output_option(parser)
        parser.add_argument("name", default=None, help="Set/Update the packageName")
        parser.add_argument("--organization", default=None,
                            help="Set/Update the packageOrganization")
        parser.add_argument("-t", "--media-type", default=None, help="Set/Update the mediaType")

    @classmethod
    def _generate(cls, model, options):
        pass

    @classmethod
    def _gen_package(cls, options, unknown=None):
        cmd = cls(options)
        descriptor = None
        version = options.version
        if options.from_descriptor:
            with open(options.from_descriptor, 'r') as ifile:
                descriptor = yaml.safe_load(ifile.read())
        package = PackageCr(cmd.name, version, cmd.media_type, descriptor=descriptor)
        if cmd.organization:
            package.add_field('packageOrg', cmd.organization)
        if options.source_dir:
            package.add_blob(options.source_dir, options.tar_dir)
        if options.source_url:
            package.add_url(options.source_url)
        if options.output == "file":
            package.write_to_file()
        else:
            cmd.status = package.render()
            cmd.render()

    @classmethod
    def _gen_descriptor(cls, options, unknown=None):
        cmd = cls(options)
        descriptor = DescriptorCr(cmd.name, cmd.media_type)
        if cmd.organization:
            descriptor.add_field('packageOrg', cmd.organization)
        cmd.status = descriptor.render()
        cmd.render()

    def _render_dict(self):
        return self.status

    def _render_console(self):
        return self.status
