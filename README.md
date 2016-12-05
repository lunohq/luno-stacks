# luno-stacks

This repo contains the stacks required to build luno. It also contains our Elasticsearch schema and management actions (within the `es` directory).

Stacks for luno.

## Working with Stacks

To build stacks:

```
make build
```

To get stack outputs:

```
make outputs
```

To install blueprints:

```
pip install -e .
```

To add an encrypted value to the config:

```
$ aws --region us-east-1 kms encrypt --key-id alias/stacker --plaintext "PASSWORD" --output text --query CiphertextBlob
```

or simply our shortcut,

```
$ make encrypt value=<value>
```

## Managing Elasticsearch

We use invoke to manage creating and migrating indices within elasticsearch.

We store the ES endpoint and region within the `invoke.yaml` file under the correct region. We use this to operate against a specific ES cluster within the tasks, ie:

```
from invoke import ctask as task


@task
def environment_config(ctx):
    config = ctx[ctx.env]
    print config


```

We default `env` to `dev`. To change this, you can provide an environmental variable: `INVOKE_ENV=prod`, this will load any production configs.

Run `invoke --list` to see available commands.
