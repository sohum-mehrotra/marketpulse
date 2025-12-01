import logging
import time
from collections import Counter

from flask import Flask, jsonify, request, redirect
import pandas as pd

from .db import init_db
from . import queries

metrics = Counter()
START_TIME = time.time()


def df_to_html(df: pd.DataFrame, title: str):
    """Convert DataFrame to clean HTML table with styling."""
    table_html = df.to_html(
        classes="data-table",
        index=False,
        border=0,
        justify="center"
    )

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 40px;
                background: #f5f5f5;
                text-align: center;
            }}
            h1 {{
                color: #333;
            }}
            .data-table {{
                margin-left: auto;
                margin-right: auto;
                border-collapse: collapse;
                width: 85%;
                background: white;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
            }}
            .data-table th {{
                background-color: #0066ff;
                color: white;
                padding: 10px;
            }}
            .data-table td {{
                border: 1px solid #ddd;
                padding: 8px;
            }}
            .btn {{
                display: inline-block;
                padding: 10px 20px;
                margin: 10px;
                background: #0066ff;
                color: white;
                border-radius: 6px;
                text-decoration: none;
                font-size: 16px;
            }}
            .btn:hover {{
                background: #0050cc;
            }}
            .back {{
                margin-top: 20px;
                display: inline-block;
                padding: 8px 16px;
                background: #444;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>

    <h1>{title}</h1>

    {table_html}

    <br>
    <a class="back" href="/">← Back Home</a>

    </body>
    </html>
    """


def create_app() -> Flask:
    # DB init
    init_db()

    app = Flask(__name__)

    # Logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    @app.before_request
    def _track_req():
        metrics["requests_total"] += 1
        metrics[f"path_{request.path}"] += 1

    @app.after_request
    def _log_response(resp):
        logger.info("%s %s → %s", request.method, request.path, resp.status_code)
        return resp

    # ----------------------------------------------------------------------
    # HOMEPAGE
    # ----------------------------------------------------------------------
    @app.route("/")
    def home():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MarketPulse</title>
            <style>
                body { font-family: Arial; padding: 40px; text-align: center; background: #f2f2f2; }
                h1 { color: #333; }
                .btn {
                    padding: 14px 24px;
                    margin: 10px;
                    background: #0066ff;
                    color: white;
                    font-size: 20px;
                    border-radius: 8px;
                    text-decoration: none;
                }
                .btn:hover { background: #004acc; }
                input {
                    padding: 12px;
                    font-size: 18px;
                    width: 260px;
                }
                button {
                    padding: 12px 20px;
                    font-size: 18px;
                    background: #28a745;
                    color: white;
                    border-radius: 6px;
                    border: none;
                }
                button:hover { background: #1d7c34; }
            </style>
        </head>
        <body>

        <h1>📈 Welcome to MarketPulse</h1>

        <a class="btn" href="/companies">View All Companies</a>
        <a class="btn" href="/sectors">View Sectors</a>
        <a class="btn" href="/index">S&P 500 Index</a>

        <div style="margin-top: 30px;">
            <h3>Search for a Company</h3>
            <form action="/go" method="post">
                <input name="symbol" placeholder="Enter ticker (ex: AAPL)">
                <button type="submit">Go</button>
            </form>
        </div>

        </body>
        </html>
        """

    @app.route("/go", methods=["POST"])
    def go():
        symbol = request.form.get("symbol", "").upper().strip()
        if symbol == "":
            return redirect("/")
        return redirect(f"/company/{symbol}")

    # ----------------------------------------------------------------------
    # COMPANIES
    # ----------------------------------------------------------------------
    @app.get("/companies")
    def companies():
        if request.args.get("format") == "json":
            df = queries.get_companies(limit=500)
            return jsonify(df.to_dict(orient="records"))

        df = queries.get_companies(limit=500)
        return df_to_html(df, "All S&P 500 Companies")

    # ----------------------------------------------------------------------
    # SINGLE COMPANY
    # ----------------------------------------------------------------------
    @app.get("/company/<symbol>")
    def company(symbol):
        df = queries.get_company(symbol.upper())

        if df.empty:
            return df_to_html(pd.DataFrame([{"error": "Symbol not found"}]), f"{symbol} Not Found")

        return df_to_html(df, f"Company: {symbol.upper()}")

    # ----------------------------------------------------------------------
    # SECTORS
    # ----------------------------------------------------------------------
    @app.get("/sectors")
    def sectors():
        df = queries.get_sectors().rename(columns={"Sector": "S&P 500 Sectors"})
        return df_to_html(df, "S&P 500 Sectors")

    # ----------------------------------------------------------------------
    # COMPANIES IN SECTOR
    # ----------------------------------------------------------------------
    @app.get("/sector/<sector>/companies")
    def sector_companies(sector):
        df = queries.get_sector_companies_with_stats(sector)
        if df.empty:
            return df_to_html(pd.DataFrame([{"error": "Sector not found"}]), f"{sector} Not Found")

        return df_to_html(df, f"Sector: {sector}")

    # ----------------------------------------------------------------------
    # INDEX
    # ----------------------------------------------------------------------
    @app.get("/index")
    def index_history():
        df = queries.get_index_history(limit=300)
        return df_to_html(df, "S&P 500 Index History")

    # ----------------------------------------------------------------------
    # METRICS
    # ----------------------------------------------------------------------
    @app.get("/metrics")
    def metrics_endpoint():
        text = f"uptime_seconds {int(time.time() - START_TIME)}\n"
        for key, val in metrics.items():
            text += f"{key.replace('/', '_')} {val}\n"
        return text, 200, {"Content-Type": "text/plain"}

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
