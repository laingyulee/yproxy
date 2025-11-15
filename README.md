# yfinance API Proxy

这是一个使用 FastAPI 和 yfinance 库构建的 API 代理服务。它允许您通过简单的 HTTP 请求获取股票信息、历史数据、分析师目标价、快速信息和财务报表。

## 功能

*   获取股票综合信息 (`/ticker/{symbol}/info`)
*   获取股票历史数据 (`/ticker/{symbol}/history`)
*   获取分析师目标价 (`/ticker/{symbol}/analyst-price-targets`)
*   获取快速概览信息 (`/ticker/{symbol}/fast-info`)
*   获取公司收入报表 (`/ticker/{symbol}/income-stmt`)

## 设置与运行

### 前提条件

*   Python 3.9+
*   pip (Python 包管理器)
*   Docker (可选，用于容器化部署)

### 本地运行

1.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **启动API服务**:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```
    服务将在 `http://127.0.0.1:8000` 运行。

### 使用 Docker 运行

1.  **构建 Docker 镜像**:
    在项目根目录中执行：
    ```bash
    docker build -t yfinance-proxy .
    ```

2.  **运行 Docker 容器**:
    ```bash
    docker run -d -p 8000:8000 --name yfinance-proxy-container yfinance-proxy
    ```
    容器将在后台运行，并将主机的 8000 端口映射到容器的 8000 端口。

3.  **停止 Docker 容器**:
    ```bash
    docker stop yfinance-proxy-container
    docker rm yfinance-proxy-container
    ```

## API 端点

所有端点都以 `http://127.0.0.1:8000` 为基础。

### 1. 获取股票综合信息

*   **GET** `/ticker/{symbol}/info`
*   **示例**: `http://127.0.0.1:8000/ticker/AAPL/info`

### 2. 获取股票历史数据

*   **GET** `/ticker/{symbol}/history`
*   **查询参数**:
    *   `period` (可选, 默认: `1mo`): 数据周期 (例如: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`)
    *   `interval` (可选, 默认: `1d`): 数据间隔 (例如: `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m`, `1h`, `1d`, `5d`, `1wk`, `1mo`, `3mo`)
*   **示例**: `http://127.0.0.1:8000/ticker/AAPL/history?period=1y&interval=1wk`

### 3. 获取分析师目标价

*   **GET** `/ticker/{symbol}/analyst-price-targets`
*   **示例**: `http://127.0.0.1:8000/ticker/AAPL/analyst-price-targets`

### 4. 获取快速概览信息

*   **GET** `/ticker/{symbol}/fast-info`
*   **示例**: `http://127.0.0.1:8000/ticker/MSFT/fast-info`

### 5. 获取公司收入报表

*   **GET** `/ticker/{symbol}/income-stmt`
*   **示例**: `http://127.0.0.1:8000/ticker/GOOG/income-stmt`

## API 文档

访问 `http://127.0.0.1:8000/docs` 可以查看由 FastAPI 自动生成的交互式 API 文档 (Swagger UI)。
