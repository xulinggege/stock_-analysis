# A股股票分析工具 (A-Share Stock Analysis Tool)

这是一个基于 Python 的 A 股股票数据分析工具，提供了一个交互式的 Web 界面，用于展示股票的 K 线走势和换手率分析。

## 功能特点

- **多数据源支持**: 优先使用 AkShare 获取数据，自动降级到 yfinance。
- **交互式图表**: 使用 Plotly 绘制可缩放、可交互的 K 线图和均线。
- **换手率分析**: 直观展示每日换手率与股价的关系。
- **Web 界面**: 基于 Streamlit 构建，操作简单直观。

## 本地运行

1.  **克隆仓库**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
    ```

2.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

3.  **运行应用**
    ```bash
    streamlit run web_app.py
    ```

## 部署到 Streamlit Cloud

本项目完全兼容 Streamlit Community Cloud，您可以轻松将其部署到云端并分享给他人。

1.  将本项目代码上传到您的 GitHub 仓库。
2.  访问 [share.streamlit.io](https://share.streamlit.io/) 并登录。
3.  点击 "New app"，选择对应的 GitHub 仓库。
4.  **Main file path** 填写 `web_app.py`。
5.  点击 "Deploy" 即可。

## 文件说明

- `web_app.py`: Streamlit Web 应用入口。
- `data_loader.py`: 数据获取模块。
- `plotter.py`: (旧版) 静态图片绘图模块。
- `main.py`: (旧版) 命令行工具入口。
- `requirements.txt`: 项目依赖列表。
