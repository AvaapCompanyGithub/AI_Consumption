import streamlit as st
from snowflake.snowpark.context import get_active_session
import altair as alt
from datetime import datetime, timedelta

#Snowpark Session
session = get_active_session()

#Last Refresh
if "last_refreshed" not in st.session_state:
    st.session_state.last_refreshed = datetime.now()

#Cache to 1 hour
@st.cache_data(ttl=3600)
def run_query(sql):
    return session.sql(sql).to_pandas()

##########
#Default styles and colors

st.markdown("""
<style>
    html, body, [class*="css"] {
    font-family: Verdana, Geneva, sans-serif;
    }
    [data-testid="stDateInput"] {
        opacity: 0.5;
    }
    [data-testid="stDateInput"]:hover {
        opacity: 1.0;
    }
    [data-testid="stCaptionContainer"] {
        opacity: 0.5;
    }
    .date-range-display {
        opacity: 0.5;
    }
    .date-range-display:hover {
        opacity: 1.0;
    }
    [data-testid="stSelectbox"] {
        opacity: 0.5;
    }
    [data-testid="stSelectbox"]:hover {
        opacity: 1.0;
    }
        [data-testid="stMetric"] {
        font-size: 0.8rem;
    }
    [data-testid="stMetric"] label {
        font-size: 0.75rem;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.2rem;
        
    }
    [data-testid="stButton"] button {
        font-size: 10px;
        padding: 2px 8px;
    }
    .compact {
        margin: 0;
        font-size: 12px;
        color: gray;
        line-height: 1.2;
        list-style-position: outside;
    }
</style>
""", unsafe_allow_html=True)


service_colors = {
    "AISQL Functions": "#f2b949",        # yellow
    "Cortex Agents": "#ff7f0e",          # orange
    "AI Functions": "#2ca02c",           # green
    "Cortex Analyst": "#d62728",         # red
    "Cortex Search": "#7f7f7f",          # gray
    "Cortex Code (Snowsight)": "#1f77b4",# blue
    "Cortex Code (CLI)": "#9467bd",      # purple
}


##########
#Title and information

st.set_page_config(page_title="Cortex/AI Credit Consumption Dashboard", layout="wide")
st.title("Cortex/AI Credit Consumption Dashboard")
st.markdown(f"<div class='compact'>ACCOUNT_USAGE views have up to 3 hours of latency.<p></div>", unsafe_allow_html=True)

#Buttons
col_refresh, col_pdf = st.columns([1, 1])
with col_refresh:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()
with col_pdf:
    if st.button("📄 Export to PDF"):
        st.info("Use Ctrl+P (or Cmd+P on Mac) to print/save this page as PDF.")

st.markdown(f"<div class='compact'>Last refreshed: {st.session_state.last_refreshed.strftime('%Y-%m-%d %H:%M:%S')}<p></div>", unsafe_allow_html=True)

##########
#Date Range options

st.markdown("---")

#2 date boxes, one dropdown
default_index = 2 if datetime.now().weekday() != 0 else 13 #If today is Monday, show last week
col_a, col_b, col_c = st.columns([1, 1, 2])
with col_c:
    preset = st.selectbox("Date Range", ["Today", "Yesterday", "This Week", "This Month", "This Quarter", "This Year", "Last 7 Days", "Last 14 Days", "Last 30 Days", "Last 60 Days", "Last 90 Days", "Last 180 Days", "Last 365 Days", "Last Week", "Last Month", "Last Quarter"], index=default_index)
if preset == "Today":
    default_start = datetime.now().date()
    default_end = datetime.now().date()
elif preset == "Yesterday":
    default_start = (datetime.now() - timedelta(days=1)).date()
    default_end = (datetime.now() - timedelta(days=1)).date()
elif preset == "This Week":
    default_start = (datetime.now() - timedelta(days=datetime.now().weekday())).date()
    default_end = datetime.now().date()
elif preset == "This Month":
    default_start = datetime.now().replace(day=1).date()
    default_end = datetime.now().date()
