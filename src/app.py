import logging
import time
from collections import Counter

from flask import Flask, jsonify, request, redirect

from .db import init_db
from . import queries

metrics = Counter()
START_TIME = time.time()


def render_table(title, rows, columns):
    html = f"""
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            h1 {{ text-align: center; }}
            table {{
                width: 95%;
                border-collapse: collapse;
                margin: 20px auto;
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 8px 12px;
                font-size: 15px;
                text-align: left;
            }}
            th {{
                background-color: #007BFF;
                color: white;
            }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            a {{ text-decoration: none; color: #007BFF; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <table>
            <tr>
    """
    # headers
    for col in columns:
        html += f"<th>{col}</th>"
    html += "</tr>"

    # rows
    for r in rows:
        html += "<tr>"
        for col in columns:
            html += f"<td>{r.get(col, '')}</td>"
        html += "</tr>"

    html += """
        </table>
        <p style="text-align:center;">
            <a href="/">Back to Home</a>
        </p>
    </body>
    </html>
    """
    return html


def create_app() -> Flask:
    # Initialize DB (safe to call repeatedly)
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

    # ---------- HOME + SEARCH ----------

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
    <p>Your S&P 500 API deployed on Render.</p>

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

    @app.route("/go", methods=["POST"])
    def go():
        symbol = request.form.get("symbol", "").upper().strip()
        if symbol == "":
            return redirect("/")
        # Go to the readable company profile page
        return redirect(f"/company/{symbol}")

    # ---------- HEALTH ----------

    @app.get("/health")
    def health():
        return jsonify(
            {"status": "ok", "uptime_seconds": int(time.time() - START_TIME)}
        )

    # ---------- COMPANIES (HTML TABLE) ----------

    @app.route("/companies")
    def companies():
        raw = queries.get_all_companies()

        rows = []
        for c in raw:
            rows.append(
                {
                    "symbol": c.get("Symbol") or c.get("symbol"),
                    "name": c.get("Shortname") or c.get("name"),
                    "sector": c.get("Sector") or c.get("sector"),
                    "industry": c.get("Industry") or c.get("industry"),
                    "price": c.get("Currentprice") or c.get("currentprice"),
                    "marketcap": c.get("Marketcap") or c.get("marketcap"),
                }
            )

        columns = ["symbol", "name", "sector", "industry", "price", "marketcap"]
        return render_table("S&P 500 Companies", rows, columns)

    # ---------- SECTORS (HTML TABLE) ----------

    @app.route("/sectors")
    def sectors():
        raw = queries.get_sectors()

        # Convert tuples → strings
        sector_list = [str(s[0]) if isinstance(s, tuple) else str(s) for s in raw]
        rows = [{"sector": s} for s in sector_list]

        return render_table("Sectors", rows, ["sector"])

    # ---------- SINGLE COMPANY (HTML TABLE) ----------

    @app.route("/company/<symbol>")
    def company_profile(symbol: str):
        c = queries.get_company_by_symbol(symbol.upper())

        if not c:
            return (
                f"<h1>Company '{symbol}' not found.</h1><p><a href='/'>Back</a></p>",
                404,
            )

        normalized = {
            "symbol": c.get("Symbol") or c.get("symbol"),
            "name": c.get("Shortname") or c.get("name"),
            "sector": c.get("Sector") or c.get("sector"),
            "industry": c.get("Industry") or c.get("industry"),
            "price": c.get("Currentprice") or c.get("currentprice"),
            "marketcap": c.get("Marketcap") or c.get("marketcap"),
        }

        return render_table(
            f"Company: {symbol.upper()}",
            [normalized],
            list(normalized.keys()),
        )

    # ---------- INDEX (HTML TABLE) ----------

    @app.route("/index")
    def index_page():
        raw = queries.get_index_data()

        rows = []
        for r in raw:
            rows.append(
                {
                    "date": r.get("date") or r.get("Date"),
                    "open": r.get("open") or r.get("Open"),
                    "high": r.get("high") or r.get("High"),
                    "low": r.get("low") or r.get("Low"),
                    "close": r.get("close") or r.get("Close"),
                    "volume": r.get("volume") or r.get("Volume"),
                }
            )

        columns = ["date", "open", "high", "low", "close", "volume"]
        return render_table("S&P 500 Index", rows, columns)

    # ---------- METRICS ----------

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

# For `python -m src.app` local dev
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
