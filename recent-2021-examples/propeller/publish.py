"""Publish files to avalon."""

import logging
import socket
import sys

import avalon.api
import avalon.io
import avalon.schema

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("propeller")


def to_camel_case(text):
    if not text:
        return None
    parts = text.replace("-", " ").replace("_", " ").split()

    first = parts[0].lower()
    last = "".join(part.capitalize() for part in parts[1:])
    return f"{first}{last}"


def get_subset(
    av_asset,
    subset_name,
    families,
    dry_run=False,
):
    """Get or create a subset."""

    subset = avalon.io.find_one(
        {"type": "subset", "parent": av_asset["_id"], "name": subset_name}
    )

    if subset is None and not dry_run:
        logger.info("Subset '%s' not found, creating...", subset_name)

        subset = {
            "schema": "avalon-core:subset-3.0",
            "type": "subset",
            "name": subset_name,
            "data": {"families": families},
            "parent": av_asset["_id"],
        }

        # Validate schema
        avalon.schema.validate(subset)

        _id = avalon.io.insert_one(subset).inserted_id
        subset["_id"] = _id

    return subset


def create_next_version(
    av_subset,
    families,
    dry_run,
    version_up,
):
    """Create the next version."""

    if av_subset:
        av_subset_id = av_subset["_id"]
    elif dry_run:
        av_subset_id = None
    else:
        logger.error(
            "This is not a 'dry run', but a subset isn't found. That's "
            "an error! Aborting..."
        )
        sys.exit(1)

    latest_version = avalon.io.find_one(
        {"type": "version", "parent": av_subset_id},
        {"name": True},
        sort=[("name", -1)],
    )
    version_name = 1
    if latest_version is not None:
        if version_up:
            version_name += latest_version["name"]
        else:
            version_name = latest_version["name"]

    version = {
        "schema": "avalon-core:version-3.0",
        "type": "version",
        "parent": av_subset_id,
        "name": version_name,
        "locations": [avalon.api.Session["AVALON_LOCATION"]],
        "data": {
            "families": families,
            "time": avalon.api.time(),
            "author": "propeller",
            "comment": "Auto reference 'publish'",
            "machine": socket.gethostname(),
            "fps": None,
            "source": "shotgun",
        },
    }

    avalon.schema.validate(version)

    if not dry_run:
        logger.debug("Creating version...")
        _id = avalon.io.insert_one(version).inserted_id
        version["_id"] = _id

    return version


def create_representation(version, publish_template, publish_data):
    """Create the representation."""

    representation = {
        "schema": "avalon-core:representation-2.0",
        "type": "representation",
        "parent": version["_id"],
        "name": publish_data["representation"],
        "data": {"template": publish_template, "loaded_assets": []},
        "dependencies": [],
        "context": {
            "app": publish_data["app"],
            "asset": publish_data["asset"],
            "hierarchy": publish_data["hierarchy"].replace("\\", "/"),
            "instance": publish_data["subset"],
            "project": publish_data["project"],
            "representation": publish_data["representation"],
            "silo": publish_data["silo"],
            "subset": publish_data["subset"],
            "task": publish_data["task"],
            "version": version["name"],
        },
    }

    avalon.schema.validate(representation)

    _id = avalon.io.insert_one(representation).inserted_id
    representation["_id"] = _id

    return representation


def publish(
    av_project,
    task,
    app,
    families,
    episode,
    sequence,
    shot,
    subset_base,
    representation,
    subset_variant=None,
    dry_run=False,
    version_up=True,
):
    """Publish to avalon (without affecting the filesystem)."""

    if not subset_variant:
        subset_variant = "default"

    subset_name = to_camel_case(f"{subset_base}-{subset_variant}")
    if subset_name is None:
        logger.error(
            "Could not determine the subset_name from: %s - %s",
            subset_base,
            subset_variant,
        )
        return False

    shot_name = f"{episode}_{sequence}_{shot}".format(
        episode=episode,
        sequence=sequence,
        shot=shot,
    )
    try:
        avalon.api.update_current_task(task=task, asset=shot_name, app=app)
    except AssertionError:
        logger.error("Could not find asset: %s", shot_name)
        return False

    # Get publish data
    publish_template = av_project["config"]["template"]["publish"]
    publish_data = {k.split("_")[-1].lower(): v for k, v in avalon.api.Session.items()}
    publish_data["root"] = publish_data["projects"]
    publish_data["representation"] = representation
    publish_data["subset"] = subset_name

    av_asset = avalon.io.find_one(
        {
            "type": "asset",
            "name": shot_name,
            "parent": av_project["_id"],
        }
    )
    if not av_asset:
        logger.error("Could not find asset: %s", shot_name)

    av_subset = get_subset(av_asset, subset_name, families, dry_run=dry_run)
    av_version = create_next_version(
        av_subset, families, dry_run=dry_run, version_up=version_up
    )

    publish_data["version"] = av_version["name"]

    if not dry_run:
        create_representation(av_version, publish_template, publish_data)

    return publish_data
