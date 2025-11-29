import logging
import time
from collections import Counter

from flask import Flask, jsonify, request

from .db import init_db
from . import queries

metrics = Counter()
START_TIME = time.time()


def create_app() -> Flask:
    # Initialize DB (idempotent)
    init_db()

    app = Flask(__name__)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logger = logging.getLogger(__name__)

    @app.before_request
    def _track_request():
        metrics["requests_total"] += 1
        metrics[f"path_{request.path}"] += 1

    @app.after_request
    def _log_response(response):
        logger.info("%s %s -> %s", request.method, request.path, response.status_code)
        return response

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "uptime_seconds": int(time.time() - START_TIME)})

    @app.get("/companies")
    def companies():
        sector = request.args.get("sector")
        limit = request.args.get("limit", default=50, type=int)
        df = queries.get_companies(limit=limit, sector=sector)
        return jsonify(df.to_dict(orient="records"))

    @app.get("/company/<symbol>")
    def company(symbol: str):
        df = queries.get_company(symbol.upper())
        if df.empty:
            return jsonify({"error": "Symbol not found"}), 404
        return jsonify(df.to_dict(orient="records")[0])

    @app.get("/sectors")
    def sectors():
        df = queries.get_sectors()
        return jsonify(df["Sector"].tolist())

    @app.get("/sector/<sector>/companies")
    def sector_companies(sector: str):
        df = queries.get_sector_companies_with_stats(sector)
        if df.empty:
            return jsonify({"error": "Sector not found"}), 404
        return jsonify(df.to_dict(orient="records"))

    @app.get("/index")
    def index_history():
        limit = request.args.get("limit", default=100, type=int)
        df = queries.get_index_history(limit=limit)
        return jsonify(df.to_dict(orient="records"))

    @app.get("/metrics")
    def metrics_endpoint():
        """
        Simple Prometheus-style metrics text output.
        """
        lines = [
            f"marketpulse_uptime_seconds {int(time.time() - START_TIME)}",
        ]
        for key, value in metrics.items():
            metric_name = key.replace("/", "_").replace("-", "_")
            lines.append(f"marketpulse_{metric_name} {value}")
        text_body = "\n".join(lines) + "\n"
        return text_body, 200, {"Content-Type": "text/plain; version=0.0.4"}

    return app


# For gunicorn
app = create_app()

# For `python src/app.py` local dev
if __name__ == "__main__":
    app.run(debug=True)
