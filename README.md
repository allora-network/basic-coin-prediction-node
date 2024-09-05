# Basic Price Prediction Node

This repository provides an example [Allora network](https://docs.allora.network/) worker node, designed to offer price predictions. The primary objective is to demonstrate the use of a basic inference model running within a dedicated container, showcasing its integration with the Allora network infrastructure to contribute valuable inferences.

## Components

- **Worker**: The node that publishes inferences to the Allora chain.
- **Inference**: A container that conducts inferences, maintains the model state, and responds to internal inference requests via a Flask application. This node operates with a basic linear regression model for price predictions.
- **Updater**: A cron-like container designed to update the inference node's data by daily fetching the latest market information from the data provider, ensuring the model stays current with new market trends.

Check the `docker-compose.yml` file for the detailed setup of each component.

## Docker-Compose Setup

A complete working example is provided in the `docker-compose.yml` file.

### Steps to Setup

1. **Clone the Repository**
2. **Copy and Populate Model Configuration environment file**
    
    Copy the example .env.example file and populate it with your variables:
    ```sh
    cp .env.example .env
    ```

    Here are the currently accepted configurations:
    - TOKEN
    Must be one in ('ETH','SOL','BTC','BNB','ARB'). 
    Note: if you are using `Binance` as the data provider, any token could be used.
    If you are using Coingecko, you should add its `coin_id` in the [token_map here](https://github.com/allora-network/basic-coin-prediction-node/blob/main/updater.py#L107). Find [more info here](https://docs.coingecko.com/reference/simple-price) and the [list here](https://docs.google.com/spreadsheets/d/1wTTuxXt8n9q7C4NDXqQpI3wpKu1_5bGVmP9Xz0XGSyU/edit?usp=sharing).
    - TRAINING_DAYS
    Must be an `int` >= 1. 
    Represents how many days of historical data to use. 
    - TIMEFRAME
    This should be in this form: `10min`, `1h`, `1d`, `1m`, etc.
    Note: For Coingecko, Data granularity (candle's body) is automatic - [see here](https://docs.coingecko.com/reference/coins-id-ohlc). To avoid downsampling, it is recommanded to use with Coingecko:
        - TIMEFRAME >= 30m if TRAINING_DAYS <= 2
        - TIMEFRAME >= 4h if TRAINING_DAYS <= 30
        - TIMEFRAME >= 4d if TRAINING_DAYS >= 31
    - MODEL
    Must be one in ('LinearRegression','SVR','KernelRidge','BayesianRidge'). 
    You can easily add support for any other models by [adding it here](https://github.com/allora-network/basic-coin-prediction-node/blob/main/model.py#L133).
    - REGION
    Used for the Binance API. This should be in this form: `US`, `EU`, etc.
    - DATA_PROVIDER
    Must be `binance` or `coingecko`. Feel free to add support for other data providers to personalize your model!
    - CG_API_KEY
    This is your `Coingecko` API key, if you've set `DATA_PROVIDER=coingecko`.

3. **Copy and Populate Worker Configuration**

    Copy the example configuration file and populate it with your variables:
    ```sh
    cp config.example.json config.json
    ```

4. **Initialize Worker**
    
    Run the following commands from the project's root directory to initialize the worker:
    ```sh
    chmod +x init.config
    ./init.config
    ```
    These commands will:
    - Automatically create Allora keys for your worker.
    - Export the needed variables from the created account to be used by the worker node, bundle them with your provided `config.json`, and pass them to the node as environment variables.

5. **Faucet Your Worker Node**
    
    You can find the offchain worker node's address in `./worker-data/env_file` under `ALLORA_OFFCHAIN_ACCOUNT_ADDRESS`. [Add faucet funds](https://docs.allora.network/devs/get-started/setup-wallet#add-faucet-funds) to your worker's wallet before starting it.

6. **Start the Services**
    
    Run the following command to start the worker node, inference, and updater nodes:
    ```sh
    docker compose up --build
    ```
    To confirm that the worker successfully sends the inferences to the chain, look for the following log:
    ```
    {"level":"debug","msg":"Send Worker Data to chain","txHash":<tx-hash>,"time":<timestamp>,"message":"Success"}
    ```

## Testing Inference Only

This setup allows you to develop your model without the need to bring up the offchain worker or the updater. To test the inference model only:

1. Run the following command to start the inference node:
    ```sh
    docker compose up --build inference
    ```
    Wait for the initial data load.

2. Send requests to the inference model. For example, request ETH price inferences:
    
    ```sh
    curl http://127.0.0.1:8000/inference/ETH
    ```
    Expected response:
    ```json
    {"value":"2564.021586281073"}
    ```

3. Update the node's internal state (download pricing data, train, and update the model):
    
    ```sh
    curl http://127.0.0.1:8000/update
    ```
    Expected response:
    ```sh
    0
    ```
