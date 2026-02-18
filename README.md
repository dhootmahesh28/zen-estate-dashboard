# 🏢 Zen Estate Financial Dashboard

A professional, interactive financial dashboard built with Streamlit for tracking revenue, expenses, and wing/shop-wise analysis for Zen Estate property management.

![Dashboard Preview](https://img.shields.io/badge/Status-Live-success)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-red)

## 🌟 Features

- 📊 **Real-time Data Upload**: Upload Excel files and see instant visualizations
- 💰 **Monthly Revenue Tracking**: Compare "To Be Received" vs "Received" amounts
- 🏘️ **Wing/Shop Analysis**: Track pending and excess payments by location
- 📈 **Trend Analysis**: Visualize financial trends over time
- 📥 **Export Reports**: Download data in CSV format
- 🎨 **Interactive Charts**: Built with Plotly for dynamic, responsive visualizations
- 📱 **Mobile Responsive**: Works perfectly on all devices

## 🚀 Live Demo

**Dashboard URL**: [Your Streamlit Cloud URL here]

## 📋 Prerequisites

- Python 3.8 or higher
- Excel file with the following structure:
  - Sheet3 containing monthly billing data
  - Wing/Shop columns (A Wing, A Shop, B Wing, etc.)
  - Monthly data for September, October, November

## 🛠️ Installation

### Local Setup

1. Clone this repository:
```bash
git clone https://github.com/your-username/zen-estate-dashboard.git
cd zen-estate-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the dashboard:
```bash
streamlit run app.py
```

4. Open your browser to `http://localhost:8501`

## ☁️ Cloud Deployment

This dashboard is deployed on **Streamlit Cloud** (FREE forever).

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

### Quick Deploy:
1. Fork this repository
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect your GitHub account
4. Select this repository
5. Deploy!

## 📊 Dashboard Sections

### 1. Key Metrics
- Total To Be Received
- Total Received
- Collection Rate
- Wings with Pending Payments

### 2. Monthly Overview
- Bar chart comparing To Be vs Received
- Line chart showing trends
- Detailed data table

### 3. Wing/Shop Analysis
- Color-coded visualization (Red = Pending, Green = Excess)
- Summary of pending and excess amounts
- Detailed data table with color coding

### 4. Export Features
- Download monthly summary as CSV
- Download wing data as CSV

## 📁 File Structure

```
zen-estate-dashboard/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── DEPLOYMENT_GUIDE.md      # Detailed deployment instructions
└── README.md                # This file
```

## 🔧 Configuration

### Customizing Colors

Edit the color codes in `app.py`:
```python
# Line ~60 - Chart colors
'#1f77b4'  # Blue - To Be Received
'#2ca02c'  # Green - Received/Excess
'#d62728'  # Red - Pending
```

### Adding New Visualizations

The code is modular. Add new charts by creating functions similar to:
```python
def create_new_chart(df):
    fig = go.Figure()
    # Your chart code here
    return fig
```

## 📊 Data Format

Your Excel file should have:

**Sheet3 Structure:**
- Row 21-23: September data (To Be, Received, Difference)
- Row 26-28: October data
- Row 31-33: November data
- Columns: One for each Wing/Shop

Example:
```
             A Wing    B Wing    C Wing    ...
To Be        100000    150000    120000
Received     98000     152000    120000
Difference   -2000     2000      0
```

## 🔒 Security & Privacy

- ✅ All data processing happens in-memory
- ✅ No files are permanently stored
- ✅ Each user session is isolated
- ✅ HTTPS encryption on Streamlit Cloud
- ✅ No data is stored in GitHub repository

## 🆘 Troubleshooting

### Common Issues:

**Issue**: Dashboard doesn't load
- **Solution**: Check if all dependencies are in `requirements.txt`

**Issue**: Charts not displaying
- **Solution**: Verify your Excel file format matches the expected structure

**Issue**: Wrong data showing
- **Solution**: Ensure Sheet3 exists and has data in correct rows (21-23, 26-28, 31-33)

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👥 Authors

- **Claude AI Assistant** - Initial development

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Charts powered by [Plotly](https://plotly.com/)
- Data processing with [Pandas](https://pandas.pydata.org/)

## 📞 Support

For support:
- Open an issue in this repository
- Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed help
- Visit [Streamlit Documentation](https://docs.streamlit.io)

## 🗺️ Roadmap

- [ ] Add more months dynamically
- [ ] Implement vendor expense breakdown
- [ ] Add email notifications for pending payments
- [ ] Create PDF report generation
- [ ] Add user authentication
- [ ] Multi-year comparison views

## 📸 Screenshots

*Add your dashboard screenshots here once deployed*

---

**Made with ❤️ for Zen Estate Management**

**Star ⭐ this repository if you find it helpful!**
