from flask import Flask, render_template, request, send_file
import pandas as pd
import sqlite3
import io

app = Flask(__name__)
DB_PATH = "smart_energy.db"

# Load filtered data
def load_data(country=None, fuel_type=None):
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM energy_data"
    filters = []

    if country:
        filters.append(f"country = '{country}'")
    if fuel_type:
        filters.append(f"fuel_type = '{fuel_type}'")

    if filters:
        query += " WHERE " + " AND ".join(filters)

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Generate chart data
def get_chart_data(df):
    if df.empty:
        return {
            "years": [],
            "used": [],
            "generated": [],
            "saved": [],
            "wasted": [],
            "difference": []
        }

    grouped = df.groupby("year").sum(numeric_only=True).reset_index()
    used = grouped["energy_consumption_ej"]
    generated = used * 1.10
    saved = generated - used
    wasted = generated * 0.02
    difference = generated - used

    return {
        "years": list(grouped["year"]),
        "used": list(used.round(2)),
        "generated": list(generated.round(2)),
        "saved": list(saved.round(2)),
        "wasted": list(wasted.round(2)),
        "difference": list(difference.round(2))
    }

# Summary stats
def compute_stats(df):
    used = df["energy_consumption_ej"].sum()
    generated = used * 1.10
    saved = generated - used
    wasted = generated * 0.02
    return {
        "used": round(used, 2),
        "generated": round(generated, 2),
        "saved": round(saved, 2),
        "wasted": round(wasted, 2)
    }

# Dropdown filter values
def get_filters():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT DISTINCT country, fuel_type FROM energy_data", conn)
    conn.close()
    return {
        "countries": df["country"].dropna().unique().tolist(),
        "fuel_types": df["fuel_type"].dropna().unique().tolist()
    }

@app.route('/')
def index():
    country = request.args.get('country')
    fuel_type = request.args.get('fuel_type')

    df = load_data(country, fuel_type)
    stats = compute_stats(df)
    chart_data = get_chart_data(df)
    filters = get_filters()

    return render_template(
        "index.html",
        filters=filters,
        selected_country=country,
        selected_fuel_type=fuel_type,
        energy_stats=stats,
        chart_data=chart_data
    )

@app.route('/download')
def download_csv():
    df = load_data()
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()),
                     mimetype='text/csv',
                     download_name='filtered_energy_data.csv',
                     as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
