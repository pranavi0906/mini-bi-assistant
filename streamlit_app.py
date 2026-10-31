
import requests
import streamlit as st
import pandas as pd


API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(
    page_title="Mini BI Assistant",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Mini AI Business Intelligence Assistant")
st.write("Ask natural-language questions about the sales dataset.")

question = st.text_input(
    "Enter your question",
    placeholder="For example: What is our total revenue?",
)

if st.button("Ask"):

    if not question.strip():
        st.warning("Please enter a question.")

    else:
        try:
            with st.spinner("Analyzing your sales data..."):
                response = requests.post(
                    API_URL,
                    json={"question": question},
                    timeout=30,
                )

            if response.status_code == 200:
                result = response.json()["result"]
                metric = result.get("metric")

                st.subheader("Answer")

                # ------------------------------------------
                # 1. Total revenue
                # ------------------------------------------

                if metric == "total_revenue":
                    st.metric(
                        "Total Revenue",
                        f"₹{result['total_revenue']:,.2f}",
                    )

                    st.write(
                        f"Completed transactions: "
                        f"{result['transaction_count']}"
                    )

                # ------------------------------------------
                # 2. Highest revenue product
                # ------------------------------------------

                elif metric == "highest_revenue_product":
                    st.write(
                        f"**{result['product']}** generated the "
                        f"highest revenue."
                    )

                    st.metric(
                        "Revenue",
                        f"₹{result['revenue']:,.2f}",
                    )

                    st.write(
                        f"Units sold: {result['units_sold']}"
                    )

                # ------------------------------------------
                # 3. Highest revenue region
                # ------------------------------------------

                elif metric == "highest_revenue_region":
                    st.write(
                        f"**{result['region']}** generated the "
                        f"highest regional revenue."
                    )

                    st.metric(
                        "Revenue",
                        f"₹{result['revenue']:,.2f}",
                    )

                    st.write(
                        f"Transactions: "
                        f"{result['transaction_count']}"
                    )

                # ------------------------------------------
                # 4. Monthly revenue trend
                # ------------------------------------------

                elif metric == "monthly_revenue":
                    df = pd.DataFrame(result["data"])

                    if not df.empty:
                        st.line_chart(
                            df.set_index("month")["revenue"]
                        )

                        st.dataframe(
                            df,
                            use_container_width=True,
                        )
                    else:
                        st.info("No monthly revenue data available.")

                # ------------------------------------------
                # 5. Monthly revenue comparison
                # ------------------------------------------

                elif metric == "monthly_revenue_comparison":
                    month_1 = result["month_1"]
                    month_2 = result["month_2"]

                    revenue_1 = result["revenue_1"]
                    revenue_2 = result["revenue_2"]

                    difference = result["difference"]
                    percentage = result["percentage_change"]

                    st.write(
                        f"**{month_1} vs {month_2}**"
                    )

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        month_1,
                        f"₹{revenue_1:,.2f}",
                    )

                    col2.metric(
                        month_2,
                        f"₹{revenue_2:,.2f}",
                    )

                    col3.metric(
                        "Revenue Change",
                        f"₹{difference:,.2f}",
                        (
                            f"{percentage:.2f}%"
                            if percentage is not None
                            else "N/A"
                        ),
                    )

                    # Natural-language interpretation
                    if difference > 0:
                        st.success(
                            f"Revenue in {month_2} was "
                            f"₹{difference:,.2f} "
                            f"({percentage:.2f}%) higher than "
                            f"{month_1}."
                        )

                    elif difference < 0:
                        percentage_text = (
                            f" ({abs(percentage):.2f}%)"
                            if percentage is not None
                            else ""
                        )

                        st.info(
                            f"Revenue in {month_2} was "
                            f"₹{abs(difference):,.2f}"
                            f"{percentage_text} lower than "
                            f"{month_1}."
                        )

                    else:
                        st.info(
                            f"Revenue was the same in "
                            f"{month_1} and {month_2}."
                        )

                # ------------------------------------------
                # 6. Total units sold
                # ------------------------------------------

                elif metric == "total_units_sold":
                    st.metric(
                        "Total Units Sold",
                        result["total_units_sold"],
                    )

                # ------------------------------------------
                # 7. Category / sales channel revenue
                # ------------------------------------------

                elif metric in [
                    "revenue_by_category",
                    "revenue_by_sales_channel",
                ]:
                    df = pd.DataFrame(result["data"])

                    if not df.empty:
                        st.bar_chart(
                            df.set_index(df.columns[0])["revenue"]
                        )

                        st.dataframe(
                            df,
                            use_container_width=True,
                        )
                    else:
                        st.info("No revenue data available.")

                # ------------------------------------------
                # 8. Unsupported questions
                # ------------------------------------------

                elif (
                    metric == "unknown"
                    or metric == "unsupported"
                    or result.get("intent") == "unknown"
                ):
                    st.info(
                        result.get(
                            "message",
                            "I couldn't understand that question. "
                            "Please ask about the sales data, such as "
                            "revenue, products, regions, monthly trends, "
                            "categories, or sales channels.",
                        )
                    )

                # ------------------------------------------
                # 9. Fallback
                # ------------------------------------------

                else:
                    st.json(result)

            else:
                st.error(
                    f"API returned status code "
                    f"{response.status_code}: {response.text}"
                )

        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to the API. "
                "Make sure the FastAPI server is running."
            )

        except requests.exceptions.Timeout:
            st.error(
                "The request took too long. Please try again."
            )

        except Exception as error:
            st.error(
                f"Something went wrong: {error}"
            )
