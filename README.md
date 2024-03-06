# Basic ETH price prediction node

Example Allora network worker node: a node to provide price predictions of ETH.

One of the primary objectives is to demonstrate the utilization of a basic inference model operating within a dedicated container. The purpose is to showcase its seamless integration with the Allora network infrastructure, enabling it to contribute with valuable inferences.

# Components

* **head**: An Allora network head node. This is not required for running your node in the Allora network, but it will help for testing your node emulating a network.
* **worker**: The node that will respond to inference requests from the Allora network heads.
* **inference**: A container that conducts inferences, maintains the model state, and responds to internal inference requests via a Flask application. The node operates with a basic linear regression model for price predictions.
* **updater**: An example of a cron-like container, that will update the data of the inference node.
Check the `docker-compose.yml` file (or see docker-compose section below) to see separate components:

# Inference request flow

When a request is made to the head, it relays this request to a number of workers associated with this head. The request specifies a function to run which will execute a wasm code that will call the `main.py` file in the worker. The worker will check the argument (the coin to predict for), and make a request to the `inference` node, and return this value to the `head`, which prepares the response from all of its nodes and sends it back to the requestor.

# Docker setup

## Structure

- head and worker nodes are built upon `Dockerfile_b7s` file
- inference and updater nodes are built with `Dockerfile`. This works as an example on how to reuse your current model containers, just by setting up a Flask web application in front with minimal integration work with the Allora network nodes.

The `Dockerfile_b7s` file is functional but simple, so you may want to change it to fit your needs, if you attempt to expand upon the current setup.
For further details, please check the base repo [allora-inference-base](https://github.com/allora-network/allora-inference-base).

###  Application path

By default, the application runtime lives under `/app`, as well as the Python code the worker provides (`/app/main.py`). The current user needs to have write permissions on `/app/runtime`.

### Data volume and permissions

It is recommended to mount `/data` as a volume, to persist the node databases of peers, functions, etc. which are defined in the flags passed to the worker.
You can create this folder e.g. `mkdir data` in the repo root directory.

It is recommended to set up two different `/data` volumes. It is suggested to use `data-worker` for the worker, `data-head` for the head.

Troubleshooting: A conflict may happen between the uid/gid of the user inside the container(1001) with the permissions of your own user.
To make the container user have permissions to write on the `/data` volume, you may need to set the UID/GID from the user running the container. You can get those in linux/osx via `id -u` and `id -g`.
The current `docker-compose.yml` file shows the `worker` service setting UID and GID. As well, the `Dockerfile` also sets UID/GID values.


# docker-compose
A full working example is provided in `docker-compose`.

## Structure
There is a docker-compose.yml provided that sets up one head node, one worker node, one inference node, and an updater node.
Please find details about options on the [allora-inference-base](https://github.com/allora-network/allora-inference-base) repo.

## Dependencies
Ensure the following dependencies are in place before proceeding:

- **Docker Image**:  Have an available image of the `allora-inference-base`, and reference it as a base on the `FROM` of the `Dockerfile_b7s` file.
- **Keys Setup**: Create a set of keys for your head and worker and use them in the head and worker configuration. If no keys are specified in the volumes, new keys are created. However, the worker will need to specify the `peer_id` of the head for defining it as a `BOOT_NODES`.

## Connecting to the Allora network
 In order to connect the an Allora network to provide inferences, both the head and the worker need to register against it.  More details on [allora-inference-base](https://github.com/allora-network/allora-inference-base) repo.
The following optional flags are used in the `command:` section of the `docker-compose.yml` file to define the connectivity with the Allora network.

```
--allora-chain-key-name=index-provider  # your local key name in your keyring
--allora-chain-restore-mnemonic='pet sock excess ...'  # your node's Allora address mnemonic
--allora-node-rpc-address=  # RPC address of a node in the chain
--allora-chain-topic-id=  # The topic id from the chain that you want to provide predictions for
```
In order for the nodes to register with the chain, a funded address is needed first.
If these flags are not provided, the nodes will not register to the appchain and will not attempt to connect to the appchain.

# Setup
Once this is set up, run `docker compose up head worker inference`
This will bring up the head, the worker and the inference nodes (which will run an initial update). The `updater` node is a companion for updating the inference node state and it's meant to hit the /update endpoint on the inference service. It is expected to run periodically, being crucial for maintaining the accuracy of the inferences.

## Testing docker-compose setup

The head node has the only open port, and responds to requests in port 6000.

Example request:
```
curl --location 'http://localhost:6000/api/v1/functions/execute' \
--header 'Content-Type: application/json' \
--data '{
    "function_id": "bafybeigpiwl3o73zvvl6dxdqu7zqcub5mhg65jiky2xqb4rdhfmikswzqm",
    "method": "allora-inference-function.wasm",
    "parameters": null,
    "topic": "1",
    "config": {
        "env_vars": [
            {
                "name": "BLS_REQUEST_PATH",
                "value": "/api"
            },
            {
                "name": "ALLORA_ARG_PARAMS",
                "value": "ETH"
            }
        ],
        "number_of_nodes": -1,
        "timeout": 2
    }
}'
```
Response: 
```
{"code":"200","request_id":"e3daeda0-c849-4b68-b21d-8f51e42bb9d3","results":[{"result":{"stdout":"{\"value\":\"2564.250058819078\"}\n\n\n","stderr":"","exit_code":0},"peers":["12D3KooWG8dHctRt6ctakJfG5masTnLaKM6xkudoR5BxLDRSrgVt"],"frequency":100}],"cluster":{"peers":["12D3KooWG8dHctRt6ctakJfG5masTnLaKM6xkudoR5BxLDRSrgVt"]}}
```

# Testing inference only
This setup allows to develop your model without need for bringing up the head and worker.
To only test the inference model, you can just:
- In docker-compose.yml, under `inference` service, uncomment the lines:
    ```
    ports:
      - "8000:8000"
    ```
- Run `docker compose up --build inference` and wait for the initial data load.
- Requests can now be sent, e.g. request ETH price inferences as in: 
  ```
    $ curl http://localhost:8000/inference/ETH
    {"value":"2564.2513659239594"}
  ```
  or update the node's internal state (download pricing data, train and update the model):
  ```
    $ curl http://localhost:8000/update
    0
  ```