elif preset == "This Quarter":
    month = datetime.now().month
    quarter_start_month = ((month - 1) // 3) * 3 + 1
    default_start = datetime.now().replace(month=quarter_start_month, day=1).date()
    default_end = datetime.now().date()
elif preset == "This Year":
    default_start = datetime.now().replace(month=1, day=1).date()
    default_end = datetime.now().date()
elif preset == "Last 7 Days":
    default_start = (datetime.now() - timedelta(days=7)).date()
    default_end = datetime.now().date()
elif preset == "Last 14 Days":
    default_start = (datetime.now() - timedelta(days=14)).date()
    default_end = datetime.now().date()
elif preset == "Last 30 Days":
    default_start = (datetime.now() - timedelta(days=30)).date()
    default_end = datetime.now().date()
elif preset == "Last 60 Days":
    default_start = (datetime.now() - timedelta(days=60)).date()
    default_end = datetime.now().date()
elif preset == "Last 90 Days":
    default_start = (datetime.now() - timedelta(days=90)).date()
    default_end = datetime.now().date()
elif preset == "Last 180 Days":
    default_start = (datetime.now() - timedelta(days=180)).date()
    default_end = datetime.now().date()
elif preset == "Last 365 Days":
    default_start = (datetime.now() - timedelta(days=365)).date()
    default_end = datetime.now().date()
elif preset == "Last Week":
    last_monday = (datetime.now() - timedelta(days=datetime.now().weekday() + 7)).date()
    default_start = last_monday
    default_end = last_monday + timedelta(days=6)
elif preset == "Last Month":
    first_of_this_month = datetime.now().replace(day=1)
    last_month_end = (first_of_this_month - timedelta(days=1)).date()
    default_start = last_month_end.replace(day=1)
    default_end = last_month_end
elif preset == "Last Quarter":
    month = datetime.now().month
    current_q_start = ((month - 1) // 3) * 3 + 1
    last_q_end = (datetime.now().replace(month=current_q_start, day=1) - timedelta(days=1)).date()
    last_q_start = ((last_q_end.month - 1) // 3) * 3 + 1
    default_start = last_q_end.replace(month=last_q_start, day=1)
    default_end = last_q_end
else:
    default_start = (datetime.now() - timedelta(days=datetime.now().weekday())).date()
    default_end = datetime.now().date()

with col_a:
    start_date = st.date_input("Start Date", value=default_start, key=f"start_{preset}")
with col_b:
    end_date = st.date_input("End Date", value=default_end, key=f"end_{preset}")

if start_date == end_date:
    end_date = end_date + timedelta(days=1)

start_ts = start_date.strftime("%Y-%m-%d")
end_ts = end_date.strftime("%Y-%m-%d")

st.markdown(f"Showing Date Range: <b style='color:red;'>{start_date} &rarr; {end_date}</b>", unsafe_allow_html=True)

##########
#Summary/Counts

#Query: Get Service/Credits
summary_sql = f"""
WITH aisql AS (
    SELECT 'AISQL Functions' AS service, ROUND(SUM(TOKEN_CREDITS), 4) AS credits
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY
    WHERE USAGE_TIME >= '{start_ts}' AND USAGE_TIME < '{end_ts}'
),
agent AS (
    SELECT 'Cortex Agents' AS service, ROUND(SUM(TOKEN_CREDITS), 4) AS credits
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY
    WHERE START_TIME >= '{start_ts}' AND START_TIME < '{end_ts}'
),
ai_func AS (
    SELECT 'AI Functions' AS service, ROUND(SUM(CREDITS), 4) AS credits
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_FUNCTIONS_USAGE_HISTORY
    WHERE START_TIME >= '{start_ts}' AND START_TIME < '{end_ts}'
),
analyst AS (
    SELECT 'Cortex Analyst' AS service, ROUND(SUM(CREDITS), 4) AS credits
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY
    WHERE START_TIME >= '{start_ts}' AND START_TIME < '{end_ts}'
),
search AS (
    SELECT 'Cortex Search' AS service, ROUND(SUM(CREDITS), 4) AS credits
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_DAILY_USAGE_HISTORY
    WHERE USAGE_DATE >= '{start_ts}' AND USAGE_DATE < '{end_ts}'
),
code_ss AS (
    SELECT 'Cortex Code (Snowsight)' AS service, ROUND(SUM(TOKEN_CREDITS), 4) AS credits
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_SNOWSIGHT_USAGE_HISTORY
    WHERE USAGE_TIME >= '{start_ts}' AND USAGE_TIME < '{end_ts}'
),
code_cli AS (
    SELECT 'Cortex Code (CLI)' AS service, ROUND(SUM(TOKEN_CREDITS), 4) AS credits
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_CLI_USAGE_HISTORY
    WHERE USAGE_TIME >= '{start_ts}' AND USAGE_TIME < '{end_ts}'
)
SELECT * FROM aisql UNION ALL SELECT * FROM agent UNION ALL SELECT * FROM ai_func
UNION ALL SELECT * FROM analyst UNION ALL SELECT * FROM search
UNION ALL SELECT * FROM code_ss UNION ALL SELECT * FROM code_cli
"""

df_summary = run_query(summary_sql)
#Calculate some totals
df_summary["CREDITS"] = df_summary["CREDITS"].fillna(0)
total_credits = df_summary["CREDITS"].sum()
top_service = df_summary.loc[df_summary["CREDITS"].idxmax(), "SERVICE"] if total_credits > 0 else "N/A"
active_services = (df_summary["CREDITS"] > 0).sum()

#Compare to previous
prev_days = (end_date - start_date).days
if prev_days > 0:
    prev_start = (start_date - timedelta(days=prev_days)).strftime("%Y-%m-%d")
    prev_end = start_ts
    prev_sql = f"""
    WITH aisql AS (
        SELECT ROUND(SUM(TOKEN_CREDITS), 4) AS credits FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY WHERE USAGE_TIME >= '{prev_start}' AND USAGE_TIME < '{prev_end}'
    ), agent AS (
        SELECT ROUND(SUM(TOKEN_CREDITS), 4) AS credits FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY WHERE START_TIME >= '{prev_start}' AND START_TIME < '{prev_end}'
    ), ai_func AS (
        SELECT ROUND(SUM(CREDITS), 4) AS credits FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_FUNCTIONS_USAGE_HISTORY WHERE START_TIME >= '{prev_start}' AND START_TIME < '{prev_end}'
    ), analyst AS (
        SELECT ROUND(SUM(CREDITS), 4) AS credits FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY WHERE START_TIME >= '{prev_start}' AND START_TIME < '{prev_end}'
    ), search AS (
        SELECT ROUND(SUM(CREDITS), 4) AS credits FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_DAILY_USAGE_HISTORY WHERE USAGE_DATE >= '{prev_start}' AND USAGE_DATE < '{prev_end}'
    ), code_ss AS (
        SELECT ROUND(SUM(TOKEN_CREDITS), 4) AS credits FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_SNOWSIGHT_USAGE_HISTORY WHERE USAGE_TIME >= '{prev_start}' AND USAGE_TIME < '{prev_end}'
    ), code_cli AS (
        SELECT ROUND(SUM(TOKEN_CREDITS), 4) AS credits FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_CLI_USAGE_HISTORY WHERE USAGE_TIME >= '{prev_start}' AND USAGE_TIME < '{prev_end}'
    )
    SELECT COALESCE(SUM(credits), 0) AS total FROM (
        SELECT * FROM aisql UNION ALL SELECT * FROM agent UNION ALL SELECT * FROM ai_func
        UNION ALL SELECT * FROM analyst UNION ALL SELECT * FROM search
        UNION ALL SELECT * FROM code_ss UNION ALL SELECT * FROM code_cli
    )
    """
    prev_credits = run_query(prev_sql)["TOTAL"].iloc[0]
    if prev_credits > 0:
        growth_pct = round(((total_credits - prev_credits) / prev_credits) * 100, 1)
        delta_str = f"{growth_pct}%"
    elif total_credits > 0:
        delta_str = "New"
    else:
        delta_str = "0%"
else:
    delta_str = "N/A"

#Avg daily
num_days = max((end_date - start_date).days, 1)
avg_daily = total_credits / num_days

#Count total requests
total_code_requests_sql = f"""
SELECT
    (SELECT COUNT(DISTINCT REQUEST_ID) FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_SNOWSIGHT_USAGE_HISTORY WHERE USAGE_TIME >= '{start_ts}' AND USAGE_TIME < '{end_ts}') +
    (SELECT COUNT(DISTINCT REQUEST_ID) FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_CLI_USAGE_HISTORY WHERE USAGE_TIME >= '{start_ts}' AND USAGE_TIME < '{end_ts}') AS TOTAL_REQUESTS
"""
total_code_requests = run_query(total_code_requests_sql)["TOTAL_REQUESTS"].iloc[0]

#Render it to the page
st.markdown("---")
st.markdown(f"Totals based on Date Range:", unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    credit_color = "red" if delta_str.startswith("+") or delta_str == "New" else "green" if delta_str.startswith("-") else "inherit"
    st.markdown(f"<div style='text-align:center;'><span style='font-size:12px;color:gray;'>Total AI Credits<br>(<span style='color:{credit_color};'>{delta_str}</span> vs prior)</span><br><span style='font-size:16px;font-weight:normal;color:{credit_color};'>{total_credits:,.4f}</span></div>", unsafe_allow_html=True)
with k2:
    burn_color = "red" if avg_daily > 1 else "green" if avg_daily > 0 else "gray"
    st.markdown(f"<div style='text-align:center;'><span style='font-size:12px;color:gray;'>Avg Daily Burn</span><br><span style='font-size:16px;font-weight:normal;color:{burn_color};'>{avg_daily:,.4f}</span></div>", unsafe_allow_html=True)
with k3:
    st.markdown(f"<div style='text-align:center;'><span style='font-size:12px;color:gray;'>Top Service</span><br><span style='font-size:16px;font-weight:normal;'>{top_service}</span></div>", unsafe_allow_html=True)
with k4:
    st.markdown(f"<div style='text-align:center;'><span style='font-size:12px;color:gray;'>Active Services</span><br><span style='font-size:16px;font-weight:normal;'>{active_services}</span></div>", unsafe_allow_html=True)
with k5:
    st.markdown(f"<div style='text-align:center;'><span style='font-size:12px;color:gray;'>Code Requests</span><br><span style='font-size:16px;font-weight:normal;'>{total_code_requests:,}</span></div>", unsafe_allow_html=True)

#Credits by Service Pie Chart (left) and Service Distribution (right)
st.markdown("---")
left, right = st.columns(2)
with left:
    st.subheader("Credits by Service")
    df_bar = df_summary[df_summary["CREDITS"] > 0].sort_values("CREDITS", ascending=False)
    if not df_bar.empty:
        chart = alt.Chart(df_bar).mark_bar().encode(
            x=alt.X("CREDITS:Q", title="Credits"),
            y=alt.Y("SERVICE:N", sort="-x", title=""),
            #color=alt.Color("SERVICE:N", legend=None),
            color=alt.Color("SERVICE:N", legend=None, scale=alt.Scale(domain=list(service_colors.keys()), range=list(service_colors.values()))),
            tooltip=["SERVICE", "CREDITS"]
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No AI credit usage in selected period.")
with right:
    st.subheader("Service Distribution")
    df_pie = df_summary[df_summary["CREDITS"] > 0]
    if not df_pie.empty:
        pie = alt.Chart(df_pie).mark_arc(innerRadius=50).encode(
            theta=alt.Theta("CREDITS:Q"),
            #color=alt.Color("SERVICE:N", title="Service"),
            color=alt.Color("SERVICE:N", title="Service", scale=alt.Scale(domain=list(service_colors.keys()), range=list(service_colors.values()))),
            tooltip=["SERVICE", "CREDITS"]
        ).properties(height=300)
        st.altair_chart(pie, use_container_width=True)
    else:
        st.info("No data.")

#Credit Summary
st.markdown("---")
st.subheader("Credit Summary Table")
st.dataframe(df_summary.sort_values("CREDITS", ascending=False).reset_index(drop=True), use_container_width=True, hide_index=True)

##########
#Daily Trend

st.markdown("---")
st.subheader("Daily Credit Trend (All Services)")

#Filter by Services, Warehouse, Database
fil1, _ = st.columns(2)
with fil1:
    trend_view = st.selectbox("Filter Trend By", ["All Services", "By Warehouse (AISQL & AI Functions)", "By Database (Agents & Search)"])
if trend_view == "By Warehouse (AISQL & AI Functions)":
    trend_sql = f"""
    WITH wh_data AS (
        SELECT DATE(a.USAGE_TIME) AS usage_date, q.WAREHOUSE_NAME AS dimension, SUM(a.TOKEN_CREDITS) AS credits
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY a
        JOIN SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY q ON a.QUERY_ID = q.QUERY_ID
        WHERE a.USAGE_TIME >= '{start_ts}' AND a.USAGE_TIME < '{end_ts}' AND q.WAREHOUSE_NAME IS NOT NULL
        GROUP BY 1, 2
        UNION ALL
        SELECT DATE(h.START_TIME), q.WAREHOUSE_NAME, SUM(h.CREDITS)
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_FUNCTIONS_USAGE_HISTORY h
        JOIN SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY q ON h.QUERY_ID = q.QUERY_ID
        WHERE h.START_TIME >= '{start_ts}' AND h.START_TIME < '{end_ts}' AND q.WAREHOUSE_NAME IS NOT NULL
        GROUP BY 1, 2
    )
    SELECT USAGE_DATE, DIMENSION, ROUND(SUM(CREDITS), 4) AS CREDITS FROM wh_data GROUP BY 1, 2 ORDER BY 1
    """
    color_field = "DIMENSION"
    chart_title = "Daily Credits by Warehouse"
elif trend_view == "By Database (Agents & Search)":
    trend_sql = f"""
    WITH db_data AS (
        SELECT DATE(START_TIME) AS usage_date, AGENT_DATABASE_NAME AS dimension, SUM(TOKEN_CREDITS) AS credits
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY
        WHERE START_TIME >= '{start_ts}' AND START_TIME < '{end_ts}' AND AGENT_DATABASE_NAME IS NOT NULL
        GROUP BY 1, 2
        UNION ALL
        SELECT DATE(USAGE_DATE), DATABASE_NAME, SUM(CREDITS)
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_DAILY_USAGE_HISTORY
        WHERE USAGE_DATE >= '{start_ts}' AND USAGE_DATE < '{end_ts}' AND DATABASE_NAME IS NOT NULL
        GROUP BY 1, 2
    )
    SELECT USAGE_DATE, DIMENSION, ROUND(SUM(CREDITS), 4) AS CREDITS FROM db_data GROUP BY 1, 2 ORDER BY 1
    """
    color_field = "DIMENSION"
    chart_title = "Daily Credits by Database"
else:
    trend_sql = f"""
    WITH daily_data AS (
        SELECT DATE(USAGE_TIME) AS usage_date, 'AISQL Functions' AS service, SUM(TOKEN_CREDITS) AS credits
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY
        WHERE USAGE_TIME >= '{start_ts}' AND USAGE_TIME < '{end_ts}' GROUP BY DATE(USAGE_TIME)
        UNION ALL
        SELECT DATE(START_TIME), 'Cortex Agents', SUM(TOKEN_CREDITS)
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY
        WHERE START_TIME >= '{start_ts}' AND START_TIME < '{end_ts}' GROUP BY DATE(START_TIME)
        UNION ALL
        SELECT DATE(START_TIME), 'AI Functions', SUM(CREDITS)
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_FUNCTIONS_USAGE_HISTORY
        WHERE START_TIME >= '{start_ts}' AND START_TIME < '{end_ts}' GROUP BY DATE(START_TIME)
        UNION ALL
        SELECT DATE(START_TIME), 'Cortex Analyst', SUM(CREDITS)
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY
        WHERE START_TIME >= '{start_ts}' AND START_TIME < '{end_ts}' GROUP BY DATE(START_TIME)
        UNION ALL
        SELECT DATE(USAGE_DATE), 'Cortex Search', SUM(CREDITS)
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_DAILY_USAGE_HISTORY
        WHERE USAGE_DATE >= '{start_ts}' AND USAGE_DATE < '{end_ts}' GROUP BY DATE(USAGE_DATE)
        UNION ALL
        SELECT DATE(USAGE_TIME), 'Cortex Code (Snowsight)', SUM(TOKEN_CREDITS)
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_SNOWSIGHT_USAGE_HISTORY
        WHERE USAGE_TIME >= '{start_ts}' AND USAGE_TIME < '{end_ts}' GROUP BY DATE(USAGE_TIME)
        UNION ALL
        SELECT DATE(USAGE_TIME), 'Cortex Code (CLI)', SUM(TOKEN_CREDITS)
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_CLI_USAGE_HISTORY
        WHERE USAGE_TIME >= '{start_ts}' AND USAGE_TIME < '{end_ts}' GROUP BY DATE(USAGE_TIME)
    )
    SELECT USAGE_DATE, SERVICE AS DIMENSION, ROUND(CREDITS, 4) AS CREDITS FROM daily_data ORDER BY USAGE_DATE
    """
    color_field = "DIMENSION"
    chart_title = "Daily Credits by Service"

df_trend = run_query(trend_sql)

#Line chart with series    
if not df_trend.empty:
    stacked = alt.Chart(df_trend).mark_area(opacity=0.7).encode(
        x=alt.X("USAGE_DATE:T", title="Date"),
        y=alt.Y("CREDITS:Q", stack="zero", title="Credits"),
        #color=alt.Color(f"{color_field}:N", title=chart_title.split("by ")[-1]),
        color=alt.Color(f"{color_field}:N", title=chart_title.split("by ")[-1], scale=alt.Scale(domain=list(service_colors.keys()), range=list(service_colors.values()))),
        tooltip=["USAGE_DATE:T", f"{color_field}:N", "CREDITS:Q"]
    ).properties(height=350)
    st.altair_chart(stacked, use_container_width=True)
else:
    st.info("No daily trend data in selected period.")

##########
#Cost Efficiency

st.markdown("---")
st.subheader("Cost Efficiency by Service")

#Query
efficiency_sql = f"""
WITH aisql AS (
    SELECT 'AISQL Functions' AS service, ROUND(SUM(TOKEN_CREDITS), 6) AS total_credits, COUNT(DISTINCT QUERY_ID) AS total_requests
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY
    WHERE USAGE_TIME >= '{start_ts}' AND USAGE_TIME < '{end_ts}'
),
agent AS (
    SELECT 'Cortex Agents', ROUND(SUM(TOKEN_CREDITS), 6), COUNT(DISTINCT REQUEST_ID)
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY
    WHERE START_TIME >= '{start_ts}' AND START_TIME < '{end_ts}'
),
ai_func AS (
    SELECT 'AI Functions', ROUND(SUM(CREDITS), 6), COUNT(DISTINCT QUERY_ID)
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_FUNCTIONS_USAGE_HISTORY
    WHERE START_TIME >= '{start_ts}' AND START_TIME < '{end_ts}'
),
analyst AS (
    SELECT 'Cortex Analyst', ROUND(SUM(CREDITS), 6), SUM(REQUEST_COUNT)
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY
    WHERE START_TIME >= '{start_ts}' AND START_TIME < '{end_ts}'
),
code_ss AS (
    SELECT 'Cortex Code (Snowsight)', ROUND(SUM(TOKEN_CREDITS), 6), COUNT(DISTINCT REQUEST_ID)
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_SNOWSIGHT_USAGE_HISTORY
    WHERE USAGE_TIME >= '{start_ts}' AND USAGE_TIME < '{end_ts}'
),
code_cli AS (
    SELECT 'Cortex Code (CLI)', ROUND(SUM(TOKEN_CREDITS), 6), COUNT(DISTINCT REQUEST_ID)
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_CLI_USAGE_HISTORY
    WHERE USAGE_TIME >= '{start_ts}' AND USAGE_TIME < '{end_ts}'
)
SELECT * FROM aisql UNION ALL SELECT * FROM agent UNION ALL SELECT * FROM ai_func
UNION ALL SELECT * FROM analyst UNION ALL SELECT * FROM code_ss UNION ALL SELECT * FROM code_cli
"""

df_eff = run_query(efficiency_sql)
#Clean the dataframe
df_eff.columns = ["SERVICE", "TOTAL_CREDITS", "TOTAL_REQUESTS"]
df_eff["TOTAL_CREDITS"] = df_eff["TOTAL_CREDITS"].fillna(0)
df_eff["TOTAL_REQUESTS"] = df_eff["TOTAL_REQUESTS"].fillna(0).astype(int)
df_eff = df_eff[df_eff["TOTAL_REQUESTS"] > 0]
df_eff["COST_PER_REQUEST"] = (df_eff["TOTAL_CREDITS"] / df_eff["TOTAL_REQUESTS"]).round(6)
df_eff = df_eff.sort_values("COST_PER_REQUEST", ascending=False)

#Bar chart
if not df_eff.empty:
    eff_chart = alt.Chart(df_eff).mark_bar().encode(
        x=alt.X("COST_PER_REQUEST:Q", title="Credits per Request"),
        y=alt.Y("SERVICE:N", sort="-x", title=""),
        #color=alt.Color("SERVICE:N", legend=None),
        color=alt.Color("SERVICE:N", title="Service", scale=alt.Scale(domain=list(service_colors.keys()), range=list(service_colors.values()))),
        tooltip=["SERVICE", "TOTAL_CREDITS", "TOTAL_REQUESTS", "COST_PER_REQUEST"]
    ).properties(height=250)
    st.altair_chart(eff_chart, use_container_width=True)
    st.dataframe(df_eff.reset_index(drop=True), use_container_width=True, hide_index=True)
else:
    st.info("No request data in selected period.")

##########
#Users by credit

st.markdown("---")
st.subheader("Top Users by AI Credits")

#Tabs showing top users by Service type
tab1, tab2, tab3, tab4, tab5 = st.tabs(["AISQL Functions", "Cortex Agents", "AI Functions", "Cortex Code (Snowsight)", "Cortex Code (CLI)"])

with tab1:
    st.dataframe(run_query(f"""
    SELECT u.NAME AS USER_NAME, ROUND(SUM(h.TOKEN_CREDITS), 4) AS TOTAL_CREDITS, SUM(h.TOKENS) AS TOTAL_TOKENS, COUNT(DISTINCT h.QUERY_ID) AS QUERIES
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY h LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.USERS u ON TRY_CAST(h.USER_ID AS NUMBER) = u.USER_ID
    WHERE h.USAGE_TIME >= '{start_ts}' AND h.USAGE_TIME < '{end_ts}' GROUP BY u.NAME ORDER BY TOTAL_CREDITS DESC LIMIT 25
    """), use_container_width=True, hide_index=True)

with tab2:
    st.dataframe(run_query(f"""
    SELECT USER_NAME, ROUND(SUM(TOKEN_CREDITS), 4) AS TOTAL_CREDITS, SUM(TOKENS) AS TOTAL_TOKENS, COUNT(DISTINCT REQUEST_ID) AS REQUESTS
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY
    WHERE START_TIME >= '{start_ts}' AND START_TIME < '{end_ts}' GROUP BY USER_NAME ORDER BY TOTAL_CREDITS DESC LIMIT 25
    """), use_container_width=True, hide_index=True)

with tab3:
    st.dataframe(run_query(f"""
    SELECT u.NAME AS USER_NAME, ROUND(SUM(h.CREDITS), 4) AS TOTAL_CREDITS, COUNT(DISTINCT h.QUERY_ID) AS QUERIES
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_FUNCTIONS_USAGE_HISTORY h LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.USERS u ON h.USER_ID = u.USER_ID
    WHERE h.START_TIME >= '{start_ts}' AND h.START_TIME < '{end_ts}' GROUP BY u.NAME ORDER BY TOTAL_CREDITS DESC LIMIT 25
    """), use_container_width=True, hide_index=True)

with tab4:
    st.dataframe(run_query(f"""
    SELECT u.NAME AS USER_NAME, ROUND(SUM(h.TOKEN_CREDITS), 4) AS TOTAL_CREDITS, SUM(h.TOKENS) AS TOTAL_TOKENS, COUNT(DISTINCT h.REQUEST_ID) AS REQUESTS
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_SNOWSIGHT_USAGE_HISTORY h LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.USERS u ON h.USER_ID = u.USER_ID
    WHERE h.USAGE_TIME >= '{start_ts}' AND h.USAGE_TIME < '{end_ts}' GROUP BY u.NAME ORDER BY TOTAL_CREDITS DESC LIMIT 25
    """), use_container_width=True, hide_index=True)

with tab5:
    st.dataframe(run_query(f"""
    SELECT u.NAME AS USER_NAME, ROUND(SUM(h.TOKEN_CREDITS), 4) AS TOTAL_CREDITS, SUM(h.TOKENS) AS TOTAL_TOKENS, COUNT(DISTINCT h.REQUEST_ID) AS REQUESTS
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_CLI_USAGE_HISTORY h LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.USERS u ON h.USER_ID = u.USER_ID
    WHERE h.USAGE_TIME >= '{start_ts}' AND h.USAGE_TIME < '{end_ts}' GROUP BY u.NAME ORDER BY TOTAL_CREDITS DESC LIMIT 25
    """), use_container_width=True, hide_index=True)

##########
#Users by Highest Service/Cost

st.markdown("---")
st.subheader("Highest Cost-per-Request by User")

#Query
user_eff_sql = f"""
WITH aisql AS (
    SELECT u.NAME AS user_name, 'AISQL Functions' AS service, ROUND(SUM(h.TOKEN_CREDITS), 6) AS total_credits, COUNT(DISTINCT h.QUERY_ID) AS total_requests
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY h
    LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.USERS u ON TRY_CAST(h.USER_ID AS NUMBER) = u.USER_ID
    WHERE h.USAGE_TIME >= '{start_ts}' AND h.USAGE_TIME < '{end_ts}'
    GROUP BY u.NAME
),
agent AS (
    SELECT USER_NAME, 'Cortex Agents', ROUND(SUM(TOKEN_CREDITS), 6), COUNT(DISTINCT REQUEST_ID)
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY
    WHERE START_TIME >= '{start_ts}' AND START_TIME < '{end_ts}'
    GROUP BY USER_NAME
),
ai_func AS (
    SELECT u.NAME, 'AI Functions', ROUND(SUM(h.CREDITS), 6), COUNT(DISTINCT h.QUERY_ID)
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_FUNCTIONS_USAGE_HISTORY h
    LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.USERS u ON h.USER_ID = u.USER_ID
    WHERE h.START_TIME >= '{start_ts}' AND h.START_TIME < '{end_ts}'
    GROUP BY u.NAME
),
code_ss AS (
    SELECT u.NAME, 'Cortex Code (Snowsight)', ROUND(SUM(h.TOKEN_CREDITS), 6), COUNT(DISTINCT h.REQUEST_ID)
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_SNOWSIGHT_USAGE_HISTORY h
    LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.USERS u ON h.USER_ID = u.USER_ID
    WHERE h.USAGE_TIME >= '{start_ts}' AND h.USAGE_TIME < '{end_ts}'
    GROUP BY u.NAME
),
code_cli AS (
    SELECT u.NAME, 'Cortex Code (CLI)', ROUND(SUM(h.TOKEN_CREDITS), 6), COUNT(DISTINCT h.REQUEST_ID)
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_CLI_USAGE_HISTORY h
    LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.USERS u ON h.USER_ID = u.USER_ID
    WHERE h.USAGE_TIME >= '{start_ts}' AND h.USAGE_TIME < '{end_ts}'
    GROUP BY u.NAME
)
SELECT * FROM aisql UNION ALL SELECT * FROM agent UNION ALL SELECT * FROM ai_func
UNION ALL SELECT * FROM code_ss UNION ALL SELECT * FROM code_cli
"""

df_user_eff = run_query(user_eff_sql)
#Clean the dataframe
df_user_eff.columns = ["USER_NAME", "SERVICE", "TOTAL_CREDITS", "TOTAL_REQUESTS"]
df_user_eff["TOTAL_CREDITS"] = df_user_eff["TOTAL_CREDITS"].fillna(0)
df_user_eff["TOTAL_REQUESTS"] = df_user_eff["TOTAL_REQUESTS"].fillna(0).astype(int)
df_user_eff = df_user_eff[df_user_eff["TOTAL_REQUESTS"] > 0]
df_user_eff["COST_PER_REQUEST"] = (df_user_eff["TOTAL_CREDITS"] / df_user_eff["TOTAL_REQUESTS"]).round(6)
df_user_eff = df_user_eff.sort_values("COST_PER_REQUEST", ascending=False).head(20)

#Bar chart and table
if not df_user_eff.empty:
    df_user_eff["LABEL"] = df_user_eff["USER_NAME"].fillna("Unknown") + " (" + df_user_eff["SERVICE"] + ")"
    user_chart = alt.Chart(df_user_eff).mark_bar().encode(
        x=alt.X("COST_PER_REQUEST:Q", title="Credits per Request"),
        y=alt.Y("LABEL:N", sort="-x", title=""),
        #color=alt.Color("SERVICE:N", title="Service"),
        color=alt.Color("SERVICE:N", title="Service", scale=alt.Scale(domain=list(service_colors.keys()), range=list(service_colors.values()))),
        tooltip=["USER_NAME", "SERVICE", "TOTAL_CREDITS", "TOTAL_REQUESTS", "COST_PER_REQUEST"]
    ).properties(height=400)
    st.altair_chart(user_chart, use_container_width=True)
    st.dataframe(df_user_eff[["USER_NAME", "SERVICE", "TOTAL_CREDITS", "TOTAL_REQUESTS", "COST_PER_REQUEST"]].reset_index(drop=True), use_container_width=True, hide_index=True)
else:
    st.info("No user request data in selected period.")
