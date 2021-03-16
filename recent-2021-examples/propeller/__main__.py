"""Parse commandline arguments."""

from argparse import ArgumentParser

import propeller.app


parser = ArgumentParser()
parser.add_argument(
    "episode",
    help="The episode name to download and publish from.",
)
parser.add_argument(
    "--task",
    default="ingest",
    help="The task to download and publish from. (Default: ingest)",
)
parser.add_argument(
    "--image-extension",
    default="tif",
    help="The image sequence extension. (Default: tif)",
)
parser.add_argument(
    "--audio-extension",
    default="wav",
    help="The audio extension. (Default: wav)",
)
parser.add_argument(
    "--process-single",
    default=False,
    action="store_true",
    help=(
        "Process only the first shot in the episode directory. "
        "(Default: False)"
    )
)
parser.add_argument(
    "--image-quality",
    default=None,
    help="The image sequence compression quality. (Default: None)",
)
parser.add_argument(
    "--families",
    default=["sonar.reference"],
    help='The families to publish to. (Default: ["sonar.reference"])',
)
parser.add_argument(
    "--subset",
    default="reference",
    help='The subset to publish to. (Default: reference)',
)
parser.add_argument(
    "--app",
    default="shell",
    help='The name of a (fake) app to publish from. (Default: shell)',
)
parser.add_argument(
    "--dry-run",
    action="store_true",
    default=False,
    help=(
            "Only show what would be done, but don't actually download, "
            "copy and publish any files. (Default: False)"
    ),
)


kwargs = vars(parser.parse_args())
propeller.app.main(**kwargs)
