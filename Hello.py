#
import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
import time
from utils import GetSharepointSpread, VersionInfo

LOGGER = get_logger(__name__)
## SET PAGE GLOBALS

if "login_accepted" not in st.session_state:
    st.session_state.login_accepted = False

uci_logo_link = (
    "https://www.logolynx.com/images/logolynx/4f/4f42c461be2388aca949521bbb6a64f1.gif"
)
vinfo = VersionInfo()


# login function
def login_allowed(pwd_input, check_against):
    if pwd_input == check_against:
        st.session_state.login_accepted = True
    else:
        error_container = st.empty()
        with error_container:
            st.error("🚨 Password Incorrect")
            time.sleep(1)
            error_container.empty()


## sidebar
def display_sidebar():
    # Sidebar Configuration
    st.sidebar.image(
        uci_logo_link,
        use_column_width=True,
    )
    st.sidebar.markdown("# PBG Communications Tracker")
    st.sidebar.markdown(
        "Log in to view details, trends, and more in PBG Denials outreach communications based on the [PBG Outreach Communications Tracker](https://forms.office.com/Pages/ResponsePage.aspx?id=dGqfIFMJpE2HKkcxkbtXXRlSdRAEP7dEuq-wuAKx0INUMzVXNVJCWE01MU5VVldYTkNaNzQwVDNPWS4u)"
    )
    st.sidebar.markdown(f"Version: `{vinfo.version}`")
    st.sidebar.divider()


def view_filtered_spreadData(df, start_date, end_date):
    c1, c2 = st.columns(2)
    dept_list = set(df["Department"].to_list())
    managers_list = set(df["Name"].to_list())
    column_list = ['Name','Department','Denial Issue','Clinic or Site']

    filter_by = c1.selectbox(label="Filter/Search By:",options=column_list,key="spread_tab")
    filter_opts = set(df[filter_by].to_list())

    filter_selection = c2.multiselect(label="Show results for: ",options=filter_opts,default=filter_opts)

    # display filtered dataframe
    #view_as_table = st.toggle("View as Table",False)
    view_as_sel = st.radio("View as: ",["List","Table","Pivot"],horizontal=True)
    view_df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date) & (df[filter_by].isin(filter_selection))]
    #st.title("View Data")
    if len(view_df) > 0 and view_as_sel =="Table":
        st.dataframe(
            view_df,
            use_container_width=True,
            column_order=[
                "Date",
                "Name",
                "Department",
                'Clinic or Site'
                "Denial Issue",
                "Meeting Attendees",
                "Summary",
            ],
            hide_index=True,
        )
    elif len(view_df) > 0 and view_as_sel == "List":
        for index,row in view_df.iterrows():
            msg = f"""##### {row["Department"]} ({row["Date"]})"""
            attendees = f"Meeting Attendees: {row['Meeting Attendees']}"
            desc = f"Summary: {row['Summary']}"
            inf = msg + "\n\n" + f"Issue: {row['Denial Issue']}" + "\n\n" + f"Manager: {row['Name']}" + "\n\n" + desc
            st.info(inf)
            # with st.expander(msg, expanded=False):
            #     st.info(f"##### **Department:** {row['Department']}")
            #     st.info(f"###### **Manager:** {row['Name']}")
            #     #st.divider()
            #     st.warning(f"**Issue:** {row['Denial Issue']}")
            #     st.success(f"**Summary:** {row['Summary']}")
    elif len(view_df) > 0 and view_as_sel == "Pivot":
        piv = pd.pivot_table(view_df,index=['Name'],columns=['Date'],values=["Denial Issue","Summary"],aggfunc="sum")
        st.table(piv)
    else:
        st.warning("No data to display ... please adjust filters",icon="⚠️")




def view_trends(df, start_date, end_date):
    column_list = ['Name','Department','Denial Issue','Clinic or Site']
    view_by = st.selectbox(label="Filter/Search By:",options=column_list)
    other_cols = [i for i in column_list if i != view_by]

    view_df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
    view_df.rename(columns={"ID":"Count"},inplace=True)
    
    chart_data = view_df.groupby([view_by],as_index=False).count()
    # chart_data["Count"] = chart_data[view_by].count()
    # st.dataframe(chart_data)
    st.header(f"Total Meetings by {view_by}")
    st.bar_chart(chart_data,x=view_by,y="Count",use_container_width=True)

    st.header(f"Trends in {view_by} Over Time")
    linePlt_data = view_df.groupby(["Date"],as_index=False).count()
    new_df = pd.get_dummies(view_df,dtype=int,columns=column_list)
    # linePlt_data["Date"] = linePlt_data

    plt_cols = [col for col in new_df if col.startswith(view_by)]
    plt_cols_mapper = {c:str(c.split("_")[-1]) for c in plt_cols}

    # st.write(plt_cols_mapper)

    new_df.rename(columns=plt_cols_mapper,inplace=True)
    new_plt_cols = plt_cols_mapper.values()

    # st.dataframe(new_df)
    st.line_chart(new_df,x="Date",y=new_plt_cols)





    



# create organization of main dashboard to display
def display_dashboard():
    with st.spinner("Collecting Data ..."):
        df = GetSharepointSpread(
            "Form1",
            url=st.secrets["URL"],
            username=st.secrets["USERNAME"],
            password=st.secrets["PWD"],
        )

    # set up data and filter options
    df["Date"] = pd.to_datetime(df["Date of Meeting or Outreach"]).dt.date

    # set up columns for filter options
    c1, c2, c3, c4 = st.columns(4)
    #c1.subheader("Meeting Dates")
    start_date, end_date = st.slider(
        "Meeting Dates:", 
        min(df["Date"]), 
        max(df["Date"]),
        (min(df["Date"]), max(df["Date"])),
        label_visibility="visible",
        format="M/d/YY"
    )
    # start_date = c2.date_input(
    #     "Start Date",
    #     min_value=min(df["Date"]),
    #     max_value=max(df["Date"]),
    #     value=min(df["Date"]),
    # )
    # end_date = c3.date_input(
    #     "End Date",
    #     min_value=min(df["Date"]),
    #     max_value=max(df["Date"]),
    #     value=max(df["Date"]),
    # )

    tab1, tab2 = st.tabs(["🔎 View Spreadsheet", "📊 View Trends"])
    with tab1:
        # st.dataframe(df)
        view_filtered_spreadData(df, start_date, end_date)
    with tab2:
        view_trends(df,start_date,end_date)


def run():
    # set page config
    st.set_page_config(
        page_title="PBG Communications Tracker",
        page_icon=uci_logo_link,
        layout="wide",
        menu_items={
            "Report a Bug": "mailto:colbyr@hs.uci.edu",
            "About": vinfo.description,
        },
    )

    display_sidebar()

    main_container = st.container()

    with main_container:
        st.title("PBG Communications Tracker")
        if not st.session_state.login_accepted:
            c1, c2, c3 = st.columns([1, 4, 1])
            login_box = c2.text_input("Enter Password: ", type="password")
            btype = "secondary" if login_box =="" else "primary"
            login_button = c2.button(
                "Login",
                on_click=login_allowed,
                args=(login_box, st.secrets["SITE_PWD"]),
                use_container_width=True,
                type=btype
            )
        else:
            display_dashboard()


if __name__ == "__main__":
    run()
