import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

DATA_DIR = Path("data")

st.set_page_config(
    page_title="YottaFlex Supply Chain Intelligence",
    page_icon="📦",
    layout="wide"
)


@st.cache_data
def load_data():
    return {
        "sku": pd.read_csv(DATA_DIR / "sku.csv"),
        "location": pd.read_csv(DATA_DIR / "location.csv"),
        "supplier": pd.read_csv(DATA_DIR / "supplier.csv"),
        "demand": pd.read_csv(DATA_DIR / "forecast_demand.csv"),
        "inventory": pd.read_csv(DATA_DIR / "inventory.csv"),
        "projected": pd.read_csv(
            DATA_DIR / "projected_inventory.csv"
        ),
        "shortage": pd.read_csv(DATA_DIR / "shortage.csv"),
        "mitigation": pd.read_csv(
            DATA_DIR / "mitigation_option.csv"
        ),
        "production": pd.read_csv(
            DATA_DIR / "production_feasibility.csv"
        )
    }


try:
    data = load_data()
except FileNotFoundError as error:
    st.error(f"Missing dataset: {error}")
    st.info(
        "Generate the datasets before launching the dashboard."
    )
    st.stop()


st.title("📦 Supply Chain Intelligence")
st.caption(
    "Demand Forecasting • Inventory Planning • "
    "Shortage Prioritization • Supplier Mitigation"
)

st.warning(
    "Synthetic demonstration data. Shortage causes and "
    "mitigation feasibility are preliminary estimates."
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Demand Analysis",
        "Inventory Analysis",
        "Shortage Prioritization",
        "Mitigation Recommendations",
        "Production Planning"
    ]
)


if page == "Overview":

    st.header("Supply Chain Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total SKUs", f"{len(data['sku']):,}")

    col2.metric(
        "Locations",
        f"{len(data['location']):,}"
    )

    col3.metric(
        "Suppliers",
        f"{len(data['supplier']):,}"
    )

    col4.metric(
        "Shortage Records",
        f"{len(data['shortage']):,}"
    )

    st.subheader("Shortage Severity Distribution")

    severity = (
        data["shortage"]["severity"]
        .value_counts()
        .reset_index()
    )

    severity.columns = ["Severity", "Count"]

    fig = px.bar(
        severity,
        x="Severity",
        y="Count",
        color="Severity",
        title="Shortages by Severity"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Supply Chain Summary")

    summary = pd.DataFrame({
        "Metric": [
            "Demand Forecast Records",
            "Inventory Records",
            "Negative Balance Weeks",
            "Mitigation Candidates",
            "Preliminary Feasible Mitigations",
            "Production Plans"
        ],
        "Value": [
            len(data["demand"]),
            len(data["inventory"]),
            int(data["projected"]["shortage_flag"].sum()),
            len(data["mitigation"]),
            int(data["mitigation"]["feasible"].sum()),
            len(data["production"])
        ]
    })

    st.dataframe(summary, use_container_width=True)


elif page == "Demand Analysis":

    st.header("Demand Forecast Analysis")

    sku_id = st.selectbox(
        "Select SKU",
        sorted(data["demand"]["sku_id"].unique())
    )

    selected = data["demand"][
        data["demand"]["sku_id"] == sku_id
    ]

    weekly = (
        selected.groupby("week", as_index=False)[
            "forecast_qty"
        ].sum()
    )

    fig = px.line(
        weekly,
        x="week",
        y="forecast_qty",
        markers=True,
        title=f"Weekly Demand Forecast — {sku_id}"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.metric(
        "Total Forecast Demand",
        f"{selected['forecast_qty'].sum():,}"
    )

    st.metric(
        "Demand Spike Records",
        int(selected["demand_spike"].sum())
    )

    st.dataframe(
        selected.head(100),
        use_container_width=True
    )


elif page == "Inventory Analysis":

    st.header("Projected Inventory Analysis")

    sku_id = st.selectbox(
        "Select SKU",
        sorted(data["projected"]["sku_id"].unique())
    )

    selected = data["projected"][
        data["projected"]["sku_id"] == sku_id
    ].copy()

    location_id = st.selectbox(
        "Select Location",
        sorted(selected["location_id"].unique())
    )

    selected = selected[
        selected["location_id"] == location_id
    ]

    fig = px.line(
        selected,
        x="week",
        y="projected_balance",
        markers=True,
        title="Weekly Projected Inventory Balance"
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        annotation_text="Shortage Threshold"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        selected[
            [
                "week",
                "opening_balance",
                "inbound_qty",
                "forecast_qty",
                "projected_balance",
                "shortage_flag"
            ]
        ],
        use_container_width=True
    )


elif page == "Shortage Prioritization":

    st.header("Shortage Prioritization")

    severity_filter = st.selectbox(
        "Select Severity",
        ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"]
    )

    shortages = data["shortage"]

    if severity_filter != "ALL":
        shortages = shortages[
            shortages["severity"] == severity_filter
        ]

    st.metric(
        "Matching Shortage Records",
        f"{len(shortages):,}"
    )

    st.subheader("Largest New Shortages")

    st.dataframe(
        shortages.sort_values(
            "new_shortage_qty",
            ascending=False
        ).head(100),
        use_container_width=True
    )

    st.subheader("Shortages by Preliminary Cause")

    causes = (
        shortages["cause"]
        .value_counts()
        .reset_index()
    )

    causes.columns = ["Cause", "Count"]

    fig = px.bar(
        causes,
        x="Cause",
        y="Count",
        color="Cause"
    )

    st.plotly_chart(fig, use_container_width=True)


elif page == "Mitigation Recommendations":

    st.header("Supplier Mitigation Recommendations")

    st.info(
        "These are independent candidate evaluations, not "
        "collectively reserved supplier capacity."
    )

    option_filter = st.selectbox(
        "Filter Options",
        ["ALL", "FEASIBLE", "NOT_FEASIBLE"]
    )

    options = data["mitigation"]

    if option_filter == "FEASIBLE":
        options = options[
            options["feasible"] == True
        ]

    elif option_filter == "NOT_FEASIBLE":
        options = options[
            options["feasible"] == False
        ]

    st.metric(
        "Matching Mitigation Options",
        f"{len(options):,}"
    )

    st.dataframe(
        options.head(200),
        use_container_width=True
    )

    st.subheader("Mitigation Coverage")

    feasible_options = options[
        options["feasible"] == True
    ]

    if not feasible_options.empty:
        fig = px.histogram(
            feasible_options,
            x="coverage_ratio",
            nbins=20,
            title="Shortage Coverage Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)


elif page == "Production Planning":

    st.header("Production Feasibility")

    production = data["production"]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Production Plans",
        f"{len(production):,}"
    )

    col2.metric(
        "Preliminary Feasible",
        f"{int(production['preliminary_feasible'].sum()):,}"
    )

    col3.metric(
        "Needs Review",
        f"{int((~production['preliminary_feasible']).sum()):,}"
    )

    status = (
        production["validation_status"]
        .value_counts()
        .reset_index()
    )

    status.columns = ["Status", "Count"]

    fig = px.pie(
        status,
        names="Status",
        values="Count",
        title="Production Feasibility Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        production.head(200),
        use_container_width=True
    )


st.divider()

st.caption(
    "YottaFlex AI Code Challenge | "
    "Synthetic Supply Chain Decision-Support Prototype"
)