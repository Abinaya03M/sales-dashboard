from flask import Flask, render_template, request,redirect,url_for
import pandas as pd

app = Flask(__name__)

# ---------------- LOAD DATA ----------------
df = pd.read_csv("Business_Sales_Dataset.csv")
df["OrderDate"] = pd.to_datetime(df["OrderDate"])


# ---------------- AI SUMMARY FUNCTION ----------------
def generate_summary(total_sales, total_profit, shipping_ratio, top_product):
    summary = "The business shows "

    if total_sales > 0:
        summary += "active sales performance "
    else:
        summary += "weak sales performance "

    if total_profit > 0:
        summary += "with overall profitability remaining positive. "
    else:
        summary += "but profitability is under pressure. "

    if shipping_ratio > 0.25:
        summary += (
            "High shipping costs are significantly impacting profit margins. "
            "Optimizing logistics could improve financial outcomes. "
        )

    summary += (
        f"{top_product} emerges as the top-performing product, "
        "presenting opportunities for focused growth strategies."
    )

    return summary


# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():

    # -------- FILTERS --------
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    region = request.args.get("region")

    filtered = df.copy()

    if start_date:
        filtered = filtered[filtered["OrderDate"] >= start_date]

    if end_date:
        filtered = filtered[filtered["OrderDate"] <= end_date]

    if region:
        filtered = filtered[filtered["Region"] == region]

    # -------- KPIs --------
    total_sales = filtered["TotalPrice"].sum()
    total_orders = filtered["OrderID"].nunique()

    filtered["Profit"] = (
        filtered["TotalPrice"]
        - filtered["ShippingCost"]
        - (filtered["TotalPrice"] * filtered["Discount"] / 100)
    )

    total_profit = filtered["Profit"].sum()

    # -------- CHART DATA --------
    monthly_sales = (
        filtered.groupby(filtered["OrderDate"].dt.to_period("M"))["TotalPrice"]
        .sum()
    )

    product_sales = filtered.groupby("Product")["TotalPrice"].sum()
    region_profit = filtered.groupby("Region")["Profit"].sum()

    regions = sorted(df["Region"].unique())

    # -------- TABLE DATA --------
    table_data = (
        filtered[["Product", "Region", "TotalPrice", "Profit"]]
        .head(10)
        .to_dict(orient="records")
    )

    # -------- AUTO INSIGHTS --------
    auto_insights = []

    if not monthly_sales.empty:
        max_month = monthly_sales.idxmax()
        min_month = monthly_sales.idxmin()

        auto_insights.append({
            "insight": f"Highest sales occurred in {max_month}, indicating seasonal demand.",
            "action": "Increase inventory and marketing efforts during this period."
        })

        auto_insights.append({
            "insight": f"Lowest sales were observed in {min_month}, suggesting weaker demand.",
            "action": "Run promotions or discounts to boost demand during this period."
        })

    avg_profit = filtered["Profit"].mean()

    if avg_profit < 0:
        auto_insights.append({
            "insight": "Overall average profit is negative, indicating high costs or discounts.",
            "action": "Review cost structure and optimize discount strategies."
        })
    else:
        auto_insights.append({
            "insight": "Overall average profit is positive, showing healthy business performance.",
            "action": "Continue current strategies and explore scaling opportunities."
        })

    shipping_ratio = filtered["ShippingCost"].sum() / filtered["TotalPrice"].sum()

    if shipping_ratio > 0.25:
        auto_insights.append({
            "insight": "Shipping cost exceeds 25% of total sales, significantly impacting profit.",
            "action": "Negotiate shipping contracts or switch to cost-effective delivery options."
        })

    top_product = product_sales.idxmax()
    auto_insights.append({
        "insight": f"{top_product} is the top-selling product by revenue.",
        "action": f"Ensure sufficient stock levels and focus marketing on {top_product}."
    })

    # -------- AI SUMMARY --------
    ai_summary = generate_summary(
        total_sales,
        total_profit,
        shipping_ratio,
        top_product
    )





    # -------- RETURN (MANDATORY) --------
    return render_template(
        "dashboard.html",
        total_sales=round(total_sales, 2),
        total_profit=round(total_profit, 2),
        total_orders=total_orders,
        regions=regions,
        months=monthly_sales.index.astype(str).tolist(),
        monthly_sales=monthly_sales.values.tolist(),
        products=product_sales.index.tolist(),
        product_sales=product_sales.values.tolist(),
        region_names=region_profit.index.tolist(),
        region_profit=region_profit.values.tolist(),
        table_data=table_data,
        auto_insights=auto_insights,
        ai_summary=ai_summary
    )



@app.route("/feedback", methods=["POST"])
def feedback():
    name = request.form.get("name")
    email = request.form.get("email")
    purpose = request.form.get("purpose")
    message = request.form.get("message")

    print("Feedback received:")
    print(name, email, purpose, message)

    return redirect(url_for("dashboard", feedback="success"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

