from cnrclient.commands.cli import get_parser, all_commands


# Real-test are in test_integration
def test_get_parser():
    parser = get_parser(all_commands())
    assert parser is not None
