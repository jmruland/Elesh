from flask import Blueprint, jsonify, current_app
from utils.index_utils import load_or_create_index
from utils.logger import logger

reload_bp = Blueprint("reload", __name__)

@reload_bp.route("/reload", methods=["POST"])
def reload():
    try:
        logger.info("Manual reload of index triggered via API.")
        # (Re)load the persistent vector index (and thus lore/rules split)
        index = load_or_create_index()
        current_app.config["INDEX"] = index

        # Count entries post-reload
        lore_dir = "./lore/lore"
        rules_dir = "./lore/rules"
        lore_count = len([f for f in os.listdir(lore_dir) if f.endswith(('.md', '.txt'))]) if os.path.isdir(lore_dir) else 0
        rules_count = len([f for f in os.listdir(rules_dir) if f.endswith(('.md', '.txt'))]) if os.path.isdir(rules_dir) else 0

        response = {
            "status": "reloaded",
            "lore_count": lore_count,
            "rules_count": rules_count,
            "message": "Index rebuilt and active."
        }
        logger.info(f"Index reloaded. Lore: {lore_count} files, Rules: {rules_count} files.")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error reloading index: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500