# Smart City Dashboard — Deployment

## What this package contains
- `streamlit_app.py` — complete 5-page interactive dashboard
- `requirements.txt` — Python dependencies
- `.streamlit/config.toml` — dark dashboard theme
- Required AQI, Energy and Traffic datasets
- Original Power BI `.pbix` and dashboard screenshots for portfolio reference

## Important
The Streamlit app recreates the interactive dashboard in Python. The `.pbix` file is kept as the original Power BI source/reference; Streamlit Cloud does not execute the PBIX file.

The original project also contains very large hourly CSV files. They are not needed by this deployed app, so do not upload them to the GitHub deployment repository.

## Streamlit Community Cloud
1. Create a GitHub repository and upload the contents of this folder.
2. Open Streamlit Community Cloud.
3. Choose **Create app**.
4. Select the GitHub repository and branch.
5. Set the main file to `streamlit_app.py`.
6. Deploy.
7. Copy the resulting `streamlit.app` URL into your resume.
