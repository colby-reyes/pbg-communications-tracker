

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import io
import pandas as pd
from dataclasses import dataclass
import streamlit as st

@dataclass
class VersionInfo:
    version = "1.0.0"
    description = """`PBG Communications Tracker` version 1.0.0"""
    author = "Colby Reyes"
    contact = "colbyr@hs.uci.edu"


#@st.cache_data(show_spinner=False)
def GetSharepointSpread(
    sheetname: str,
    url: str = st.secrets["URL"],
    username: str = st.secrets["USERNAME"],
    password: str = st.secrets["PWD"],
):

    ctx_auth = AuthenticationContext(url)
    if ctx_auth.acquire_token_for_user(username, password):
        ctx = ClientContext(url, ctx_auth)
        # web = ctx.web
        # ctx.load(web)
        ctx.execute_query()
        print("Authentication successful")

    response = File.open_binary(ctx, url)

    # %% save data to BytesIO stream
    bytes_file_obj = io.BytesIO()
    bytes_file_obj.write(response.content)
    bytes_file_obj.seek(0)  # set file object to start

    # %% read excel file and each sheet into pandas dataframe
    
    df = pd.read_excel(bytes_file_obj, sheet_name=sheetname)
    return df


