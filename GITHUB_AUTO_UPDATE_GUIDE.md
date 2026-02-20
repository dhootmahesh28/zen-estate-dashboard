# 🚀 Setup Guide: Auto-Update Dashboard from GitHub

## 📋 Overview
Your dashboard will now:
- ✅ Load Excel file **automatically** from GitHub
- ✅ Update **instantly** when you commit changes to Excel
- ✅ Look like a **professional website** (no upload button)
- ✅ Work for anyone with the URL (but data source is controlled by you)

---

## 🔧 Setup Steps

### Step 1: Upload Excel File to GitHub

1. **Go to your repository**: `https://github.com/dhootmahesh28/zen-estate-dashboard`

2. **Click "Add file" → "Upload files"**

3. **Upload your Excel file**: `Zen_Estate_Combined_Expenses_Q1.xlsx`

4. **Commit** with message: "Add Excel data file"

### Step 2: Get the Raw File URL

1. **Click on the Excel file** in your repo

2. **Click "Raw" button** (top right of file view)

3. **Copy the URL** - it will look like:
   ```
   https://raw.githubusercontent.com/dhootmahesh28/zen-estate-dashboard/master/Zen_Estate_Combined_Expenses_Q1.xlsx
   ```

4. **Important**: Make sure the URL has:
   - `raw.githubusercontent.com` (NOT `github.com`)
   - `/master/` or `/main/` (your branch name)

### Step 3: Update app.py with Your URL

1. **Open app.py** in your repo

2. **Find line ~20** (the GITHUB_EXCEL_URL line)

3. **Replace** the URL with YOUR actual URL:
   ```python
   GITHUB_EXCEL_URL = "https://raw.githubusercontent.com/dhootmahesh28/zen-estate-dashboard/master/Zen_Estate_Combined_Expenses_Q1.xlsx"
   ```

4. **Commit changes**

### Step 4: Update requirements.txt

1. **Open requirements.txt** in your repo

2. **Replace** all content with:
   ```
   streamlit>=1.28.0
   pandas>=2.0.0
   plotly>=5.17.0
   openpyxl>=3.1.0
   numpy>=1.24.0
   requests>=2.31.0
   ```

3. **Commit changes**

### Step 5: Wait for Deployment

- Streamlit Cloud will auto-deploy (2-3 minutes)
- Your dashboard will now load data automatically!

---

## 🔄 How to Update Data (Going Forward)

### Every time you want to update the dashboard:

1. **Update your Excel file** locally on your computer

2. **Go to GitHub repo** → Click on the Excel file

3. **Click "Edit" (pencil icon)** or delete and re-upload

4. **Commit changes** with a message like: "Update financial data for Feb 2026"

5. **Wait ~1 minute** - Dashboard auto-updates!

### That's it! No need to:
- ❌ Re-deploy anything
- ❌ Upload through Streamlit
- ❌ Touch the code

Just **commit the Excel file** and the dashboard updates automatically! 🎉

---

## 🌐 Professional Website Features

### What Changed:

**Before:**
- Sidebar with file upload
- Manual upload required
- "Upload your file" messages

**After:**
- ✅ Clean, professional layout
- ✅ Auto-loads on page open
- ✅ Loading spinner while fetching data
- ✅ Looks like a real website
- ✅ Anyone can view (but only you can update data)

### How It Works:

1. **User opens dashboard** → Sees loading spinner
2. **Dashboard fetches Excel** from GitHub automatically
3. **Data displays** immediately
4. **User sees** professional charts and tables
5. **No upload interface** visible

---

## 🔒 Security & Access Control

### Current Setup (Public Dashboard):
- ✅ Anyone with URL can **view** the dashboard
- ✅ Only you can **update** data (via GitHub)
- ✅ Excel file is in your GitHub repo

### Want to Make it Private?

If you want to restrict who can view the dashboard:

**Option 1: Password Protection (Free)**
Add authentication to the Streamlit app:
```python
import streamlit as st

def check_password():
    def password_entered():
        if st.session_state["password"] == "YOUR_PASSWORD_HERE":
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if check_password():
    # Your dashboard code here
    main()
```

