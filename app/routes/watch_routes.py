from flask import Blueprint, render_template
from app.models.channel_model import Channel

watch_bp = Blueprint("watch", __name__)

@watch_bp.route("/watch/<int:channel_id>")
def watch_channel(channel_id):
    ch = Channel.query.get(channel_id)

    if not ch:
        return "Channel not found", 404

    return render_template("watch.html", channel=ch)