import logging
import time
from collections import Counter

from flask import Flask, jsonify, request
from flask import request, redirect

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

    @app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>MarketPulse</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: #f9f9f9; 
                padding: 40px; 
                text-align: center;
            }
            h1 { color: #333; }
            .btn {
                display: inline-block;
                padding: 12px 22px;
                margin: 10px;
                font-size: 18px;
                background-color: #0066ff;
                color: white;
                border-radius: 6px;
                text-decoration: none;
            }
            .btn:hover { background-color: #004acc; }
            .search-box { 
                margin-top: 30px; 
            }
            input {
                padding: 10px;
                font-size: 18px;
                width: 250px;
            }
            button {
                padding: 10px 18px;
                font-size: 18px;
                margin-left: 8px;
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
            }
            button:hover {
                background-color: #1e7c34;
            }
        </style>
    </head>

    <body>

        <h1>📈 Welcome to MarketPulse</h1>
        <p>Your S&P 500 API, deployed on Render.</p>

        <div>
            <a class="btn" href="/companies">View All Companies</a>
            <a class="btn" href="/sectors">View Sectors</a>
            <a class="btn" href="/index">S&P 500 Index</a>
        </div>

        <div class="search-box">
            <h3>Search for a Company</h3>
            <form action="/go" method="post">
                <input type="text" name="symbol" placeholder="Enter stock ticker (e.g., AAPL)" required />
                <button type="submit">Go</button>
            </form>
        </div>

    </body>
    </html>
    """
    
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

    @app.route("/go", methods=["POST"])
    def go():
        symbol = request.form.get("symbol", "").upper().strip()
        if symbol == "":
            return redirect("/")
        return redirect(f"/company/{symbol}")

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
