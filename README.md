# Basic ETH price prediction node

Example Allora network worker node: a node to provide price predictions of ETH.

One of the primary objectives is to demonstrate the utilization of a basic inference model operating within a dedicated container. The purpose is to showcase its seamless integration with the Allora network infrastructure, enabling it to contribute with valuable inferences.

### Components

* **Head**: An Allora network head node. This is not required for running your node in the Allora network, but it will help for testing your node emulating a network.
* **Worker**: The node that will respond to inference requests from the Allora network heads.
* **Inference**: A container that conducts inferences, maintains the model state, and responds to internal inference requests via a Flask application. The node operates with a basic linear regression model for price predictions.
* **Updater**: An example of a cron-like container designed to update the inference node's data by daily fetching the latest market information from Binance, ensuring the model is kept current with new market trends.

Check the `docker-compose.yml` file to see the separate components.

### Inference request flow

When a request is made to the head, it relays this request to several workers associated with this head. The request specifies a function to run which will execute a wasm code that will call the `main.py` file in the worker. The worker will check the argument (the coin to predict for), make a request to the `inference` node, and return this value to the `head`, which prepares the response from all of its nodes and sends it back to the requestor.

# Docker Setup

- head and worker nodes are built upon `Dockerfile_b7s` file. This file is functional but simple, so you may want to change it to fit your needs, if you attempt to expand upon the current setup.
For further details, please check the base repo [allora-inference-base](https://github.com/allora-network/allora-inference-base).
- inference and updater nodes are built with `Dockerfile`. This works as an example of how to reuse your current model containers, just by setting up a Flask web application in front with minimal integration work with the Allora network nodes.

###  Application path

By default, the application runtime lives under `/app`, as well as the Python code the worker provides (`/app/main.py`). The current user needs to have write permissions on `/app/runtime`.

### Data volume and permissions

It is recommended to mount `/data` as a volume, to persist the node databases of peers, functions, etc. which are defined in the flags passed to the worker.
You can create this folder e.g. `mkdir data` in the repo root directory.

It is recommended to set up two different `/data` volumes. It is suggested to use `worker-data` for the worker, `head-data` for the head.

Troubleshooting: A conflict may happen between the uid/gid of the user inside the container(1001) with the permissions of your own user.
To make the container user have permissions to write on the `/data` volume, you may need to set the UID/GID from the user running the container. You can get those in linux/osx via `id -u` and `id -g`.
The current `docker-compose.yml` file shows the `worker` service setting UID and GID. As well, the `Dockerfile` also sets UID/GID values.


# Docker-Compose Setup
A full working example is provided in the `docker-compose.yml` file.

1. **Generate keys**: Create a set of keys for your head and worker nodes. These keys will be used in the configuration of the head and worker nodes.

**Create head keys:**
```
docker run -it --entrypoint=bash -v ./head-data:/data alloranetwork/allora-inference-base:latest -c "mkdir -p /data/keys && (cd /data/keys && allora-keys)"
```

**Create worker keys**
```
docker run -it --entrypoint=bash -v ./worker-data:/data alloranetwork/allora-inference-base:latest -c "mkdir -p /data/keys && (cd /data/keys && allora-keys)"
```

Important note: If no keys are specified in the volumes, new keys will be automatically created inside `head-data/keys` and `worker-data/keys` when first running step 3.

2. **Connect the worker node to the head node**:

At this step, both worker and head nodes identities are generated inside `head-data/keys` and `worker-data/keys`.
To instruct the worker node to connect to the head node:
- run `cat head-data/keys/identity` to extract the head node's peer_id specified in the `head-data/keys/identity`
- use the printed peer_id to replace the `head-id` placeholder value specified inside the docker-compose.yml file when running the worker service: `--boot-nodes=/ip4/172.22.0.100/tcp/9010/p2p/head-id`

3. **Run setup**
Once all the above is set up, run `docker-compose build && docker-compose up`
This will bring up the head, the worker and the inference nodes (which will run an initial update). The `updater` node is a companion for updating the inference node state and it's meant to hit the /update endpoint on the inference service. It is expected to run periodically, being crucial for maintaining the accuracy of the inferences.

## Testing docker-compose setup

The head node has the only open port and responds to requests in port 6000.

Example request:
```
curl --location 'http://127.0.0.1:6000/api/v1/functions/execute' \
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
{
  "code": "200",
  "request_id": "03001a39-4387-467c-aba1-c0e1d0d44f59",
  "results": [
    {
      "result": {
        "stdout": "{\"value\":\"2564.021586281073\"}",
        "stderr": "",
        "exit_code": 0
      },
      "peers": [
        "12D3KooWG8dHctRt6ctakJfG5masTnLaKM6xkudoR5BxLDRSrgVt"
      ],
      "frequency": 100
    }
  ],
  "cluster": {
    "peers": [
      "12D3KooWG8dHctRt6ctakJfG5masTnLaKM6xkudoR5BxLDRSrgVt"
    ]
  }
}
```

## Testing inference only
This setup allows to develop your model without the need for bringing up the head and worker.
To only test the inference model, you can just:
- Run `docker compose up --build inference` and wait for the initial data load.
- Requests can now be sent, e.g. request ETH price inferences as in: 
  ```
    $ curl http://127.0.0.1:8000/inference/ETH
    {"value":"2564.021586281073"}
  ```
  or update the node's internal state (download pricing data, train and update the model):
  ```
    $ curl http://127.0.0.1:8000/update
    0
  ```

## Connecting to the Allora network
 To connect to the Allora network to provide inferences, both the head and the worker need to register against it. More details on [allora-inference-base](https://github.com/allora-network/allora-inference-base) repo.
The following optional flags are used in the `command:` section of the `docker-compose.yml` file to define the connectivity with the Allora network.

```
--allora-chain-key-name=index-provider  # your local key name in your keyring
--allora-chain-restore-mnemonic='pet sock excess ...'  # your node's Allora address mnemonic
--allora-node-rpc-address=  # RPC address of a node in the chain
--allora-chain-topic-id=  # The topic id from the chain that you want to provide predictions for
```
For the nodes to register with the chain, a funded address is needed first.
If these flags are not provided, the nodes will not register to the appchain and will not attempt to connect to the appchain.
