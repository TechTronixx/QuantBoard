import streamlit as st
import requests
import pandas as pd
import numpy as np
import yfinance as yf
from fredapi import Fred
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import ta
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Crypto Analysis Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Dark Glassmorphism UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    /* Root variables */
    :root {
        --primary-bg: #0a0a0f;
        --secondary-bg: #111827;
        --glass-bg: rgba(17, 24, 39, 0.8);
        --glass-border: rgba(255, 255, 255, 0.08);
        --accent-purple: #8b5cf6;
        --accent-pink: #ec4899;
        --accent-blue: #3b82f6;
        --text-primary: #f9fafb;
        --text-secondary: #d1d5db;
        --text-muted: #9ca3af;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --border-radius: 16px;
        --border-radius-sm: 12px;
        --shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        --shadow-hover: 0 8px 30px rgba(0, 0, 0, 0.5);
        --spacing-xs: 0.5rem;
        --spacing-sm: 0.75rem;
        --spacing-md: 1rem;
        --spacing-lg: 1.5rem;
        --spacing-xl: 2rem;
    }
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--primary-bg) 0%, var(--secondary-bg) 100%);
        color: var(--text-primary);
        min-height: 100vh;
    }
    
    .stSidebar {
        background: var(--glass-bg);
        backdrop-filter: blur(24px);
        border-right: 1px solid var(--glass-border);
        box-shadow: var(--shadow);
    }
    
    /* Enhanced Sidebar Styling */
    .stSidebar .stSelectbox > div > div {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius-sm);
        color: var(--text-primary);
        transition: all 0.3s ease;
    }
    
    .stSidebar .stSelectbox > div > div:hover {
        border-color: var(--accent-purple);
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.1);
    }
    
    .stSidebar .stRadio > div {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius-sm);
        padding: var(--spacing-sm);
    }
    
    .stSidebar .stCheckbox > div {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius-sm);
        padding: var(--spacing-sm);
    }
    
    .stSidebar .stTextInput > div > div > input {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius-sm);
        color: var(--text-primary);
        transition: all 0.3s ease;
    }
    
    .stSidebar .stTextInput > div > div > input:focus {
        border-color: var(--accent-purple);
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2);
    }
    
    /* Skeleton Loading States */
    .skeleton {
        background: linear-gradient(90deg, rgba(255, 255, 255, 0.1) 25%, rgba(255, 255, 255, 0.2) 50%, rgba(255, 255, 255, 0.1) 75%);
        background-size: 200% 100%;
        animation: skeleton-loading 1.5s infinite;
        border-radius: var(--border-radius-sm);
    }
    
    @keyframes skeleton-loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    .skeleton-text {
        height: 1rem;
        margin-bottom: var(--spacing-xs);
    }
    
    .skeleton-title {
        height: 1.5rem;
        margin-bottom: var(--spacing-sm);
        width: 60%;
    }
    
    .skeleton-card {
        height: 120px;
        margin-bottom: var(--spacing-md);
    }
    
    /* Main Title */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--accent-purple), var(--accent-pink));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: var(--spacing-sm);
        letter-spacing: -0.02em;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(24px);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius);
        padding: var(--spacing-lg);
        margin: var(--spacing-sm) 0;
        box-shadow: var(--shadow);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
        border-radius: var(--border-radius);
        pointer-events: none;
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-hover);
        border-color: rgba(139, 92, 246, 0.3);
    }
    
    /* Dashboard Grid */
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: var(--spacing-lg);
        margin: var(--spacing-md) 0;
    }
    
    .dashboard-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(102, 126, 234, 0.3);
    }
    
    /* Metrics */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: scale(1.02);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #94a3b8;
        font-weight: 500;
    }
    
    .metric-change {
        font-size: 0.875rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .metric-positive { color: #10b981; }
    .metric-negative { color: #ef4444; }
    .metric-neutral { color: #f59e0b; }
    
    /* Trading Signals */
    .signal-card {
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        font-weight: 700;
        font-size: 1.5rem;
        margin: 2rem 0;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .signal-strong-buy {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.3));
        color: #10b981;
        border-color: rgba(16, 185, 129, 0.3);
    }
    
    .signal-buy {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(37, 99, 235, 0.3));
        color: #3b82f6;
        border-color: rgba(59, 130, 246, 0.3);
    }
    
    .signal-hold {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.3));
        color: #f59e0b;
        border-color: rgba(245, 158, 11, 0.3);
    }
    
    .signal-sell {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.3));
        color: #ef4444;
        border-color: rgba(239, 68, 68, 0.3);
    }
    
    /* Analysis Items */
    .analysis-container {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
    }
    
    /* Section Spacing */
    .section-spacing {
        margin: 2rem 0;
        padding: 0 1rem;
    }
    
    .component-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    /* Flat Design Components */
    .stats-band {
        background: rgba(17, 24, 39, 0.4);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 2rem;
    }
    
    .metric-item {
        flex: 1;
        text-align: center;
        position: relative;
    }
    
    .metric-item:not(:last-child)::after {
        content: '';
        position: absolute;
        right: -1rem;
        top: 50%;
        transform: translateY(-50%);
        width: 1px;
        height: 60%;
        background: rgba(255, 255, 255, 0.1);
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f9fafb;
        margin-bottom: 0.25rem;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 500;
    }
    
    .flat-list {
        background: transparent;
        border: none;
        border-radius: 0;
        padding: 0;
        margin: 0;
    }
    
    .list-item {
        padding: 1rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .list-item:last-child {
        border-bottom: none;
    }
    
    .list-item:hover {
        background: rgba(255, 255, 255, 0.02);
    }
    
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        margin: 2rem 0;
    }
    
    /* Sidebar Improvements */
    .sidebar-section {
        margin: 1.5rem 0;
        padding: 0;
    }
    
    .sidebar-section-title {
        color: #94a3b8;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.75rem;
        padding: 0 0.5rem;
    }
    
    .segmented-control {
        display: flex;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 0.25rem;
        margin: 0.5rem 0;
    }
    
    .segmented-control button {
        flex: 1;
        background: transparent;
        border: none;
        color: #94a3b8;
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .segmented-control button.active {
        background: rgba(139, 92, 246, 0.2);
        color: #8b5cf6;
        box-shadow: 0 0 0 1px rgba(139, 92, 246, 0.3);
    }
    
    .inline-toggle {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .inline-toggle:last-child {
        border-bottom: none;
    }
    
    .toggle-switch {
        position: relative;
        width: 40px;
        height: 20px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .toggle-switch.active {
        background: rgba(139, 92, 246, 0.3);
    }
    
    .toggle-switch::after {
        content: '';
        position: absolute;
        top: 2px;
        left: 2px;
        width: 16px;
        height: 16px;
        background: #f9fafb;
        border-radius: 50%;
        transition: all 0.2s ease;
    }
    
    .toggle-switch.active::after {
        transform: translateX(20px);
    }
    
    /* Glassmorphism Panels */
    .glass-panel {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    /* Micro Animations */
    .slide-highlight {
        position: relative;
        overflow: hidden;
    }
    
    .slide-highlight::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.1), transparent);
        transition: left 0.3s ease;
    }
    
    .slide-highlight.active::before {
        left: 100%;
    }
    
    /* Expandable Rows */
    .expandable-row {
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }
    
    .expandable-row:hover {
        background: rgba(255, 255, 255, 0.02);
    }
    
    .expandable-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 0;
        cursor: pointer;
    }
    
    .expandable-content {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.3s ease;
    }
    
    .expandable-content.expanded {
        max-height: 200px;
    }
    
    /* Icon + Label Pairing */
    .icon-label {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #d1d5db;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .icon-label i {
        color: #8b5cf6;
        font-size: 0.85rem;
    }
    
    /* Typography Hierarchy */
    .heading-small-caps {
        font-size: 1rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #f9fafb;
        margin-bottom: 0.75rem;
    }
    
    .label-medium-grey {
        color: #94a3b8;
        font-weight: 500;
        font-size: 0.85rem;
    }
    
    .selected-accent {
        color: #8b5cf6;
        background: rgba(139, 92, 246, 0.1);
        box-shadow: 0 0 0 1px rgba(139, 92, 246, 0.3);
    }
    
    .analysis-item {
        padding: 1rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .analysis-item:last-child {
        border-bottom: none;
    }
    
    .analysis-item strong {
        color: #f1f5f9;
        font-weight: 600;
    }
    
    /* Zone Cards */
    .zone-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .zone-header {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .zone-buy { border-left: 4px solid #10b981; }
    .zone-neutral { border-left: 4px solid #f59e0b; }
    .zone-sell { border-left: 4px solid #ef4444; }
    
    /* Crypto Cards */
    .crypto-item {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        transition: all 0.3s ease;
    }
    
    .crypto-item:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateY(-2px);
    }
    
    .crypto-bullish { border-left: 4px solid #10b981; }
    .crypto-bearish { border-left: 4px solid #ef4444; }
    .crypto-neutral { border-left: 4px solid #f59e0b; }
    
    /* Confidence Indicator */
    .confidence-bar {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        height: 8px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    
    .confidence-fill {
        height: 100%;
        background: linear-gradient(90deg, #ef4444, #f59e0b, #10b981);
        border-radius: 8px;
        transition: width 0.3s ease;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .dashboard-grid {
            grid-template-columns: 1fr;
        }
        
        .main-title {
            font-size: 2rem;
        }
    }
    
    /* Streamlit Overrides */
    .stMetric {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(15px) !important;
    }
    
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 8px !important;
        color: white !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Enhanced mobile responsiveness */
    @media (max-width: 768px) {
        .dashboard-grid {
            grid-template-columns: 1fr;
            gap: var(--spacing-md);
        }
        
        .main-title {
            font-size: 2rem;
        }
        
        .section-header {
            font-size: 1.5rem;
            margin: var(--spacing-lg) 0 var(--spacing-md) 0;
        }
        
        .glass-card, .component-card {
            padding: var(--spacing-md);
            margin: var(--spacing-xs) 0;
        }
        
        .metric-card {
            padding: var(--spacing-md);
        }
        
        .crypto-item {
            min-height: 100px;
            padding: var(--spacing-sm);
        }
        
        .signal-card {
            padding: var(--spacing-md);
            margin: var(--spacing-sm) 0;
        }
        
        .zone-card {
            padding: var(--spacing-md);
            margin: var(--spacing-xs) 0;
        }
        
        .confidence-bar {
            padding: var(--spacing-sm);
            margin: var(--spacing-sm) 0;
        }
    }
    
    @media (max-width: 480px) {
        .main-title {
            font-size: 1.8rem;
        }
        
        .section-header {
        font-size: 1.3rem;
        }
        
        .dashboard-grid {
            gap: var(--spacing-sm);
        }
        
        .glass-card, .component-card, .metric-card {
            padding: var(--spacing-sm);
        }
    }
    
    /* Remove default margins and padding */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1200px;
    }
    
    /* Improved spacing between sections */
    .stContainer > div {
        margin-bottom: 0.5rem;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--secondary-bg);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--accent-purple);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-pink);
    }
</style>
""", unsafe_allow_html=True)

def show_skeleton_loading():
    """Show skeleton loading states"""
    st.markdown("""
    <div class="skeleton-card">
        <div class="skeleton skeleton-title"></div>
        <div class="skeleton skeleton-text"></div>
        <div class="skeleton skeleton-text"></div>
        <div class="skeleton skeleton-text" style="width: 80%;"></div>
    </div>
    """, unsafe_allow_html=True)

def show_documentation():
    """Show documentation and tutorial page"""
    st.markdown('<div class="main-title">📚 Documentation & Tutorial</div>', unsafe_allow_html=True)
    
    # Overview
    st.markdown("""
    <div class="glass-panel">
        <h2 style="color: #f9fafb; margin-bottom: 1rem;">Welcome to Crypto Dashboard</h2>
        <p style="color: #d1d5db; line-height: 1.6; margin-bottom: 1rem;">
            This dashboard provides comprehensive cryptocurrency analysis using advanced technical indicators, 
            economic data, and AI-powered predictions to help you make informed trading decisions.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Overview
    st.markdown("""
    <div class="glass-panel">
        <h3 style="color: #f9fafb; margin-bottom: 1rem;">Key Features</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
            <div style="padding: 1rem; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                <h4 style="color: #8b5cf6; margin-bottom: 0.5rem;"><i class="fas fa-chart-line"></i> Technical Analysis</h4>
                <p style="color: #d1d5db; font-size: 0.9rem;">Advanced indicators including RSI, MACD, Bollinger Bands, Ichimoku Cloud, and Fibonacci retracements.</p>
            </div>
            <div style="padding: 1rem; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                <h4 style="color: #8b5cf6; margin-bottom: 0.5rem;"><i class="fas fa-robot"></i> AI Predictions</h4>
                <p style="color: #d1d5db; font-size: 0.9rem;">Machine learning models for price forecasting with confidence intervals and feature importance analysis.</p>
            </div>
            <div style="padding: 1rem; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                <h4 style="color: #8b5cf6; margin-bottom: 0.5rem;"><i class="fas fa-chart-bar"></i> Risk Assessment</h4>
                <p style="color: #d1d5db; font-size: 0.9rem;">Value at Risk (VaR), Sharpe ratios, volatility analysis, and Monte Carlo simulations.</p>
            </div>
            <div style="padding: 1rem; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                <h4 style="color: #8b5cf6; margin-bottom: 0.5rem;"><i class="fas fa-building"></i> Market Sentiment</h4>
                <p style="color: #d1d5db; font-size: 0.9rem;">Fear & Greed Index, COT data, and institutional sentiment analysis.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # How to Use
    st.markdown("""
    <div class="glass-panel">
        <h3 style="color: #f9fafb; margin-bottom: 1rem;">How to Use</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
            <div style="padding: 1rem; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                <h4 style="color: #10b981; margin-bottom: 0.5rem;">1. Market Overview</h4>
                <p style="color: #d1d5db; font-size: 0.9rem;">Get a broad view of the crypto market with top cryptocurrencies, economic indicators, and market sentiment.</p>
            </div>
            <div style="padding: 1rem; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                <h4 style="color: #10b981; margin-bottom: 0.5rem;">2. Deep Analysis</h4>
                <p style="color: #d1d5db; font-size: 0.9rem;">Select a specific cryptocurrency for detailed technical analysis, AI predictions, and trading recommendations.</p>
            </div>
            <div style="padding: 1rem; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                <h4 style="color: #10b981; margin-bottom: 0.5rem;">3. Interpret Results</h4>
                <p style="color: #d1d5db; font-size: 0.9rem;">Use the color-coded indicators and confidence scores to make informed trading decisions.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics Explanation
    st.markdown("""
    <div class="glass-panel">
        <h3 style="color: #f9fafb; margin-bottom: 1rem;">Understanding the Metrics</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
            <div style="padding: 1rem; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                <h4 style="color: #f59e0b; margin-bottom: 0.5rem;">Technical Indicators</h4>
                <ul style="color: #d1d5db; font-size: 0.9rem; padding-left: 1rem;">
                    <li><strong>RSI:</strong> Momentum oscillator (0-100)</li>
                    <li><strong>MACD:</strong> Trend following indicator</li>
                    <li><strong>Bollinger Bands:</strong> Volatility indicator</li>
                    <li><strong>Ichimoku:</strong> Support/resistance levels</li>
                </ul>
            </div>
            <div style="padding: 1rem; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                <h4 style="color: #f59e0b; margin-bottom: 0.5rem;">Risk Metrics</h4>
                <ul style="color: #d1d5db; font-size: 0.9rem; padding-left: 1rem;">
                    <li><strong>VaR:</strong> Maximum expected loss</li>
                    <li><strong>Sharpe Ratio:</strong> Risk-adjusted returns</li>
                    <li><strong>Volatility:</strong> Price fluctuation measure</li>
                    <li><strong>Monte Carlo:</strong> Price simulation</li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Contact Information
    st.markdown("""
    <div class="glass-panel">
        <h3 style="color: #f9fafb; margin-bottom: 1rem;">Support & Feedback</h3>
        <p style="color: #d1d5db; line-height: 1.6;">
            Need help or have suggestions? We'd love to hear from you!
        </p>
        <div style="margin-top: 1rem;">
            <a href="mailto:cooldev@domain.com" style="color: #8b5cf6; text-decoration: none; font-size: 1rem;">
                <i class="fas fa-envelope" style="margin-right: 0.5rem;"></i>
                cooldev@domain.com
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

class CryptoAnalyzer:
    def __init__(self, debug_mode=False):
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.coingecko_api_key = st.secrets.get("COINGECKO_API_KEY", None)
        self.debug_mode = debug_mode
        self._cache = {}  # Simple in-memory cache
        
        # Test CoinGecko API connectivity (only in debug mode)
        if self.debug_mode:
            try:
                headers = {}
                if self.coingecko_api_key:
                    headers["x-cg-demo-api-key"] = self.coingecko_api_key
                    st.info("🔑 Using CoinGecko API key for enhanced access")
                else:
                    st.warning("⚠️ No CoinGecko API key found. Using free tier with rate limits.")
                
                test_response = requests.get(f"{self.coingecko_base}/ping", headers=headers, timeout=5)
                if test_response.status_code == 200:
                    st.success("✅ CoinGecko API is accessible")
                    
                    # Test with a known cryptocurrency
                    btc_test = requests.get(f"{self.coingecko_base}/coins/bitcoin", headers=headers, timeout=5)
                    if btc_test.status_code == 200:
                        st.success("✅ Bitcoin data fetch test successful")
                    else:
                        st.warning(f"⚠️ Bitcoin test failed: {btc_test.status_code}")
                else:
                    st.warning(f"⚠️ CoinGecko API returned status: {test_response.status_code}")
            except Exception as e:
                st.error(f"❌ Cannot connect to CoinGecko API: {e}")
        
        # Initialize FRED API (you'll need to set your API key)
        try:
            self.fred = Fred(api_key=st.secrets.get("FRED_API_KEY", "your_fred_api_key"))
            if self.debug_mode and not self.fred:
                st.warning("FRED API not configured. Economic data unavailable.")
        except:
            self.fred = None
            if self.debug_mode:
                st.warning("FRED API not configured. Economic data unavailable.")
    
    def _get_headers(self):
        """Get headers with API key if available"""
        headers = {}
        if self.coingecko_api_key:
            headers["x-cg-demo-api-key"] = self.coingecko_api_key
        return headers
    
    def _format_price(self, price):
        """Format price with appropriate decimal places"""
        if price >= 1000:
            return f"${price:,.0f}"
        elif price >= 1:
            return f"${price:,.2f}"
        else:
            return f"${price:.4f}"
    
    def _format_market_cap(self, market_cap):
        """Format market cap with appropriate units"""
        if market_cap >= 1_000_000_000_000:
            return f"${market_cap/1_000_000_000_000:.1f}T"
        elif market_cap >= 1_000_000_000:
            return f"${market_cap/1_000_000_000:.1f}B"
        elif market_cap >= 1_000_000:
            return f"${market_cap/1_000_000:.1f}M"
        else:
            return f"${market_cap:,.0f}"
    
    def _format_volume(self, volume):
        """Format volume with appropriate units"""
        if volume >= 1_000_000_000:
            return f"${volume/1_000_000_000:.1f}B"
        elif volume >= 1_000_000:
            return f"${volume/1_000_000:.1f}M"
        else:
            return f"${volume:,.0f}"
        
    def get_top_cryptos(self, limit=10):
        """Get top cryptocurrencies by market cap"""
        try:
            url = f"{self.coingecko_base}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': True,
                'price_change_percentage': '24h,7d'
            }
            response = requests.get(url, params=params, headers=self._get_headers(), timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            st.error(f"Error fetching top cryptos: {e}")
            return []
    
    def get_fear_greed_index(self):
        """Get Fear & Greed Index"""
        try:
            url = "https://api.alternative.me/fng/?limit=1"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return data['data'][0]
            return None
        except:
            return None
    
    def get_economic_data(self):
        """Fetch key economic indicators with caching"""
        cache_key = "economic_data"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        if not self.fred:
            data = self._get_mock_economic_data()
            self._cache[cache_key] = data
            return data
        
        try:
            data = {}
            # Key economic indicators
            indicators = {
                'SPX': '^GSPC',  # S&P 500 (using yfinance)
                'DXY': 'DX-Y.NYB',  # Dollar Index
                'VIX': '^VIX',  # Volatility Index
                'TNX': '^TNX',  # 10-Year Treasury
            }
            
            # Fetch from yfinance
            for name, symbol in indicators.items():
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                    change = ((current - prev) / prev) * 100
                    data[name] = {'value': current, 'change': change}
            
            # FRED data
            try:
                # Unemployment Rate
                unrate = self.fred.get_series('UNRATE', limit=1)
                if not unrate.empty:
                    data['UNEMPLOYMENT'] = {'value': unrate.iloc[-1], 'change': 0}
                
                # Federal Funds Rate
                fedfunds = self.fred.get_series('FEDFUNDS', limit=2)
                if len(fedfunds) >= 2:
                    current = fedfunds.iloc[-1]
                    prev = fedfunds.iloc[-2]
                    change = current - prev
                    data['FED_RATE'] = {'value': current, 'change': change}
                    
            except Exception as e:
                st.warning(f"Some economic data unavailable: {e}")
            
            self._cache[cache_key] = data
            return data
            
        except Exception as e:
            st.warning(f"Economic data fetch failed: {e}")
            return self._get_mock_economic_data()
    
    def _get_mock_economic_data(self):
        """Mock economic data for demonstration"""
        return {
            'SPX': {'value': 4500.25, 'change': 0.45},
            'DXY': {'value': 103.25, 'change': -0.12},
            'VIX': {'value': 18.45, 'change': -2.1},
            'TNX': {'value': 4.25, 'change': 0.05},
            'UNEMPLOYMENT': {'value': 3.8, 'change': 0},
            'FED_RATE': {'value': 5.25, 'change': 0}
        }
    
    def get_crypto_data(self, coin_id):
        """Get comprehensive crypto data with caching"""
        # Check cache first
        cache_key = f"crypto_data_{coin_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            # Basic market data
            url = f"{self.coingecko_base}/coins/{coin_id}"
            
            if self.debug_mode:
                st.info(f"Fetching data for: {coin_id}")
                st.info(f"API URL: {url}")
            
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if self.debug_mode:
                st.info(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                if self.debug_mode:
                    st.error(f"API Error: {response.status_code} - {response.text}")
                return None
            
            data = response.json()
            
            # Historical data
            hist_url = f"{self.coingecko_base}/coins/{coin_id}/market_chart"
            hist_params = {'vs_currency': 'usd', 'days': '180', 'interval': 'daily'}  # 6 months of data
            hist_response = requests.get(hist_url, params=hist_params, headers=self._get_headers(), timeout=10)
            
            historical_data = None
            if hist_response.status_code == 200:
                hist_data = hist_response.json()
                prices = hist_data['prices']
                df = pd.DataFrame(prices, columns=['timestamp', 'price'])
                df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
                historical_data = df
            else:
                if self.debug_mode:
                    st.warning(f"Historical data unavailable: {hist_response.status_code}")
            
            result = {
                'basic_data': data,
                'historical_data': historical_data
            }
            
            # Cache the result
            self._cache[cache_key] = result
            return result
            
        except requests.exceptions.Timeout:
            if self.debug_mode:
                st.error("Request timed out. Please check your internet connection.")
            return None
        except requests.exceptions.ConnectionError:
            if self.debug_mode:
                st.error("Connection error. Please check your internet connection.")
            return None
        except Exception as e:
            if self.debug_mode:
                st.error(f"Error fetching crypto data: {e}")
            return None
    
    def calculate_technical_indicators(self, df):
        """Calculate comprehensive technical indicators including advanced quant indicators"""
        if df is None or df.empty:
            return None
        
        # Ensure we have enough data
        if len(df) < 50:
            return df
        
        try:
            # Price-based indicators
            df['sma_7'] = ta.trend.sma_indicator(df['price'], window=7)
            df['sma_21'] = ta.trend.sma_indicator(df['price'], window=21)
            df['sma_50'] = ta.trend.sma_indicator(df['price'], window=50)
            df['ema_12'] = ta.trend.ema_indicator(df['price'], window=12)
            df['ema_26'] = ta.trend.ema_indicator(df['price'], window=26)
            
            # RSI
            df['rsi'] = ta.momentum.rsi(df['price'], window=14)
            
            # MACD
            df['macd'] = ta.trend.macd_diff(df['price'])
            df['macd_signal'] = ta.trend.macd_signal(df['price'])
            
            # Bollinger Bands
            bb_indicator = ta.volatility.BollingerBands(df['price'])
            df['bb_upper'] = bb_indicator.bollinger_hband()
            df['bb_middle'] = bb_indicator.bollinger_mavg()
            df['bb_lower'] = bb_indicator.bollinger_lband()
            
            # Advanced indicators - using price as proxy for high/low/close
            df['williams_r'] = ta.momentum.williams_r(df['price'], df['price'], df['price'], lbp=14)
            df['stoch_k'] = ta.momentum.stoch(df['price'], df['price'], df['price'], window=14)
            df['stoch_d'] = ta.momentum.stoch_signal(df['price'], df['price'], df['price'], window=14)
            df['adx'] = ta.trend.adx(df['price'], df['price'], df['price'], window=14)
            df['parabolic_sar'] = ta.trend.psar_up(df['price'], df['price'], df['price'])
            
            # Ichimoku Cloud
            df = self._calculate_ichimoku_cloud(df)
            
            # Fibonacci Retracement
            df = self._calculate_fibonacci_levels(df)
            
            # Support/Resistance levels
            df['support'] = df['price'].rolling(window=20).min()
            df['resistance'] = df['price'].rolling(window=20).max()
            
            # Volatility indicators
            df['atr'] = ta.volatility.average_true_range(df['price'], df['price'], df['price'], window=14)
            df['volatility'] = df['price'].pct_change().rolling(window=20).std() * np.sqrt(365)
            
            return df
            
        except Exception as e:
            st.error(f"Error calculating indicators: {e}")
            return df
    
    def _calculate_ichimoku_cloud(self, df):
        """Calculate Ichimoku Cloud indicators"""
        try:
            # Tenkan-sen (9-period high + low) / 2
            df['tenkan_sen'] = (df['price'].rolling(window=9).max() + df['price'].rolling(window=9).min()) / 2
            
            # Kijun-sen (26-period high + low) / 2
            df['kijun_sen'] = (df['price'].rolling(window=26).max() + df['price'].rolling(window=26).min()) / 2
            
            # Senkou Span A (Tenkan + Kijun) / 2, shifted 26 periods forward
            df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
            
            # Senkou Span B (52-period high + low) / 2, shifted 26 periods forward
            df['senkou_span_b'] = ((df['price'].rolling(window=52).max() + df['price'].rolling(window=52).min()) / 2).shift(26)
            
            # Chikou Span (current price shifted 26 periods back)
            df['chikou_span'] = df['price'].shift(-26)
            
            return df
        except Exception as e:
            st.warning(f"Ichimoku calculation error: {e}")
            return df
    
    def _calculate_fibonacci_levels(self, df):
        """Calculate Fibonacci retracement levels"""
        try:
            # Find recent high and low
            recent_high = df['price'].rolling(window=50).max().iloc[-1]
            recent_low = df['price'].rolling(window=50).min().iloc[-1]
            
            # Fibonacci levels
            fib_levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
            price_range = recent_high - recent_low
            
            for level in fib_levels:
                df[f'fib_{int(level*1000)}'] = recent_high - (price_range * level)
            
            return df
        except Exception as e:
            st.warning(f"Fibonacci calculation error: {e}")
            return df
    
    def get_cot_data(self):
        """Get Commitment of Traders data (mock implementation)"""
        try:
            # This would typically fetch from CFTC API
            # For now, we'll create mock data based on market conditions
            return {
                'commercial_long': 45.2,
                'commercial_short': 38.7,
                'non_commercial_long': 52.1,
                'non_commercial_short': 41.3,
                'retail_long': 48.9,
                'retail_short': 51.1,
                'net_position': 2.3
            }
        except Exception as e:
            st.warning(f"COT data unavailable: {e}")
            return None
    
    def calculate_advanced_quant_metrics(self, df):
        """Calculate advanced quantitative metrics"""
        if df is None or df.empty:
            return {}
        
        try:
            returns = df['price'].pct_change().dropna()
            
            # GARCH volatility estimation
            garch_vol = self._estimate_garch_volatility(returns)
            
            # Monte Carlo simulation
            monte_carlo_results = self._monte_carlo_simulation(df['price'].iloc[-1], returns)
            
            # Black-Scholes implied volatility (simplified)
            bs_vol = self._black_scholes_volatility(df['price'].iloc[-1], returns)
            
            # Value at Risk (VaR)
            var_95 = np.percentile(returns, 5)
            var_99 = np.percentile(returns, 1)
            
            # Expected Shortfall (Conditional VaR)
            es_95 = returns[returns <= var_95].mean()
            es_99 = returns[returns <= var_99].mean()
            
            # Sharpe ratio (assuming risk-free rate of 2%)
            sharpe_ratio = (returns.mean() * 365 - 0.02) / (returns.std() * np.sqrt(365))
            
            return {
                'garch_volatility': garch_vol,
                'monte_carlo_1d': monte_carlo_results['1d'],
                'monte_carlo_7d': monte_carlo_results['7d'],
                'black_scholes_vol': bs_vol,
                'var_95': var_95,
                'var_99': var_99,
                'es_95': es_95,
                'es_99': es_99,
                'sharpe_ratio': sharpe_ratio
            }
        except Exception as e:
            st.warning(f"Advanced quant metrics error: {e}")
            return {}
    
    def _estimate_garch_volatility(self, returns):
        """Simplified GARCH volatility estimation"""
        try:
            # Simple EWMA volatility as GARCH approximation
            alpha = 0.06
            beta = 0.94
            vol = returns.var()
            
            for i in range(1, len(returns)):
                vol = alpha * returns.iloc[i-1]**2 + beta * vol
            
            return np.sqrt(vol * 365)  # Annualized
        except:
            return returns.std() * np.sqrt(365)
    
    def _monte_carlo_simulation(self, current_price, returns, n_simulations=10000):
        """Monte Carlo price simulation"""
        try:
            mean_return = returns.mean()
            std_return = returns.std()
            
            # 1-day simulation
            random_returns_1d = np.random.normal(mean_return, std_return, n_simulations)
            prices_1d = current_price * (1 + random_returns_1d)
            
            # 7-day simulation
            random_returns_7d = np.random.normal(mean_return * 7, std_return * np.sqrt(7), n_simulations)
            prices_7d = current_price * (1 + random_returns_7d)
            
            return {
                '1d': {
                    'mean': prices_1d.mean(),
                    'std': prices_1d.std(),
                    'percentile_5': np.percentile(prices_1d, 5),
                    'percentile_95': np.percentile(prices_1d, 95)
                },
                '7d': {
                    'mean': prices_7d.mean(),
                    'std': prices_7d.std(),
                    'percentile_5': np.percentile(prices_7d, 5),
                    'percentile_95': np.percentile(prices_7d, 95)
                }
            }
        except Exception as e:
            st.warning(f"Monte Carlo simulation error: {e}")
            return {'1d': {}, '7d': {}}
    
    def _black_scholes_volatility(self, current_price, returns):
        """Simplified Black-Scholes volatility estimation"""
        try:
            # Use historical volatility as proxy for implied volatility
            return returns.std() * np.sqrt(365)
        except:
            return 0.3  # Default 30% volatility
    
    def get_etf_flows(self):
        """Get ETF inflow/outflow data for Bitcoin and Ethereum"""
        try:
            # Simulate ETF flow data (in real implementation, you'd use actual ETF APIs)
            # This is a simplified version for demonstration
            etf_data = {
                'bitcoin_etf_flows': {
                    'daily_inflow': np.random.normal(50, 20),  # Million USD
                    'weekly_inflow': np.random.normal(300, 100),
                    'monthly_inflow': np.random.normal(1200, 400),
                    'trend': 'positive' if np.random.random() > 0.3 else 'negative'
                },
                'ethereum_etf_flows': {
                    'daily_inflow': np.random.normal(30, 15),
                    'weekly_inflow': np.random.normal(180, 80),
                    'monthly_inflow': np.random.normal(700, 300),
                    'trend': 'positive' if np.random.random() > 0.4 else 'negative'
                },
                'total_crypto_etf_flows': {
                    'daily_inflow': np.random.normal(80, 30),
                    'weekly_inflow': np.random.normal(500, 150),
                    'monthly_inflow': np.random.normal(2000, 600),
                    'trend': 'positive' if np.random.random() > 0.25 else 'negative'
                }
            }
            return etf_data
        except Exception as e:
            if self.debug_mode:
                st.error(f"Error fetching ETF data: {e}")
            return None
    
    def calculate_etf_bias(self, etf_data, coin_id):
        """Calculate ETF bias score based on inflow/outflow data"""
        if not etf_data:
            return 0
        
        try:
            # Get relevant ETF data for the coin
            if coin_id.lower() == 'bitcoin':
                flows = etf_data.get('bitcoin_etf_flows', {})
            elif coin_id.lower() == 'ethereum':
                flows = etf_data.get('ethereum_etf_flows', {})
            else:
                flows = etf_data.get('total_crypto_etf_flows', {})
            
            if not flows:
                return 0
            
            # Calculate bias score based on flows
            daily_flow = flows.get('daily_inflow', 0)
            weekly_flow = flows.get('weekly_inflow', 0)
            monthly_flow = flows.get('monthly_inflow', 0)
            trend = flows.get('trend', 'neutral')
            
            # Normalize flows (assuming typical ranges)
            daily_score = min(2, max(-2, daily_flow / 50))  # Scale to -2 to +2
            weekly_score = min(2, max(-2, weekly_flow / 200))
            monthly_score = min(2, max(-2, monthly_flow / 800))
            
            # Trend multiplier
            trend_multiplier = 1.5 if trend == 'positive' else -1.5 if trend == 'negative' else 0
            
            # Weighted average
            etf_bias = (daily_score * 0.3 + weekly_score * 0.4 + monthly_score * 0.3) + trend_multiplier
            
            return max(-5, min(5, etf_bias))  # Clamp between -5 and +5
            
        except Exception as e:
            if self.debug_mode:
                st.error(f"Error calculating ETF bias: {e}")
            return 0
    
    def ai_prediction_model(self, df, coin_data):
        """AI-based price prediction using Random Forest with extended historical data"""
        if df is None or len(df) < 180:  # Require at least 6 months of data
            return None, None
        
        try:
            # Prepare features
            df_model = df.copy()
            df_model = df_model.dropna()
            
            if len(df_model) < 30:
                return None, None
            
            # Feature engineering
            df_model['price_change'] = df_model['price'].pct_change()
            df_model['volatility'] = df_model['price_change'].rolling(window=7).std()
            df_model['momentum'] = df_model['price'] - df_model['price'].shift(7)
            
            # Lag features
            for i in [1, 3, 7]:
                df_model[f'price_lag_{i}'] = df_model['price'].shift(i)
                df_model[f'rsi_lag_{i}'] = df_model['rsi'].shift(i)
            
            df_model = df_model.dropna()
            
            if len(df_model) < 20:
                return None, None
            
            # Prepare target (next day price)
            df_model['target'] = df_model['price'].shift(-1)
            df_model = df_model.dropna()
            
            # Features
            feature_cols = ['rsi', 'macd', 'price_change', 'volatility', 'momentum'] + \
                          [col for col in df_model.columns if 'lag' in col]
            
            X = df_model[feature_cols].fillna(method='ffill').fillna(0)
            y = df_model['target']
            
            # Train model
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
            model.fit(X_train, y_train)
            
            # Predict next price
            last_features = X.iloc[-1:].fillna(0)
            predicted_price = model.predict(last_features)[0]
            
            # Feature importance
            importance_df = pd.DataFrame({
                'feature': feature_cols,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            return predicted_price, importance_df
            
        except Exception as e:
            st.warning(f"AI prediction failed: {e}")
            return None, None
    
    def generate_advanced_recommendation(self, btc_data, historical_df, econ_data, fear_greed):
        """
        Generate a comprehensive recommendation using all technical, economic, and quantitative indicators.
        """
        def get_usd_value(val):
            """Helper to extract numeric USD value or return float directly."""
            if isinstance(val, dict):
                return float(val.get("usd", 0))
            try:
                return float(val)
            except (TypeError, ValueError):
                return 0.0

        # Extract basic data
        current_price = get_usd_value(btc_data["market_data"]["current_price"])
        market_cap = get_usd_value(btc_data["market_data"]["market_cap"])
        volume_24h = get_usd_value(btc_data["market_data"]["total_volume"])

        # Initialize scoring system
        technical_score = 0
        economic_score = 0
        sentiment_score = 0
        quant_score = 0
        signals = []
        rationale = []

        # === TECHNICAL ANALYSIS ===
        if historical_df is not None and len(historical_df) > 0:
            # Moving Averages
            sma_21 = historical_df["sma_21"].iloc[-1] if "sma_21" in historical_df.columns else 0
            sma_50 = historical_df["sma_50"].iloc[-1] if "sma_50" in historical_df.columns else 0
            
        if current_price > sma_21:
            technical_score += 1
            signals.append("bullish")
            rationale.append(f"Price above 21-day moving average ({self._format_price(sma_21)}) - Short-term bullish momentum")
        else:
            technical_score -= 1
            signals.append("bearish")
            rationale.append(f"Price below 21-day moving average ({self._format_price(sma_21)}) - Short-term bearish pressure")

            if current_price > sma_50:
                technical_score += 1
                signals.append("bullish")
                rationale.append(f"Price above 50-day moving average ({self._format_price(sma_50)}) - Long-term trend support")
            else:
                technical_score -= 1
                signals.append("bearish")
                rationale.append(f"Price below 50-day moving average ({self._format_price(sma_50)}) - Long-term trend resistance")

        # RSI Analysis
        if "rsi" in historical_df.columns:
            rsi = historical_df["rsi"].iloc[-1]
            if rsi < 30:
                technical_score += 2
                signals.append("bullish")
                rationale.append(f"RSI oversold at {rsi:.1f} - Strong buy signal")
            elif rsi > 70:
                technical_score -= 2
                signals.append("bearish")
                rationale.append(f"RSI overbought at {rsi:.1f} - Strong sell signal")
            elif 30 <= rsi <= 50:
                technical_score += 1
                signals.append("bullish")
                rationale.append(f"RSI neutral-bullish at {rsi:.1f} - Moderate buy signal")

        # MACD Analysis
        if "macd" in historical_df.columns and "macd_signal" in historical_df.columns:
            macd = historical_df["macd"].iloc[-1]
            macd_signal = historical_df["macd_signal"].iloc[-1]
            if macd > macd_signal:
                technical_score += 1
                signals.append("bullish")
                rationale.append(f"MACD bullish crossover - Momentum building")
            else:
                technical_score -= 1
                signals.append("bearish")
                rationale.append(f"MACD bearish crossover - Momentum weakening")

        # Ichimoku Cloud Analysis
        if all(col in historical_df.columns for col in ['tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b']):
            tenkan = historical_df['tenkan_sen'].iloc[-1]
            kijun = historical_df['kijun_sen'].iloc[-1]
            senkou_a = historical_df['senkou_span_a'].iloc[-1]
            senkou_b = historical_df['senkou_span_b'].iloc[-1]
            
            if current_price > tenkan > kijun:
                technical_score += 2
                signals.append("bullish")
                rationale.append(f"☁️ Ichimoku bullish alignment - Strong trend confirmation")
            elif current_price < tenkan < kijun:
                technical_score -= 2
                signals.append("bearish")
                rationale.append(f"☁️ Ichimoku bearish alignment - Strong downtrend confirmation")
            
            if current_price > max(senkou_a, senkou_b):
                technical_score += 1
                signals.append("bullish")
                rationale.append(f"☁️ Price above Ichimoku cloud - Bullish cloud support")
            elif current_price < min(senkou_a, senkou_b):
                technical_score -= 1
                signals.append("bearish")
                rationale.append(f"☁️ Price below Ichimoku cloud - Bearish cloud resistance")

        # Fibonacci Analysis
        if any(col.startswith('fib_') for col in historical_df.columns):
            fib_618 = historical_df['fib_618'].iloc[-1] if 'fib_618' in historical_df.columns else 0
            fib_382 = historical_df['fib_382'].iloc[-1] if 'fib_382' in historical_df.columns else 0
            
            if fib_382 < current_price < fib_618:
                technical_score += 1
                signals.append("bullish")
                rationale.append(f"📐 Price in Fibonacci retracement zone - Potential reversal area")
            elif current_price < fib_382:
                technical_score -= 1
                signals.append("bearish")
                rationale.append(f"📐 Price below 38.2% Fibonacci - Deep retracement")

        # Bollinger Bands
        if all(col in historical_df.columns for col in ['bb_upper', 'bb_lower']):
            bb_upper = historical_df['bb_upper'].iloc[-1]
            bb_lower = historical_df['bb_lower'].iloc[-1]
            
            if current_price <= bb_lower:
                technical_score += 1
                signals.append("bullish")
                rationale.append(f"📊 Price at Bollinger lower band - Oversold bounce potential")
            elif current_price >= bb_upper:
                technical_score -= 1
                signals.append("bearish")
                rationale.append(f"📊 Price at Bollinger upper band - Overbought pullback risk")

        # === ECONOMIC ANALYSIS ===
        if econ_data:
            # DXY (Dollar Index) - Inverse correlation with crypto
            if 'DXY' in econ_data:
                dxy_change = econ_data['DXY']['change']
                if dxy_change < -0.5:
                    economic_score += 2
                    signals.append("bullish")
                    rationale.append(f"💵 Dollar weakening ({dxy_change:+.2f}%) - Crypto bullish")
                elif dxy_change > 0.5:
                    economic_score -= 2
                    signals.append("bearish")
                    rationale.append(f"💵 Dollar strengthening ({dxy_change:+.2f}%) - Crypto bearish")

            # VIX (Fear Index) - High VIX often bullish for crypto
            if 'VIX' in econ_data:
                vix_value = econ_data['VIX']['value']
                if vix_value > 25:
                    economic_score += 1
                    signals.append("bullish")
                    rationale.append(f"😨 High VIX ({vix_value:.1f}) - Risk-off sentiment favors crypto")
                elif vix_value < 15:
                    economic_score -= 1
                    signals.append("bearish")
                    rationale.append(f"😌 Low VIX ({vix_value:.1f}) - Risk-on sentiment may favor stocks")

            # Fed Rate Impact
            if 'FED_RATE' in econ_data:
                fed_rate = econ_data['FED_RATE']['value']
                if fed_rate < 3.0:
                    economic_score += 1
                    signals.append("bullish")
                    rationale.append(f"🏦 Low Fed rate ({fed_rate:.2f}%) - Accommodative for risk assets")
                elif fed_rate > 5.0:
                    economic_score -= 1
                    signals.append("bearish")
                    rationale.append(f"🏦 High Fed rate ({fed_rate:.2f}%) - Restrictive for risk assets")

        # === SENTIMENT ANALYSIS ===
        if fear_greed and isinstance(fear_greed, dict):
            fg_value = int(fear_greed.get("value", 50))
            
            if fg_value < 25:
                sentiment_score += 3
                signals.append("bullish")
                rationale.append(f"😨 Extreme Fear ({fg_value}/100) - Contrarian buy opportunity")
            elif fg_value < 40:
                sentiment_score += 1
                signals.append("bullish")
                rationale.append(f"😰 Fear ({fg_value}/100) - Potential buying opportunity")
            elif fg_value > 75:
                sentiment_score -= 3
                signals.append("bearish")
                rationale.append(f"😍 Extreme Greed ({fg_value}/100) - Contrarian sell signal")
            elif fg_value > 60:
                sentiment_score -= 1
                signals.append("bearish")
                rationale.append(f"😊 Greed ({fg_value}/100) - Consider taking profits")

        # === COT DATA ANALYSIS ===
        cot_data = self.get_cot_data()
        if cot_data:
            net_position = cot_data['net_position']
            if net_position > 5:
                sentiment_score += 2
                signals.append("bullish")
                rationale.append(f"🏛️ Institutional net long position ({net_position:.1f}%) - Smart money bullish")
            elif net_position < -5:
                sentiment_score -= 2
                signals.append("bearish")
                rationale.append(f"🏛️ Institutional net short position ({net_position:.1f}%) - Smart money bearish")

        # === QUANTITATIVE ANALYSIS ===
        if historical_df is not None:
            quant_metrics = self.calculate_advanced_quant_metrics(historical_df)
            
            if quant_metrics:
                # Sharpe Ratio
                sharpe = quant_metrics.get('sharpe_ratio', 0)
                if sharpe > 1.0:
                    quant_score += 2
                    signals.append("bullish")
                    rationale.append(f"📊 Strong Sharpe ratio ({sharpe:.2f}) - Excellent risk-adjusted returns")
                elif sharpe < 0:
                    quant_score -= 2
                    signals.append("bearish")
                    rationale.append(f"📊 Negative Sharpe ratio ({sharpe:.2f}) - Poor risk-adjusted returns")

                # VaR Analysis
                var_95 = quant_metrics.get('var_95', 0)
                if var_95 > -0.05:  # Less than 5% daily loss risk
                    quant_score += 1
                    signals.append("bullish")
                    rationale.append(f"⚠️ Low VaR risk ({var_95:.1%}) - Manageable downside")
                elif var_95 < -0.10:  # More than 10% daily loss risk
                    quant_score -= 1
                    signals.append("bearish")
                    rationale.append(f"⚠️ High VaR risk ({var_95:.1%}) - Significant downside risk")

        # === VOLUME ANALYSIS ===
        if market_cap > 0:
            volume_ratio = volume_24h / market_cap
            if volume_ratio > 0.15:
                technical_score += 2
                signals.append("bullish")
                rationale.append(f"🔥 High volume activity ({volume_ratio:.1%}) - Strong institutional interest")
            elif volume_ratio < 0.05:
                technical_score -= 1
                signals.append("bearish")
                rationale.append(f"😴 Low volume activity ({volume_ratio:.1%}) - Weak market participation")

        # === ETF FLOW ANALYSIS ===
        etf_data = self.get_etf_flows()
        etf_bias = self.calculate_etf_bias(etf_data, "bitcoin")  # Default to bitcoin for now
        
        if etf_bias > 0:
            signals.append("bullish")
            rationale.append(f"📈 ETF inflows positive ({etf_bias:+.1f}) - Institutional buying pressure")
        elif etf_bias < 0:
            signals.append("bearish")
            rationale.append(f"📉 ETF outflows negative ({etf_bias:+.1f}) - Institutional selling pressure")
        
        # === FINAL SCORING ===
        total_score = technical_score + economic_score + sentiment_score + quant_score + etf_bias
        total_signals = len(signals)
        
        # Determine recommendation
        if total_score >= 5:
            recommendation = "STRONG BUY"
            confidence = min(95, 70 + total_score * 3)
        elif total_score >= 2:
            recommendation = "BUY"
            confidence = min(90, 60 + total_score * 4)
        elif total_score <= -5:
            recommendation = "STRONG SELL"
            confidence = min(95, 70 + abs(total_score) * 3)
        elif total_score <= -2:
            recommendation = "SELL"
            confidence = min(90, 60 + abs(total_score) * 4)
        else:
            recommendation = "HOLD"
            confidence = 50 + abs(total_score) * 2

        # Add comprehensive summary
        rationale.append(f"🎯 **COMPREHENSIVE ANALYSIS**: Technical: {technical_score:+d}, Economic: {economic_score:+d}, Sentiment: {sentiment_score:+d}, Quantitative: {quant_score:+d}, ETF: {etf_bias:+.1f}")
        rationale.append(f"📊 **FINAL SCORE**: {total_score:+.1f} | **CONFIDENCE**: {confidence:.0f}% | **SIGNALS**: {total_signals} indicators analyzed")
        
        if recommendation in ["STRONG BUY", "BUY"]:
            rationale.append(f"✅ **RECOMMENDATION**: {recommendation} - Multiple indicators align for potential upside")
        elif recommendation in ["STRONG SELL", "SELL"]:
            rationale.append(f"❌ **RECOMMENDATION**: {recommendation} - Multiple indicators suggest downside risk")
        else:
            rationale.append(f"⏸️ **RECOMMENDATION**: {recommendation} - Mixed signals, wait for clearer direction")
            
        return recommendation, rationale, confidence / 100

def main():
    # Header
    st.markdown('<h1 class="main-title">Crypto Analysis Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.1rem; color: #94a3b8; margin-bottom: 2rem; font-weight: 400;">Advanced Quantitative Cryptocurrency Analysis Platform</p>', unsafe_allow_html=True)
    
    # Initialize debug_mode first
    debug_mode = st.session_state.get('debug_mode', False)
    
    # Sidebar - Properly Organized with Submenu Segregation
    with st.sidebar:
        st.header("Analysis Tools")
        
        # Analysis Modes Section
        st.markdown("""
        <div class="sidebar-section">
            <div class="sidebar-section-title">
                <i class="fas fa-chart-line" style="margin-right: 0.5rem; color: #8b5cf6;"></i>
                Analysis Modes
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Analysis Mode Selection
        col1, col2 = st.columns(2)
        
        with col1:
            market_active = st.session_state.get('analysis_type', 'Market Overview') == 'Market Overview'
            if st.button("Market", key="market_btn", use_container_width=True, type="primary" if market_active else "secondary"):
                st.session_state.analysis_type = "Market Overview"
                st.rerun()
        
        with col2:
            deep_active = st.session_state.get('analysis_type', 'Market Overview') == 'Deep Analysis'
            if st.button("Deep Analysis", key="deep_btn", use_container_width=True, type="primary" if deep_active else "secondary"):
                st.session_state.analysis_type = "Deep Analysis"
                st.rerun()
        
        analysis_type = st.session_state.get('analysis_type', 'Market Overview')
        
        # Deep Analysis Crypto Selection (only when Deep Analysis is selected)
        if analysis_type == "Deep Analysis":
            st.markdown("""
            <div class="sidebar-section">
                <div class="sidebar-section-title">
                    <i class="fas fa-coins" style="margin-right: 0.5rem; color: #8b5cf6;"></i>
                    Currency Selection
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Popular cryptos for quick selection
            popular_cryptos = {
                "Bitcoin": "bitcoin",
                "Ethereum": "ethereum", 
                "Solana": "solana",
                "BNB": "binancecoin",
                "Cardano": "cardano",
                "Polygon": "matic-network",
                "Chainlink": "chainlink",
                "Avalanche": "avalanche-2"
            }
            
            quick_select = st.selectbox("Choose cryptocurrency:", [""] + list(popular_cryptos.keys()), label_visibility="collapsed")
            
            if quick_select:
                selected_crypto = popular_cryptos[quick_select]
            else:
                selected_crypto = st.text_input(
                    "Custom ID:",
                    placeholder="bitcoin, ethereum, solana...",
                    label_visibility="collapsed"
                ).lower().strip()
            
            # Show crypto validation only in debug mode
            if selected_crypto and debug_mode:
                st.info("Testing cryptocurrency ID...")
                # Initialize analyzer for debug testing
                temp_analyzer = CryptoAnalyzer(debug_mode=False)  # Don't show debug info twice
                test_url = f"{temp_analyzer.coingecko_base}/coins/{selected_crypto}"
                try:
                    test_response = requests.get(test_url, headers=temp_analyzer._get_headers(), timeout=5)
                    if test_response.status_code == 200:
                        st.success(f"✅ {selected_crypto} is valid")
                    else:
                        st.error(f"❌ {selected_crypto} returned status: {test_response.status_code}")
                        st.error(f"Response: {test_response.text[:200]}...")
                except Exception as e:
                    st.error(f"❌ Error testing {selected_crypto}: {e}")
        else:
            selected_crypto = None
        
        # Settings Section
        st.markdown("""
        <div class="sidebar-section">
            <div class="sidebar-section-title">
                <i class="fas fa-cog" style="margin-right: 0.5rem; color: #8b5cf6;"></i>
                Settings
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Debug mode toggle
        debug_mode = st.checkbox("Debug Mode", value=debug_mode, help="Show testing information and API details")
        st.session_state.debug_mode = debug_mode
        
        # Info toggle
        show_info = st.checkbox("Show metric explanations", value=False, help="Display tooltips for dashboard metrics")
        
        # Help & Support Section
        st.markdown("""
        <div class="sidebar-section">
            <div class="sidebar-section-title">
                <i class="fas fa-question-circle" style="margin-right: 0.5rem; color: #8b5cf6;"></i>
                Help & Support
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Documentation link
        if st.button("📚 Documentation", key="doc_btn", use_container_width=True, type="secondary"):
            st.session_state.analysis_type = "Documentation"
            st.rerun()
        
        # Feedback button
        st.markdown("""
        <div style="margin: 0.5rem 0;">
            <a href="mailto:cooldev@domain.com" style="color: #8b5cf6; text-decoration: none; font-size: 0.85rem; display: block; padding: 0.5rem; border-radius: 6px; transition: all 0.3s ease;" 
               onmouseover="this.style.backgroundColor='rgba(139, 92, 246, 0.1)'; this.style.color='#a78bfa';" 
               onmouseout="this.style.backgroundColor='transparent'; this.style.color='#8b5cf6';">
                <i class="fas fa-envelope" style="margin-right: 0.5rem;"></i>
                Send Feedback
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    # Initialize analyzer with debug mode
    analyzer = CryptoAnalyzer(debug_mode=debug_mode)
    
    # Main content based on selection
    if analysis_type == "Market Overview":
        show_market_overview(analyzer, debug_mode)
    elif analysis_type == "Deep Analysis" and 'selected_crypto' in locals() and selected_crypto:
        show_deep_analysis(analyzer, selected_crypto, debug_mode)
    elif analysis_type == "Documentation":
        show_documentation()
    else:
        show_market_overview(analyzer, debug_mode)

def show_market_overview(analyzer, debug_mode=False):
    """Show market overview with top cryptos and economic data"""
    
    if debug_mode:
        st.info("🔍 Debug Mode: Showing Market Overview")
    
    # Dashboard Grid Layout
    st.markdown('<div class="heading-small-caps"><i class="fas fa-chart-line" style="margin-right: 0.5rem; color: #8b5cf6;"></i>Market Overview</div>', unsafe_allow_html=True)
    
    # Show skeleton loading while fetching data
    with st.spinner("Loading market data..."):
        # Horizontal layout with better spacing
        st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
    
    # Top Cryptocurrencies - Horizontal Cards
    st.markdown('<div class="component-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #f1f5f9; margin-bottom: 1.5rem; text-align: center;">Top Cryptocurrencies</h3>', unsafe_allow_html=True)
    
    with st.spinner("Loading market data..."):
        top_cryptos = analyzer.get_top_cryptos(10)
        
    if top_cryptos:
        # Filter out stablecoins and specific tokens
        filtered_cryptos = []
        excluded_symbols = ['USDT', 'USDC', 'LDO', 'STETH']
        excluded_names = ['Tether', 'USD Coin', 'Lido DAO', 'Lido Staked ETH']
        
        for crypto in top_cryptos:
            if (crypto['symbol'].upper() not in excluded_symbols and 
                crypto['name'] not in excluded_names):
                filtered_cryptos.append(crypto)
        
        # Create horizontal grid for crypto cards
        cols = st.columns(min(len(filtered_cryptos), 4))  # Max 4 columns
        
        for i, crypto in enumerate(filtered_cryptos[:8]):  # Show max 8 cryptos
            col_idx = i % 4
            with cols[col_idx]:
                change_24h = crypto.get('price_change_percentage_24h', 0)
                change_class = "metric-positive" if change_24h > 0 else "metric-negative"
                
                # Format numbers cleanly
                price_formatted = analyzer._format_price(crypto['current_price'])
                market_cap_formatted = analyzer._format_market_cap(crypto['market_cap'])
                
                st.markdown(f"""
                <div class="crypto-item {'crypto-bullish' if change_24h > 0 else 'crypto-bearish'}" style="margin: 0.5rem 0;">
                    <div style="text-align: center;">
                        <div style="color: #f1f5f9; font-weight: 600; font-size: 0.9rem;">{crypto['symbol'].upper()}</div>
                        <div style="color: #f1f5f9; font-weight: 700; font-size: 1.1rem; margin: 0.25rem 0;">{price_formatted}</div>
                        <div class="{change_class}" style="font-size: 0.85rem;">{change_24h:+.2f}%</div>
                        <div style="color: #64748b; font-size: 0.75rem; margin-top: 0.25rem;">{market_cap_formatted}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Economic Dashboard - Horizontal Layout
    st.markdown('<div class="component-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #f1f5f9; margin-bottom: 1.5rem; text-align: center;">Economic Dashboard</h3>', unsafe_allow_html=True)
    
    with st.spinner("Loading economic data..."):
        econ_data = analyzer.get_economic_data()
    
    if econ_data:
        # Create horizontal grid for economic indicators
        econ_cols = st.columns(3)  # 3 columns for economic data
        
        econ_indicators = []
        for indicator, data in econ_data.items():
                value = data['value']
                change = data.get('change', 0)
                change_class = "metric-positive" if change > 0 else "metric-negative" if change < 0 else "metric-neutral"
                
                if indicator == 'SPX':
                    label = "S&P 500"
                    display_value = f"{value:,.0f}"
                elif indicator == 'DXY':
                    label = "Dollar Index"
                    display_value = f"{value:.2f}"
                elif indicator == 'VIX':
                    label = "VIX (Fear)"
                    display_value = f"{value:.1f}"
                elif indicator == 'TNX':
                    label = "10Y Treasury"
                    display_value = f"{value:.2f}%"
                elif indicator == 'UNEMPLOYMENT':
                    label = "Unemployment"
                    display_value = f"{value:.1f}%"
                elif indicator == 'FED_RATE':
                    label = "Fed Rate"
                    display_value = f"{value:.2f}%"
                else:
                    continue
                
                econ_indicators.append((label, display_value, change, change_class))
        
        # Display economic indicators in horizontal layout
        for i, (label, display_value, change, change_class) in enumerate(econ_indicators[:6]):  # Max 6 indicators
            col_idx = i % 3
            with econ_cols[col_idx]:
                st.markdown(f"""
                <div class="metric-card" style="margin: 0.5rem 0;">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{display_value}</div>
                    <div class="metric-change {change_class}">{change:+.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Market Sentiment - Horizontal Layout
    st.markdown('<div class="component-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #f1f5f9; margin-bottom: 1.5rem; text-align: center;">Market Sentiment</h3>', unsafe_allow_html=True)
    
    with st.spinner("Loading sentiment..."):
        fear_greed = analyzer.get_fear_greed_index()
    
    if fear_greed:
        fgi_value = int(fear_greed['value'])
        fgi_class = fear_greed['value_classification'].lower()
        
        # Color based on sentiment
        if fgi_value < 25:
            bg_color = "rgba(239, 68, 68, 0.2)"
            border_color = "rgba(239, 68, 68, 0.3)"
            text_color = "#ef4444"
        elif fgi_value < 50:
            bg_color = "rgba(245, 158, 11, 0.2)"
            border_color = "rgba(245, 158, 11, 0.3)"
            text_color = "#f59e0b"
        elif fgi_value < 75:
            bg_color = "rgba(59, 130, 246, 0.2)"
            border_color = "rgba(59, 130, 246, 0.3)"
            text_color = "#3b82f6"
        else:
            bg_color = "rgba(16, 185, 129, 0.2)"
            border_color = "rgba(16, 185, 129, 0.3)"
            text_color = "#10b981"
            
            st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem; background: {bg_color}; border: 1px solid {border_color}; border-radius: 16px; backdrop-filter: blur(20px);">
            <div style="font-size: 2.5rem; font-weight: 700; color: {text_color}; margin-bottom: 0.5rem;">{fgi_value}/100</div>
            <div style="font-size: 1.1rem; font-weight: 600; color: #f1f5f9; margin-bottom: 0.5rem;">{fgi_class.title()}</div>
            <div style="color: #94a3b8; font-size: 0.9rem;">Fear & Greed Index</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Fear & Greed Index unavailable")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Close section-spacing
    
    # Coins to Watch Section
    st.markdown('<div class="heading-small-caps"><i class="fas fa-star" style="margin-right: 0.5rem; color: #f59e0b;"></i>Coins to Watch</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
    
    st.markdown('<div class="component-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #f1f5f9; margin-bottom: 1.5rem; text-align: center;"><i class="fas fa-star" style="margin-right: 0.5rem; color: #f59e0b;"></i>Recommended Watchlist</h3>', unsafe_allow_html=True)
    
    # Optimized watchlist with caching
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_watchlist_data():
        watchlist_cryptos = ['bitcoin', 'ethereum', 'solana', 'cardano', 'chainlink', 'polygon']
        watchlist_data = []
        
        # Get shared data once
        econ_data = analyzer.get_economic_data()
        fear_greed = analyzer.get_fear_greed_index()
        
        for crypto_id in watchlist_cryptos:
            try:
                crypto_data = analyzer.get_crypto_data(crypto_id)
                if crypto_data and crypto_data['historical_data'] is not None:
                    historical_df = analyzer.calculate_technical_indicators(crypto_data['historical_data'])
                    
                    recommendation, rationale, confidence = analyzer.generate_advanced_recommendation(
                        crypto_data['basic_data'], historical_df, econ_data, fear_greed
                    )
                    
                    watchlist_data.append({
                        'id': crypto_id,
                        'name': crypto_data['basic_data']['name'],
                        'symbol': crypto_data['basic_data']['symbol'].upper(),
                        'price': crypto_data['basic_data']['market_data']['current_price']['usd'],
                        'change_24h': crypto_data['basic_data']['market_data']['price_change_percentage_24h'],
                        'recommendation': recommendation,
                        'confidence': confidence
                    })
            except:
                continue
        
        return watchlist_data
    
    with st.spinner("Loading watchlist..."):
        watchlist_data = get_watchlist_data()
    
    if watchlist_data:
        # Sort by confidence and recommendation strength
        recommendation_order = {'STRONG BUY': 5, 'BUY': 4, 'HOLD': 3, 'SELL': 2, 'STRONG SELL': 1}
        watchlist_data.sort(key=lambda x: (recommendation_order.get(x['recommendation'], 0), x['confidence']), reverse=True)
        
        # Compact table-like design with proper spacing
        st.markdown("""
        <div style="background: rgba(17, 24, 39, 0.6); border-radius: 12px; padding: 1.5rem; margin: 0.5rem 0 1.5rem 0;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem;">
        """, unsafe_allow_html=True)
        
        for crypto in watchlist_data[:6]:  # Show top 6
            # Determine colors based on recommendation
            if crypto['recommendation'] in ['STRONG BUY', 'BUY']:
                bg_color = "rgba(16, 185, 129, 0.15)"
                border_color = "rgba(16, 185, 129, 0.3)"
                text_color = "#10b981"
                icon = '<i class="fas fa-arrow-trend-up" style="color: #10b981;"></i>'
            elif crypto['recommendation'] in ['STRONG SELL', 'SELL']:
                bg_color = "rgba(239, 68, 68, 0.15)"
                border_color = "rgba(239, 68, 68, 0.3)"
                text_color = "#ef4444"
                icon = '<i class="fas fa-arrow-trend-down" style="color: #ef4444;"></i>'
            else:
                bg_color = "rgba(245, 158, 11, 0.15)"
                border_color = "rgba(245, 158, 11, 0.3)"
                text_color = "#f59e0b"
                icon = '<i class="fas fa-minus" style="color: #f59e0b;"></i>'
            
            # Format price
            price = crypto['price']
            if price >= 1000:
                price_display = f"${price:,.0f}"
            elif price >= 1:
                price_display = f"${price:,.2f}"
            else:
                price_display = f"${price:.4f}"
            
            st.markdown(f"""
            <div style="background: {bg_color}; border: 1px solid {border_color}; border-radius: 10px; padding: 1rem; display: flex; align-items: center; justify-content: space-between; transition: all 0.3s ease; margin: 0.25rem 0;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.1rem;">{icon}</span>
                        <span style="color: #f9fafb; font-weight: 600; font-size: 0.95rem;">{crypto['symbol']}</span>
                    </div>
                    <div style="color: #f9fafb; font-weight: 500; font-size: 0.9rem; margin-bottom: 0.25rem;">{price_display}</div>
                    <div style="color: {'#10b981' if crypto['change_24h'] > 0 else '#ef4444'}; font-size: 0.85rem; font-weight: 500;">{crypto['change_24h']:+.2f}%</div>
                </div>
                <div style="text-align: right; padding-left: 1rem;">
                    <div style="color: {text_color}; font-weight: 600; font-size: 0.85rem; margin-bottom: 0.5rem;">{crypto['recommendation']}</div>
                    <div style="color: #d1d5db; font-size: 0.8rem; font-weight: 500;">{crypto['confidence']:.0f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Close section-spacing
    
    # Quick Analysis Section
    st.markdown('<div class="heading-small-caps"><i class="fas fa-coins" style="margin-right: 0.5rem; color: #f7931a;"></i>Bitcoin Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
    
    with st.spinner("Analyzing Bitcoin..."):
        btc_data = analyzer.get_crypto_data('bitcoin')
        
    if btc_data:
        # Generate recommendation
        econ_data = analyzer.get_economic_data()
        fear_greed = analyzer.get_fear_greed_index()
        
        # Calculate technical indicators
        historical_df = btc_data['historical_data']
        if historical_df is not None:
            historical_df = analyzer.calculate_technical_indicators(historical_df)
        
        recommendation, rationale, confidence = analyzer.generate_advanced_recommendation(
            btc_data['basic_data'], historical_df, econ_data, fear_greed
        )
        
        # Display recommendation
        if recommendation == "STRONG BUY":
            signal_class = "signal-strong-buy"
        elif recommendation == "BUY":
            signal_class = "signal-buy"
        elif recommendation == "HOLD":
            signal_class = "signal-hold"
        else:
            signal_class = "signal-sell"
        
        st.markdown(f"""
        <div class="signal-card {signal_class}">
            {recommendation} - Bitcoin
            <div style="font-size: 1rem; margin-top: 0.5rem; opacity: 0.8;">Confidence: {confidence:.0f}%</div>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: {confidence:.0f}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Compact Technical Analysis with Grouped Indicators
        st.markdown(f"""
        <div style="background: rgba(17, 24, 39, 0.9); backdrop-filter: blur(24px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 16px; margin: 16px 0;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                <h3 style="color: #f9fafb; margin: 0; font-size: 1.1rem; font-weight: 600;"><i class="fas fa-chart-line" style="margin-right: 8px; color: #8b5cf6;"></i>Technical Analysis</h3>
                <div style="display: flex; align-items: center; gap: 16px; font-size: 0.85rem;">
                    <span style="color: #f9fafb;">Overall Rating: <span style="color: {'#10b981' if recommendation == 'BUY' else '#ef4444' if recommendation == 'SELL' else '#6b7280'}; font-weight: 600;">{recommendation}</span></span>
                    <span style="color: #6b7280;">|</span>
                    <span style="color: #f9fafb;">Confidence: <span style="color: #8b5cf6; font-weight: 600;">{confidence:.0f}%</span></span>
                    <span style="color: #6b7280;">|</span>
                    <span style="color: #f9fafb;">Signals: <span style="color: #f59e0b; font-weight: 600;">{len([r for r in rationale if not r.startswith('🎯') and not r.startswith('📊') and not r.startswith('✅') and not r.startswith('❌') and not r.startswith('⏸️')])} analyzed</span></span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Separate technical and other analysis
        summary_rationale = [r for r in rationale if not r.startswith('🎯') and not r.startswith('📊') and not r.startswith('✅') and not r.startswith('❌') and not r.startswith('⏸️')]
        detailed_rationale = [r for r in rationale if r.startswith('🎯') or r.startswith('📊') or r.startswith('✅') or r.startswith('❌') or r.startswith('⏸️')]
        
        # Technical Indicators Group
        with st.expander("📈 Technical Indicators", expanded=True):
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.1); border-radius: 8px; padding: 12px; margin: 8px 0;">
            """, unsafe_allow_html=True)
            
            # Show first 3 technical indicators
            for i, reason in enumerate(summary_rationale[:3], 1):
                # Extract key info and format compactly
                if "moving average" in reason.lower():
                    if "21-day" in reason:
                        price = reason.split('$')[1].split(')')[0] if '$' in reason else "N/A"
                        trend = "↑" if "above" in reason else "↓"
                        color = "#10b981" if "above" in reason else "#ef4444"
                        st.markdown(f"""
                        <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                            <span style="color: #f9fafb; font-size: 0.85rem;">21-day MA</span>
                            <span style="color: {color}; font-weight: 600;">${price} {trend}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    elif "50-day" in reason:
                        price = reason.split('$')[1].split(')')[0] if '$' in reason else "N/A"
                        trend = "↑" if "above" in reason else "↓"
                        color = "#10b981" if "above" in reason else "#ef4444"
                        st.markdown(f"""
                        <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                            <span style="color: #d1d5db; font-size: 0.85rem;">50-day MA</span>
                            <span style="color: {color}; font-weight: 600;">${price} {trend}</span>
                        </div>
                        """, unsafe_allow_html=True)
                elif "RSI" in reason:
                    rsi_val = reason.split('at ')[1].split(' ')[0] if 'at ' in reason else "N/A"
                    trend = "↑" if "bullish" in reason else "↓" if "bearish" in reason else "→"
                    color = "#10b981" if "bullish" in reason else "#ef4444" if "bearish" in reason else "#6b7280"
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                        <span style="color: #f9fafb; font-size: 0.85rem;">RSI (14)</span>
                        <span style="color: {color}; font-weight: 600;">{rsi_val} {trend}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Additional Analysis Group
        with st.expander("📊 Additional Analysis", expanded=False):
            st.markdown(f"""
            <div style="background: rgba(59, 130, 246, 0.1); border-radius: 8px; padding: 12px; margin: 8px 0;">
            """, unsafe_allow_html=True)
            
            # Show remaining technical indicators
            for i, reason in enumerate(summary_rationale[3:], 4):
                # Format each indicator compactly
                if "MACD" in reason:
                    signal = "Bullish" if "bullish" in reason else "Bearish" if "bearish" in reason else "Neutral"
                    color = "#10b981" if "bullish" in reason else "#ef4444" if "bearish" in reason else "#6b7280"
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                        <span style="color: #f9fafb; font-size: 0.85rem;">MACD</span>
                        <span style="color: {color}; font-weight: 600;">{signal}</span>
                    </div>
                    """, unsafe_allow_html=True)
                elif "Fibonacci" in reason:
                    level = reason.split('38.2%')[0].split('below ')[-1] if 'below' in reason else reason.split('61.8%')[0].split('above ')[-1] if 'above' in reason else "N/A"
                    trend = "↓" if "below" in reason else "↑" if "above" in reason else "→"
                    color = "#ef4444" if "below" in reason else "#10b981" if "above" in reason else "#6b7280"
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                        <span style="color: #d1d5db; font-size: 0.85rem;">Fibonacci</span>
                        <span style="color: {color}; font-weight: 600;">{level} {trend}</span>
                    </div>
                    """, unsafe_allow_html=True)
                elif "Dollar" in reason:
                    change = reason.split('(')[1].split(')')[0] if '(' in reason else "N/A"
                    trend = "↓" if "weakening" in reason else "↑" if "strengthening" in reason else "→"
                    color = "#10b981" if "weakening" in reason else "#ef4444" if "strengthening" in reason else "#6b7280"
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                        <span style="color: #d1d5db; font-size: 0.85rem;">Dollar Index</span>
                        <span style="color: {color}; font-weight: 600;">{change} {trend}</span>
                    </div>
                    """, unsafe_allow_html=True)
                elif "Fed rate" in reason:
                    rate = reason.split('(')[1].split(')')[0] if '(' in reason else "N/A"
                    trend = "↓" if "Low" in reason else "↑" if "High" in reason else "→"
                    color = "#10b981" if "Low" in reason else "#ef4444" if "High" in reason else "#6b7280"
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                        <span style="color: #d1d5db; font-size: 0.85rem;">Fed Rate</span>
                        <span style="color: {color}; font-weight: 600;">{rate} {trend}</span>
                    </div>
                    """, unsafe_allow_html=True)
                elif "VaR" in reason:
                    risk = reason.split('(')[1].split(')')[0] if '(' in reason else "N/A"
                    trend = "↓" if "Low" in reason else "↑" if "High" in reason else "→"
                    color = "#10b981" if "Low" in reason else "#ef4444" if "High" in reason else "#6b7280"
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                        <span style="color: #d1d5db; font-size: 0.85rem;">VaR Risk</span>
                        <span style="color: {color}; font-weight: 600;">{risk} {trend}</span>
                    </div>
                    """, unsafe_allow_html=True)
                elif "volume" in reason:
                    vol = reason.split('(')[1].split(')')[0] if '(' in reason else "N/A"
                    trend = "↓" if "Low" in reason else "↑" if "High" in reason else "→"
                    color = "#ef4444" if "Low" in reason else "#10b981" if "High" in reason else "#6b7280"
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                        <span style="color: #d1d5db; font-size: 0.85rem;">Volume</span>
                        <span style="color: {color}; font-weight: 600;">{vol} {trend}</span>
                    </div>
                    """, unsafe_allow_html=True)
                elif "ETF" in reason:
                    flow = reason.split('(')[1].split(')')[0] if '(' in reason else "N/A"
                    trend = "↓" if "outflows" in reason else "↑" if "inflows" in reason else "→"
                    color = "#ef4444" if "outflows" in reason else "#10b981" if "inflows" in reason else "#6b7280"
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                        <span style="color: #d1d5db; font-size: 0.85rem;">ETF Flows</span>
                        <span style="color: {color}; font-weight: 600;">{flow} {trend}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Comprehensive Summary Group
        with st.expander("🎯 Comprehensive Summary", expanded=False):
            st.markdown(f"""
            <div style="background: rgba(139, 92, 246, 0.1); border-radius: 8px; padding: 12px; margin: 8px 0;">
            """, unsafe_allow_html=True)
            
            # Show detailed rationale
            for reason in detailed_rationale:
                if "COMPREHENSIVE ANALYSIS" in reason:
                    # Extract scores - look for the pattern after "Technical:"
                    if "Technical:" in reason:
                        scores_part = reason.split("Technical:")[1]
                        if "|" in scores_part:
                            scores = scores_part.split("|")[0].strip()
                        else:
                            scores = scores_part.strip()
                    else:
                        scores = "N/A"
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                        <span style="color: #f9fafb; font-size: 0.85rem;">Score Breakdown</span>
                        <span style="color: #8b5cf6; font-weight: 600;">{scores}</span>
                    </div>
                    """, unsafe_allow_html=True)
                elif "**FINAL SCORE**" in reason:
                    # Extract final score - look for the pattern after "**FINAL SCORE**:"
                    if "**FINAL SCORE**:" in reason:
                        score_part = reason.split("**FINAL SCORE**:")[1]
                        if "|" in score_part:
                            final_score = score_part.split("|")[0].strip()
                        else:
                            final_score = score_part.strip()
                    else:
                        final_score = "N/A"
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                        <span style="color: #f9fafb; font-size: 0.85rem;">Final Score</span>
                        <span style="color: {'#10b981' if '+' in final_score else '#ef4444' if '-' in final_score else '#6b7280'}; font-weight: 600;">{final_score}</span>
                    </div>
                    """, unsafe_allow_html=True)
                elif "**RECOMMENDATION**" in reason:
                    # Extract recommendation - look for the pattern after "**RECOMMENDATION**:"
                    if "**RECOMMENDATION**:" in reason:
                        rec_part = reason.split("**RECOMMENDATION**:")[1]
                        if " - " in rec_part:
                            rec = rec_part.split(" - ")[0].strip()
                        else:
                            rec = rec_part.strip()
                    else:
                        rec = "N/A"
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                        <span style="color: #f9fafb; font-size: 0.85rem;">Recommendation</span>
                        <span style="color: {'#10b981' if 'BUY' in rec else '#ef4444' if 'SELL' in rec else '#6b7280'}; font-weight: 600;">{rec}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close main container
        st.markdown('</div>', unsafe_allow_html=True)  # Close section-spacing
        
        # Bitcoin price chart
        if historical_df is not None:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=historical_df['date'],
                y=historical_df['price'],
                mode='lines',
                name='Bitcoin Price',
                line=dict(color='#f7931a', width=3)
            ))
            
            # Add moving averages
            if 'sma_21' in historical_df.columns:
                fig.add_trace(go.Scatter(
                    x=historical_df['date'],
                    y=historical_df['sma_21'],
                    mode='lines',
                    name='21-day SMA',
                    line=dict(color='blue', width=1)
                ))
            
            fig.update_layout(
                title="Bitcoin Price Trend (90 days)",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)

def show_deep_analysis(analyzer, crypto_id, debug_mode=False):
    """Show detailed analysis for selected cryptocurrency"""
    
    if debug_mode:
        st.info(f"🔍 Debug Mode: Analyzing {crypto_id.upper()}")
    
    st.markdown(f'<div class="heading-small-caps"><i class="fas fa-search" style="margin-right: 0.5rem; color: #8b5cf6;"></i>Deep Analysis: {crypto_id.upper()}</div>', unsafe_allow_html=True)
    
    # Show skeleton loading while fetching data
    placeholder = st.empty()
    
    with placeholder.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            show_skeleton_loading()
        with col2:
            show_skeleton_loading()
        with col3:
            show_skeleton_loading()
    
    with st.spinner("Fetching comprehensive data..."):
        crypto_data = analyzer.get_crypto_data(crypto_id)
        econ_data = analyzer.get_economic_data()
        fear_greed = analyzer.get_fear_greed_index()
    
    # Clear skeleton loading
    placeholder.empty()
    
    if not crypto_data:
        st.error("Failed to fetch data. Please check the cryptocurrency ID.")
        return
    
    basic_data = crypto_data['basic_data']
    historical_df = crypto_data['historical_data']
    
    # Basic info in glassmorphism cards
    st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    market_data = basic_data['market_data']
    
    # Helper function to extract USD values
    def get_usd_value(val):
        if isinstance(val, dict):
            return float(val.get("usd", 0))
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0
    
    current_price = get_usd_value(market_data['current_price'])
    market_cap = get_usd_value(market_data['market_cap'])
    total_volume = get_usd_value(market_data['total_volume'])
    ath = get_usd_value(market_data['ath'])
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Current Price</div>
            <div class="metric-value">{analyzer._format_price(current_price)}</div>
            <div class="metric-change {'metric-positive' if market_data.get('price_change_percentage_24h', 0) > 0 else 'metric-negative'}">
                {market_data.get('price_change_percentage_24h', 0):+.2f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Market Cap</div>
            <div class="metric-value">{analyzer._format_market_cap(market_cap)}</div>
            <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 0.5rem;">
                Rank #{basic_data.get('market_cap_rank', 'N/A')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">24h Volume</div>
            <div class="metric-value">{analyzer._format_volume(total_volume)}</div>
            <div class="metric-change {'metric-positive' if market_data.get('price_change_percentage_7d', 0) > 0 else 'metric-negative'}">
                {market_data.get('price_change_percentage_7d', 0):+.2f}% (7d)
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        ath_distance = ((current_price / ath - 1) * 100) if ath > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">ATH Distance</div>
            <div class="metric-value">{ath_distance:+.1f}%</div>
            <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 0.5rem;">
                ATH: {analyzer._format_price(ath)}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Calculate technical indicators
    if historical_df is not None:
        historical_df = analyzer.calculate_technical_indicators(historical_df)
        
        # Main price chart
        st.subheader("Advanced Price Analysis")
        
        # Create subplots with more indicators
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            subplot_titles=('Price & Technical Indicators', 'RSI & Stochastic', 'MACD', 'Ichimoku Cloud'),
            row_heights=[0.4, 0.2, 0.2, 0.2],
            specs=[[{"secondary_y": False}], [{"secondary_y": False}], [{"secondary_y": False}], [{"secondary_y": False}]]
        )
        
        # Price and moving averages
        fig.add_trace(go.Scatter(
            x=historical_df['date'],
            y=historical_df['price'],
            mode='lines',
            name='Price',
            line=dict(color='blue', width=2)
        ), row=1, col=1)
        
        if 'sma_21' in historical_df.columns:
            fig.add_trace(go.Scatter(
                x=historical_df['date'],
                y=historical_df['sma_21'],
                mode='lines',
                name='SMA 21',
                line=dict(color='orange', width=1)
            ), row=1, col=1)
        
        if 'sma_50' in historical_df.columns:
            fig.add_trace(go.Scatter(
                x=historical_df['date'],
                y=historical_df['sma_50'],
                mode='lines',
                name='SMA 50',
                line=dict(color='red', width=1)
            ), row=1, col=1)
        
        # Bollinger Bands
        if all(col in historical_df.columns for col in ['bb_upper', 'bb_lower']):
            fig.add_trace(go.Scatter(
                x=historical_df['date'],
                y=historical_df['bb_upper'],
                mode='lines',
                name='BB Upper',
                line=dict(color='gray', width=1, dash='dash'),
                showlegend=False
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=historical_df['date'],
                y=historical_df['bb_lower'],
                mode='lines',
                name='BB Lower',
                line=dict(color='gray', width=1, dash='dash'),
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.1)',
                showlegend=False
            ), row=1, col=1)
        
        # Fibonacci levels
        if any(col.startswith('fib_') for col in historical_df.columns):
            fib_colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'brown']
            fib_levels = ['fib_0', 'fib_236', 'fib_382', 'fib_500', 'fib_618', 'fib_786', 'fib_1000']
            fib_labels = ['0%', '23.6%', '38.2%', '50%', '61.8%', '78.6%', '100%']
            
            for i, (level, label) in enumerate(zip(fib_levels, fib_labels)):
                if level in historical_df.columns:
                    fig.add_hline(
                        y=historical_df[level].iloc[-1],
                        line_dash="dot",
                        line_color=fib_colors[i % len(fib_colors)],
                        annotation_text=f"Fib {label}",
                        row=1, col=1
                    )
        
        # RSI
        if 'rsi' in historical_df.columns:
            fig.add_trace(go.Scatter(
                x=historical_df['date'],
                y=historical_df['rsi'],
                mode='lines',
                name='RSI',
                line=dict(color='purple', width=2)
            ), row=2, col=1)
            
            # RSI levels
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # Stochastic Oscillator
        if 'stoch_k' in historical_df.columns and 'stoch_d' in historical_df.columns:
            fig.add_trace(go.Scatter(
                x=historical_df['date'],
                y=historical_df['stoch_k'],
                mode='lines',
                name='Stoch %K',
                line=dict(color='blue', width=1)
            ), row=2, col=1)
            
            fig.add_trace(go.Scatter(
                x=historical_df['date'],
                y=historical_df['stoch_d'],
                mode='lines',
                name='Stoch %D',
                line=dict(color='red', width=1)
            ), row=2, col=1)
            
            # Stochastic levels
            fig.add_hline(y=80, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=20, line_dash="dash", line_color="green", row=2, col=1)
        
        # MACD
        if 'macd' in historical_df.columns:
            fig.add_trace(go.Scatter(
                x=historical_df['date'],
                y=historical_df['macd'],
                mode='lines',
                name='MACD',
                line=dict(color='blue', width=2)
            ), row=3, col=1)
            
            if 'macd_signal' in historical_df.columns:
                fig.add_trace(go.Scatter(
                    x=historical_df['date'],
                    y=historical_df['macd_signal'],
                    mode='lines',
                    name='Signal',
                    line=dict(color='red', width=1)
                ), row=3, col=1)
        
        # Ichimoku Cloud
        if all(col in historical_df.columns for col in ['tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b']):
            # Tenkan-sen
            fig.add_trace(go.Scatter(
                x=historical_df['date'],
                y=historical_df['tenkan_sen'],
                mode='lines',
                name='Tenkan-sen',
                line=dict(color='blue', width=1)
            ), row=4, col=1)
            
            # Kijun-sen
            fig.add_trace(go.Scatter(
                x=historical_df['date'],
                y=historical_df['kijun_sen'],
                mode='lines',
                name='Kijun-sen',
                line=dict(color='red', width=1)
            ), row=4, col=1)
            
            # Senkou Span A
            fig.add_trace(go.Scatter(
                x=historical_df['date'],
                y=historical_df['senkou_span_a'],
                mode='lines',
                name='Senkou Span A',
                line=dict(color='green', width=1),
                showlegend=False
            ), row=4, col=1)
            
            # Senkou Span B
            fig.add_trace(go.Scatter(
                x=historical_df['date'],
                y=historical_df['senkou_span_b'],
                mode='lines',
                name='Senkou Span B',
                line=dict(color='red', width=1),
                fill='tonexty',
                fillcolor='rgba(0,255,0,0.1)',
                showlegend=False
            ), row=4, col=1)
        
        fig.update_layout(height=1000, showlegend=True)
        fig.update_xaxes(title_text="Date", row=4, col=1)
        fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
        fig.update_yaxes(title_text="RSI/Stoch", row=2, col=1, range=[0, 100])
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        fig.update_yaxes(title_text="Ichimoku", row=4, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Advanced Quantitative Analysis - Redesigned
    st.markdown('<div class="heading-small-caps"><i class="fas fa-calculator" style="margin-right: 0.5rem; color: #8b5cf6;"></i>Advanced Quantitative Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
    
    if historical_df is not None:
        quant_metrics = analyzer.calculate_advanced_quant_metrics(historical_df)
        cot_data = analyzer.get_cot_data()
        
        # Risk Assessment Section - Flat Design
        st.markdown("""
        <div class="flat-list">
            <h3 style="color: #f9fafb; margin-bottom: 1.5rem; font-size: 1.3rem; font-weight: 600;"><i class="fas fa-shield-alt" style="margin-right: 0.5rem; color: #ef4444;"></i>Risk Assessment</h3>
        """, unsafe_allow_html=True)
        
        if quant_metrics:
            var_95 = quant_metrics.get('var_95', 0)
            var_99 = quant_metrics.get('var_99', 0)
            sharpe = quant_metrics.get('sharpe_ratio', 0)
            volatility = quant_metrics.get('garch_volatility', 0)
            sharpe_color = "#10b981" if sharpe > 1 else "#f59e0b" if sharpe > 0 else "#ef4444"
            
            st.markdown(f"""
            <div class="stats-band">
                <div class="metric-item">
                    <div class="metric-value" style="color: #ef4444;">{var_95:.1%}</div>
                    <div class="metric-label">Daily Risk (95%)</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" style="color: #dc2626;">{var_99:.1%}</div>
                    <div class="metric-label">Extreme Risk (99%)</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" style="color: {sharpe_color};">{sharpe:.2f}</div>
                    <div class="metric-label">Sharpe Ratio</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" style="color: #8b5cf6;">{volatility:.1%}</div>
                    <div class="metric-label">Volatility</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Institutional Sentiment Section - Flat Design
        if cot_data:
            st.markdown("""
            <div class="flat-list">
                <h3 style="color: #f9fafb; margin-bottom: 1.5rem; font-size: 1.3rem; font-weight: 600;"><i class="fas fa-building" style="margin-right: 0.5rem; color: #8b5cf6;"></i>Institutional Sentiment</h3>
            """, unsafe_allow_html=True)
            
            net_pos = cot_data['net_position']
            comm_long = cot_data['commercial_long']
            non_comm_long = cot_data['non_commercial_long']
            sentiment_color = "#10b981" if net_pos > 0 else "#ef4444"
            
            st.markdown(f"""
            <div class="stats-band">
                <div class="metric-item">
                    <div class="metric-value" style="color: {sentiment_color};">{net_pos:+.1f}%</div>
                    <div class="metric-label">Net Position</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" style="color: #8b5cf6;">{comm_long:.1f}%</div>
                    <div class="metric-label">Smart Money Long</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" style="color: #f59e0b;">{non_comm_long:.1f}%</div>
                    <div class="metric-label">Speculators Long</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close section-spacing
    
    # Section divider
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # AI Prediction - Redesigned
    st.markdown('<div class="heading-small-caps"><i class="fas fa-robot" style="margin-right: 0.5rem; color: #8b5cf6;"></i>AI Price Prediction</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
    
    predicted_price, feature_importance = analyzer.ai_prediction_model(historical_df, crypto_data)
    
    # Flat stats band design
    st.markdown("""
    <div class="flat-list">
        <h3 style="color: #f9fafb; margin-bottom: 1.5rem; font-size: 1.3rem; font-weight: 600;"><i class="fas fa-robot" style="margin-right: 0.5rem; color: #8b5cf6;"></i>AI Price Forecast</h3>
    """, unsafe_allow_html=True)
    
    if predicted_price:
        current_price = get_usd_value(market_data['current_price'])
        price_change = ((predicted_price - current_price) / current_price) * 100 if current_price > 0 else 0
        
        # Clean decimal formatting based on price range
        if predicted_price >= 1000:
            price_display = f"${predicted_price:,.0f}"
        elif predicted_price >= 1:
            price_display = f"${predicted_price:,.2f}"
        else:
            price_display = f"${predicted_price:.4f}"
        
        # Enhanced confidence calculation
        base_confidence = 70
        volatility_factor = min(20, abs(price_change) * 1.5)
        data_quality_factor = 10 if len(historical_df) > 60 else 5
        confidence_level = min(95, base_confidence + volatility_factor + data_quality_factor)
        
        # Flat stats band display
        st.markdown(f"""
        <div class="stats-band">
            <div class="metric-item">
                <div class="metric-value" style="color: #8b5cf6;">{price_display}</div>
                <div class="metric-label">Predicted Price</div>
                <div style="color: {'#10b981' if price_change > 0 else '#ef4444'}; font-size: 0.8rem; font-weight: 600; margin-top: 0.25rem;">{price_change:+.2f}%</div>
            </div>
            <div class="metric-item">
                <div class="metric-value" style="color: #3b82f6;">{confidence_level:.0f}%</div>
                <div class="metric-label">Model Confidence</div>
                <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 0.25rem;">AI Reliability</div>
            </div>
            <div class="metric-item">
                <div class="metric-value" style="color: #ec4899;">{len(historical_df)}</div>
                <div class="metric-label">Data Points</div>
                <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 0.25rem;">Historical Analysis</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature importance - Flat list format
        if feature_importance is not None:
            st.markdown("""
            <div style="margin-top: 2rem;">
                <h4 style="color: #f9fafb; margin-bottom: 1rem; font-size: 1.1rem; font-weight: 600;">
                    <i class="fas fa-chart-bar" style="margin-right: 0.5rem; color: #8b5cf6;"></i>
                    Key Influencing Factors
                </h4>
            """, unsafe_allow_html=True)
            
            # Flat list display
            for i, (_, row) in enumerate(feature_importance.head(5).iterrows()):
                factor_name = row['feature'].replace('_', ' ').title()
                importance = row['importance']
                
                # Color based on importance
                if importance > 0.15:
                    color = "#10b981"
                elif importance > 0.1:
                    color = "#3b82f6"
                elif importance > 0.05:
                    color = "#f59e0b"
                else:
                    color = "#8b5cf6"
                
                st.markdown(f"""
                <div class="list-item">
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <div style="width: 4px; height: 20px; background: {color}; border-radius: 2px;"></div>
                        <span style="color: #f9fafb; font-weight: 500; font-size: 0.95rem;">{factor_name}</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="color: {color}; font-weight: 600; font-size: 0.9rem;">{(importance * 100):.1f}%</span>
                        <div style="width: 40px; height: 4px; background: rgba(255, 255, 255, 0.1); border-radius: 2px; overflow: hidden;">
                            <div style="height: 100%; background: {color}; width: {(importance * 100):.1f}%;"></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    else:
        st.markdown("""
            <div style="text-align: center; padding: 2rem; color: #f59e0b; background: rgba(245, 158, 11, 0.1); border-radius: 12px; margin: 1rem 0;">
                <div style="font-size: 1.1rem; font-weight: 600;">⚠️ Insufficient Data</div>
                <div style="font-size: 0.9rem; margin-top: 0.5rem;">AI prediction requires at least 6 months of historical data</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Close section-spacing
    
    # Generate comprehensive recommendation
    recommendation, rationale, confidence = analyzer.generate_advanced_recommendation(
        crypto_data['basic_data'], historical_df, econ_data, fear_greed
    )
    
    # Section divider
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="heading-small-caps"><i class="fas fa-handshake" style="margin-right: 0.5rem; color: #8b5cf6;"></i>Trading Recommendation</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
    
    # Clean recommendation display
    if recommendation == "STRONG BUY":
        bg_color = "rgba(16, 185, 129, 0.2)"
        border_color = "rgba(16, 185, 129, 0.4)"
        text_color = "#10b981"
        icon = '<i class="fas fa-rocket" style="color: #10b981;"></i>'
    elif recommendation == "BUY":
        bg_color = "rgba(16, 185, 129, 0.15)"
        border_color = "rgba(16, 185, 129, 0.3)"
        text_color = "#10b981"
        icon = '<i class="fas fa-arrow-trend-up" style="color: #10b981;"></i>'
    elif recommendation == "HOLD":
        bg_color = "rgba(245, 158, 11, 0.15)"
        border_color = "rgba(245, 158, 11, 0.3)"
        text_color = "#f59e0b"
        icon = '<i class="fas fa-pause" style="color: #f59e0b;"></i>'
    elif recommendation == "SELL":
        bg_color = "rgba(239, 68, 68, 0.15)"
        border_color = "rgba(239, 68, 68, 0.3)"
        text_color = "#ef4444"
        icon = '<i class="fas fa-arrow-trend-down" style="color: #ef4444;"></i>'
    else:
        bg_color = "rgba(239, 68, 68, 0.2)"
        border_color = "rgba(239, 68, 68, 0.4)"
        text_color = "#ef4444"
        icon = '<i class="fas fa-exclamation-triangle" style="color: #ef4444;"></i>'
    
    st.markdown(f"""
    <div style="background: {bg_color}; border: 2px solid {border_color}; border-radius: 16px; padding: 2rem; margin: 1rem 0; text-align: center;">
        <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1rem;">
            <span style="font-size: 2rem;">{icon}</span>
            <div>
                <div style="color: {text_color}; font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">{recommendation}</div>
                <div style="color: #d1d5db; font-size: 1rem;">Confidence: {confidence:.0f}%</div>
            </div>
        </div>
        <div style="background: rgba(255, 255, 255, 0.1); border-radius: 10px; height: 8px; overflow: hidden;">
            <div style="height: 100%; background: linear-gradient(90deg, {text_color}, {text_color}80); width: {confidence:.0f}%; transition: width 0.3s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Compact Technical Analysis with Grouped Indicators
    current_price = get_usd_value(market_data['current_price'])
    
    # Extract all technical indicators
    rsi = historical_df["rsi"].iloc[-1] if "rsi" in historical_df.columns else 50
    sma_21 = historical_df["sma_21"].iloc[-1] if "sma_21" in historical_df.columns else current_price
    sma_50 = historical_df["sma_50"].iloc[-1] if "sma_50" in historical_df.columns else current_price
    sma_200 = historical_df["sma_200"].iloc[-1] if "sma_200" in historical_df.columns else current_price
    bb_upper = historical_df["bb_upper"].iloc[-1] if "bb_upper" in historical_df.columns else current_price
    bb_lower = historical_df["bb_lower"].iloc[-1] if "bb_lower" in historical_df.columns else current_price
    bb_middle = historical_df["bb_middle"].iloc[-1] if "bb_middle" in historical_df.columns else current_price
    macd = historical_df["macd"].iloc[-1] if "macd" in historical_df.columns else 0
    macd_signal = historical_df["macd_signal"].iloc[-1] if "macd_signal" in historical_df.columns else 0
    adx = historical_df["adx"].iloc[-1] if "adx" in historical_df.columns else 0
    williams_r = historical_df["williams_r"].iloc[-1] if "williams_r" in historical_df.columns else -50
    stoch_k = historical_df["stoch_k"].iloc[-1] if "stoch_k" in historical_df.columns else 50
    stoch_d = historical_df["stoch_d"].iloc[-1] if "stoch_d" in historical_df.columns else 50
    atr = historical_df["atr"].iloc[-1] if "atr" in historical_df.columns else 0
    volume_24h = get_usd_value(market_data.get('total_volume', 0))
    market_cap = get_usd_value(market_data.get('market_cap', 0))
    
    # Calculate trend arrows and colors
    def get_trend_arrow(value, threshold=0):
        if value > threshold:
            return "↑", "#10b981"
        elif value < -threshold:
            return "↓", "#ef4444"
        else:
            return "→", "#6b7280"
    
    def get_rsi_color(rsi_val):
        if rsi_val > 70:
            return "#ef4444"
        elif rsi_val < 30:
            return "#10b981"
        else:
            return "#6b7280"
    
    # Header bar with overall rating
    overall_rating = "BULLISH" if current_price > sma_21 > sma_50 else "BEARISH" if current_price < sma_21 < sma_50 else "NEUTRAL"
    primary_signal = "BUY" if rsi < 30 and current_price < bb_lower else "SELL" if rsi > 70 and current_price > bb_upper else "HOLD"
    risk_level = "HIGH" if abs(rsi - 50) > 20 or current_price > bb_upper or current_price < bb_lower else "MEDIUM" if abs(rsi - 50) > 10 else "LOW"
    
    st.markdown(f"""
    <div style="background: rgba(17, 24, 39, 0.9); backdrop-filter: blur(24px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 16px; margin: 16px 0;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
            <h3 style="color: #f9fafb; margin: 0; font-size: 1.1rem; font-weight: 600;"><i class="fas fa-chart-line" style="margin-right: 8px; color: #8b5cf6;"></i>Technical Analysis</h3>
            <div style="display: flex; align-items: center; gap: 16px; font-size: 0.85rem;">
                <span style="color: #f9fafb;">Overall Rating: <span style="color: {'#10b981' if overall_rating == 'BULLISH' else '#ef4444' if overall_rating == 'BEARISH' else '#6b7280'}; font-weight: 600;">{overall_rating}</span></span>
                <span style="color: #6b7280;">|</span>
                <span style="color: #f9fafb;">Primary Signal: <span style="color: {'#10b981' if primary_signal == 'BUY' else '#ef4444' if primary_signal == 'SELL' else '#6b7280'}; font-weight: 600;">{primary_signal}</span></span>
                <span style="color: #6b7280;">|</span>
                <span style="color: #f9fafb;">Risk Level: <span style="color: {'#ef4444' if risk_level == 'HIGH' else '#f59e0b' if risk_level == 'MEDIUM' else '#10b981'}; font-weight: 600;">{risk_level}</span></span>
                <span style="color: #6b7280;">|</span>
                <span style="color: #f9fafb;">Confidence: <span style="color: #8b5cf6; font-weight: 600;">{confidence:.0f}%</span></span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Price Action Group
    with st.expander("📈 Price Action", expanded=True):
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.1); border-radius: 8px; padding: 12px; margin: 8px 0;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                <span style="color: #f9fafb; font-size: 0.85rem;">Current Price</span>
                <span style="color: #f9fafb; font-weight: 600;">${current_price:,.0f}</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                <span style="color: #d1d5db; font-size: 0.85rem;">21-day MA</span>
                <span style="color: {get_trend_arrow(current_price - sma_21)[1]}; font-weight: 600;">${sma_21:,.0f} {get_trend_arrow(current_price - sma_21)[0]}</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                <span style="color: #d1d5db; font-size: 0.85rem;">50-day MA</span>
                <span style="color: {get_trend_arrow(current_price - sma_50)[1]}; font-weight: 600;">${sma_50:,.0f} {get_trend_arrow(current_price - sma_50)[0]}</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                <span style="color: #d1d5db; font-size: 0.85rem;">200-day MA</span>
                <span style="color: {get_trend_arrow(current_price - sma_200)[1]}; font-weight: 600;">${sma_200:,.0f} {get_trend_arrow(current_price - sma_200)[0]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Technical Signals Group
    with st.expander("⚡ Technical Signals", expanded=True):
        st.markdown(f"""
        <div style="background: rgba(139, 92, 246, 0.1); border-radius: 8px; padding: 12px; margin: 8px 0;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                <span style="color: #f9fafb; font-size: 0.85rem;">RSI (14)</span>
                <span style="color: {get_rsi_color(rsi)}; font-weight: 600;">{rsi:.1f} {get_trend_arrow(rsi - 50, 10)[0]}</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                <span style="color: #d1d5db; font-size: 0.85rem;">MACD</span>
                <span style="color: {get_trend_arrow(macd)[1]}; font-weight: 600;">{macd:.3f} {get_trend_arrow(macd)[0]}</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                <span style="color: #d1d5db; font-size: 0.85rem;">Williams %R</span>
                <span style="color: {get_trend_arrow(-williams_r - 50, 10)[1]}; font-weight: 600;">{williams_r:.1f} {get_trend_arrow(-williams_r - 50, 10)[0]}</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                <span style="color: #d1d5db; font-size: 0.85rem;">Stochastic %K</span>
                <span style="color: {get_trend_arrow(stoch_k - 50, 10)[1]}; font-weight: 600;">{stoch_k:.1f} {get_trend_arrow(stoch_k - 50, 10)[0]}</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                <span style="color: #d1d5db; font-size: 0.85rem;">ADX</span>
                <span style="color: {'#10b981' if adx > 25 else '#f59e0b' if adx > 15 else '#6b7280'}; font-weight: 600;">{adx:.1f} {'↑' if adx > 25 else '→'}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Volume Analysis Group
    with st.expander("📊 Volume Analysis", expanded=False):
        volume_ratio = (volume_24h / market_cap * 100) if market_cap > 0 else 0
        st.markdown(f"""
        <div style="background: rgba(59, 130, 246, 0.1); border-radius: 8px; padding: 12px; margin: 8px 0;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                <span style="color: #f9fafb; font-size: 0.85rem;">24h Volume</span>
                <span style="color: #f9fafb; font-weight: 600;">${volume_24h:,.0f}M</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                <span style="color: #d1d5db; font-size: 0.85rem;">Volume Ratio</span>
                <span style="color: {'#10b981' if volume_ratio > 5 else '#f59e0b' if volume_ratio > 2 else '#6b7280'}; font-weight: 600;">{volume_ratio:.1f}% {'↑' if volume_ratio > 5 else '→'}</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                <span style="color: #d1d5db; font-size: 0.85rem;">Market Cap</span>
                <span style="color: #f9fafb; font-weight: 600;">${market_cap:,.0f}B</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Volatility Analysis Group
    with st.expander("📈 Volatility Analysis", expanded=False):
        st.markdown(f"""
        <div style="background: rgba(245, 158, 11, 0.1); border-radius: 8px; padding: 12px; margin: 8px 0;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                <span style="color: #f9fafb; font-size: 0.85rem;">Bollinger Upper</span>
                <span style="color: {'#ef4444' if current_price > bb_upper else '#6b7280'}; font-weight: 600;">${bb_upper:,.0f} {'↑' if current_price > bb_upper else '→'}</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                <span style="color: #d1d5db; font-size: 0.85rem;">Bollinger Middle</span>
                <span style="color: #6b7280; font-weight: 600;">${bb_middle:,.0f} →</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                <span style="color: #d1d5db; font-size: 0.85rem;">Bollinger Lower</span>
                <span style="color: {'#10b981' if current_price < bb_lower else '#6b7280'}; font-weight: 600;">${bb_lower:,.0f} {'↓' if current_price < bb_lower else '→'}</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                <span style="color: #d1d5db; font-size: 0.85rem;">ATR (14)</span>
                <span style="color: {'#ef4444' if atr > current_price * 0.05 else '#f59e0b' if atr > current_price * 0.02 else '#10b981'}; font-weight: 600;">${atr:,.0f} {'↑' if atr > current_price * 0.05 else '→'}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Key Levels Section
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 1.5rem; margin: 1rem 0; border-left: 4px solid #3b82f6;">
        <h4 style="color: #f9fafb; margin-bottom: 1rem; font-size: 1.1rem;"><i class="fas fa-bullseye" style="margin-right: 0.5rem; color: #3b82f6;"></i>Key Levels to Watch</h4>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="color: #10b981; font-size: 1.2rem; font-weight: 600;">${bb_upper:,.2f}</div>
            <div style="color: #d1d5db; font-size: 0.9rem;">Resistance Level</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="color: #f9fafb; font-size: 1.2rem; font-weight: 600;">${current_price:,.2f}</div>
            <div style="color: #d1d5db; font-size: 0.9rem;">Current Price</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="color: #ef4444; font-size: 1.2rem; font-weight: 600;">${bb_lower:,.2f}</div>
            <div style="color: #d1d5db; font-size: 0.9rem;">Support Level</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Close section-spacing
    
    # Compact Buy/Sell Zones Analysis with Grouped Indicators
    st.markdown(f"""
    <div style="background: rgba(17, 24, 39, 0.9); backdrop-filter: blur(24px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 16px; margin: 16px 0;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
            <h3 style="color: #f9fafb; margin: 0; font-size: 1.1rem; font-weight: 600;"><i class="fas fa-bullseye" style="margin-right: 8px; color: #8b5cf6;"></i>Buy/Sell Zones Analysis</h3>
            <div style="display: flex; align-items: center; gap: 16px; font-size: 0.85rem;">
                <span style="color: #f9fafb;">Current Price: <span style="color: #8b5cf6; font-weight: 600;">${current_price:,.0f}</span></span>
                <span style="color: #6b7280;">|</span>
                <span style="color: #f9fafb;">Zone: <span style="color: {'#10b981' if current_price < bb_lower else '#ef4444' if current_price > bb_upper else '#6b7280'}; font-weight: 600;">{'Oversold' if current_price < bb_lower else 'Overbought' if current_price > bb_upper else 'Neutral'}</span></span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if historical_df is not None:
        # Calculate key levels
        sma_21 = historical_df["sma_21"].iloc[-1] if "sma_21" in historical_df.columns else current_price
        sma_50 = historical_df["sma_50"].iloc[-1] if "sma_50" in historical_df.columns else current_price
        sma_200 = historical_df["sma_200"].iloc[-1] if "sma_200" in historical_df.columns else current_price
        bb_upper = historical_df["bb_upper"].iloc[-1] if "bb_upper" in historical_df.columns else current_price
        bb_lower = historical_df["bb_lower"].iloc[-1] if "bb_lower" in historical_df.columns else current_price
        bb_middle = historical_df["bb_middle"].iloc[-1] if "bb_middle" in historical_df.columns else current_price
        
        # Fibonacci levels
        fib_382 = historical_df['fib_382'].iloc[-1] if 'fib_382' in historical_df.columns else current_price
        fib_618 = historical_df['fib_618'].iloc[-1] if 'fib_618' in historical_df.columns else current_price
        
        # Ichimoku levels
        tenkan = historical_df['tenkan_sen'].iloc[-1] if 'tenkan_sen' in historical_df.columns else current_price
        kijun = historical_df['kijun_sen'].iloc[-1] if 'kijun_sen' in historical_df.columns else current_price
        
        # Calculate proper buy/sell zones (buy below current price, sell above current price)
        # Buy zones = support levels below current price
        short_buy_zone = current_price * 0.95  # 5% below current price
        mid_buy_zone = current_price * 0.85   # 15% below current price  
        long_buy_zone = current_price * 0.70  # 30% below current price
        
        # Sell zones = resistance levels above current price
        short_sell_zone = current_price * 1.05  # 5% above current price
        mid_sell_zone = current_price * 1.15   # 15% above current price
        long_sell_zone = current_price * 1.30  # 30% above current price
        
        # Support/Resistance Levels Group
        with st.expander("🎯 Support & Resistance Levels", expanded=True):
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.1); border-radius: 8px; padding: 12px; margin: 8px 0;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                    <span style="color: #f9fafb; font-size: 0.85rem;">Strong Support</span>
                    <span style="color: #10b981; font-weight: 600;">${bb_lower:,.0f} (Lower BB)</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                    <span style="color: #d1d5db; font-size: 0.85rem;">Support</span>
                    <span style="color: #3b82f6; font-weight: 600;">${sma_50:,.0f} (50-day MA)</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                    <span style="color: #d1d5db; font-size: 0.85rem;">Current Price</span>
                    <span style="color: #f9fafb; font-weight: 600;">${current_price:,.0f}</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                    <span style="color: #d1d5db; font-size: 0.85rem;">Resistance</span>
                    <span style="color: #3b82f6; font-weight: 600;">${sma_21:,.0f} (21-day MA)</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                    <span style="color: #f9fafb; font-size: 0.85rem;">Strong Resistance</span>
                    <span style="color: #ef4444; font-weight: 600;">${bb_upper:,.0f} (Upper BB)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Buy/Sell Zones Group
        with st.expander("📈 Buy/Sell Zones", expanded=True):
            st.markdown(f"""
            <div style="background: rgba(139, 92, 246, 0.1); border-radius: 8px; padding: 12px; margin: 8px 0;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                    <span style="color: #f9fafb; font-size: 0.85rem;">Short-term Buy Zone</span>
                    <span style="color: #10b981; font-weight: 600;">${short_buy_zone:,.0f} (-5%)</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                    <span style="color: #d1d5db; font-size: 0.85rem;">Short-term Sell Zone</span>
                    <span style="color: #ef4444; font-weight: 600;">${short_sell_zone:,.0f} (+5%)</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                    <span style="color: #f9fafb; font-size: 0.85rem;">Mid-term Buy Zone</span>
                    <span style="color: #10b981; font-weight: 600;">${mid_buy_zone:,.0f} (-15%)</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                    <span style="color: #d1d5db; font-size: 0.85rem;">Mid-term Sell Zone</span>
                    <span style="color: #ef4444; font-weight: 600;">${mid_sell_zone:,.0f} (+15%)</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                    <span style="color: #f9fafb; font-size: 0.85rem;">Long-term Buy Zone</span>
                    <span style="color: #10b981; font-weight: 600;">${long_buy_zone:,.0f} (-30%)</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                    <span style="color: #d1d5db; font-size: 0.85rem;">Long-term Sell Zone</span>
                    <span style="color: #ef4444; font-weight: 600;">${long_sell_zone:,.0f} (+30%)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Fibonacci Levels Group
        with st.expander("📐 Fibonacci Levels", expanded=False):
            st.markdown(f"""
            <div style="background: rgba(59, 130, 246, 0.1); border-radius: 8px; padding: 12px; margin: 8px 0;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                    <span style="color: #f9fafb; font-size: 0.85rem;">61.8% Retracement</span>
                    <span style="color: {'#ef4444' if current_price > fib_618 else '#6b7280'}; font-weight: 600;">${fib_618:,.0f} {'↑' if current_price > fib_618 else '→'}</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                    <span style="color: #d1d5db; font-size: 0.85rem;">50% Retracement</span>
                    <span style="color: #6b7280; font-weight: 600;">${(bb_upper + bb_lower) / 2:,.0f} →</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                    <span style="color: #d1d5db; font-size: 0.85rem;">38.2% Retracement</span>
                    <span style="color: {'#10b981' if current_price < fib_382 else '#6b7280'}; font-weight: 600;">${fib_382:,.0f} {'↓' if current_price < fib_382 else '→'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Ichimoku Levels Group
        with st.expander("☁️ Ichimoku Cloud", expanded=False):
            st.markdown(f"""
            <div style="background: rgba(245, 158, 11, 0.1); border-radius: 8px; padding: 12px; margin: 8px 0;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                    <span style="color: #f9fafb; font-size: 0.85rem;">Tenkan-sen</span>
                    <span style="color: {'#10b981' if current_price > tenkan else '#ef4444'}; font-weight: 600;">${tenkan:,.0f} {'↑' if current_price > tenkan else '↓'}</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                    <span style="color: #d1d5db; font-size: 0.85rem;">Kijun-sen</span>
                    <span style="color: {'#10b981' if current_price > kijun else '#ef4444'}; font-weight: 600;">${kijun:,.0f} {'↑' if current_price > kijun else '↓'}</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin: 4px 0;">
                    <span style="color: #d1d5db; font-size: 0.85rem;">Cloud Status</span>
                    <span style="color: {'#10b981' if tenkan > kijun else '#ef4444'}; font-weight: 600;">{'Bullish' if tenkan > kijun else 'Bearish'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Risk assessment
    st.markdown('<div class="section-header">Risk Assessment</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
    
    volatility = historical_df['price'].pct_change().std() * np.sqrt(365) * 100 if historical_df is not None else 50
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_level = "High" if volatility > 100 else "Medium" if volatility > 50 else "Low"
        risk_color = "#ef4444" if risk_level == "High" else "#f59e0b" if risk_level == "Medium" else "#10b981"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Volatility Risk</div>
            <div class="metric-value" style="color: {risk_color};">{risk_level}</div>
            <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #94a3b8;">{volatility:.1f}% annually</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_volume = get_usd_value(market_data['total_volume'])
        market_cap = get_usd_value(market_data['market_cap'])
        liquidity_score = min(100, (total_volume / market_cap) * 1000) if market_cap > 0 else 0
        liquidity_level = "High" if liquidity_score > 20 else "Medium" if liquidity_score > 10 else "Low"
        liquidity_color = "#10b981" if liquidity_level == "High" else "#f59e0b" if liquidity_level == "Medium" else "#ef4444"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Liquidity</div>
            <div class="metric-value" style="color: {liquidity_color};">{liquidity_level}</div>
            <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #94a3b8;">{liquidity_score:.1f}/100</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        market_cap_rank = basic_data.get('market_cap_rank', 100)
        stability_level = "High" if market_cap_rank <= 20 else "Medium" if market_cap_rank <= 100 else "Low"
        stability_color = "#10b981" if stability_level == "High" else "#f59e0b" if stability_level == "Medium" else "#ef4444"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Market Position</div>
            <div class="metric-value" style="color: {stability_color};">{stability_level}</div>
            <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #94a3b8;">Rank #{market_cap_rank}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close section-spacing

if __name__ == "__main__":
    main()