**Option 2: Streamlit Cloud Authentication**
- Upgrade to Streamlit Pro ($20/month)
- Add email-based authentication
- Control who can access

**Option 3: Keep GitHub Private**
- Your GitHub repo is already public
- To make it private: Repo Settings → Change visibility → Private
- Then use a GitHub personal access token in the code

---

## 🎨 Customization Options

### 1. Change the Excel File Name

If your Excel file has a different name:

1. Rename it in GitHub OR
2. Update the URL in app.py to match your filename

### 2. Add Loading Message

Want to customize the loading message?

**In app.py, line ~291:**
```python
with st.spinner('Loading latest data from repository...'):
```

Change to:
```python
with st.spinner('Loading Zen Estate Financial Data...'):
```

### 3. Add Footer

Add this at the end of `main()` function:
```python
st.markdown("---")
st.markdown("**Zen Estate Management** | Last Updated: Auto-synced from GitHub")
```

### 4. Add Refresh Button

Want users to manually refresh?
```python
if st.button('🔄 Refresh Data'):
    st.cache_data.clear()
    st.rerun()
```

---

## 🐛 Troubleshooting

### Problem: "Error loading data from GitHub"

**Solutions:**
1. **Check the URL** - Make sure it's the RAW URL
2. **Check file exists** - Go to the URL in browser, should download
3. **Check repo is public** - Private repos need authentication
4. **Check filename** - Must match exactly (case-sensitive)

### Problem: "404 Not Found"

**Solutions:**
1. Branch might be `main` not `master` - check your GitHub
2. Update URL: `.../main/...` instead of `.../master/...`

### Problem: Data not updating

**Solutions:**
1. **Clear cache**: Add `st.cache_data.clear()` and redeploy
2. **Hard refresh**: Ctrl+Shift+R in browser
3. **Wait**: GitHub can take 1-2 minutes to update

### Problem: Old data showing

**Solution:**
The dashboard caches data for performance. To force refresh:
1. Change something in app.py (add a space)
2. Commit the change
3. Streamlit will redeploy and clear cache

---

## 📊 File Structure

Your GitHub repo should look like:
```
zen-estate-dashboard/
├── app.py                              # Dashboard code
├── requirements.txt                     # Python packages
├── Zen_Estate_Combined_Expenses_Q1.xlsx # Your data file ⭐
├── README.md                            # Documentation
└── .streamlit/
    └── config.toml                      # Streamlit config
```

---

## 🎯 Best Practices

### 1. Keep Backups
- Keep a local copy of your Excel file
- GitHub stores version history automatically

### 2. Use Clear Commit Messages
```
✅ Good: "Update Jan 2026 financial data"
❌ Bad: "update"
```

### 3. Test Locally First
Before committing:
1. Update Excel locally
2. Test formulas work
3. Then upload to GitHub

### 4. Regular Updates
- Update monthly when new data is available
- Keep the Excel structure consistent
- Don't change column positions

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Excel file is in GitHub repo
- [ ] Raw URL works (opens/downloads file in browser)
- [ ] app.py has correct URL
- [ ] requirements.txt has `requests>=2.31.0`
- [ ] Streamlit app deployed successfully
- [ ] Dashboard loads without upload button
- [ ] All charts display correctly
- [ ] Data matches your Excel file

---

## 🎉 You're Done!

Your dashboard is now:
- ✅ Professional-looking
- ✅ Auto-updating
- ✅ Easy to maintain
- ✅ Shareable with anyone

**Just update the Excel file in GitHub, and the dashboard updates automatically!**

---

## 📞 Need Help?

If you run into issues:
1. Check the Streamlit logs (Manage app → View logs)
2. Verify the GitHub URL works in your browser
3. Make sure requirements.txt is updated
4. Try a hard refresh (Ctrl+Shift+R)

---

**Last Updated**: February 2026
**Dashboard URL**: https://zen-estate-financial-dashboard.streamlit.app
**GitHub Repo**: https://github.com/dhootmahesh28/zen-estate-dashboard
